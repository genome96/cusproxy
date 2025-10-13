# Installation Notes - Ubuntu Server

## Current Status

The installation stopped at the user creation step due to a UID conflict. The `stunnel4` package created a user with UID 998, which conflicts with our `proxyd` user.

## Fix Applied

The bootstrap script has been updated to handle UID conflicts gracefully. It will now:
1. Try to create users with the specified UIDs (999 and 998)
2. If a UID is already taken, automatically use an available UID
3. Update the service configuration with the actual UIDs used

## How to Continue Installation

### Option 1: Pull Latest Changes and Re-run (Recommended)

```bash
# On your Ubuntu server:
cd /home/ubuntu/cusproxy

# Pull the latest fix
git pull origin master

# Re-run the bootstrap script
sudo ./bootstrap.sh --yes
```

### Option 2: Continue from Where It Stopped

The script has already installed the packages, so you can continue manually:

```bash
cd /home/ubuntu/cusproxy

# Check which users exist
id stunnel4  # This is using UID 998
id proxyadmin 2>/dev/null || echo "Does not exist"
id proxyd 2>/dev/null || echo "Does not exist"

# Create the users with different UIDs
sudo useradd --system --home-dir /opt/vps-proxy-kit --shell /bin/bash proxyadmin
sudo useradd --system --no-create-home --shell /usr/sbin/nologin proxyd

# Continue with the rest of the installation
sudo ./bootstrap.sh --yes
# (It will skip the package installation and continue)
```

### Option 3: Clean Reinstall

```bash
# Remove the partial installation
cd /home/ubuntu
sudo rm -rf cusproxy

# Clone fresh
git clone https://github.com/genome96/cusproxy.git
cd cusproxy

# Run the bootstrap (it will now handle UID conflicts)
sudo ./bootstrap.sh --yes
```

## What Happened

1. ✅ Package installation completed successfully:
   - dante-server (SOCKS5)
   - squid (HTTP/HTTPS proxy)
   - stunnel4 (TLS wrapper)
   - prometheus-node-exporter
   - fail2ban
   - vnstat
   - Python 3.10 development tools
   - All build dependencies

2. ❌ User creation failed:
   - `stunnel4` package created its own user with UID 998
   - Our script tried to create `proxyadmin` with UID 999 (should succeed)
   - Our script tried to create `proxyd` with UID 998 (conflict!)

3. ✅ Fix applied:
   - Script now detects UID conflicts
   - Automatically uses next available UID
   - Continues installation without errors

## Verification After Installation

Once the installation completes, verify:

```bash
# Check users were created
id proxyadmin
id proxyd

# Check services are installed
systemctl status danted
systemctl status squid
systemctl status stunnel4
systemctl status prometheus-node-exporter

# Check Python virtual environment
ls -la /opt/vps-proxy-kit/venv/

# Verify VPK CLI is installed
which vpk
vpk --version
```

## Next Steps After Installation

1. **Initialize the database**:
   ```bash
   sudo vpk init-db
   ```

2. **Create your first user**:
   ```bash
   sudo vpk create-user \
     --username testuser \
     --password "SecurePass123!" \
     --protocol socks,https \
     --quota 100GB
   ```

3. **Check proxy status**:
   ```bash
   sudo vpk status
   ```

4. **Test the SOCKS5 proxy**:
   ```bash
   # From another machine
   curl -x socks5://testuser:SecurePass123!@YOUR_VPS_IP:1080 https://ifconfig.me
   ```

5. **Test the HTTP proxy**:
   ```bash
   curl -x http://testuser:SecurePass123!@YOUR_VPS_IP:3128 https://ifconfig.me
   ```

## Troubleshooting

### If bootstrap.sh fails again

Check the logs:
```bash
journalctl -xe | tail -50
```

### If services don't start

```bash
# Check individual service status
sudo systemctl status danted
sudo systemctl status squid
sudo systemctl status stunnel4

# Check service logs
sudo journalctl -u danted -n 50
sudo journalctl -u squid -n 50
```

### If VPK commands don't work

```bash
# Activate the virtual environment manually
source /opt/vps-proxy-kit/venv/bin/activate

# Try the command
vpk --version
```

## Current System Info

- **Server**: Ubuntu 22.04 LTS
- **Location**: AWS (ip-172-26-0-193)
- **Packages Installed**: All required packages installed successfully
- **Next Step**: Pull latest changes and re-run bootstrap.sh

---

**Last Updated**: 2025-10-13  
**Status**: Installation paused at user creation - fix available in latest commit
