"""
Proxy backend management module

Handles starting, stopping, and reloading proxy services (Dante, Squid).
"""

import subprocess
from typing import Optional, Tuple
from vpk.config import Config
from vpk.utils import run_command


class ProxyBackend:
    """Base class for proxy backend management"""

    def __init__(self, config: Config):
        self.config = config

    def start(self) -> Tuple[bool, str]:
        """Start proxy service"""
        raise NotImplementedError

    def stop(self) -> Tuple[bool, str]:
        """Stop proxy service"""
        raise NotImplementedError

    def reload(self) -> Tuple[bool, str]:
        """Reload proxy configuration"""
        raise NotImplementedError

    def status(self) -> Tuple[bool, str]:
        """Get service status"""
        raise NotImplementedError


class DanteBackend(ProxyBackend):
    """Dante SOCKS5 server backend"""

    SERVICE_NAME = "vpk-dante"

    def start(self) -> Tuple[bool, str]:
        try:
            run_command(['systemctl', 'start', self.SERVICE_NAME])
            return True, f"{self.SERVICE_NAME} started"
        except Exception as e:
            return False, str(e)

    def stop(self) -> Tuple[bool, str]:
        try:
            run_command(['systemctl', 'stop', self.SERVICE_NAME])
            return True, f"{self.SERVICE_NAME} stopped"
        except Exception as e:
            return False, str(e)

    def reload(self) -> Tuple[bool, str]:
        try:
            run_command(['systemctl', 'reload', self.SERVICE_NAME])
            return True, f"{self.SERVICE_NAME} reloaded"
        except Exception as e:
            return False, str(e)

    def status(self) -> Tuple[bool, str]:
        try:
            code, stdout, stderr = run_command(
                ['systemctl', 'is-active', self.SERVICE_NAME],
                check=False
            )
            is_running = stdout.strip() == 'active'
            return is_running, stdout.strip()
        except Exception as e:
            return False, str(e)


class SquidBackend(ProxyBackend):
    """Squid HTTP/HTTPS proxy backend"""

    SERVICE_NAME = "vpk-squid"

    def start(self) -> Tuple[bool, str]:
        try:
            run_command(['systemctl', 'start', self.SERVICE_NAME])
            return True, f"{self.SERVICE_NAME} started"
        except Exception as e:
            return False, str(e)

    def stop(self) -> Tuple[bool, str]:
        try:
            run_command(['systemctl', 'stop', self.SERVICE_NAME])
            return True, f"{self.SERVICE_NAME} stopped"
        except Exception as e:
            return False, str(e)

    def reload(self) -> Tuple[bool, str]:
        try:
            run_command(['systemctl', 'reload', self.SERVICE_NAME])
            return True, f"{self.SERVICE_NAME} reloaded"
        except Exception as e:
            return False, str(e)

    def status(self) -> Tuple[bool, str]:
        try:
            code, stdout, stderr = run_command(
                ['systemctl', 'is-active', self.SERVICE_NAME],
                check=False
            )
            is_running = stdout.strip() == 'active'
            return is_running, stdout.strip()
        except Exception as e:
            return False, str(e)


def get_backend(backend_type: str, config: Config) -> Optional[ProxyBackend]:
    """
    Get proxy backend instance

    Args:
        backend_type: Backend type ('dante' or 'squid')
        config: Configuration instance

    Returns:
        Backend instance or None
    """
    backends = {
        'dante': DanteBackend,
        'squid': SquidBackend,
    }

    backend_class = backends.get(backend_type.lower())
    if backend_class:
        return backend_class(config)

    return None
