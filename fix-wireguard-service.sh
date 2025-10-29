#!/bin/bash
# WireGuard Service Fix Script

set -e

echo "======================================"
echo "WireGuard Service Fix Script"
echo "======================================"
echo ""

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo "❌ Please run as root (use sudo)"
    exit 1
fi

echo "1. Checking if WireGuard is installed..."
if ! command -v wg &> /dev/null; then
    echo "   Installing WireGuard..."
    apt update
    apt install -y wireguard wireguard-tools
fi
echo "   ✅ WireGuard installed"
echo ""

echo "2. Checking kernel module..."
if ! lsmod | grep -q wireguard; then
    echo "   Loading WireGuard module..."
    modprobe wireguard
fi
echo "   ✅ Module loaded"
echo ""

echo "3. Checking config file..."
if [ ! -f /etc/wireguard/wg0.conf ]; then
    echo "   ❌ Config file missing!"
    echo "   Creating basic config template..."
    
    # Generate server keys
    umask 077
    SERVER_PRIVATE_KEY=$(wg genkey)
    SERVER_PUBLIC_KEY=$(echo "$SERVER_PRIVATE_KEY" | wg pubkey)
    
    cat > /etc/wireguard/wg0.conf << EOF
[Interface]
Address = 10.0.0.1/24
ListenPort = 51820
PrivateKey = $SERVER_PRIVATE_KEY
PostUp = iptables -A FORWARD -i wg0 -j ACCEPT; iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE
PostDown = iptables -D FORWARD -i wg0 -j ACCEPT; iptables -t nat -D POSTROUTING -o eth0 -j MASQUERADE

# Clients will be added here by the management interface
EOF
    
    echo "   ✅ Config created"
    echo "   Server Public Key: $SERVER_PUBLIC_KEY"
    echo "   ** SAVE THIS KEY - You need it for config.py **"
    echo ""
else
    echo "   ✅ Config exists"
fi
echo ""

echo "4. Setting permissions..."
chmod 600 /etc/wireguard/wg0.conf
chown root:root /etc/wireguard/wg0.conf
echo "   ✅ Permissions set"
echo ""

echo "5. Enable IP forwarding..."
sysctl -w net.ipv4.ip_forward=1
sysctl -w net.ipv6.conf.all.forwarding=1
echo "net.ipv4.ip_forward=1" >> /etc/sysctl.conf
echo "net.ipv6.conf.all.forwarding=1" >> /etc/sysctl.conf
echo "   ✅ IP forwarding enabled"
echo ""

echo "6. Enabling WireGuard service..."
systemctl enable wg-quick@wg0
echo "   ✅ Service enabled"
echo ""

echo "7. Starting WireGuard service..."
systemctl start wg-quick@wg0
echo "   ✅ Service started"
echo ""

echo "8. Checking status..."
systemctl status wg-quick@wg0 --no-pager
echo ""

echo "======================================"
echo "WireGuard service should now be running!"
echo "======================================"
echo ""

# Show interface status
if wg show wg0 &> /dev/null; then
    echo "✅ WireGuard interface is UP:"
    wg show wg0
else
    echo "⚠️  Interface status unclear, check logs:"
    journalctl -u wg-quick@wg0 -n 20 --no-pager
fi
