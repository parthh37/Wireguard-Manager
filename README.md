# 🔐 WireGuard Manager

A secure, web-based management interface for WireGuard VPN with 2FA, automated client management, and comprehensive usage tracking.

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Flask](https://img.shields.io/badge/Flask-3.0-green.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

## ✨ Features

### 🎯 Core Features

- **📊 Dashboard** - Real-time overview of connected clients, data usage, and system status
- **👥 Client Management** - Add, remove, enable/disable VPN clients with one click
- **⏰ Automatic Expiry** - Clients automatically disabled after expiration date
- **📱 QR Code Generation** - Instant mobile setup via QR code scanning
- **💾 Config Download** - Secure download of client configuration files
- **🌐 IPv6 Support** - Dual-stack IPv4/IPv6 with public routing for service hosting

### 🔒 Security

- **🔐 Secure Login** - Password-based authentication with bcrypt hashing
- **🛡️ Two-Factor Authentication (2FA)** - TOTP-based 2FA support
- **🌐 IP Whitelisting** - Restrict access by IP address
- **🔒 HTTPS Only** - SSL/TLS encryption for all connections
- **⏱️ Auto Logout** - Automatic session timeout after inactivity
- **📝 Audit Logging** - Complete audit trail of all actions

### 📈 Usage Tracking

- **📊 Real-time Statistics** - Live monitoring of data usage per client
- **📅 Daily/Monthly Reports** - Historical usage data and trends
- **📉 Usage Charts** - Visual representation of bandwidth usage
- **💽 Data Breakdown** - Upload/download statistics per client

### 🎨 Connection Profiles

- **📋 Custom Templates** - Create reusable connection profiles
- **🌍 Full Tunnel** - Route all traffic through VPN
- **🔀 Split Tunnel** - Route only specific traffic through VPN
- **🔧 Custom DNS** - Use custom DNS servers per profile
- **📍 Allowed IPs** - Fine-grained control over routed networks
- **🌐 IPv6 Service Hosting** - Publicly routable IPv6 for hosting services from any device

### 🤖 Automation

- **⏰ Auto-disable Expired Clients** - Hourly check and disable
- **📊 Daily Usage Recording** - Automatic statistics collection
- **💾 Automated Backups** - Configurable daily backups
- **🧹 Backup Cleanup** - Automatic removal of old backups

### 💾 Backup & Restore

- **📦 One-click Backup** - Create full system backup instantly
- **♻️ Easy Restore** - Restore from any backup point
- **🔄 Automated Backups** - Scheduled daily backups
- **📤 Download Backups** - Export backups to external storage

### 🎨 User Interface

- **📱 Responsive Design** - Works on desktop, tablet, and mobile
- **🎯 Clean & Intuitive** - Easy-to-use interface
- **🌓 Modern UI** - Clean, professional design
- **⚡ Fast & Lightweight** - Minimal resource usage

## 🚀 Quick Start

### Prerequisites

- Ubuntu 20.04/22.04 or Debian 11/12
- Root or sudo access
- Public IP address or domain name

### Automated Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/wireguard-manager.git
cd wireguard-manager

# Run installation script
sudo bash deployment/install.sh
```

The installer will:
1. Install all dependencies (Python, WireGuard, Redis, Nginx)
2. Configure WireGuard interface
3. Set up the web application
4. Configure Nginx with optional SSL
5. Set up firewall rules

### Access the Application

After installation:
1. Navigate to `https://your-domain.com`
2. Complete initial setup (create admin password)
3. Set up 2FA authentication
4. Create your first connection profile
5. Add VPN clients

## 📖 Documentation

- **[Deployment Guide](DEPLOYMENT.md)** - Complete installation and setup instructions
- **[IPv6 Service Hosting](IPv6_SERVICE_HOSTING.md)** - Host services from any device with public IPv6
- **[Connection Profiles](PROFILES.md)** - Pre-configured profile templates and IPv6 examples
- **[Configuration](DEPLOYMENT.md#-configuration-options)** - Environment variables and settings
- **[Troubleshooting](DEPLOYMENT.md#-troubleshooting)** - Common issues and solutions
- **[Security](DEPLOYMENT.md#-security-best-practices)** - Best practices and recommendations

## 🏗️ Architecture

### Technology Stack

- **Backend**: Flask (Python 3.8+)
- **Session Storage**: Redis
- **VPN**: WireGuard
- **Web Server**: Nginx (reverse proxy)
- **Data Storage**: File-based JSON (no external database)
- **2FA**: TOTP (pyotp)
- **QR Codes**: qrcode library

### File Structure

```
wireguard-manager/
├── app.py                 # Main Flask application
├── config.py              # Configuration management
├── automation.py          # Scheduled tasks
├── requirements.txt       # Python dependencies
├── .env.example          # Environment variables template
│
├── routes/               # Flask blueprints
│   ├── auth.py          # Authentication routes
│   ├── dashboard.py     # Dashboard routes
│   ├── clients.py       # Client management routes
│   ├── profiles.py      # Profile routes
│   ├── usage.py         # Usage tracking routes
│   ├── settings.py      # Settings routes
│   └── audit.py         # Audit log routes
│
├── utils/               # Utility modules
│   ├── storage.py      # File-based data storage
│   ├── wireguard.py    # WireGuard integration
│   ├── auth.py         # Authentication utilities
│   └── helpers.py      # Helper functions
│
├── templates/           # HTML templates
│   ├── base.html
│   ├── login.html
│   ├── dashboard.html
│   ├── clients/
│   ├── profiles/
│   ├── usage/
│   ├── settings/
│   └── audit/
│
├── deployment/          # Deployment files
│   ├── install.sh      # Installation script
│   ├── nginx.conf      # Nginx configuration
│   └── wireguard-manager.service
│
└── data/               # Application data (created at runtime)
    ├── clients/        # Client configurations
    ├── profiles/       # Connection profiles
    ├── usage/          # Usage statistics
    └── audit/          # Audit logs
```

## 🔧 Configuration

### Environment Variables

Key configuration options in `.env`:

```bash
# Security
SECRET_KEY=<random-secret>
ENABLE_2FA=True
SESSION_TIMEOUT=1800
IP_WHITELIST=

# WireGuard IPv4
WG_SERVER_IP=10.0.0.1
WG_SERVER_PORT=51820
SERVER_PUBLIC_IP=<your-public-ip>

# WireGuard IPv6 (Optional - for service hosting)
WG_IPV6_ENABLED=False
WG_IPV6_SUBNET=2a11:8083:11:13f0::/64
WG_SERVER_IPV6=2a11:8083:11:13f0::1
IPV6_PUBLIC_ROUTING=False

# Backup
AUTO_BACKUP_ENABLED=True
AUTO_BACKUP_HOUR=2
BACKUP_RETENTION_DAYS=30
```

See [DEPLOYMENT.md](DEPLOYMENT.md#-configuration-options) for all options.

## 📱 Client Setup

### Desktop

1. Download [WireGuard](https://www.wireguard.com/install/)
2. Download config file from web interface
3. Import into WireGuard client
4. Connect

### Mobile

1. Install WireGuard app
2. Scan QR code from client details page
3. Connect

## 🌐 IPv6 Service Hosting

**NEW:** Host public services directly from your devices using IPv6!

When IPv6 is enabled, each VPN client receives a **publicly routable IPv6 address** from your VPS's /64 subnet. This allows you to:

- ✅ **Host web servers** from your laptop
- ✅ **Run SSH servers** with public access
- ✅ **Deploy game servers** without port forwarding
- ✅ **Self-host services** (Nextcloud, Plex, etc.)
- ✅ **Development/testing** with public endpoints
- ✅ **IoT remote access** to devices at home

### Example Use Case

```bash
# Client automatically gets IPv6: 2a11:8083:11:13f0::2

# Start a web server on your laptop
python3 -m http.server 8080

# Access from anywhere on the internet
curl http://[2a11:8083:11:13f0::2]:8080
```

**No port forwarding. No NAT. Direct public access.**

### Quick Setup

1. **Enable in `.env`:**
   ```bash
   WG_IPV6_ENABLED=True
   WG_IPV6_SUBNET=2a11:8083:11:13f0::/64
   IPV6_PUBLIC_ROUTING=True
   ```

2. **Create IPv6 profile** (e.g., "Full Tunnel + Services")
3. **Add client** - automatically gets IPv4 + IPv6
4. **Host anything** - services are publicly accessible

📖 **See [IPv6_SERVICE_HOSTING.md](IPv6_SERVICE_HOSTING.md) for complete guide**

## 🔐 Security Features

- **Password Hashing**: bcrypt with salts
- **2FA**: Time-based One-Time Passwords (TOTP)
- **Session Management**: Secure session handling with Redis
- **IP Whitelisting**: Restrict access by IP
- **HTTPS**: TLS 1.2+ encryption
- **Audit Logging**: Complete activity tracking
- **Auto Logout**: Configurable inactivity timeout
- **Secure Headers**: HSTS, CSP, XSS protection

> **IPv6 Security Note:** When hosting public services, always use firewalls on client devices to restrict access to only necessary ports.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [WireGuard](https://www.wireguard.com/) - Fast, modern VPN protocol
- [Flask](https://flask.palletsprojects.com/) - Lightweight web framework
- [Chart.js](https://www.chartjs.org/) - Beautiful charts

## ⚠️ Disclaimer

This software is provided "as is" without warranty of any kind. Use at your own risk. Always test in a non-production environment first.

## 📞 Support

- **Issues**: Use GitHub Issues for bug reports
- **Documentation**: See [DEPLOYMENT.md](DEPLOYMENT.md)
- **Security**: Report security issues privately

## 🗺️ Roadmap

- [ ] Multi-admin support
- [ ] Email notifications
- [ ] Advanced analytics
- [ ] Client groups
- [ ] API access
- [ ] Docker deployment
- [ ] Multi-server support

## 📸 Screenshots

### Dashboard
View overall system statistics, connected clients, and recent activity.

### Client Management
Easily add, remove, and manage VPN clients with detailed information.

### QR Code Generation
Instant mobile setup by scanning QR codes.

### Usage Tracking
Monitor bandwidth usage with detailed charts and statistics.

### Profiles
Create and manage connection templates for different use cases.

---

Made with ❤️ for secure VPN management
