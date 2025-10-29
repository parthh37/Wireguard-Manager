import os
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Flask
    SECRET_KEY = os.getenv('SECRET_KEY', os.urandom(32).hex())
    SESSION_TYPE = 'redis'
    SESSION_PERMANENT = True
    PERMANENT_SESSION_LIFETIME = timedelta(seconds=int(os.getenv('SESSION_TIMEOUT', 1800)))
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # Redis
    REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
    
    # Admin
    ADMIN_USERNAME = os.getenv('ADMIN_USERNAME', 'admin')
    ADMIN_PASSWORD_HASH = os.getenv('ADMIN_PASSWORD_HASH', '')
    
    # WireGuard
    WG_INTERFACE = os.getenv('WG_INTERFACE', 'wg0')
    WG_SERVER_IP = os.getenv('WG_SERVER_IP', '10.0.0.1')
    WG_SERVER_PORT = int(os.getenv('WG_SERVER_PORT', 51820))
    WG_SERVER_PUBLIC_KEY = os.getenv('WG_SERVER_PUBLIC_KEY', '')
    WG_SERVER_PRIVATE_KEY = os.getenv('WG_SERVER_PRIVATE_KEY', '')
    WG_ALLOWED_IPS = os.getenv('WG_ALLOWED_IPS', '0.0.0.0/0,::/0')
    WG_DNS = os.getenv('WG_DNS', '1.1.1.1,1.0.0.1')
    WG_MTU = int(os.getenv('WG_MTU', 1420))
    WG_PERSISTENT_KEEPALIVE = int(os.getenv('WG_PERSISTENT_KEEPALIVE', 25))
    
    # Server
    SERVER_PUBLIC_IP = os.getenv('SERVER_PUBLIC_IP', '')
    SERVER_PUBLIC_IPV6 = os.getenv('SERVER_PUBLIC_IPV6', '')
    WG_SUBNET = os.getenv('WG_SUBNET', '10.0.0.0/24')
    
    # IPv6 Configuration
    WG_IPV6_ENABLED = os.getenv('WG_IPV6_ENABLED', 'True').lower() == 'true'
    WG_IPV6_SUBNET = os.getenv('WG_IPV6_SUBNET', '')
    WG_SERVER_IPV6 = os.getenv('WG_SERVER_IPV6', '')
    IPV6_PUBLIC_ROUTING = os.getenv('IPV6_PUBLIC_ROUTING', 'True').lower() == 'true'
    
    # Security
    SESSION_TIMEOUT = int(os.getenv('SESSION_TIMEOUT', 1800))
    MAX_LOGIN_ATTEMPTS = int(os.getenv('MAX_LOGIN_ATTEMPTS', 5))
    IP_WHITELIST = [ip.strip() for ip in os.getenv('IP_WHITELIST', '').split(',') if ip.strip()]
    ENABLE_2FA = os.getenv('ENABLE_2FA', 'True').lower() == 'true'
    
    # Directories
    DATA_DIR = os.getenv('DATA_DIR', './data')
    BACKUP_DIR = os.getenv('BACKUP_DIR', './backups')
    
    # Backup
    BACKUP_RETENTION_DAYS = int(os.getenv('BACKUP_RETENTION_DAYS', 30))
    AUTO_BACKUP_ENABLED = os.getenv('AUTO_BACKUP_ENABLED', 'True').lower() == 'true'
    AUTO_BACKUP_HOUR = int(os.getenv('AUTO_BACKUP_HOUR', 2))
    
    @staticmethod
    def init_app():
        """Initialize application directories"""
        os.makedirs(Config.DATA_DIR, exist_ok=True)
        os.makedirs(Config.BACKUP_DIR, exist_ok=True)
        os.makedirs(os.path.join(Config.DATA_DIR, 'clients'), exist_ok=True)
        os.makedirs(os.path.join(Config.DATA_DIR, 'profiles'), exist_ok=True)
        os.makedirs(os.path.join(Config.DATA_DIR, 'usage'), exist_ok=True)
        os.makedirs(os.path.join(Config.DATA_DIR, 'audit'), exist_ok=True)
        os.makedirs('logs', exist_ok=True)
