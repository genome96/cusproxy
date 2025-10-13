# 🔐 CusProxy - Multi-Protocol Proxy Server

**Production-ready proxy server with authentication, encryption, and multiple protocols**

**Server:** darkanon.store (34.214.132.38)  
**Platform:** Ubuntu 22.04 LTS  
**Location:** AWS Oregon  

---

## ✨ Features

- ✅ **4 Proxy Protocols**: SOCKS5, HTTP, HTTPS+TLS, Shadowsocks
- ✅ **Authentication**: Username/password on all protocols
- ✅ **Encryption**: TLS 1.2+ (HTTPS), ChaCha20 (Shadowsocks)
- ✅ **Auto-Start**: Systemd services (survives reboots)
- ✅ **MoreLogin Compatible**: Direct copy-paste configuration
- ✅ **Security Hardened**: No unauthenticated access

---

## 🚀 Available Protocols

### 1. SOCKS5 with Authentication (Port 1080) ⭐
```
Protocol:  SOCKS5
Host:      darkanon.store
Port:      1080
Username:  socksadmin
Password:  SecurePass123!
```
- ✅ Authentication: Username/Password
- ❌ Encryption: None (plaintext)
- 📱 MoreLogin: Native support
- 🔒 Use for: Testing, private networks

**MoreLogin Format:** `darkanon.store:1080:socksadmin:SecurePass123!`

---

### 2. HTTP Proxy (Port 3128)
```
Protocol:  HTTP
Host:      darkanon.store
Port:      3128
Username:  admin
Password:  SecurePass123!
```
- ✅ Authentication: Username/Password
- ❌ Encryption: None
- 📱 MoreLogin: Native support

**MoreLogin Format:** `darkanon.store:3128:admin:SecurePass123!`

---

### 3. HTTPS Proxy with TLS (Port 8443) ⭐ RECOMMENDED
```
Protocol:  HTTPS
Host:      darkanon.store
Port:      8443
Username:  admin
Password:  SecurePass123!
[✓] Ignore SSL certificate errors
```
- ✅ Authentication: Username/Password
- ✅ Encryption: TLS 1.2+ (military-grade)
- 📱 MoreLogin: Native support
- 🔒 Use for: Production, public WiFi, security

**MoreLogin Format:** `darkanon.store:8443:admin:SecurePass123!`

**This is the recommended option for encrypted + authenticated proxy!**

---

### 4. Shadowsocks (Port 11080)
```
Protocol:  Shadowsocks
Host:      darkanon.store
Port:      11080
Password:  YourStrongPassword123!
Method:    chacha20-ietf-poly1305
```
- ✅ Authentication: Password
- ✅ Encryption: ChaCha20
- ⚠️ MoreLogin: Needs Shadowsocks client
- 🔒 Use for: Maximum security, anti-censorship

---

## 📋 Quick Comparison

| Port | Protocol | Auth | Encryption | MoreLogin | Best For |
|------|----------|------|------------|-----------|----------|
| **1080** | SOCKS5 | ✅ | ❌ | ✅ Native | Testing, speed |
| **3128** | HTTP | ✅ | ❌ | ✅ Native | Basic proxy |
| **8443** | HTTPS | ✅ | ✅ TLS | ✅ Native | **Production** ⭐ |
| **11080** | Shadowsocks | ✅ | ✅ ChaCha20 | ⚠️ Client | Max security |

---

## 🔐 Security Features

### Authentication
- ✅ All protocols require credentials
- ✅ Unauthenticated requests are blocked
- ✅ PAM-based (SOCKS5) and htpasswd (HTTP/HTTPS)

### Encryption
- ✅ Port 8443: TLS 1.2+ (same as HTTPS websites)
- ✅ Port 11080: ChaCha20 stream cipher
- ⚠️ Port 1080 & 3128: No encryption (plaintext)

### Access Control
- ✅ Systemd service hardening
- ✅ Firewall rules configured
- ✅ No anonymous proxy access

---

## 🎯 Recommended Setup for MoreLogin

### For Security (Encrypted + Authenticated): Use Port 8443
```
Protocol:  HTTPS
Host:      darkanon.store
Port:      8443
Username:  admin
Password:  SecurePass123!
```
**Why?**
- ✅ Full TLS encryption
- ✅ Authentication required
- ✅ Works natively in MoreLogin
- ✅ Secure for public networks

### For Speed (Authenticated Only): Use Port 1080
```
Protocol:  SOCKS5
Host:      darkanon.store
Port:      1080
Username:  socksadmin
Password:  SecurePass123!
```
**Why?**
- ✅ Faster (no TLS overhead)
- ✅ Authentication required
- ⚠️ No encryption (use on trusted networks only)

