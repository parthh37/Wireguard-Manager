from flask import Flask, redirect, url_for
from flask_session import Session
import redis
import logging
from logging.handlers import RotatingFileHandler
import os

from config import Config
from routes.auth import auth_bp
from routes.dashboard import dashboard_bp
from routes.clients import clients_bp
from routes.profiles import profiles_bp
from routes.usage import usage_bp
from routes.settings import settings_bp
from routes.audit import audit_bp
from automation import AutomationTasks

# Initialize Flask app
app = Flask(__name__)
app.config.from_object(Config)

# Initialize directories
Config.init_app()

# Configure logging
if not os.path.exists('logs'):
    os.makedirs('logs')

file_handler = RotatingFileHandler(
    'logs/wireguard_manager.log',
    maxBytes=10240000,
    backupCount=10
)
file_handler.setFormatter(logging.Formatter(
    '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
))
file_handler.setLevel(logging.INFO)

app.logger.addHandler(file_handler)
app.logger.setLevel(logging.INFO)
app.logger.info('WireGuard Manager startup')

# Configure session with Redis
try:
    redis_client = redis.from_url(Config.REDIS_URL)
    redis_client.ping()
    app.config['SESSION_REDIS'] = redis_client
    Session(app)
    app.logger.info('Redis session configured')
except Exception as e:
    app.logger.warning(f'Redis not available, using filesystem sessions: {e}')
    app.config['SESSION_TYPE'] = 'filesystem'
    Session(app)

# Register blueprints
app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(dashboard_bp, url_prefix='/')
app.register_blueprint(clients_bp, url_prefix='/clients')
app.register_blueprint(profiles_bp, url_prefix='/profiles')
app.register_blueprint(usage_bp, url_prefix='/usage')
app.register_blueprint(settings_bp, url_prefix='/settings')
app.register_blueprint(audit_bp, url_prefix='/audit')

# Initialize automation tasks
automation = AutomationTasks()

@app.before_request
def before_request():
    """Check if initial setup is required"""
    from flask import request, session
    from utils.storage import DataStore
    
    # Skip for static files
    if request.endpoint and 'static' in request.endpoint:
        return
    
    # Skip for setup routes
    if request.endpoint and ('auth.setup' in request.endpoint or 'auth.setup_2fa' in request.endpoint):
        return
    
    store = DataStore()
    settings = store.get_settings()
    
    # Redirect to setup if not initialized
    if not settings.get('initialized') and request.endpoint != 'auth.setup':
        return redirect(url_for('auth.setup'))

@app.route('/')
def index():
    """Root route"""
    return redirect(url_for('dashboard.index'))

@app.route('/health')
def health_check():
    """Health check endpoint for monitoring"""
    from flask import jsonify
    from utils.wireguard import WireGuardManager
    from utils.storage import DataStore
    
    try:
        wg = WireGuardManager()
        store = DataStore()
        
        # Get WireGuard service status
        wg_status = wg.get_service_status()
        
        # Check if data storage is accessible
        try:
            store.get_settings()
            storage_ok = True
        except:
            storage_ok = False
        
        # Overall health status
        overall_status = 'healthy' if (wg_status['status'] == 'healthy' and storage_ok) else 'unhealthy'
        
        return jsonify({
            'status': overall_status,
            'wireguard': wg_status,
            'storage': 'ok' if storage_ok else 'error',
            'version': '1.0.0'
        }), 200 if overall_status == 'healthy' else 503
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500

@app.errorhandler(404)
def not_found_error(error):
    """404 error handler"""
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    """500 error handler"""
    app.logger.error(f'Server Error: {error}')
    return render_template('errors/500.html'), 500

@app.errorhandler(403)
def forbidden_error(error):
    """403 error handler"""
    return render_template('errors/403.html'), 403

# Start automation tasks
try:
    automation.start()
    app.logger.info('Automation tasks started')
except Exception as e:
    app.logger.error(f'Failed to start automation tasks: {e}')

# Cleanup on shutdown
import atexit

@atexit.register
def cleanup():
    """Cleanup on application shutdown"""
    automation.stop()
    app.logger.info('WireGuard Manager shutdown')

from flask import render_template

if __name__ == '__main__':
    # For development only
    app.run(host='127.0.0.1', port=5000, debug=False)
