"""
VPS Proxy Kit - Production-ready proxy server management system

This package provides a complete solution for managing SOCKS5 and HTTP/HTTPS
proxy servers with strong authentication, encryption, quota management, and
monitoring capabilities.
"""

__version__ = "1.0.0"
__author__ = "VPS Proxy Kit Team"
__email__ = "admin@example.com"

from vpk.config import Config
from vpk.db import Database
from vpk.users import UserManager

__all__ = ["Config", "Database", "UserManager", "__version__"]
