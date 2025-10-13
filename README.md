# VPS Proxy Kit

A complete, production-ready proxy server management system for Ubuntu 22.04 VPS deployments.

## Features

- **Multi-Protocol Support**: SOCKS5 (Dante), HTTP/HTTPS (Squid)
- **Strong Authentication**: Per-user credentials with Argon2id hashing, optional token-based auth
- **High-Grade Encryption**: TLS 1.3 for HTTP/HTTPS, optional TLS wrapping for SOCKS5 via stunnel
- **Per-User Accounting**: Bandwidth tracking and quota enforcement
- **User Management**: Terminal UI + CLI for complete user lifecycle management
- **Monitoring**: Prometheus metrics exporter, Grafana dashboard support
- **Security Hardened**: Unprivileged service users, encrypted database, firewall rules, fail2ban integration

## Architecture

```
┌─────────────┐         ┌──────────────────────────────────────┐
│   Clients   │────────▶│  VPS (34.214.132.38)                 │
└─────────────┘         │                                      │
                        │  ┌────────────────────────────────┐  │
                        │  │ Stunnel (TLS termination)      │  │
                        │  │  :8443 (HTTPS) :11080 (SOCKS)  │  │
                        │  └─────────┬──────────────────────┘  │
                        │            │                          │
                        │  ┌─────────▼──────────┐              │
                        │  │ Squid :3128        │              │
                        │  │ Dante :1080        │              │
                        │  └─────────┬──────────┘              │
                        │            │                          │
                        │  ┌─────────▼──────────┐              │
                        │  │ VPK Log Parser     │              │
                        │  │ VPK Quota Enforcer │              │
                        │  │ VPK Metrics Export │              │
                        │  └─────────┬──────────┘              │
                        │            │                          │
                        │  ┌─────────▼──────────┐              │
                        │  │ Encrypted SQLite DB│              │
                        │  └────────────────────┘              │
                        └──────────────────────────────────────┘
```

## Quick Start (10 Commands)

```bash
# 1. Clone repository
git clone https://github.com/genome96/cusproxy.git
cd cusproxy

# 2. Run bootstrap installer (as root)
sudo ./bootstrap.sh --yes

# 3. With domain for Let's Encrypt SSL (recommended)
sudo ./bootstrap.sh --domain yourdomain.com --yes

# 4. Activate virtualenv
source /opt/vps-proxy-kit/venv/bin/activate

# 5. Create your first user
vpk create-user --username alice --password 'YourSecurePassword123!' --protocol socks,https --quota 100GB

# 6. Check status
vpk list-users

# 7. View active connections
vpk show-sessions

# 8. Enable metrics endpoint
sudo systemctl start vpk-metrics

# 9. Test SOCKS5 connection
curl --socks5 alice:YourSecurePassword123!@YOUR_SERVER_IP:1080 https://ipinfo.io/ip

# 10. Test HTTPS proxy (with TLS)
curl --proxy https://alice:YourSecurePassword123!@YOUR_SERVER_IP:8443 https://ipinfo.io/ip --insecure
```

## Installation

### Prerequisites

- **OS**: Ubuntu 22.04 LTS (fresh installation recommended)
- **Resources**: Minimum 1GB RAM, 10GB disk space
- **Access**: Root or sudo privileges
- **Network**: Public IP address
- **Domain** (optional): For Let's Encrypt SSL certificates
  - Domain must have A record pointing to your VPS IP
  - DNS propagation completed (verify with `dig yourdomain.com`)
  - Port 80 accessible for Let's Encrypt validation

### Full Installation

```bash
# Clone the repository
git clone https://github.com/genome96/cusproxy.git
cd cusproxy

# Run bootstrap installer
sudo ./bootstrap.sh

# With domain for Let's Encrypt certificates (recommended)
sudo ./bootstrap.sh --domain yourdomain.com --yes

# Quick mode (autossh + microsocks for single-user)
sudo ./bootstrap.sh --mode quick
```

The bootstrap script will:

