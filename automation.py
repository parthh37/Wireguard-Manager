from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, timedelta
from utils.storage import DataStore
from utils.wireguard import WireGuardManager
from config import Config
import os
import tarfile
import logging

logger = logging.getLogger(__name__)

class AutomationTasks:
    """Automated tasks for WireGuard Manager"""
    
    def __init__(self):
        self.store = DataStore()
        self.wg = WireGuardManager()
        self.scheduler = BackgroundScheduler()
    
    def start(self):
        """Start all scheduled tasks"""
        # Check expired clients every hour
        self.scheduler.add_job(
            self.check_expired_clients,
            'interval',
            hours=1,
            id='check_expired'
        )
        
        # Record usage stats daily at 00:00
        self.scheduler.add_job(
            self.record_daily_usage,
            'cron',
            hour=0,
            minute=0,
            id='daily_usage'
        )
        
        # Create backup if enabled
        if Config.AUTO_BACKUP_ENABLED:
            self.scheduler.add_job(
                self.create_auto_backup,
                'cron',
                hour=Config.AUTO_BACKUP_HOUR,
                minute=0,
                id='auto_backup'
            )
        
        # Clean old backups daily
        self.scheduler.add_job(
            self.clean_old_backups,
            'cron',
            hour=Config.AUTO_BACKUP_HOUR,
            minute=30,
            id='clean_backups'
        )
        
        self.scheduler.start()
        logger.info("Automation tasks started")
    
    def stop(self):
        """Stop scheduler"""
        if self.scheduler.running:
            self.scheduler.shutdown()
            logger.info("Automation tasks stopped")
    
    def check_expired_clients(self):
        """Disable expired clients"""
        logger.info("Checking for expired clients...")
        
        clients = self.store.get_all_clients()
        disabled_count = 0
        
        for client in clients:
            if not client.get('enabled', True):
                continue
            
            if not client.get('expiry_date'):
                continue
            
            expiry = datetime.fromisoformat(client['expiry_date'])
            if datetime.now() > expiry:
                try:
                    # Disable client
                    self.wg.remove_peer(client['public_key'])
                    client['enabled'] = False
                    self.store.save_client(client)
                    
                    self.store.log_audit(
                        'CLIENT_AUTO_DISABLED',
                        'system',
                        {'client_id': client['id'], 'name': client['name'], 'reason': 'expired'}
                    )
                    
                    disabled_count += 1
                    logger.info(f"Disabled expired client: {client['name']}")
                except Exception as e:
                    logger.error(f"Failed to disable client {client['name']}: {e}")
        
        if disabled_count > 0:
            logger.info(f"Disabled {disabled_count} expired client(s)")
        else:
            logger.info("No expired clients found")
    
    def record_daily_usage(self):
        """Record daily usage statistics"""
        logger.info("Recording daily usage statistics...")
        
        try:
            stats = self.wg.get_interface_stats()
            clients = self.store.get_all_clients()
            
            # Build usage snapshot
            snapshot = {
                'date': datetime.now().strftime('%Y-%m-%d'),
                'timestamp': datetime.now().isoformat(),
                'total_rx': 0,
                'total_tx': 0,
                'clients': []
            }
            
            peer_stats = {p['public_key']: p for p in stats.get('peers', [])}
            
            for client in clients:
                peer = peer_stats.get(client.get('public_key'))
                if peer:
                    client_data = {
                        'id': client['id'],
                        'name': client['name'],
                        'transfer_rx': peer['transfer_rx'],
                        'transfer_tx': peer['transfer_tx'],
                        'transfer_total': peer['transfer_rx'] + peer['transfer_tx']
                    }
                    
                    snapshot['total_rx'] += peer['transfer_rx']
                    snapshot['total_tx'] += peer['transfer_tx']
                    snapshot['clients'].append(client_data)
            
            self.store.save_usage_snapshot(snapshot['date'], snapshot)
            
            self.store.log_audit(
                'USAGE_RECORDED',
                'system',
                {'date': snapshot['date'], 'total_clients': len(snapshot['clients'])}
            )
            
            logger.info(f"Recorded usage for {len(snapshot['clients'])} client(s)")
        except Exception as e:
            logger.error(f"Failed to record daily usage: {e}")
    
    def create_auto_backup(self):
        """Create automatic backup"""
        logger.info("Creating automatic backup...")
        
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_filename = f'auto_backup_{timestamp}.tar.gz'
            backup_path = os.path.join(Config.BACKUP_DIR, backup_filename)
            
            # Create tar archive
            with tarfile.open(backup_path, 'w:gz') as tar:
                tar.add(Config.DATA_DIR, arcname='data')
            
            self.store.log_audit(
                'AUTO_BACKUP_CREATED',
                'system',
                {'filename': backup_filename}
            )
            
            logger.info(f"Auto backup created: {backup_filename}")
        except Exception as e:
            logger.error(f"Failed to create auto backup: {e}")
    
    def clean_old_backups(self):
        """Remove old backups"""
        logger.info("Cleaning old backups...")
        
        try:
            if not os.path.exists(Config.BACKUP_DIR):
                return
            
            retention_seconds = Config.BACKUP_RETENTION_DAYS * 24 * 3600
            now = datetime.now().timestamp()
            removed_count = 0
            
            for filename in os.listdir(Config.BACKUP_DIR):
                if not filename.endswith('.tar.gz'):
                    continue
                
                filepath = os.path.join(Config.BACKUP_DIR, filename)
                file_age = now - os.path.getctime(filepath)
                
                if file_age > retention_seconds:
                    os.remove(filepath)
                    removed_count += 1
                    logger.info(f"Removed old backup: {filename}")
            
            if removed_count > 0:
                self.store.log_audit(
                    'OLD_BACKUPS_CLEANED',
                    'system',
                    {'removed_count': removed_count}
                )
                logger.info(f"Removed {removed_count} old backup(s)")
        except Exception as e:
            logger.error(f"Failed to clean old backups: {e}")
