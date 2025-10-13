# Fresh Installation Guide

Complete guide for installing VPS Proxy Kit on a clean Ubuntu 22.04 server.

## Prerequisites

- Fresh Ubuntu 22.04 LTS server
- Root or sudo access
- At least 1GB RAM
- 10GB free disk space
- Public IP address
- (Optional) Domain name pointed to server IP

## Quick Start

### Option 1: With Domain Name (Recommended for Production)

**Before installation:**
1. Configure DNS A record pointing to your VPS IP
2. Wait 2-5 minutes for DNS propagation
3. Verify: `nslookup proxy.yourdomain.com`

**Install:**
```bash
# Clone repository
git clone https://github.com/genome96/cusproxy.git
cd cusproxy

# Run installer (will prompt for domain)
sudo ./bootstrap.sh

# Or specify domain directly
sudo ./bootstrap.sh --domain proxy.yourdomain.com
```

### Option 2: Without Domain (Self-Signed Certificate)

```bash
# Clone repository
git clone https://github.com/genome96/cusproxy.git
cd cusproxy

# Run installer
sudo ./bootstrap.sh
```

When prompted about domain, answer "No" or press Enter.

### Option 3: Fully Automated (No Prompts)

```bash
# With domain
sudo ./bootstrap.sh --yes --domain proxy.yourdomain.com

# Without domain
sudo ./bootstrap.sh --yes
```

## Installation Process

The bootstrap script will automatically:

1. ✅ Update system packages
2. ✅ Install dependencies (Python, Dante, Squid, stunnel, fail2ban)
3. ✅ Create service users (proxyadmin, proxyd)
4. ✅ Create directory structure
5. ✅ Generate encryption keys
6. ✅ Obtain SSL certificate (Let's Encrypt or self-signed)
7. ✅ Configure all proxy services
8. ✅ Set up firewall rules (UFW)
9. ✅ Configure fail2ban for DDoS protection
10. ✅ Create systemd services
11. ✅ Start all services

**Installation time:** 3-5 minutes

## Post-Installation

### 1. Verify Services

```bash
# Check all services
sudo systemctl status vpk-squid vpk-dante vpk-stunnel

# Should all show "active (running)"
```

### 2. Initialize Database

```bash
# Initialize VPK database
sudo vpk init-db
```

### 3. Create First User

```bash
# Create admin user with full access
sudo vpk create-user \
  --username admin \
  --password 'YourSecurePassword123!' \
  --protocol all \
  --quota 1TB
```

### 4. Test Proxies

**Test SOCKS5 proxy:**
```bash
# From another machine
curl -x socks5://admin:YourSecurePassword123!@YOUR_VPS_IP:1080 https://ifconfig.me
```

**Test HTTP proxy:**
```bash
# From another machine
curl -x http://admin:YourSecurePassword123!@YOUR_VPS_IP:3128 https://ifconfig.me
```

**Test SOCKS5 with TLS:**
```bash
# From another machine
curl -x socks5h://admin:YourSecurePassword123!@YOUR_VPS_IP:11080 https://ifconfig.me
```

**Test HTTPS with TLS:**
```bash
# From another machine
curl -x https://admin:YourSecurePassword123!@YOUR_VPS_IP:8443 https://ifconfig.me
```

## Troubleshooting

### Issue: Services not starting

**Check logs:**
```bash
sudo journalctl -u vpk-dante -n 50
sudo journalctl -u vpk-squid -n 50
sudo journalctl -u vpk-stunnel -n 50
```

**Common solutions:**
```bash
# Fix log file permissions
sudo chown -R proxyd:proxyd /var/log/vpk/

# Restart services
sudo systemctl restart vpk-dante vpk-squid vpk-stunnel
```

### Issue: Port already in use

**Check what's using the port:**
```bash
sudo netstat -tlnp | grep :1080
sudo netstat -tlnp | grep :3128
```

**Kill conflicting process:**
```bash
sudo fuser -k 1080/tcp
sudo fuser -k 3128/tcp
```

### Issue: Can't connect to proxy

**Check firewall:**
```bash
sudo ufw status

# Allow ports if blocked
sudo ufw allow 1080,3128,8443,11080/tcp
```

**Check if services are listening:**
```bash
sudo netstat -tlnp | grep -E ':(1080|3128|8443|11080)'
```

### Issue: Let's Encrypt certificate failed

**Common causes:**
1. DNS not propagated yet (wait 5 minutes and retry)
2. Cloudflare proxy enabled (must be DNS only / gray cloud)
3. Port 80 blocked by firewall
4. Another service using port 80

**Retry certificate:**
```bash
# Stop services
sudo systemctl stop vpk-squid

# Retry with acme.sh
sudo /root/.acme.sh/acme.sh --issue -d proxy.yourdomain.com --standalone --force

# Restart services
sudo systemctl start vpk-squid
```

## Configuration Files

All configuration files are located in `/etc/vpk/`:

```
/etc/vpk/
├── certs/
│   ├── server.crt     # SSL certificate
│   └── server.key     # SSL private key
├── config.yaml        # VPK configuration
└── secret.key         # Master encryption key

/etc/dante/
└── danted.conf        # Dante SOCKS5 config

/etc/squid/
└── squid.conf         # Squid HTTP/HTTPS config

/etc/stunnel/
└── vpk.conf           # stunnel TLS wrapper config
```

## Management Commands

```bash
# Check status
sudo vpk status

# List users
sudo vpk list-users

# Create user
sudo vpk create-user --username newuser --password 'Pass123!' --protocol all --quota 500GB

# Delete user
sudo vpk delete-user --username olduser

# Update quota
sudo vpk update-quota --username newuser --quota 1TB

# View logs
sudo vpk logs --lines 50

# View metrics
sudo vpk metrics

# Backup configuration
sudo vpk backup

# Test proxy connectivity
sudo vpk test-proxy --username admin
```

## Security Recommendations

### 1. Change Default Settings

```bash
# Edit VPK config
sudo nano /etc/vpk/config.yaml

# Update:
# - database path
# - log levels
# - quota limits
```

### 2. Restrict Access by IP (Recommended)

```bash
# Allow only specific IPs
sudo ufw delete allow 1080,3128,8443,11080/tcp
sudo ufw allow from YOUR_HOME_IP to any port 1080,3128,8443,11080 proto tcp
sudo ufw reload
```

### 3. Enable Rate Limiting (Already configured via fail2ban)

```bash
# Check fail2ban status
sudo fail2ban-client status vpk-proxy

# View banned IPs
sudo fail2ban-client status vpk-proxy | grep "Banned IP"
```

### 4. Regular Updates

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Update VPK
cd /opt/vps-proxy-kit/cusproxy
git pull origin master
sudo ./bootstrap.sh --yes  # Re-run to apply updates
```

### 5. Monitor Logs

```bash
# Set up log monitoring
sudo apt install logwatch
sudo logwatch --detail high --service all --range today --mailto admin@yourdomain.com
```

## Performance Tuning

### For High Traffic (1000+ concurrent connections)

```bash
# Increase file descriptor limits
sudo nano /etc/security/limits.conf

# Add:
proxyd soft nofile 65535
proxyd hard nofile 65535

# Tune Squid
sudo nano /etc/squid/squid.conf

# Increase:
# cache_mem 256 MB
# maximum_object_size 512 MB
# cache_dir ufs /var/spool/squid 10000 16 256
```

### For Low Latency

```bash
# Tune kernel parameters
sudo nano /etc/sysctl.conf

# Add:
net.ipv4.tcp_fastopen = 3
net.ipv4.tcp_tw_reuse = 1
net.core.rmem_max = 134217728
net.core.wmem_max = 134217728
net.ipv4.tcp_rmem = 4096 87380 67108864
net.ipv4.tcp_wmem = 4096 65536 67108864

# Apply
sudo sysctl -p
```

## Uninstallation

To completely remove VPS Proxy Kit:

```bash
# Stop and disable services
sudo systemctl stop vpk-dante vpk-squid vpk-stunnel
sudo systemctl disable vpk-dante vpk-squid vpk-stunnel

# Remove systemd units
sudo rm /etc/systemd/system/vpk-*.service
sudo systemctl daemon-reload

# Remove files
sudo rm -rf /opt/vps-proxy-kit
sudo rm -rf /etc/vpk
sudo rm -rf /var/log/vpk
sudo rm /etc/dante/danted.conf
sudo rm /etc/stunnel/vpk.conf

# Remove users
sudo userdel -r proxyadmin
sudo userdel proxyd

# Remove packages (optional)
sudo apt remove --purge dante-server squid stunnel4
sudo apt autoremove -y
```

## Upgrading from Old Installation

If you have an existing installation:

```bash
# Backup existing configuration
sudo /opt/vps-proxy-kit/venv/bin/vpk backup

# Pull latest code
cd /opt/vps-proxy-kit/cusproxy
git pull origin master

# Re-run bootstrap (will preserve data)
sudo ./bootstrap.sh --yes

# Restore configuration if needed
sudo /opt/vps-proxy-kit/venv/bin/vpk restore /path/to/backup.tar.gz
```

## Additional Resources

- [Cloudflare Setup Guide](CLOUDFLARE_SETUP.md) - SSL/TLS with Cloudflare
- [Deployment Guide](DEPLOYMENT.md) - Advanced deployment scenarios
- [Security Guide](SECURITY.md) - Hardening and best practices
- [Quick Start Guide](QUICKSTART.md) - Basic usage examples

## Support

- **Documentation**: https://github.com/genome96/cusproxy
- **Issues**: https://github.com/genome96/cusproxy/issues
- **Discussions**: https://github.com/genome96/cusproxy/discussions

---

**Installation successful? Don't forget to:**
1. ⭐ Star the repository
2. 🔒 Secure your proxy with strong passwords
3. 📊 Monitor resource usage
4. 🔄 Enable automatic updates
