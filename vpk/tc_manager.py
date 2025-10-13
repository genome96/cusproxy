"""
Traffic control (tc) management module

Provides bandwidth shaping and limiting using Linux tc (traffic control).
"""

from typing import Tuple, Optional
from vpk.utils import run_command


class TCManager:
    """Manage traffic control rules for bandwidth shaping"""

    def __init__(self, interface: str = "eth0"):
        """
        Initialize TC manager

        Args:
            interface: Network interface to apply rules
        """
        self.interface = interface

    def setup_root_qdisc(self) -> Tuple[bool, str]:
        """
        Set up root qdisc (HTB - Hierarchical Token Bucket)

        Returns:
            Tuple of (success, message)
        """
        try:
            # Delete existing qdisc
            run_command(['tc', 'qdisc', 'del', 'dev',
                        self.interface, 'root'], check=False)

            # Add HTB root qdisc
            run_command([
                'tc', 'qdisc', 'add', 'dev', self.interface, 'root',
                'handle', '1:', 'htb', 'default', '30'
            ])

            return True, f"Root qdisc configured on {self.interface}"
        except Exception as e:
            return False, str(e)

    def add_user_class(self, user_id: int, rate_limit: str) -> Tuple[bool, str]:
        """
        Add traffic class for user

        Args:
            user_id: User ID (used as class ID)
            rate_limit: Rate limit (e.g., '10mbit', '1mbit')

        Returns:
            Tuple of (success, message)
        """
        try:
            class_id = f"1:{user_id}"

            # Add class
            run_command([
                'tc', 'class', 'add', 'dev', self.interface,
                'parent', '1:', 'classid', class_id, 'htb',
                'rate', rate_limit, 'ceil', rate_limit
            ])

            # Add SFQ qdisc to class
            run_command([
                'tc', 'qdisc', 'add', 'dev', self.interface,
                'parent', class_id, 'handle', f"{user_id}:",
                'sfq', 'perturb', '10'
            ])

            return True, f"Traffic class added for user {user_id}: {rate_limit}"
        except Exception as e:
            return False, str(e)

    def remove_user_class(self, user_id: int) -> Tuple[bool, str]:
        """
        Remove traffic class for user

        Args:
            user_id: User ID

        Returns:
            Tuple of (success, message)
        """
        try:
            class_id = f"1:{user_id}"

            # Remove class
            run_command([
                'tc', 'class', 'del', 'dev', self.interface,
                'classid', class_id
            ], check=False)

            return True, f"Traffic class removed for user {user_id}"
        except Exception as e:
            return False, str(e)

    def show_classes(self) -> Optional[str]:
        """
        Show all traffic classes

        Returns:
            tc output or None
        """
        try:
            code, stdout, stderr = run_command([
                'tc', '-s', 'class', 'show', 'dev', self.interface
            ])
            return stdout
        except Exception:
            return None


# Note: Per-connection bandwidth limiting requires marking packets
# with iptables/nftables and then using tc filters to match marks.
# This is complex and requires cooperation with the proxy server.
#
# For simpler per-user limits, use Squid's delay_pools or
# Dante's bandwidth configuration options.
