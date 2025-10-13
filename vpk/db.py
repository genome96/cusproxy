"""
Database management module with encryption at rest

Provides encrypted SQLite database with user and usage tracking.
"""

import os
import sqlite3
from typing import Optional, List, Dict, Any
from datetime import datetime
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2
import base64
import json


class Database:
    """Encrypted SQLite database manager"""

    def __init__(self, db_path: str, encryption_key_path: str):
        """
        Initialize database with encryption

        Args:
            db_path: Path to SQLite database file
            encryption_key_path: Path to encryption key file
        """
        self.db_path = db_path
        self.encryption_key_path = encryption_key_path
        self.fernet: Optional[Fernet] = None

        # Load encryption key
        self._load_encryption_key()

        # Ensure database directory exists
        os.makedirs(os.path.dirname(db_path), exist_ok=True)

        # Initialize database
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row

        # Create tables if not exist
        self._create_tables()

    def _load_encryption_key(self) -> None:
        """Load and derive encryption key from master key file"""
        if not os.path.exists(self.encryption_key_path):
            raise RuntimeError(
                f"Encryption key not found: {self.encryption_key_path}")

        with open(self.encryption_key_path, 'rb') as f:
            master_key = f.read().strip()

        # Derive Fernet key from master key using PBKDF2
        kdf = PBKDF2(
            algorithm=hashes.SHA256(),
            length=32,
            salt=b'vpk-salt-2025',  # Static salt for deterministic key
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(master_key))
        self.fernet = Fernet(key)

    def _create_tables(self) -> None:
        """Create database tables if they don't exist"""
        cursor = self.conn.cursor()

        # Users table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT,
                token_hash TEXT,
                protocols TEXT NOT NULL,
                quota_bytes INTEGER NOT NULL,
                usage_bytes INTEGER DEFAULT 0,
                status TEXT DEFAULT 'active',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP,
                last_login TIMESTAMP,
                last_ip TEXT
            )
        """)

        # Usage logs table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS usage_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                protocol TEXT NOT NULL,
                bytes_in INTEGER DEFAULT 0,
                bytes_out INTEGER DEFAULT 0,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                source_ip TEXT,
                destination TEXT,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        """)

        # Sessions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                protocol TEXT NOT NULL,
                source_ip TEXT,
                destination TEXT,
                started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                ended_at TIMESTAMP,
                bytes_transferred INTEGER DEFAULT 0,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        """)

        # Auth failures table (for rate limiting)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS auth_failures (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT,
                source_ip TEXT NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                protocol TEXT
            )
        """)

        # Audit log table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS audit_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                actor TEXT NOT NULL,
                action TEXT NOT NULL,
                target TEXT,
                details TEXT,
                source_ip TEXT
            )
        """)

        # Create indexes
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_users_username ON users(username)")
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_users_status ON users(status)")
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_usage_logs_user_id ON usage_logs(user_id)")
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_usage_logs_timestamp ON usage_logs(timestamp)")
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_sessions_user_id ON sessions(user_id)")
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_sessions_ended_at ON sessions(ended_at)")
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_auth_failures_ip ON auth_failures(source_ip)")
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_auth_failures_timestamp ON auth_failures(timestamp)")

        self.conn.commit()

    def execute(self, query: str, params: tuple = ()) -> sqlite3.Cursor:
        """
        Execute SQL query

        Args:
            query: SQL query string
            params: Query parameters

        Returns:
            Cursor object
        """
        cursor = self.conn.cursor()
        cursor.execute(query, params)
        self.conn.commit()
        return cursor

    def fetchone(self, query: str, params: tuple = ()) -> Optional[Dict[str, Any]]:
        """
        Fetch single row

        Args:
            query: SQL query string
            params: Query parameters

        Returns:
            Dictionary of row data or None
        """
        cursor = self.conn.cursor()
        cursor.execute(query, params)
        row = cursor.fetchone()
        return dict(row) if row else None

    def fetchall(self, query: str, params: tuple = ()) -> List[Dict[str, Any]]:
        """
        Fetch all rows

        Args:
            query: SQL query string
            params: Query parameters

        Returns:
            List of dictionaries
        """
        cursor = self.conn.cursor()
        cursor.execute(query, params)
        rows = cursor.fetchall()
        return [dict(row) for row in rows]

    def encrypt_field(self, value: str) -> str:
        """
        Encrypt a field value

        Args:
            value: Plain text value

        Returns:
            Encrypted value (base64 encoded)
        """
        if not self.fernet:
            raise RuntimeError("Encryption not initialized")

        encrypted = self.fernet.encrypt(value.encode())
        return encrypted.decode()

    def decrypt_field(self, encrypted_value: str) -> str:
        """
        Decrypt a field value

        Args:
            encrypted_value: Encrypted value (base64 encoded)

        Returns:
            Decrypted plain text value
        """
        if not self.fernet:
            raise RuntimeError("Encryption not initialized")

        decrypted = self.fernet.decrypt(encrypted_value.encode())
        return decrypted.decode()

    def log_audit(self, actor: str, action: str, target: Optional[str] = None,
                  details: Optional[str] = None, source_ip: Optional[str] = None) -> None:
        """
        Log an audit event

        Args:
            actor: Who performed the action
            action: What action was performed
            target: Target of the action (optional)
            details: Additional details (optional)
            source_ip: Source IP address (optional)
        """
        self.execute(
            """
            INSERT INTO audit_log (actor, action, target, details, source_ip)
            VALUES (?, ?, ?, ?, ?)
            """,
            (actor, action, target, details, source_ip)
        )

    def cleanup_old_data(self, days: int = 30) -> Dict[str, int]:
        """
        Clean up old data based on retention policy

        Args:
            days: Number of days to retain

        Returns:
            Dictionary with count of deleted records per table
        """
        cutoff_date = datetime.now().timestamp() - (days * 86400)

        deleted = {}

        # Delete old usage logs
        cursor = self.execute(
            "DELETE FROM usage_logs WHERE timestamp < datetime(?, 'unixepoch')",
            (cutoff_date,)
        )
        deleted['usage_logs'] = cursor.rowcount

        # Delete old ended sessions
        cursor = self.execute(
            "DELETE FROM sessions WHERE ended_at IS NOT NULL AND ended_at < datetime(?, 'unixepoch')",
            (cutoff_date,)
        )
        deleted['sessions'] = cursor.rowcount

        # Delete old auth failures
        cursor = self.execute(
            "DELETE FROM auth_failures WHERE timestamp < datetime(?, 'unixepoch')",
            (cutoff_date,)
        )
        deleted['auth_failures'] = cursor.rowcount

        # Keep audit log longer (2x retention)
        audit_cutoff = datetime.now().timestamp() - (days * 2 * 86400)
        cursor = self.execute(
            "DELETE FROM audit_log WHERE timestamp < datetime(?, 'unixepoch')",
            (audit_cutoff,)
        )
        deleted['audit_log'] = cursor.rowcount

        # Vacuum database to reclaim space
        self.conn.execute("VACUUM")

        return deleted

    def get_stats(self) -> Dict[str, Any]:
        """
        Get database statistics

        Returns:
            Dictionary with statistics
        """
        stats = {}

        # User counts
        result = self.fetchone(
            "SELECT COUNT(*) as count FROM users WHERE status = 'active'")
        stats['active_users'] = result['count'] if result else 0

        result = self.fetchone(
            "SELECT COUNT(*) as count FROM users WHERE status = 'suspended'")
        stats['suspended_users'] = result['count'] if result else 0

        # Total usage
        result = self.fetchone("SELECT SUM(usage_bytes) as total FROM users")
        stats['total_usage_bytes'] = result['total'] if result and result['total'] else 0

        # Active sessions
        result = self.fetchone(
            "SELECT COUNT(*) as count FROM sessions WHERE ended_at IS NULL")
        stats['active_sessions'] = result['count'] if result else 0

        # Database size
        stats['db_size_bytes'] = os.path.getsize(
            self.db_path) if os.path.exists(self.db_path) else 0

        return stats

    def close(self) -> None:
        """Close database connection"""
        if self.conn:
            self.conn.close()

    def __enter__(self):
        """Context manager entry"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close()


def init_database(db_path: str, encryption_key_path: str) -> Database:
    """
    Initialize database

    Args:
        db_path: Path to database file
        encryption_key_path: Path to encryption key

    Returns:
        Database instance
    """
    return Database(db_path, encryption_key_path)
