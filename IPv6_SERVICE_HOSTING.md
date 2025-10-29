# 🌐 IPv6 Service Hosting Guide

Complete guide to hosting public services from your devices using WireGuard Manager with IPv6.

## 📋 Overview

With IPv6 enabled, each device connected to your WireGuard VPN gets a **publicly routable IPv6 address** from your VPS's /64 subnet. This means you can host services (web servers, SSH, game servers, etc.) directly from any device, accessible from anywhere on the internet.

## 🎯 Key Benefits

✅ **Direct Public Access** - Each device gets a real public IPv6 address  
✅ **No Port Forwarding** - No NAT, no port forwarding needed  
✅ **Unlimited Addresses** - /64 subnet = 18 quintillion addresses  
✅ **End-to-End Connectivity** - Direct connection to your devices  
✅ **Service Hosting** - Host anything: web, SSH, gaming, streaming  
✅ **Split/Full Tunnel** - Choose how to route traffic  

## 🔧 Setup Requirements

### VPS Requirements
- Must have native IPv6 connectivity
- Dedicated /64 IPv6 subnet (most providers give /64 by default)
- IPv6 forwarding enabled
- Public IPv6 address

### Supported Scenarios

1. **Full Tunnel + Service Hosting**
   - All device traffic goes through VPN
   - Services hosted on device's public IPv6
   - Privacy + hosting capability

2. **Split Tunnel + Service Hosting**
   - Only specific traffic through VPN
   - Services hosted on public IPv6
   - Better performance for local traffic

3. **Hybrid Configuration**
   - Some devices full tunnel (privacy)
   - Some devices split tunnel (services)

## 📝 Installation with IPv6

### Automated Installation

```bash
sudo bash deployment/install.sh
```

The installer will:
1. Detect your server's IPv6 address
2. Ask for your /64 subnet
3. Configure WireGuard with IPv6
4. Set up routing and forwarding
5. Configure firewall for IPv6

### Example Installation Flow

```
Detected IPv4: 203.0.113.10
Detected IPv6: 2a11:8083:11:13f0::1

=== IPv6 Configuration ===
Enable IPv6 for WireGuard? (Y/n): Y
Enter your IPv6 /64 subnet: 2a11:8083:11:13f0::/64
Server IPv6 will be: 2a11:8083:11:13f0::1
Enable public IPv6 routing for hosting services? (Y/n): Y
```

## 🎨 Creating Profiles for IPv6

### Profile 1: Full Tunnel with Service Hosting

Perfect for: Privacy while hosting services

```
Name: Full Tunnel + Services
Description: All traffic through VPN, host services on IPv6
Allowed IPs: 0.0.0.0/0, ::/0
DNS: 1.1.1.1, 1.0.0.1
```

**What happens:**
- All IPv4 traffic → through VPN → NAT
- All IPv6 traffic → through VPN → direct routing
- Services on IPv6 → publicly accessible
- Complete privacy

### Profile 2: Split Tunnel for Services Only

Perfect for: Hosting services without routing all traffic

```
Name: IPv6 Services Only
Description: Only VPN network access, host IPv6 services
Allowed IPs: 10.0.0.0/24, 2a11:8083:11:13f0::/64
DNS: 1.1.1.1, 1.0.0.1
```

**What happens:**
- IPv4 internet → direct connection (fast)
- IPv6 within subnet → through VPN
- Services on IPv6 → publicly accessible
- Local traffic stays local

### Profile 3: IPv6 Only Access

Perfect for: IPv6-only environments

```
Name: IPv6 Only
Description: Only IPv6 traffic through VPN
Allowed IPs: ::/0
DNS: 2606:4700:4700::1111, 2606:4700:4700::1001
```

**What happens:**
- IPv4 → local connection
- IPv6 → through VPN
- Dual stack support

## 📱 Adding Clients with IPv6

### From Web Interface

1. **Go to Clients → Add New Client**
2. Enter client name (e.g., "My Laptop")
3. Select profile
4. Client automatically gets:
   - IPv4: `10.0.0.2`
   - IPv6: `2a11:8083:11:13f0::2`

### IP Assignment

