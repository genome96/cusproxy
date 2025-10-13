# 🔐 SSH TUNNEL SETUP GUIDE (SOCKS5 + Encryption)

**Date:** October 13, 2025  
**Server:** darkanon.store  
**Method:** Dynamic Port Forwarding (SSH -D flag)

---

## ✅ WHAT YOU'LL GET

**SSH Tunnel creates:**
- ✅ SOCKS5 proxy on your LOCAL computer
- ✅ Full SSH encryption (military-grade)
- ✅ SSH key authentication
- ✅ All traffic encrypted end-to-end
- ✅ No additional server configuration needed

**Connection Flow:**
```
MoreLogin → localhost:1080 (SOCKS5) 
          → [SSH encrypted tunnel] 
          → darkanon.store 
          → Internet
```

---

## 🚀 SETUP INSTRUCTIONS

### Step 1: Create SSH Tunnel (Windows PowerShell)

Open PowerShell and run:

```powershell
ssh -i C:\Users\Anon\Documents\GitHub\cusproxy\oregon.pem -D 1080 -N ubuntu@darkanon.store
```

**Explanation of flags:**
- `-i oregon.pem` = Use your SSH key file
- `-D 1080` = Create SOCKS5 proxy on LOCAL port 1080
- `-N` = Don't execute remote commands (just tunnel)
- `ubuntu@darkanon.store` = Your server

**What happens:**
- Creates SOCKS5 proxy at `localhost:1080` (on YOUR computer)
- All traffic through this proxy is encrypted via SSH
- Terminal stays open (keep it running)

---

### Step 2: Configure MoreLogin

**Important:** You connect to **LOCALHOST**, not darkanon.store!

```
Protocol:  SOCKS5
Host:      localhost  (or 127.0.0.1)
Port:      1080
Username:  [leave empty]
Password:  [leave empty]
```

**Why localhost?**
- SSH creates the proxy on YOUR computer (localhost:1080)
- MoreLogin connects to your local proxy
- The local proxy encrypts and forwards via SSH

---

## ⚠️ IMPORTANT LIMITATIONS

### 1. Terminal Must Stay Open
```
✅ Terminal running = Tunnel active = MoreLogin works
❌ Terminal closed = Tunnel stops = MoreLogin fails
```

You must keep the PowerShell window with SSH running!

### 2. One Connection at a Time
- Can't run multiple SSH tunnels on same port
- Each tunnel occupies port 1080

### 3. MoreLogin Configuration Challenge
```
MoreLogin expects: server:port:user:pass
SSH tunnel gives:  localhost:1080:[no-auth]
```

**Potential issue:** Some proxy managers expect remote servers, not localhost.

---

## 🎯 STEP-BY-STEP TEST

### 1. Start SSH Tunnel

Open PowerShell:
```powershell
cd C:\Users\Anon\Documents\GitHub\cusproxy
ssh -i oregon.pem -D 1080 -N ubuntu@darkanon.store
```

**Expected output:** (cursor just waits, no output = working!)

### 2. Keep Terminal Open

⚠️ **DO NOT CLOSE THIS WINDOW!**  
Minimize it, but keep it running.

### 3. Test the Tunnel

Open a NEW PowerShell window and run:
```powershell
python test_socks5.py
```

Modify the test script to test `localhost:1080`.

### 4. Configure MoreLogin

In MoreLogin proxy settings:
```
Type: SOCKS5
Address: 127.0.0.1
Port: 1080
Authentication: None
```

---

## 🔧 ALTERNATIVE: Background Tunnel

To run SSH tunnel in background (without keeping terminal open):

### Windows (using PuTTY)

1. **Download PuTTY:** https://www.putty.org/
2. **Configure:**
   - Host: darkanon.store
   - Port: 22
   - Connection → SSH → Auth → Private key: oregon.ppk (convert .pem to .ppk)
   - Connection → SSH → Tunnels:
     - Source port: 1080
     - Destination: Dynamic
     - Click "Add"
3. **Save session** (name it "darkanon-tunnel")
4. **Connect** (runs in background)

### Windows (using nssm - service)

Install SSH tunnel as Windows service:
```powershell
# Download nssm: https://nssm.cc/download
nssm install SSHTunnel "C:\Windows\System32\OpenSSH\ssh.exe" "-i C:\Users\Anon\Documents\GitHub\cusproxy\oregon.pem -D 1080 -N ubuntu@darkanon.store"
nssm start SSHTunnel
```

