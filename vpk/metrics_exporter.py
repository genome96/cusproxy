"""
Prometheus metrics exporter for VPS Proxy Kit

Exposes metrics for monitoring and alerting.
"""

import time
from prometheus_client import start_http_server, Gauge, Counter, Info

from vpk.config import Config
from vpk.db import Database
from vpk.utils import setup_logging


# Define metrics
vpk_info = Info('vpk', 'VPS Proxy Kit information')
vpk_users_total = Gauge('vpk_users_total', 'Total number of users', ['status'])
vpk_user_bytes_total = Counter(
    'vpk_user_bytes_total', 'Total bytes transferred by user', ['user', 'protocol'])
vpk_user_quota_bytes = Gauge(
    'vpk_user_quota_bytes', 'User quota in bytes', ['user'])
vpk_user_usage_bytes = Gauge(
    'vpk_user_usage_bytes', 'User current usage in bytes', ['user'])
vpk_active_connections = Gauge(
    'vpk_active_connections', 'Active connections by user', ['user', 'protocol'])
vpk_quota_usage_percent = Gauge(
    'vpk_quota_usage_percent', 'Quota usage percentage', ['user'])
vpk_database_size_bytes = Gauge(
    'vpk_database_size_bytes', 'Database size in bytes')


class MetricsExporter:
    """Export metrics to Prometheus"""

    def __init__(self, db: Database, config: Config):
        """
        Initialize metrics exporter

        Args:
            db: Database instance
            config: Configuration instance
        """
        self.db = db
        self.config = config
        self.logger = setup_logging(
            config.logging.directory, config.logging.level)

        # Set info metric
        from vpk import __version__
        vpk_info.info({
            'version': __version__,
            'hostname': config.server.hostname,
            'external_ip': config.server.external_ip,
        })

    def update_metrics(self):
        """Update all metrics from database"""
        try:
            # User counts by status
            for status in ['active', 'suspended', 'expired']:
                result = self.db.fetchone(
                    "SELECT COUNT(*) as count FROM users WHERE status = ?",
                    (status,)
                )
                count = result['count'] if result else 0
                vpk_users_total.labels(status=status).set(count)

            # Per-user metrics
            users = self.db.fetchall("SELECT * FROM users")

            for user in users:
                username = user['username']

                # Quota
                vpk_user_quota_bytes.labels(
                    user=username).set(user['quota_bytes'])

                # Usage
                vpk_user_usage_bytes.labels(
                    user=username).set(user['usage_bytes'])

                # Usage percentage
                if user['quota_bytes'] > 0:
                    usage_percent = (
                        user['usage_bytes'] / user['quota_bytes']) * 100
                    vpk_quota_usage_percent.labels(
                        user=username).set(usage_percent)

                # Active connections
                for protocol in ['socks', 'https']:
                    result = self.db.fetchone(
                        """
                        SELECT COUNT(*) as count FROM sessions
                        WHERE user_id = ? AND protocol = ? AND ended_at IS NULL
                        """,
                        (user['id'], protocol)
                    )
                    count = result['count'] if result else 0
                    vpk_active_connections.labels(
                        user=username, protocol=protocol).set(count)

            # Database size
            stats = self.db.get_stats()
            vpk_database_size_bytes.set(stats['db_size_bytes'])

            self.logger.debug("Metrics updated successfully")

        except Exception as e:
            self.logger.error(f"Error updating metrics: {e}")

    def run(self):
        """Run metrics exporter"""
        host = self.config.monitoring.metrics_host
        port = self.config.monitoring.metrics_port

        self.logger.info(f"Starting metrics exporter on {host}:{port}")

        # Start HTTP server
        start_http_server(port, addr=host)

        # Update metrics periodically
        while True:
            try:
                self.update_metrics()
                time.sleep(30)  # Update every 30 seconds

            except KeyboardInterrupt:
                self.logger.info("Metrics exporter stopped by user")
                break
            except Exception as e:
                self.logger.error(f"Error in metrics exporter: {e}")
                time.sleep(60)


def main():
    """Main entry point for metrics exporter service"""
    from vpk.config import Config
    from vpk.db import Database

    # Load config
    config = Config()

    if not config.monitoring.metrics_enabled:
        print("Metrics are disabled in configuration")
        return

    # Initialize database
    db = Database(config.database.path, config.database.encryption_key_path)

    # Start exporter
    exporter = MetricsExporter(db, config)
    exporter.run()


if __name__ == '__main__':
    main()
