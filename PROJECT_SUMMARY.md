# VPS Proxy Kit - Project Summary

## Project Overview

**VPS Proxy Kit** is a production-ready, modular proxy server management system for Ubuntu 22.04 that provides:

- **Multi-Protocol Support**: SOCKS5 (Dante), HTTP/HTTPS (Squid)
- **Strong Security**: Argon2id hashing, encrypted database, TLS 1.3
- **Per-User Management**: Bandwidth quotas, usage tracking, session monitoring
- **User-Friendly CLI**: Interactive menu + scriptable commands
- **Monitoring**: Prometheus metrics, Grafana dashboards
- **Hardened Deployment**: systemd services, firewall rules, fail2ban

## Complete File Structure

```
vps-proxy-kit/
├── bootstrap.sh                    # Automated installer script
├── requirements.txt                # Python dependencies
├── setup.py                        # Python package setup
├── LICENSE                         # MIT License
├── README.md                       # Main documentation
├── SECURITY.md                     # Security policy and threat model
├── DEPLOYMENT.md                   # Deployment checklist
├── QUICKSTART.md                   # 10-command quick start
├── .gitignore                      # Git ignore patterns
│
├── vpk/                            # Main Python package
│   ├── __init__.py                 # Package initialization
│   ├── cli.py                      # Click-based CLI (main entry point)
│   ├── config.py                   # YAML configuration management
│   ├── db.py                       # Encrypted SQLite database
│   ├── users.py                    # User management with Argon2id
│   ├── logparser.py                # Parse proxy logs, update counters
│   ├── quota.py                    # Quota enforcement daemon
│   ├── metrics_exporter.py         # Prometheus metrics exporter
│   ├── proxy_backends.py           # Dante/Squid service management
│   ├── tc_manager.py               # Traffic control (bandwidth shaping)
│   ├── firewall.py                 # UFW/nftables management
│   └── utils.py                    # Utility functions
│
├── examples/                       # Example configurations
│   ├── dante.conf                  # Dante SOCKS5 config
│   ├── squid.conf                  # Squid HTTP/HTTPS config
│   ├── stunnel-proxy.conf          # stunnel TLS wrapper config
│   └── client-examples.txt         # Client configuration examples
│
└── tests/                          # Unit and integration tests
    └── test_vpk.py                 # pytest test suite
```

## Technology Stack

### Core Technologies

- **Language**: Python 3.10+
- **Database**: SQLite with encryption (Fernet/AES-256)
- **Password Hashing**: Argon2id
- **Encryption**: cryptography library (PBKDF2, AES-256-GCM)
- **CLI Framework**: Click
- **Monitoring**: Prometheus, Grafana

### Proxy Servers

- **SOCKS5**: Dante server (production) or microsocks (quick mode)
- **HTTP/HTTPS**: Squid proxy server
- **TLS Wrapper**: stunnel4 for TLS 1.3 encryption

### System Services

- **Init System**: systemd
- **Firewall**: UFW (iptables/nftables)
- **Intrusion Prevention**: fail2ban
- **Log Rotation**: logrotate
- **Traffic Control**: tc (HTB, SFQ)

## Key Features Implemented

### Authentication & Security

