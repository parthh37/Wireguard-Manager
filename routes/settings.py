from flask import Blueprint, render_template, request, redirect, url_for, flash, send_file, jsonify
from utils.auth import login_required, log_action, hash_password
from utils.storage import DataStore
from utils.wireguard import WireGuardManager
from config import Config
import os
import shutil
import tarfile
from datetime import datetime
import io

settings_bp = Blueprint('settings', __name__)
store = DataStore()
wg = WireGuardManager()

@settings_bp.route('/')
@login_required
def index():
    """Settings page"""
    log_action('VIEW_SETTINGS', {})
    
    settings = store.get_settings()
    
    # Get WireGuard status
    wg_status = {
        'interface_up': wg.is_interface_up(),
        'interface': Config.WG_INTERFACE,
        'server_ip': Config.WG_SERVER_IP,
        'server_port': Config.WG_SERVER_PORT,
        'public_ip': Config.SERVER_PUBLIC_IP
    }
    
    # Get backup list
    backups = []
    if os.path.exists(Config.BACKUP_DIR):
        for filename in os.listdir(Config.BACKUP_DIR):
            if filename.endswith('.tar.gz'):
                filepath = os.path.join(Config.BACKUP_DIR, filename)
                stat = os.stat(filepath)
                backups.append({
                    'filename': filename,
                    'size': stat.st_size,
                    'created': datetime.fromtimestamp(stat.st_ctime).strftime('%Y-%m-%d %H:%M:%S')
                })
    
    backups.sort(key=lambda x: x['created'], reverse=True)
    
    return render_template('settings/index.html',
                         settings=settings,
                         wg_status=wg_status,
                         backups=backups,
                         config=Config)

@settings_bp.route('/change-password', methods=['POST'])
@login_required
def change_password():
    """Change admin password"""
    current_password = request.form.get('current_password')
    new_password = request.form.get('new_password')
    confirm_password = request.form.get('confirm_password')
    
    settings = store.get_settings()
    
    # Verify current password
    from utils.auth import verify_password
    if not verify_password(current_password, settings.get('admin_password_hash', '')):
        flash('Current password is incorrect', 'error')
        return redirect(url_for('settings.index'))
    
    # Validate new password
    if len(new_password) < 8:
        flash('New password must be at least 8 characters', 'error')
        return redirect(url_for('settings.index'))
    
    if new_password != confirm_password:
        flash('New passwords do not match', 'error')
        return redirect(url_for('settings.index'))
    
    # Update password
    settings['admin_password_hash'] = hash_password(new_password)
    store.save_settings(settings)
    
    log_action('PASSWORD_CHANGED', {})
    flash('Password changed successfully', 'success')
    return redirect(url_for('settings.index'))

@settings_bp.route('/backup/create', methods=['POST'])
@login_required
def create_backup():
    """Create backup"""
    try:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_filename = f'wireguard_manager_backup_{timestamp}.tar.gz'
        backup_path = os.path.join(Config.BACKUP_DIR, backup_filename)
        
        # Create tar archive
        with tarfile.open(backup_path, 'w:gz') as tar:
            tar.add(Config.DATA_DIR, arcname='data')
        
        log_action('BACKUP_CREATED', {'filename': backup_filename})
        flash('Backup created successfully', 'success')
    except Exception as e:
        flash(f'Backup failed: {str(e)}', 'error')
    
    return redirect(url_for('settings.index'))

@settings_bp.route('/backup/download/<filename>')
@login_required
def download_backup(filename):
    """Download backup file"""
    filepath = os.path.join(Config.BACKUP_DIR, filename)
    
    if not os.path.exists(filepath) or not filename.endswith('.tar.gz'):
        flash('Backup file not found', 'error')
        return redirect(url_for('settings.index'))
    
    log_action('BACKUP_DOWNLOADED', {'filename': filename})
    return send_file(filepath, as_attachment=True, download_name=filename)

@settings_bp.route('/backup/restore/<filename>', methods=['POST'])
@login_required
def restore_backup(filename):
    """Restore from backup"""
    filepath = os.path.join(Config.BACKUP_DIR, filename)
    
    if not os.path.exists(filepath) or not filename.endswith('.tar.gz'):
        flash('Backup file not found', 'error')
        return redirect(url_for('settings.index'))
    
    try:
        # Extract backup
        with tarfile.open(filepath, 'r:gz') as tar:
            tar.extractall(path=Config.DATA_DIR.replace('/data', ''))
        
        log_action('BACKUP_RESTORED', {'filename': filename})
        flash('Backup restored successfully. Please restart the application.', 'success')
    except Exception as e:
        flash(f'Restore failed: {str(e)}', 'error')
    
    return redirect(url_for('settings.index'))

@settings_bp.route('/backup/delete/<filename>', methods=['POST'])
@login_required
def delete_backup(filename):
    """Delete backup file"""
    filepath = os.path.join(Config.BACKUP_DIR, filename)
    
    if not os.path.exists(filepath) or not filename.endswith('.tar.gz'):
        flash('Backup file not found', 'error')
        return redirect(url_for('settings.index'))
    
    try:
        os.remove(filepath)
        log_action('BACKUP_DELETED', {'filename': filename})
        flash('Backup deleted successfully', 'success')
    except Exception as e:
        flash(f'Delete failed: {str(e)}', 'error')
    
    return redirect(url_for('settings.index'))

@settings_bp.route('/wireguard/restart', methods=['POST'])
@login_required
def restart_wireguard():
    """Restart WireGuard interface"""
    try:
        wg.reload_interface()
        log_action('WIREGUARD_RESTARTED', {})
        flash('WireGuard interface restarted successfully', 'success')
    except Exception as e:
        flash(f'Failed to restart WireGuard: {str(e)}', 'error')
    
    return redirect(url_for('settings.index'))