1. Validate DNS configuration (if domain provided)
2. Install required packages (dante-server, squid, stunnel4, etc.)
3. Create unprivileged users (`proxyadmin`, `proxyd`)
4. Set up Python virtual environment
5. Install Python dependencies
6. Create directory structure under `/opt/vps-proxy-kit/`
7. Generate encryption keys and SSL certificates
8. Configure proxy services with production-ready settings
9. Set up systemd units with automatic retries
10. Configure firewall rules
11. Enable fail2ban protection
12. Initialize service caches and log files

**Automated Fixes Included**:
- ✅ DNS validation before Let's Encrypt certificate requests
- ✅ stunnel IPv4-only binding to prevent address conflicts
- ✅ Proper certificate directory permissions (755)
- ✅ Squid log file pre-creation with correct ownership
- ✅ Squid cache initialization before first start
- ✅ Service startup retry logic (3 attempts for Squid)
- ✅ DH parameter generation with progress feedback
- ✅ Default stunnel4 service masking to prevent conflicts

## Usage

### Interactive Menu

```bash
vpk menu
```

This launches an interactive terminal UI with options:

- Create user
- Delete user
- List users
- Set quota
- Show active sessions
- Kill session
- Rotate keys
- Enable/Disable protocols
- View logs
- Export usage CSV

### CLI Commands

#### User Management

```bash
# Create user with SOCKS5 and HTTPS access
vpk create-user --username bob --password 'SecurePass!' --protocol socks,https --quota 50GB

# Create user with expiration date
vpk create-user --username charlie --password 'Pass123!' --protocol socks --quota 25GB --expires 2026-01-01

# Create user with token authentication
vpk create-user --username dave --token-auth --protocol https --quota 100GB

# List all users
vpk list-users

# Show detailed user info
vpk user-info --username alice

# Delete user
vpk delete-user --username bob --yes

# Suspend user
vpk suspend-user --username alice

# Resume user
vpk resume-user --username alice
```

#### Quota Management

```bash
# Set quota for user
vpk set-quota --username alice --quota 200GB

# Show quota usage
vpk quota-usage --username alice

# Reset monthly usage counter
vpk reset-usage --username alice --yes
```

#### Session Management

```bash
# Show active sessions
vpk show-sessions

# Show sessions for specific user
vpk show-sessions --username alice

# Kill specific session
vpk kill-session --session-id 12345

# Kill all sessions for user
vpk kill-sessions --username alice --yes
```

#### Monitoring & Logs

```bash
# View recent logs
vpk view-logs --lines 100

# View logs for specific user
vpk view-logs --username alice --lines 50

# Export usage report to CSV
vpk export-usage --output /tmp/usage-report.csv

# Export monthly report
vpk export-usage --month 2025-10 --output /tmp/october-report.csv
```

#### System Management

```bash
# Rotate encryption keys
vpk rotate-keys --yes

# Enable protocol globally
vpk enable-protocol --protocol socks

# Disable protocol globally
vpk disable-protocol --protocol https

# Run database migrations
vpk migrate-db

# Upgrade VPK to latest version
vpk upgrade

# Check system status
vpk status

# Test proxy configuration
vpk test-proxy --protocol socks --username alice
```

## Configuration

### Main Configuration File

`/etc/vpk/config.yml`:

```yaml
database:
  path: /opt/vps-proxy-kit/data/vpk.db
  encryption_key_path: /etc/vpk/secret.key

proxies:
  socks5:
    enabled: true
    backend: dante
    port: 1080
    tls_port: 11080
    config_path: /etc/dante/dante.conf

  https:
    enabled: true
    backend: squid
    port: 3128
    tls_port: 8443
    config_path: /etc/squid/squid.conf

security:
  argon2_time_cost: 4
  argon2_memory_cost: 65536
  argon2_parallelism: 2
  tls_min_version: "1.3"
  allowed_ciphers: "TLS_AES_256_GCM_SHA384:TLS_CHACHA20_POLY1305_SHA256"

logging:
  directory: /var/log/vpk
  retention_days: 30
  max_size_mb: 100

quotas:
  check_interval_seconds: 300
  warning_threshold_percent: 80
  grace_period_hours: 24

monitoring:
  metrics_enabled: true
  metrics_port: 9100
  metrics_host: 127.0.0.1

firewall:
  ssh_port: 22
  allowed_ssh_ips: []
```

