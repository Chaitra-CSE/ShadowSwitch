# Policy decisions and failover logic
import pandas as pd
from datetime import datetime, timedelta

class PolicyEngine:
    def __init__(self):
        self.thresholds = {
            'compromised': 30,
            'critical': 50,
            'risky': 70,
            'monitor': 85,
            'packet_loss_critical': 15,
            'latency_critical': 100,
            'signal_critical': 35
        }
        self.failover_history = []
        self.alert_history = []
        
    def evaluate(self, trust_result, telemetry, drift_info, device_context=None):
        """
        Make policy decision based on trust and drift
        Returns: action, reason, severity, recommendation
        """
        is_anomaly, confidence, explanation, drift_details = drift_info
        
        action = "CONTINUE_LIFI"
        reason = "Normal operation"
        severity = "INFO"
        recommendation = "No action needed"
        
        # Check for hard violations
        if trust_result['score'] < self.thresholds['compromised']:
            action = "🚨 ISOLATE DEVICE"
            reason = f"Device compromised: Trust {trust_result['score']}"
            severity = "CRITICAL"
            recommendation = "Immediate isolation and forensic analysis"
            
        elif trust_result['score'] < self.thresholds['critical']:
            action = "🔄 FAILOVER TO RF"
            reason = f"Trust critical: {trust_result['score']}"
            severity = "CRITICAL"
            recommendation = "Switch to backup channel"
            
        elif telemetry.get('encryption') in ['None', 'DISABLED', 'Disabled']:
            action = "🔒 BLOCK DEVICE"
            reason = "Encryption disabled - security breach"
            severity = "CRITICAL"
            recommendation = "Block until encryption enabled"
            
        elif 'Unauthorized' in telemetry.get('channel', ''):
            action = "⛔ BLOCK CHANNEL"
            reason = "Unauthorized RF channel detected"
            severity = "CRITICAL"
            recommendation = "Block unauthorized access"
            
        elif 'Flooded' in telemetry.get('channel', ''):
            action = "🌊 REROUTE TRAFFIC"
            reason = "Channel flooding detected"
            severity = "CRITICAL"
            recommendation = "Switch to backup channel"
            
        elif trust_result['score'] < self.thresholds['risky']:
            action = "⚠️ INVESTIGATE"
            reason = f"Trust risky: {trust_result['score']}"
            severity = "HIGH"
            recommendation = "Run diagnostic routines"
            
        elif trust_result['score'] < self.thresholds['monitor']:
            action = "👁️ MONITOR"
            reason = f"Trust degrading: {trust_result['score']}"
            severity = "MEDIUM"
            recommendation = "Increase sampling frequency"
            
        elif is_anomaly and confidence > 75:
            action = "🔍 DEEP SCAN"
            reason = f"High-confidence anomaly"
            severity = "HIGH"
            recommendation = "Correlate with other devices"
            
        elif is_anomaly:
            action = "📊 ANALYZE"
            reason = f"Anomaly detected"
            severity = "MEDIUM"
            recommendation = "Monitor closely"
        
        # Log decision
        decision = {
            'timestamp': datetime.now(),
            'action': action,
            'reason': reason,
            'severity': severity,
            'trust_score': trust_result['score'],
            'device_id': telemetry.get('device_id', 'unknown')
        }
        
        if severity != "INFO":
            self.failover_history.append(decision)
            self.alert_history.append(decision)
        
        # Keep history manageable
        if len(self.failover_history) > 100:
            self.failover_history = self.failover_history[-100:]
        if len(self.alert_history) > 200:
            self.alert_history = self.alert_history[-200:]
        
        return {
            'action': action,
            'reason': reason,
            'severity': severity,
            'recommendation': recommendation,
            'timestamp': datetime.now(),
            'confidence': confidence if is_anomaly else None
        }
    
    def get_failover_count(self, minutes=5):
        """Count recent failovers"""
        if not self.failover_history:
            return 0
        
        cutoff = datetime.now() - timedelta(minutes=minutes)
        recent = [f for f in self.failover_history 
                 if f['timestamp'] > cutoff]
        return len(recent)
    
    def get_recent_alerts(self, count=10):
        """Get most recent alerts"""
        return sorted(self.alert_history[-count:], 
                     key=lambda x: x['timestamp'], 
                     reverse=True)
    
    def get_statistics(self):
        """Get policy statistics"""
        total = len(self.failover_history)
        if total == 0:
            return {
                'total_failovers': 0,
                'critical_events': 0,
                'avg_trust_during_failover': 0,
                'unique_devices_affected': 0
            }
        
        df = pd.DataFrame(self.failover_history)
        critical = len(df[df['severity'] == 'CRITICAL'])
        avg_trust = df['trust_score'].mean()
        unique_devices = df['device_id'].nunique() if 'device_id' in df.columns else 1
        
        return {
            'total_failovers': total,
            'critical_events': critical,
            'avg_trust_during_failover': round(avg_trust, 1),
            'unique_devices_affected': unique_devices
        }