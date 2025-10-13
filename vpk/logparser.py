"""
Log parser module for VPS Proxy Kit

Parses proxy server logs (Dante, Squid) and updates per-user bandwidth counters.
"""

import re
import time
from typing import Dict, Optional
from datetime import datetime
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from vpk.config import Config
from vpk.db import Database
from vpk.utils import setup_logging


class LogParser:
    """Parse proxy logs and update usage counters"""

    def __init__(self, db: Database, config: Config):
        """
        Initialize log parser

        Args:
            db: Database instance
            config: Configuration instance
        """
        self.db = db
        self.config = config
        self.logger = setup_logging(
            config.logging.directory, config.logging.level)

        # Log file paths
        self.dante_log = f"{config.logging.directory}/danted.log"
        self.squid_log = f"{config.logging.directory}/squid_access.log"

        # Regex patterns for log parsing
        # Dante: extract username and bytes transferred
        self.dante_pattern = re.compile(
            r'transfer\s+.*user\s+(\S+).*bytes\s+in:\s+(\d+)\s+out:\s+(\d+)'
        )

        # Squid: extract username and bytes (from custom logformat)
        self.squid_pattern = re.compile(
            r'(\S+)\s+\S+\s+(\d+)\s+\S+\s+\S+\s+(\d+)'
        )

    def parse_dante_line(self, line: str) -> Optional[Dict]:
        """
        Parse Dante log line

        Args:
            line: Log line

        Returns:
            Dictionary with username and bytes or None
        """
        match = self.dante_pattern.search(line)
        if match:
            username = match.group(1)
            bytes_in = int(match.group(2))
            bytes_out = int(match.group(3))

            return {
                'username': username,
                'protocol': 'socks',
                'bytes_in': bytes_in,
                'bytes_out': bytes_out,
                'total_bytes': bytes_in + bytes_out
            }
        return None

    def parse_squid_line(self, line: str) -> Optional[Dict]:
        """
        Parse Squid log line

        Args:
            line: Log line

        Returns:
            Dictionary with username and bytes or None
        """
        match = self.squid_pattern.search(line)
        if match:
            username = match.group(1)
            # In Squid access.log, bytes are response size
            bytes_transferred = int(match.group(3))

            return {
                'username': username,
                'protocol': 'https',
                'bytes_in': 0,
                'bytes_out': bytes_transferred,
                'total_bytes': bytes_transferred
            }
        return None

    def update_user_usage(self, username: str, bytes_amount: int, protocol: str):
        """
        Update user usage in database

        Args:
            username: Username
            bytes_amount: Number of bytes to add
            protocol: Protocol (socks or https)
        """
        try:
            # Get user ID
            user = self.db.fetchone(
                "SELECT id FROM users WHERE username = ?", (username,))
            if not user:
                return

            user_id = user['id']

            # Update usage counter
            self.db.execute(
                "UPDATE users SET usage_bytes = usage_bytes + ? WHERE id = ?",
                (bytes_amount, user_id)
            )

            # Log usage
            self.db.execute(
                """
                INSERT INTO usage_logs (user_id, protocol, bytes_in, bytes_out)
                VALUES (?, ?, ?, ?)
                """,
                (user_id, protocol, 0, bytes_amount)
            )

            self.logger.debug(
                f"Updated usage for {username}: +{bytes_amount} bytes ({protocol})")

        except Exception as e:
            self.logger.error(f"Failed to update usage for {username}: {e}")

    def watch_logs(self):
        """Watch log files for changes and parse new lines"""
        self.logger.info("Starting log parser in watch mode...")

        # TODO: Implement file watching with watchdog
        # For now, use simple polling
        while True:
            try:
                # Parse Dante logs
                if self.config.socks5.enabled:
                    self.parse_log_file(self.dante_log, 'dante')

                # Parse Squid logs
                if self.config.https.enabled:
                    self.parse_log_file(self.squid_log, 'squid')

                time.sleep(60)  # Check every minute

            except KeyboardInterrupt:
                self.logger.info("Log parser stopped by user")
                break
            except Exception as e:
                self.logger.error(f"Error in log parser: {e}")
                time.sleep(60)

    def parse_log_file(self, log_path: str, log_type: str):
        """
        Parse entire log file (for batch processing)

        Args:
            log_path: Path to log file
            log_type: Type of log (dante or squid)
        """
        # This is a simplified implementation
        # In production, you'd track the last read position
        pass


def main():
    """Main entry point for log parser service"""
    import sys
    from vpk.config import Config
    from vpk.db import Database

    # Load config
    config = Config()

    # Initialize database
    db = Database(config.database.path, config.database.encryption_key_path)

    # Start parser
    parser = LogParser(db, config)
    parser.watch_logs()


if __name__ == '__main__':
    main()