✅ Argon2id password hashing (time=4, memory=64MB, parallelism=2)  
✅ Encrypted SQLite database at rest  
✅ Token-based authentication (optional)  
✅ Rate limiting (5 failures per 15 minutes)  
✅ TLS 1.3 only (modern cipher suites)  
✅ Automatic certificate management (Let's Encrypt + self-signed)  
✅ fail2ban integration for brute force protection

### User Management

✅ Create/delete/suspend/resume users  
✅ Per-user bandwidth quotas  
✅ Multi-protocol support (SOCKS5, HTTP/HTTPS)  
✅ Expiration dates  
✅ Token authentication for APIs  
✅ Session tracking

### Monitoring & Logging

✅ Prometheus metrics exporter  
✅ Per-user bandwidth counters  
✅ Active session tracking  
✅ Quota usage metrics  
✅ Audit logging  
✅ Log rotation (30 days default)

### Quota Enforcement

✅ Automatic quota checking (5-minute intervals)  
✅ User suspension when quota exceeded  
✅ Warning thresholds (80% default)  
✅ Grace periods  
✅ Real-time usage tracking from logs

### Deployment & Operations

✅ One-command bootstrap installer  
✅ systemd service management  
✅ Automated firewall configuration  
✅ Backup and restore procedures  
✅ Health checks and status monitoring  
✅ Non-interactive CLI for automation

## System Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                     Internet Clients                         │
└────────────────────┬─────────────────────────────────────────┘
                     │
                     ▼
┌──────────────────────────────────────────────────────────────┐
│                    UFW Firewall                              │
│  Ports: 1080, 11080 (SOCKS5)  3128, 8443 (HTTP/HTTPS)      │
└────────────────────┬─────────────────────────────────────────┘
                     │
                     ▼
┌──────────────────────────────────────────────────────────────┐
│               stunnel (TLS Termination)                      │
│     :11080 (SOCKS5+TLS)    :8443 (HTTPS+TLS)                │
└────────────────────┬─────────────────────────────────────────┘
                     │
                     ▼
┌──────────────────────────────────────────────────────────────┐
│          Proxy Servers (User: proxyd)                        │
│    Dante :1080 (SOCKS5)    Squid :3128 (HTTP/HTTPS)         │
└────────────────────┬─────────────────────────────────────────┘
                     │
                     ▼
┌──────────────────────────────────────────────────────────────┐
│           VPK Management Layer (User: proxyadmin)            │
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ Log Parser   │  │ Quota        │  │ Metrics      │      │
│  │ (Watchdog)   │  │ Enforcer     │  │ Exporter     │      │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘      │
│         │                  │                  │              │
│         └──────────────────┼──────────────────┘              │
│                            ▼                                 │
│                 ┌──────────────────────┐                     │
│                 │  Encrypted SQLite DB  │                     │
│                 │  (AES-256 at rest)    │                     │
│                 └──────────────────────┘                     │
└──────────────────────────────────────────────────────────────┘
                            │
                            ▼
                   ┌─────────────────┐
                   │  vpk CLI Tool   │
                   │  (Admin Access)  │
                   └─────────────────┘
```

## Security Model

### Threat Protection

| Threat               | Protection Mechanism                |
| -------------------- | ----------------------------------- |
| Credential theft     | Argon2id hashing, encrypted DB      |
| Man-in-the-middle    | TLS 1.3, certificate pinning        |
| Brute force          | fail2ban, rate limiting             |
| Database compromise  | Encryption at rest (Fernet/AES-256) |
| Privilege escalation | Unprivileged service users          |
| Log injection        | Input sanitization                  |
| DoS attacks          | Rate limiting, connection limits    |

### Security Layers

1. **Network Layer**: UFW firewall, fail2ban
2. **Transport Layer**: TLS 1.3 (stunnel)
3. **Application Layer**: User authentication (Argon2id)
4. **Data Layer**: Encrypted database (AES-256)
5. **System Layer**: Unprivileged users, systemd hardening

## Deployment Options

### Production Mode (Default)

- Dante + Squid + stunnel
- Full monitoring and logging
- systemd service management
- Recommended for multi-user production environments

### Quick Mode (Development/Testing)

- microsocks or autossh
- Minimal logging
- Single-user oriented
- Rapid setup for testing

## CLI Commands Summary

### User Management

```bash
vpk create-user --username USER --password PASS --protocol socks,https --quota 100GB
vpk delete-user --username USER --yes
vpk list-users
vpk user-info --username USER
vpk suspend-user --username USER
vpk resume-user --username USER
```

### Quota Management

```bash
vpk set-quota --username USER --quota 200GB
vpk quota-usage --username USER
vpk reset-usage --username USER --yes
```

### Monitoring

```bash
vpk status
vpk show-sessions
vpk view-logs --lines 100
vpk export-usage --output report.csv
```

### System Management

```bash
vpk init-db
vpk check-quotas --force
vpk rotate-keys --yes
vpk backup --output backup.tar.gz
```

## Performance Characteristics

### Scalability

- **Concurrent Users**: 100-500 (depending on VPS specs)
- **Connections per User**: 10-100
- **Throughput**: Limited by VPS network bandwidth
- **Database Size**: Scales to millions of log entries

### Resource Requirements

#### Minimum (Development)

- 1 vCPU
- 1GB RAM
- 10GB disk
- 100 Mbps network

#### Recommended (Production)

- 2-4 vCPU
- 4GB RAM
- 50GB SSD
- 1 Gbps network

### Performance Tuning

- Increase file descriptor limits (`ulimit -n`)
- Tune kernel parameters (`sysctl`)
- Adjust Squid cache size
- Configure Dante connection limits
- Enable workers for multi-core CPUs

## Testing Strategy

### Unit Tests

- Password hashing and verification
- Quota parsing and formatting
- Database encryption/decryption
- User CRUD operations
- Configuration validation

### Integration Tests

- End-to-end proxy connection
- Authentication flows
- Quota enforcement
- Log parsing and counter updates
- Service restart and recovery

### Manual Tests

- Client connectivity (curl, browsers)
- Load testing (multiple concurrent connections)
- Failover scenarios
- Certificate expiration handling

## Monitoring & Alerting

### Prometheus Metrics

- `vpk_users_total{status}`
- `vpk_user_bytes_total{user,protocol}`
- `vpk_user_quota_bytes{user}`
- `vpk_active_connections{user,protocol}`
- `vpk_quota_usage_percent{user}`

### Alert Rules (Recommended)

- User quota >90%
- Service downtime >1 minute
- High authentication failure rate
- Certificate expiration <30 days
- Database size >90% capacity

## Compliance & Legal

### Data Retention

- Connection logs: 30 days
- Usage statistics: 12 months (aggregated)
- Audit logs: 60 days
- Backups: 30 days

### GDPR Compliance

- Right to access: `vpk export-user-data`
- Right to erasure: `vpk delete-user --purge-data`
- Right to portability: JSON export format
- Data processing transparency: Documented in SECURITY.md

### Legal Warnings

- Users responsible for compliance with local laws
- Terms of service required for public deployment
- Acceptable use policy recommended
- No logging of request contents (privacy by design)

## Future Enhancements

### Planned Features

- [ ] Two-factor authentication (TOTP)
- [ ] Web-based admin UI (read-only dashboard)
- [ ] REST API for user management
- [ ] Real-time quota enforcement (via proxy plugins)
- [ ] GeoIP-based access control
- [ ] Content filtering integration
- [ ] DDoS protection (rate limiting per IP)
- [ ] Multi-server clustering
- [ ] IPv6 support

### Known Limitations

- Per-connection bandwidth shaping requires tc filters (complex)
- UDP SOCKS5 quota tracking is approximate
- HTTPS destination logging limited to CONNECT domains
- No built-in content filtering (requires integration)

## Contributing

Contributions welcome! See README.md for guidelines.

Key areas for contribution:

- Web UI implementation
- Additional proxy backends (3proxy, tinyproxy)
- Enhanced monitoring dashboards
- Mobile app for user management
- Docker deployment option

## License

MIT License - see LICENSE file

## Support

- **GitHub**: https://github.com/genome96/vps-proxy-kit
- **Issues**: https://github.com/genome96/vps-proxy-kit/issues
- **Documentation**: See README.md, SECURITY.md, DEPLOYMENT.md

---

**Project Status**: Production-ready v1.0.0  
**Target Platform**: Ubuntu 22.04 LTS  
**Maintenance**: Active  
**Last Updated**: 2025-10-13
