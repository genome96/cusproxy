"""
Firewall management module

Manages UFW/nftables firewall rules.
"""

from typing import List, Tuple
from vpk.utils import run_command


class FirewallManager:
    """Manage firewall rules"""

    def __init__(self):
        """Initialize firewall manager"""
        self.backend = self._detect_backend()

    def _detect_backend(self) -> str:
        """Detect firewall backend (ufw or nftables)"""
        try:
            run_command(['which', 'ufw'])
            return 'ufw'
        except:
            pass

        try:
            run_command(['which', 'nft'])
            return 'nftables'
        except:
            pass

        return 'none'

    def allow_port(self, port: int, protocol: str = 'tcp', comment: str = '') -> Tuple[bool, str]:
        """
        Allow port through firewall

        Args:
            port: Port number
            protocol: Protocol (tcp or udp)
            comment: Optional comment

        Returns:
            Tuple of (success, message)
        """
        if self.backend == 'ufw':
            try:
                cmd = ['ufw', 'allow', f'{port}/{protocol}']
                if comment:
                    cmd.extend(['comment', comment])
                run_command(cmd)
                return True, f"Allowed {port}/{protocol}"
            except Exception as e:
                return False, str(e)

        return False, "Firewall backend not supported"

    def deny_port(self, port: int, protocol: str = 'tcp') -> Tuple[bool, str]:
        """
        Deny port through firewall

        Args:
            port: Port number
            protocol: Protocol (tcp or udp)

        Returns:
            Tuple of (success, message)
        """
        if self.backend == 'ufw':
            try:
                run_command(['ufw', 'deny', f'{port}/{protocol}'])
                return True, f"Denied {port}/{protocol}"
            except Exception as e:
                return False, str(e)

        return False, "Firewall backend not supported"

    def status(self) -> str:
        """
        Get firewall status

        Returns:
            Status output
        """
        if self.backend == 'ufw':
            try:
                code, stdout, stderr = run_command(
                    ['ufw', 'status', 'verbose'])
                return stdout
            except:
                return "Error getting firewall status"

        return "Firewall backend not supported"
