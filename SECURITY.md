# Security Policy

## Threat Model

### Assets

1. **User Credentials** - Passwords, authentication tokens
2. **Usage Data** - Per-user bandwidth consumption, connection logs
3. **Proxy Availability** - Service uptime and reliability
4. **Encryption Keys** - Database encryption key, TLS certificates
5. **System Access** - VPS root/admin access

### Threats

| Threat                            | Impact   | Likelihood | Mitigation                            |
| --------------------------------- | -------- | ---------- | ------------------------------------- |
| Credential theft via log exposure | High     | Medium     | Encrypted DB, no plaintext logs       |
| Brute force authentication        | High     | High       | fail2ban, rate limiting, Argon2id     |
| Man-in-the-middle attacks         | High     | Medium     | TLS 1.3, certificate pinning          |
| Database compromise               | High     | Low        | Encryption at rest, strict file perms |
| Service disruption (DoS)          | Medium   | High       | Rate limiting, connection limits      |
| Unauthorized proxy usage          | High     | Medium     | Per-user auth, session tracking       |
| Log injection attacks             | Medium   | Low        | Input validation, log sanitization    |
| Privilege escalation              | Critical | Low        | Unprivileged service users, SELinux   |

## Security Controls

### Authentication & Authorization

#### Password Security

- **Hashing Algorithm**: Argon2id (winner of Password Hashing Competition)
- **Parameters**:
  - Time cost: 4 iterations
  - Memory cost: 65536 KB (64 MB)
  - Parallelism: 2 threads
  - Salt: 16 bytes, cryptographically random
- **Rationale**: Argon2id provides resistance to GPU cracking attacks and side-channel attacks
- **Performance**: ~200ms per hash on typical VPS (1 vCPU, 2GB RAM)

#### Token Authentication

- **Token Format**: `tok_` + 32 bytes of cryptographically random data (base64-encoded)
- **Storage**: SHA-256 hash stored in database
- **Lifetime**: No expiration by default, user-revocable
- **Use Case**: API integrations, automated clients

#### Rate Limiting

- **Authentication Attempts**: Max 5 failures per 15 minutes per IP
- **Connection Rate**: Max 100 connections per minute per user
- **Enforcement**: fail2ban for IP bans, proxy config for connection limits

### Encryption

#### Data at Rest

- **Database Encryption**:
  - Algorithm: AES-256-GCM via `cryptography.fernet`
  - Key derivation: PBKDF2-HMAC-SHA256 from master key
  - Master key location: `/etc/vpk/secret.key`
  - Key permissions: `0600`, owner `root`
- **Encrypted Fields**:
  - Full database file encrypted
  - Individual password hashes use Argon2id
  - Token hashes use SHA-256

#### Data in Transit

- **TLS Configuration**:
  - Minimum version: TLS 1.3
  - Cipher suites: `TLS_AES_256_GCM_SHA384:TLS_CHACHA20_POLY1305_SHA256:TLS_AES_128_GCM_SHA256`
  - No TLS 1.2 or earlier (unless explicitly enabled by admin)
  - HSTS enabled for HTTPS connections
  - OCSP stapling enabled
- **Certificate Management**:
  - Let's Encrypt for domain-based deployments (auto-renewal)
  - Self-signed certificates for IP-only deployments (manual rotation recommended every 90 days)
  - Certificate validity check on service startup

#### Transport Protection

- **SOCKS5**: Optional TLS wrapper via stunnel on port 11080
- **HTTP/HTTPS Proxy**: TLS wrapper via stunnel on port 8443
- **Management API**: TLS-only (no plaintext HTTP)

### Access Control

#### Service Users

```bash
# proxyadmin - Owns application files, runs management services
uid=999, gid=999
home=/opt/vps-proxy-kit
shell=/bin/bash
groups=proxyadmin

# proxyd - Runs proxy services (dante, squid)
uid=998, gid=998
home=/nonexistent
shell=/usr/sbin/nologin
groups=proxyd
```

#### File Permissions

```
/opt/vps-proxy-kit/                     0750 proxyadmin:proxyadmin
/opt/vps-proxy-kit/data/                0700 proxyadmin:proxyadmin
/opt/vps-proxy-kit/data/vpk.db          0600 proxyadmin:proxyadmin
/etc/vpk/                               0750 root:root
/etc/vpk/secret.key                     0600 root:root
/etc/vpk/config.yml                     0640 root:proxyadmin
/etc/vpk/certs/                         0750 root:root
/etc/vpk/certs/server.key               0600 root:root
/var/log/vpk/                           0750 proxyadmin:proxyadmin
/var/log/vpk/*.log                      0640 proxyadmin:proxyadmin
```

#### Firewall Rules (UFW)

```bash
# Default deny incoming, allow outgoing
ufw default deny incoming
ufw default allow outgoing

# SSH (change port from 22 in production)
ufw allow 22/tcp

# Proxy services
ufw allow 1080/tcp    # SOCKS5
ufw allow 11080/tcp   # SOCKS5 + TLS
ufw allow 3128/tcp    # HTTP/HTTPS
ufw allow 8443/tcp    # HTTP/HTTPS + TLS

# Management API (localhost only)
ufw deny 5000/tcp     # Block external access

# Monitoring (localhost only)
ufw deny 9100/tcp     # Block external Prometheus scraping
```