Now tunnel runs automatically, even after reboot!

---

## 🧪 TESTING SCRIPT

Let me create a test script for localhost SSH tunnel:

### test_ssh_tunnel.py
```python
#!/usr/bin/env python3
"""Test SSH SOCKS5 tunnel on localhost"""
import requests

def test_ssh_tunnel():
    """Test local SOCKS5 proxy created by SSH tunnel"""
    try:
        print("\n" + "="*60)
        print("TESTING SSH TUNNEL (localhost:1080)")
        print("="*60 + "\n")
        
        # Test connection through localhost SOCKS5
        proxies = {
            'http': 'socks5://localhost:1080',
            'https': 'socks5://localhost:1080'
        }
        
        print("Connecting through SSH tunnel...")
        response = requests.get('http://ifconfig.me/ip', proxies=proxies, timeout=10)
        
        if response.status_code == 200:
            print(f"✅ SUCCESS! Your IP through SSH tunnel: {response.text.strip()}")
            print(f"   (Should be: 34.214.132.38)")
            return True
        else:
            print(f"❌ FAILED! Status code: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        print("\n⚠️  Is SSH tunnel running?")
        print("   Run: ssh -i oregon.pem -D 1080 -N ubuntu@darkanon.store")
        return False

if __name__ == "__main__":
    test_ssh_tunnel()
```

---

## 📊 COMPARISON: SSH Tunnel vs Server-Side SOCKS5

| Feature | SSH Tunnel | Server SOCKS5 (Port 1080) |
|---------|------------|--------------------------|
| **Encryption** | ✅ SSH (very strong) | ❌ None (plaintext) |
| **Auth** | ✅ SSH key | ✅ Username/password |
| **Proxy Location** | 🖥️ localhost (your PC) | 🌐 darkanon.store (server) |
| **MoreLogin Setup** | `localhost:1080` | `darkanon.store:1080:user:pass` |
| **Terminal Open** | ⚠️ Must stay open | ✅ Not needed |
| **Complexity** | Easy (one command) | Easy (already setup) |
| **Auto-start** | ❌ Manual (unless service) | ✅ Systemd (auto) |

---

## 💡 RECOMMENDATION

### For MoreLogin, you have 3 good options:

### Option 1: Server-Side SOCKS5 (Current Setup) ⭐ SIMPLEST
```
darkanon.store:1080:socksadmin:SecurePass123!

✅ Works directly in MoreLogin
✅ Always available (server-side)
✅ No local setup needed
❌ No encryption
```

### Option 2: SSH Tunnel (This Guide) ⭐ MOST SECURE
```
localhost:1080 (SSH tunnel must be running)

✅ Full encryption (SSH)
✅ Very secure
❌ Must keep terminal/service running
⚠️ MoreLogin might not like "localhost"
```

### Option 3: HTTPS Proxy (Already Working) ⭐ BEST BALANCE
```
darkanon.store:8443:admin:SecurePass123!

✅ Works directly in MoreLogin
✅ Always available (server-side)
✅ Full TLS encryption
✅ Already tested and working
```

---

## 🎯 MY HONEST RECOMMENDATION

**For MoreLogin specifically:**

1. **Best for security + ease:** Use **Port 8443 (HTTPS)**
   - Server-side (always available)
   - Encrypted (TLS)
   - MoreLogin native support
   - No local setup needed

2. **Best for testing:** Use **Port 1080 (SOCKS5)**
   - Server-side (always available)
   - No encryption (but authenticated)
   - MoreLogin native support

3. **Best for security experts:** Use **SSH Tunnel**
   - Maximum encryption
   - But requires local setup
   - MoreLogin may have issues with "localhost" proxy

---

## ❓ WANT TO TRY SSH TUNNEL ANYWAY?

I can help you:
1. ✅ Set up the SSH tunnel
2. ✅ Test if it works
3. ✅ Create test script for localhost:1080
4. ✅ See if MoreLogin accepts localhost as proxy
5. ✅ Set up as Windows service (optional)

Just let me know if you want to proceed with SSH tunnel setup!

---

**Bottom Line:** SSH tunnel is excellent for security, but Port 8443 (HTTPS) gives you similar encryption with easier setup for MoreLogin.
