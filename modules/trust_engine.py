# Calculates dynamic trust scores with explainability
import numpy as np

class TrustEngine:
    def __init__(self):
        # Penalty weights (configurable per deployment)
        self.weights = {
            'signal': 0.35,
            'packet_loss': 0.45,  # Most severe
            'latency': 0.25,
            'encryption': 0.6,     # Critical security
            'unauthorized_channel': 0.7,  # Critical security
            'failover_frequency': 0.3,
            'device_type_factor': 0.2
        }
        
    def calculate_score(self, telemetry, recent_failovers=0, device_risk_factor=1.0):
        """
        Calculate trust score 0-100 based on telemetry
        Returns score, status, color, and detailed reasons
        """
        base_score = 100
        penalties = []
        reasons = []
        
        # 1. Signal strength penalty
        if telemetry['signal'] < 80:
            penalty = (80 - telemetry['signal']) * self.weights['signal']
            penalties.append(penalty)
            if penalty > 5:
                reasons.append({
                    'factor': 'Signal Strength',
                    'value': f"{telemetry['signal']:.1f}%",
                    'penalty': round(penalty, 1),
                    'severity': 'HIGH' if telemetry['signal'] < 40 else 'MEDIUM',
                    'description': f"Signal below optimal threshold"
                })
        
        # 2. Packet loss penalty (most severe)
        if telemetry['packet_loss'] > 3:
            penalty = min(45, telemetry['packet_loss'] * self.weights['packet_loss'] * 2.8)
            penalties.append(penalty)
            if penalty > 5:
                severity = 'CRITICAL' if telemetry['packet_loss'] > 18 else 'HIGH' if telemetry['packet_loss'] > 10 else 'MEDIUM'
                reasons.append({
                    'factor': 'Packet Loss',
                    'value': f"{telemetry['packet_loss']:.1f}%",
                    'penalty': round(penalty, 1),
                    'severity': severity,
                    'description': f"Data packets being dropped"
                })
        
        # 3. Latency penalty
        if telemetry['latency'] > 25:
            penalty = (telemetry['latency'] - 25) * self.weights['latency']
            penalties.append(penalty)
            if penalty > 5:
                severity = 'CRITICAL' if telemetry['latency'] > 120 else 'HIGH' if telemetry['latency'] > 60 else 'MEDIUM'
                reasons.append({
                    'factor': 'Latency',
                    'value': f"{telemetry['latency']:.1f}ms",
                    'penalty': round(penalty, 1),
                    'severity': severity,
                    'description': f"Communication delay"
                })
        
        # 4. Encryption check (hard violation)
        if telemetry.get('encryption') in ['None', 'DISABLED', 'Disabled']:
            penalties.append(40)
            reasons.append({
                'factor': 'Encryption',
                'value': telemetry['encryption'],
                'penalty': 40,
                'severity': 'CRITICAL',
                'description': f"Security protocol violation"
            })
        
        # 5. Unauthorized channel check
        if 'Unauthorized' in telemetry.get('channel', '') or 'Flooded' in telemetry.get('channel', ''):
            penalties.append(50)
            reasons.append({
                'factor': 'Channel Violation',
                'value': telemetry['channel'],
                'penalty': 50,
                'severity': 'CRITICAL',
                'description': f"Unauthorized channel access"
            })
        
        # 6. Failover frequency penalty
        if recent_failovers > 1:
            penalty = min(30, recent_failovers * self.weights['failover_frequency'] * 10)
            penalties.append(penalty)
            if penalty > 5:
                reasons.append({
                    'factor': 'Instability',
                    'value': f"{recent_failovers} failovers",
                    'penalty': round(penalty, 1),
                    'severity': 'HIGH',
                    'description': f"Frequent channel switching"
                })
        
        # Apply device risk factor
        total_penalty = sum(penalties) * device_risk_factor
        final_score = max(0, min(100, base_score - total_penalty))
        
        # Determine status and color
        if final_score >= 85:
            status = "STABLE"
            color = "#00C853"  # Green
            status_desc = "Device operating normally"
        elif final_score >= 70:
            status = "MONITOR"
            color = "#FFB300"  # Amber
            status_desc = "Suspicious patterns detected"
        elif final_score >= 50:
            status = "RISKY"
            color = "#FF6B00"  # Orange
            status_desc = "Significant anomalies"
        elif final_score >= 30:
            status = "CRITICAL"
            color = "#D32F2F"  # Red
            status_desc = "Immediate action required"
        else:
            status = "COMPROMISED"
            color = "#8B0000"  # Dark Red
            status_desc = "Device isolated - security breach"
        
        return {
            'score': round(final_score, 1),
            'status': status,
            'status_desc': status_desc,
            'color': color,
            'total_penalty': round(total_penalty, 1),
            'reasons': reasons,
            'timestamp': telemetry.get('timestamp')
        }