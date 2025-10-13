# VPS Proxy Kit Deployment Checklist

## Pre-Installation

- [ ] Ubuntu 22.04 LTS server provisioned
- [ ] Root or sudo access confirmed
- [ ] Public IP address noted: `34.214.132.38`
- [ ] Domain name (optional): `proxy.example.com`
- [ ] SSH access configured
- [ ] At least 1GB RAM, 10GB disk space available

## Installation Steps

### 1. Clone Repository

```bash
git clone https://github.com/genome96/vps-proxy-kit.git
cd vps-proxy-kit
```

- [ ] Repository cloned successfully

### 2. Run Bootstrap Installer

```bash
# With domain (recommended for production)
sudo ./bootstrap.sh --domain proxy.example.com --yes

# Or without domain (self-signed certificates)
sudo ./bootstrap.sh --yes
```

- [ ] Bootstrap completed without errors
- [ ] All services installed
- [ ] Encryption key generated
- [ ] TLS certificates created
- [ ] Firewall configured
- [ ] systemd units created

### 3. Initialize Database

```bash
sudo -u proxyadmin vpk init-db
```

- [ ] Database initialized successfully
- [ ] Database file created at `/opt/vps-proxy-kit/data/vpk.db`

### 4. Start Monitoring Services

```bash
sudo systemctl start vpk-logparser
sudo systemctl start vpk-quota
sudo systemctl start vpk-metrics
```

- [ ] All monitoring services started
- [ ] Check status: `sudo systemctl status vpk-*`

### 5. Create First User

```bash
vpk create-user \
  --username admin \
  --password 'YourStrongPassword123!' \
  --protocol socks,https \
  --quota 100GB
```

- [ ] Admin user created successfully
- [ ] Credentials stored securely

### 6. Test Proxy Connectivity

```bash
# Test SOCKS5
curl --socks5 admin:YourStrongPassword123!@34.214.132.38:1080 https://ipinfo.io/ip

# Test HTTP proxy
curl --proxy http://admin:YourStrongPassword123!@34.214.132.38:3128 https://ipinfo.io/ip
```

- [ ] SOCKS5 proxy working
- [ ] HTTP proxy working
- [ ] Public IP returned correctly

## Security Hardening

### SSH Security

```bash
# Change SSH port
sudo nano /etc/ssh/sshd_config
# Change: Port 22 → Port 2222

# Disable root login
# Change: PermitRootLogin yes → PermitRootLogin no

# Disable password authentication (use keys only)
# Change: PasswordAuthentication yes → PasswordAuthentication no

sudo systemctl restart sshd
```

- [ ] SSH port changed (update firewall: `sudo ufw allow 2222/tcp`)
- [ ] Root SSH login disabled
- [ ] Password authentication disabled
- [ ] SSH key authentication working

### Firewall Configuration

```bash
# Review firewall rules
sudo ufw status verbose

# If SSH port changed, update firewall
sudo ufw delete allow 22/tcp
sudo ufw allow 2222/tcp

# Restrict SSH to specific IPs (optional)
sudo ufw delete allow 2222/tcp
sudo ufw allow from YOUR_IP_ADDRESS to any port 2222
```

- [ ] Only necessary ports open
- [ ] SSH access restricted (if applicable)
- [ ] Firewall enabled

### fail2ban Configuration

```bash
# Check fail2ban status
sudo systemctl status fail2ban

# View jails
sudo fail2ban-client status

# View VPK jails
sudo fail2ban-client status vpk-socks
sudo fail2ban-client status vpk-squid
```

- [ ] fail2ban running
- [ ] VPK jails active
- [ ] Test ban (optional): Trigger 5+ auth failures and verify IP banned

### System Updates

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Enable automatic security updates
sudo dpkg-reconfigure --priority=low unattended-upgrades
```

- [ ] System fully updated
- [ ] Automatic updates enabled

### Certificate Management

If using Let's Encrypt:

```bash
# Test auto-renewal
sudo certbot renew --dry-run

