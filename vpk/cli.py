"""
Command-line interface for VPS Proxy Kit

Provides both interactive menu and non-interactive commands for automation.
"""

import click
import sys
import os
from typing import Optional
from datetime import datetime
from tabulate import tabulate

from vpk import __version__
from vpk.config import Config
from vpk.db import Database
from vpk.users import UserManager, parse_quota_string, format_bytes
from vpk.utils import setup_logging


# Global instances
config: Optional[Config] = None
db: Optional[Database] = None
user_manager: Optional[UserManager] = None
logger = None


def init_app(config_path: Optional[str] = None):
    """Initialize application with config and database"""
    global config, db, user_manager, logger

    # Load configuration
    config = Config(config_path)

    # Setup logging
    logger = setup_logging(config.logging.directory, config.logging.level)

    # Initialize database
    if not os.path.exists(config.database.path):
        logger.warning("Database not found. Run 'vpk init-db' to initialize.")
        return False

    db = Database(config.database.path, config.database.encryption_key_path)
    user_manager = UserManager(db, config)

    return True


@click.group()
@click.version_option(version=__version__)
@click.option('--config', '-c', help='Path to configuration file')
@click.pass_context
def cli(ctx, config):
    """VPS Proxy Kit - Production-ready proxy server management"""
    ctx.ensure_object(dict)
    ctx.obj['config_path'] = config


