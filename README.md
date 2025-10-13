# CusProxy - Multi-Protocol Proxy Server# 🔐 CusProxy - Multi-Protocol Proxy Server



**Production-ready proxy server with authentication and encryption****Production-ready proxy server with authentication, encryption, and multiple protocols**



Server: `darkanon.store` (34.214.132.38)**Server:** darkanon.store (34.214.132.38)  

**Platform:** Ubuntu 22.04 LTS  

---**Location:** AWS Oregon  



## 🚀 Quick Start---



### Available Proxies (Ready to Use)## ✨ Features



**1. HTTPS Proxy (Encrypted + Authenticated) ⭐ RECOMMENDED**- ✅ **4 Proxy Protocols**: SOCKS5, HTTP, HTTPS+TLS, Shadowsocks

```- ✅ **Authentication**: Username/password on all protocols

Host:     darkanon.store- ✅ **Encryption**: TLS 1.2+ (HTTPS), ChaCha20 (Shadowsocks)

Port:     8443- ✅ **Auto-Start**: Systemd services (survives reboots)

Protocol: HTTPS- ✅ **MoreLogin Compatible**: Direct copy-paste configuration

Username: admin- ✅ **Security Hardened**: No unauthenticated access

Password: SecurePass123!

```---

- ✅ Full TLS encryption

- ✅ Authentication required## 🚀 Available Protocols

- ✅ Best for production use

### 1. SOCKS5 with Authentication (Port 1080) ⭐

**2. SOCKS5 Proxy (Authenticated, No Encryption)**```

```Protocol:  SOCKS5

Host:     darkanon.storeHost:      darkanon.store

Port:     1080Port:      1080

Protocol: SOCKS5Username:  socksadmin

Username: socksadminPassword:  SecurePass123!

Password: SecurePass123!```

```- ✅ Authentication: Username/Password

- ✅ Authentication required- ❌ Encryption: None (plaintext)

- ❌ No encryption (use on trusted networks only)- 📱 MoreLogin: Native support

- ✅ Faster than HTTPS- 🔒 Use for: Testing, private networks



**3. HTTP Proxy (Authenticated)****MoreLogin Format:** `darkanon.store:1080:socksadmin:SecurePass123!`

```

Host:     darkanon.store---

Port:     3128

Protocol: HTTP### 2. HTTP Proxy (Port 3128)

Username: admin```

Password: SecurePass123!Protocol:  HTTP

```Host:      darkanon.store

Port:      3128

**4. Shadowsocks (Encrypted)**Username:  admin

```Password:  SecurePass123!

Host:     darkanon.store```

Port:     11080- ✅ Authentication: Username/Password

Password: YourStrongPassword123!- ❌ Encryption: None

Method:   chacha20-ietf-poly1305- 📱 MoreLogin: Native support

```

- Requires Shadowsocks client**MoreLogin Format:** `darkanon.store:3128:admin:SecurePass123!`



------



## 📋 Comparison### 3. HTTPS Proxy with TLS (Port 8443) ⭐ RECOMMENDED

```

| Port | Protocol | Auth | Encryption | Best For |Protocol:  HTTPS

|------|----------|------|------------|----------|Host:      darkanon.store

| 8443 | HTTPS    | ✅   | ✅ TLS     | Production, public WiFi |Port:      8443

| 1080 | SOCKS5   | ✅   | ❌         | Testing, speed |Username:  admin

| 3128 | HTTP     | ✅   | ❌         | Basic proxy |Password:  SecurePass123!

| 11080| Shadowsocks | ✅ | ✅ ChaCha20 | Max security |[✓] Ignore SSL certificate errors

```

---- ✅ Authentication: Username/Password

- ✅ Encryption: TLS 1.2+ (military-grade)

## ⚙️ Installation (Fresh Server)- 📱 MoreLogin: Native support

- 🔒 Use for: Production, public WiFi, security

### Requirements

- Ubuntu 22.04 LTS**MoreLogin Format:** `darkanon.store:8443:admin:SecurePass123!`

- Root access

- Ports 1080, 3128, 8443, 11080 open**This is the recommended option for encrypted + authenticated proxy!**



### Install---

