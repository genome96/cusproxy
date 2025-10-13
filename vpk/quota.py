"""
Quota enforcement module

Monitors user bandwidth usage and suspends accounts when quota exceeded.
"""

import time
from typing import List, Dict
from datetime import datetime

from vpk.config import Config
from vpk.db import Database
from vpk.users import UserManager, format_bytes
from vpk.utils import setup_logging


class QuotaEnforcer:
    """Enforce per-user bandwidth quotas"""

    def __init__(self, db: Database, config: Config):
        """
        Initialize quota enforcer

        Args:
            db: Database instance
            config: Configuration instance
        """
        self.db = db
        self.config = config
        self.user_manager = UserManager(db, config)
        self.logger = setup_logging(
            config.logging.directory, config.logging.level)

    def check_quotas(self) -> Dict[str, List[str]]:
        """
        Check all user quotas and enforce limits

        Returns:
            Dictionary with lists of warned and suspended users
        """
        warned_users = []
        suspended_users = []

        # Get all active users
        users = self.db.fetchall(
            "SELECT id, username, quota_bytes, usage_bytes FROM users WHERE status = 'active'"
        )

        for user in users:
            username = user['username']
            quota = user['quota_bytes']
            usage = user['usage_bytes']

            if quota <= 0:
                continue  # Unlimited quota

            usage_percent = (usage / quota) * 100

            # Check if over quota
            if usage >= quota:
                self.logger.warning(
                    f"User {username} exceeded quota: {usage}/{quota} bytes")

                # Suspend user
                success, message = self.user_manager.suspend_user(username)
                if success:
                    suspended_users.append(username)
                    self.logger.info(
                        f"Suspended user {username} due to quota exceeded")

                    # TODO: Send notification email if configured

            # Check if approaching quota (warning threshold)
            elif usage_percent >= self.config.quotas.warning_threshold_percent:
                self.logger.info(
                    f"User {username} approaching quota: {usage_percent:.1f}% "
                    f"({format_bytes(usage)} / {format_bytes(quota)})"
                )
                warned_users.append(username)

                # TODO: Send warning email if configured

        return {
            'warned': warned_users,
            'suspended': suspended_users
        }

    def run_daemon(self):
        """Run quota enforcer as daemon"""
        self.logger.info("Starting quota enforcer daemon...")
        self.logger.info(
            f"Check interval: {self.config.quotas.check_interval_seconds} seconds")

        while True:
            try:
                if self.config.quotas.enforcement_enabled:
                    result = self.check_quotas()

                    if result['suspended']:
                        self.logger.warning(
                            f"Suspended users: {', '.join(result['suspended'])}")

                    if result['warned']:
                        self.logger.info(
                            f"Warned users: {', '.join(result['warned'])}")

                time.sleep(self.config.quotas.check_interval_seconds)

            except KeyboardInterrupt:
                self.logger.info("Quota enforcer stopped by user")
                break
            except Exception as e:
                self.logger.error(f"Error in quota enforcer: {e}")
                time.sleep(60)


def main():
    """Main entry point for quota enforcer service"""
    import sys
    import argparse
    from vpk.config import Config
    from vpk.db import Database

    parser = argparse.ArgumentParser(description='VPK Quota Enforcer')
    parser.add_argument('--daemon', action='store_true', help='Run as daemon')
    parser.add_argument('--force', action='store_true',
                        help='Force immediate check')
    args = parser.parse_args()

    # Load config
    config = Config()

    # Initialize database
    db = Database(config.database.path, config.database.encryption_key_path)

    # Create enforcer
    enforcer = QuotaEnforcer(db, config)

    if args.daemon:
        enforcer.run_daemon()
    else:
        # Single run
        result = enforcer.check_quotas()
        print(
            f"Warned: {len(result['warned'])}, Suspended: {len(result['suspended'])}")


if __name__ == '__main__':
    main()
