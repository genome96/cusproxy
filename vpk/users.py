"""
User management module with Argon2id password hashing

Handles user creation, authentication, and management with strong security.
"""

import secrets
import hashlib
from typing import Optional, List, Dict, Any, Tuple
from datetime import datetime, timedelta
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError, VerificationError

from vpk.db import Database
from vpk.config import Config


class UserManager:
    """User management with secure authentication"""

    def __init__(self, db: Database, config: Config):
        """
        Initialize user manager

        Args:
            db: Database instance
            config: Configuration instance
        """
        self.db = db
        self.config = config

        # Initialize Argon2 password hasher with config parameters
        self.ph = PasswordHasher(
            time_cost=config.security.argon2_time_cost,
            memory_cost=config.security.argon2_memory_cost,
            parallelism=config.security.argon2_parallelism,
            hash_len=32,
            salt_len=16,
        )

    def create_user(
        self,
        username: str,
        password: Optional[str] = None,
        token_auth: bool = False,
        protocols: List[str] = ['socks', 'https'],
        quota_bytes: int = 107374182400,  # 100 GB default
        expires_at: Optional[datetime] = None,
    ) -> Tuple[bool, str, Optional[str]]:
        """
        Create a new user

        Args:
            username: Username (must be unique)
            password: Plain text password (required if not token_auth)
            token_auth: Use token authentication instead of password
            protocols: List of allowed protocols ('socks', 'https')
            quota_bytes: Bandwidth quota in bytes
            expires_at: Optional expiration date

        Returns:
            Tuple of (success, message, token if token_auth)
        """
        # Validate username
        if not username or len(username) < 3:
            return False, "Username must be at least 3 characters", None

        if not username.isalnum():
            return False, "Username must be alphanumeric", None

        # Check if user exists
        existing = self.db.fetchone(
            "SELECT id FROM users WHERE username = ?", (username,))
        if existing:
            return False, f"User '{username}' already exists", None

        # Validate protocols
        valid_protocols = {'socks', 'https'}
        protocols = [p.lower() for p in protocols]
        if not all(p in valid_protocols for p in protocols):
            return False, f"Invalid protocols. Must be one of: {valid_protocols}", None

        protocols_str = ','.join(protocols)

        # Handle authentication
        password_hash = None
        token_hash = None
        token = None

        if token_auth:
            # Generate random token
            token = 'tok_' + secrets.token_urlsafe(32)
            # Hash token with SHA-256 for storage
            token_hash = hashlib.sha256(token.encode()).hexdigest()
        else:
            if not password:
                return False, "Password is required when token_auth is False", None

            # Validate password strength
            if len(password) < 8:
                return False, "Password must be at least 8 characters", None

            # Hash password with Argon2id
            try:
                password_hash = self.ph.hash(password)
            except Exception as e:
                return False, f"Failed to hash password: {e}", None

        # Convert expiration to string if provided
        expires_str = expires_at.isoformat() if expires_at else None

        # Insert user
        try:
            self.db.execute(
                """
                INSERT INTO users (username, password_hash, token_hash, protocols, quota_bytes, expires_at)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (username, password_hash, token_hash,
                 protocols_str, quota_bytes, expires_str)
            )

            # Log audit event
            self.db.log_audit(
                actor='system',
                action='create_user',
                target=username,
                details=f"protocols={protocols_str}, quota={quota_bytes}, token_auth={token_auth}"
            )

            msg = f"User '{username}' created successfully"
            if token:
                msg += f"\nGenerated token: {token}\nStore this securely - it cannot be recovered"

            return True, msg, token

        except Exception as e:
            return False, f"Failed to create user: {e}", None

    def authenticate(self, username: str, credential: str, protocol: str, source_ip: Optional[str] = None) -> Tuple[bool, Optional[Dict[str, Any]]]:
        """
        Authenticate user with password or token

        Args:
            username: Username
            credential: Password or token
            protocol: Protocol being accessed ('socks' or 'https')
            source_ip: Source IP address for logging

        Returns:
            Tuple of (success, user_data dict or None)
        """
        # Check rate limiting
        if not self._check_rate_limit(source_ip):
            self._log_auth_failure(username, source_ip, protocol)
            return False, None

        # Fetch user
        user = self.db.fetchone(
            "SELECT * FROM users WHERE username = ?",
            (username,)
        )

        if not user:
            self._log_auth_failure(username, source_ip, protocol)
            return False, None

        # Check if user is active
        if user['status'] != 'active':
            return False, None

        # Check if expired
        if user['expires_at']:
            expires = datetime.fromisoformat(user['expires_at'])
            if datetime.now() > expires:
                # Mark as expired
                self.db.execute(
                    "UPDATE users SET status = 'expired' WHERE id = ?", (user['id'],))
                return False, None

        # Check if protocol is allowed
        allowed_protocols = user['protocols'].split(',')
        if protocol not in allowed_protocols:
            return False, None

        # Verify credential
        authenticated = False

        if user['token_hash']:
            # Token authentication
            credential_hash = hashlib.sha256(credential.encode()).hexdigest()
            authenticated = secrets.compare_digest(
                credential_hash, user['token_hash'])
        elif user['password_hash']:
            # Password authentication
            try:
                self.ph.verify(user['password_hash'], credential)
                authenticated = True

                # Check if rehashing is needed (parameters changed)
                if self.ph.check_needs_rehash(user['password_hash']):
                    new_hash = self.ph.hash(credential)
                    self.db.execute(
                        "UPDATE users SET password_hash = ? WHERE id = ?",
                        (new_hash, user['id'])
                    )
            except (VerifyMismatchError, VerificationError):
                authenticated = False

        if not authenticated:
            self._log_auth_failure(username, source_ip, protocol)
            return False, None

        # Update last login
        self.db.execute(
            "UPDATE users SET last_login = CURRENT_TIMESTAMP, last_ip = ? WHERE id = ?",
            (source_ip, user['id'])
        )

        return True, dict(user)

    def _check_rate_limit(self, source_ip: Optional[str]) -> bool:
        """
        Check if IP is rate limited

        Args:
            source_ip: Source IP address

        Returns:
            True if allowed, False if rate limited
        """
        if not source_ip:
            return True

        # Check failures in last window
        window_start = datetime.now() - timedelta(seconds=self.config.security.auth_failure_window)

        result = self.db.fetchone(
            """
            SELECT COUNT(*) as count FROM auth_failures
            WHERE source_ip = ? AND timestamp > ?
            """,
            (source_ip, window_start.isoformat())
        )

        failure_count = result['count'] if result else 0
        return failure_count < self.config.security.max_auth_failures

    def _log_auth_failure(self, username: str, source_ip: Optional[str], protocol: str) -> None:
        """Log authentication failure"""
        self.db.execute(
            "INSERT INTO auth_failures (username, source_ip, protocol) VALUES (?, ?, ?)",
            (username, source_ip, protocol)
        )

    def delete_user(self, username: str) -> Tuple[bool, str]:
        """
        Delete a user

        Args:
            username: Username to delete

        Returns:
            Tuple of (success, message)
        """
        user = self.db.fetchone(
            "SELECT id FROM users WHERE username = ?", (username,))
        if not user:
            return False, f"User '{username}' not found"

        try:
            self.db.execute(
                "DELETE FROM users WHERE username = ?", (username,))

            # Log audit event
            self.db.log_audit(
                actor='system',
                action='delete_user',
                target=username
            )

            return True, f"User '{username}' deleted successfully"
        except Exception as e:
            return False, f"Failed to delete user: {e}"

    def list_users(self, status: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        List all users

        Args:
            status: Filter by status (optional)

        Returns:
            List of user dictionaries
        """
        if status:
            users = self.db.fetchall(
                "SELECT * FROM users WHERE status = ? ORDER BY username",
                (status,)
            )
        else:
            users = self.db.fetchall("SELECT * FROM users ORDER BY username")

        # Remove sensitive fields
        for user in users:
            user.pop('password_hash', None)
            user.pop('token_hash', None)

        return users

    def get_user(self, username: str) -> Optional[Dict[str, Any]]:
        """
        Get user information

        Args:
            username: Username

        Returns:
            User dictionary or None
        """
        user = self.db.fetchone(
            "SELECT * FROM users WHERE username = ?", (username,))
        if user:
            # Remove sensitive fields
            user.pop('password_hash', None)
            user.pop('token_hash', None)
        return user

    def update_password(self, username: str, new_password: str) -> Tuple[bool, str]:
        """
        Update user password

        Args:
            username: Username
            new_password: New password

        Returns:
            Tuple of (success, message)
        """
        user = self.db.fetchone(
            "SELECT id FROM users WHERE username = ?", (username,))
        if not user:
            return False, f"User '{username}' not found"

        if len(new_password) < 8:
            return False, "Password must be at least 8 characters"

        try:
            password_hash = self.ph.hash(new_password)
            self.db.execute(
                "UPDATE users SET password_hash = ?, token_hash = NULL WHERE username = ?",
                (password_hash, username)
            )

            # Log audit event
            self.db.log_audit(
                actor='system',
                action='update_password',
                target=username
            )

            return True, f"Password updated for user '{username}'"
        except Exception as e:
            return False, f"Failed to update password: {e}"

    def set_quota(self, username: str, quota_bytes: int) -> Tuple[bool, str]:
        """
        Set user quota

        Args:
            username: Username
            quota_bytes: Quota in bytes

        Returns:
            Tuple of (success, message)
        """
        user = self.db.fetchone(
            "SELECT id FROM users WHERE username = ?", (username,))
        if not user:
            return False, f"User '{username}' not found"

        try:
            self.db.execute(
                "UPDATE users SET quota_bytes = ? WHERE username = ?",
                (quota_bytes, username)
            )

            # Log audit event
            self.db.log_audit(
                actor='system',
                action='set_quota',
                target=username,
                details=f"quota={quota_bytes}"
            )

            return True, f"Quota set to {quota_bytes} bytes for user '{username}'"
        except Exception as e:
            return False, f"Failed to set quota: {e}"

    def reset_usage(self, username: str) -> Tuple[bool, str]:
        """
        Reset user usage counter

        Args:
            username: Username

        Returns:
            Tuple of (success, message)
        """
        user = self.db.fetchone(
            "SELECT id FROM users WHERE username = ?", (username,))
        if not user:
            return False, f"User '{username}' not found"

        try:
            self.db.execute(
                "UPDATE users SET usage_bytes = 0 WHERE username = ?",
                (username,)
            )

            # Log audit event
            self.db.log_audit(
                actor='system',
                action='reset_usage',
                target=username
            )

            return True, f"Usage counter reset for user '{username}'"
        except Exception as e:
            return False, f"Failed to reset usage: {e}"

    def suspend_user(self, username: str) -> Tuple[bool, str]:
        """
        Suspend user account

        Args:
            username: Username

        Returns:
            Tuple of (success, message)
        """
        user = self.db.fetchone(
            "SELECT id FROM users WHERE username = ?", (username,))
        if not user:
            return False, f"User '{username}' not found"

        try:
            self.db.execute(
                "UPDATE users SET status = 'suspended' WHERE username = ?",
                (username,)
            )

            # Log audit event
            self.db.log_audit(
                actor='system',
                action='suspend_user',
                target=username
            )

            return True, f"User '{username}' suspended"
        except Exception as e:
            return False, f"Failed to suspend user: {e}"

    def resume_user(self, username: str) -> Tuple[bool, str]:
        """
        Resume suspended user account

        Args:
            username: Username

        Returns:
            Tuple of (success, message)
        """
        user = self.db.fetchone(
            "SELECT id FROM users WHERE username = ?", (username,))
        if not user:
            return False, f"User '{username}' not found"

        try:
            self.db.execute(
                "UPDATE users SET status = 'active' WHERE username = ?",
                (username,)
            )

            # Log audit event
            self.db.log_audit(
                actor='system',
                action='resume_user',
                target=username
            )

            return True, f"User '{username}' resumed"
        except Exception as e:
            return False, f"Failed to resume user: {e}"

    def get_quota_usage(self, username: str) -> Optional[Dict[str, Any]]:
        """
        Get quota usage for user

        Args:
            username: Username

        Returns:
            Dictionary with quota info or None
        """
        user = self.db.fetchone(
            "SELECT username, quota_bytes, usage_bytes, status FROM users WHERE username = ?",
            (username,)
        )

        if not user:
            return None

        usage_percent = (user['usage_bytes'] / user['quota_bytes']
                         * 100) if user['quota_bytes'] > 0 else 0

        return {
            'username': user['username'],
            'quota_bytes': user['quota_bytes'],
            'usage_bytes': user['usage_bytes'],
            'remaining_bytes': max(0, user['quota_bytes'] - user['usage_bytes']),
            'usage_percent': round(usage_percent, 2),
            'status': user['status'],
        }


def parse_quota_string(quota_str: str) -> int:
    """
    Parse human-readable quota string to bytes

    Args:
        quota_str: Quota string (e.g., "100GB", "50MB", "1TB")

    Returns:
        Quota in bytes
    """
    quota_str = quota_str.upper().strip()

    multipliers = {
        'TB': 1024 ** 4,
        'GB': 1024 ** 3,
        'MB': 1024 ** 2,
        'KB': 1024,
        'B': 1,
    }

    # Try matching units (check longer units first)
    for unit, multiplier in multipliers.items():
        if quota_str.endswith(unit):
            value_str = quota_str[:-len(unit)].strip()
            try:
                value = float(value_str)
                return int(value * multiplier)
            except ValueError:
                raise ValueError(f"Invalid quota format: {quota_str}. Could not parse number '{value_str}'")

    # Try parsing as plain number (bytes)
    try:
        return int(quota_str)
    except ValueError:
        raise ValueError(f"Invalid quota format: {quota_str}. Expected format: '100GB', '50MB', etc.")


def format_bytes(bytes_val: int) -> str:
    """
    Format bytes to human-readable string

    Args:
        bytes_val: Number of bytes

    Returns:
        Formatted string (e.g., "100.5 GB")
    """
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes_val < 1024.0:
            return f"{bytes_val:.2f} {unit}"
        bytes_val /= 1024.0
    return f"{bytes_val:.2f} PB"