Clients get sequential IPs:
- Client 1: `10.0.0.2`, `2a11:8083:11:13f0::2`
- Client 2: `10.0.0.3`, `2a11:8083:11:13f0::3`
- Client 3: `10.0.0.4`, `2a11:8083:11:13f0::4`
- etc.

All IPv6 addresses are **publicly routable**.

## 🌍 Hosting Services

### Example: Web Server on Client

**On your laptop (connected to VPN):**

```bash
# Start a simple web server
python3 -m http.server 8080
```

**Access from anywhere:**
```
http://[2a11:8083:11:13f0::2]:8080
```

Anyone on the internet with IPv6 can access it!

### Example: SSH Server

**Enable SSH on your device:**
```bash
sudo systemctl enable ssh
sudo systemctl start ssh
```

**Connect from anywhere:**
```bash
ssh user@2a11:8083:11:13f0::2
```

### Example: Game Server

**Start Minecraft server:**
```bash
java -Xmx1024M -Xms1024M -jar minecraft_server.jar
```

**Players connect to:**
```
2a11:8083:11:13f0::2:25565
```

### Example: Self-Hosted Services

Host anything:
- **Nextcloud**: Personal cloud storage
- **Plex**: Media streaming
- **Home Assistant**: Smart home
- **Git server**: Code repositories
- **Websites**: Personal blog/portfolio
- **APIs**: Your own backend services

## 🔒 Security Considerations

### Firewall on Devices

Since devices are publicly accessible, use firewalls:

**UFW (Ubuntu/Debian):**
```bash
# Enable firewall
sudo ufw enable

# Allow specific services
sudo ufw allow 22/tcp   # SSH
sudo ufw allow 80/tcp   # HTTP
sudo ufw allow 443/tcp  # HTTPS

# Block everything else
sudo ufw default deny incoming
sudo ufw default allow outgoing
```

**Firewalld (RHEL/CentOS):**
```bash
sudo firewall-cmd --permanent --add-service=ssh
sudo firewall-cmd --permanent --add-service=http
sudo firewall-cmd --permanent --add-service=https
sudo firewall-cmd --reload
```

### Best Practices

1. **Only open necessary ports** - Don't expose everything
2. **Use strong authentication** - SSH keys, not passwords
3. **Keep software updated** - Regular security updates
4. **Monitor access logs** - Check for suspicious activity
5. **Use HTTPS** - Encrypt web traffic
6. **Fail2ban** - Protect against brute force
7. **Regular backups** - Protect your data

### VPS Firewall

Configure VPS firewall to allow WireGuard:

```bash
# Allow WireGuard port
sudo ufw allow 51820/udp

# Allow IPv6 forwarding
sudo ufw default allow routed
```

## 🔍 Verification & Testing

### Check IPv6 Connectivity

**On VPS:**
```bash
# Test IPv6 connectivity
ping6 -c 4 google.com

# Check your IPv6
curl -6 https://api64.ipify.org

# Verify WireGuard interface
ip -6 addr show wg0
```

**On Client (connected to VPN):**
```bash
# Check assigned IPv6
ip -6 addr

# Test connectivity
ping6 -c 4 google.com

# Verify your public IPv6
curl -6 https://api64.ipify.org
```

### Test Service Accessibility

**From another IPv6-enabled device:**

```bash
# Test HTTP
curl -6 http://[2a11:8083:11:13f0::2]:8080

# Test SSH
ssh -6 user@2a11:8083:11:13f0::2

# Test with telnet
telnet -6 2a11:8083:11:13f0::2 80
```

### Troubleshooting

**Service not accessible?**

1. Check device firewall
2. Verify service is listening on IPv6
3. Check WireGuard connection status
4. Verify IPv6 routing on VPS
5. Test from VPS first

**Check service binding:**
```bash
# See what's listening
sudo netstat -tulpn | grep -E ':80|:22|:443'

# Or with ss
sudo ss -tulpn | grep -E ':80|:22|:443'
```

## 📊 Monitoring

### Check Client Status

**From web interface:**
- Dashboard shows connected clients
- View client details for IPv6 address
- Monitor data usage per client

