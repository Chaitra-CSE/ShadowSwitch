# Attack logging and timeline management
import pandas as pd
from datetime import datetime
import numpy as np

class AttackLogger:
    def __init__(self):
        self.attacks = []
        self.mitigations = []
        
    def log_attack(self, device_id, attack_type, trust_before, trust_after, 
                   response_time, mitigation, confidence):
        """Log an attack event with details"""
        self.attacks.append({
            'timestamp': datetime.now(),
            'device_id': device_id,
            'attack_type': attack_type,
            'trust_before': round(trust_before, 1),
            'trust_after': round(trust_after, 1),
            'trust_drop': round(trust_before - trust_after, 1),
            'response_time': round(response_time, 2),
            'mitigation': mitigation,
            'confidence': confidence,
            'resolved': True
        })
        
        # Keep only last 50 attacks
        if len(self.attacks) > 50:
            self.attacks = self.attacks[-50:]
    
    def log_mitigation(self, device_id, action, success=True):
        """Log mitigation actions"""
        self.mitigations.append({
            'timestamp': datetime.now(),
            'device_id': device_id,
            'action': action,
            'success': success
        })
    
    def get_timeline_df(self):
        """Get attacks as DataFrame for visualization"""
        if not self.attacks:
            return pd.DataFrame()
        
        df = pd.DataFrame(self.attacks)
        
        # Add severity classification
        def get_severity(row):
            if row['trust_after'] < 30:
                return 'CRITICAL'
            elif row['trust_after'] < 50:
                return 'HIGH'
            elif row['trust_after'] < 70:
                return 'MEDIUM'
            else:
                return 'LOW'
        
        df['severity'] = df.apply(get_severity, axis=1)
        return df
    
    def get_statistics(self):
        """Get attack statistics"""
        if not self.attacks:
            return {
                'total_attacks': 0,
                'avg_response': 0,
                'avg_trust_drop': 0,
                'most_common_attack': 'None',
                'critical_count': 0
            }
        
        df = pd.DataFrame(self.attacks)
        
        return {
            'total_attacks': len(df),
            'avg_response': round(df['response_time'].mean(), 2),
            'avg_trust_drop': round(df['trust_drop'].mean(), 1),
            'most_common_attack': df['attack_type'].mode().iloc[0] if len(df) > 0 else 'None',
            'critical_count': len(df[df['trust_after'] < 30])
        }
    
    def get_attack_by_type(self, attack_type):
        """Filter attacks by type"""
        df = pd.DataFrame(self.attacks)
        if len(df) == 0:
            return pd.DataFrame()
        return df[df['attack_type'] == attack_type]