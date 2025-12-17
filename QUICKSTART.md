# Quick Start Guide - Completing Your Installation

Since your bootstrap installation was interrupted, follow these steps to complete the setup:

## 1. Complete the Installation

SSH into your server and run:

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
vpk create-user --username alice --password 'YourSecurePassword!' --protocol socks,https --quota 100GB
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
