# 🔧 Update Instructions - Bug Fixes

## Issues Fixed

✅ **500 Internal Server Error** - Fixed WireGuard command permissions  
✅ **Dashboard Errors** - Added comprehensive error handling  
✅ **Profile Creation** - Enhanced wizard with 6 presets  
✅ **Better UX** - Live preview, MTU options, persistent keepalive  

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

3. **`templates/profiles/add.html`**
   - Added 6 preset buttons
   - Live configuration preview
   - Persistent keepalive checkbox
   - Custom MTU option
   - Better form descriptions

4. **`routes/profiles.py`**
   - Support for new profile options
   - MTU and keepalive fields

## ✅ Expected Behavior After Update

- ✅ Dashboard loads without errors
- ✅ Shows connected clients count
- ✅ Displays data usage stats
- ✅ Profile wizard has preset buttons
- ✅ Live preview updates as you type
- ✅ No 500 errors on any page

## 🎉 Success!

After updating:
1. Dashboard works ✅
2. Client list loads ✅
3. Profiles have new wizard ✅
4. Enhanced UX with presets ✅

**Questions? Check logs:**
```bash
sudo journalctl -u wireguard-manager -f
```
