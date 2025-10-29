# Default Connection Profiles

This file contains example profiles you can create in the application.

> **IPv6 Service Hosting:** If you've enabled IPv6 support, see the [IPv6-specific profiles](#ipv6-service-hosting-profiles) at the bottom for hosting services from client devices.

## Standard Profiles (IPv4)

## 1. Full Tunnel (All Traffic)

**Use Case**: Route all internet traffic through VPN for maximum privacy

```
Name: Full Tunnel
Description: Route all internet traffic through VPN
Allowed IPs: 0.0.0.0/0,::/0
DNS: 1.1.1.1,1.0.0.1
```

**Benefits**:
- Complete privacy and encryption
- Hide your IP address from websites
- Bypass censorship and geo-restrictions
- Protect on public WiFi

## 2. Split Tunnel (Private Networks Only)

**Use Case**: Access home/office networks remotely

```
Name: Split Tunnel - Private Networks
Description: Only route private network traffic through VPN
Allowed IPs: 10.0.0.0/8,172.16.0.0/12,192.168.0.0/16
DNS: 1.1.1.1,1.0.0.1
```

**Benefits**:
- Access home/office resources
- Faster speeds (only VPN traffic goes through tunnel)
- Regular internet traffic uses local connection
- Good for remote work

## 3. Privacy with Ad Blocking

**Use Case**: Full privacy with DNS-level ad blocking

```
Name: Privacy + Ad Blocking
Description: Full tunnel with ad-blocking DNS
Allowed IPs: 0.0.0.0/0,::/0
DNS: 9.9.9.9,149.112.112.112
```

DNS Provider: Quad9 (blocks malicious domains)

## 4. Netflix/Streaming

**Use Case**: Access geo-restricted streaming content

```
Name: Streaming
Description: Optimized for streaming services
Allowed IPs: 0.0.0.0/0,::/0
DNS: 8.8.8.8,8.8.4.4
```

**Note**: Ensure your server is in the desired region

## 5. Gaming

**Use Case**: Low latency gaming with DDoS protection

```
Name: Gaming
Description: Low latency for online gaming
Allowed IPs: 0.0.0.0/0,::/0
DNS: 1.1.1.1,1.0.0.1
```

**Tips**:
- Use a server close to game servers
- Monitor latency in usage stats
- Consider regional servers

## 6. Torrenting/P2P

**Use Case**: Safe torrenting with privacy

```
Name: P2P/Torrenting
Description: Secure P2P with privacy
Allowed IPs: 0.0.0.0/0,::/0
DNS: 1.1.1.1,1.0.0.1
```

**Important**:
- Ensure your VPS provider allows P2P
- Check terms of service
- Use port forwarding if needed

## 7. Mobile Data Saver

**Use Case**: Compress and save mobile data

```
Name: Mobile Data Saver
Description: Split tunnel for mobile devices
Allowed IPs: 10.0.0.0/8,192.168.0.0/16
DNS: 1.1.1.1,1.0.0.1
```

**Benefits**:
- Only tunnel necessary traffic
- Save mobile data
- Better battery life

## 8. Work VPN

**Use Case**: Access office resources securely

```
Name: Work Access
Description: Access office network (example: 192.168.1.0/24)
Allowed IPs: 192.168.1.0/24
DNS: 192.168.1.1 (or your office DNS)
```

**Customize**:
- Replace with your office network subnet
- Use office DNS server

## 9. IoT Devices

**Use Case**: Secure IoT devices with limited access

```
Name: IoT Secure
Description: Limited access for IoT devices
Allowed IPs: 10.0.0.0/24
DNS: 1.1.1.1,1.0.0.1
```

**Benefits**:
- Isolate IoT devices
- Control what they can access
- Enhanced security

## 10. Family Safe

**Use Case**: Family-friendly with content filtering

```
Name: Family Safe
Description: Content filtering for family
Allowed IPs: 0.0.0.0/0,::/0
DNS: 208.67.222.123,208.67.220.123
```

DNS Provider: OpenDNS FamilyShield (blocks adult content)

