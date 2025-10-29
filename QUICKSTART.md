# 🚀 Quick Start Guide

Get WireGuard Manager up and running in minutes!

## One-Command Installation

```bash
curl -sSL https://raw.githubusercontent.com/yourusername/wireguard-manager/main/deployment/install.sh | sudo bash
```

## Step-by-Step Installation

### 1. Prepare Your Server

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Download WireGuard Manager
git clone https://github.com/yourusername/wireguard-manager.git
cd wireguard-manager
```

### 2. Run Installer

```bash
sudo bash deployment/install.sh
```

The installer will ask you:
- **Domain name**: Enter your domain or press Enter to use IP
- **WireGuard server IP**: Default is 10.0.0.1 (press Enter)
- **WireGuard port**: Default is 51820 (press Enter)

### 3. Complete Web Setup

1. Open your browser and go to the URL shown at the end of installation
2. **Create Admin Password** (minimum 8 characters)
3. **Set Up 2FA**:
   - Open your authenticator app (Google Authenticator, Authy, etc.)
   - Scan the QR code
   - Enter the 6-digit code
   - **IMPORTANT**: Save the secret key in a safe place!

### 4. Create First Profile

Profiles define how clients connect to your VPN.

**Full Tunnel (all traffic through VPN)**:
- Name: `Full Tunnel`
- Description: `Route all internet traffic through VPN`
- Allowed IPs: `0.0.0.0/0,::/0`
- DNS: `1.1.1.1,1.0.0.1`

**Split Tunnel (only private networks)**:
- Name: `Split Tunnel`
- Description: `Only private networks through VPN`
- Allowed IPs: `10.0.0.0/8,192.168.0.0/16`
- DNS: `1.1.1.1,1.0.0.1`

### 5. Add Your First Client

1. Click **"Clients"** → **"Add New Client"**
2. Enter client details:
   - **Name**: e.g., "John's iPhone"
   - **Profile**: Select the profile you created
   - **Expiry**: Optional, e.g., 30 days
   - **Notes**: Optional notes
3. Click **"Create Client"**

### 6. Connect Your Device

**Desktop (Windows/Mac/Linux)**:
1. Install [WireGuard Client](https://www.wireguard.com/install/)
2. Click **"Download Config"** on the client details page
3. Import the `.conf` file into WireGuard
4. Click **"Activate"**

**Mobile (iOS/Android)**:
1. Install WireGuard app from App Store/Play Store
2. Open the app
3. Tap **"+"** → **"Create from QR code"**
4. Scan the QR code from the client details page
5. Tap **"Activate"**

## 🎉 You're Done!

Your VPN is now active! Check the dashboard to see:
- Connected clients
- Data usage
- System status

## Next Steps

### Customize Settings

Go to **Settings** to:
- Change admin password
- Configure automatic backups
- Restart WireGuard if needed

### Create More Profiles

Create different profiles for different use cases:
- Gaming (low latency)
- Streaming (specific regions)
- Privacy (full tunnel with DNS blocking)

### Add More Clients

Add VPN access for:
- Family members
- Devices (phones, tablets, laptops)
- Smart home devices

### Monitor Usage

Check **Usage** to:
- See bandwidth per client
- View historical data
- Identify heavy users

### Review Audit Logs

Check **Audit Log** to:
- See all actions taken
- Monitor login attempts
- Track configuration changes

## Common Use Cases

### Personal VPN

```
Profile: Full Tunnel
- Routes all traffic through VPN
- Encrypts all internet activity
- Hides your IP address
```

### Access Home Network

```
Profile: Home Access
- Allowed IPs: 192.168.1.0/24
- Access home devices remotely
- Stream local media
```

### Bypass Geo-Restrictions

```
Profile: Region Bypass
- Full tunnel with specific DNS
- Access region-locked content
- Maintain privacy
```

## Troubleshooting

### Can't connect to web interface?

```bash
# Check if service is running
sudo systemctl status wireguard-manager

# Check if Nginx is running
sudo systemctl status nginx

# View logs
sudo journalctl -u wireguard-manager -n 50
```

### VPN connection not working?

```bash
# Check WireGuard status
sudo wg show

# Restart WireGuard
sudo systemctl restart wg-quick@wg0
```

### Forgot admin password?

```bash
# Reset (requires server access)
cd /opt/wireguard-manager
sudo rm data/settings.json
# Visit web interface to set up again
```

## Tips & Tricks

### 1. Set Client Expiry for Guests

When adding temporary clients, set an expiry date. They'll automatically be disabled when expired.

### 2. Use Meaningful Names

Name clients clearly: "John-iPhone", "Jane-Laptop", "Guest-Device"

### 3. Regular Backups

Download backups regularly from **Settings** → **Backup & Restore**

### 4. Monitor Audit Logs

Check audit logs weekly for suspicious activity

### 5. Test Your VPN

After setting up, test your VPN:
- Check IP: https://whatismyip.com
- DNS leak test: https://dnsleaktest.com
- Speed test: https://speedtest.net

## Getting Help

- **Documentation**: See [DEPLOYMENT.md](DEPLOYMENT.md)
- **Issues**: Check logs and troubleshooting guide
- **Updates**: Keep system and app updated

## Security Reminders

✅ Use strong admin password  
✅ Keep 2FA enabled  
✅ Save backup codes  
✅ Enable automatic backups  
✅ Use HTTPS only  
✅ Monitor audit logs  
✅ Update regularly  

---

Happy VPN-ing! 🔐
