# 🚀 Deployment to sg.gc.parthh.com

## Server Details

- **Host**: `sg.gc.parthh.com`
- **IPv4**: `172.93.186.41`
- **IPv6**: `2a11:8083:11:13f0::a`
- **IPv6 Subnet**: `2a11:8083:11:13f0::/64`
- **SSH**: `root@sg.gc.parthh.com`

## ✅ Pre-Flight Check

Your server is **perfect** for IPv6 service hosting:
- ✅ IPv6 connectivity confirmed
- ✅ /64 subnet available
- ✅ Domain configured
- ✅ SSH access ready

## 🚀 Quick Deployment

### Option 1: Direct from GitHub (Recommended)

```bash
# 1. SSH to server
ssh root@sg.gc.parthh.com

# 2. Clone repository
git clone https://github.com/parthh37/Wireguard-Manager.git
cd Wireguard-Manager

# 3. Run installer
chmod +x deployment/install.sh
sudo bash deployment/install.sh
```

**Installer will auto-detect:**
- IPv4: `172.93.186.41`
- IPv6: `2a11:8083:11:13f0::a`
- Subnet: `2a11:8083:11:13f0::/64`

### Option 2: Direct Upload

```bash
# From your local machine
scp -r "/Users/parthpatel/Downloads/Wireguard Manager" root@sg.gc.parthh.com:/opt/wireguard-manager

# SSH to server
ssh root@sg.gc.parthh.com

# Run installer
cd /opt/wireguard-manager
chmod +x deployment/install.sh
sudo bash deployment/install.sh
```

## 📋 Installation Questions

When the installer runs, answer:

```
Detected IPv4: 172.93.186.41
Detected IPv6: 2a11:8083:11:13f0::a

=== IPv6 Configuration ===
Enable IPv6 for WireGuard? (Y/n): Y
Enter your IPv6 /64 subnet: 2a11:8083:11:13f0::/64
Server IPv6 will be: 2a11:8083:11:13f0::1
Enable public IPv6 routing for hosting services? (Y/n): Y

=== Domain Configuration ===
Enter domain name (or press Enter for IP): sg.gc.parthh.com

=== SSL Certificate ===
Install SSL certificate with Let's Encrypt? (Y/n): Y
```

## 🎯 Expected Result

After installation:

1. **Access Web Interface**:
   - https://sg.gc.parthh.com

2. **Server IPs**:
   - WireGuard IPv4: `10.0.0.1/24`
   - WireGuard IPv6: `2a11:8083:11:13f0::1/64`

3. **Client IP Range**:
   - IPv4: `10.0.0.2` - `10.0.0.254`
   - IPv6: `2a11:8083:11:13f0::2` - `2a11:8083:11:13f0::ffff`

4. **Each client gets**:
   - Private IPv4 (NAT for privacy)
   - Public IPv6 (direct routing for services)

## 🧪 Testing After Install

### 1. Verify WireGuard

```bash
sudo wg show
ip -6 addr show wg0
```

### 2. Test IPv6 Connectivity

```bash
ping6 -c 4 google.com
curl -6 https://api64.ipify.org
# Should show: 2a11:8083:11:13f0::a or similar
```

### 3. Add Test Client

1. Login to https://sg.gc.parthh.com
2. Create profile: "Full Tunnel + Services"
   - AllowedIPs: `0.0.0.0/0,::/0`
   - DNS: `1.1.1.1,2606:4700:4700::1111`
3. Add client: "My Laptop"
4. Download config or scan QR code

### 4. Test Service Hosting

```bash
# On client (after connecting to VPN)
python3 -m http.server 8080

# Check your IPv6
curl -6 https://api64.ipify.org
# Should show: 2a11:8083:11:13f0::2 (or ::3, ::4, etc.)

# Access from anywhere
curl -6 http://[2a11:8083:11:13f0::2]:8080
```

## 🔒 Security Setup

### 1. Configure Client Firewall

```bash
# On each client that hosts services
sudo ufw enable
sudo ufw allow 22/tcp   # SSH
sudo ufw allow 80/tcp   # HTTP
sudo ufw allow 443/tcp  # HTTPS
sudo ufw default deny incoming
sudo ufw default allow outgoing
```