### User Database Schema

```sql
-- users table
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT,  -- Argon2id hash
    token_hash TEXT,     -- Optional token for API auth
    protocols TEXT,      -- Comma-separated: socks,https
    quota_bytes INTEGER,
    usage_bytes INTEGER DEFAULT 0,
    status TEXT DEFAULT 'active',  -- active, suspended, expired
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP,
    last_login TIMESTAMP
);

-- usage_logs table
CREATE TABLE usage_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    protocol TEXT,
    bytes_in INTEGER,
    bytes_out INTEGER,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    source_ip TEXT,
    destination TEXT,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- sessions table
CREATE TABLE sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    protocol TEXT,
    source_ip TEXT,
    destination TEXT,
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ended_at TIMESTAMP,
    bytes_transferred INTEGER,
    FOREIGN KEY (user_id) REFERENCES users(id)
);
```

## Client Configuration Examples

### SOCKS5 (No TLS)

```bash
# Using curl
curl --socks5 alice:S3cReT!@34.214.132.38:1080 https://ipinfo.io/ip

# Using Firefox
# Settings → Network Settings → Manual proxy configuration
# SOCKS Host: 34.214.132.38
# Port: 1080
# SOCKS v5: checked
# Username: alice
# Password: S3cReT!

# Using ssh -D
ssh -D 1080 alice@34.214.132.38  # Not recommended, use dedicated proxy
```

### SOCKS5 with TLS (via stunnel)

```bash
# Client-side stunnel config (stunnel-client.conf)
client = yes

[socks5-tls]
accept = 127.0.0.1:1080
connect = 34.214.132.38:11080
# For production, verify certificate:
CAfile = /path/to/ca-bundle.crt
verifyChain = yes

# Start stunnel client
stunnel stunnel-client.conf

# Now connect via localhost
curl --socks5 alice:S3cReT!@127.0.0.1:1080 https://ipinfo.io/ip
```

### HTTP/HTTPS Proxy (No TLS)

```bash
# Using curl
curl --proxy http://alice:S3cReT!@34.214.132.38:3128 https://ipinfo.io/ip

# Using wget
wget -e use_proxy=yes -e http_proxy=http://alice:S3cReT!@34.214.132.38:3128 https://ipinfo.io/ip

# System-wide (Linux)
export http_proxy=http://alice:S3cReT!@34.214.132.38:3128
export https_proxy=http://alice:S3cReT!@34.214.132.38:3128
```

### HTTPS Proxy with TLS

```bash
# Using curl (if your curl supports HTTPS proxy)
curl --proxy https://alice:S3cReT!@34.214.132.38:8443 https://ipinfo.io/ip

# For browsers, configure HTTPS proxy:
# Host: 34.214.132.38
# Port: 8443
# Username: alice
# Password: S3cReT!
```

### Using Token Authentication

```bash
# Create user with token
vpk create-user --username dave --token-auth --protocol https --quota 100GB
# Token will be printed: tok_abc123def456...

# Use token as password
curl --proxy http://dave:tok_abc123def456@34.214.132.38:3128 https://ipinfo.io/ip
```

## Security Considerations

### Threat Model

- **Attacker Goal**: Unauthorized proxy access, credential theft, service disruption
- **Assets Protected**: User credentials, usage data, proxy availability
- **Security Controls**: See SECURITY.md for detailed threat analysis

### Hardening Checklist

- [x] Services run as unprivileged users (`proxyadmin`, `proxyd`)
- [x] Argon2id password hashing (time=4, memory=65536 KB, parallelism=2)
- [x] Encrypted SQLite database at rest
- [x] Encryption key stored in `/etc/vpk/secret.key` (permissions 600, owner root)
- [x] TLS 1.3 only by default, modern cipher suites
- [x] Firewall rules via UFW (only necessary ports open)
- [x] fail2ban enabled for SSH and repeated auth failures
- [x] Log rotation (30 days retention by default)
- [x] No plaintext credentials stored anywhere
- [x] Optional token-based authentication
- [x] Rate limiting on authentication attempts
- [x] Session timeout and idle connection killing

