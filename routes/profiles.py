from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, send_file
from utils.auth import login_required, log_action
from utils.storage import DataStore
from utils.wireguard import WireGuardManager
from utils.helpers import generate_qr_code, generate_qr_code_buffer
from config import Config
import uuid
import io

profiles_bp = Blueprint('profiles', __name__)
store = DataStore()
wg = WireGuardManager()

@profiles_bp.route('/')
@login_required
def index():
    """List all profiles"""
    log_action('VIEW_PROFILES', {})
    
    profiles = store.get_all_profiles()
    
    # Count clients per profile
    clients = store.get_all_clients()
    for profile in profiles:
        profile['client_count'] = len([c for c in clients if c.get('profile_id') == profile['id']])
    
    return render_template('profiles/list.html', profiles=profiles)

@profiles_bp.route('/<profile_id>')
@login_required
def view(profile_id):
    """View profile details"""
    profile = store.get_profile(profile_id)
    if not profile:
        flash('Profile not found', 'error')
        return redirect(url_for('profiles.index'))
    
    # Count clients using this profile
    clients = store.get_all_clients()
    profile['client_count'] = len([c for c in clients if c.get('profile_id') == profile_id])
    
    log_action('VIEW_PROFILE', {'profile_id': profile_id, 'name': profile.get('name')})
    
    return render_template('profiles/view.html', 
                         profile=profile,
                         server_public_key=Config.WG_SERVER_PUBLIC_KEY,
                         server_endpoint=f"{Config.SERVER_PUBLIC_IP}:{Config.WG_SERVER_PORT}",
                         ipv6_enabled=Config.WG_IPV6_ENABLED)

@profiles_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add():
    """Add new profile"""
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        description = request.form.get('description', '').strip()
        allowed_ips = request.form.get('allowed_ips', Config.WG_ALLOWED_IPS).strip()
        dns = request.form.get('dns', Config.WG_DNS).strip()
        persistent_keepalive = request.form.get('persistent_keepalive', '')
        mtu = request.form.get('mtu', '1420') if request.form.get('custom_mtu') else '1420'
        
        if not name:
            flash('Profile name is required', 'error')
            return render_template('profiles/add.html')
        
        # Create profile
        profile_id = str(uuid.uuid4())
        profile = {
            'id': profile_id,
            'name': name,
            'description': description,
            'allowed_ips': allowed_ips,
            'dns': dns,
            'persistent_keepalive': persistent_keepalive,
            'mtu': mtu,
            'created_at': datetime.now().isoformat()
        }
        
        store.save_profile(profile)
        log_action('PROFILE_ADDED', {'profile_id': profile_id, 'name': name})
        
        flash(f'Profile "{name}" created successfully!', 'success')
        return redirect(url_for('profiles.index'))
    
    return render_template('profiles/add.html', 
                         default_allowed_ips=Config.WG_ALLOWED_IPS,
                         default_dns=Config.WG_DNS)

@profiles_bp.route('/<profile_id>/edit', methods=['GET', 'POST'])
@login_required
def edit(profile_id):
    """Edit profile"""
    profile = store.get_profile(profile_id)
    if not profile:
        flash('Profile not found', 'error')
        return redirect(url_for('profiles.index'))
    
    if request.method == 'POST':
        profile['name'] = request.form.get('name', '').strip()
        profile['description'] = request.form.get('description', '').strip()
        profile['allowed_ips'] = request.form.get('allowed_ips', Config.WG_ALLOWED_IPS).strip()
        profile['dns'] = request.form.get('dns', Config.WG_DNS).strip()
        
        if not profile['name']:
            flash('Profile name is required', 'error')
            return render_template('profiles/edit.html', profile=profile)
        
        store.save_profile(profile)
        log_action('PROFILE_UPDATED', {'profile_id': profile_id, 'name': profile['name']})
        
        flash(f'Profile "{profile["name"]}" updated successfully!', 'success')
        return redirect(url_for('profiles.index'))
    
    return render_template('profiles/edit.html', profile=profile)

@profiles_bp.route('/<profile_id>/delete', methods=['POST'])
@login_required
def delete(profile_id):
    """Delete profile"""
    profile = store.get_profile(profile_id)
    if not profile:
        flash('Profile not found', 'error')
        return redirect(url_for('profiles.index'))
    
    # Check if any clients use this profile
    clients = store.get_all_clients()
    using_clients = [c for c in clients if c.get('profile_id') == profile_id]
    
    if using_clients:
        flash(f'Cannot delete profile: {len(using_clients)} client(s) are using it', 'error')
        return redirect(url_for('profiles.index'))
    
    store.delete_profile(profile_id)
    log_action('PROFILE_DELETED', {'profile_id': profile_id, 'name': profile.get('name')})
    
    flash(f'Profile "{profile["name"]}" deleted successfully', 'success')
    return redirect(url_for('profiles.index'))