### 2. Server Firewall

```bash
# Already configured by installer
sudo ufw status
# Should show:
# 22/tcp    ALLOW
# 80/tcp    ALLOW
# 443/tcp   ALLOW
# 51820/udp ALLOW
```

## 📊 Example Client Assignments

| Client | IPv4 | IPv6 | Use Case |
|--------|------|------|----------|
| My Laptop | 10.0.0.2 | 2a11:8083:11:13f0::2 | Web development |
| Home Server | 10.0.0.3 | 2a11:8083:11:13f0::3 | Nextcloud, Plex |
| Gaming PC | 10.0.0.4 | 2a11:8083:11:13f0::4 | Minecraft server |
| Phone | 10.0.0.5 | 2a11:8083:11:13f0::5 | File sharing |

## 🌐 Service Hosting Examples

### Web Server on Client

```bash
# Client gets: 2a11:8083:11:13f0::2
python3 -m http.server 8080

# Access from anywhere
http://[2a11:8083:11:13f0::2]:8080
```

### SSH Server

```bash
# Enable SSH on client
sudo systemctl start ssh

# Connect from anywhere
ssh user@2a11:8083:11:13f0::2
```

### Minecraft Server

```bash
# Start server on client
java -Xmx2G -jar minecraft_server.jar

# Players connect to
2a11:8083:11:13f0::2:25565
```

### Docker Services

```bash
# Run Nextcloud
docker run -d -p 80:80 nextcloud

# Access at
http://[2a11:8083:11:13f0::2]
```

## 🔧 Maintenance

### View Logs

```bash
# Application logs
sudo journalctl -u wireguard-manager -f

# WireGuard status
sudo wg show

# Nginx logs
sudo tail -f /var/log/nginx/access.log
```

### Backup

```bash
# From web interface: Settings → Create Backup
# Or manual:
cd /opt/wireguard-manager
sudo tar -czf backup-$(date +%Y%m%d).tar.gz data/
```

### Update

```bash
cd /opt/wireguard-manager
git pull
sudo systemctl restart wireguard-manager
```

## 🆘 Troubleshooting

### Can't access web interface

```bash
# Check service
sudo systemctl status wireguard-manager
sudo systemctl status nginx

# Check SSL certificate
sudo certbot certificates
```

### IPv6 not working

```bash
# Verify IPv6 connectivity
ping6 -c 4 google.com
curl -6 https://api64.ipify.org

# Check WireGuard
ip -6 addr show wg0
sudo wg show

# Verify forwarding
sysctl net.ipv6.conf.all.forwarding
```

### Service not accessible

```bash
# On client - check firewall
sudo ufw status

# On server - test connection
ping6 2a11:8083:11:13f0::2

# Check service is listening
sudo netstat -tulpn | grep :80
```

## 📚 Documentation

After deployment, refer to:
- **IPv6_SERVICE_HOSTING.md** - Complete IPv6 guide
- **IPv6_QUICK_REFERENCE.md** - Quick command reference
- **DEPLOYMENT.md** - Full deployment guide
- **PROFILES.md** - Profile templates

## ✅ Deployment Checklist

- [ ] SSH access to `root@sg.gc.parthh.com`
- [ ] Code uploaded or cloned to server
- [ ] Installer executed (`deployment/install.sh`)
- [ ] IPv6 enabled and configured
- [ ] SSL certificate installed
- [ ] Web interface accessible at https://sg.gc.parthh.com
- [ ] Admin account created with 2FA
- [ ] Test profile created
- [ ] Test client added
- [ ] VPN connection tested
- [ ] IPv6 service hosting verified
- [ ] Backup created

## 🎉 Success!

Once deployed, you can:
- Manage VPN clients from https://sg.gc.parthh.com
- Each client gets both IPv4 and IPv6
- Host services publicly from any device
- No port forwarding needed
- Direct internet access via IPv6

**Your subnet `2a11:8083:11:13f0::/64` has 18 quintillion addresses available!** 🌐