# Check certificate expiration
sudo certbot certificates
```

- [ ] Auto-renewal working
- [ ] Certificate valid for 90 days

If using self-signed certificates:

```bash
# Check certificate expiration
openssl x509 -in /etc/vpk/certs/server.crt -noout -enddate

# Set reminder to rotate in 90 days
```

- [ ] Certificate expiration date noted
- [ ] Rotation reminder set

### File Permissions Review

```bash
vpk check-permissions  # If implemented
```

Or manually:

```bash
ls -la /etc/vpk/secret.key
# Should be: -rw------- root root

ls -la /opt/vps-proxy-kit/data/vpk.db
# Should be: -rw------- proxyadmin proxyadmin

ls -la /etc/vpk/certs/server.key
# Should be: -rw------- root root
```

- [ ] Encryption key permissions correct (600, root)
- [ ] Database permissions correct (600, proxyadmin)
- [ ] Certificate key permissions correct (600, root)

## Monitoring Setup

### Prometheus Configuration

```bash
# If Prometheus installed, add scrape configs
sudo nano /etc/prometheus/prometheus.yml
```

Add:

```yaml
scrape_configs:
  - job_name: "vpk"
    static_configs:
      - targets: ["localhost:9100"]
```

```bash
sudo systemctl restart prometheus
```

- [ ] Prometheus scraping VPK metrics
- [ ] Verify metrics: `curl http://localhost:9100/metrics`

### Grafana Dashboard (Optional)

- [ ] Import `examples/grafana-dashboard.json`
- [ ] Configure Prometheus data source
- [ ] Verify dashboard displays data

### Log Monitoring

```bash
# Check log rotation
ls -lh /var/log/vpk/

# Test log parser
vpk view-logs --lines 50
```

- [ ] Logs rotating correctly
- [ ] Log parser processing logs
- [ ] Logs readable and formatted correctly

## User Management

### Create Additional Users

```bash
# Create users for different use cases
vpk create-user --username user1 --password 'Pass1!' --protocol socks --quota 50GB
vpk create-user --username user2 --password 'Pass2!' --protocol https --quota 100GB

# Create API user with token
vpk create-user --username apiuser --token-auth --protocol socks,https --quota 200GB
```

- [ ] Users created successfully
- [ ] User credentials documented securely

### Test Quota Enforcement

```bash
# Set low quota for testing
vpk set-quota --username testuser --quota 1MB

# Generate traffic to exceed quota
# (Use curl or other tools)

# Verify user suspended
vpk quota-usage --username testuser
vpk list-users
```

- [ ] Quota enforcement working
- [ ] Users suspended when quota exceeded
- [ ] Usage counters updating correctly

## Performance Tuning

### System Limits

```bash
# Edit /etc/security/limits.conf
sudo nano /etc/security/limits.conf
```

Add:

```
proxyd soft nofile 65536
proxyd hard nofile 65536
proxyadmin soft nofile 65536
proxyadmin hard nofile 65536
```

```bash
# Edit /etc/sysctl.conf
sudo nano /etc/sysctl.conf
```

Add:

```
net.core.somaxconn = 1024
net.ipv4.tcp_max_syn_backlog = 2048
net.ipv4.ip_local_port_range = 10000 65000
net.ipv4.tcp_tw_reuse = 1
net.ipv4.tcp_fin_timeout = 30
```

```bash
sudo sysctl -p
```

- [ ] File descriptor limits increased
- [ ] Kernel parameters tuned
- [ ] Services restarted to apply changes

### Proxy Service Tuning

Review and adjust:

- `/etc/dante/danted.conf` - Connection limits, timeouts
- `/etc/squid/squid.conf` - Cache size, workers, bandwidth limits

- [ ] Dante configuration tuned
- [ ] Squid configuration tuned
- [ ] Services restarted

## Backup & Recovery

### Set Up Automated Backups

```bash
# Create backup script
sudo nano /usr/local/bin/vpk-backup.sh
```

