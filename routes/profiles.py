from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from utils.auth import login_required, log_action
from utils.storage import DataStore
from config import Config
import uuid

profiles_bp = Blueprint('profiles', __name__)
store = DataStore()

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

@profiles_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add():
    """Add new profile"""
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        description = request.form.get('description', '').strip()
        allowed_ips = request.form.get('allowed_ips', Config.WG_ALLOWED_IPS).strip()
        dns = request.form.get('dns', Config.WG_DNS).strip()
        
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

from datetime import datetime