### Certificate Management

#### With Domain (Let's Encrypt)

```bash
# Install certbot if not already done
sudo apt install certbot

# Obtain certificate
sudo certbot certonly --standalone -d proxy.example.com

# Certificates will be in:
# /etc/letsencrypt/live/proxy.example.com/fullchain.pem
# /etc/letsencrypt/live/proxy.example.com/privkey.pem

# Set up auto-renewal
sudo certbot renew --dry-run
```

#### IP-Only Deployment (Self-Signed)

```bash
# Generate self-signed certificate
vpk generate-cert --ip 34.214.132.38 --days 365

# Certificate will be in:
# /etc/vpk/certs/server.crt
# /etc/vpk/certs/server.key

# Rotate certificate
vpk rotate-cert --ip 34.214.132.38 --days 365
```

### Firewall Configuration

```bash
# Applied automatically by bootstrap.sh
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 1080/tcp  # SOCKS5
sudo ufw allow 3128/tcp  # HTTP/HTTPS proxy
sudo ufw allow 8443/tcp  # HTTPS proxy with TLS
sudo ufw allow 11080/tcp # SOCKS5 with TLS
sudo ufw enable

# To restrict SSH to specific IPs
sudo ufw delete allow 22/tcp
sudo ufw allow from 203.0.113.0/24 to any port 22
```

### fail2ban Configuration

The bootstrap script installs custom fail2ban filters:

- `/etc/fail2ban/filter.d/vpk-auth.conf` - Detects repeated auth failures in proxy logs
- `/etc/fail2ban/jail.d/vpk.conf` - Enables VPK jails

```ini
[vpk-socks]
enabled = true
port = 1080,11080
filter = vpk-auth
logpath = /var/log/vpk/danted.log
maxretry = 5
bantime = 3600

[vpk-squid]
enabled = true
port = 3128,8443
filter = vpk-auth
logpath = /var/log/vpk/squid_access.log
maxretry = 5
bantime = 3600
```

## Bandwidth Management

### Per-User Quotas

Quotas are enforced by the `vpk-quota` service which runs every 5 minutes (configurable):

1. Parses proxy logs to calculate per-user bytes transferred
2. Updates `usage_bytes` in database
3. Compares against `quota_bytes`
4. When quota exceeded:
   - Marks user as `suspended`
   - Reloads proxy configs to block the user
   - Optionally sends email notification (if configured)

### Bandwidth Throttling

#### Squid delay_pools (Per-User Speed Limiting)

Edit `/etc/squid/squid.conf`:

```conf
# Create delay pool
delay_pools 1
delay_class 1 2

# 256 Kbps (32 KB/s) per user
delay_parameters 1 -1/-1 32000/32000

# Apply to authenticated users
delay_access 1 allow authenticated
delay_access 1 deny all
```

#### tc (Traffic Control) for Connection-Level Shaping

VPK provides `tc_manager.py` to apply traffic shaping rules:

```bash
# Limit user 'alice' to 10 Mbps
vpk set-bandwidth --username alice --limit 10mbit

# Remove bandwidth limit
vpk set-bandwidth --username alice --limit unlimited

# Show current tc rules
vpk show-bandwidth
```

Implementation uses HTB (Hierarchical Token Bucket) with connection marking.

## Monitoring & Metrics

### Prometheus Integration

The `vpk-metrics` service exposes metrics on `http://127.0.0.1:9100/metrics`:

```prometheus
# HELP vpk_users_total Total number of users
# TYPE vpk_users_total gauge
vpk_users_total 5

# HELP vpk_user_bytes_total Total bytes transferred by user
# TYPE vpk_user_bytes_total counter
vpk_user_bytes_total{user="alice",protocol="socks"} 1073741824
vpk_user_bytes_total{user="alice",protocol="https"} 536870912

# HELP vpk_user_quota_bytes User quota in bytes
# TYPE vpk_user_quota_bytes gauge
vpk_user_quota_bytes{user="alice"} 107374182400

# HELP vpk_active_connections Active connections by user
# TYPE vpk_active_connections gauge
vpk_active_connections{user="alice",protocol="socks"} 3

# HELP vpk_quota_usage_percent Quota usage percentage
# TYPE vpk_quota_usage_percent gauge
vpk_quota_usage_percent{user="alice"} 1.5
```