### Logging & Monitoring

#### Log Security

- **No Plaintext Credentials**: Passwords and tokens never logged
- **Sanitization**: User input sanitized before logging
- **Retention**: 30 days by default (configurable)
- **Access**: Logs readable only by `proxyadmin` user and `root`
- **Audit Trail**: All user management actions logged with timestamp and actor

#### What We Log

✅ **DO LOG**:

- Connection start/end timestamps
- Source IP addresses (anonymized after 7 days)
- Destination domains/IPs (hashed for privacy)
- Bytes transferred per connection
- Authentication success/failure events
- User management actions
- Service start/stop/restart events
- Quota enforcement actions
- Error conditions

❌ **DO NOT LOG**:

- Passwords or password hashes
- Authentication tokens
- Full URLs (only domain + path length)
- Request/response bodies
- Decrypted database contents

#### Security Monitoring

- **fail2ban**: Monitors auth failures, auto-bans IPs
- **Prometheus Alerts**:
  - High authentication failure rate
  - Unusual bandwidth spike
  - Service downtime
  - Certificate expiration (30 days warning)
- **Log Analysis**: Daily automated scan for suspicious patterns

### Vulnerability Management

#### Dependency Updates

```bash
# Check for security updates
vpk check-updates --security-only

# Apply security updates
sudo vpk update --security --yes

# View update history
vpk update-history
```

#### CVE Monitoring

- Automated scanning of Python dependencies via `safety` package
- Monthly review of proxy binary versions (Dante, Squid, stunnel)
- Subscribe to security mailing lists:
  - ubuntu-security-announce
  - squid-announce
  - dante-announce

#### Vulnerability Disclosure

**Reporting**: Email security@example.com with:

- Description of vulnerability
- Steps to reproduce
- Potential impact assessment
- Suggested remediation (optional)

**Response Time**:

- Critical: 24 hours
- High: 7 days
- Medium: 30 days
- Low: 90 days

### Incident Response

#### Security Incident Procedures

1. **Detect**: Automated alerts, manual review
2. **Contain**:
   - Isolate affected users/services
   - Block malicious IPs via firewall
   - Disable compromised accounts
3. **Investigate**:
   - Review logs: `vpk view-logs --since "2025-10-01" --output /tmp/incident.log`
   - Check active sessions: `vpk show-sessions --all`
   - Analyze database: `vpk db-audit`
4. **Remediate**:
   - Patch vulnerabilities
   - Rotate credentials: `vpk rotate-keys --yes`
   - Force password reset: `vpk force-password-reset --all`
5. **Recover**:
   - Restore from backup if needed
   - Re-enable services
   - Monitor for recurrence
6. **Document**:
   - Incident report
   - Lessons learned
   - Update runbooks

#### Emergency Commands

```bash
# Immediately disable all users
vpk emergency-lockdown --yes

# Kill all active sessions
vpk kill-sessions --all --yes

# Rotate all keys and tokens
vpk rotate-keys --force --yes

# Export audit trail
vpk export-audit-log --output /tmp/audit-$(date +%Y%m%d).log

# Re-enable after incident resolved
vpk resume-all-users --yes
```

### Compliance & Data Retention

#### GDPR Compliance

**Legal Basis**: Legitimate interest (service provision)

**Data Subject Rights**:

- **Right to Access**: `vpk export-user-data --username alice --output alice-data.zip`
- **Right to Erasure**: `vpk delete-user --username alice --purge-data --yes`
- **Right to Portability**: Exported data in JSON format
- **Right to Rectification**: User can update own credentials

**Data Processing**:

- Purpose: Proxy service provision, billing, security monitoring
- Retention: See below
- Processors: None (all data processed on VPS)
- International transfers: None

#### Data Retention Policy

| Data Type                     | Retention Period         | Rationale                  |
| ----------------------------- | ------------------------ | -------------------------- |
| User account info             | Until deleted            | Service provision          |
| Connection logs               | 30 days                  | Security, debugging        |
| Usage statistics (aggregated) | 12 months                | Billing, capacity planning |
| Source IP addresses           | 7 days (then anonymized) | Security, abuse prevention |
| Authentication logs           | 90 days                  | Security audit trail       |
| System logs                   | 30 days                  | Debugging, compliance      |
| Backup data                   | 30 days                  | Disaster recovery          |

**Anonymization**: After initial retention period, source IPs are hashed with salt, making re-identification impractical.

**Data Deletion**:

```bash
# Automated cleanup (runs daily via cron)
vpk cleanup-old-data --yes

# Manual purge
vpk purge-logs --older-than 30d --yes
```

### Hardening Checklist

Before deploying to production:

