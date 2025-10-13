# Cloudflare SSL/TLS Setup Guide

This guide explains how to configure Cloudflare DNS and SSL/TLS settings for use with VPS Proxy Kit.

## Prerequisites

- A domain registered and added to Cloudflare
- Your VPS public IP address
- Access to Cloudflare dashboard

## Step 1: Configure DNS Record

### 1.1 Log in to Cloudflare
Go to https://dash.cloudflare.com and select your domain.

### 1.2 Add DNS A Record

1. Click on **DNS** in the left sidebar
2. Click **Add record**
3. Configure the record:
   - **Type**: A
   - **Name**: `proxy` (or any subdomain you prefer, e.g., `vpn`, `socks`, etc.)
   - **IPv4 address**: Your VPS IP (e.g., `34.214.132.38`)
   - **Proxy status**: ⚠️ **DNS only (gray cloud)** ⚠️
   - **TTL**: Auto

4. Click **Save**

### ⚠️ CRITICAL: Proxy Status Must Be "DNS Only"

**The proxy status MUST be set to "DNS only" (gray cloud icon).**

- ✅ **DNS only (gray cloud)**: Direct connection to your VPS - Required for Let's Encrypt
- ❌ **Proxied (orange cloud)**: Traffic routes through Cloudflare - Will break Let's Encrypt validation

**Why?** Let's Encrypt needs to connect directly to your server on port 80 to verify domain ownership. If Cloudflare proxy is enabled (orange cloud), Let's Encrypt will connect to Cloudflare's servers instead of yours, causing validation to fail.

### 1.3 Wait for DNS Propagation

DNS changes typically propagate within 1-5 minutes, but can take up to 24 hours in rare cases.

**Verify DNS propagation:**
```bash
# From your local machine
nslookup proxy.yourdomain.com

# Or use online tools:
# - https://dnschecker.org
# - https://www.whatsmydns.net
```

You should see your VPS IP address in the results.

## Step 2: Configure SSL/TLS Settings

### 2.1 Set SSL/TLS Encryption Mode

1. In Cloudflare dashboard, click on **SSL/TLS** in the left sidebar
2. Under **Overview**, set encryption mode to:
   - **Full** or **Full (strict)** if you want to enable Cloudflare proxy later (orange cloud)
   - **Off** or **Flexible** if you'll keep DNS only (gray cloud)

For this proxy setup with **DNS only**, the SSL/TLS mode doesn't matter since traffic goes directly to your server.

### 2.2 Edge Certificates (Optional)

If you plan to enable Cloudflare proxy (orange cloud) in the future:

1. Go to **SSL/TLS** → **Edge Certificates**
2. Enable:
   - ✅ Always Use HTTPS
   - ✅ Automatic HTTPS Rewrites
   - ✅ Minimum TLS Version: TLS 1.2 or higher

**Note:** Only enable these after Let's Encrypt certificate is installed and working.

## Step 3: Install VPS Proxy Kit with SSL

### 3.1 Clone the Repository
```bash
git clone https://github.com/genome96/cusproxy.git
cd cusproxy
```

### 3.2 Run Bootstrap with Domain
```bash
sudo ./bootstrap.sh --domain proxy.yourdomain.com
```

The installer will:
1. Prompt you for domain confirmation
2. Verify DNS is configured
3. Automatically obtain Let's Encrypt certificate
4. Configure all proxy services with valid SSL
5. Set up automatic certificate renewal

### 3.3 Without Domain Prompt (Automated)
```bash
sudo ./bootstrap.sh --yes --domain proxy.yourdomain.com
```

## Step 4: Verify Installation

### 4.1 Check Certificate
```bash
# Check certificate details
openssl x509 -in /etc/vpk/certs/server.crt -text -noout | grep -A2 "Subject:"

# Should show your domain name
```

### 4.2 Test HTTPS Connection
```bash
# From another machine
curl -v https://proxy.yourdomain.com:8443

# Should show valid SSL certificate (no warnings)
```

### 4.3 Check Auto-Renewal
```bash
# View acme.sh cron job
crontab -l | grep acme

# Should show:
# 0 0 * * * "/root/.acme.sh"/acme.sh --cron --home "/root/.acme.sh" > /dev/null
```

## Step 5: Post-Installation (Optional)

### 5.1 Enable Cloudflare Proxy (Orange Cloud)

After verifying everything works, you can optionally enable Cloudflare proxy:

