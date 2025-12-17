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

If you're getting authentication errors, verify you're using the correct password file:

- For HTTP/HTTPS proxies, check: `/etc/vpk/htpasswd`
- For SOCKS5, use the system user password: `sudo passwd socksadmin`
