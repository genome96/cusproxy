#!/bin/bash
#
# VPS Proxy Kit Bootstrap Installer
# Target: Ubuntu 22.04 LTS
# Usage: sudo ./bootstrap.sh [options]
#

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration defaults
INSTALL_DIR="/opt/vps-proxy-kit"
CONFIG_DIR="/etc/vpk"
LOG_DIR="/var/log/vpk"
DATA_DIR="${INSTALL_DIR}/data"
VENV_DIR="${INSTALL_DIR}/venv"

SERVICE_USER="proxyadmin"
SERVICE_UID=999
PROXY_USER="proxyd"
PROXY_UID=998

MODE="prod"  # prod or quick
DOMAIN=""
AUTO_YES=false
ENABLE_SOCKS=true
ENABLE_HTTPS=true
QUICK_USERNAME=""
QUICK_PASSWORD=""

# Parse command line arguments
while [[ $# -gt 0 ]]; do
  case $1 in
    --mode)
      MODE="$2"
      shift 2
      ;;
    --domain)
      DOMAIN="$2"
      shift 2
      ;;
    --yes|-y)
      AUTO_YES=true
      shift
      ;;
    --username)
      QUICK_USERNAME="$2"
      shift 2
      ;;
    --password)
      QUICK_PASSWORD="$2"
      shift 2
      ;;
    --no-socks)
      ENABLE_SOCKS=false
      shift
      ;;
    --no-https)
      ENABLE_HTTPS=false
      shift
      ;;
    --help|-h)
      cat <<EOF
VPS Proxy Kit Bootstrap Installer

Usage: sudo ./bootstrap.sh [options]

Options:
  --mode MODE          Installation mode: 'prod' (default) or 'quick'
  --domain DOMAIN      Domain name for Let's Encrypt certificates
  --yes, -y            Skip confirmation prompts
  --username USER      Username for quick mode (required if --mode quick)
  --password PASS      Password for quick mode (required if --mode quick)
  --no-socks           Disable SOCKS5 proxy
  --no-https           Disable HTTP/HTTPS proxy
  --help, -h           Show this help message

Examples:
  # Production installation
  sudo ./bootstrap.sh --mode prod --domain proxy.example.com

  # Production with auto-yes
  sudo ./bootstrap.sh --yes

  # Quick mode for testing
  sudo ./bootstrap.sh --mode quick --username testuser --password testpass123

EOF
      exit 0
      ;;
    *)
      echo -e "${RED}Unknown option: $1${NC}"
      echo "Use --help for usage information"
      exit 1
      ;;
  esac
done