## DNS Providers Reference

### Cloudflare (Fast, Privacy-focused)
- Primary: `1.1.1.1`
- Secondary: `1.0.0.1`

### Google (Reliable, Fast)
- Primary: `8.8.8.8`
- Secondary: `8.8.4.4`

### Quad9 (Security, blocks malicious sites)
- Primary: `9.9.9.9`
- Secondary: `149.112.112.112`

### OpenDNS (Content filtering)
- Standard: `208.67.222.222`, `208.67.220.220`
- FamilyShield: `208.67.222.123`, `208.67.220.123`

### AdGuard (Ad blocking)
- Primary: `94.140.14.14`
- Secondary: `94.140.15.15`

## Allowed IPs Reference

### Full Tunnel (All Traffic)
```
0.0.0.0/0,::/0
```

### Private Networks (RFC1918)
```
10.0.0.0/8,172.16.0.0/12,192.168.0.0/16
```

### Specific Network (example)
```
192.168.1.0/24
```

### Multiple Networks
```
10.0.0.0/8,192.168.0.0/16,172.16.0.0/12
```

### VPN Server Only
```
10.0.0.0/24
```

## Creating Custom Profiles

1. Go to **Profiles** → **Create Profile**
2. Choose a template above or create custom
3. Enter name and description
4. Set Allowed IPs based on your needs
5. Choose appropriate DNS servers
6. Save profile

## Tips for Profile Management

### Naming Convention
Use clear, descriptive names:
- ✅ "Full Tunnel - Privacy"
- ✅ "Office Network Access"
- ✅ "Home Media Streaming"
- ❌ "Profile1"
- ❌ "Test"

### Testing Profiles
After creating a profile:
1. Create a test client
2. Connect and verify:
   - IP address changed: https://whatismyip.com
   - DNS working: `nslookup google.com`
   - No DNS leaks: https://dnsleaktest.com

### Profile Best Practices

1. **Start Simple**: Begin with full tunnel, then customize
2. **Test Thoroughly**: Always test new profiles
3. **Document Changes**: Use description field
4. **Don't Over-complicate**: Keep allowed IPs simple
5. **Consider Performance**: Full tunnel uses more bandwidth

## Troubleshooting Profiles

### Client can't browse internet
- Check Allowed IPs includes `0.0.0.0/0`
- Verify DNS servers are accessible
- Test DNS: `nslookup google.com`

### Can't access local network
- Add local subnet to Allowed IPs
- Example: `10.0.0.0/8,0.0.0.0/0,::/0`

### Slow connection
- Try different DNS servers
- Consider split tunnel instead of full
- Check server bandwidth

### DNS not working
- Verify DNS IPs are correct
- Test: `nslookup google.com <dns-ip>`
- Try alternative DNS provider

---

These profiles cover most common use cases. Customize them based on your specific needs!

---

## IPv6 Service Hosting Profiles

**Prerequisites**: 
- IPv6 enabled in `.env`: `WG_IPV6_ENABLED=True`
- Public routing enabled: `IPV6_PUBLIC_ROUTING=True`
- Valid /64 IPv6 subnet configured

See [IPv6_SERVICE_HOSTING.md](IPv6_SERVICE_HOSTING.md) for complete guide.

### 11. Full Tunnel + IPv6 Services

**Use Case**: Complete privacy while hosting public services on IPv6

```
Name: Full Tunnel + IPv6 Services
Description: All traffic through VPN, host services on public IPv6
Allowed IPs: 0.0.0.0/0,::/0
DNS: 1.1.1.1,1.0.0.1,2606:4700:4700::1111,2606:4700:4700::1001
```

**Features**:
- All IPv4 traffic → VPN (NAT for privacy)
- All IPv6 traffic → VPN (direct routing)
- Services on client IPv6 → publicly accessible
- Complete traffic encryption
- Full anonymity for browsing

**Perfect For**:
- Hosting web servers from laptop
- Running SSH servers with privacy
- Self-hosted services with security
- Development/testing public services