@cli.command()
@click.pass_context
def init_db(ctx):
    """Initialize database"""
    config_path = ctx.obj.get('config_path')

    # Load configuration
    cfg = Config(config_path)

    # Check if encryption key exists
    if not os.path.exists(cfg.database.encryption_key_path):
        click.echo(
            f"❌ Encryption key not found: {cfg.database.encryption_key_path}", err=True)
        click.echo("Run bootstrap.sh first to set up the system.", err=True)
        sys.exit(1)

    # Create database
    click.echo(f"📦 Initializing database at {cfg.database.path}...")

    try:
        database = Database(cfg.database.path,
                            cfg.database.encryption_key_path)
        click.echo("✅ Database initialized successfully")
        database.close()
    except Exception as e:
        click.echo(f"❌ Failed to initialize database: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.option('--username', '-u', required=True, help='Username')
@click.option('--password', '-p', help='Password (will prompt if not provided)')
@click.option('--token-auth', is_flag=True, help='Use token authentication instead of password')
@click.option('--protocol', '-t', default='socks,https', help='Allowed protocols (comma-separated: socks,https)')
@click.option('--quota', '-q', default='100GB', help='Bandwidth quota (e.g., 100GB, 50MB)')
@click.option('--expires', help='Expiration date (YYYY-MM-DD)')
@click.pass_context
def create_user(ctx, username, password, token_auth, protocol, quota, expires):
    """Create a new user"""
    if not init_app(ctx.obj.get('config_path')):
        sys.exit(1)

    # Prompt for password if not provided and not using token auth
    if not token_auth and not password:
        password = click.prompt(
            'Password', hide_input=True, confirmation_prompt=True)

    # Parse quota
    try:
        quota_bytes = parse_quota_string(quota)
    except ValueError as e:
        click.echo(f"❌ {e}", err=True)
        sys.exit(1)

    # Parse expiration
    expires_at = None
    if expires:
        try:
            expires_at = datetime.strptime(expires, '%Y-%m-%d')
        except ValueError:
            click.echo("❌ Invalid date format. Use YYYY-MM-DD", err=True)
            sys.exit(1)

    # Parse protocols
    protocols = [p.strip() for p in protocol.split(',')]

    # Create user
    success, message, token = user_manager.create_user(
        username=username,
        password=password,
        token_auth=token_auth,
        protocols=protocols,
        quota_bytes=quota_bytes,
        expires_at=expires_at
    )

    if success:
        click.echo(f"✅ {message}")
        if token:
            click.echo(f"\n🔑 Token: {token}")
            click.echo(
                "⚠️  Store this token securely - it cannot be recovered!")
    else:
        click.echo(f"❌ {message}", err=True)
        sys.exit(1)


@cli.command()
@click.option('--username', '-u', required=True, help='Username to delete')
@click.option('--yes', is_flag=True, help='Skip confirmation prompt')
@click.pass_context
def delete_user(ctx, username, yes):
    """Delete a user"""
    if not init_app(ctx.obj.get('config_path')):
        sys.exit(1)

    if not yes:
        if not click.confirm(f'Are you sure you want to delete user "{username}"?'):
            click.echo("Cancelled.")
            return

    success, message = user_manager.delete_user(username)

    if success:
        click.echo(f"✅ {message}")
    else:
        click.echo(f"❌ {message}", err=True)
        sys.exit(1)


@cli.command()
@click.option('--status', help='Filter by status (active, suspended, expired)')
@click.pass_context
def list_users(ctx, status):
    """List all users"""
    if not init_app(ctx.obj.get('config_path')):
        sys.exit(1)

    users = user_manager.list_users(status=status)

    if not users:
        click.echo("No users found.")
        return

    # Prepare table data
    headers = ['Username', 'Protocols', 'Quota',
               'Usage', 'Usage %', 'Status', 'Created']
    rows = []

    for user in users:
        usage_percent = (user['usage_bytes'] / user['quota_bytes']
                         * 100) if user['quota_bytes'] > 0 else 0

        rows.append([
            user['username'],
            user['protocols'],
            format_bytes(user['quota_bytes']),
            format_bytes(user['usage_bytes']),
            f"{usage_percent:.1f}%",
            user['status'],
            user['created_at'][:10] if user['created_at'] else 'N/A'
        ])

    click.echo(tabulate(rows, headers=headers, tablefmt='grid'))
    click.echo(f"\nTotal users: {len(users)}")


@cli.command()
@click.option('--username', '-u', required=True, help='Username')
@click.pass_context
def user_info(ctx, username):
    """Show detailed user information"""
    if not init_app(ctx.obj.get('config_path')):
        sys.exit(1)

    user = user_manager.get_user(username)

    if not user:
        click.echo(f"❌ User '{username}' not found", err=True)
        sys.exit(1)

    # Get quota usage
    quota_info = user_manager.get_quota_usage(username)

    click.echo(f"\n{'='*60}")
    click.echo(f"User Information: {username}")
    click.echo(f"{'='*60}\n")

    click.echo(f"Status:          {user['status']}")
    click.echo(f"Protocols:       {user['protocols']}")
    click.echo(f"Quota:           {format_bytes(user['quota_bytes'])}")
    click.echo(f"Usage:           {format_bytes(user['usage_bytes'])}")
    click.echo(
        f"Remaining:       {format_bytes(quota_info['remaining_bytes'])}")
    click.echo(f"Usage Percent:   {quota_info['usage_percent']:.2f}%")
    click.echo(f"Created:         {user['created_at']}")
    click.echo(f"Last Login:      {user['last_login'] or 'Never'}")
    click.echo(f"Last IP:         {user['last_ip'] or 'N/A'}")

    if user['expires_at']:
        click.echo(f"Expires:         {user['expires_at']}")

    click.echo()


@cli.command()
@click.option('--username', '-u', required=True, help='Username')
@click.option('--quota', '-q', required=True, help='New quota (e.g., 100GB, 50MB)')
@click.pass_context
def set_quota(ctx, username, quota):
    """Set user bandwidth quota"""
    if not init_app(ctx.obj.get('config_path')):
        sys.exit(1)

    # Parse quota
    try:
        quota_bytes = parse_quota_string(quota)
    except ValueError as e:
        click.echo(f"❌ {e}", err=True)
        sys.exit(1)

    success, message = user_manager.set_quota(username, quota_bytes)

    if success:
        click.echo(f"✅ {message}")
    else:
        click.echo(f"❌ {message}", err=True)
        sys.exit(1)


@cli.command()
@click.option('--username', '-u', help='Username (show for specific user)')
@click.pass_context
def quota_usage(ctx, username):
    """Show quota usage"""
    if not init_app(ctx.obj.get('config_path')):
        sys.exit(1)

    if username:
        # Show for specific user
        quota_info = user_manager.get_quota_usage(username)

        if not quota_info:
            click.echo(f"❌ User '{username}' not found", err=True)
            sys.exit(1)

        click.echo(f"\n{'='*60}")
        click.echo(f"Quota Usage: {username}")
        click.echo(f"{'='*60}\n")
        click.echo(f"Quota:       {format_bytes(quota_info['quota_bytes'])}")
        click.echo(f"Used:        {format_bytes(quota_info['usage_bytes'])}")
        click.echo(
            f"Remaining:   {format_bytes(quota_info['remaining_bytes'])}")
        click.echo(f"Usage:       {quota_info['usage_percent']:.2f}%")
        click.echo(f"Status:      {quota_info['status']}\n")
    else:
        # Show for all users
        users = user_manager.list_users()

        if not users:
            click.echo("No users found.")
            return

        headers = ['Username', 'Quota', 'Used',
                   'Remaining', 'Usage %', 'Status']
        rows = []

        for user in users:
            quota_info = user_manager.get_quota_usage(user['username'])
            rows.append([
                user['username'],
                format_bytes(quota_info['quota_bytes']),
                format_bytes(quota_info['usage_bytes']),
                format_bytes(quota_info['remaining_bytes']),
                f"{quota_info['usage_percent']:.1f}%",
                quota_info['status']
            ])

        click.echo(tabulate(rows, headers=headers, tablefmt='grid'))


@cli.command()
@click.option('--username', '-u', required=True, help='Username')
@click.option('--yes', is_flag=True, help='Skip confirmation prompt')
@click.pass_context
def reset_usage(ctx, username, yes):
    """Reset user usage counter"""
    if not init_app(ctx.obj.get('config_path')):
        sys.exit(1)

    if not yes:
        if not click.confirm(f'Reset usage counter for user "{username}"?'):
            click.echo("Cancelled.")
            return

    success, message = user_manager.reset_usage(username)

    if success:
        click.echo(f"✅ {message}")
    else:
        click.echo(f"❌ {message}", err=True)
        sys.exit(1)


@cli.command()
@click.option('--username', '-u', required=True, help='Username')
@click.pass_context
def suspend_user(ctx, username):
    """Suspend a user account"""
    if not init_app(ctx.obj.get('config_path')):
        sys.exit(1)

    success, message = user_manager.suspend_user(username)

    if success:
        click.echo(f"✅ {message}")
    else:
        click.echo(f"❌ {message}", err=True)
        sys.exit(1)


@cli.command()
@click.option('--username', '-u', required=True, help='Username')
@click.pass_context
def resume_user(ctx, username):
    """Resume a suspended user account"""
    if not init_app(ctx.obj.get('config_path')):
        sys.exit(1)

    success, message = user_manager.resume_user(username)

    if success:
        click.echo(f"✅ {message}")
    else:
        click.echo(f"❌ {message}", err=True)
        sys.exit(1)


@cli.command()
@click.pass_context
def status(ctx):
    """Show system status"""
    if not init_app(ctx.obj.get('config_path')):
        sys.exit(1)

    click.echo(f"\n{'='*60}")
    click.echo("VPS Proxy Kit Status")
    click.echo(f"{'='*60}\n")

    # Database stats
    stats = db.get_stats()

    click.echo(f"Active Users:        {stats['active_users']}")
    click.echo(f"Suspended Users:     {stats['suspended_users']}")
    click.echo(f"Active Sessions:     {stats['active_sessions']}")
    click.echo(
        f"Total Usage:         {format_bytes(stats['total_usage_bytes'])}")
    click.echo(f"Database Size:       {format_bytes(stats['db_size_bytes'])}")

    click.echo(
        f"\nServer:              {config.server.hostname} ({config.server.external_ip})")
    click.echo(
        f"SOCKS5:              {'Enabled' if config.socks5.enabled else 'Disabled'} (port {config.socks5.port})")
    click.echo(
        f"HTTPS Proxy:         {'Enabled' if config.https.enabled else 'Disabled'} (port {config.https.port})")
    click.echo(
        f"Metrics:             {'Enabled' if config.monitoring.metrics_enabled else 'Disabled'}")

    click.echo()


@cli.command()
@click.pass_context
def menu(ctx):
    """Launch interactive menu"""
    click.echo("\n🚀 VPS Proxy Kit Interactive Menu")
    click.echo("\nThis feature is coming soon!")
    click.echo(
        "For now, use the CLI commands directly. Run 'vpk --help' for options.\n")


def main():
    """Main entry point"""
    try:
        cli(obj={})
    except KeyboardInterrupt:
        click.echo("\n\nInterrupted by user")
        sys.exit(130)
    except Exception as e:
        click.echo(f"\n❌ Error: {e}", err=True)
        sys.exit(1)


if __name__ == '__main__':
    main()
