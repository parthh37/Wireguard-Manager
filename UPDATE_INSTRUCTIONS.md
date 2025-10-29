# 🔧 Update Instructions - Bug Fixes

## Issues Fixed

✅ **500 Internal Server Error** - Fixed WireGuard command permissions  
✅ **Dashboard Errors** - Added comprehensive error handling  
✅ **Profile Creation** - Enhanced wizard with 6 presets  
✅ **Profile QR Codes & Downloads** - Fixed config generation errors (sudo path issue)  
✅ **Clients & Usage Pages** - Fixed 500 errors with proper error handling  
✅ **Better UX** - Live preview, MTU options, persistent keepalive  
✅ **Health Monitoring** - Added service status display and health check API  

## 🚀 Update on Server

### Quick Update

```bash
# SSH to server
ssh root@sg.gc.parthh.com

# Go to installation directory
cd ~/Wireguard-Manager

# Pull latest changes
git pull

# Copy updated files
sudo cp -r * /opt/wireguard-manager/

# Restart the service
sudo systemctl restart wireguard-manager

# Check status
sudo systemctl status wireguard-manager
```

### Verify Fix

1. **Visit dashboard**: https://sgvpn.parthh.com
2. **Login** with your credentials
3. **Dashboard should load** without 500 error
4. **Navigate to Profiles** → Create New Profile
5. **Test the new wizard** with presets

## 🎨 New Features

### Enhanced Profile Creation

**6 Quick Presets:**
1. 🌍 Full Tunnel - All traffic through VPN
2. 🔀 Split Tunnel - VPN network only
3. 🌐 IPv6 Services - Full tunnel + public IPv6
4. 🎮 Gaming - Low latency gaming
5. 📺 Streaming - Netflix, YouTube optimized
6. 🔒 Privacy + Ad Block - DNS-level ad blocking

**New Options:**
- ✅ Persistent Keepalive (25s) - For NAT/mobile
- ✅ Custom MTU - Adjust if needed (1280-1500)
- ✅ Live Preview - See config before creating
- ✅ Better descriptions and examples

## 🔍 Troubleshooting

### ❌ WireGuard Service Showing as Inactive/Down?

This means WireGuard service is not running on your server. **Run these diagnostic steps:**

```bash
# SSH to server
ssh root@sg.gc.parthh.com

# Go to installation directory
cd ~/Wireguard-Manager

# Run diagnostic script
chmod +x diagnose-wireguard.sh
sudo ./diagnose-wireguard.sh
```

**Common fixes:**

```bash
# 1. Check if service exists and is enabled
sudo systemctl status wg-quick@wg0

# 2. If service is disabled, enable it
sudo systemctl enable wg-quick@wg0

# 3. Start the service
sudo systemctl start wg-quick@wg0

# 4. Check config file exists
ls -la /etc/wireguard/wg0.conf

# 5. If config is missing or you want to rebuild
sudo chmod +x fix-wireguard-service.sh
sudo ./fix-wireguard-service.sh

# 6. Check logs for errors
sudo journalctl -u wg-quick@wg0 -n 50 --no-pager
```

**If WireGuard was never set up:**
```bash
# Run the fix script to create initial config
sudo ./fix-wireguard-service.sh

# This will:
# - Install WireGuard if missing
# - Create /etc/wireguard/wg0.conf
# - Generate server keys
# - Enable and start service
# - Configure IP forwarding
```

### Still Getting 500 Error?

```bash
# Check application logs
sudo journalctl -u wireguard-manager -n 50 --no-pager

# Check if WireGuard is running
sudo wg show

# Verify permissions
sudo cat /etc/sudoers.d/wireguard-manager
# Should show:
# www-data ALL=(ALL) NOPASSWD: /usr/bin/wg
# www-data ALL=(ALL) NOPASSWD: /usr/bin/wg-quick
```

### Test WireGuard Commands

```bash
# Test as www-data user
sudo -u www-data sudo wg show

# Should display WireGuard status without errors
```

### Restart Everything

