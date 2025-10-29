# 📋 Deployment Checklist

Use this checklist to ensure a smooth deployment of WireGuard Manager.

## Pre-Deployment

### Server Preparation
- [ ] VPS/Server provisioned
- [ ] Ubuntu 20.04/22.04 or Debian 11/12 installed
- [ ] Root or sudo access confirmed
- [ ] Server updated: `sudo apt update && sudo apt upgrade -y`
- [ ] SSH key authentication configured (recommended)
- [ ] Firewall disabled temporarily (will be configured during install)

### Domain & DNS (Optional but Recommended)
- [ ] Domain name registered
- [ ] DNS A record pointing to server IP
- [ ] DNS propagated (check with `nslookup your-domain.com`)
- [ ] Port 80 and 443 accessible for Let's Encrypt

### Information Gathered
- [ ] Server public IP address
- [ ] Domain name (or will use IP)
- [ ] Desired WireGuard subnet (default: 10.0.0.0/24)
- [ ] Desired WireGuard port (default: 51820)
- [ ] Admin username (default: admin)
- [ ] Strong admin password (12+ characters)

## Installation

### Step 1: Download
- [ ] Downloaded/cloned WireGuard Manager
- [ ] Transferred to server or cloned directly
- [ ] In project directory: `cd wireguard-manager`

### Step 2: Run Installer
- [ ] Made installer executable: `chmod +x deployment/install.sh`
- [ ] Running as root: `sudo bash deployment/install.sh`
- [ ] Entered domain name or pressed Enter for IP
- [ ] Confirmed WireGuard settings
- [ ] Installer completed without errors

### Step 3: Verify Installation
- [ ] Service running: `sudo systemctl status wireguard-manager`
- [ ] WireGuard running: `sudo systemctl status wg-quick@wg0`
- [ ] Redis running: `sudo systemctl status redis`
- [ ] Nginx running: `sudo systemctl status nginx`
- [ ] No errors in logs: `sudo journalctl -u wireguard-manager -n 50`

### Step 4: Network Configuration
- [ ] Firewall enabled: `sudo ufw status`
- [ ] Port 22 (SSH) allowed
- [ ] Port 80 (HTTP) allowed
- [ ] Port 443 (HTTPS) allowed
- [ ] Port 51820 (WireGuard) allowed
- [ ] Can access server via browser

## Initial Setup

### Web Interface Access
- [ ] Opened browser to server URL
- [ ] HTTPS working (if domain used)
- [ ] Redirected to setup page
- [ ] No certificate warnings (if SSL configured)

### Admin Account Setup
- [ ] Created admin password (12+ characters)
- [ ] Password meets complexity requirements
- [ ] Setup completed successfully
- [ ] Redirected to 2FA setup

### 2FA Configuration
- [ ] Authenticator app installed (Google Authenticator, Authy, etc.)
- [ ] QR code scanned successfully
- [ ] Secret key backed up securely
- [ ] 6-digit code verified
- [ ] 2FA setup completed
- [ ] Redirected to login page

### First Login
- [ ] Logged in with username
- [ ] Entered password
- [ ] Entered 2FA code
- [ ] Successfully logged in
- [ ] Dashboard loads correctly

## Configuration

### Create Default Profile
- [ ] Navigated to Profiles
- [ ] Created "Full Tunnel" profile:
  - Name: Full Tunnel
  - Allowed IPs: 0.0.0.0/0,::/0
  - DNS: 1.1.1.1,1.0.0.1
- [ ] Profile saved successfully

### Optional: Create Additional Profiles
- [ ] Split Tunnel profile (if needed)
- [ ] Regional profiles (if needed)
- [ ] Custom profiles for specific use cases

### Test Client Creation
- [ ] Navigated to Clients → Add New Client
- [ ] Entered test client name
- [ ] Selected profile
- [ ] Set expiry (optional)
- [ ] Client created successfully
- [ ] QR code displayed
- [ ] Config file downloadable