1. Go to Cloudflare **DNS** settings
2. Click on your A record
3. Toggle proxy status to **Proxied (orange cloud)**
4. Click **Save**

**Benefits:**
- DDoS protection
- Hide your real IP address
- CDN caching (not useful for proxy, but included)
- Web Application Firewall (WAF)

**Considerations:**
- Cloudflare will see all your proxy traffic
- May impact proxy performance
- Some IP-based services may break
- Certificate renewal will still work (acme.sh uses DNS challenge as fallback)

### 5.2 Cloudflare Firewall Rules (Recommended)

If you enable orange cloud, add firewall rules:

1. Go to **Security** → **WAF**
2. Create rule to allow your proxy ports:
   - Expression: `(http.request.uri.path contains "/proxy")`
   - Action: Allow

### 5.3 Cloudflare SSL/TLS Settings with Orange Cloud

1. **SSL/TLS mode**: Set to **Full (strict)**
2. **Minimum TLS Version**: 1.2 or higher
3. **TLS 1.3**: Enabled
4. **Automatic HTTPS Rewrites**: Enabled
5. **Always Use HTTPS**: Enabled

## Troubleshooting

### Issue: Let's Encrypt validation fails

**Error:** `Challenge failed for domain proxy.yourdomain.com`

**Solutions:**
1. Verify DNS is propagated: `nslookup proxy.yourdomain.com`
2. Ensure proxy status is **DNS only (gray cloud)**
3. Check firewall allows port 80: `sudo ufw status | grep 80`
4. Verify no other service uses port 80: `sudo netstat -tlnp | grep :80`

### Issue: Certificate not renewing

**Check renewal:**
```bash
/root/.acme.sh/acme.sh --list
/root/.acme.sh/acme.sh --renew -d proxy.yourdomain.com --force
```

**Common causes:**
- Cloudflare proxy enabled (orange cloud) - Use DNS challenge instead
- Firewall blocking port 80
- DNS record changed or deleted

**Fix: Use DNS challenge for renewal**
```bash
# Get Cloudflare API token (dashboard → My Profile → API Tokens)
export CF_Token="your_cloudflare_api_token"
export CF_Account_ID="your_account_id"

# Re-issue with DNS challenge
/root/.acme.sh/acme.sh --issue -d proxy.yourdomain.com --dns dns_cf
```

### Issue: Browser shows "Invalid Certificate"

**Causes:**
- Certificate not installed correctly
- Using wrong port (8443 for TLS, 3128 for plain HTTP)
- Certificate expired

**Check:**
```bash
# View certificate
openssl s_client -connect proxy.yourdomain.com:8443 -servername proxy.yourdomain.com

# Check expiration
openssl x509 -in /etc/vpk/certs/server.crt -noout -dates
```

## Security Best Practices

1. **Keep DNS only (gray cloud)** for proxy services
   - Cloudflare proxy (orange cloud) can break proxy functionality
   - Direct connection provides better performance

2. **Restrict access by IP** if possible
   ```bash
   # Example: Allow only your home IP
   sudo ufw allow from YOUR_HOME_IP to any port 1080,3128,8443,11080
   ```

3. **Monitor certificate expiration**
   ```bash
   # Add to crontab
   0 0 * * * openssl x509 -in /etc/vpk/certs/server.crt -noout -checkend 604800 || echo "Certificate expires in 7 days" | mail -s "SSL Alert" admin@yourdomain.com
   ```

4. **Use strong authentication**
   ```bash
   sudo vpk create-user --username admin --password 'ComplexP@ssw0rd!123' --protocol all --quota 1TB
   ```

## Quick Reference

### DNS Configuration
- **Type**: A
- **Name**: proxy (or your subdomain)
- **IPv4**: Your VPS IP
- **Proxy**: 🌐 DNS only (gray cloud) ⚠️
- **TTL**: Auto

### Install Command
```bash
sudo ./bootstrap.sh --domain proxy.yourdomain.com
```

### Certificate Location
- Certificate: `/etc/vpk/certs/server.crt`
- Private key: `/etc/vpk/certs/server.key`

### Renewal
- Automatic via cron (every 60 days)
- Manual: `/root/.acme.sh/acme.sh --renew -d proxy.yourdomain.com --force`

### Ports
- **1080**: SOCKS5 (plain)
- **3128**: HTTP/HTTPS proxy (plain)
- **8443**: HTTPS proxy with TLS
- **11080**: SOCKS5 with TLS

---

**Need help?** Create an issue at https://github.com/genome96/cusproxy/issues
