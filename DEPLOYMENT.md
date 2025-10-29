# WireGuard Manager - Deployment Guide

Complete guide to deploy WireGuard Manager on a VPS.

## 📋 Prerequisites

- **VPS/Server** running Ubuntu 20.04/22.04 or Debian 11/12
- **Root access** or sudo privileges
- **Public IP address** or domain name
- **Minimum specs**: 1 CPU, 1GB RAM, 10GB storage

## 🚀 Quick Install (Automated)

The easiest way to install WireGuard Manager:

```bash
# 1. Download the project
git clone <your-repo> wireguard-manager
cd wireguard-manager

# 2. Run the installation script
sudo bash deployment/install.sh
```

The script will:
- Install all dependencies (Python, WireGuard, Redis, Nginx)
- Configure WireGuard interface
- Set up the web application
- Configure Nginx with optional SSL
- Configure firewall rules

## 📝 Manual Installation

If you prefer manual installation or need to customize:

### Step 1: Install System Dependencies

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install dependencies
sudo apt install -y python3 python3-pip python3-venv wireguard wireguard-tools \
    redis-server nginx certbot python3-certbot-nginx git curl ufw
```

### Step 2: Configure IP Forwarding

```bash
# Enable IPv4 forwarding
sudo sed -i 's/#net.ipv4.ip_forward=1/net.ipv4.ip_forward=1/' /etc/sysctl.conf

# Enable IPv6 forwarding (if using IPv6)
sudo sed -i 's/#net.ipv6.conf.all.forwarding=1/net.ipv6.conf.all.forwarding=1/' /etc/sysctl.conf

# Apply changes
sudo sysctl -p
```

### Step 3: Set Up WireGuard

```bash
# Generate WireGuard keys
cd /etc/wireguard
sudo wg genkey | sudo tee privatekey | wg pubkey | sudo tee publickey

# Create WireGuard configuration
sudo nano /etc/wireguard/wg0.conf
```

Add this configuration (replace with your details):

**IPv4 Only:**
```ini
[Interface]
Address = 10.0.0.1/24
ListenPort = 51820
PrivateKey = <your-private-key>
PostUp = iptables -A FORWARD -i %i -j ACCEPT; iptables -A FORWARD -o %i -j ACCEPT; iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE
PostDown = iptables -D FORWARD -i %i -j ACCEPT; iptables -D FORWARD -o %i -j ACCEPT; iptables -t nat -D POSTROUTING -o eth0 -j MASQUERADE
```

**Dual Stack (IPv4 + IPv6):**
```ini
[Interface]
Address = 10.0.0.1/24, 2a11:8083:11:13f0::1/64
ListenPort = 51820
PrivateKey = <your-private-key>
PostUp = iptables -A FORWARD -i %i -j ACCEPT; iptables -A FORWARD -o %i -j ACCEPT; iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE; ip6tables -A FORWARD -i %i -j ACCEPT; ip6tables -A FORWARD -o %i -j ACCEPT
PostDown = iptables -D FORWARD -i %i -j ACCEPT; iptables -D FORWARD -o %i -j ACCEPT; iptables -t nat -D POSTROUTING -o eth0 -j MASQUERADE; ip6tables -D FORWARD -i %i -j ACCEPT; ip6tables -D FORWARD -o %i -j ACCEPT
```

> **Note:** For IPv6, replace `2a11:8083:11:13f0::1/64` with your actual /64 subnet. See [IPv6_SERVICE_HOSTING.md](IPv6_SERVICE_HOSTING.md) for complete IPv6 setup.

```bash
# Set proper permissions
sudo chmod 600 /etc/wireguard/wg0.conf
sudo chmod 600 /etc/wireguard/privatekey

# Enable and start WireGuard
sudo systemctl enable wg-quick@wg0
sudo systemctl start wg-quick@wg0

# Verify it's running
sudo wg show
```

### Step 4: Install Application

```bash
# Create application directory
sudo mkdir -p /opt/wireguard-manager
cd /opt/wireguard-manager

