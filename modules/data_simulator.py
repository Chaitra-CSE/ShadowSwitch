# Simulates IoT device telemetry with realistic patterns
import numpy as np
import pandas as pd
from datetime import datetime
import random

class IoTSimulator:
    def __init__(self, device_id="FACTORY_CAM_07", device_type="camera"):
        self.device_id = device_id
        self.device_type = device_type
        
        # Different baselines per device type
        if device_type == "camera":
            self.baseline = {
                'signal': 96.5,
                'packet_loss': 1.8,
                'latency': 14.2,
                'channel': 'Li-Fi',
                'encryption': 'AES-256'
            }
        elif device_type == "sensor":
            self.baseline = {
                'signal': 92.0,
                'packet_loss': 2.5,
                'latency': 18.5,
                'channel': 'Li-Fi',
                'encryption': 'AES-128'
            }
        elif device_type == "controller":
            self.baseline = {
                'signal': 98.0,
                'packet_loss': 1.2,
                'latency': 8.5,
                'channel': 'Li-Fi',
                'encryption': 'AES-256'
            }
        else:  # meter
            self.baseline = {
                'signal': 88.5,
                'packet_loss': 3.2,
                'latency': 22.0,
                'channel': 'RF',
                'encryption': 'AES-128'
            }
        
        self.history = []
        self.attack_mode = False
        self.attack_type = None
        self.attack_start_time = None
        
    def generate_reading(self):
        """Generate one telemetry reading with realistic variation"""
        if self.attack_mode:
            return self._generate_attack_reading()
        else:
            return self._generate_normal_reading()
    
    def _generate_normal_reading(self):
        """Normal operation with small random variations"""
        # Small natural fluctuations
        signal = self.baseline['signal'] + np.random.normal(0, 1.5)
        signal = max(75, min(100, signal))
        
        packet_loss = self.baseline['packet_loss'] + np.random.normal(0, 0.4)
        packet_loss = max(0.3, min(6, packet_loss))
        
        latency = self.baseline['latency'] + np.random.normal(0, 1.5)
        latency = max(5, min(30, latency))
        
        reading = {
            'timestamp': datetime.now(),
            'device_id': self.device_id,
            'device_type': self.device_type,
            'signal': round(signal, 1),
            'packet_loss': round(packet_loss, 1),
            'latency': round(latency, 1),
            'channel': self.baseline['channel'],
            'encryption': self.baseline['encryption'],
            'attack_flag': False,
            'attack_type': 'None'
        }
        self.history.append(reading)
        return reading
    
    def _generate_attack_reading(self):
        """Generate attack pattern based on type"""
        if self.attack_type == "rf_spoofing":
            reading = {
                'timestamp': datetime.now(),
                'device_id': self.device_id,
                'device_type': self.device_type,
                'signal': round(np.random.uniform(45, 65), 1),
                'packet_loss': round(np.random.uniform(18, 35), 1),
                'latency': round(np.random.uniform(50, 95), 1),
                'channel': 'RF (Unauthorized)',
                'encryption': 'None',
                'attack_flag': True,
                'attack_type': 'RF SPOOFING'
            }
        elif self.attack_type == "signal_degradation":
            reading = {
                'timestamp': datetime.now(),
                'device_id': self.device_id,
                'device_type': self.device_type,
                'signal': round(np.random.uniform(20, 38), 1),
                'packet_loss': round(np.random.uniform(10, 22), 1),
                'latency': round(np.random.uniform(40, 65), 1),
                'channel': 'Li-Fi (Degraded)',
                'encryption': 'AES-128',
                'attack_flag': True,
                'attack_type': 'SIGNAL DEGRADATION'
            }
        elif self.attack_type == "ddos":
            reading = {
                'timestamp': datetime.now(),
                'device_id': self.device_id,
                'device_type': self.device_type,
                'signal': round(np.random.uniform(60, 78), 1),
                'packet_loss': round(np.random.uniform(30, 52), 1),
                'latency': round(np.random.uniform(150, 300), 1),
                'channel': 'RF (Flooded)',
                'encryption': 'AES-256',
                'attack_flag': True,
                'attack_type': 'DDoS'
            }
        else:  # encryption_failure
            reading = {
                'timestamp': datetime.now(),
                'device_id': self.device_id,
                'device_type': self.device_type,
                'signal': round(np.random.uniform(70, 85), 1),
                'packet_loss': round(np.random.uniform(7, 15), 1),
                'latency': round(np.random.uniform(25, 42), 1),
                'channel': 'Li-Fi',
                'encryption': 'DISABLED',
                'attack_flag': True,
                'attack_type': 'ENCRYPTION FAILURE'
            }
        
        self.history.append(reading)
        return reading
    
    def trigger_attack(self, attack_type):
        """Start attack simulation"""
        self.attack_mode = True
        self.attack_type = attack_type
        self.attack_start_time = datetime.now()
    
    def stop_attack(self):
        """Return to normal"""
        self.attack_mode = False
        self.attack_type = None
        self.attack_start_time = None
    
    def get_history_df(self):
        """Return history as DataFrame"""
        if not self.history:
            return pd.DataFrame()
        return pd.DataFrame(self.history)
    
    def get_attack_duration(self):
        """Get seconds since attack started"""
        if self.attack_start_time:
            return (datetime.now() - self.attack_start_time).seconds
        return 0
    
    def reset_history(self):
        """Clear history"""
        self.history = []