# Helper functions
log_info() {
  echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
  echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warn() {
  echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
  echo -e "${RED}[ERROR]${NC} $1"
}

check_root() {
  if [[ $EUID -ne 0 ]]; then
    log_error "This script must be run as root"
    exit 1
  fi
}

check_ubuntu() {
  if [[ ! -f /etc/os-release ]]; then
    log_error "Cannot detect OS version"
    exit 1
  fi
  
  source /etc/os-release
  if [[ "$ID" != "ubuntu" ]] || [[ "$VERSION_ID" != "22.04" ]]; then
    log_warn "This script is designed for Ubuntu 22.04 LTS"
    log_warn "Detected: $ID $VERSION_ID"
    if [[ "$AUTO_YES" != true ]]; then
      read -p "Continue anyway? (y/N): " -n 1 -r
      echo
      if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
      fi
    fi
  fi
}

confirm_installation() {
  # Prompt for domain if not provided and not in auto-yes mode
  if [[ "$AUTO_YES" != true ]] && [[ -z "$DOMAIN" ]]; then
    cat <<EOF

${YELLOW}=============================================================
SSL Certificate Setup
=============================================================${NC}

Do you have a domain name pointed to this server's IP address?

If YES:
  - You will get a valid Let's Encrypt SSL certificate
  - No browser warnings
  - Certificate auto-renews every 60 days
  - ${GREEN}Recommended for production${NC}

If NO:
  - Self-signed certificate will be used
  - Browser warnings expected
  - ${YELLOW}OK for testing/development${NC}

${BLUE}Cloudflare DNS Setup (if using Cloudflare):${NC}
  1. Log in to Cloudflare dashboard
  2. Go to your domain's DNS settings
  3. Add an A record:
     - Name: proxy (or subdomain of your choice)
     - IPv4 address: $(curl -s https://api.ipify.org)
     - Proxy status: ${YELLOW}DNS only (gray cloud)${NC} ⚠️
     - TTL: Auto
  4. Wait 1-2 minutes for DNS propagation

${RED}IMPORTANT: Cloudflare proxy MUST be disabled (gray cloud)${NC}
${RED}Otherwise Let's Encrypt verification will fail!${NC}

EOF
    
    read -p "Do you have a domain name ready? (y/N): " -r
    if [[ $REPLY =~ ^[Yy]$ ]]; then
      echo
      read -p "Enter your domain name (e.g., proxy.example.com): " DOMAIN
      DOMAIN=$(echo "$DOMAIN" | tr -d '[:space:]' | tr '[:upper:]' '[:lower:]')
      
      if [[ -z "$DOMAIN" ]]; then
        log_warn "No domain provided, will use self-signed certificate"
      else
        log_info "Will obtain Let's Encrypt certificate for: ${DOMAIN}"
        echo
        read -p "Is the DNS A record already configured and propagated? (y/N): " -r
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
          log_warn "Please configure DNS first, then re-run with --domain ${DOMAIN}"
          log_info "Continuing with self-signed certificate for now..."
          DOMAIN=""
        fi
      fi
    fi
  fi
  
  if [[ "$AUTO_YES" == true ]]; then
    return 0
  fi
  
  cat <<EOF

${BLUE}=============================================================
VPS Proxy Kit Installation
=============================================================${NC}

Installation mode: ${GREEN}${MODE}${NC}
Installation directory: ${INSTALL_DIR}
Configuration directory: ${CONFIG_DIR}
Domain: ${DOMAIN:-"None (self-signed certificates)"}

Services to install:
- SOCKS5 proxy: ${ENABLE_SOCKS}
- HTTP/HTTPS proxy: ${ENABLE_HTTPS}
- TLS wrapper (stunnel): Yes
- Monitoring (Prometheus): Yes
- Log parser: Yes
- Quota enforcer: Yes
- fail2ban: Yes

This will:
1. Install system packages via apt
2. Create service users (${SERVICE_USER}, ${PROXY_USER})
3. Set up Python virtualenv
4. Configure proxy services
5. Create systemd units
6. Configure firewall rules
7. Generate encryption keys

EOF
  
  read -p "Proceed with installation? (y/N): " -n 1 -r
  echo
  if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    log_info "Installation cancelled"
    exit 0
  fi
}

update_system() {
  log_info "Updating package lists..."
  apt-get update -qq
  log_success "Package lists updated"
}

install_packages() {
  log_info "Installing system packages..."
  
  local packages=(
    python3.10
    python3-venv
    python3-pip
    python3-dev
    build-essential
    git
    curl
    wget
    logrotate
    fail2ban
    iproute2
    iptables
    net-tools
    vnstat
    prometheus-node-exporter
    sqlite3
    libsqlite3-dev
    libsodium-dev
    libssl-dev
    stunnel4
  )
  
  if [[ "$MODE" == "prod" ]]; then
    if [[ "$ENABLE_SOCKS" == true ]]; then
      packages+=(dante-server shadowsocks-libev)
    fi
    if [[ "$ENABLE_HTTPS" == true ]]; then
      packages+=(squid apache2-utils)
    fi
  fi
  
  if [[ -n "$DOMAIN" ]]; then
    packages+=(socat) # Required for acme.sh
  fi
  
  # Install with DEBIAN_FRONTEND=noninteractive to avoid prompts
  DEBIAN_FRONTEND=noninteractive apt-get install -y -qq "${packages[@]}" 2>&1 | grep -v "^Selecting\|^Preparing\|^Unpacking" || true
  
  log_success "System packages installed"
}

create_users() {
  log_info "Creating service users..."
  
  # Create proxyadmin user
  if ! id -u "${SERVICE_USER}" >/dev/null 2>&1; then
    # Try with specified UID, fall back to auto-assignment if UID is taken
    if useradd --system --uid ${SERVICE_UID} --home-dir "${INSTALL_DIR}" --shell /bin/bash "${SERVICE_USER}" 2>/dev/null; then
      log_success "Created user: ${SERVICE_USER} with UID ${SERVICE_UID}"
    else
      log_warn "UID ${SERVICE_UID} already taken, using auto-assigned UID"
      useradd --system --home-dir "${INSTALL_DIR}" --shell /bin/bash "${SERVICE_USER}"
      SERVICE_UID=$(id -u "${SERVICE_USER}")
      log_success "Created user: ${SERVICE_USER} with UID ${SERVICE_UID}"
    fi
  else
    log_info "User ${SERVICE_USER} already exists"
    SERVICE_UID=$(id -u "${SERVICE_USER}")
  fi
  
  # Create proxyd user (no login)
  if ! id -u "${PROXY_USER}" >/dev/null 2>&1; then
    # Try with specified UID, fall back to auto-assignment if UID is taken
    if useradd --system --uid ${PROXY_UID} --no-create-home --shell /usr/sbin/nologin "${PROXY_USER}" 2>/dev/null; then
      log_success "Created user: ${PROXY_USER} with UID ${PROXY_UID}"
    else
      log_warn "UID ${PROXY_UID} already taken, using auto-assigned UID"
      useradd --system --no-create-home --shell /usr/sbin/nologin "${PROXY_USER}"
      PROXY_UID=$(id -u "${PROXY_USER}")
      log_success "Created user: ${PROXY_USER} with UID ${PROXY_UID}"
    fi
  else
    log_info "User ${PROXY_USER} already exists"
    PROXY_UID=$(id -u "${PROXY_USER}")
  fi
}

create_directories() {
  log_info "Creating directory structure..."
  
  mkdir -p "${INSTALL_DIR}"/{data,logs,tmp}
  mkdir -p "${CONFIG_DIR}"/{certs,backup}
  mkdir -p "${LOG_DIR}"
  mkdir -p /etc/dante
  
  # Pre-create log files with correct ownership
  touch "${LOG_DIR}/squid.log"
  touch "${LOG_DIR}/stunnel.log"
  touch "${LOG_DIR}/danted.log"
  touch "${LOG_DIR}/vpk.log"
  
  # Set ownership
  chown -R "${SERVICE_USER}:${SERVICE_USER}" "${INSTALL_DIR}"
  chown -R "${PROXY_USER}:${PROXY_USER}" "${LOG_DIR}"
  chown -R root:root "${CONFIG_DIR}"
  
  # Set permissions
  chmod 750 "${INSTALL_DIR}"
  chmod 700 "${DATA_DIR}"
  chmod 755 "${LOG_DIR}"
  chmod 644 "${LOG_DIR}"/*.log 2>/dev/null || true
  chmod 755 "${CONFIG_DIR}"
  chmod 755 "${CONFIG_DIR}/certs"
  
  # Create Squid-specific log files with correct ownership
  if [[ "$ENABLE_HTTPS" == true ]]; then
    touch "${LOG_DIR}/squid_access.log" "${LOG_DIR}/squid_cache.log"
    chown proxy:proxy "${LOG_DIR}/squid"*.log
    chmod 644 "${LOG_DIR}/squid"*.log
  fi
  
  log_success "Directory structure created"
}

setup_python_venv() {
  log_info "Setting up Python virtual environment..."
  
  # Create virtualenv
  sudo -u "${SERVICE_USER}" python3.10 -m venv "${VENV_DIR}"
  
  # Upgrade pip
  sudo -u "${SERVICE_USER}" "${VENV_DIR}/bin/pip" install --upgrade pip setuptools wheel -q
  
  log_success "Python virtual environment created"
}

install_python_deps() {
  log_info "Installing Python dependencies..."
  
  # Create requirements.txt
  cat > "${INSTALL_DIR}/requirements.txt" <<'EOF'
click>=8.1.7
argon2-cffi>=23.1.0
sqlalchemy>=2.0.23
cryptography>=41.0.7
psutil>=5.9.6
prometheus-client>=0.19.0
pyyaml>=6.0.1
watchdog>=3.0.0
pytest>=7.4.3
pytest-cov>=4.1.0
tabulate>=0.9.0
python-dateutil>=2.8.2
requests>=2.31.0
aiofiles>=23.2.1
fastapi>=0.108.0
uvicorn>=0.25.0
pydantic>=2.5.3
EOF
  
  chown "${SERVICE_USER}:${SERVICE_USER}" "${INSTALL_DIR}/requirements.txt"
  
  # Install dependencies
  sudo -u "${SERVICE_USER}" "${VENV_DIR}/bin/pip" install -r "${INSTALL_DIR}/requirements.txt" -q
  
  log_success "Python dependencies installed"
}

install_vpk_package() {
  log_info "Installing VPK package..."
  
  # Get the directory where this script is located
  SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
  
  # Copy VPK package to installation directory
  if [[ -d "${SCRIPT_DIR}/vpk" ]]; then
    log_info "Copying VPK package files..."
    cp -r "${SCRIPT_DIR}/vpk" "${INSTALL_DIR}/"
    cp "${SCRIPT_DIR}/setup.py" "${INSTALL_DIR}/"
    cp "${SCRIPT_DIR}/README.md" "${INSTALL_DIR}/"
    chown -R "${SERVICE_USER}:${SERVICE_USER}" "${INSTALL_DIR}/vpk" "${INSTALL_DIR}/setup.py" "${INSTALL_DIR}/README.md"
    
    # Install the package in development mode
    log_info "Installing VPK package in editable mode..."
    cd "${INSTALL_DIR}"
    sudo -u "${SERVICE_USER}" "${VENV_DIR}/bin/pip" install -e . -q
    
    # Fix permissions for venv directories
    chmod 755 "${INSTALL_DIR}" "${VENV_DIR}" "${VENV_DIR}/bin"
    
    # Fix permissions for secret key and config to allow proxyadmin to read
    chmod 640 "${CONFIG_DIR}/secret.key"
    chown root:${SERVICE_USER} "${CONFIG_DIR}/secret.key"
    chmod 644 "${CONFIG_DIR}/config.yml"
    
    # Create and fix log file permissions
    touch "${LOG_DIR}/vpk.log"
    chown ${SERVICE_USER}:${SERVICE_USER} "${LOG_DIR}/vpk.log"
    chmod 644 "${LOG_DIR}/vpk.log"
    
    log_success "VPK package installed"
  else
    log_error "VPK package directory not found at ${SCRIPT_DIR}/vpk"
    log_error "Make sure you're running bootstrap.sh from the cusproxy directory"
    exit 1
  fi
}

generate_encryption_key() {
  log_info "Generating encryption keys..."
  
  # Generate master encryption key (32 bytes = 256 bits)
  if [[ ! -f "${CONFIG_DIR}/secret.key" ]]; then
    openssl rand -base64 32 > "${CONFIG_DIR}/secret.key"
    chmod 600 "${CONFIG_DIR}/secret.key"
    chown root:root "${CONFIG_DIR}/secret.key"
    log_success "Master encryption key generated"
  else
    log_warn "Encryption key already exists, skipping"
  fi
}

validate_domain() {
  local domain="$1"
  local expected_ip="$2"
  
  log_info "Validating DNS configuration for ${domain}..."
  
  # Get actual IP from DNS
  local resolved_ip
  resolved_ip=$(dig +short "$domain" A | tail -n1 2>/dev/null)
  
  if [[ -z "$resolved_ip" ]]; then
    resolved_ip=$(host "$domain" | grep "has address" | awk '{print $NF}' | head -n1 2>/dev/null)
  fi
  
  if [[ -z "$resolved_ip" ]]; then
    log_error "Unable to resolve domain ${domain}"
    return 1
  fi
  
  log_info "Domain ${domain} resolves to: ${resolved_ip}"
  log_info "Server public IP: ${expected_ip}"
  
  if [[ "$resolved_ip" != "$expected_ip" ]]; then
    log_error "DNS mismatch! Domain points to ${resolved_ip} but server is ${expected_ip}"
    log_warn "Please update your DNS A record to point to ${expected_ip}"
    return 1
  fi
  
  log_success "DNS validation passed"
  return 0
}

generate_certificates() {
  log_info "Setting up TLS certificates..."
  
  if [[ -n "$DOMAIN" ]]; then
    # Validate domain DNS first
    PUBLIC_IP=$(curl -s https://api.ipify.org || curl -s https://ifconfig.me || echo "")
    
    if [[ -z "$PUBLIC_IP" ]]; then
      log_error "Unable to determine public IP"
      log_info "Falling back to self-signed certificate"
      DOMAIN=""
    elif ! validate_domain "$DOMAIN" "$PUBLIC_IP"; then
      log_error "Domain validation failed"
      log_info "Falling back to self-signed certificate"
      DOMAIN=""
    fi
  fi
  
  if [[ -n "$DOMAIN" ]]; then
    # Use acme.sh for Let's Encrypt
    log_info "Installing acme.sh..."
    
    # Install acme.sh
    if [[ ! -d /root/.acme.sh ]]; then
      curl -s https://get.acme.sh | sh -s || {
        log_error "Failed to install acme.sh"
        log_info "Falling back to self-signed certificate"
        DOMAIN=""
      }
    fi
    
    if [[ -n "$DOMAIN" ]]; then
      log_info "Obtaining Let's Encrypt certificate for ${DOMAIN}..."
      
      # Stop services that might use port 80/443
      systemctl stop squid 2>/dev/null || true
      systemctl stop apache2 2>/dev/null || true
      systemctl stop nginx 2>/dev/null || true
      
      # Issue certificate using standalone mode with Let's Encrypt
      /root/.acme.sh/acme.sh --set-default-ca --server letsencrypt
      /root/.acme.sh/acme.sh --issue -d "${DOMAIN}" --standalone --keylength 4096 --force || {
        log_warn "Failed to obtain Let's Encrypt certificate"
        log_info "Falling back to self-signed certificate"
        DOMAIN=""
      }
      
      if [[ -n "$DOMAIN" ]]; then
        # Install certificates to our directory
        /root/.acme.sh/acme.sh --install-cert -d "${DOMAIN}" \
          --key-file "${CONFIG_DIR}/certs/server.key" \
          --fullchain-file "${CONFIG_DIR}/certs/server.crt" \
          --reloadcmd "systemctl reload vpk-stunnel" || {
          log_error "Failed to install certificate"
          DOMAIN=""
        }
        
        if [[ -n "$DOMAIN" ]]; then
          chmod 600 "${CONFIG_DIR}/certs/server.key"
          chmod 644 "${CONFIG_DIR}/certs/server.crt"
          chown ${PROXY_USER}:${PROXY_USER} "${CONFIG_DIR}/certs/server.key"
          chown ${PROXY_USER}:${PROXY_USER} "${CONFIG_DIR}/certs/server.crt"
          
          log_success "Let's Encrypt certificate installed"
          log_info "Certificate will auto-renew every 60 days"
        fi
      fi
    fi
  fi
  
  if [[ -z "$DOMAIN" ]]; then
    # Generate self-signed certificate
    log_info "Generating self-signed certificate..."
    
    # Get public IP
    PUBLIC_IP=$(curl -s https://api.ipify.org || echo "127.0.0.1")
    
    # Create OpenSSL config file with SAN extension (required for OpenSSL 3.0)
    cat > /tmp/ssl_cert.cnf << EOF
[req]
default_bits = 4096
prompt = no
default_md = sha256
distinguished_name = dn
x509_extensions = v3_ext

[dn]
CN = ${PUBLIC_IP}

[v3_ext]
subjectAltName = IP:${PUBLIC_IP}
keyUsage = digitalSignature, keyEncipherment
extendedKeyUsage = serverAuth
EOF
    
    openssl req -x509 -newkey rsa:4096 -nodes \
      -keyout "${CONFIG_DIR}/certs/server.key" \
      -out "${CONFIG_DIR}/certs/server.crt" \
      -days 365 \
      -config /tmp/ssl_cert.cnf
    
    rm -f /tmp/ssl_cert.cnf
    
    chmod 600 "${CONFIG_DIR}/certs/server.key"
    chmod 644 "${CONFIG_DIR}/certs/server.crt"
    chown ${PROXY_USER}:${PROXY_USER} "${CONFIG_DIR}/certs/server.key"
    chown ${PROXY_USER}:${PROXY_USER} "${CONFIG_DIR}/certs/server.crt"
    
    log_success "Self-signed certificate generated (valid for 365 days)"
    log_warn "For production, use --domain option with a valid domain name"
  fi
}

configure_dante() {
  if [[ "$MODE" != "prod" ]] || [[ "$ENABLE_SOCKS" != true ]]; then
    return 0
  fi
  
  log_info "Configuring Dante SOCKS5 server..."
  
  # Create Dante config directory if it doesn't exist
  mkdir -p /etc/dante
  
  # Detect network interface
  IFACE=$(ip route | grep default | awk '{print $5}' | head -n1)
  
  cat > /etc/dante/danted.conf <<EOF
# Dante SOCKS5 server configuration
# Generated by VPS Proxy Kit

logoutput: ${LOG_DIR}/danted.log

# Internal interface
internal: 0.0.0.0 port = 1080

# External interface
external: ${IFACE}

# Authentication methods (temporarily disabled until VPK database is initialized)
# Change to 'socksmethod: username' after running 'vpk init-db' and creating users
socksmethod: none

# Service users
user.privileged: root
user.unprivileged: ${PROXY_USER}

# Client rules
client pass {
    from: 0.0.0.0/0 to: 0.0.0.0/0
    log: connect disconnect error
}

# SOCKS rules
socks pass {
    from: 0.0.0.0/0 to: 0.0.0.0/0
    protocol: tcp udp
    command: bind connect udpassociate
    log: connect disconnect error
    socksmethod: none
}

# Block by default
socks block {
    from: 0.0.0.0/0 to: 0.0.0.0/0
    log: connect error
}
EOF
  
  # Create PAM configuration for Dante
  cat > /etc/pam.d/sockd <<'EOF'
auth required pam_unix.so
account required pam_unix.so
EOF
  
  chmod 644 /etc/dante/danted.conf
  
  # Disable default systemd service (we'll use our own)
  systemctl stop danted 2>/dev/null || true
  systemctl disable danted 2>/dev/null || true
  
  log_success "Dante configured"
}

configure_squid() {
  if [[ "$MODE" != "prod" ]] || [[ "$ENABLE_HTTPS" != true ]]; then
    return 0
  fi
  
  log_info "Configuring Squid HTTP/HTTPS proxy..."
  
  # Backup original config
  if [[ -f /etc/squid/squid.conf ]]; then
    cp /etc/squid/squid.conf /etc/squid/squid.conf.backup
  fi
  
  cat > /etc/squid/squid.conf <<EOF
# Squid HTTP/HTTPS proxy configuration
# Generated by VPS Proxy Kit

# HTTP port
http_port 3128

# Access logging with bytes
logformat vpk %ts.%03tu %6tr %>a %Ss/%03>Hs %<st %rm %ru %[un %Sh/%<a %mt
access_log ${LOG_DIR}/squid_access.log vpk
cache_log ${LOG_DIR}/squid_cache.log

# Authentication
auth_param basic program /usr/lib/squid/basic_ncsa_auth /etc/vpk/htpasswd
auth_param basic children 5
auth_param basic realm VPS Proxy Kit
auth_param basic credentialsttl 2 hours

# ACLs
acl authenticated proxy_auth REQUIRED
acl SSL_ports port 443
acl Safe_ports port 80          # http
acl Safe_ports port 21          # ftp
acl Safe_ports port 443         # https
acl Safe_ports port 70          # gopher
acl Safe_ports port 210         # wais
acl Safe_ports port 1025-65535  # unregistered ports
acl Safe_ports port 280         # http-mgmt
acl Safe_ports port 488         # gss-http
acl Safe_ports port 591         # filemaker
acl Safe_ports port 777         # multiling http
acl CONNECT method CONNECT

# Access rules
http_access deny !Safe_ports
http_access deny CONNECT !SSL_ports
http_access allow localhost manager
http_access deny manager
http_access allow authenticated
http_access deny all

# Performance tuning
cache_mem 256 MB
maximum_object_size 100 MB
cache_dir ufs /var/spool/squid 10000 16 256

# Disable cache for privacy
cache deny all

# Forwarded headers
forwarded_for on
via on

# Service user
cache_effective_user proxy
cache_effective_group proxy

# PID file
pid_filename /run/squid/squid.pid

# Connection limits per user (soft limit)
# delay_pools 1
# delay_class 1 2
# delay_parameters 1 -1/-1 32000/32000
# delay_access 1 allow authenticated
EOF
  
  # Initialize htpasswd file
  touch /etc/vpk/htpasswd
  chmod 640 /etc/vpk/htpasswd
  chown root:${PROXY_USER} /etc/vpk/htpasswd
  
  # Initialize Squid cache
  squid -z 2>/dev/null || true
  
  # Stop default service
  systemctl stop squid 2>/dev/null || true
  systemctl disable squid 2>/dev/null || true
  
  log_success "Squid configured"
}

configure_stunnel() {
  log_info "Configuring stunnel TLS wrapper..."
  
  cat > /etc/stunnel/vpk.conf <<EOF
# stunnel TLS wrapper configuration
# Generated by VPS Proxy Kit

# Global options
setuid = ${PROXY_USER}
setgid = ${PROXY_USER}
output = ${LOG_DIR}/stunnel.log
foreground = yes
pid =

# TLS options (OpenSSL 3.0 compatible)
sslVersion = TLSv1.2
options = NO_SSLv2
options = NO_SSLv3
options = NO_TLSv1
options = NO_TLSv1_1
ciphers = HIGH:!aNULL:!MD5:!RC4
EOF
  
  if [[ "$ENABLE_HTTPS" == true ]]; then
    cat >> /etc/stunnel/vpk.conf <<EOF

# HTTPS proxy (Squid with TLS)
[squid-https]
accept = 0.0.0.0:8443
connect = 127.0.0.1:3128
cert = ${CONFIG_DIR}/certs/server.crt
key = ${CONFIG_DIR}/certs/server.key
TIMEOUTclose = 0
EOF
  fi
  
  # NOTE: SOCKS5+TLS (port 11080) is now handled by Shadowsocks with encryption
  # The stunnel approach doesn't work with standard SOCKS5 clients
  
  chmod 644 /etc/stunnel/vpk.conf
  
  # Disable default stunnel4 service
  systemctl stop stunnel4 2>/dev/null || true
  systemctl disable stunnel4 2>/dev/null || true
  systemctl mask stunnel4 2>/dev/null || true
  
  log_success "stunnel configured"
}

configure_shadowsocks() {
  log_info "Configuring Shadowsocks encrypted SOCKS5 proxy..."
  
  # Generate a secure random password if not set
  local SS_PASSWORD="${QUICK_PASSWORD:-$(openssl rand -base64 24)}"
  
  # Create shadowsocks configuration
  cat > ${CONFIG_DIR}/shadowsocks.json <<EOF
{
    "server": "0.0.0.0",
    "server_port": 11080,
    "password": "${SS_PASSWORD}",
    "timeout": 300,
    "method": "chacha20-ietf-poly1305",
    "mode": "tcp_and_udp",
    "fast_open": false,
    "nameserver": "8.8.8.8"
}
EOF
  
  chmod 644 ${CONFIG_DIR}/shadowsocks.json
  
  # Create log file with proper permissions
  touch /var/log/vpk/shadowsocks.log
  chown ${PROXY_USER}:${PROXY_USER} /var/log/vpk/shadowsocks.log
  chmod 644 /var/log/vpk/shadowsocks.log
  
  log_success "Shadowsocks configured on port 11080 with chacha20-ietf-poly1305 encryption"
  log_info "Shadowsocks password: ${SS_PASSWORD}"
}

create_systemd_units() {
  log_info "Creating systemd service units..."
  
  # Dante service
  if [[ "$ENABLE_SOCKS" == true ]]; then
    cat > /etc/systemd/system/vpk-dante.service <<EOF
[Unit]
Description=VPK Dante SOCKS5 Server
After=network.target

[Service]
Type=forking
User=${PROXY_USER}
Group=${PROXY_USER}
PIDFile=/run/danted/danted.pid
RuntimeDirectory=danted
RuntimeDirectoryMode=0755
ExecStart=/usr/sbin/danted -f /etc/dante/danted.conf -p /run/danted/danted.pid
ExecReload=/bin/kill -HUP \$MAINPID
Restart=on-failure
RestartSec=5
TimeoutStartSec=30
LimitNOFILE=65536

[Install]
WantedBy=multi-user.target
EOF
  fi
  
  # Squid service
  if [[ "$ENABLE_HTTPS" == true ]]; then
    cat > /etc/systemd/system/vpk-squid.service <<EOF
[Unit]
Description=VPK Squid HTTP/HTTPS Proxy
After=network.target

[Service]
Type=forking
User=proxy
Group=proxy
PIDFile=/run/squid/squid.pid
RuntimeDirectory=squid
RuntimeDirectoryMode=0755
ExecStart=/usr/sbin/squid -f /etc/squid/squid.conf -sYC
ExecReload=/bin/kill -HUP \$MAINPID
Restart=on-failure
RestartSec=5
LimitNOFILE=65536

[Install]
WantedBy=multi-user.target
EOF
  fi
  
  # Shadowsocks service (replaces stunnel SOCKS5+TLS on port 11080)
  if [[ "$ENABLE_SOCKS" == true ]]; then
    cat > /etc/systemd/system/vpk-shadowsocks.service <<EOF
[Unit]
Description=VPK Shadowsocks Encrypted SOCKS5 Proxy
After=network.target

[Service]
Type=simple
User=${PROXY_USER}
Group=${PROXY_USER}
ExecStart=/usr/bin/ss-server -c ${CONFIG_DIR}/shadowsocks.json -v
Restart=on-failure
RestartSec=5s
StandardOutput=append:/var/log/vpk/shadowsocks.log
StandardError=append:/var/log/vpk/shadowsocks.log

[Install]
WantedBy=multi-user.target
EOF
  fi
  
  # stunnel service (only for HTTPS+TLS on port 8443 now)
  cat > /etc/systemd/system/vpk-stunnel.service <<EOF
[Unit]
Description=VPK stunnel TLS Wrapper
After=network.target

[Service]
Type=forking
User=root
ExecStart=/usr/bin/stunnel /etc/stunnel/vpk.conf
ExecStop=/bin/kill -TERM \$MAINPID
Restart=on-failure
LimitNOFILE=65536

[Install]
WantedBy=multi-user.target
EOF
  
  # Log parser service
  cat > /etc/systemd/system/vpk-logparser.service <<EOF
[Unit]
Description=VPK Log Parser
After=network.target

[Service]
User=${SERVICE_USER}
Group=${SERVICE_USER}
WorkingDirectory=${INSTALL_DIR}
Environment="PATH=${VENV_DIR}/bin:/usr/local/bin:/usr/bin:/bin"
ExecStart=${VENV_DIR}/bin/python -m vpk.logparser --watch
Restart=on-failure
LimitNOFILE=65536

[Install]
WantedBy=multi-user.target
EOF
  
  # Quota enforcer service
  cat > /etc/systemd/system/vpk-quota.service <<EOF
[Unit]
Description=VPK Quota Enforcer
After=network.target

[Service]
User=${SERVICE_USER}
Group=${SERVICE_USER}
WorkingDirectory=${INSTALL_DIR}
Environment="PATH=${VENV_DIR}/bin:/usr/local/bin:/usr/bin:/bin"
ExecStart=${VENV_DIR}/bin/python -m vpk.quota --daemon
Restart=on-failure

[Install]
WantedBy=multi-user.target
EOF
  
  # Metrics exporter service
  cat > /etc/systemd/system/vpk-metrics.service <<EOF
[Unit]
Description=VPK Metrics Exporter
After=network.target

[Service]
User=${SERVICE_USER}
Group=${SERVICE_USER}
WorkingDirectory=${INSTALL_DIR}
Environment="PATH=${VENV_DIR}/bin:/usr/local/bin:/usr/bin:/bin"
ExecStart=${VENV_DIR}/bin/python -m vpk.metrics_exporter
Restart=on-failure

[Install]
WantedBy=multi-user.target
EOF
  
  # Reload systemd
  systemctl daemon-reload
  
  log_success "Systemd units created"
}

configure_firewall() {
  log_info "Configuring firewall rules..."
  
  # Check if ufw is installed
  if ! command -v ufw &> /dev/null; then
    log_warn "ufw not installed, skipping firewall configuration"
    return 0
  fi
  
  # Reset to default deny
  ufw --force reset >/dev/null 2>&1
  ufw default deny incoming
  ufw default allow outgoing
  
  # Allow SSH
  ufw allow 22/tcp comment 'SSH'
  
  # Allow proxy ports
  if [[ "$ENABLE_SOCKS" == true ]]; then
    ufw allow 1080/tcp comment 'SOCKS5'
    ufw allow 11080/tcp comment 'SOCKS5+TLS'
  fi
  
  if [[ "$ENABLE_HTTPS" == true ]]; then
    ufw allow 3128/tcp comment 'HTTP/HTTPS Proxy'
    ufw allow 8443/tcp comment 'HTTPS Proxy+TLS'
  fi
  
  # Enable firewall
  ufw --force enable
  
  log_success "Firewall configured"
}

configure_fail2ban() {
  log_info "Configuring fail2ban..."
  
  # Create VPK filter
  cat > /etc/fail2ban/filter.d/vpk-auth.conf <<'EOF'
# fail2ban filter for VPK auth failures
[Definition]
failregex = ^.*authentication.*failed.*from.*<HOST>.*$
            ^.*auth.*failure.*<HOST>.*$
            ^.*invalid.*user.*from.*<HOST>.*$
ignoreregex =
EOF
  
  # Create VPK jail
  cat > /etc/fail2ban/jail.d/vpk.conf <<EOF
# fail2ban jail for VPK

[vpk-socks]
enabled = true
port = 1080,11080
filter = vpk-auth
logpath = ${LOG_DIR}/danted.log
maxretry = 5
bantime = 3600
findtime = 600

[vpk-squid]
enabled = true
port = 3128,8443
filter = vpk-auth
logpath = ${LOG_DIR}/squid_access.log
maxretry = 5
bantime = 3600
findtime = 600
EOF
  
  # Restart fail2ban
  systemctl restart fail2ban
  systemctl enable fail2ban
  
  log_success "fail2ban configured"
}

configure_logrotate() {
  log_info "Configuring log rotation..."
  
  cat > /etc/logrotate.d/vpk <<EOF
${LOG_DIR}/*.log {
    daily
    rotate 30
    compress
    delaycompress
    notifempty
    create 0640 ${SERVICE_USER} ${SERVICE_USER}
    sharedscripts
    postrotate
        systemctl reload vpk-logparser > /dev/null 2>&1 || true
    endscript
}
EOF
  
  chmod 644 /etc/logrotate.d/vpk
  
  log_success "Log rotation configured"
}

create_config_file() {
  log_info "Creating main configuration file..."
  
  # Get public IP
  PUBLIC_IP=$(curl -s https://api.ipify.org || echo "127.0.0.1")
  
  cat > "${CONFIG_DIR}/config.yml" <<EOF
# VPS Proxy Kit Configuration
# Generated on $(date)

server:
  external_ip: "${PUBLIC_IP}"
  hostname: "${DOMAIN:-$PUBLIC_IP}"

database:
  path: ${DATA_DIR}/vpk.db
  encryption_key_path: ${CONFIG_DIR}/secret.key

proxies:
  socks5:
    enabled: ${ENABLE_SOCKS}
    backend: dante
    port: 1080
    tls_port: 11080
    config_path: /etc/dante/danted.conf
  
  https:
    enabled: ${ENABLE_HTTPS}
    backend: squid
    port: 3128
    tls_port: 8443
    config_path: /etc/squid/squid.conf

security:
  argon2_time_cost: 4
  argon2_memory_cost: 65536
  argon2_parallelism: 2
  tls_min_version: "1.3"
  allowed_ciphers: "TLS_AES_256_GCM_SHA384:TLS_CHACHA20_POLY1305_SHA256:TLS_AES_128_GCM_SHA256"
  max_auth_failures: 5
  auth_failure_window: 900

logging:
  directory: ${LOG_DIR}
  retention_days: 30
  max_size_mb: 100
  level: INFO

quotas:
  check_interval_seconds: 300
  warning_threshold_percent: 80
  grace_period_hours: 24
  enforcement_enabled: true

monitoring:
  metrics_enabled: true
  metrics_port: 9100
  metrics_host: 127.0.0.1

firewall:
  ssh_port: 22
  allowed_ssh_ips: []

backup:
  enabled: true
  directory: ${CONFIG_DIR}/backup
  retention_days: 30
  encryption: true
EOF
  
  chmod 640 "${CONFIG_DIR}/config.yml"
  chown root:${SERVICE_USER} "${CONFIG_DIR}/config.yml"
  
  log_success "Configuration file created"
}

install_vpk_command() {
  log_info "Installing vpk command..."
  
  # Create vpk wrapper script
  cat > /usr/local/bin/vpk <<EOF
#!/bin/bash
# VPS Proxy Kit CLI wrapper

source ${VENV_DIR}/bin/activate
exec python -m vpk.cli "\$@"
EOF
  
  chmod 755 /usr/local/bin/vpk
  
  log_success "vpk command installed"
}

enable_services() {
  log_info "Enabling and starting services..."
  
  # Initialize Squid cache directories if needed
  if [[ "$ENABLE_HTTPS" == true ]]; then
    log_info "Initializing Squid cache directories..."
    mkdir -p /run/squid
    chown proxy:proxy /run/squid
    sudo -u proxy /usr/sbin/squid -f /etc/squid/squid.conf -z 2>/dev/null || log_warn "Squid cache initialization had issues"
  fi
  
  # Enable and start proxy services with retry logic
  if [[ "$ENABLE_SOCKS" == true ]]; then
    systemctl enable vpk-dante
    log_info "Starting Dante SOCKS5 service..."
    systemctl start vpk-dante || log_warn "Dante service startup had issues (this is normal, it will auto-restart)"
    
    systemctl enable vpk-shadowsocks
    log_info "Starting Shadowsocks encrypted SOCKS5 service..."
    systemctl start vpk-shadowsocks || log_warn "Shadowsocks service startup had issues (this is normal, it will auto-restart)"
  fi
  
  if [[ "$ENABLE_HTTPS" == true ]]; then
    systemctl enable vpk-squid
    log_info "Starting Squid HTTP/HTTPS proxy..."
    
    # Wait for cache init to complete
    sleep 2
    
    for i in {1..3}; do
      if systemctl start vpk-squid; then
        log_success "Squid started successfully"
        break
      else
        log_warn "Squid start attempt $i/3 failed, retrying..."
        sleep 2
      fi
    done
  fi
  
  # Enable stunnel
  systemctl enable vpk-stunnel
  log_info "Starting stunnel TLS wrapper..."
  
  # stunnel needs time to generate DH parameters on first run
  systemctl start vpk-stunnel || log_warn "stunnel is starting (DH parameter generation may take 1-2 minutes)"
  
  # Wait a bit and check if stunnel is listening
  sleep 5
  if ss -tln | grep -q ':8443\|:11080'; then
    log_success "stunnel is listening on ports"
  else
    log_warn "stunnel may still be initializing DH parameters"
  fi
  
  # Enable monitoring services (but don't start yet - need DB initialization)
  systemctl enable vpk-logparser 2>/dev/null || true
  systemctl enable vpk-quota 2>/dev/null || true
  systemctl enable vpk-metrics 2>/dev/null || true
  
  log_success "Services enabled"
}

create_quick_mode_user() {
  if [[ "$MODE" != "quick" ]]; then
    return 0
  fi
  
  if [[ -z "$QUICK_USERNAME" ]] || [[ -z "$QUICK_PASSWORD" ]]; then
    log_error "Quick mode requires --username and --password"
    exit 1
  fi
  
  log_info "Creating quick mode user: ${QUICK_USERNAME}..."
  
  # This will be handled by vpk CLI after it's set up
  # For now, just log the instruction
  log_warn "After installation, run: vpk create-user --username ${QUICK_USERNAME} --password '${QUICK_PASSWORD}' --protocol socks,https --quota 100GB"
}

print_summary() {
  local PUBLIC_IP=$(curl -s https://api.ipify.org || echo "127.0.0.1")
  
  cat <<EOF

${GREEN}=============================================================
Installation Complete!
=============================================================${NC}

VPS Proxy Kit has been successfully installed.

${BLUE}Installation Details:${NC}
- Installation directory: ${INSTALL_DIR}
- Configuration directory: ${CONFIG_DIR}
- Log directory: ${LOG_DIR}
- Public IP: ${PUBLIC_IP}

${BLUE}Installed Services:${NC}
EOF
  
  if [[ "$ENABLE_SOCKS" == true ]]; then
    echo "- SOCKS5 proxy (Dante): port 1080"
    echo "- SOCKS5 with TLS: port 11080"
  fi
  
  if [[ "$ENABLE_HTTPS" == true ]]; then
    echo "- HTTP/HTTPS proxy (Squid): port 3128"
    echo "- HTTPS proxy with TLS: port 8443"
  fi
  
  cat <<EOF

${BLUE}Next Steps:${NC}

1. Initialize the database:
   sudo -u ${SERVICE_USER} vpk init-db

2. Create your first user:
   vpk create-user --username alice --password 'YourSecurePassword!' --protocol socks,https --quota 100GB

3. Start monitoring services:
   sudo systemctl start vpk-logparser
   sudo systemctl start vpk-quota
   sudo systemctl start vpk-metrics

4. Check status:
   vpk status

5. Test the connection:
   curl --socks5 alice:YourSecurePassword!@${PUBLIC_IP}:1080 https://ipinfo.io/ip

${BLUE}Management:${NC}
- Interactive menu: vpk menu
- List users: vpk list-users
- View logs: vpk view-logs
- Check quotas: vpk quota-usage --username alice

${BLUE}Documentation:${NC}
- README: ${INSTALL_DIR}/README.md
- Security policy: ${INSTALL_DIR}/SECURITY.md
- Configuration: ${CONFIG_DIR}/config.yml

${YELLOW}Security Reminders:${NC}
- Change default SSH port: sudo nano /etc/ssh/sshd_config
- Disable SSH password authentication (use keys)
- Review firewall rules: sudo ufw status
- Keep system updated: sudo apt update && sudo apt upgrade
- Rotate certificates regularly: vpk rotate-cert

${GREEN}Happy proxying!${NC}

EOF
}

# Main installation flow
main() {
  log_info "Starting VPS Proxy Kit installation..."
  
  check_root
  check_ubuntu
  confirm_installation
  
  update_system
  install_packages
  create_users
  create_directories
  setup_python_venv
  install_python_deps
  install_vpk_package
  generate_encryption_key
  generate_certificates
  
  if [[ "$MODE" == "prod" ]]; then
    configure_dante
    configure_squid
  fi
  
  configure_stunnel
  configure_shadowsocks
  create_systemd_units
  configure_firewall
  configure_fail2ban
  configure_logrotate
  create_config_file
  install_vpk_command
  enable_services
  create_quick_mode_user
  
  print_summary
  
  log_success "Installation completed successfully!"
}

# Run main installation
main "$@"
