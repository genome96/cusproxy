"""
Configuration management module for VPS Proxy Kit

Handles loading and saving YAML configuration files with secure defaults.
"""

import os
import yaml
from pathlib import Path
from typing import Any, Dict, Optional
from dataclasses import dataclass, field


@dataclass
class ServerConfig:
    """Server configuration"""
    external_ip: str = "127.0.0.1"
    hostname: str = "localhost"


@dataclass
class DatabaseConfig:
    """Database configuration"""
    path: str = "/opt/vps-proxy-kit/data/vpk.db"
    encryption_key_path: str = "/etc/vpk/secret.key"


@dataclass
class ProxyConfig:
    """Individual proxy configuration"""
    enabled: bool = True
    backend: str = ""
    port: int = 0
    tls_port: int = 0
    config_path: str = ""


@dataclass
class SecurityConfig:
    """Security settings"""
    argon2_time_cost: int = 4
    argon2_memory_cost: int = 65536  # 64 MB
    argon2_parallelism: int = 2
    tls_min_version: str = "1.3"
    allowed_ciphers: str = "TLS_AES_256_GCM_SHA384:TLS_CHACHA20_POLY1305_SHA256:TLS_AES_128_GCM_SHA256"
    max_auth_failures: int = 5
    auth_failure_window: int = 900  # 15 minutes


@dataclass
class LoggingConfig:
    """Logging configuration"""
    directory: str = "/var/log/vpk"
    retention_days: int = 30
    max_size_mb: int = 100
    level: str = "INFO"


@dataclass
class QuotaConfig:
    """Quota enforcement configuration"""
    check_interval_seconds: int = 300  # 5 minutes
    warning_threshold_percent: int = 80
    grace_period_hours: int = 24
    enforcement_enabled: bool = True


@dataclass
class MonitoringConfig:
    """Monitoring and metrics configuration"""
    metrics_enabled: bool = True
    metrics_port: int = 9100
    metrics_host: str = "127.0.0.1"


@dataclass
class FirewallConfig:
    """Firewall configuration"""
    ssh_port: int = 22
    allowed_ssh_ips: list = field(default_factory=list)


@dataclass
class BackupConfig:
    """Backup configuration"""
    enabled: bool = True
    directory: str = "/etc/vpk/backup"
    retention_days: int = 30
    encryption: bool = True


