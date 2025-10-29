from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, send_file
from utils.auth import login_required, log_action
from utils.storage import DataStore
from utils.wireguard import WireGuardManager
from utils.helpers import generate_qr_code, format_bytes, format_timestamp
from config import Config
from datetime import datetime, timedelta
import uuid
import io

clients_bp = Blueprint('clients', __name__)
store = DataStore()
wg = WireGuardManager()

@clients_bp.route('/')
@login_required
def index():
    """List all clients"""
    log_action('VIEW_CLIENTS', {})
    
    clients = store.get_all_clients()
    profiles = store.get_all_profiles()
    stats = wg.get_interface_stats()
    
    # Enrich clients with stats
    peer_stats = {p['public_key']: p for p in stats.get('peers', [])}
    
    for client in clients:
        peer = peer_stats.get(client.get('public_key'))
        if peer:
            client['stats'] = {
                'connected': peer['latest_handshake'] > 0 and (datetime.now().timestamp() - peer['latest_handshake'] < 180),
                'last_handshake': format_timestamp(peer['latest_handshake']),
                'transfer_rx': format_bytes(peer['transfer_rx']),
                'transfer_tx': format_bytes(peer['transfer_tx']),
                'transfer_total': format_bytes(peer['transfer_rx'] + peer['transfer_tx'])
            }
        else:
            client['stats'] = {
                'connected': False,
                'last_handshake': 'Never',
                'transfer_rx': '0 B',
                'transfer_tx': '0 B',
                'transfer_total': '0 B'
            }
        
        # Check expiry
        if client.get('expiry_date'):
            expiry = datetime.fromisoformat(client['expiry_date'])
            client['is_expired'] = datetime.now() > expiry
            client['expiry_formatted'] = expiry.strftime('%Y-%m-%d %H:%M')
        else:
            client['is_expired'] = False
            client['expiry_formatted'] = 'Never'
    
    return render_template('clients/list.html', clients=clients, profiles=profiles)

@clients_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add():
    """Add new client"""
    profiles = store.get_all_profiles()
    
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        profile_id = request.form.get('profile_id')
        expiry_days = request.form.get('expiry_days', type=int)
        notes = request.form.get('notes', '').strip()
        
        if not name:
            flash('Client name is required', 'error')
            return render_template('clients/add.html', profiles=profiles)
        
        # Get profile
        profile = store.get_profile(profile_id) if profile_id else None
        if not profile and profiles:
            profile = profiles[0]  # Use first profile as default
        
        if not profile:
            flash('No profiles available. Please create a profile first.', 'error')
            return redirect(url_for('profiles.index'))
        
        # Generate keys
        private_key, public_key = wg.generate_keypair()
        preshared_key = wg.generate_preshared_key()
        
        # Get next IP
        settings = store.get_settings()
        last_ip = settings.get('last_client_ip', 2)
        ip_address = wg.get_next_ip(last_ip)
        
        # Get next IPv6 if enabled
        ipv6_address = ''
        if Config.WG_IPV6_ENABLED:
            ipv6_address = wg.get_next_ipv6(last_ip)
        
        # Calculate expiry
        expiry_date = None
        if expiry_days and expiry_days > 0:
            expiry_date = (datetime.now() + timedelta(days=expiry_days)).isoformat()
        
        # Create client
        client_id = str(uuid.uuid4())
        client = {
            'id': client_id,
            'name': name,
            'ip_address': ip_address,
            'ipv6_address': ipv6_address,
            'public_key': public_key,
            'private_key': private_key,
            'preshared_key': preshared_key,
            'profile_id': profile['id'],
            'profile_name': profile['name'],
            'created_at': datetime.now().isoformat(),
            'expiry_date': expiry_date,
            'enabled': True,
            'notes': notes
        }
        
        # Save client
        store.save_client(client)
        
        # Update last IP
        settings['last_client_ip'] = last_ip + 1
        store.save_settings(settings)
        
        # Add peer to WireGuard
        try:
            allowed_ips = f"{ip_address}/32"
            if ipv6_address:
                allowed_ips += f",{ipv6_address}/128"
            
            wg.add_peer(public_key, preshared_key, allowed_ips)
            log_action('CLIENT_ADDED', {'client_id': client_id, 'name': name})
            flash(f'Client "{name}" added successfully!', 'success')
            return redirect(url_for('clients.view', client_id=client_id))
        except Exception as e:
            # Rollback
            store.delete_client(client_id)
            flash(f'Failed to add client: {str(e)}', 'error')
            return render_template('clients/add.html', profiles=profiles)
    
    return render_template('clients/add.html', profiles=profiles)

