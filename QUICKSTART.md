# Quick Start Guide - 10 Commands

This guide gets VPS Proxy Kit running on Ubuntu 22.04 in 10 commands.

## Prerequisites

- Ubuntu 22.04 LTS server
- Root/sudo access
- Public IP: `34.214.132.38` (replace with your IP)

## Installation

### 1. Update System

```bash
sudo apt update && sudo apt upgrade -y
```

### 2. Clone Repository

```bash
cd /tmp
git clone https://github.com/yourusername/vps-proxy-kit.git
cd vps-proxy-kit
```

### 3. Run Bootstrap Installer

```bash
sudo ./bootstrap.sh --yes
```

This installs all dependencies, creates users, configures services, and sets up the firewall. Takes 3-5 minutes.

### 4. Initialize Database

```bash
sudo -u proxyadmin vpk init-db
```

### 5. Start Monitoring Services

```bash
sudo systemctl start vpk-logparser vpk-quota vpk-metrics
```

### 6. Create First User

```bash
vpk create-user \
  --username alice \
  --password 'MySecurePassword123!' \
  --protocol socks,https \
  --quota 100GB
```

### 7. Check Status

```bash
vpk status
```

You should see:

- Active users: 1
- SOCKS5: Enabled (port 1080)
- HTTPS Proxy: Enabled (port 3128)

### 8. Test SOCKS5 Proxy

```bash
curl --socks5 alice:MySecurePassword123!@localhost:1080 https://ipinfo.io/ip
```

Should return your server's public IP: `34.214.132.38`

### 9. Test HTTP Proxy

```bash
curl --proxy http://alice:MySecurePassword123!@localhost:3128 https://ipinfo.io/ip
```

Should return your server's public IP: `34.214.132.38`

### 10. Test from Remote Client

```bash
# From your local machine:
curl --socks5 alice:MySecurePassword123!@34.214.132.38:1080 https://ipinfo.io/ip
```

Should return your server's IP, confirming the proxy is working!

---

## What's Running?

| Service          | Port  | Purpose                             |
| ---------------- | ----- | ----------------------------------- |
| Dante SOCKS5     | 1080  | SOCKS5 proxy (no TLS)               |
| Dante SOCKS5+TLS | 11080 | SOCKS5 with TLS encryption          |
| Squid HTTP/HTTPS | 3128  | HTTP/HTTPS proxy (no TLS)           |
| Squid+TLS        | 8443  | HTTPS proxy with TLS                |
| Metrics          | 9100  | Prometheus metrics (localhost only) |

---

## Next Steps

### Add More Users

```bash
vpk create-user --username bob --password 'BobPass123!' --protocol socks --quota 50GB
```

### View Users

```bash
vpk list-users
```

### Check Quota Usage

```bash
vpk quota-usage --username alice
```

### View Logs

```bash
vpk view-logs --lines 50
```

### Monitor Active Sessions

```bash
vpk show-sessions
```

---

## Security Hardening (Recommended)

1. **Change SSH Port**

   ```bash
   sudo nano /etc/ssh/sshd_config
   # Change Port 22 to Port 2222
   sudo systemctl restart sshd
   sudo ufw allow 2222/tcp
   sudo ufw delete allow 22/tcp
   ```

2. **Disable SSH Password Auth (use keys only)**

   ```bash
   sudo nano /etc/ssh/sshd_config
   # Set: PasswordAuthentication no
   sudo systemctl restart sshd
   ```

3. **Set Up Let's Encrypt (if you have a domain)**
   ```bash
   sudo certbot certonly --standalone -d proxy.example.com
   # Update stunnel config to use Let's Encrypt certs
   ```

---

## Troubleshooting

### Proxy not working?

1. Check firewall:

   ```bash
   sudo ufw status
   ```

2. Check services:

   ```bash
   sudo systemctl status vpk-dante
   sudo systemctl status vpk-squid
   ```

3. Check logs:
   ```bash
   vpk view-logs --lines 100
   ```

### Authentication failed?

1. Verify user exists:

   ```bash
   vpk user-info --username alice
   ```

2. Check user status is 'active'

3. Try resetting password:
   ```bash
   vpk update-password --username alice
   ```

---

## Documentation

- **Full README**: `README.md`
- **Security Guide**: `SECURITY.md`
- **Deployment Checklist**: `DEPLOYMENT.md`
- **Client Examples**: `examples/client-examples.txt`

---

## Support

- GitHub Issues: https://github.com/yourusername/vps-proxy-kit/issues
- Documentation: See README.md

---

**You're all set! Your proxy server is now running securely.**

For production use, follow the full deployment checklist in `DEPLOYMENT.md`.
