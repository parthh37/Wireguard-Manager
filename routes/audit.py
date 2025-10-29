from flask import Blueprint, render_template, request
from utils.auth import login_required, log_action
from utils.storage import DataStore
from datetime import datetime, timedelta

audit_bp = Blueprint('audit', __name__)
store = DataStore()

@audit_bp.route('/')
@login_required
def index():
    """Audit log page"""
    log_action('VIEW_AUDIT_LOG', {})
    
    # Get date range from query params
    days = request.args.get('days', 7, type=int)
    
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    
    logs = store.get_audit_logs(
        start_date.strftime('%Y-%m-%d'),
        end_date.strftime('%Y-%m-%d')
    )
    
    # Flatten entries
    all_entries = []
    for log in logs:
        for entry in log.get('entries', []):
            entry['date'] = log.get('date')
            all_entries.append(entry)
    
    # Sort by timestamp descending
    all_entries.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
    
    return render_template('audit/index.html', logs=all_entries, days=days)