@profiles_bp.route('/<profile_id>/qr')
@login_required
def qr_code(profile_id):
    """Generate QR code for profile with real client config"""
    profile = store.get_profile(profile_id)
    if not profile:
        return "Profile not found", 404
    
    try:
        # Generate REAL WireGuard keys
        private_key, public_key = wg.generate_keypair()
        preshared_key = wg.generate_preshared_key()
        
        # Build Address line
        address_line = "10.0.0.X/32"
        if Config.WG_IPV6_ENABLED:
            address_line += ", 2a11:8083:11:13f0::X/128"
        
        # Build endpoint
        endpoint = f"{Config.SERVER_PUBLIC_IP}:{Config.WG_SERVER_PORT}"
        
        # Get profile settings with defaults
        dns = profile.get('dns', Config.WG_DNS) or Config.WG_DNS
        allowed_ips = profile.get('allowed_ips', Config.WG_ALLOWED_IPS) or Config.WG_ALLOWED_IPS
        mtu = profile.get('mtu', '1420') or '1420'
        keepalive = profile.get('persistent_keepalive', '25') or '25'
        
        # Build config manually
        config = f"""[Interface]
PrivateKey = {private_key}
Address = {address_line}
DNS = {dns}
MTU = {mtu}

[Peer]
PublicKey = {Config.WG_SERVER_PUBLIC_KEY}
PresharedKey = {preshared_key}
Endpoint = {endpoint}
AllowedIPs = {allowed_ips}
PersistentKeepalive = {keepalive}
"""
        
        # Generate QR code as buffer
        qr_buffer = generate_qr_code_buffer(config)
        log_action('PROFILE_QR_VIEWED', {'profile_id': profile_id, 'name': profile.get('name')})
        
        return send_file(
            qr_buffer,
            mimetype='image/png',
            as_attachment=False,
            download_name=f"{profile['name']}_qr.png"
        )
    except Exception as e:
        import traceback
        error_msg = traceback.format_exc()
        print(f"Error generating QR code: {error_msg}")
        return f"Error generating QR code: {str(e)}", 500

@profiles_bp.route('/<profile_id>/download')
@login_required
def download(profile_id):
    """Download profile configuration with real keys"""
    profile = store.get_profile(profile_id)
    if not profile:
        return "Profile not found", 404
    
    try:
        # Generate REAL WireGuard keys
        private_key, public_key = wg.generate_keypair()
        preshared_key = wg.generate_preshared_key()
        
        # Build Address line
        address_line = "10.0.0.X/32"
        if Config.WG_IPV6_ENABLED:
            address_line += ", 2a11:8083:11:13f0::X/128"
        
        # Build endpoint
        endpoint = f"{Config.SERVER_PUBLIC_IP}:{Config.WG_SERVER_PORT}"
        
        # Get profile settings with defaults
        dns = profile.get('dns', Config.WG_DNS) or Config.WG_DNS
        allowed_ips = profile.get('allowed_ips', Config.WG_ALLOWED_IPS) or Config.WG_ALLOWED_IPS
        mtu = profile.get('mtu', '1420') or '1420'
        keepalive = profile.get('persistent_keepalive', '25') or '25'
        
        # Build config manually
        config_content = f"""[Interface]
PrivateKey = {private_key}
Address = {address_line}
DNS = {dns}
MTU = {mtu}

[Peer]
PublicKey = {Config.WG_SERVER_PUBLIC_KEY}
PresharedKey = {preshared_key}
Endpoint = {endpoint}
AllowedIPs = {allowed_ips}
PersistentKeepalive = {keepalive}
"""
        
        # Add header with profile info
        config_with_header = f"""# WireGuard Configuration - Profile: {profile['name']}
# {profile.get('description', 'Quick connect configuration')}
# Generated with REAL keys - Replace X with your assigned IP number
# Contact admin to get your IP assignment

{config_content}"""
        
        # Create file buffer
        buffer = io.BytesIO(config_with_header.encode('utf-8'))
        buffer.seek(0)
        
        log_action('PROFILE_CONFIG_DOWNLOADED', {'profile_id': profile_id, 'name': profile.get('name')})
        
        filename = f"{profile['name'].replace(' ', '_')}.conf"
        return send_file(
            buffer,
            mimetype='text/plain',
            as_attachment=True,
            download_name=filename
        )
    except Exception as e:
        import traceback
        error_msg = traceback.format_exc()
        print(f"Error generating config: {error_msg}")
        return f"Error generating config: {str(e)}", 500

from datetime import datetime
