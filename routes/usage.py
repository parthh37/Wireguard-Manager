from flask import Blueprint, render_template, jsonify
from utils.auth import login_required, log_action
from utils.storage import DataStore
from utils.wireguard import WireGuardManager
from utils.helpers import format_bytes
from datetime import datetime, timedelta

usage_bp = Blueprint('usage', __name__)
store = DataStore()
wg = WireGuardManager()

@usage_bp.route('/')
@login_required
def index():
    """Usage tracking page"""
    log_action('VIEW_USAGE', {})
    
    clients = store.get_all_clients()
    stats = wg.get_interface_stats()
    
    # Get current usage
    peer_stats = {p['public_key']: p for p in stats.get('peers', [])}
    
    client_usage = []
    for client in clients:
        peer = peer_stats.get(client.get('public_key'))
        if peer:
            client_usage.append({
                'id': client['id'],
                'name': client['name'],
                'ip_address': client['ip_address'],
                'transfer_rx': peer['transfer_rx'],
                'transfer_tx': peer['transfer_tx'],
                'transfer_total': peer['transfer_rx'] + peer['transfer_tx'],
                'transfer_rx_formatted': format_bytes(peer['transfer_rx']),
                'transfer_tx_formatted': format_bytes(peer['transfer_tx']),
                'transfer_total_formatted': format_bytes(peer['transfer_rx'] + peer['transfer_tx'])
            })
        else:
            client_usage.append({
                'id': client['id'],
                'name': client['name'],
                'ip_address': client['ip_address'],
                'transfer_rx': 0,
                'transfer_tx': 0,
                'transfer_total': 0,
                'transfer_rx_formatted': '0 B',
                'transfer_tx_formatted': '0 B',
                'transfer_total_formatted': '0 B'
            })
    
    # Sort by total usage
    client_usage.sort(key=lambda x: x['transfer_total'], reverse=True)
    
    # Get historical data
    today = datetime.now()
    dates = [(today - timedelta(days=i)).strftime('%Y-%m-%d') for i in range(30, -1, -1)]
    
    historical_data = []
    for date in dates:
        snapshot = store.get_usage_snapshot(date)
        if snapshot:
            historical_data.append(snapshot)
    
    return render_template('usage/index.html', 
                         client_usage=client_usage,
                         historical_data=historical_data)

@usage_bp.route('/api/chart-data')
@login_required
def chart_data():
    """Get chart data for usage over time"""
    days = request.args.get('days', 30, type=int)
    
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    
    snapshots = store.get_usage_range(
        start_date.strftime('%Y-%m-%d'),
        end_date.strftime('%Y-%m-%d')
    )
    
    # Format for chart
    labels = []
    rx_data = []
    tx_data = []
    
    for snapshot in snapshots:
        labels.append(snapshot.get('date', ''))
        
        total_rx = snapshot.get('total_rx', 0)
        total_tx = snapshot.get('total_tx', 0)
        
        rx_data.append(total_rx / (1024 ** 3))  # Convert to GB
        tx_data.append(total_tx / (1024 ** 3))
    
    return jsonify({
        'labels': labels,
        'datasets': [
            {
                'label': 'Download',
                'data': rx_data,
                'borderColor': 'rgb(75, 192, 192)',
                'backgroundColor': 'rgba(75, 192, 192, 0.2)'
            },
            {
                'label': 'Upload',
                'data': tx_data,
                'borderColor': 'rgb(255, 99, 132)',
                'backgroundColor': 'rgba(255, 99, 132, 0.2)'
            }
        ]
    })

from flask import request