# Copy application files
sudo cp -r /path/to/your/files/* /opt/wireguard-manager/

# Create virtual environment
sudo python3 -m venv venv
sudo venv/bin/pip install --upgrade pip

# Install dependencies
sudo venv/bin/pip install -r requirements.txt
sudo venv/bin/pip install gunicorn
```

### Step 5: Configure Application

```bash
# Copy example environment file
sudo cp .env.example .env

# Edit configuration
sudo nano .env
```

Update these critical settings:

```bash
SECRET_KEY=<generate-random-key>
WG_SERVER_IP=10.0.0.1
WG_SERVER_PORT=51820
WG_SERVER_PUBLIC_KEY=<your-public-key>
WG_SERVER_PRIVATE_KEY=<your-private-key>
SERVER_PUBLIC_IP=<your-vps-ip>
```

Generate a secret key:
```bash
python3 -c 'import secrets; print(secrets.token_hex(32))'
```

```bash
# Create data directories
sudo mkdir -p data/clients data/profiles data/usage data/audit
sudo mkdir -p backups logs

# Set ownership
sudo chown -R www-data:www-data /opt/wireguard-manager
sudo chmod -R 750 /opt/wireguard-manager
```

### Step 6: Allow www-data to Run WireGuard Commands

```bash
# Create sudoers file
sudo nano /etc/sudoers.d/wireguard-manager
```

Add:
```
www-data ALL=(ALL) NOPASSWD: /usr/bin/wg
www-data ALL=(ALL) NOPASSWD: /usr/bin/wg-quick
```

```bash
# Set permissions
sudo chmod 440 /etc/sudoers.d/wireguard-manager
```

### Step 7: Set Up Systemd Service

```bash
# Copy service file
sudo cp deployment/wireguard-manager.service /etc/systemd/system/

# Reload systemd
sudo systemctl daemon-reload

# Enable and start service
sudo systemctl enable wireguard-manager
sudo systemctl start wireguard-manager

# Check status
sudo systemctl status wireguard-manager
```

### Step 8: Configure Nginx

```bash
# Copy nginx configuration
sudo cp deployment/nginx.conf /etc/nginx/sites-available/wireguard-manager

# Update domain name
sudo sed -i 's/your-domain.com/YOUR_DOMAIN/g' /etc/nginx/sites-available/wireguard-manager

# Enable site
sudo ln -s /etc/nginx/sites-available/wireguard-manager /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default

# Test configuration
sudo nginx -t

# Restart Nginx
sudo systemctl restart nginx
```

### Step 9: Set Up SSL (Optional but Recommended)

```bash
# Install SSL certificate with Let's Encrypt
sudo certbot --nginx -d your-domain.com

# Test auto-renewal
sudo certbot renew --dry-run
```

### Step 10: Configure Firewall

```bash
# Enable UFW
sudo ufw enable

# Allow necessary ports
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 80/tcp    # HTTP
sudo ufw allow 443/tcp   # HTTPS
sudo ufw allow 51820/udp # WireGuard

# Allow routing (important for VPN)
sudo ufw default allow routed

# Check status
sudo ufw status
```

**For IPv6 service hosting:**
```bash
# IPv6 is automatically allowed through WireGuard interface
# No additional ports needed - clients are directly routable
# Client firewalls should be configured individually
```

## 🔐 Initial Setup

1. **Access the Web Interface**
   - Navigate to `https://your-domain.com`
   - Or `http://your-server-ip` if not using SSL

2. **Initial Setup**
   - Create admin password (minimum 8 characters)
   - Click "Complete Setup"

3. **Configure 2FA**
   - Scan QR code with authenticator app (Google Authenticator, Authy, etc.)
   - Enter 6-digit code to verify
   - **Save the secret key** in a secure location

4. **Login**
   - Username: `admin`
   - Password: your password
   - 2FA token: from authenticator app

5. **Create First Profile**
   - Go to "Profiles" → "Create Profile"
   - Example full tunnel:
     - Name: Full Tunnel
     - Allowed IPs: `0.0.0.0/0,::/0`
     - DNS: `1.1.1.1,1.0.0.1`

6. **Add First Client**
   - Go to "Clients" → "Add New Client"
   - Enter name, select profile
   - Optionally set expiry
   - Download config or scan QR code

## 🔧 Configuration Options

### Environment Variables (.env)

```bash
# Flask Configuration
SECRET_KEY=                    # Random secret key
FLASK_ENV=production          # production or development

# Admin Credentials
ADMIN_USERNAME=admin          # Admin username
ADMIN_PASSWORD_HASH=          # Set during initial setup

# WireGuard IPv4
WG_INTERFACE=wg0             # WireGuard interface name
WG_SERVER_IP=10.0.0.1        # Server VPN IP
WG_SERVER_PORT=51820         # WireGuard port
WG_SERVER_PUBLIC_KEY=        # Server public key
WG_SERVER_PRIVATE_KEY=       # Server private key
SERVER_PUBLIC_IP=            # Server's public IP or domain

# WireGuard IPv6 (Optional - for service hosting)
WG_IPV6_ENABLED=False        # Enable IPv6 support
WG_IPV6_SUBNET=              # Your /64 subnet (e.g., 2a11:8083:11:13f0::/64)
WG_SERVER_IPV6=              # Server IPv6 address (e.g., 2a11:8083:11:13f0::1)
IPV6_PUBLIC_ROUTING=False    # Enable public IPv6 routing for services

# Security
SESSION_TIMEOUT=1800         # Session timeout in seconds (30 min)
MAX_LOGIN_ATTEMPTS=5         # Max failed login attempts
IP_WHITELIST=                # Comma-separated IPs (empty = allow all)
ENABLE_2FA=True             # Enable/disable 2FA

# Backup
AUTO_BACKUP_ENABLED=True     # Enable automatic backups
AUTO_BACKUP_HOUR=2          # Hour for daily backup (0-23)
BACKUP_RETENTION_DAYS=30    # Keep backups for X days
```

> **IPv6 Service Hosting:** When `WG_IPV6_ENABLED=True` and `IPV6_PUBLIC_ROUTING=True`, each client gets a publicly routable IPv6 address. See [IPv6_SERVICE_HOSTING.md](IPv6_SERVICE_HOSTING.md) for complete guide.

### Security Recommendations

1. **Use Strong Passwords**
   - Minimum 12 characters
   - Mix of uppercase, lowercase, numbers, symbols

2. **Enable 2FA**
   - Always keep 2FA enabled
   - Store backup codes securely

3. **IP Whitelist** (Optional)
   ```bash
   IP_WHITELIST=1.2.3.4,5.6.7.8
   ```

4. **HTTPS Only**
   - Always use SSL/TLS in production
   - Redirect HTTP to HTTPS

5. **Regular Backups**
   - Enable automatic backups
   - Download backups to external storage
   - Test restore procedure

## 🔄 Updating the Application

```bash
# Stop the service
sudo systemctl stop wireguard-manager

# Backup current version
sudo cp -r /opt/wireguard-manager /opt/wireguard-manager.backup

# Pull latest changes
cd /opt/wireguard-manager
sudo git pull

# Update dependencies
sudo venv/bin/pip install -r requirements.txt

# Restart service
sudo systemctl start wireguard-manager

# Check status
sudo systemctl status wireguard-manager
```

## 🐛 Troubleshooting

### Service won't start

```bash
# Check service logs
sudo journalctl -u wireguard-manager -n 50 --no-pager

# Check Python errors
sudo tail -f /opt/wireguard-manager/logs/wireguard_manager.log

# Check permissions
sudo chown -R www-data:www-data /opt/wireguard-manager
```

### WireGuard not working

```bash
# Check WireGuard status
sudo wg show

# Check interface
ip a show wg0

# Restart WireGuard
sudo systemctl restart wg-quick@wg0

# Check logs
sudo journalctl -u wg-quick@wg0 -n 50
```

### Can't add/remove clients

```bash
# Verify www-data can run wg commands
sudo -u www-data wg show

# Check sudoers configuration
sudo cat /etc/sudoers.d/wireguard-manager
```

### Redis connection issues

```bash
# Check Redis status
sudo systemctl status redis

# Restart Redis
sudo systemctl restart redis

# Test connection
redis-cli ping
```

### Nginx errors

```bash
# Check Nginx configuration
sudo nginx -t

# Check Nginx logs
sudo tail -f /var/log/nginx/error.log

# Restart Nginx
sudo systemctl restart nginx
```

### IPv6 not working

```bash
# Check VPS has IPv6
ip -6 addr show

# Test IPv6 connectivity
ping6 -c 4 google.com
curl -6 https://api64.ipify.org

# Check WireGuard interface has IPv6
ip -6 addr show wg0

# Verify IPv6 forwarding enabled
sysctl net.ipv6.conf.all.forwarding

# Check ip6tables rules
sudo ip6tables -L -n -v

# Test from client
# After connecting, run on client:
curl -6 https://api64.ipify.org
# Should show your VPS IPv6 or client's public IPv6
```

### IPv6 services not accessible

```bash
# On VPS - verify client has IPv6 assigned
sudo wg show

# Test from VPS to client
ping6 -c 4 2a11:8083:11:13f0::2

# Check service is listening on IPv6
sudo netstat -tulpn | grep -E ':80|:443'
# Should show :::80 or :::443 for IPv6

# On client - check firewall
sudo ufw status
# Make sure required ports are open

# Test service binding
sudo ss -tulpn | grep LISTEN
```

## 📊 Monitoring

### Check Application Status

```bash
# Service status
sudo systemctl status wireguard-manager

# Live logs
sudo journalctl -u wireguard-manager -f

# Application logs
sudo tail -f /opt/wireguard-manager/logs/wireguard_manager.log
```

### Check WireGuard Status

```bash
# Show all peers
sudo wg show

# Detailed output
sudo wg show all dump
```

### Check System Resources

```bash
# CPU and memory
top

# Disk usage
df -h

# Network traffic
vnstat -l
```

## 🔐 Security Best Practices

1. **Change default admin username**
   - Edit `.env` before first setup

2. **Keep system updated**
   ```bash
   sudo apt update && sudo apt upgrade -y
   ```

3. **Monitor audit logs**
   - Check regularly in web interface
   - Look for suspicious activity

4. **Limit SSH access**
   ```bash
   # Use SSH keys only
   sudo nano /etc/ssh/sshd_config
   # Set: PasswordAuthentication no
   ```

5. **Enable fail2ban**
   ```bash
   sudo apt install fail2ban
   sudo systemctl enable fail2ban
   ```

## 📱 Client Setup

### Desktop (Windows, macOS, Linux)

1. Install [WireGuard Client](https://www.wireguard.com/install/)
2. Download config file from web interface
3. Import config into WireGuard client
4. Activate connection

### Mobile (iOS, Android)

1. Install WireGuard app from App Store/Play Store
2. Scan QR code from client details page
3. Activate connection

## 🔄 Backup & Restore

### Manual Backup

```bash
# From Settings page in web interface
# Or manually:
sudo -u www-data tar -czf backup-$(date +%Y%m%d).tar.gz -C /opt/wireguard-manager data
```

### Restore

```bash
# From Settings page in web interface
# Or manually:
sudo systemctl stop wireguard-manager
sudo tar -xzf backup-YYYYMMDD.tar.gz -C /opt/wireguard-manager
sudo chown -R www-data:www-data /opt/wireguard-manager/data
sudo systemctl start wireguard-manager
```

## 📞 Support

For issues and questions:
- Check this documentation first
- Review application logs
- Check WireGuard status
- Verify configuration files

## 📄 License

[Your License Here]
