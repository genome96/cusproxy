# VPS Proxy Kit - Encrypted SOCKS5 Connection Guide

## ✅ FIXED: TLS Encryption Now Available via Shadowsocks

Port **11080** now provides **encrypted SOCKS5 proxy** using **Shadowsocks** with **chacha20-ietf-poly1305** encryption.

---

## Connection Details

**Server:** darkanon.store (or 34.214.132.38)  
**Port:** 11080  
**Encryption Method:** chacha20-ietf-poly1305  
**Password:** SecurePass123!VPK2025  
**Protocol:** Shadowsocks (SS)

---

## Client Setup

### Option 1: Shadowsocks Client (Recommended)

**Windows:**
1. Download [Shadowsocks-Windows](https://github.com/shadowsocks/shadowsocks-windows/releases)
2. Install and open Shadowsocks
3. Add server configuration:
   - Server Address: `darkanon.store`
   - Server Port: `11080`
   - Password: `SecurePass123!VPK2025`
   - Encryption: `chacha20-ietf-poly1305`
   - Local Port: `1080` (or any available port)
4. Connect and configure system proxy to use `localhost:1080`

**Linux/Mac:**
```bash
# Install shadowsocks-libev
sudo apt-get install shadowsocks-libev  # Ubuntu/Debian
brew install shadowsocks-libev          # macOS

# Create config file
cat > ss-client.json << EOF
{
    "server": "darkanon.store",
    "server_port": 11080,
    "local_address": "127.0.0.1",
    "local_port": 1080,
    "password": "SecurePass123!VPK2025",
    "timeout": 300,
    "method": "chacha20-ietf-poly1305"
}
EOF

# Start client
ss-local -c ss-client.json -v
```

Then use `localhost:1080` as your SOCKS5 proxy with any application.

### Option 2: Shadowsocks-Rust (Cross-platform)
Download from: https://github.com/shadowsocks/shadowsocks-rust/releases

```bash
# Command line usage
sslocal -s darkanon.store:11080 \
        -b 127.0.0.1:1080 \
        -m chacha20-ietf-poly1305 \
        -k "SecurePass123!VPK2025"
```

---

## Testing Connection

### After setting up shadowsocks client locally:

```bash
# Test with curl (via local shadowsocks client)
curl --socks5 127.0.0.1:1080 https://ipinfo.io/ip
# Should return: 34.214.132.38
```

### Test with browser:
1. Configure browser to use SOCKS5 proxy: `127.0.0.1:1080`
2. Visit https://ipinfo.io/ip
3. Should show: 34.214.132.38

---

## Available Protocols

| Protocol | Port | Encryption | Authentication | Status |
|----------|------|------------|----------------|--------|
| SOCKS5 | 1080 | ❌ None | ❌ None | ✅ Working |
| HTTP/HTTPS | 3128 | ❌ None | ✅ htpasswd | ✅ Working |
| HTTPS+TLS | 8443 | ✅ TLS 1.2+ | ✅ htpasswd | ✅ Working |
| **Shadowsocks** | **11080** | **✅ ChaCha20-Poly1305** | **✅ Password** | **✅ Working** |

---

## Why Shadowsocks Instead of SOCKS5+TLS?

**Problem with SOCKS5+TLS (stunnel approach):**
- Standard SOCKS5 clients don't support TLS wrapping
- curl, browsers don't natively speak "SOCKS5 over TLS"
- Requires complex client-side TLS tunnel setup

**Shadowsocks Solution:**
- ✅ Purpose-built encrypted SOCKS5 protocol
- ✅ Native clients for all platforms
- ✅ Strong encryption (chacha20-ietf-poly1305)
- ✅ Designed for bypassing censorship and providing privacy
- ✅ Industry-standard solution used worldwide

---

## Security Notes

1. **Encryption:** chacha20-ietf-poly1305 is a modern AEAD cipher providing both confidentiality and authentication
2. **Password:** Change the default password in `/etc/vpk/shadowsocks.json` on the server
3. **Cloudflare:** DNS is configured as **DNS-only (gray cloud)** - Cloudflare does not interfere with the connection
4. **Firewall:** Port 11080 is open in AWS Security Group

---

## Server Management

### Service Control
```bash
# Check status
sudo systemctl status vpk-shadowsocks

# Restart service
sudo systemctl restart vpk-shadowsocks

# View logs
sudo tail -f /var/log/vpk/shadowsocks.log

# Check listening port
ss -tlnp | grep 11080
```

### Configuration
Server config: `/etc/vpk/shadowsocks.json`

To change password:
```bash
sudo nano /etc/vpk/shadowsocks.json
sudo systemctl restart vpk-shadowsocks
```

---

## Troubleshooting

### Client can't connect:
1. Check if service is running: `sudo systemctl status vpk-shadowsocks`
2. Check port is listening: `ss -tlnp | grep 11080`
3. Verify AWS Security Group allows port 11080
4. Check logs: `sudo tail /var/log/vpk/shadowsocks.log`

### Authentication fails:
1. Verify password matches exactly (case-sensitive)
2. Verify encryption method is `chacha20-ietf-poly1305`
3. Check server logs for connection attempts

---

## Cloudflare Configuration ✅

**Current DNS Setup:**
- **Status:** DNS-only (gray cloud) ✅
- **Why:** Cloudflare's proxy doesn't support custom ports like 11080
- **Resolution:** Direct A record pointing to 34.214.132.38

**SSL/TLS Mode:**
- Not applicable for Shadowsocks (handles its own encryption)
- For port 8443 (HTTPS+TLS): Set Cloudflare SSL/TLS to "Full" mode

**Firewall:**
- Cloudflare firewall doesn't affect traffic since we're not using the proxy
- All filtering happens at AWS Security Group level

---

## Summary

✅ **Port 11080 now provides encrypted SOCKS5 via Shadowsocks**  
✅ **ChaCha20-Poly1305 encryption enabled**  
✅ **Cloudflare configured correctly (DNS-only)**  
✅ **Service running and listening**  
✅ **AWS firewall allows connections**  

**Next step:** Install a Shadowsocks client on your device and connect using the configuration above!