```bash

# Clone repository### 4. Shadowsocks (Port 11080)

git clone https://github.com/genome96/cusproxy.git```

cd cusproxyProtocol:  Shadowsocks

Host:      darkanon.store

# Run installer as rootPort:      11080

sudo bash bootstrap.shPassword:  YourStrongPassword123!

```Method:    chacha20-ietf-poly1305

```

The installer will:- ✅ Authentication: Password

1. Install Dante (SOCKS5), Squid (HTTP), stunnel (TLS), Shadowsocks- ✅ Encryption: ChaCha20

2. Configure authentication- ⚠️ MoreLogin: Needs Shadowsocks client

3. Set up systemd services (auto-start on boot)- 🔒 Use for: Maximum security, anti-censorship

4. Configure firewall rules

---

---

## 📋 Quick Comparison

## 🔧 Configuration

| Port | Protocol | Auth | Encryption | MoreLogin | Best For |

### Change Passwords|------|----------|------|------------|-----------|----------|

| **1080** | SOCKS5 | ✅ | ❌ | ✅ Native | Testing, speed |

**SOCKS5 (socksadmin user):**| **3128** | HTTP | ✅ | ❌ | ✅ Native | Basic proxy |

```bash| **8443** | HTTPS | ✅ | ✅ TLS | ✅ Native | **Production** ⭐ |

sudo passwd socksadmin| **11080** | Shadowsocks | ✅ | ✅ ChaCha20 | ⚠️ Client | Max security |

```

---

**HTTP/HTTPS (admin user):**

```bash## 🔐 Security Features

# Create new password file

sudo htpasswd -c /etc/squid/passwords admin### Authentication

sudo systemctl restart vpk-squid vpk-stunnel- ✅ All protocols require credentials

```- ✅ Unauthenticated requests are blocked

- ✅ PAM-based (SOCKS5) and htpasswd (HTTP/HTTPS)

**Shadowsocks:**

```bash### Encryption

sudo nano /etc/shadowsocks-libev/config.json- ✅ Port 8443: TLS 1.2+ (same as HTTPS websites)

# Change "password" field- ✅ Port 11080: ChaCha20 stream cipher

sudo systemctl restart vpk-shadowsocks- ⚠️ Port 1080 & 3128: No encryption (plaintext)

```

### Access Control

### Add More Users- ✅ Systemd service hardening

- ✅ Firewall rules configured

**SOCKS5:**- ✅ No anonymous proxy access

```bash

sudo useradd -r -m -s /bin/false newuser---

sudo passwd newuser

```## 🎯 Recommended Setup for MoreLogin



**HTTP/HTTPS:**### For Security (Encrypted + Authenticated): Use Port 8443

```bash```

sudo htpasswd /etc/squid/passwords newuserProtocol:  HTTPS

sudo systemctl restart vpk-squid vpk-stunnelHost:      darkanon.store

```Port:      8443

Username:  admin

---Password:  SecurePass123!

```

## 🛠️ Service Management**Why?**

- ✅ Full TLS encryption

### Check Status- ✅ Authentication required

```bash- ✅ Works natively in MoreLogin

sudo systemctl status vpk-dante      # SOCKS5- ✅ Secure for public networks

sudo systemctl status vpk-squid      # HTTP

sudo systemctl status vpk-stunnel    # HTTPS### For Speed (Authenticated Only): Use Port 1080

sudo systemctl status vpk-shadowsocks```

```Protocol:  SOCKS5

Host:      darkanon.store

### Restart ServicesPort:      1080

```bashUsername:  socksadmin

sudo systemctl restart vpk-dantePassword:  SecurePass123!

sudo systemctl restart vpk-squid```

sudo systemctl restart vpk-stunnel**Why?**

sudo systemctl restart vpk-shadowsocks- ✅ Faster (no TLS overhead)

```- ✅ Authentication required

- ⚠️ No encryption (use on trusted networks only)

### Enable Auto-Start

```bash---

sudo systemctl enable vpk-dante

sudo systemctl enable vpk-squid## 📖 Additional Documentation

sudo systemctl enable vpk-stunnel

sudo systemctl enable vpk-shadowsocks- **[MORELOGIN_SETUP.md](MORELOGIN_SETUP.md)** - Complete MoreLogin configuration guide

```- **[AUTHENTICATED_SOCKS5_WORKING.md](AUTHENTICATED_SOCKS5_WORKING.md)** - SOCKS5 authentication details