### Prometheus Configuration

Add to `/etc/prometheus/prometheus.yml`:

```yaml
scrape_configs:
  - job_name: "vpk"
    static_configs:
      - targets: ["localhost:9100"]
    scrape_interval: 30s

  - job_name: "node"
    static_configs:
      - targets: ["localhost:9101"]
    scrape_interval: 30s
```

### Grafana Dashboard

Import the provided dashboard: `examples/grafana-dashboard.json`

Key panels:

- Total users and active connections
- Per-user bandwidth usage (time series)
- Quota usage gauges
- Top 10 users by bandwidth
- Connection heatmap
- Alert history

### vnstat Integration

```bash
# View network usage
vnstat -i eth0

# Live monitoring
vnstat -l -i eth0

# Monthly report
vnstat -m -i eth0
```

## Log Management

### Log Files

- `/var/log/vpk/danted.log` - Dante SOCKS5 server logs
- `/var/log/vpk/squid_access.log` - Squid access logs
- `/var/log/vpk/squid_cache.log` - Squid cache logs
- `/var/log/vpk/stunnel.log` - stunnel TLS wrapper logs
- `/var/log/vpk/vpk.log` - VPK application logs
- `/var/log/vpk/logparser.log` - Log parser service logs
- `/var/log/vpk/quota.log` - Quota enforcer logs

### Log Rotation

Configured in `/etc/logrotate.d/vpk`:

```
/var/log/vpk/*.log {
    daily
    rotate 30
    compress
    delaycompress
    notifempty
    create 0640 proxyadmin proxyadmin
    sharedscripts
    postrotate
        systemctl reload vpk-logparser > /dev/null 2>&1 || true
    endscript
}
```

### Viewing Logs

```bash
# Live tail
vpk view-logs --follow

# Filter by user
vpk view-logs --username alice --lines 100

# Filter by protocol
vpk view-logs --protocol socks --lines 50

# Filter by date range
vpk view-logs --since "2025-10-01" --until "2025-10-31"

# Export logs
vpk export-logs --output /tmp/logs.txt --since "2025-10-01"
```

## Deployment Modes

### Production Mode (Default)

Full-featured deployment with:

- Dante SOCKS5 server
- Squid HTTP/HTTPS proxy
- stunnel TLS wrappers
- Full monitoring and logging
- systemd service management

```bash
sudo ./bootstrap.sh --mode prod
```

### Quick Mode (Development/Testing)

Lightweight deployment with:

- microsocks (simple SOCKS5 server)
- autossh for SSH tunneling
- Minimal logging
- Single-user oriented

```bash
sudo ./bootstrap.sh --mode quick --username testuser --password testpass
```

### Migration from Quick to Prod

```bash
# Export users from quick mode
vpk export-users --output /tmp/users.json

# Install production mode
sudo ./bootstrap.sh --mode prod

# Import users
vpk import-users --input /tmp/users.json

# Verify
vpk list-users
```

## Troubleshooting

### Installation Issues

#### DNS Validation Failed

**Symptom**: Bootstrap script reports "DNS mismatch! Domain points to X.X.X.X but server is Y.Y.Y.Y"

**Solution**:
```bash
# Verify DNS propagation
dig +short yourdomain.com

# Or use host command
host yourdomain.com

# If not propagated, wait or use self-signed certificate
sudo ./bootstrap.sh --yes  # Skips Let's Encrypt, uses self-signed
```

#### stunnel Service Failed to Start

**Symptom**: `systemctl status vpk-stunnel` shows "activating" or "Address already in use"

**Causes & Solutions**:

1. **IPv6/IPv4 binding conflict** (Fixed in latest bootstrap):
   ```bash
   # Check if default stunnel4 is running
   systemctl status stunnel4
   
   # Disable it
   sudo systemctl stop stunnel4
   sudo systemctl mask stunnel4
   
   # Restart vpk-stunnel
   sudo systemctl restart vpk-stunnel
   ```