class Config:
    """Main configuration manager"""

    DEFAULT_CONFIG_PATH = "/etc/vpk/config.yml"

    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize configuration manager

        Args:
            config_path: Path to configuration file (default: /etc/vpk/config.yml)
        """
        self.config_path = config_path or self.DEFAULT_CONFIG_PATH
        self.data: Dict[str, Any] = {}

        # Configuration objects
        self.server = ServerConfig()
        self.database = DatabaseConfig()
        self.socks5 = ProxyConfig()
        self.https = ProxyConfig()
        self.security = SecurityConfig()
        self.logging = LoggingConfig()
        self.quotas = QuotaConfig()
        self.monitoring = MonitoringConfig()
        self.firewall = FirewallConfig()
        self.backup = BackupConfig()

        if os.path.exists(self.config_path):
            self.load()

    def load(self) -> None:
        """Load configuration from YAML file"""
        try:
            with open(self.config_path, 'r') as f:
                self.data = yaml.safe_load(f) or {}

            # Parse configuration sections
            if 'server' in self.data:
                self.server = ServerConfig(**self.data['server'])

            if 'database' in self.data:
                self.database = DatabaseConfig(**self.data['database'])

            if 'proxies' in self.data:
                if 'socks5' in self.data['proxies']:
                    self.socks5 = ProxyConfig(**self.data['proxies']['socks5'])
                if 'https' in self.data['proxies']:
                    self.https = ProxyConfig(**self.data['proxies']['https'])

            if 'security' in self.data:
                self.security = SecurityConfig(**self.data['security'])

            if 'logging' in self.data:
                self.logging = LoggingConfig(**self.data['logging'])

            if 'quotas' in self.data:
                self.quotas = QuotaConfig(**self.data['quotas'])

            if 'monitoring' in self.data:
                self.monitoring = MonitoringConfig(**self.data['monitoring'])

            if 'firewall' in self.data:
                self.firewall = FirewallConfig(**self.data['firewall'])

            if 'backup' in self.data:
                self.backup = BackupConfig(**self.data['backup'])

        except Exception as e:
            raise RuntimeError(
                f"Failed to load configuration from {self.config_path}: {e}")

    def save(self) -> None:
        """Save configuration to YAML file"""
        self.data = {
            'server': {
                'external_ip': self.server.external_ip,
                'hostname': self.server.hostname,
            },
            'database': {
                'path': self.database.path,
                'encryption_key_path': self.database.encryption_key_path,
            },
            'proxies': {
                'socks5': {
                    'enabled': self.socks5.enabled,
                    'backend': self.socks5.backend,
                    'port': self.socks5.port,
                    'tls_port': self.socks5.tls_port,
                    'config_path': self.socks5.config_path,
                },
                'https': {
                    'enabled': self.https.enabled,
                    'backend': self.https.backend,
                    'port': self.https.port,
                    'tls_port': self.https.tls_port,
                    'config_path': self.https.config_path,
                },
            },
            'security': {
                'argon2_time_cost': self.security.argon2_time_cost,
                'argon2_memory_cost': self.security.argon2_memory_cost,
                'argon2_parallelism': self.security.argon2_parallelism,
                'tls_min_version': self.security.tls_min_version,
                'allowed_ciphers': self.security.allowed_ciphers,
                'max_auth_failures': self.security.max_auth_failures,
                'auth_failure_window': self.security.auth_failure_window,
            },
            'logging': {
                'directory': self.logging.directory,
                'retention_days': self.logging.retention_days,
                'max_size_mb': self.logging.max_size_mb,
                'level': self.logging.level,
            },
            'quotas': {
                'check_interval_seconds': self.quotas.check_interval_seconds,
                'warning_threshold_percent': self.quotas.warning_threshold_percent,
                'grace_period_hours': self.quotas.grace_period_hours,
                'enforcement_enabled': self.quotas.enforcement_enabled,
            },
            'monitoring': {
                'metrics_enabled': self.monitoring.metrics_enabled,
                'metrics_port': self.monitoring.metrics_port,
                'metrics_host': self.monitoring.metrics_host,
            },
            'firewall': {
                'ssh_port': self.firewall.ssh_port,
                'allowed_ssh_ips': self.firewall.allowed_ssh_ips,
            },
            'backup': {
                'enabled': self.backup.enabled,
                'directory': self.backup.directory,
                'retention_days': self.backup.retention_days,
                'encryption': self.backup.encryption,
            },
        }

        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(self.config_path), exist_ok=True)

            with open(self.config_path, 'w') as f:
                yaml.safe_dump(
                    self.data, f, default_flow_style=False, sort_keys=False)
        except Exception as e:
            raise RuntimeError(
                f"Failed to save configuration to {self.config_path}: {e}")

    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value by dot notation key

        Args:
            key: Configuration key (e.g., "server.external_ip")
            default: Default value if key not found

        Returns:
            Configuration value or default
        """
        keys = key.split('.')
        value = self.data

        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default

        return value

    def set(self, key: str, value: Any) -> None:
        """
        Set configuration value by dot notation key

        Args:
            key: Configuration key (e.g., "server.external_ip")
            value: Value to set
        """
        keys = key.split('.')
        data = self.data

        for k in keys[:-1]:
            if k not in data:
                data[k] = {}
            data = data[k]

        data[keys[-1]] = value

    def validate(self) -> tuple[bool, list[str]]:
        """
        Validate configuration

        Returns:
            Tuple of (is_valid, list of error messages)
        """
        errors = []

        # Check database encryption key exists
        if not os.path.exists(self.database.encryption_key_path):
            errors.append(
                f"Encryption key not found: {self.database.encryption_key_path}")

        # Check log directory is writable
        if not os.access(self.logging.directory, os.W_OK):
            errors.append(
                f"Log directory not writable: {self.logging.directory}")

        # Validate Argon2 parameters
        if self.security.argon2_time_cost < 1:
            errors.append("argon2_time_cost must be >= 1")
        if self.security.argon2_memory_cost < 8192:
            errors.append("argon2_memory_cost must be >= 8192 KB")
        if self.security.argon2_parallelism < 1:
            errors.append("argon2_parallelism must be >= 1")

        # Validate ports
        for name, proxy in [("socks5", self.socks5), ("https", self.https)]:
            if proxy.enabled:
                if proxy.port < 1 or proxy.port > 65535:
                    errors.append(f"{name}.port must be between 1-65535")
                if proxy.tls_port < 1 or proxy.tls_port > 65535:
                    errors.append(f"{name}.tls_port must be between 1-65535")

        return len(errors) == 0, errors


def load_config(config_path: Optional[str] = None) -> Config:
    """
    Load configuration from file

    Args:
        config_path: Path to configuration file

    Returns:
        Config object
    """
    return Config(config_path)