```bash
#!/bin/bash
BACKUP_DIR="/backup/vpk"
DATE=$(date +%Y%m%d)

mkdir -p "$BACKUP_DIR"

# Backup database and config
tar -czf "$BACKUP_DIR/vpk-$DATE.tar.gz" \
  /opt/vps-proxy-kit/data/vpk.db \
  /etc/vpk/

# Keep last 30 days
find "$BACKUP_DIR" -name "vpk-*.tar.gz" -mtime +30 -delete
```

```bash
sudo chmod +x /usr/local/bin/vpk-backup.sh

# Add to cron
sudo crontab -e
```

Add:

```
0 2 * * * /usr/local/bin/vpk-backup.sh
```

- [ ] Backup script created
- [ ] Cron job scheduled
- [ ] Test backup restoration

### Test Disaster Recovery

```bash
# Test restoring from backup
sudo tar -xzf /backup/vpk/vpk-20251013.tar.gz -C /
sudo systemctl restart vpk-*
vpk status
```

- [ ] Backup restoration tested
- [ ] Services recover correctly

## Documentation

### Update Configuration

```bash
# Edit config with your settings
sudo nano /etc/vpk/config.yml
```

- [ ] External IP configured correctly
- [ ] Hostname set (if using domain)
- [ ] Quotas and thresholds adjusted as needed

### Document Deployment

Create internal documentation:

- [ ] List of users and purposes
- [ ] IP addresses and ports
- [ ] Firewall rules
- [ ] Certificate expiration dates
- [ ] Backup locations
- [ ] Emergency contacts
- [ ] Incident response procedures

## Post-Deployment Testing

### Functional Testing

- [ ] SOCKS5 proxy (no TLS): Port 1080
- [ ] SOCKS5 with TLS: Port 11080
- [ ] HTTP/HTTPS proxy (no TLS): Port 3128
- [ ] HTTPS proxy with TLS: Port 8443
- [ ] User authentication working
- [ ] Token authentication working (if configured)
- [ ] Quota enforcement working
- [ ] User suspension working
- [ ] Metrics endpoint responding
- [ ] Logs being written and parsed

### Load Testing (Optional)

```bash
# Use tools like ab, wrk, or locust to test
# Example with curl in loop:
for i in {1..100}; do
  curl --socks5 user:pass@34.214.132.38:1080 https://ipinfo.io/ip &
done
wait
```

- [ ] System handles expected load
- [ ] No errors under load
- [ ] Usage counters accurate

### Security Testing

- [ ] Port scan from external IP (should only show open proxy ports + SSH)
- [ ] Test with invalid credentials (should be blocked)
- [ ] Test fail2ban (trigger 5+ failures, verify IP banned)
- [ ] Verify TLS configuration (use SSLLabs or similar)
- [ ] Check for common vulnerabilities

## Operational Procedures

### Daily Operations

```bash
# Check system status
vpk status

# View recent logs
vpk view-logs --lines 100

# Check quota usage
vpk quota-usage

# Monitor metrics
curl http://localhost:9100/metrics
```

### Weekly Maintenance

```bash
# Review user list
vpk list-users

# Check for suspended users
vpk list-users --status suspended

# Review audit log
vpk view-logs --since "7 days ago"

# Check system updates
sudo apt update && sudo apt list --upgradable
```

### Monthly Tasks

- [ ] Review and rotate logs
- [ ] Check certificate expiration
- [ ] Review and update user quotas
- [ ] Verify backups are working
- [ ] Review security updates
- [ ] Update documentation

## Troubleshooting

Common issues and solutions documented in:

- Main README.md - Troubleshooting section
- SECURITY.md - Security incident procedures

## Compliance

- [ ] Data retention policy documented (SECURITY.md)
- [ ] Privacy policy updated (if public-facing)
- [ ] Terms of service created (if applicable)
- [ ] Legal warnings displayed
- [ ] Acceptable use policy defined

## Sign-Off

Deployment completed by: **\*\***\_\_\_**\*\***  
Date: **\*\***\_\_\_**\*\***  
Sign-off: **\*\***\_\_\_**\*\***

Next review date: **\*\***\_\_\_**\*\***

---

**Notes:**

- Keep this checklist with deployment documentation
- Update as new features are added
- Review checklist after each deployment
- Document any deviations from standard procedure