2. **DH parameter generation** (takes 1-2 minutes on first start):
   ```bash
   # This is normal, wait 2 minutes then check
   sudo journalctl -u vpk-stunnel -f
   
   # Verify stunnel is listening
   sudo ss -tlnp | grep ':8443\|:11080'
   ```

3. **Permission issues with certificates**:
   ```bash
   # Check certificate permissions
   ls -la /etc/vpk/certs/
   
   # Should be 755 for directories, 644 for files
   sudo chmod 755 /etc/vpk /etc/vpk/certs
   sudo chmod 644 /etc/vpk/certs/*
   ```

#### Squid Service Failed to Start

**Symptom**: `systemctl status vpk-squid` shows "failed" or "cannot open log file"

**Solutions**:

1. **Log file permission issues** (Fixed in latest bootstrap):
   ```bash
   # Create log files with correct ownership
   sudo touch /var/log/vpk/squid_access.log /var/log/vpk/squid_cache.log
   sudo chown proxy:proxy /var/log/vpk/squid*.log
   sudo chmod 644 /var/log/vpk/squid*.log
   ```

2. **Cache directory not initialized** (Fixed in latest bootstrap):
   ```bash
   # Initialize Squid cache
   sudo mkdir -p /run/squid
   sudo chown proxy:proxy /run/squid
   sudo -u proxy /usr/sbin/squid -f /etc/squid/squid.conf -z
   
   # Restart service
   sudo systemctl restart vpk-squid
   ```

3. **Service startup timeout**:
   ```bash
   # The installer now includes retry logic (3 attempts)
   # Manual restart if needed:
   sudo systemctl restart vpk-squid
   sleep 2
   sudo systemctl status vpk-squid
   ```

### Common Issues

#### Proxy not accepting connections

```bash
# Check service status
sudo systemctl status vpk-dante vpk-squid vpk-stunnel

# Check ports are listening
sudo ss -tulpn | grep -E '1080|3128|8443|11080'

# Check firewall
sudo ufw status

# Test connectivity
telnet YOUR_SERVER_IP 1080
telnet YOUR_SERVER_IP 3128
```

#### Authentication failures

```bash
# Verify user exists and is active
vpk user-info --username alice

# Check logs for auth errors
vpk view-logs --username alice --lines 50

# Test credentials
vpk test-proxy --username alice --password 'S3cReT!' --protocol socks
```

#### Quota not updating

```bash
# Check log parser service
sudo systemctl status vpk-logparser

# Manually trigger quota check
vpk check-quotas --force

# View quota service logs
sudo journalctl -u vpk-quota -n 100
```

#### TLS connection errors

```bash
# Verify stunnel is running
sudo systemctl status stunnel4

# Check certificate validity
openssl s_client -connect 34.214.132.38:8443

# Test without TLS first
curl --proxy http://alice:S3cReT!@34.214.132.38:3128 https://ipinfo.io/ip
```

### Debug Mode

```bash
# Enable debug logging
vpk config set logging.level DEBUG

# Restart services
sudo systemctl restart vpk-logparser vpk-quota

# View debug logs
tail -f /var/log/vpk/vpk.log
```

### Performance Issues

```bash
# Check system resources
vpk status --detailed

# View connection statistics
vpk show-sessions --stats

# Check for rate limiting
vpk show-bandwidth

# View database size
du -sh /opt/vps-proxy-kit/data/vpk.db
```

## Data Retention & GDPR

See `SECURITY.md` for full policy. Summary:

- **Logs**: Retained for 30 days (configurable)
- **Usage data**: Aggregated monthly, details deleted after 90 days
- **User accounts**: Retained until explicitly deleted
- **Session data**: Deleted after session ends (max 24 hours)

### User Data Export

```bash
# Export all data for a user
vpk export-user-data --username alice --output /tmp/alice-data.zip
```

### User Data Deletion

```bash
# Delete user and all associated data
vpk delete-user --username alice --yes --purge-data
```

## Testing

### Unit Tests

```bash
# Run all tests
cd /opt/vps-proxy-kit
source venv/bin/activate
pytest tests/

# Run specific test module
pytest tests/test_users.py -v

# Run with coverage
pytest --cov=vpk --cov-report=html tests/
```

