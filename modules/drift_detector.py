# ML-based anomaly detection with explainability and forecasting
import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LinearRegression
import warnings
warnings.filterwarnings('ignore')

class DriftDetector:
    def __init__(self):
        self.model = IsolationForest(
            contamination=0.08,
            random_state=42,
            n_estimators=120,
            max_samples='auto',
            bootstrap=False
        )
        self.scaler = StandardScaler()
        self.is_trained = False
        self.training_samples = []
        self.forecast_model = LinearRegression()
        
    def train(self, normal_data):
        """Train model on normal telemetry"""
        if len(normal_data) < 20:
            synthetic = self._generate_synthetic_normal(50)
            train_data = pd.concat([normal_data, synthetic]) if len(normal_data) > 0 else synthetic
        else:
            train_data = normal_data
        
        # Scale features
        scaled = self.scaler.fit_transform(train_data[['signal','packet_loss','latency']])
        
        # Train model
        self.model.fit(scaled)
        self.is_trained = True
        self.training_samples = train_data
        
        return True
    
    def _generate_synthetic_normal(self, n_samples=50):
        """Generate synthetic normal data for training"""
        np.random.seed(42)
        data = {
            'signal': np.random.normal(95, 3, n_samples),
            'packet_loss': np.random.normal(2, 0.8, n_samples),
            'latency': np.random.normal(15, 3, n_samples)
        }
        return pd.DataFrame(data)
    
    def detect(self, telemetry_df):
        """Detect anomalies in telemetry stream"""
        if not self.is_trained or len(telemetry_df) < 3:
            return self._statistical_detection(telemetry_df)
        
        latest = telemetry_df[['signal','packet_loss','latency']].iloc[-3:].copy()
        
        # Scale
        scaled = self.scaler.transform(latest)
        
        # Get predictions
        predictions = self.model.predict(scaled)
        is_anomaly = predictions[-1] == -1
        
        # Get anomaly scores
        scores = self.model.score_samples(scaled)
        confidence = min(95, max(0, abs(scores[-1]) * 40))
        
        # Generate explanation
        explanation, details = self._generate_explanation(
            latest.iloc[-1], 
            telemetry_df.iloc[-2:-1] if len(telemetry_df) > 1 else None,
            is_anomaly,
            scores[-1]
        )
        
        return is_anomaly, round(confidence, 1), explanation, details
    
    def _statistical_detection(self, df):
        """Fallback statistical detection"""
        if len(df) < 5:
            return False, 0, "Insufficient data", {}
        
        latest = df.iloc[-1]
        mean = df[['signal','packet_loss','latency']].iloc[:-1].mean()
        std = df[['signal','packet_loss','latency']].iloc[:-1].std()
        
        anomalies = []
        for col in ['signal','packet_loss','latency']:
            if std[col] > 0:
                z = abs((latest[col] - mean[col]) / std[col])
                if z > 2.5:
                    anomalies.append(col)
        
        is_anomaly = len(anomalies) > 0
        confidence = min(85, len(anomalies) * 30)
        
        details = {
            'z_scores': {col: round(abs((latest[col] - mean[col]) / std[col]), 2) if std[col] > 0 else 0 for col in ['signal','packet_loss','latency']},
            'anomalous_features': anomalies,
            'method': 'statistical'
        }
        
        explanation = f"Statistical anomaly detected in: {', '.join(anomalies)}" if is_anomaly else "Within normal bounds"
        
        return is_anomaly, confidence, explanation, details
    
    def _generate_explanation(self, current, previous, is_anomaly, score):
        """Generate human-readable explanation"""
        details = {
            'ml_score': round(score, 3),
            'current_values': current.to_dict(),
            'triggers': []
        }
        
        if not is_anomaly:
            return "Normal behavior pattern", details
        
        reasons = []
        
        if current['packet_loss'] > 15:
            reasons.append(f"Critical packet loss: {current['packet_loss']:.1f}%")
            details['triggers'].append({
                'feature': 'packet_loss',
                'value': current['packet_loss'],
                'threshold': 15,
                'severity': 'CRITICAL'
            })
        elif current['packet_loss'] > 8:
            reasons.append(f"High packet loss: {current['packet_loss']:.1f}%")
            details['triggers'].append({
                'feature': 'packet_loss',
                'value': current['packet_loss'],
                'threshold': 8,
                'severity': 'HIGH'
            })
        
        if current['latency'] > 100:
            reasons.append(f"Critical latency: {current['latency']:.1f}ms")
            details['triggers'].append({
                'feature': 'latency',
                'value': current['latency'],
                'threshold': 100,
                'severity': 'CRITICAL'
            })
        elif current['latency'] > 50:
            reasons.append(f"High latency: {current['latency']:.1f}ms")
            details['triggers'].append({
                'feature': 'latency',
                'value': current['latency'],
                'threshold': 50,
                'severity': 'HIGH'
            })
        
        if current['signal'] < 35:
            reasons.append(f"Critical signal loss: {current['signal']:.1f}%")
            details['triggers'].append({
                'feature': 'signal',
                'value': current['signal'],
                'threshold': 35,
                'severity': 'CRITICAL'
            })
        elif current['signal'] < 55:
            reasons.append(f"Weak signal: {current['signal']:.1f}%")
            details['triggers'].append({
                'feature': 'signal',
                'value': current['signal'],
                'threshold': 55,
                'severity': 'HIGH'
            })
        
        if previous is not None and len(previous) > 0:
            prev = previous.iloc[0]
            if abs(current['packet_loss'] - prev['packet_loss']) > 10:
                reasons.append(f"Sudden packet loss spike")
        
        if not reasons:
            reasons.append("Unusual pattern detected by ML")
        
        explanation = " • ".join(reasons[:2])
        return explanation, details
    
    def predict_trust_trend(self, trust_history, minutes_ahead=2):
        """
        Predict future trust scores using linear regression
        Returns predicted scores and confidence interval
        """
        if len(trust_history) < 15:
            return None, None, None
        
        # Prepare data
        recent = trust_history[-30:] if len(trust_history) > 30 else trust_history
        x = np.arange(len(recent)).reshape(-1, 1)
        y = np.array([h['score'] for h in recent])
        
        # Train forecast model
        self.forecast_model.fit(x, y)
        
        # Predict future (4 points = 2 minutes with 30s intervals)
        future_points = minutes_ahead * 2
        future_x = np.arange(len(recent), len(recent) + future_points).reshape(-1, 1)
        predictions = self.forecast_model.predict(future_x)
        
        # Calculate confidence interval (80% prediction interval)
        residuals = y - self.forecast_model.predict(x)
        std = np.std(residuals)
        
        # Clip to valid range
        predictions = np.clip(predictions, 0, 100)
        
        return predictions, std * 1.5, std