- **[SOCKS5_ENCRYPTION_EXPLAINED.md](SOCKS5_ENCRYPTION_EXPLAINED.md)** - Understanding SOCKS5 encryption

### View Logs- **[SSH_TUNNEL_SETUP.md](SSH_TUNNEL_SETUP.md)** - SSH tunnel for encrypted SOCKS5

```bash- **[SECURITY.md](SECURITY.md)** - Security best practices

sudo journalctl -u vpk-dante -n 50

sudo journalctl -u vpk-squid -n 50---

```

## 🛠️ Server Configuration

---

### Services Running

## 📁 Configuration Files```bash

# SOCKS5 (Dante)

- **SOCKS5**: `/etc/dante/danted.conf`sudo systemctl status vpk-dante

- **HTTP**: `/etc/squid/squid.conf`

- **HTTPS**: `/etc/stunnel/stunnel.conf`# HTTP/HTTPS (Squid + stunnel)

- **Shadowsocks**: `/etc/shadowsocks-libev/config.json`sudo systemctl status vpk-squid

- **HTTP/HTTPS Passwords**: `/etc/squid/passwords`sudo systemctl status vpk-stunnel



---# Shadowsocks

sudo systemctl status vpk-shadowsocks

## 🧪 Testing```



### Test with curl### Configuration Files

- **SOCKS5**: `/etc/dante/danted.conf`

**SOCKS5:**- **HTTP**: `/etc/squid/squid.conf`

```bash- **HTTPS**: `/etc/stunnel/stunnel.conf`

curl -x socks5://socksadmin:SecurePass123!@darkanon.store:1080 http://ifconfig.me/ip- **Shadowsocks**: `/etc/shadowsocks-libev/config.json`

```

### User Management

**HTTP:**- **SOCKS5 users**: System users (PAM authentication)

```bash- **HTTP/HTTPS users**: `/etc/squid/passwords` (htpasswd)

curl -x http://admin:SecurePass123!@darkanon.store:3128 http://ifconfig.me/ip

```---



**HTTPS:**## 🧪 Testing

```bash

curl -x https://admin:SecurePass123!@darkanon.store:8443 -k http://ifconfig.me/ip### Test SOCKS5 Authentication

``````bash

# Should work (with credentials)

### Test Authenticationcurl -x socks5://socksadmin:SecurePass123!@darkanon.store:1080 http://ifconfig.me/ip



**Should FAIL (no credentials):**# Should fail (no credentials)

```bashcurl -x socks5://darkanon.store:1080 http://ifconfig.me/ip

curl -x socks5://darkanon.store:1080 http://ifconfig.me/ip```

```

### Test HTTPS Proxy

**Should WORK (with credentials):**```bash

```bash# With authentication

curl -x socks5://socksadmin:SecurePass123!@darkanon.store:1080 http://ifconfig.me/ipcurl -x https://admin:SecurePass123!@darkanon.store:8443 -k http://ifconfig.me/ip

``````



---### Python Test Scripts

```bash

## 🔒 Security Notes# Test all SOCKS5 configurations

python test_socks5.py

### HTTPS (Port 8443) - Recommended

- ✅ Full TLS 1.2+ encryption# Test SSH tunnel (if configured)

- ✅ Credentials encryptedpython test_ssh_tunnel.py

- ✅ Traffic encrypted```

- ✅ Safe for public networks

---

### SOCKS5 (Port 1080) - Use Carefully

- ❌ NO encryption - credentials sent in plaintext## 🔄 Updates and Maintenance

- ❌ All traffic visible

- ⚠️ Only use on trusted networks### Check Service Status

- ⚠️ NOT recommended for public WiFi```bash

sudo systemctl status vpk-dante

### Best Practicesudo systemctl status vpk-squid

- **Production/Public WiFi**: Use port 8443 (HTTPS)sudo systemctl status vpk-stunnel

- **Private networks/Testing**: Use port 1080 (SOCKS5)sudo systemctl status vpk-shadowsocks