### Integration Tests

```bash
# Run integration test suite
./tests/integration_test.sh

# This will:
# 1. Create ephemeral proxy instances
# 2. Create test users
# 3. Generate test traffic
# 4. Verify counters update correctly
# 5. Test quota enforcement
# 6. Clean up
```

### Manual Testing

```bash
# Create test user
vpk create-user --username testuser --password 'Test123!' --protocol socks,https --quota 1GB

# Test SOCKS5
curl --socks5 testuser:Test123!@localhost:1080 https://ipinfo.io/ip

# Test HTTP proxy
curl --proxy http://testuser:Test123!@localhost:3128 https://ipinfo.io/ip

# Generate traffic to test quota
for i in {1..100}; do
  curl --socks5 testuser:Test123!@localhost:1080 https://httpbin.org/bytes/10485760 > /dev/null
done

# Verify usage updated
vpk quota-usage --username testuser

# Clean up
vpk delete-user --username testuser --yes
```

## API & Automation

### REST API (Optional)

Install the optional REST API:

```bash
pip install 'vpk[api]'

# Start API server
vpk serve-api --host 0.0.0.0 --port 5000 --auth-token YOUR_SECRET_TOKEN
```

API endpoints:

- `POST /api/v1/users` - Create user
- `GET /api/v1/users` - List users
- `GET /api/v1/users/{username}` - Get user info
- `DELETE /api/v1/users/{username}` - Delete user
- `PUT /api/v1/users/{username}/quota` - Update quota
- `GET /api/v1/sessions` - List active sessions
- `DELETE /api/v1/sessions/{id}` - Kill session
- `GET /api/v1/metrics` - Get metrics JSON

### Automation Examples

```bash
# Create users from CSV
vpk import-users --csv users.csv

# CSV format:
# username,password,protocols,quota_gb,expires
# alice,Pass123!,"socks,https",100,2026-01-01
# bob,Pass456!,socks,50,2026-06-01

# Batch delete users
vpk delete-users --usernames alice,bob,charlie --yes

# Reset all quotas on first of month (cron)
0 0 1 * * /usr/local/bin/vpk reset-all-usage --yes

# Daily usage report (cron)
0 0 * * * /usr/local/bin/vpk export-usage --output /tmp/daily-$(date +\%Y\%m\%d).csv
```

## Performance Tuning

### System Limits

Edit `/etc/security/limits.conf`:

```
proxyd soft nofile 65536
proxyd hard nofile 65536
proxyadmin soft nofile 65536
proxyadmin hard nofile 65536
```

Edit `/etc/sysctl.conf`:

```
net.core.somaxconn = 1024
net.ipv4.tcp_max_syn_backlog = 2048
net.ipv4.ip_local_port_range = 10000 65000
net.ipv4.tcp_tw_reuse = 1
net.ipv4.tcp_fin_timeout = 30
```

Apply:

```bash
sudo sysctl -p
```

### Proxy Tuning

#### Dante

Edit `/etc/dante/dante.conf`:

```
child.maxidle: 30
child.maxrequests: 0
child.maxconcurrent: 10000
```

#### Squid

Edit `/etc/squid/squid.conf`:

```
workers 4
cache_mem 256 MB
maximum_object_size 100 MB
cache_dir ufs /var/spool/squid 10000 16 256
```

## License

MIT License - see LICENSE file

## Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## Support

- GitHub Issues: https://github.com/genome96/cusproxy/issues
- Documentation: https://vps-proxy-kit.readthedocs.io
- Email: support@example.com

## Acknowledgments

- Inspired by [vanjoe667/socks5-vps-proxy](https://github.com/vanjoe667/socks5-vps-proxy)
- SSH tunnel patterns from [devarashs/autossh-proxy](https://github.com/devarashs/autossh-proxy)
- Built on Dante SOCKS5 server and Squid proxy server

## Legal Notice

**IMPORTANT**: This software is provided for legitimate use only. Users are responsible for:

- Complying with local laws and regulations
- Respecting terms of service of upstream networks
- Not using for illegal activities
- Obtaining necessary permissions

The authors assume no liability for misuse of this software.
