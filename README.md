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
    -   Dante (SOCKS5 Proxy)
    -   Squid (HTTP/HTTPS Proxy)
    -   stunnel (TLS wrapper for HTTPS)
    -   Shadowsocks (Encrypted Proxy)
    -   Systemd services for auto-start on boot.

## Usage

Replace `your-server.com` with your server's actual IP address or domain name.

---

### ⭐ HTTPS Proxy (Encrypted & Authenticated) - Recommended

This is the most secure option, suitable for all use cases.

-   **Host**: `your-server.com`
-   **Port**: `8443`
-   **Username**: `admin`
-   **Password**: The password you set during installation.

---

### SOCKS5 Proxy (Authenticated, No Encryption)

Fast, but not encrypted. Use only on trusted networks.

-   **Host**: `your-server.com`
-   **Port**: `1080`
-   **Username**: `socksadmin`
-   **Password**: The password you set for the `socksadmin` user.

---

### HTTP Proxy (Authenticated, No Encryption)

Basic proxy, not encrypted.

-   **Host**: `your-server.com`
-   **Port**: `3128`
-   **Username**: `admin`
-   **Password**: The password you set during installation.

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
    -   **Server**: `your-server.com`
    -   **Port**: `11080`
    -   **Password**: Your new password
    -   **Cipher**: `chacha20-ietf-poly1305`

---

## Configuration & Management

### Changing Passwords

-   **SOCKS5 (`socksadmin` user):**
    ```bash
    sudo passwd socksadmin
    ```

-   **HTTP/HTTPS (`admin` user):**
    First, ensure `apache2-utils` is installed:
    ```bash
    sudo apt-get update && sudo apt-get install -y apache2-utils
    ```
    Then, create a new password (this will overwrite the old one):
    ```bash
    sudo htpasswd -c /etc/squid/passwords admin
    ```
    Finally, restart the proxy services:
    ```bash
    sudo systemctl restart vpk-squid vpk-stunnel
    ```

### Managing Services

You can manage the proxy services using `systemctl`:

-   **Check Status**: `sudo systemctl status vpk-dante`
-   **Restart**: `sudo systemctl restart vpk-dante`
-   **View Logs**: `sudo journalctl -u vpk-dante -n 50`

(Replace `vpk-dante` with `vpk-squid`, `vpk-stunnel`, or `vpk-shadowsocks` for the other services).