**Example Use Cases**:
```bash
# On client device with IPv6: 2a11:8083:11:13f0::2

# Host a web server
python3 -m http.server 8080
# Access from anywhere: http://[2a11:8083:11:13f0::2]:8080

# Run SSH server
sudo systemctl start ssh
# Connect from anywhere: ssh user@2a11:8083:11:13f0::2

# Host game server
./minecraft_server.jar
# Players connect to: 2a11:8083:11:13f0::2:25565
```

### 12. Split Tunnel for Services Only

**Use Case**: Host services without routing all traffic through VPN

```
Name: IPv6 Services Only
Description: Only VPN network access, host public IPv6 services
Allowed IPs: 10.0.0.0/24,2a11:8083:11:13f0::/64
DNS: 1.1.1.1,1.0.0.1
```

**Features**:
- IPv4 internet → direct (fast, low latency)
- IPv6 VPN subnet → through VPN
- Services on IPv6 → publicly accessible
- Local traffic stays local
- Better performance than full tunnel

**Perfect For**:
- Game servers (low latency)
- Home lab services
- IoT device access
- Remote development environments
- Raspberry Pi projects

**Benefits**:
- Faster general internet (no VPN overhead)
- Low latency for gaming/streaming
- Services still publicly accessible
- Remote access to devices at home

### 13. Home Lab Public Access

**Use Case**: Make home lab services publicly accessible

```
Name: Home Lab IPv6
Description: Expose home lab services on public IPv6
Allowed IPs: 10.0.0.0/24,2a11:8083:11:13f0::/64
DNS: 192.168.1.1,1.1.1.1
```

**Perfect For**:
- Homelab servers (Proxmox, TrueNAS)
- Docker containers with public access
- Development servers
- Testing environments
- CI/CD pipelines

**Example Setup**:
```bash
# Home server gets: 2a11:8083:11:13f0::10

# Run services
docker run -p 80:80 nginx  # Web server
docker run -p 3000:3000 app # Custom app

# Access from anywhere
http://[2a11:8083:11:13f0::10]
http://[2a11:8083:11:13f0::10]:3000
```

### 14. Mobile IPv6 Hotspot

**Use Case**: Share public IPv6 from mobile device

```
Name: Mobile IPv6 Hotspot
Description: Mobile device with public IPv6 services
Allowed IPs: 10.0.0.0/24,2a11:8083:11:13f0::/64
DNS: 1.1.1.1,1.0.0.1
```

**Perfect For**:
- Temporary file sharing
- Mobile development testing
- Remote access to phone
- IoT device programming

**Use Cases**:
- Share files via simple HTTP server
- SSH into your phone (Termux)
- Test mobile apps with public endpoint
- Remote camera/sensor access

### 15. Development & Testing

**Use Case**: Public endpoints for development/testing

```
Name: Dev Environment IPv6
Description: Development with public test endpoints
Allowed IPs: 10.0.0.0/24,2a11:8083:11:13f0::/64
DNS: 1.1.1.1,1.0.0.1
```

**Perfect For**:
- Webhook testing (GitHub, Stripe, etc.)
- OAuth callback development
- API testing with public URLs
- Mobile app backend testing

**Examples**:
```bash
# Development server with public endpoint
npm run dev
# Accessible at: http://[2a11:8083:11:13f0::5]:3000

# Test webhooks
# Configure webhook URL: http://[2a11:8083:11:13f0::5]:4000/webhook

# OAuth callbacks
# Callback URL: http://[2a11:8083:11:13f0::5]:8080/auth/callback
```

### 16. Self-Hosted Services

**Use Case**: Run self-hosted apps with public access

```
Name: Self-Hosted Apps
Description: Full tunnel with self-hosted service access
Allowed IPs: 0.0.0.0/0,::/0
DNS: 1.1.1.1,1.0.0.1
```

**Perfect For**:
- Nextcloud (file sync)
- Bitwarden (password manager)
- Plex/Jellyfin (media streaming)
- Gitea (Git hosting)
- Home Assistant (smart home)

