# 🌐 IPv6 Quick Reference Card

Quick reference for IPv6 service hosting with WireGuard Manager.

## ⚡ Quick Start

### 1. Enable IPv6 in .env
```bash
WG_IPV6_ENABLED=True
WG_IPV6_SUBNET=2a11:8083:11:13f0::/64
WG_SERVER_IPV6=2a11:8083:11:13f0::1
IPV6_PUBLIC_ROUTING=True
```

### 2. Verify VPS Has IPv6
```bash
curl -6 https://api64.ipify.org
ping6 -c 4 google.com
```

### 3. Create Profile
```
Name: Full Tunnel + Services
Allowed IPs: 0.0.0.0/0,::/0
DNS: 1.1.1.1,2606:4700:4700::1111
```

### 4. Add Client
- Client gets: IPv4 `10.0.0.2` + IPv6 `2a11:8083:11:13f0::2`
- IPv6 is publicly routable!

---

## 🎯 Common Use Cases

### Web Server
```bash
# On client
python3 -m http.server 8080

# Access from anywhere
http://[2a11:8083:11:13f0::2]:8080
```

### SSH Server
```bash
# On client
sudo systemctl start ssh

# Connect from anywhere
ssh user@2a11:8083:11:13f0::2
```

### Game Server (Minecraft)
```bash
# On client
java -Xmx2G -jar minecraft_server.jar

# Players connect to
2a11:8083:11:13f0::2:25565
```

### Docker Services
```bash
# On client
docker run -d -p 80:80 nginx

# Access from anywhere
http://[2a11:8083:11:13f0::2]
```

---

## 🔒 Security Checklist

### On Every Client
```bash
# Enable firewall
sudo ufw enable

# Allow only what you need
sudo ufw allow 22/tcp   # SSH
sudo ufw allow 80/tcp   # HTTP
sudo ufw allow 443/tcp  # HTTPS

# Block everything else
sudo ufw default deny incoming
sudo ufw default allow outgoing
```

### Strong SSH
```bash
# Disable password auth
sudo nano /etc/ssh/sshd_config
# Set: PasswordAuthentication no
# Use SSH keys only

# Restart SSH
sudo systemctl restart ssh
```

### Monitor Access
```bash
# Check auth logs
sudo tail -f /var/log/auth.log

# Check service logs
sudo journalctl -u <service-name> -f
```

---

## 🔍 Verification Commands

### Check IPv6 Assigned
```bash
ip -6 addr show
# Look for 2a11:8083:11:13f0::X
```

### Test Connectivity
```bash
ping6 -c 4 google.com
curl -6 https://api64.ipify.org
```

### Verify Service Listening
```bash
# Should show ::: for IPv6
sudo netstat -tulpn | grep :80
sudo ss -tulpn | grep LISTEN
```

### Test From Another Device
```bash
# Replace with your IPv6
curl -6 http://[2a11:8083:11:13f0::2]:8080
telnet -6 2a11:8083:11:13f0::2 80
```

---

## 🛠️ Troubleshooting

### Service Not Accessible

**1. Check Client Firewall**
```bash
sudo ufw status
# Make sure port is allowed
```

**2. Verify Service Binds to IPv6**
```bash
sudo netstat -tulpn | grep <port>
# Look for ::: not just 0.0.0.0
```

**3. Test From VPS**
```bash
ping6 2a11:8083:11:13f0::2
curl -6 http://[2a11:8083:11:13f0::2]:8080
```

**4. Check WireGuard Connection**
```bash
# On VPS
sudo wg show

# On client
sudo wg show
```

### No IPv6 Connectivity

**1. Verify VPS IPv6**
```bash
curl -6 https://api64.ipify.org
# Should return IPv6 address
```

**2. Check Forwarding**
```bash
sysctl net.ipv6.conf.all.forwarding
# Should be 1
```

**3. Verify WireGuard Config**
```bash
sudo cat /etc/wireguard/wg0.conf
# Should have IPv6 Address line
```

