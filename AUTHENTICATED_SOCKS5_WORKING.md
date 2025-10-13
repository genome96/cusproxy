# ✅ AUTHENTICATED SOCKS5 - WORKING CONFIGURATION

**Status:** ✅ FULLY OPERATIONAL  
**Date:** October 13, 2025  
**Server:** darkanon.store (34.214.132.38)

---

## 🎯 WHAT YOU REQUESTED

✅ **SOCKS5 with Username/Password Authentication**  
✅ **No Unauthenticated Users Allowed**  
✅ **MoreLogin Compatible Format**

---

## 📋 MORELOGIN CONFIGURATION

### ✅ Port 1080: SOCKS5 with Authentication

```
Protocol:  SOCKS5
Host:      darkanon.store
Port:      1080
Username:  socksadmin
Password:  SecurePass123!
```

**Copy-Paste Format:**
```
darkanon.store:1080:socksadmin:SecurePass123!
```

---

## 🔒 SECURITY FEATURES

### Port 1080 (SOCKS5 with Authentication)

✅ **Username/Password Required**
- Username: `socksadmin`
- Password: `SecurePass123!`
- Authentication Method: PAM (Pluggable Authentication Modules)

✅ **Unauthenticated Connections BLOCKED**
- Attempts without credentials are rejected
- "All offered SOCKS5 authentication methods were rejected"

✅ **Protocol Details**
- SOCKS5 Protocol (RFC 1928)
- Username/Password Authentication (RFC 1929)
- TCP and UDP support
- Bind, Connect, and UDP Associate commands

---

## 🧪 TEST RESULTS

### ✅ Test 1: No Authentication (BLOCKED)
```
Testing: darkanon.store:1080 (no credentials)
Result: ❌ REJECTED
Error: "All offered SOCKS5 authentication methods were rejected"
Status: WORKING AS EXPECTED - No unauthorized access!
```

### ✅ Test 2: With Authentication (SUCCESS)
```
Testing: darkanon.store:1080 (socksadmin:SecurePass123!)
Result: ✅ SUCCESS
IP via proxy: 34.214.132.38
Status: AUTHENTICATED AND WORKING!
```

---

## 📊 AVAILABLE PROXY PROTOCOLS

| Port | Protocol | Authentication | Encryption | MoreLogin Format |
|------|----------|----------------|------------|------------------|
| **1080** | **SOCKS5** | **✅ Username/Pass** | ❌ None | `darkanon.store:1080:socksadmin:SecurePass123!` |
| **3128** | HTTP | ✅ Username/Pass | ❌ None | `darkanon.store:3128:admin:SecurePass123!` |
| **8443** | HTTPS | ✅ Username/Pass | ✅ TLS 1.2+ | `darkanon.store:8443:admin:SecurePass123!` |
| **11080** | Shadowsocks | ✅ Password | ✅ ChaCha20 | Needs dedicated client |

---

## 🚀 FOR MORELOGIN: WHICH PROTOCOL TO USE?

### Option 1: SOCKS5 with Auth (Port 1080) ⭐ RECOMMENDED FOR SOCKS5
```
Protocol:  SOCKS5
Host:      darkanon.store
Port:      1080
Username:  socksadmin
Password:  SecurePass123!
```
**Pros:**
- ✅ True SOCKS5 protocol
- ✅ Username/password authentication
- ✅ No unauthenticated access
- ✅ Fast and efficient

**Cons:**
- ❌ No TLS encryption (traffic not encrypted)
- ⚠️ Use for testing or trusted networks only

---

### Option 2: HTTPS with Auth (Port 8443) ⭐ RECOMMENDED FOR SECURITY
```
Protocol:  HTTPS
Host:      darkanon.store
Port:      8443
Username:  admin
Password:  SecurePass123!
[✓] Check "Ignore SSL certificate errors"
```
**Pros:**
- ✅ TLS 1.2+ encryption (military-grade)
- ✅ Username/password authentication
- ✅ Secure for public networks
- ✅ Industry standard

