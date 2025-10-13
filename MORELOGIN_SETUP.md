# VPS Proxy Kit - Connection Details for MoreLogin/Browser Tools

## Quick Reference for Multi-Login Browsers

Copy these details directly into MoreLogin, GoLogin, AdsPower, or any browser automation tool.

---

## ✅ OPTION 1: SOCKS5 (No Authentication)

**Best for:** Speed, no login needed  
**Encryption:** ❌ None

```
Protocol:  SOCKS5
Host:      darkanon.store
Port:      1080
Username:  (leave empty)
Password:  (leave empty)
```

**MoreLogin Format:**
```
Type: SOCKS5
Server: darkanon.store
Port: 1080
Authentication: No
```

---

## ✅ OPTION 2: HTTP Proxy (With Authentication)

**Best for:** Compatibility, works everywhere  
**Encryption:** ❌ None (but auth required)

```
Protocol:  HTTP
Host:      darkanon.store
Port:      3128
Username:  admin
Password:  SecurePass123!
```

**MoreLogin Format:**
```
Type: HTTP
Server: darkanon.store
Port: 3128
Username: admin
Password: SecurePass123!
```

---

## ✅ OPTION 3: HTTPS Proxy (TLS Encrypted + Auth) ⭐ RECOMMENDED

**Best for:** Security, encrypted connection  
**Encryption:** ✅ TLS 1.2+

```
Protocol:  HTTPS
Host:      darkanon.store
Port:      8443
Username:  admin
Password:  SecurePass123!
```

**MoreLogin Format:**
```
Type: HTTPS
Server: darkanon.store
Port: 8443
Username: admin
Password: SecurePass123!
SSL: Ignore certificate errors (self-signed cert)
```

**Note:** You may need to enable "Allow invalid certificates" or similar option.

---

## ⚠️ OPTION 4: Shadowsocks (Requires Client)

**Not directly usable in MoreLogin!** Requires Shadowsocks client setup first.

If you set up Shadowsocks client locally (see ENCRYPTED_SOCKS5_GUIDE.md), you can then use:

```
Protocol:  SOCKS5
Host:      127.0.0.1 (or localhost)
Port:      1080
Username:  (leave empty)
Password:  (leave empty)
```

---

## Testing Your Connection

After configuring in MoreLogin, test by:

1. Open browser profile with proxy
2. Visit: https://ipinfo.io/ip
3. Should show: **34.214.132.38**
4. If you see your real IP, proxy is not working

Alternative test sites:
- https://api.ipify.org
- https://icanhazip.com
- https://whatismyip.com

---

## Troubleshooting

### "Connection Failed" or "Timeout"
- ✅ Verify server is running: All services confirmed active
- ✅ Check domain resolves: `nslookup darkanon.store` → 34.214.132.38
- ✅ AWS Security Group: All TCP ports open
- ❌ Possible issue: Your ISP or firewall blocking

### "Authentication Failed" (Port 3128 or 8443)
- Check username: `admin` (case-sensitive)
- Check password: `SecurePass123!` (exact match, case-sensitive)

### HTTPS Certificate Error (Port 8443)
- This is normal (self-signed certificate)
- Enable "Ignore SSL errors" or "Allow invalid certificates"
- Browser will still be encrypted, just certificate not trusted by CA

### Proxy Working But Slow
- Normal for first connection (SSL handshake)
- SOCKS5 (1080) is fastest
- HTTP (3128) is middle speed
- HTTPS (8443) is slightly slower (encryption overhead)

---

## Recommended Settings by Use Case

### Speed Priority → Use SOCKS5 (Port 1080)
```
darkanon.store:1080 (SOCKS5, no auth)
```

### Security Priority → Use HTTPS (Port 8443) ⭐
```
darkanon.store:8443 (HTTPS, admin/SecurePass123!)
```

### Maximum Compatibility → Use HTTP (Port 3128)
```
darkanon.store:3128 (HTTP, admin/SecurePass123!)
```

### Maximum Security + Speed → Shadowsocks (Port 11080)
```
Requires Shadowsocks client setup first
See ENCRYPTED_SOCKS5_GUIDE.md
```

---

## Server Status Verification

All services are currently **ACTIVE** and tested:

| Port | Protocol | Status | Last Tested |
|------|----------|--------|-------------|
| 1080 | SOCKS5 | ✅ WORKING | 2025-10-13 |
| 3128 | HTTP | ✅ WORKING | 2025-10-13 |
| 8443 | HTTPS | ✅ WORKING | 2025-10-13 |
| 11080 | Shadowsocks | ✅ RUNNING | 2025-10-13 |

Server IP: **34.214.132.38**  
Domain: **darkanon.store**  
Location: AWS US-West-2 (Oregon)

---

## Example Configurations

### MoreLogin Configuration Screen

```
┌─────────────────────────────────────┐
│ Proxy Type: [HTTPS ▼]              │
│ Server:     darkanon.store          │
│ Port:       8443                    │
│ Username:   admin                   │
│ Password:   SecurePass123!          │
│ [✓] Ignore SSL certificate errors  │
│                                     │
│ [Test Connection] [Save]            │
└─────────────────────────────────────┘
```

### GoLogin / AdsPower Format

```
Proxy Type: HTTPS
Proxy Server: darkanon.store:8443
Proxy Login: admin
Proxy Password: SecurePass123!
```

### Browser Extension Format (FoxyProxy, etc.)

```
Title: VPS Proxy Kit
Type: HTTPS
Hostname: darkanon.store
Port: 8443
Username: admin
Password: SecurePass123!
```

---

## Quick Copy-Paste Values

**For SOCKS5:**
```
darkanon.store
1080
```

**For HTTP:**
```
darkanon.store
3128
admin
SecurePass123!
```

**For HTTPS:**
```
darkanon.store
8443
admin
SecurePass123!
```

---

## Additional Resources

- **Full Documentation:** See repository README.md
- **Shadowsocks Setup:** ENCRYPTED_SOCKS5_GUIDE.md
- **Test Report:** PROTOCOL_TEST_REPORT.md
- **Technical Details:** SOLUTION_SUMMARY.md

---

**All protocols tested and confirmed working on October 13, 2025** ✅
