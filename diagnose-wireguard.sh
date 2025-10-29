#!/bin/bash
# WireGuard Diagnostics Script

echo "======================================"
echo "WireGuard Service Diagnostics"
echo "======================================"
echo ""

echo "1. Checking WireGuard installation..."
if command -v wg &> /dev/null; then
    echo "   ✅ WireGuard installed"
    wg version
else
    echo "   ❌ WireGuard NOT installed"
fi
echo ""

echo "2. Checking WireGuard service status..."
systemctl status wg-quick@wg0 --no-pager
echo ""

echo "3. Checking if interface exists..."
if ip link show wg0 &> /dev/null; then
    echo "   ✅ Interface wg0 exists"
    ip addr show wg0
else
    echo "   ❌ Interface wg0 does NOT exist"
fi
echo ""

echo "4. Checking config file..."
if [ -f /etc/wireguard/wg0.conf ]; then
    echo "   ✅ Config file exists at /etc/wireguard/wg0.conf"
    echo "   Permissions:"
    ls -la /etc/wireguard/wg0.conf
else
    echo "   ❌ Config file NOT found at /etc/wireguard/wg0.conf"
fi
echo ""

echo "5. Checking if WireGuard module is loaded..."
if lsmod | grep -q wireguard; then
    echo "   ✅ WireGuard kernel module loaded"
else
    echo "   ❌ WireGuard kernel module NOT loaded"
    echo "   Attempting to load module..."
    modprobe wireguard && echo "   ✅ Module loaded successfully" || echo "   ❌ Failed to load module"
fi
echo ""

echo "6. Checking systemd service file..."
if [ -f /etc/systemd/system/wg-quick@.service ] || [ -f /lib/systemd/system/wg-quick@.service ]; then
    echo "   ✅ Service file exists"
else
    echo "   ❌ Service file NOT found"
fi
echo ""

echo "7. Checking journal logs for errors..."
echo "   Recent errors:"
journalctl -u wg-quick@wg0 -n 20 --no-pager
echo ""

echo "8. Network interfaces..."
ip addr show
echo ""

echo "======================================"
echo "Diagnostic complete!"
echo "======================================"
echo ""
echo "Common fixes:"
echo "1. If config missing: Run installation script"
echo "2. If service disabled: sudo systemctl enable wg-quick@wg0"
echo "3. If service failed: sudo systemctl start wg-quick@wg0"
echo "4. If permission errors: sudo chmod 600 /etc/wireguard/wg0.conf"
echo "5. If module not loaded: sudo modprobe wireguard"