**From VPS:**
```bash
# Show connected peers
sudo wg show

# Show with endpoints
sudo wg show all endpoints

# Show IPv6 routes
ip -6 route show table main
```

### Traffic Monitoring

**Per-client bandwidth:**
```bash
# WireGuard built-in stats
sudo wg show wg0 transfer
```

**System-wide:**
```bash
# Install vnstat
sudo apt install vnstat

# Monitor IPv6 traffic
vnstat -i wg0 --live
```

## 🎯 Common Use Cases

### Use Case 1: Home Lab Access

**Scenario:** Access home services while traveling

**Setup:**
- Client: Home server
- Profile: Split tunnel
- Services: SSH, Web apps, File server

**Result:** Access everything as if you're home

### Use Case 2: Remote Development

**Scenario:** Code on remote machine

**Setup:**
- Client: Development laptop
- Profile: Full tunnel
- Services: VS Code Server, SSH, Git

**Result:** Secure remote coding environment

### Use Case 3: Game Server Hosting

**Scenario:** Host game for friends

**Setup:**
- Client: Gaming PC
- Profile: Split tunnel (low latency)
- Services: Minecraft, Terraria, etc.

**Result:** Friends connect to your IPv6, low latency

### Use Case 4: Personal Cloud

**Scenario:** Self-hosted cloud storage

**Setup:**
- Client: Raspberry Pi at home
- Profile: Full tunnel (privacy)
- Services: Nextcloud, Syncthing

**Result:** Private cloud accessible anywhere

### Use Case 5: IoT Device Management

**Scenario:** Manage IoT devices remotely

**Setup:**
- Client: Home Assistant device
- Profile: Split tunnel
- Services: Home Assistant, MQTT

**Result:** Control smart home from anywhere

## 🔄 Migration from IPv4-only

If you're upgrading from IPv4-only setup:

1. **Backup current configuration**
2. **Update .env with IPv6 settings**
3. **Restart WireGuard Manager**
4. **Existing clients keep IPv4**
5. **New clients get both IPv4 + IPv6**
6. **Regenerate configs for old clients to add IPv6**

## 📱 Client Configuration Examples

### Full Tunnel with Services

```ini
[Interface]
PrivateKey = <client-private-key>
Address = 10.0.0.2/32, 2a11:8083:11:13f0::2/128
DNS = 1.1.1.1, 1.0.0.1

[Peer]
PublicKey = <server-public-key>
PresharedKey = <preshared-key>
Endpoint = 203.0.113.10:51820
AllowedIPs = 0.0.0.0/0, ::/0
PersistentKeepalive = 25
```

### Split Tunnel

```ini
[Interface]
PrivateKey = <client-private-key>
Address = 10.0.0.2/32, 2a11:8083:11:13f0::2/128
DNS = 1.1.1.1, 1.0.0.1

[Peer]
PublicKey = <server-public-key>
PresharedKey = <preshared-key>
Endpoint = 203.0.113.10:51820
AllowedIPs = 10.0.0.0/24, 2a11:8083:11:13f0::/64
PersistentKeepalive = 25
```

## 🌟 Advanced Features

### Custom IPv6 Ranges

Manually assign specific IPv6 addresses:
- Reserve ::10-::99 for servers
- Use ::100-::999 for clients
- Document assignments

### DNS for Services

Set up DNS records:
```
myservice.example.com    AAAA    2a11:8083:11:13f0::2
```

Now access via domain instead of IP!

### Load Balancing

Distribute services across devices:
- Device 1: Web server (IPv6 ::2)
- Device 2: API server (IPv6 ::3)
- Device 3: Database (IPv6 ::4)

### High Availability

Multiple devices for redundancy:
- Primary: 2a11:8083:11:13f0::10
- Secondary: 2a11:8083:11:13f0::11

## 📞 Support

For issues:
1. Check VPS has IPv6 enabled
2. Verify /64 subnet assignment
3. Test IPv6 connectivity
4. Check firewall rules
5. Review WireGuard logs
6. See DEPLOYMENT.md troubleshooting

---

**You now have the power to host services from any device, anywhere!** 🚀
