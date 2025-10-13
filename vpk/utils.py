"""
Utility functions for VPS Proxy Kit
"""

import os
import sys
import subprocess
from typing import Optional, List, Tuple
import logging


def setup_logging(log_dir: str, log_level: str = "INFO") -> logging.Logger:
    """
    Set up logging configuration

    Args:
        log_dir: Directory for log files
        log_level: Logging level

    Returns:
        Logger instance
    """
    os.makedirs(log_dir, exist_ok=True)

    logger = logging.getLogger('vpk')
    logger.setLevel(getattr(logging, log_level.upper()))

    # File handler
    fh = logging.FileHandler(os.path.join(log_dir, 'vpk.log'))
    fh.setLevel(logging.DEBUG)

    # Console handler
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.INFO)

    # Formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)

    logger.addHandler(fh)
    logger.addHandler(ch)

    return logger


def run_command(cmd: List[str], capture_output: bool = True, check: bool = True) -> Tuple[int, str, str]:
    """
    Run shell command

    Args:
        cmd: Command and arguments as list
        capture_output: Capture stdout and stderr
        check: Raise exception on non-zero exit

    Returns:
        Tuple of (returncode, stdout, stderr)
    """
    result = subprocess.run(
        cmd,
        capture_output=capture_output,
        text=True,
        check=check
    )

    return result.returncode, result.stdout, result.stderr


def is_root() -> bool:
    """Check if running as root"""
    return os.geteuid() == 0


def get_public_ip() -> Optional[str]:
    """
    Get public IP address

    Returns:
        Public IP or None if failed
    """
    try:
        import requests
        response = requests.get('https://api.ipify.org', timeout=5)
        if response.status_code == 200:
            return response.text.strip()
    except:
        pass

    return None


def check_port_available(port: int) -> bool:
    """
    Check if port is available

    Args:
        port: Port number

    Returns:
        True if available
    """
    import socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.bind(('', port))
            return True
        except OSError:
            return False


def validate_ip(ip: str) -> bool:
    """
    Validate IP address

    Args:
        ip: IP address string

    Returns:
        True if valid
    """
    import ipaddress
    try:
        ipaddress.ip_address(ip)
        return True
    except ValueError:
        return False
