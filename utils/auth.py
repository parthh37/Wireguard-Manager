import pyotp
import qrcode
from io import BytesIO
import base64
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from flask import session, redirect, url_for, request, abort
from datetime import datetime
from config import Config
from utils.storage import DataStore

def generate_2fa_secret() -> str:
    """Generate a new 2FA secret"""
    return pyotp.random_base32()

def generate_2fa_qr(secret: str, username: str) -> str:
    """Generate QR code for 2FA setup"""
    totp = pyotp.TOTP(secret)
    uri = totp.provisioning_uri(
        name=username,
        issuer_name='WireGuard Manager'
    )
    
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(uri)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    
    buffer = BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)
    
    img_str = base64.b64encode(buffer.getvalue()).decode()
    return f"data:image/png;base64,{img_str}"

def verify_2fa_token(secret: str, token: str) -> bool:
    """Verify 2FA token"""
    totp = pyotp.TOTP(secret)
    return totp.verify(token, valid_window=1)

def hash_password(password: str) -> str:
    """Hash password"""
    return generate_password_hash(password, method='pbkdf2:sha256')

def verify_password(password: str, password_hash: str) -> bool:
    """Verify password against hash"""
    return check_password_hash(password_hash, password)

def login_required(f):
    """Decorator to require login"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('logged_in'):
            return redirect(url_for('auth.login', next=request.url))
        
        # Check session timeout
        last_activity = session.get('last_activity')
        if last_activity:
            last_activity_time = datetime.fromisoformat(last_activity)
            if (datetime.now() - last_activity_time).seconds > Config.SESSION_TIMEOUT:
                session.clear()
                return redirect(url_for('auth.login', timeout=1))
        
        session['last_activity'] = datetime.now().isoformat()
        return f(*args, **kwargs)
    return decorated_function

def check_ip_whitelist():
    """Check if request IP is whitelisted"""
    if not Config.IP_WHITELIST:
        return True
    
    client_ip = request.remote_addr
    return client_ip in Config.IP_WHITELIST

def ip_whitelist_required(f):
    """Decorator to require IP whitelist"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not check_ip_whitelist():
            abort(403, description="Access denied: IP not whitelisted")
        return f(*args, **kwargs)
    return decorated_function

def log_action(action: str, details: dict = None):
    """Log action to audit trail"""
    store = DataStore()
    user = session.get('username', 'unknown')
    store.log_audit(action, user, details)