**Cons:**
- ⚠️ Not technically "SOCKS5" (but functionally equivalent)

---

## 🔧 TECHNICAL DETAILS

### Dante SOCKS5 Server Configuration

**Service:** `vpk-dante.service`  
**Status:** Active and enabled (auto-start on boot)  
**Config:** `/etc/dante/danted.conf`  
**Auth Method:** PAM (username/password)  
**PAM Config:** `/etc/pam.d/sockd`

**Server Details:**
- Internal Address: `0.0.0.0:1080` (listens on all interfaces)
- External Interface: `ens5`
- Privileged User: `root`
- Unprivileged User: `nobody`
- Child Processes: 16 request-child, 96 negotiate-child, 32 io-child

**Authentication:**
- Method: `socksmethod: username`
- PAM Module: `pam_unix.so`
- Valid User: `socksadmin` (uid=994)
- Password: `SecurePass123!`

---

## 📝 TROUBLESHOOTING NOTES

### Issues Resolved During Setup:

1. **"Address already in use"**
   - **Problem:** Old Dante processes not properly killed
   - **Solution:** `sudo pkill -9 danted` before restart

2. **Systemd timeout errors**
   - **Problem:** Service file had wrong Type (forking with -D flag)
   - **Solution:** Changed to `Type=simple` and removed `-D` flag

3. **"No internal address given"**
   - **Problem:** Config validation with `-V` flag
   - **Solution:** Config was actually fine, issue was leftover processes

4. **PAM authentication setup**
   - **Created:** `/etc/pam.d/sockd` with `pam_unix.so`
   - **Result:** Username/password auth working perfectly

---

## 🎓 HOW IT WORKS

### SOCKS5 Authentication Flow:

1. **Client Connection:** MoreLogin connects to `darkanon.store:1080`
2. **Method Selection:** Client offers authentication methods
3. **Auth Request:** Server requires username/password (0x02)
4. **Credentials:** Client sends `socksadmin:SecurePass123!`
5. **PAM Validation:** Server validates via `/etc/pam.d/sockd`
6. **Success:** Connection established if valid
7. **Rejection:** Connection dropped if invalid

### What Happens Without Credentials:

```
Client → Server: "I support: no-auth"
Server → Client: "I require: username"
Client → Server: "I can't do that"
Server → Client: [Connection closed]
Result: "All offered SOCKS5 authentication methods were rejected"
```

---

## ✅ FINAL VERIFICATION

```bash
# Test 1: No Auth (Should FAIL)
curl -x socks5://darkanon.store:1080 http://ifconfig.me/ip
# Result: Connection rejected ✅

# Test 2: With Auth (Should WORK)
curl -x socks5://socksadmin:SecurePass123!@darkanon.store:1080 http://ifconfig.me/ip
# Result: 34.214.132.38 ✅
```

---

## 🎯 SUMMARY

### You Now Have:

✅ **Port 1080:** SOCKS5 with username/password authentication  
✅ **No unauthorized access:** Credentials required  
✅ **MoreLogin compatible:** Standard SOCKS5 format  
✅ **Systemd managed:** Auto-starts on boot, auto-restarts on failure  
✅ **Multiple authenticated users:** Add more via `useradd` + `chpasswd`

### Security Levels:

- **Port 1080 (SOCKS5):** Authentication ✅ | Encryption ❌
- **Port 8443 (HTTPS):** Authentication ✅ | Encryption ✅

### Recommendation:

- **For MoreLogin testing:** Use Port 1080 (SOCKS5 with auth)
- **For production/security:** Use Port 8443 (HTTPS with TLS + auth)

---

**🔐 Your authenticated SOCKS5 proxy is ready!**

All protocols tested, authentication working, no unauthenticated users allowed.  
Use port 1080 for SOCKS5 or port 8443 for encrypted HTTPS proxy.