```

---

### Restart Services

## 🔍 Troubleshooting```bash

sudo systemctl restart vpk-dante

### Service won't startsudo systemctl restart vpk-squid

```bashsudo systemctl restart vpk-stunnel

# Check logssudo systemctl restart vpk-shadowsocks

sudo journalctl -u vpk-dante -n 50```



# Check if port is in use### View Logs

sudo ss -tlnp | grep :1080```bash

sudo journalctl -u vpk-dante -n 50

# Kill conflicting processsudo journalctl -u vpk-squid -n 50

sudo pkill -9 danted```



# Restart service---

sudo systemctl restart vpk-dante

```## 📊 Service Ports



### Authentication not working| Port | Service | Protocol | Status |

```bash|------|---------|----------|--------|

# Verify user exists (SOCKS5)| 22 | SSH | SSH | ✅ Open |

id socksadmin| 1080 | Dante | SOCKS5 | ✅ Running |

| 3128 | Squid | HTTP | ✅ Running |

# Verify password file (HTTP/HTTPS)| 8443 | Stunnel→Squid | HTTPS+TLS | ✅ Running |

sudo cat /etc/squid/passwords| 11080 | Shadowsocks | SS+ChaCha20 | ✅ Running |



# Check PAM config (SOCKS5)---

cat /etc/pam.d/sockd

```## 🔒 Security Notes



### Can't connect from outside### SOCKS5 (Port 1080)

```bash- ⚠️ **NO ENCRYPTION** - Credentials and traffic sent in plaintext

# Check firewall- ✅ Authentication required

sudo ufw status- 🔴 **DO NOT use on public WiFi or untrusted networks**

- 🟢 Safe for: Private networks, testing, trusted environments

# Open ports if needed

sudo ufw allow 1080/tcp### HTTPS (Port 8443)

sudo ufw allow 3128/tcp- ✅ **FULL TLS ENCRYPTION** - All traffic encrypted

sudo ufw allow 8443/tcp- ✅ Authentication required

sudo ufw allow 11080/tcp- 🟢 Safe for: Production, public WiFi, any network

```- ⭐ **Recommended for all serious use**



---### Best Practice

**If you need encryption → Use Port 8443 (HTTPS)**  

## 📊 Technical Details**If encryption not needed → Use Port 1080 (SOCKS5)**



### Services---

- **Dante** v1.4.2 - SOCKS5 proxy with PAM authentication

- **Squid** v5.7 - HTTP/HTTPS proxy with htpasswd authentication## 📜 License

- **stunnel** v5.65 - TLS wrapper for Squid

- **shadowsocks-libev** v3.3.5 - Encrypted SOCKS5-like proxyMIT License - See [LICENSE](LICENSE) file



### Authentication---

- **SOCKS5**: PAM (system users)

- **HTTP/HTTPS**: htpasswd (Apache-style)## 🎉 Quick Start Summary

- **Shadowsocks**: Password-based

**Want encrypted proxy for MoreLogin?**

### Encryption```

- **HTTPS**: TLS 1.2+ with self-signed certificateUse: darkanon.store:8443:admin:SecurePass123!

- **Shadowsocks**: ChaCha20-IETF-Poly1305Protocol: HTTPS

```

---

**Want fast SOCKS5 for testing?**

## 📜 License```

Use: darkanon.store:1080:socksadmin:SecurePass123!

MIT LicenseProtocol: SOCKS5

```

---

**Both options:**

## 🎯 Summary- ✅ Authentication required

- ✅ Work in MoreLogin

**For most users: Use port 8443 (HTTPS)**- ✅ Already configured and tested

```- ✅ Auto-start on boot

darkanon.store:8443:admin:SecurePass123!

```**Choose 8443 for security, 1080 for speed!**

- Encrypted

- Authenticated---

- Secure for any network

**Last Updated:** October 13, 2025  

**For speed/testing: Use port 1080 (SOCKS5)****Status:** All services operational ✅

```
darkanon.store:1080:socksadmin:SecurePass123!
```
- Fast
- Authenticated
- No encryption (trusted networks only)

---

**Status:** All services operational ✅  
**Last Updated:** October 13, 2025
