from flask import Blueprint, render_template, jsonify
from utils.auth import login_required, log_action
from utils.storage import DataStore
from utils.wireguard import WireGuardManager
from utils.helpers import format_bytes, format_timestamp
from datetime import datetime, timedelta

dashboard_bp = Blueprint('dashboard', __name__)
store = DataStore()
wg = WireGuardManager()

@dashboard_bp.route('/')
@login_required
def index():
    """Dashboard home page"""
    try:
        log_action('VIEW_DASHBOARD', {})
        
        clients = store.get_all_clients()
        
        # Calculate statistics
        total_clients = len(clients)
        active_clients = len([c for c in clients if c.get('enabled', True)])
        expired_clients = len([c for c in clients if is_expired(c)])
        
        # Get connected clients (had handshake in last 3 minutes)
        connected = 0
        total_rx = 0
        total_tx = 0
        
        try:
            stats = wg.get_interface_stats()
            for peer in stats.get('peers', []):
                if peer['latest_handshake'] > 0:
                    last_handshake = datetime.now().timestamp() - peer['latest_handshake']
                    if last_handshake < 180:  # 3 minutes
                        connected += 1
                
                total_rx += peer.get('transfer_rx', 0)
                total_tx += peer.get('transfer_tx', 0)
        except Exception as e:
            # WireGuard interface might not be ready yet
            print(f"Warning: Could not get WireGuard stats: {e}")
        
        # Get recent activity
        today = datetime.now().strftime('%Y-%m-%d')
        yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
        
        recent_activity = []
        try:
            for date in [today, yesterday]:
                logs = store.get_audit_logs(date, date)
                for log in logs:
                    recent_activity.extend(log.get('entries', [])[:10])
            
            recent_activity.sort(key=lambda x: x['timestamp'], reverse=True)
            recent_activity = recent_activity[:10]
        except Exception as e:
            print(f"Warning: Could not get recent activity: {e}")
        
        return render_template('dashboard.html',
                             total_clients=total_clients,
                             active_clients=active_clients,
                             expired_clients=expired_clients,
                             connected_clients=connected,
                             total_rx=format_bytes(total_rx),
                             total_tx=format_bytes(total_tx),
                             total_data=format_bytes(total_rx + total_tx),
                             recent_activity=recent_activity)
    except Exception as e:
        print(f"Error in dashboard: {e}")
        import traceback
        traceback.print_exc()
        # Return a simple error page
        return render_template('dashboard.html',
                             total_clients=0,
                             active_clients=0,
                             expired_clients=0,
                             connected_clients=0,
                             total_rx='0 B',
                             total_tx='0 B',
                             total_data='0 B',
                             recent_activity=[],
                             error="Dashboard temporarily unavailable")

@dashboard_bp.route('/api/stats')
@login_required
def api_stats():
    """API endpoint for dashboard statistics"""
    clients = store.get_all_clients()
    stats = wg.get_interface_stats()
    
    connected = 0
    total_rx = 0
    total_tx = 0
    
    for peer in stats.get('peers', []):
        if peer['latest_handshake'] > 0:
            last_handshake = datetime.now().timestamp() - peer['latest_handshake']
            if last_handshake < 180:
                connected += 1
        
        total_rx += peer.get('transfer_rx', 0)
        total_tx += peer.get('transfer_tx', 0)
    
    return jsonify({
        'total_clients': len(clients),
        'connected_clients': connected,
        'total_rx': total_rx,
        'total_tx': total_tx,
        'total_data': total_rx + total_tx
    })

def is_expired(client: dict) -> bool:
    """Check if client is expired"""
    if not client.get('expiry_date'):
        return False
    
    expiry = datetime.fromisoformat(client['expiry_date'])
    return datetime.now() > expiry