@clients_bp.route('/<client_id>')
@login_required
def view(client_id):
    """View client details"""
    client = store.get_client(client_id)
    if not client:
        flash('Client not found', 'error')
        return redirect(url_for('clients.index'))
    
    log_action('VIEW_CLIENT', {'client_id': client_id})
    
    # Get profile
    profile = store.get_profile(client.get('profile_id', ''))
    if not profile:
        profile = {'name': 'Default', 'dns': '', 'allowed_ips': ''}
    
    # Generate config
    config_content = wg.generate_client_config(client, profile)
    
    # Generate QR code
    qr_code = generate_qr_code(config_content)
    
    # Get stats
    stats = wg.get_interface_stats()
    peer_stats = next((p for p in stats.get('peers', []) if p['public_key'] == client.get('public_key')), None)
    
    if peer_stats:
        client['stats'] = {
            'connected': peer_stats['latest_handshake'] > 0 and (datetime.now().timestamp() - peer_stats['latest_handshake'] < 180),
            'last_handshake': format_timestamp(peer_stats['latest_handshake']),
            'transfer_rx': format_bytes(peer_stats['transfer_rx']),
            'transfer_tx': format_bytes(peer_stats['transfer_tx']),
            'transfer_total': format_bytes(peer_stats['transfer_rx'] + peer_stats['transfer_tx']),
            'endpoint': peer_stats.get('endpoint', 'N/A')
        }
    else:
        client['stats'] = {
            'connected': False,
            'last_handshake': 'Never',
            'transfer_rx': '0 B',
            'transfer_tx': '0 B',
            'transfer_total': '0 B',
            'endpoint': 'N/A'
        }
    
    return render_template('clients/view.html', client=client, config=config_content, qr_code=qr_code, profile=profile)

@clients_bp.route('/<client_id>/download')
@login_required
def download(client_id):
    """Download client configuration"""
    client = store.get_client(client_id)
    if not client:
        flash('Client not found', 'error')
        return redirect(url_for('clients.index'))
    
    log_action('DOWNLOAD_CONFIG', {'client_id': client_id, 'name': client.get('name')})
    
    profile = store.get_profile(client.get('profile_id', ''))
    if not profile:
        profile = {'name': 'Default', 'dns': '', 'allowed_ips': ''}
    
    config_content = wg.generate_client_config(client, profile)
    
    buffer = io.BytesIO()
    buffer.write(config_content.encode('utf-8'))
    buffer.seek(0)
    
    filename = f"{client['name'].replace(' ', '_')}.conf"
    
    return send_file(buffer, as_attachment=True, download_name=filename, mimetype='text/plain')

@clients_bp.route('/<client_id>/delete', methods=['POST'])
@login_required
def delete(client_id):
    """Delete client"""
    client = store.get_client(client_id)
    if not client:
        flash('Client not found', 'error')
        return redirect(url_for('clients.index'))
    
    # Remove from WireGuard
    try:
        wg.remove_peer(client['public_key'])
    except Exception as e:
        flash(f'Warning: Failed to remove from WireGuard: {str(e)}', 'warning')
    
    # Delete from storage
    store.delete_client(client_id)
    
    log_action('CLIENT_DELETED', {'client_id': client_id, 'name': client.get('name')})
    flash(f'Client "{client["name"]}" deleted successfully', 'success')
    
    return redirect(url_for('clients.index'))

@clients_bp.route('/<client_id>/toggle', methods=['POST'])
@login_required
def toggle(client_id):
    """Enable/disable client"""
    client = store.get_client(client_id)
    if not client:
        return jsonify({'success': False, 'error': 'Client not found'}), 404
    
    new_state = not client.get('enabled', True)
    client['enabled'] = new_state
    
    if new_state:
        # Enable - add peer
        try:
            allowed_ips = f"{client['ip_address']}/32"
            if client.get('ipv6_address'):
                allowed_ips += f",{client['ipv6_address']}/128"
            
            wg.add_peer(client['public_key'], client['preshared_key'], allowed_ips)
            store.save_client(client)
            log_action('CLIENT_ENABLED', {'client_id': client_id, 'name': client.get('name')})
            return jsonify({'success': True, 'enabled': True})
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500
    else:
        # Disable - remove peer
        try:
            wg.remove_peer(client['public_key'])
            store.save_client(client)
            log_action('CLIENT_DISABLED', {'client_id': client_id, 'name': client.get('name')})
            return jsonify({'success': True, 'enabled': False})
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500

@clients_bp.route('/<client_id>/extend', methods=['POST'])
@login_required
def extend(client_id):
    """Extend client expiry"""
    client = store.get_client(client_id)
    if not client:
        return jsonify({'success': False, 'error': 'Client not found'}), 404
    
    days = request.json.get('days', 30)
    
    if client.get('expiry_date'):
        expiry = datetime.fromisoformat(client['expiry_date'])
        # Extend from current expiry or now, whichever is later
        base_date = max(expiry, datetime.now())
    else:
        base_date = datetime.now()
    
    new_expiry = base_date + timedelta(days=days)
    client['expiry_date'] = new_expiry.isoformat()
    
    store.save_client(client)
    log_action('CLIENT_EXTENDED', {'client_id': client_id, 'name': client.get('name'), 'days': days})
    
    return jsonify({
        'success': True,
        'expiry_date': new_expiry.strftime('%Y-%m-%d %H:%M')
    })
