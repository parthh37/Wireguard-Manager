from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify
from utils.auth import hash_password, verify_password, verify_2fa_token, generate_2fa_secret, generate_2fa_qr, ip_whitelist_required, log_action
from utils.storage import DataStore
from config import Config
from datetime import datetime

auth_bp = Blueprint('auth', __name__)
store = DataStore()

@auth_bp.route('/login', methods=['GET', 'POST'])
@ip_whitelist_required
def login():
    """Login page"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        token_2fa = request.form.get('token_2fa', '')
        
        settings = store.get_settings()
        
        # Check credentials
        if username != Config.ADMIN_USERNAME:
            flash('Invalid credentials', 'error')
            log_action('LOGIN_FAILED', {'reason': 'Invalid username', 'ip': request.remote_addr})
            return render_template('login.html')
        
        if not verify_password(password, settings.get('admin_password_hash', '')):
            flash('Invalid credentials', 'error')
            log_action('LOGIN_FAILED', {'reason': 'Invalid password', 'ip': request.remote_addr})
            return render_template('login.html')
        
        # Check 2FA if enabled
        if Config.ENABLE_2FA:
            secret = settings.get('admin_2fa_secret', '')
            if not secret:
                # 2FA not set up yet
                flash('2FA not configured. Please complete setup.', 'error')
                return redirect(url_for('auth.setup_2fa'))
            
            if not token_2fa:
                flash('2FA token required', 'error')
                return render_template('login.html', require_2fa=True)
            
            if not verify_2fa_token(secret, token_2fa):
                flash('Invalid 2FA token', 'error')
                log_action('LOGIN_FAILED', {'reason': 'Invalid 2FA', 'ip': request.remote_addr})
                return render_template('login.html', require_2fa=True)
        
        # Login successful
        session['logged_in'] = True
        session['username'] = username
        session['last_activity'] = datetime.now().isoformat()
        
        log_action('LOGIN_SUCCESS', {'ip': request.remote_addr})
        
        next_page = request.args.get('next')
        return redirect(next_page or url_for('dashboard.index'))
    
    return render_template('login.html')

@auth_bp.route('/logout')
def logout():
    """Logout"""
    log_action('LOGOUT', {'ip': request.remote_addr})
    session.clear()
    flash('You have been logged out', 'success')
    return redirect(url_for('auth.login'))

@auth_bp.route('/setup', methods=['GET', 'POST'])
@ip_whitelist_required
def setup():
    """Initial setup page"""
    settings = store.get_settings()
    
    if settings.get('initialized'):
        return redirect(url_for('auth.login'))
    
    if request.method == 'POST':
        password = request.form.get('password')
        password_confirm = request.form.get('password_confirm')
        
        if not password or len(password) < 8:
            flash('Password must be at least 8 characters', 'error')
            return render_template('setup.html')
        
        if password != password_confirm:
            flash('Passwords do not match', 'error')
            return render_template('setup.html')
        
        # Save password hash
        settings['admin_password_hash'] = hash_password(password)
        settings['initialized'] = True
        store.save_settings(settings)
        
        log_action('INITIAL_SETUP', {'ip': request.remote_addr})
        
        if Config.ENABLE_2FA:
            flash('Setup complete! Please configure 2FA.', 'success')
            return redirect(url_for('auth.setup_2fa'))
        else:
            flash('Setup complete! Please login.', 'success')
            return redirect(url_for('auth.login'))
    
    return render_template('setup.html')

@auth_bp.route('/setup-2fa', methods=['GET', 'POST'])
@ip_whitelist_required
def setup_2fa():
    """2FA setup page"""
    settings = store.get_settings()
    
    if not settings.get('initialized'):
        return redirect(url_for('auth.setup'))
    
    if request.method == 'POST':
        token = request.form.get('token')
        secret = session.get('2fa_secret')
        
        if not secret:
            flash('Invalid session. Please try again.', 'error')
            return redirect(url_for('auth.setup_2fa'))
        
        if verify_2fa_token(secret, token):
            settings['admin_2fa_secret'] = secret
            store.save_settings(settings)
            session.pop('2fa_secret', None)
            
            log_action('2FA_SETUP', {'ip': request.remote_addr})
            flash('2FA configured successfully!', 'success')
            return redirect(url_for('auth.login'))
        else:
            flash('Invalid token. Please try again.', 'error')
    
    # Generate new secret
    secret = generate_2fa_secret()
    session['2fa_secret'] = secret
    qr_code = generate_2fa_qr(secret, Config.ADMIN_USERNAME)
    
    return render_template('setup_2fa.html', qr_code=qr_code, secret=secret)