**4. Check ip6tables**
```bash
sudo ip6tables -L -n -v
# Should have FORWARD rules
```

---

## 📋 Profile Templates

### Full Tunnel + Services
```
AllowedIPs: 0.0.0.0/0,::/0
DNS: 1.1.1.1,2606:4700:4700::1111
```
All traffic through VPN, services publicly accessible

### Split Tunnel for Services
```
AllowedIPs: 10.0.0.0/24,2a11:8083:11:13f0::/64
DNS: 1.1.1.1
```
Only VPN subnet routed, low latency for services

### IPv6 Only
```
AllowedIPs: ::/0
DNS: 2606:4700:4700::1111
```
Only IPv6 traffic through VPN

---

## 🌍 IPv6 DNS Servers

| Provider | Primary | Secondary |
|----------|---------|-----------|
| Cloudflare | `2606:4700:4700::1111` | `2606:4700:4700::1001` |
| Google | `2001:4860:4860::8888` | `2001:4860:4860::8844` |
| Quad9 | `2620:fe::fe` | `2620:fe::9` |

---

## 💡 Tips & Tricks

### Use DNS Instead of IPs
```bash
# Set up AAAA record
myserver.example.com → 2a11:8083:11:13f0::2

# Much easier to remember!
ssh user@myserver.example.com
```

### Reserve IPv6 Ranges
- ::1 - Server
- ::2-::9 - Important services
- ::10-::99 - Servers/VMs
- ::100+ - Regular clients

### Monitor Bandwidth
```bash
# Install vnstat
sudo apt install vnstat

# Watch live traffic
vnstat -i wg0 --live
```

### Bind Services to Specific IP
```nginx
# Nginx - listen only on IPv6
server {
    listen [2a11:8083:11:13f0::2]:80;
    server_name _;
}
```

### Test Before Deploying
```bash
# Always test locally first
python3 -m http.server 8080

# Then test from VPS
curl -6 http://[<client-ipv6>]:8080

# Finally test from internet
curl -6 http://[<client-ipv6>]:8080
```

---

## 📊 Common Port Numbers

| Service | Port | Protocol |
|---------|------|----------|
| SSH | 22 | TCP |
| HTTP | 80 | TCP |
| HTTPS | 443 | TCP |
| Minecraft | 25565 | TCP |
| MySQL | 3306 | TCP |
| PostgreSQL | 5432 | TCP |
| MongoDB | 27017 | TCP |
| Redis | 6379 | TCP |

---

## 🚨 Emergency Commands

### Stop WireGuard
```bash
sudo systemctl stop wg-quick@wg0
```

### Disable All Client Access
```bash
# Remove all peers from wg0.conf
sudo nano /etc/wireguard/wg0.conf
sudo systemctl restart wg-quick@wg0
```

### Block IPv6 Temporarily
```bash
sudo ip6tables -P FORWARD DROP
# Restore:
sudo ip6tables -P FORWARD ACCEPT
```

### Check Who's Connected
```bash
sudo wg show wg0 latest-handshakes
# Shows last handshake time for each peer
```

---

## 📚 Further Reading

- **[IPv6_SERVICE_HOSTING.md](IPv6_SERVICE_HOSTING.md)** - Complete guide
- **[PROFILES.md](PROFILES.md)** - IPv6 profile examples
- **[DEPLOYMENT.md](DEPLOYMENT.md)** - Installation & troubleshooting

---

## ⚡ One-Liners

```bash
# Quick IPv6 check
curl -6 https://api64.ipify.org && echo " ← Your IPv6"

# Test if service is up
curl -I http://[2a11:8083:11:13f0::2]:8080

# See all listening services
sudo ss -tulpn | grep LISTEN

# Monitor WireGuard live
watch -n 1 sudo wg show

# Check all IPv6 addresses
ip -6 addr | grep inet6

# Test DNS resolution
nslookup -type=AAAA google.com

# Scan open ports (from another machine)
nmap -6 2a11:8083:11:13f0::2
```

---

**Remember:** With great power comes great responsibility. Always secure your services! 🔒
