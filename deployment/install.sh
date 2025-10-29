#!/bin/bash

# WireGuard Manager Installation Script
# For Ubuntu 20.04/22.04 or Debian 11/12

set -e

echo "=================================="
echo "WireGuard Manager Installation"
echo "=================================="
echo ""

# Check if running as root
if [[ $EUID -ne 0 ]]; then
   echo "This script must be run as root (use sudo)" 
   exit 1
fi

# Get the directory where the script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
SOURCE_DIR="$(dirname "$SCRIPT_DIR")"

echo "Installation source: $SOURCE_DIR"
echo ""

# Get server public IP
echo "Detecting server public IP..."
SERVER_IP=$(curl -s https://api.ipify.org)
echo "Detected IPv4: $SERVER_IP"

# Detect IPv6
SERVER_IPV6=$(curl -s https://api64.ipify.org 2>/dev/null || echo "")
if [ -n "$SERVER_IPV6" ]; then
    echo "Detected IPv6: $SERVER_IPV6"
else
    echo "No IPv6 detected"
fi
echo ""

# Prompt for domain or IP
read -p "Enter your domain name (or press Enter to use IP $SERVER_IP): " DOMAIN
if [ -z "$DOMAIN" ]; then
    DOMAIN=$SERVER_IP
    USE_LETSENCRYPT=false
else
    USE_LETSENCRYPT=true
fi

# Prompt for WireGuard settings
read -p "Enter WireGuard server IP (default: 10.0.0.1): " WG_SERVER_IP
WG_SERVER_IP=${WG_SERVER_IP:-10.0.0.1}

read -p "Enter WireGuard port (default: 51820): " WG_PORT
WG_PORT=${WG_PORT:-51820}

# IPv6 Configuration
echo ""
echo "=== IPv6 Configuration ==="
if [ -n "$SERVER_IPV6" ]; then
    read -p "Enable IPv6 for WireGuard? (Y/n): " ENABLE_IPV6
    ENABLE_IPV6=${ENABLE_IPV6:-Y}
    
    if [[ $ENABLE_IPV6 =~ ^[Yy]$ ]]; then
        read -p "Enter your IPv6 /64 subnet (e.g., 2a11:8083:11:13f0::/64): " IPV6_SUBNET
        if [ -z "$IPV6_SUBNET" ]; then
            echo "No IPv6 subnet provided, IPv6 will be disabled"
            ENABLE_IPV6=false
            IPV6_SUBNET=""
            WG_SERVER_IPV6=""
        else
            # Extract network prefix and create server IPv6
            IPV6_PREFIX=$(echo $IPV6_SUBNET | cut -d':' -f1-4)
            WG_SERVER_IPV6="${IPV6_PREFIX}::1"
            echo "Server IPv6 will be: $WG_SERVER_IPV6"
            
            read -p "Enable public IPv6 routing for hosting services? (Y/n): " IPV6_ROUTING
            IPV6_ROUTING=${IPV6_ROUTING:-Y}
        fi
    else
        ENABLE_IPV6=false
        IPV6_SUBNET=""
        WG_SERVER_IPV6=""
    fi
else
    echo "IPv6 not available on this server"
    ENABLE_IPV6=false
    IPV6_SUBNET=""
    WG_SERVER_IPV6=""
fi

echo ""
echo "Installing system dependencies..."
apt update
apt install -y python3 python3-pip python3-venv wireguard wireguard-tools \
    redis-server nginx certbot python3-certbot-nginx git curl

# Enable IP forwarding
echo "Configuring IP forwarding..."
sed -i 's/#net.ipv4.ip_forward=1/net.ipv4.ip_forward=1/' /etc/sysctl.conf
sed -i 's/#net.ipv6.conf.all.forwarding=1/net.ipv6.conf.all.forwarding=1/' /etc/sysctl.conf
sysctl -p

# Set up WireGuard
echo "Setting up WireGuard..."
if [ ! -f /etc/wireguard/wg0.conf ]; then
    cd /etc/wireguard
    wg genkey | tee privatekey | wg pubkey > publickey
    
    SERVER_PRIVATE_KEY=$(cat privatekey)
    SERVER_PUBLIC_KEY=$(cat publickey)
    
    # Create basic WireGuard config
    cat > /etc/wireguard/wg0.conf << EOF
[Interface]
Address = $WG_SERVER_IP/24$([ -n "$WG_SERVER_IPV6" ] && echo ", $WG_SERVER_IPV6/64")
ListenPort = $WG_PORT
PrivateKey = $SERVER_PRIVATE_KEY
PostUp = iptables -A FORWARD -i %i -j ACCEPT; iptables -A FORWARD -o %i -j ACCEPT; iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE$([ -n "$WG_SERVER_IPV6" ] && echo "; ip6tables -A FORWARD -i %i -j ACCEPT; ip6tables -A FORWARD -o %i -j ACCEPT")
PostDown = iptables -D FORWARD -i %i -j ACCEPT; iptables -D FORWARD -o %i -j ACCEPT; iptables -t nat -D POSTROUTING -o eth0 -j MASQUERADE$([ -n "$WG_SERVER_IPV6" ] && echo "; ip6tables -D FORWARD -i %i -j ACCEPT; ip6tables -D FORWARD -o %i -j ACCEPT")
EOF
    
    chmod 600 /etc/wireguard/wg0.conf
    chmod 600 privatekey
    
    echo "WireGuard keys generated"
else
    echo "WireGuard already configured, reading existing keys..."
    SERVER_PRIVATE_KEY=$(grep PrivateKey /etc/wireguard/wg0.conf | cut -d' ' -f3)
    SERVER_PUBLIC_KEY=$(wg pubkey < /etc/wireguard/privatekey)
fi

# Enable and start WireGuard
systemctl enable wg-quick@wg0
systemctl start wg-quick@wg0 || systemctl restart wg-quick@wg0

# Set up application
echo "Setting up WireGuard Manager application..."

# Copy application files to /opt/wireguard-manager
if [ "$SOURCE_DIR" != "/opt/wireguard-manager" ]; then
    echo "Copying files from $SOURCE_DIR to /opt/wireguard-manager..."
    mkdir -p /opt/wireguard-manager
    cp -r "$SOURCE_DIR"/* /opt/wireguard-manager/
else
    echo "Already in /opt/wireguard-manager"
fi

cd /opt/wireguard-manager

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
pip install --upgrade pip
pip install gunicorn
if [ -f requirements.txt ]; then
    pip install -r requirements.txt
fi

# Create .env file
cat > /opt/wireguard-manager/.env << EOF
SECRET_KEY=$(python3 -c 'import secrets; print(secrets.token_hex(32))')
FLASK_ENV=production
FLASK_DEBUG=False

# Admin Credentials
ADMIN_USERNAME=admin
ADMIN_PASSWORD_HASH=

# WireGuard Configuration
WG_INTERFACE=wg0
WG_SERVER_IP=$WG_SERVER_IP
WG_SERVER_PORT=$WG_PORT
WG_SERVER_PUBLIC_KEY=$SERVER_PUBLIC_KEY
WG_SERVER_PRIVATE_KEY=$SERVER_PRIVATE_KEY
SERVER_PUBLIC_IP=$SERVER_IP
$([ -n "$SERVER_IPV6" ] && echo "SERVER_PUBLIC_IPV6=$SERVER_IPV6")

# IPv6 Configuration
$([ "$ENABLE_IPV6" = "true" ] || [ "$ENABLE_IPV6" = "Y" ] || [ "$ENABLE_IPV6" = "y" ] && echo "WG_IPV6_ENABLED=True" || echo "WG_IPV6_ENABLED=False")
$([ -n "$IPV6_SUBNET" ] && echo "WG_IPV6_SUBNET=$IPV6_SUBNET")
$([ -n "$WG_SERVER_IPV6" ] && echo "WG_SERVER_IPV6=$WG_SERVER_IPV6")
$([ "$IPV6_ROUTING" = "Y" ] || [ "$IPV6_ROUTING" = "y" ] && echo "IPV6_PUBLIC_ROUTING=True" || echo "IPV6_PUBLIC_ROUTING=False")

# Security
SESSION_TIMEOUT=1800
ENABLE_2FA=True

# Redis
REDIS_URL=redis://localhost:6379/0

# Directories
DATA_DIR=/opt/wireguard-manager/data
BACKUP_DIR=/opt/wireguard-manager/backups

# Backup
AUTO_BACKUP_ENABLED=True
AUTO_BACKUP_HOUR=2
BACKUP_RETENTION_DAYS=30
EOF

# Create directories
mkdir -p /opt/wireguard-manager/data /opt/wireguard-manager/backups /opt/wireguard-manager/logs
mkdir -p /opt/wireguard-manager/data/clients /opt/wireguard-manager/data/profiles /opt/wireguard-manager/data/usage /opt/wireguard-manager/data/audit

# Set permissions
chown -R www-data:www-data /opt/wireguard-manager
chmod -R 750 /opt/wireguard-manager

# Allow www-data to run wg commands
cat > /etc/sudoers.d/wireguard-manager << EOF
www-data ALL=(ALL) NOPASSWD: /usr/bin/wg
www-data ALL=(ALL) NOPASSWD: /usr/bin/wg-quick
EOF

chmod 440 /etc/sudoers.d/wireguard-manager

# Set up systemd service
echo "Setting up systemd service..."
if [ -f /opt/wireguard-manager/deployment/wireguard-manager.service ]; then
    cp /opt/wireguard-manager/deployment/wireguard-manager.service /etc/systemd/system/
    systemctl daemon-reload
    systemctl enable wireguard-manager
    systemctl start wireguard-manager
else
    echo "ERROR: wireguard-manager.service file not found!"
    exit 1
fi

# Configure Nginx
echo "Configuring Nginx..."

# Create HTTP-only config first
cat > /etc/nginx/sites-available/wireguard-manager << 'EOF'
server {
    listen 80;
    server_name DOMAIN_PLACEHOLDER;
    
    # Logging
    access_log /var/log/nginx/wireguard-manager-access.log;
    error_log /var/log/nginx/wireguard-manager-error.log;
    
    # Proxy to Flask app
    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
    
    # Static files (if any)
    location /static {
        alias /opt/wireguard-manager/static;
        expires 1d;
        add_header Cache-Control "public, immutable";
    }
    
    # Deny access to sensitive files
    location ~ /\. {
        deny all;
    }
}
EOF

sed -i "s/DOMAIN_PLACEHOLDER/$DOMAIN/g" /etc/nginx/sites-available/wireguard-manager
ln -sf /etc/nginx/sites-available/wireguard-manager /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default

# Configure firewall BEFORE starting services
echo "Configuring firewall..."
ufw --force enable
ufw allow 22/tcp
ufw allow 80/tcp
ufw allow 443/tcp
ufw allow $WG_PORT/udp
ufw default allow routed

# Test and start Nginx
nginx -t && systemctl restart nginx

# Set up SSL if using domain
if [ "$USE_LETSENCRYPT" = true ]; then
    echo "Setting up SSL certificate..."
    certbot --nginx -d $DOMAIN --non-interactive --agree-tos --register-unsafely-without-email
    
    if [ $? -eq 0 ]; then
        echo "SSL certificate installed successfully"
        # Restart Nginx with SSL
        systemctl restart nginx
    else
        echo "WARNING: SSL certificate installation failed, continuing with HTTP only"
        echo "You can manually run: sudo certbot --nginx -d $DOMAIN"
    fi
fi

echo ""
echo "=================================="
echo "Installation Complete!"
echo "=================================="
echo ""
echo "WireGuard Manager is now installed and running."
echo ""
echo "Access the web interface at:"
if [ "$USE_LETSENCRYPT" = true ]; then
    echo "  https://$DOMAIN"
else
    echo "  http://$DOMAIN"
fi
echo ""
echo "Important Next Steps:"
echo "1. Visit the URL above to complete initial setup"
echo "2. Create your admin password"
echo "3. Set up 2FA authentication"
echo "4. Create your first connection profile"
echo "5. Add VPN clients"
echo ""
echo "WireGuard Server Details:"
echo "  Interface: wg0"
echo "  IP: $WG_SERVER_IP"
echo "  Port: $WG_PORT"
echo "  Public Key: $SERVER_PUBLIC_KEY"
echo ""
echo "Useful Commands:"
echo "  sudo systemctl status wireguard-manager  # Check app status"
echo "  sudo systemctl restart wireguard-manager # Restart app"
echo "  sudo wg show                             # Show WireGuard status"
echo "  sudo journalctl -u wireguard-manager -f  # View app logs"
echo ""
