import subprocess
import os
import ipaddress
from typing import Dict, Optional, Tuple
from config import Config

class WireGuardManager:
    """Manage WireGuard interface and configurations"""
    
    def __init__(self):
        self.interface = Config.WG_INTERFACE
        self.config_path = f'/etc/wireguard/{self.interface}.conf'
    
    def generate_keypair(self) -> Tuple[str, str]:
        """Generate WireGuard private and public key pair"""
        try:
            # Generate private key (use full sudo path)
            private_key = subprocess.check_output(
                ['/usr/bin/sudo', '/usr/bin/wg', 'genkey'],
                stderr=subprocess.PIPE
            ).decode().strip()
            
            # Generate public key from private key
            public_key = subprocess.check_output(
                ['/usr/bin/sudo', '/usr/bin/wg', 'pubkey'],
                input=private_key.encode(),
                stderr=subprocess.PIPE
            ).decode().strip()
            
            return private_key, public_key
        except subprocess.CalledProcessError as e:
            raise Exception(f"Failed to generate keypair: {e}")
    
    def generate_preshared_key(self) -> str:
        """Generate WireGuard preshared key"""
        try:
            psk = subprocess.check_output(
                ['/usr/bin/sudo', '/usr/bin/wg', 'genpsk'],
                stderr=subprocess.PIPE
            ).decode().strip()
            return psk
        except subprocess.CalledProcessError as e:
            raise Exception(f"Failed to generate preshared key: {e}")
    
    def get_next_ip(self, current_ip: int) -> str:
        """Get next available IPv4 address"""
        network = ipaddress.ip_network(Config.WG_SUBNET)
        # Server uses .1, start clients from .2
        ip_int = current_ip
        next_ip = str(network.network_address + ip_int)
        
        return next_ip
    
    def get_next_ipv6(self, current_ip: int) -> str:
        """Get next available IPv6 address from subnet"""
        if not Config.WG_IPV6_ENABLED or not Config.WG_IPV6_SUBNET:
            return ''
        
        network = ipaddress.ip_network(Config.WG_IPV6_SUBNET)
        # Server uses ::1, start clients from ::2
        next_ip = str(network.network_address + current_ip)
        
        return next_ip
    
    def add_peer(self, public_key: str, preshared_key: str, allowed_ips: str):
        """Add peer to WireGuard interface"""
        try:
            cmd = [
                'sudo', 'wg', 'set', self.interface,
                'peer', public_key,
                'preshared-key', '/dev/stdin',
                'allowed-ips', allowed_ips
            ]
            
            subprocess.run(
                cmd,
                input=preshared_key.encode(),
                check=True,
                capture_output=True
            )
            
            # Save configuration
            self.save_config()
            return True
        except subprocess.CalledProcessError as e:
            raise Exception(f"Failed to add peer: {e}")
    
    def remove_peer(self, public_key: str):
        """Remove peer from WireGuard interface"""
        try:
            subprocess.run(
                ['sudo', 'wg', 'set', self.interface, 'peer', public_key, 'remove'],
                check=True,
                capture_output=True
            )
            
            # Save configuration
            self.save_config()
            return True
        except subprocess.CalledProcessError as e:
            raise Exception(f"Failed to remove peer: {e}")
    
    def save_config(self):
        """Save current WireGuard configuration"""
        try:
            # Get current config from wg command
            result = subprocess.run(
                ['sudo', 'wg', 'showconf', self.interface],
                capture_output=True,
                text=True,
                check=True
            )
            
            # Write configuration
            with open(self.config_path, 'w') as f:
                f.write(result.stdout)
            
            return True
        except Exception as e:
            # If interface doesn't exist yet, that's okay
            pass
    
    def get_interface_stats(self) -> Dict:
        """Get WireGuard interface statistics"""
        try:
            result = subprocess.run(
                ['sudo', 'wg', 'show', self.interface, 'dump'],
                capture_output=True,
                text=True,
                check=True
            )
            
            lines = result.stdout.strip().split('\n')
            peers = []
            
            for line in lines[1:]:  # Skip header
                parts = line.split('\t')
                if len(parts) >= 8:
                    peers.append({
                        'public_key': parts[0],
                        'preshared_key': parts[1] if parts[1] != '(none)' else None,
                        'endpoint': parts[2] if parts[2] != '(none)' else None,
                        'allowed_ips': parts[3],
                        'latest_handshake': int(parts[4]),
                        'transfer_rx': int(parts[5]),
                        'transfer_tx': int(parts[6]),
                        'persistent_keepalive': parts[7] if parts[7] != 'off' else None
                    })
            
            return {'peers': peers}
        except subprocess.CalledProcessError:
            return {'peers': []}
    
    def generate_client_config(self, client: Dict, profile: Dict) -> str:
        """Generate client configuration file content"""
        
        # Build Address line with both IPv4 and IPv6 if enabled
        addresses = [f"{client['ip_address']}/32"]
        if Config.WG_IPV6_ENABLED and client.get('ipv6_address'):
            addresses.append(f"{client['ipv6_address']}/128")
        
        address_line = ', '.join(addresses)
        
        # Build Endpoint with IPv6 if available
        if Config.SERVER_PUBLIC_IPV6 and profile.get('use_ipv6_endpoint', False):
            endpoint = f"[{Config.SERVER_PUBLIC_IPV6}]:{Config.WG_SERVER_PORT}"
        else:
            endpoint = f"{Config.SERVER_PUBLIC_IP}:{Config.WG_SERVER_PORT}"
        
        # Get MTU from profile or use default
        mtu = profile.get('mtu', Config.WG_MTU) or Config.WG_MTU
        
        # Get persistent keepalive from profile or use default
        keepalive = profile.get('persistent_keepalive', Config.WG_PERSISTENT_KEEPALIVE) or Config.WG_PERSISTENT_KEEPALIVE
        
        config = f"""[Interface]
PrivateKey = {client['private_key']}
Address = {address_line}
DNS = {profile.get('dns', Config.WG_DNS)}
MTU = {mtu}

[Peer]
PublicKey = {Config.WG_SERVER_PUBLIC_KEY}
PresharedKey = {client['preshared_key']}
Endpoint = {endpoint}
AllowedIPs = {profile.get('allowed_ips', Config.WG_ALLOWED_IPS)}
PersistentKeepalive = {keepalive}
"""
        return config
    
    def is_interface_up(self) -> bool:
        """Check if WireGuard interface is up"""
        try:
            result = subprocess.run(
                ['wg', 'show', self.interface],
                capture_output=True,
                check=True
            )
            return True
        except subprocess.CalledProcessError:
            return False
    
    def get_service_status(self) -> Dict:
        """Get WireGuard service status and health information"""
        try:
            # Check if service is active
            service_result = subprocess.run(
                ['/usr/bin/systemctl', 'is-active', f'wg-quick@{self.interface}'],
                capture_output=True,
                text=True
            )
            is_active = service_result.stdout.strip() == 'active'
            
            # Check if interface is up
            interface_up = self.is_interface_up()
            
            # Get peer count
            peer_count = 0
            if interface_up:
                try:
                    stats = self.get_stats()
                    peer_count = len(stats.get('peers', []))
                except:
                    pass
            
            # Get uptime
            uptime = 'Unknown'
            try:
                uptime_result = subprocess.run(
                    ['/usr/bin/systemctl', 'show', f'wg-quick@{self.interface}', '-p', 'ActiveEnterTimestamp'],
                    capture_output=True,
                    text=True
                )
                if uptime_result.returncode == 0:
                    timestamp_line = uptime_result.stdout.strip()
                    if '=' in timestamp_line:
                        uptime = timestamp_line.split('=', 1)[1]
            except:
                pass
            
            return {
                'service_active': is_active,
                'interface_up': interface_up,
                'peer_count': peer_count,
                'uptime': uptime,
                'status': 'healthy' if (is_active and interface_up) else 'unhealthy'
            }
        except Exception as e:
            return {
                'service_active': False,
                'interface_up': False,
                'peer_count': 0,
                'uptime': 'Unknown',
                'status': 'error',
                'error': str(e)
            }
    
    def reload_interface(self):
        """Reload WireGuard interface"""
        try:
            subprocess.run(['wg-quick', 'down', self.interface], check=False)
            subprocess.run(['wg-quick', 'up', self.interface], check=True)
            return True
        except subprocess.CalledProcessError as e:
            raise Exception(f"Failed to reload interface: {e}")
