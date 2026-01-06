# Quick Start Guide - Completing Your Installation

Since your bootstrap installation was interrupted, follow these steps to complete the setup:

## 1. Update VPK Code (If Already Installed)

If you've already run bootstrap.sh and just need to update the VPK code:

```bash
cd ~/cusproxy
git pull
# Copy updated files to installation directory
sudo cp -r vpk /opt/vps-proxy-kit/
sudo cp setup.py /opt/vps-proxy-kit/
sudo chown -R proxyadmin:proxyadmin /opt/vps-proxy-kit/vpk /opt/vps-proxy-kit/setup.py
# Reinstall the package
cd /opt/vps-proxy-kit
sudo -u proxyadmin /opt/vps-proxy-kit/venv/bin/pip install -e . --quiet
```

Or re-run the full installation:

```bash
cd ~/cusproxy
sudo bash bootstrap.sh --yes
```

The script should complete successfully now with the fixes we pushed.

## 2. Initialize the Database

After installation completes, initialize the VPK database:

```bash
sudo -u proxyadmin vpk init-db
```

## 3. Create Your First User

Create a user for accessing the proxies:

```bash
# Replace 'alice' and 'YourSecurePassword!' with your preferred credentials
# Quota examples: 50GB, 100GB, 1TB, 500MB
vpk create-user --username alice --password 'YourSecurePassword!' --protocol socks,https --quota 100GB
```

**Important for HTTP/HTTPS Proxies**: Users must also be added to the htpasswd file:

```bash
# Add the user to htpasswd for HTTP/HTTPS proxy authentication
sudo htpasswd -b /etc/vpk/htpasswd alice 'YourSecurePassword!'
```

## 4. Start the Services

Enable and start all proxy services:

```bash
sudo systemctl enable vpk-dante vpk-squid vpk-stunnel vpk-shadowsocks
sudo systemctl start vpk-dante vpk-squid vpk-stunnel vpk-shadowsocks
```

Check status:

```bash
sudo systemctl status vpk-dante vpk-squid vpk-stunnel vpk-shadowsocks
```

## 5. Test Your Proxies

### Test HTTPS Proxy (Recommended - Encrypted)

```bash
curl -x https://alice:YourSecurePassword!@karlito.tech:8443 -k http://ifconfig.me/ip
```

### Test SOCKS5 Proxy

```bash
curl --socks5 alice:YourSecurePassword!@karlito.tech:1080 http://ifconfig.me/ip
```

### Test HTTP Proxy

```bash
curl -x http://alice:YourSecurePassword!@karlito.tech:3128 http://ifconfig.me/ip
```

## 6. Configure Your Client

### For MoreLogin or similar proxy clients:

**HTTPS Proxy (Recommended):**
- Protocol: HTTPS
- Host: karlito.tech
- Port: 8443
- Username: alice
- Password: YourSecurePassword!

**SOCKS5 Proxy (Faster, no encryption):**
- Protocol: SOCKS5
- Host: karlito.tech
- Port: 1080
- Username: alice
- Password: YourSecurePassword!

## Using a Custom Domain

If you want to use a domain (e.g., `darkanon.store`):

- Set your domain's A record to your VPS IP (e.g., `34.214.132.38`).
- Make sure your firewall allows proxy ports (1080, 3128, 8443, 11080).
- If using HTTPS, update your SSL certificates for the new domain.

## Troubleshooting

If services fail to start, check logs:

```bash
sudo journalctl -u vpk-dante -n 50
sudo journalctl -u vpk-squid -n 50
sudo journalctl -u vpk-stunnel -n 50
```

View VPK logs:

```bash
vpk view-logs
```

Check service status:

```bash
vpk status
```

## Management Commands

```bash
# List all users
vpk list-users

# Check user quota
vpk quota-usage --username alice

# Create additional users
vpk create-user --username bob --password 'AnotherPass!' --protocol socks --quota 50GB

# Update user password
vpk update-user --username alice --password 'NewPassword123!'

# Delete user
vpk delete-user --username alice

# Interactive menu
vpk menu
```

## Firewall Check

Make sure your firewall allows the proxy ports:

```bash
sudo ufw allow 1080/tcp  # SOCKS5
sudo ufw allow 3128/tcp  # HTTP
sudo ufw allow 8443/tcp  # HTTPS
sudo ufw allow 11080/tcp # Shadowsocks
sudo ufw status
```

## Adding a User for All Proxies

1. **Create the VPK user:**
   ```bash
   vpk create-user --username anon --password 'carl7641' --protocol socks,https --quota unlimited
   ```
2. **Add to htpasswd for HTTP/HTTPS:**
   ```bash
   sudo htpasswd -b /etc/vpk/htpasswd anon 'carl7641'
   ```
3. **Create system user for SOCKS5 (PAM):**
   ```bash
   sudo useradd -M -s /usr/sbin/nologin anon
   echo 'anon:carl7641' | sudo chpasswd
   ```
4. **Restart Squid:**
   ```bash
   sudo systemctl restart vpk-squid
   ```

---
