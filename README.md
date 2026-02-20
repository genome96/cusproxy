# CusProxy - Multi-Protocol Proxy Server

A production-ready proxy server setup for Ubuntu that provides multiple proxy protocols with authentication and encryption.

## Requirements

- Ubuntu VPS (22.04 LTS recommended)
- Root or `sudo` access
- Open ports on your firewall: `1080`, `3128`, `8443`, `11080`

## Installation

1.  **Clone the repository:**

    ```bash
    git clone https://github.com/genome96/cusproxy.git
    ```

2.  **Navigate into the project directory:**

    ```bash
    cd cusproxy
    ```

3.  **Run the installation script:**

    ```bash
    sudo bash bootstrap.sh
    ```

    This script will automatically install and configure:
    - Dante (SOCKS5 Proxy)
    - Squid (HTTP/HTTPS Proxy)
    - stunnel (TLS wrapper for HTTPS)
    - Shadowsocks (Encrypted Proxy)
    - Systemd services for auto-start on boot.

4.  **Initialize the database and create users:**

    ```bash
    # Initialize the VPK database
    sudo -u proxyadmin vpk init-db

    # Create your first user (for both SOCKS5 and HTTPS proxies)
    vpk create-user --username alice --password 'YourSecurePassword!' --protocol socks,https --quota 100GB
    ```

## Usage

Replace `your-server.com` with your server's actual IP address or domain name.

---

### ⭐ HTTPS Proxy (Encrypted & Authenticated) - Recommended

This is the most secure option, suitable for all use cases.

- **Host**: `your-server.com`
- **Port**: `8443`
- **Username**: The username you created with `vpk create-user`
- **Password**: The password you set for that user.

---

### SOCKS5 Proxy (Authenticated, No Encryption)

Fast, but not encrypted. Use only on trusted networks.

- **Host**: `your-server.com`
- **Port**: `1080`
- **Username**: The username you created with `vpk create-user`
- **Password**: The password you set for that user.

---

### HTTP Proxy (Authenticated, No Encryption)

Basic proxy, not encrypted.

- **Host**: `your-server.com`
- **Port**: `3128`
- **Username**: The username you created with `vpk create-user`
- **Password**: The password you set for that user.

---

### Shadowsocks (Encrypted)

Provides strong encryption, requires a Shadowsocks client.

1.  Edit the configuration file on your server:
    ```bash
    sudo nano /etc/shadowsocks-libev/config.json
    ```
2.  Change the default `password` to a strong password of your choice.
3.  Restart the service to apply changes:
    ```bash
    sudo systemctl restart vpk-shadowsocks
    ```
4.  Use the following details in your client:
    - **Server**: `your-server.com`
    - **Port**: `11080`
    - **Password**: Your new password
    - **Cipher**: `chacha20-ietf-poly1305`

---

## Configuration & Management

### Creating and Managing Users

Users are managed through the `vpk` command-line tool:

- **Create a new user:**

  ```bash
  vpk create-user --username john --password 'SecurePass123!' --protocol socks,https --quota 50GB
  ```

- **List all users:**

  ```bash
  vpk list-users
  ```

- **Change user password:**

  ```bash
  vpk update-user --username john --password 'NewPassword456!'
  ```

- **Delete a user:**
  ```bash
  vpk delete-user --username john
  ```

### Changing Passwords

Proxy user passwords are managed via the `vpk` command (see above).

For system-level changes:

- **Shadowsocks password:**
  Edit the configuration file on your server:

### Managing Services

You can manage the proxy services using `systemctl`:

- **Check Status**: `sudo systemctl status vpk-dante`
- **Restart**: `sudo systemctl restart vpk-dante`
- **View Logs**: `sudo journalctl -u vpk-dante -n 50`

(Replace `vpk-dante` with `vpk-squid`, `vpk-stunnel`, or `vpk-shadowsocks` for the other services).

---

## Troubleshooting

### stunnel Service Won't Start

If the `vpk-stunnel` service fails to start or times out, check the systemd service configuration:

1. Verify the service type matches the stunnel configuration:

   ```bash
   sudo cat /etc/stunnel/vpk.conf | grep foreground
   ```

   If `foreground = yes`, then the systemd service should use `Type=simple`.

2. Fix the service type if needed:

   ```bash
   sudo sed -i 's/Type=forking/Type=simple/' /etc/systemd/system/vpk-stunnel.service
   sudo systemctl daemon-reload
   sudo systemctl restart vpk-stunnel
   ```

3. Verify SSL certificates exist:
   ```bash
   ls -l /etc/vpk/certs/server.crt /etc/vpk/certs/server.key
   ```

### Authentication Failures

**Important**: VPK uses different authentication systems for different proxy types:

- **SOCKS5**: Uses VPK database via PAM authentication
- **HTTP/HTTPS**: Uses htpasswd file at `/etc/vpk/htpasswd`

If you're getting authentication errors:

1. **For SOCKS5 proxies**: Users are managed through the VPK database:

   ```bash
   # List users
   vpk list-users

   # Create a new user
   vpk create-user --username alice --password 'SecurePass123' --protocol socks --quota 50GB
   ```

2. **For HTTP/HTTPS proxies**: You must manually sync users to the htpasswd file:

   ```bash
   # Add user to htpasswd file
   sudo htpasswd -b /etc/vpk/htpasswd alice 'SecurePass123'

   # Verify the user was added
   sudo cat /etc/vpk/htpasswd

   # Restart Squid to apply changes
   sudo systemctl restart vpk-squid
   ```

3. **Verify htpasswd file permissions** (must be readable by Squid):

   ```bash
   ls -la /etc/vpk/htpasswd
   # Should show: -rw-r----- 1 root proxy

   # Fix permissions if needed
   sudo chown root:proxy /etc/vpk/htpasswd
   sudo chmod 640 /etc/vpk/htpasswd
   sudo systemctl restart vpk-squid
   ```

4. **Test authentication manually**:
   ```bash
   # Test htpasswd authentication
   echo "username password" | /usr/lib/squid/basic_ncsa_auth /etc/vpk/htpasswd
   # Should output: OK
   ```

### Domain and DNS Setup

To use your proxy with a custom domain (e.g., `darkanon.store`):

1. Point your domain's A record to your VPS IP (e.g., `34.214.132.38`) in your DNS provider (Cloudflare, etc).
2. Ensure your firewall allows ports 1080, 3128, 8443, 11080.
3. If using HTTPS, update your SSL certificates for the new domain.

---

### System User for SOCKS5 (PAM)

If you use PAM authentication for SOCKS5, you must create a matching system user:

```bash
sudo useradd -M -s /usr/sbin/nologin <username>
echo '<username>:<password>' | sudo chpasswd
```

Example for user `anon`:

```bash
sudo useradd -M -s /usr/sbin/nologin anon
echo 'anon:carl7641' | sudo chpasswd
```

---

### Fixing Squid Log Directory Permissions

If Squid fails to start with a log error:

```bash
sudo chown -R proxy:proxy /var/log/vpk
sudo chmod 755 /var/log/vpk
sudo systemctl restart vpk-squid
```

---

### htpasswd File Permissions

Ensure the htpasswd file is readable by Squid:

```bash
sudo chown root:proxy /etc/vpk/htpasswd
sudo chmod 640 /etc/vpk/htpasswd
```

---

### Example: Add a New User for All Proxies

```bash
# Add to VPK (SOCKS5/HTTPS)
vpk create-user --username anon --password 'carl7641' --protocol socks,https --quota unlimited

# Add to htpasswd (HTTP/HTTPS)
sudo htpasswd -b /etc/vpk/htpasswd anon 'carl7641'

# Add system user for SOCKS5 (PAM)
sudo useradd -M -s /usr/sbin/nologin anon
echo 'anon:carl7641' | sudo chpasswd

# Restart Squid
tsudo systemctl restart vpk-squid
```

---