### Test VPN Connection
- [ ] Downloaded config file OR scanned QR code
- [ ] Imported to WireGuard client
- [ ] Connection activated
- [ ] IP address changed (check: https://whatismyip.com)
- [ ] Internet working
- [ ] DNS working (check: https://dnsleaktest.com)
- [ ] Client shows as "Connected" in dashboard

## Security Hardening

### Application Security
- [ ] Strong admin password in use
- [ ] 2FA enabled and working
- [ ] Session timeout configured (default: 30 min)
- [ ] HTTPS enforced (if using domain)
- [ ] HTTP redirects to HTTPS

### Server Security
- [ ] SSH key authentication enabled
- [ ] Password authentication disabled (in /etc/ssh/sshd_config)
- [ ] Root login disabled
- [ ] Firewall (UFW) enabled with correct rules
- [ ] Automatic security updates enabled (optional)
- [ ] Fail2ban installed (optional but recommended)

### WireGuard Security
- [ ] WireGuard keys properly secured (600 permissions)
- [ ] Server private key backed up securely
- [ ] Client keys unique per client
- [ ] Unused clients removed

### Optional IP Whitelist
- [ ] IP whitelist configured in .env (if needed)
- [ ] Tested access from allowed IP
- [ ] Tested blocking from non-allowed IP

## Backup & Recovery

### Initial Backup
- [ ] Created first backup from Settings page
- [ ] Downloaded backup file
- [ ] Stored backup in safe location (off-server)
- [ ] Verified backup file integrity

### Automatic Backups
- [ ] Confirmed AUTO_BACKUP_ENABLED=True
- [ ] Confirmed backup time (default: 2 AM)
- [ ] Confirmed retention period (default: 30 days)

### Test Restore (Optional but Recommended)
- [ ] Created test backup
- [ ] Restored from backup
- [ ] Verified data integrity
- [ ] Verified clients still work

## Monitoring Setup

### Application Monitoring
- [ ] Dashboard accessible and updating
- [ ] Usage statistics collecting
- [ ] Audit logs recording
- [ ] No errors in application logs

### System Monitoring
- [ ] Checked disk space: `df -h`
- [ ] Checked memory usage: `free -h`
- [ ] Checked CPU usage: `top`
- [ ] Set up monitoring alerts (optional)

### WireGuard Monitoring
- [ ] Can view peer status: `sudo wg show`
- [ ] Transfer stats updating
- [ ] Handshakes occurring
- [ ] No connection issues

## Documentation

### Information Recorded
- [ ] Server IP/domain documented
- [ ] Admin credentials stored securely
- [ ] 2FA secret backed up
- [ ] WireGuard server public key recorded
- [ ] Initial configuration documented

### Access Documentation
- [ ] Team members know how to access
- [ ] Login procedure documented
- [ ] 2FA setup instructions available
- [ ] Emergency contact information updated

## Final Verification

### Functionality Check
- [ ] Can login to web interface
- [ ] Can create new clients
- [ ] Can download/scan configs
- [ ] Can enable/disable clients
- [ ] Can extend client expiry
- [ ] Can delete clients
- [ ] Can create/edit profiles
- [ ] Can view usage statistics
- [ ] Can view audit logs
- [ ] Can create backups
- [ ] Can download backups

### Performance Check
- [ ] Web interface loads quickly
- [ ] No lag in dashboard
- [ ] Statistics update correctly
- [ ] VPN connection stable
- [ ] Good connection speed

### Error Handling Check
- [ ] Tested wrong password (blocks correctly)
- [ ] Tested wrong 2FA (blocks correctly)
- [ ] Tested invalid inputs (handled gracefully)
- [ ] Error messages clear and helpful

## Post-Deployment

### Week 1 Tasks
- [ ] Monitor logs daily
- [ ] Check for any errors
- [ ] Verify automatic backups running
- [ ] Test VPN from multiple devices
- [ ] Review audit logs
- [ ] Check disk space

### Week 2-4 Tasks
- [ ] Review usage statistics
- [ ] Optimize profiles if needed
- [ ] Remove test clients
- [ ] Add real users
- [ ] Fine-tune settings

### Monthly Tasks
- [ ] Review and download backups
- [ ] Update system packages
- [ ] Review audit logs
- [ ] Check disk space
- [ ] Monitor performance
- [ ] Review security settings

## Maintenance Schedule

### Daily (Automated)
- ✅ Usage statistics recording (midnight)
- ✅ Automatic backups (2 AM)
- ✅ Old backup cleanup

### Hourly (Automated)
- ✅ Expired client checks

### Weekly (Manual)
- [ ] Review audit logs
- [ ] Check for errors
- [ ] Monitor disk space

### Monthly (Manual)
- [ ] Download backups
- [ ] System updates
- [ ] Security review
- [ ] Performance review

## Troubleshooting Reference

### If Something Goes Wrong

**Service won't start:**
```bash
sudo journalctl -u wireguard-manager -n 50
sudo systemctl restart wireguard-manager
```

**Can't connect to VPN:**
```bash
sudo wg show
sudo systemctl restart wg-quick@wg0
```

**Web interface not loading:**
```bash
sudo systemctl status nginx
sudo nginx -t
sudo systemctl restart nginx
```

**Database/session issues:**
```bash
sudo systemctl status redis
sudo systemctl restart redis
```

## Success Criteria

Deployment is successful when:
- ✅ Web interface accessible via HTTPS
- ✅ Admin can login with 2FA
- ✅ Can create and manage clients
- ✅ VPN connections work
- ✅ Usage tracking works
- ✅ Backups are created
- ✅ Audit logs recording
- ✅ No errors in logs
- ✅ System stable and performant

## Emergency Contacts

- **Hosting Provider Support**: _______________
- **Domain Registrar**: _______________
- **System Administrator**: _______________
- **Emergency Access**: _______________

## Notes

Use this section to record any deployment-specific information:

```
Installation Date: _______________
Server IP: _______________
Domain: _______________
WireGuard Port: _______________
Special Configuration: _______________




```

---

**Deployment Status**: ☐ Not Started | ☐ In Progress | ☐ Completed | ☐ Verified

**Date Completed**: _______________
**Deployed By**: _______________