**Setup Example**:
```bash
# Client: 2a11:8083:11:13f0::20

# Run Nextcloud in Docker
docker run -d -p 80:80 nextcloud

# Access from anywhere
http://[2a11:8083:11:13f0::20]

# Or set up DNS
nextcloud.yourdomain.com → AAAA → 2a11:8083:11:13f0::20
```

### 17. Gaming Server Host

**Use Case**: Host game servers with low latency

```
Name: Gaming Server IPv6
Description: Split tunnel optimized for game hosting
Allowed IPs: 10.0.0.0/24,2a11:8083:11:13f0::/64
DNS: 1.1.1.1,1.0.0.1
```

**Perfect For**:
- Minecraft servers
- Terraria/Starbound
- Counter-Strike servers
- Valheim/Satisfactory
- ARK/Rust servers

**Benefits**:
- Low latency (split tunnel)
- Public IPv6 (no port forwarding)
- Easy player connections
- No NAT traversal issues

**Example**:
```bash
# Client: 2a11:8083:11:13f0::30

# Start Minecraft server
java -Xmx2G -jar server.jar

# Players connect to
2a11:8083:11:13f0::30:25565
```

### 18. IoT & Smart Home

**Use Case**: Remote access to IoT devices

```
Name: IoT Remote Access
Description: Secure IoT access with limited routing
Allowed IPs: 10.0.0.0/24,2a11:8083:11:13f0::/64
DNS: 1.1.1.1,1.0.0.1
```

**Perfect For**:
- Raspberry Pi projects
- Home Assistant instances
- ESP32/ESP8266 devices
- Security cameras
- Sensor networks

**Security Considerations**:
```bash
# Always use firewall on IoT devices
sudo ufw enable
sudo ufw allow from 2a11:8083:11:13f0::/64 to any port 22  # SSH from VPN only
sudo ufw allow 80/tcp  # HTTP for all
```

## IPv6 DNS Servers

### Cloudflare (IPv6)
- Primary: `2606:4700:4700::1111`
- Secondary: `2606:4700:4700::1001`

### Google (IPv6)
- Primary: `2001:4860:4860::8888`
- Secondary: `2001:4860:4860::8844`

### Quad9 (IPv6)
- Primary: `2620:fe::fe`
- Secondary: `2620:fe::9`

## IPv6 Profile Tips

### Security Best Practices

1. **Firewall Everything**
   - Use UFW/firewalld on all clients
   - Only open necessary ports
   - Default deny incoming

2. **Monitor Access**
   - Check connection logs
   - Review audit logs in dashboard
   - Set up fail2ban for SSH

3. **Use DNS Names**
   - Set up AAAA records
   - Easier than remembering IPs
   - Can change IPs without updating clients

4. **Regular Updates**
   - Keep services patched
   - Update firewall rules
   - Review open ports

### Testing IPv6 Services

After creating IPv6 profile and client:

```bash
# On client - verify IPv6 address
ip -6 addr show

# Test VPN IPv6 connectivity
ping6 -c 4 google.com

# Verify your public IPv6
curl -6 https://api64.ipify.org
# Should show your assigned IPv6

# Start test service
python3 -m http.server 8080

# Test from another device
curl -6 http://[2a11:8083:11:13f0::2]:8080
```

### Troubleshooting IPv6 Profiles

**Service not accessible from internet?**
1. Check client firewall allows the port
2. Verify service binds to IPv6 (`:::` not `0.0.0.0`)
3. Test from VPS first: `ping6 <client-ipv6>`
4. Check AllowedIPs includes IPv6 CIDR

**Slow IPv6 performance?**
1. Use split tunnel (only VPN for subnet)
2. Check VPS IPv6 bandwidth
3. Test with `iperf3 -V` (IPv6 mode)

**Can't connect to VPN with IPv6 enabled?**
1. Verify VPS has IPv6 connectivity
2. Check endpoint supports IPv6
3. Try IPv4 endpoint first
4. Review WireGuard logs

---

For complete IPv6 setup, troubleshooting, and advanced use cases, see:
📖 **[IPv6_SERVICE_HOSTING.md](IPv6_SERVICE_HOSTING.md)**