- [ ] Change default SSH port: `sudo nano /etc/ssh/sshd_config`
- [ ] Disable SSH password auth (use keys only)
- [ ] Enable UFW firewall: `sudo ufw enable`
- [ ] Configure fail2ban: `sudo systemctl enable fail2ban`
- [ ] Set strong root password: `sudo passwd`
- [ ] Disable root SSH login: `PermitRootLogin no`
- [ ] Install security updates: `sudo apt update && sudo apt upgrade -y`
- [ ] Enable automatic security updates: `sudo dpkg-reconfigure unattended-upgrades`
- [ ] Set up log monitoring: Configure Prometheus alerts
- [ ] Rotate default keys: `vpk rotate-keys --yes`
- [ ] Review config: `vpk config review --security`
- [ ] Obtain TLS certificate: `sudo certbot certonly --standalone -d proxy.example.com`
- [ ] Configure TLS 1.3 only: Already default in config
- [ ] Set strong admin password: `vpk set-admin-password`
- [ ] Restrict management API: Localhost only (default)
- [ ] Enable audit logging: Already enabled
- [ ] Test backup restore: `vpk test-backup-restore`
- [ ] Document incident response: Update SECURITY.md with contact info
- [ ] Review file permissions: `vpk check-permissions`
- [ ] Scan for CVEs: `vpk scan-vulnerabilities`
- [ ] Set up monitoring alerts: Configure Grafana alert rules

### Backup & Recovery

#### Backup Strategy

**What to Backup**:

- `/opt/vps-proxy-kit/data/vpk.db` - User database
- `/etc/vpk/` - Configuration and keys
- `/var/log/vpk/` - Logs (optional)

**Backup Frequency**: Daily

**Backup Retention**: 30 days

**Backup Encryption**: GPG-encrypted with passphrase

```bash
# Manual backup
vpk backup --output /backup/vpk-$(date +%Y%m%d).tar.gz.gpg

# Automated backup (cron)
0 2 * * * /usr/local/bin/vpk backup --output /backup/vpk-$(date +\%Y\%m\%d).tar.gz.gpg --encrypt --passphrase-file /root/.vpk-backup-pass

# Verify backup
vpk verify-backup --input /backup/vpk-20251013.tar.gz.gpg

# Restore from backup
vpk restore --input /backup/vpk-20251013.tar.gz.gpg --yes
```

#### Disaster Recovery

**RTO (Recovery Time Objective)**: 4 hours  
**RPO (Recovery Point Objective)**: 24 hours

**Recovery Steps**:

1. Provision new VPS with Ubuntu 22.04
2. Clone repository: `git clone https://github.com/genome96/vps-proxy-kit.git`
3. Run bootstrap: `sudo ./bootstrap.sh --yes`
4. Restore backup: `vpk restore --input /backup/vpk-latest.tar.gz.gpg`
5. Update IP addresses: `vpk config set external_ip NEW_IP`
6. Verify services: `vpk status --detailed`
7. Test connectivity: `vpk test-proxy --all`
8. Update DNS (if using domain)

### Known Limitations

1. **Per-Connection Bandwidth Shaping**: Kernel-level per-connection shaping without proxy cooperation is difficult. We use proxy-level limiting (Squid delay_pools) and tc for aggregate user limits.

2. **Real-Time Quota Enforcement**: Log parsing introduces 30-60 second delay. For strict real-time enforcement, consider integrating with proxy APIs (Squid ICAP, Dante plugin).

3. **Protocol Detection**: Cannot distinguish between HTTPS destinations when using HTTPS proxy (due to TLS encryption). Destination logging limited to CONNECT method domains.

4. **UDP Support**: SOCKS5 UDP is supported by Dante but harder to track per-user. UDP quota tracking is approximate based on session duration.

5. **IP Geolocation**: Not implemented. For IP-based access control, integrate with GeoIP2 database (commercial).

6. **DPI/Content Filtering**: No deep packet inspection. For content filtering, integrate with Squid+SquidGuard or E2Guardian.

### Security Roadmap

**Planned Enhancements**:

- [ ] Two-factor authentication (TOTP)
- [ ] Client certificate authentication (mutual TLS)
- [ ] Real-time quota enforcement via proxy plugins
- [ ] Automated certificate rotation
- [ ] Intrusion detection system (Suricata/Snort integration)
- [ ] GeoIP-based access control
- [ ] Content filtering integration
- [ ] DDoS protection (rate limiting per-IP)
- [ ] Web-based admin UI (read-only dashboard)
- [ ] SSO integration (OAuth2, SAML)

### Security Audit History

| Date       | Auditor  | Scope           | Findings | Status   |
| ---------- | -------- | --------------- | -------- | -------- |
| 2025-10-13 | Internal | Initial release | N/A      | Baseline |

Future audits recommended annually or after major version updates.

### References

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [CIS Ubuntu 22.04 Benchmark](https://www.cisecurity.org/benchmark/ubuntu_linux)
- [NIST Cybersecurity Framework](https://www.nist.gov/cyberframework)
- [Argon2 RFC 9106](https://datatracker.ietf.org/doc/rfc9106/)
- [TLS 1.3 RFC 8446](https://datatracker.ietf.org/doc/rfc8446/)

### Contact

**Security Team**: security@example.com  
**PGP Key**: Available at https://example.com/security.asc  
**Response Time**: 24-48 hours for security reports

---

**Last Updated**: 2025-10-13  
**Version**: 1.0.0