```bash
# Restart WireGuard
sudo systemctl restart wg-quick@wg0

# Restart application
sudo systemctl restart wireguard-manager

# Restart Nginx
sudo systemctl restart nginx

# Check all services
sudo systemctl status wg-quick@wg0
sudo systemctl status wireguard-manager
sudo systemctl status nginx
```

## 📝 What Changed

### Files Modified

1. **`utils/wireguard.py`**
   - Added `sudo` prefix to all `wg` commands
   - `wg genkey`, `wg pubkey`, `wg genpsk`
   - `wg set`, `wg show`, `wg showconf`

2. **`routes/dashboard.py`**
   - Added try-catch blocks
   - Graceful error handling
   - Returns default values if WireGuard unavailable

3. **`routes/clients.py`**
   - Fixed 500 errors with comprehensive error handling
   - Protected WireGuard stats retrieval
   - Graceful fallback for missing data

4. **`routes/usage.py`**
   - Fixed 500 errors with try-catch blocks
   - Protected historical data access
   - Error-safe chart rendering

5. **`routes/profiles.py`**
   - Support for new profile options (MTU, keepalive)
   - Added QR code generation route
   - Added config download route
   - Fixed method signature for config generation
   - View profile details page

6. **`templates/profiles/add.html`**
   - Added 6 preset buttons
   - Live configuration preview
   - Persistent keepalive checkbox
   - Custom MTU option
   - Better form descriptions

7. **`templates/profiles/list.html`**
   - Added QR code button (📱 QR)
   - Added download button (💾 Config)
   - Clickable profile names
   - Enhanced action buttons

8. **`templates/profiles/view.html`** *(NEW)*
   - Profile detail view page
   - Large QR code display
   - Config preview
   - Profile usage stats

## ✅ Expected Behavior After Update

- ✅ Dashboard loads without errors
- ✅ Shows WireGuard service status badge (green/red)
- ✅ Displays service active, interface up, peer count
- ✅ Shows connected clients count
- ✅ Displays data usage stats
- ✅ Clients page displays properly (no 500 errors)
- ✅ Usage page shows statistics (no 500 errors)
- ✅ Profile wizard has preset buttons
- ✅ Live preview updates as you type
- ✅ Profile QR codes generate correctly
- ✅ Profile configs download successfully
- ✅ Click profile name to see details
- ✅ Health check API available at /health
- ✅ No 500 errors on any page

## 🎉 Success!

After updating:
1. Dashboard works ✅
2. Client list loads ✅
3. Usage page displays ✅
4. Profiles have new wizard ✅
5. QR codes generate properly ✅
6. Config downloads work ✅
7. Enhanced UX with presets ✅

## 🆕 New Features to Try

### WireGuard Service Status Monitor
1. Open **Dashboard**
2. See status badge at top:
   - **Green**: Service running & healthy ✅
   - **Red**: Service issues detected ⚠️
   - **Gray**: Status unknown ❓
3. Shows: Service active, Interface up, Active peers

### Health Check API
```bash
# Check system health
curl https://sgvpn.parthh.com/health

# Returns JSON:
{
  "status": "healthy",
  "wireguard": {
    "service_active": true,
    "interface_up": true,
    "peer_count": 5,
    "status": "healthy"
  },
  "storage": "ok",
  "version": "1.0.0"
}
```

### Profile QR Codes & Downloads
1. Go to **Profiles** page
2. Click **📱 QR** to see QR code for any profile
3. Click **💾 Config** to download configuration
4. Click **profile name** to view full profile details with large QR code
5. Configs have **real WireGuard keys** - ready to use!

### Enhanced Profile Creation
1. Go to **Profiles** → **Create New Profile**
2. Choose from 6 presets:
   - 🌍 Full Tunnel (all traffic)
   - 🔀 Split Tunnel (VPN network only)
   - 🌐 IPv6 Services (public hosting)
   - 🎮 Gaming (low latency)
   - 📺 Streaming (optimized)
   - 🔒 Privacy + Ad Block
3. See live preview as you customize
4. Add persistent keepalive for mobile devices
5. Adjust MTU if needed

**Questions? Check logs:**
```bash
sudo journalctl -u wireguard-manager -f
```
