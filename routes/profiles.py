from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, send_file
from utils.auth import login_required, log_action
from utils.storage import DataStore
from utils.wireguard import WireGuardManager
from utils.helpers import generate_qr_code
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
    """Generate QR code for profile (as example config)"""
    profile = store.get_profile(profile_id)
    if not profile:
        flash('Profile not found', 'error')
        return redirect(url_for('profiles.index'))
    
    try:
        # Generate example keys for demonstration
        private_key, public_key = wg.generate_keypair()
        preshared_key = wg.generate_preshared_key()
        
        # Create example client dict for config generation
        example_client = {
            'name': f"Example-{profile['name']}",
            'private_key': private_key,
            'public_key': public_key,
            'preshared_key': preshared_key,
            'ip_address': '10.0.0.X',
            'ipv6_address': '2001:db8::X' if Config.WG_IPV6_ENABLED else None
        }
        
        # Generate configuration using proper method signature
        config = wg.generate_client_config(example_client, profile)
        
        # Generate QR code
        qr_buffer = generate_qr_code(config)
        log_action('PROFILE_QR_VIEWED', {'profile_id': profile_id, 'name': profile.get('name')})
        
        return send_file(qr_buffer, mimetype='image/png')
    except Exception as e:
        print(f"Error generating QR code: {e}")
        flash('Error generating QR code', 'error')
        return redirect(url_for('profiles.index'))

@profiles_bp.route('/<profile_id>/download')
@login_required
def download(profile_id):
    """Download profile configuration (as example)"""
    profile = store.get_profile(profile_id)
    if not profile:
        flash('Profile not found', 'error')
        return redirect(url_for('profiles.index'))
    
    try:
        # Generate example keys for demonstration
        private_key, public_key = wg.generate_keypair()
        preshared_key = wg.generate_preshared_key()
        
        # Create example client dict for config generation
        example_client = {
            'name': f"Example-{profile['name']}",
            'private_key': private_key,
            'public_key': public_key,
            'preshared_key': preshared_key,
            'ip_address': '10.0.0.X',
            'ipv6_address': '2001:db8::X' if Config.WG_IPV6_ENABLED else None
        }
        
        # Generate configuration using proper method signature
        config = wg.generate_client_config(example_client, profile)
        
        # Add note at the top
        config_with_note = f"""# Example Configuration for Profile: {profile['name']}
# This is a template - actual client configs will have real keys and IPs
# {profile.get('description', '')}

{config}"""
        
        # Create file buffer
        buffer = io.BytesIO(config_with_note.encode('utf-8'))
        buffer.seek(0)
        
        log_action('PROFILE_CONFIG_DOWNLOADED', {'profile_id': profile_id, 'name': profile.get('name')})
        
        filename = f"{profile['name'].replace(' ', '_')}_example.conf"
        return send_file(buffer, 
                        mimetype='text/plain',
                        as_attachment=True,
                        download_name=filename)
    except Exception as e:
        print(f"Error generating config: {e}")
        flash('Error generating configuration', 'error')
        return redirect(url_for('profiles.index'))

from datetime import datetime