---

## 📖 Additional Documentation

- **[MORELOGIN_SETUP.md](MORELOGIN_SETUP.md)** - Complete MoreLogin configuration guide
- **[AUTHENTICATED_SOCKS5_WORKING.md](AUTHENTICATED_SOCKS5_WORKING.md)** - SOCKS5 authentication details
- **[SOCKS5_ENCRYPTION_EXPLAINED.md](SOCKS5_ENCRYPTION_EXPLAINED.md)** - Understanding SOCKS5 encryption
- **[SSH_TUNNEL_SETUP.md](SSH_TUNNEL_SETUP.md)** - SSH tunnel for encrypted SOCKS5
- **[SECURITY.md](SECURITY.md)** - Security best practices

---

## 🛠️ Server Configuration

### Services Running
```bash
# SOCKS5 (Dante)
sudo systemctl status vpk-dante

# HTTP/HTTPS (Squid + stunnel)
sudo systemctl status vpk-squid
sudo systemctl status vpk-stunnel

# Shadowsocks
sudo systemctl status vpk-shadowsocks
```

### Configuration Files
- **SOCKS5**: `/etc/dante/danted.conf`
- **HTTP**: `/etc/squid/squid.conf`
- **HTTPS**: `/etc/stunnel/stunnel.conf`
- **Shadowsocks**: `/etc/shadowsocks-libev/config.json`

### User Management
- **SOCKS5 users**: System users (PAM authentication)
- **HTTP/HTTPS users**: `/etc/squid/passwords` (htpasswd)

---

## 🧪 Testing

### Test SOCKS5 Authentication
```bash
# Should work (with credentials)
curl -x socks5://socksadmin:SecurePass123!@darkanon.store:1080 http://ifconfig.me/ip

# Should fail (no credentials)
curl -x socks5://darkanon.store:1080 http://ifconfig.me/ip
```

### Test HTTPS Proxy
```bash
# With authentication
curl -x https://admin:SecurePass123!@darkanon.store:8443 -k http://ifconfig.me/ip
```

### Python Test Scripts
```bash
# Test all SOCKS5 configurations
python test_socks5.py

# Test SSH tunnel (if configured)
python test_ssh_tunnel.py
```

---

## 🔄 Updates and Maintenance

### Check Service Status
```bash
sudo systemctl status vpk-dante
sudo systemctl status vpk-squid
sudo systemctl status vpk-stunnel
sudo systemctl status vpk-shadowsocks
```

### Restart Services
```bash
sudo systemctl restart vpk-dante
sudo systemctl restart vpk-squid
sudo systemctl restart vpk-stunnel
sudo systemctl restart vpk-shadowsocks
```

### View Logs
```bash
sudo journalctl -u vpk-dante -n 50
sudo journalctl -u vpk-squid -n 50
```

---

## 📊 Service Ports

| Port | Service | Protocol | Status |
|------|---------|----------|--------|
| 22 | SSH | SSH | ✅ Open |
| 1080 | Dante | SOCKS5 | ✅ Running |
| 3128 | Squid | HTTP | ✅ Running |
| 8443 | Stunnel→Squid | HTTPS+TLS | ✅ Running |
| 11080 | Shadowsocks | SS+ChaCha20 | ✅ Running |

---

## 🔒 Security Notes

### SOCKS5 (Port 1080)
- ⚠️ **NO ENCRYPTION** - Credentials and traffic sent in plaintext
- ✅ Authentication required
- 🔴 **DO NOT use on public WiFi or untrusted networks**
- 🟢 Safe for: Private networks, testing, trusted environments

### HTTPS (Port 8443)
- ✅ **FULL TLS ENCRYPTION** - All traffic encrypted
- ✅ Authentication required
- 🟢 Safe for: Production, public WiFi, any network
- ⭐ **Recommended for all serious use**

### Best Practice
**If you need encryption → Use Port 8443 (HTTPS)**  
**If encryption not needed → Use Port 1080 (SOCKS5)**

---

## 📜 License

MIT License - See [LICENSE](LICENSE) file

---

## 🎉 Quick Start Summary

**Want encrypted proxy for MoreLogin?**
```
Use: darkanon.store:8443:admin:SecurePass123!
Protocol: HTTPS
```

**Want fast SOCKS5 for testing?**
```
Use: darkanon.store:1080:socksadmin:SecurePass123!
Protocol: SOCKS5
```

**Both options:**
- ✅ Authentication required
- ✅ Work in MoreLogin
- ✅ Already configured and tested
- ✅ Auto-start on boot

**Choose 8443 for security, 1080 for speed!**

---

**Last Updated:** October 13, 2025  
**Status:** All services operational ✅
