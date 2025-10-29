import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from config import Config

class DataStore:
    """File-based data storage for clients, profiles, and settings"""
    
    def __init__(self):
        self.data_dir = Config.DATA_DIR
        self.clients_dir = os.path.join(self.data_dir, 'clients')
        self.profiles_dir = os.path.join(self.data_dir, 'profiles')
        self.usage_dir = os.path.join(self.data_dir, 'usage')
        self.audit_dir = os.path.join(self.data_dir, 'audit')
        
    def _read_json(self, filepath: str) -> dict:
        """Read JSON file"""
        if not os.path.exists(filepath):
            return {}
        with open(filepath, 'r') as f:
            return json.load(f)
    
    def _write_json(self, filepath: str, data: dict):
        """Write JSON file"""
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2, default=str)
    
    # Client Management
    def get_client(self, client_id: str) -> Optional[Dict]:
        """Get client by ID"""
        filepath = os.path.join(self.clients_dir, f'{client_id}.json')
        return self._read_json(filepath) if os.path.exists(filepath) else None
    
    def get_all_clients(self) -> List[Dict]:
        """Get all clients"""
        clients = []
        if not os.path.exists(self.clients_dir):
            return clients
        
        for filename in os.listdir(self.clients_dir):
            if filename.endswith('.json'):
                filepath = os.path.join(self.clients_dir, filename)
                clients.append(self._read_json(filepath))
        
        return sorted(clients, key=lambda x: x.get('created_at', ''), reverse=True)
    
    def save_client(self, client: Dict):
        """Save client data"""
        filepath = os.path.join(self.clients_dir, f"{client['id']}.json")
        self._write_json(filepath, client)
    
    def delete_client(self, client_id: str):
        """Delete client"""
        filepath = os.path.join(self.clients_dir, f'{client_id}.json')
        if os.path.exists(filepath):
            os.remove(filepath)
    
    # Profile Management
    def get_profile(self, profile_id: str) -> Optional[Dict]:
        """Get profile by ID"""
        filepath = os.path.join(self.profiles_dir, f'{profile_id}.json')
        return self._read_json(filepath) if os.path.exists(filepath) else None
    
    def get_all_profiles(self) -> List[Dict]:
        """Get all profiles"""
        profiles = []
        if not os.path.exists(self.profiles_dir):
            return profiles
        
        for filename in os.listdir(self.profiles_dir):
            if filename.endswith('.json'):
                filepath = os.path.join(self.profiles_dir, filename)
                profiles.append(self._read_json(filepath))
        
        return sorted(profiles, key=lambda x: x.get('name', ''))
    
    def save_profile(self, profile: Dict):
        """Save profile data"""
        filepath = os.path.join(self.profiles_dir, f"{profile['id']}.json")
        self._write_json(filepath, profile)
    
    def delete_profile(self, profile_id: str):
        """Delete profile"""
        filepath = os.path.join(self.profiles_dir, f'{profile_id}.json')
        if os.path.exists(filepath):
            os.remove(filepath)
    
    # Usage Tracking
    def save_usage_snapshot(self, date: str, data: Dict):
        """Save daily usage snapshot"""
        filepath = os.path.join(self.usage_dir, f'{date}.json')
        self._write_json(filepath, data)
    
    def get_usage_snapshot(self, date: str) -> Optional[Dict]:
        """Get usage snapshot for a specific date"""
        filepath = os.path.join(self.usage_dir, f'{date}.json')
        return self._read_json(filepath) if os.path.exists(filepath) else None
    
    def get_usage_range(self, start_date: str, end_date: str) -> List[Dict]:
        """Get usage snapshots for a date range"""
        snapshots = []
        if not os.path.exists(self.usage_dir):
            return snapshots
        
        for filename in os.listdir(self.usage_dir):
            if filename.endswith('.json'):
                date = filename.replace('.json', '')
                if start_date <= date <= end_date:
                    filepath = os.path.join(self.usage_dir, filename)
                    snapshots.append(self._read_json(filepath))
        
        return sorted(snapshots, key=lambda x: x.get('date', ''))
    
    # Audit Logging
    def log_audit(self, action: str, user: str, details: Dict = None):
        """Log audit entry"""
        today = datetime.now().strftime('%Y-%m-%d')
        filepath = os.path.join(self.audit_dir, f'{today}.json')
        
        logs = self._read_json(filepath) if os.path.exists(filepath) else {'date': today, 'entries': []}
        
        entry = {
            'timestamp': datetime.now().isoformat(),
            'action': action,
            'user': user,
            'details': details or {}
        }
        
        logs['entries'].append(entry)
        self._write_json(filepath, logs)
    
    def get_audit_logs(self, start_date: str, end_date: str) -> List[Dict]:
        """Get audit logs for a date range"""
        logs = []
        if not os.path.exists(self.audit_dir):
            return logs
        
        for filename in os.listdir(self.audit_dir):
            if filename.endswith('.json'):
                date = filename.replace('.json', '')
                if start_date <= date <= end_date:
                    filepath = os.path.join(self.audit_dir, filename)
                    logs.append(self._read_json(filepath))
        
        return sorted(logs, key=lambda x: x.get('date', ''), reverse=True)
    
    # Settings
    def get_settings(self) -> Dict:
        """Get application settings"""
        filepath = os.path.join(self.data_dir, 'settings.json')
        default_settings = {
            'admin_2fa_secret': '',
            'admin_password_hash': '',
            'last_client_ip': 2,  # Start from 10.0.0.2
            'initialized': False
        }
        
        if os.path.exists(filepath):
            return {**default_settings, **self._read_json(filepath)}
        return default_settings
    
    def save_settings(self, settings: Dict):
        """Save application settings"""
        filepath = os.path.join(self.data_dir, 'settings.json')
        self._write_json(filepath, settings)
    
    def update_setting(self, key: str, value):
        """Update a single setting"""
        settings = self.get_settings()
        settings[key] = value
        self.save_settings(settings)
