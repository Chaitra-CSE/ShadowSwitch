import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import time
from sklearn.ensemble import IsolationForest

st.set_page_config(page_title="ML Detection", page_icon="🤖", layout="wide")

st.markdown("""
<style>
    .stApp { background: linear-gradient(135deg, #1a1a2a, #2a1f3a); }
    .ml-box {
        background: rgba(30,20,40,0.8);
        padding: 2rem;
        border-radius: 20px;
        border: 2px solid #b86bff;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

st.title("🤖 ML Anomaly Detection")
st.markdown("### Isolation Forest - Real-time Threat Detection")

if 'ml_data' not in st.session_state:
    st.session_state.ml_data = []
    st.session_state.model = IsolationForest(contamination=0.1, random_state=42)

# Generate data
signal = np.random.normal(95, 3)
packet_loss = np.random.normal(2, 1)
latency = np.random.normal(15, 5)

# Inject anomaly sometimes
if np.random.random() < 0.15:
    packet_loss = np.random.normal(20, 5)
    latency = np.random.normal(80, 20)

st.session_state.ml_data.append([signal, packet_loss, latency])
if len(st.session_state.ml_data) > 50:
    st.session_state.ml_data.pop(0)

# Detect anomaly
if len(st.session_state.ml_data) > 20:
    df = pd.DataFrame(st.session_state.ml_data, columns=['signal', 'packet_loss', 'latency'])
    model = IsolationForest(contamination=0.1).fit(df)
    pred = model.predict(df)[-1]
    score = abs(model.score_samples(df)[-1]) * 50
    is_anomaly = pred == -1
else:
    is_anomaly = packet_loss > 15 or latency > 60
    score = min(100, (packet_loss/20 + latency/100) * 50)

col1, col2 = st.columns(2)

with col1:
    color = '#ff4444' if is_anomaly else '#4ecdc4'
    status = '🚨 THREAT DETECTED' if is_anomaly else '✅ SYSTEM NORMAL'
    st.markdown(f"""
    <div class="ml-box">
        <h2 style="color:{color};">{status}</h2>
        <h1 style="font-size:4rem; color:{color};">{score:.1f}%</h1>
        <p>Confidence Level</p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="ml-box">
        <h3>Current Readings</h3>
        <p style="font-size:1.2rem;">📶 Signal: {signal:.1f}%</p>
        <p style="font-size:1.2rem;">📉 Packet Loss: {packet_loss:.1f}%</p>
        <p style="font-size:1.2rem;">⏱️ Latency: {latency:.1f}ms</p>
    </div>
    """, unsafe_allow_html=True)

if st.button("← Back to Home"):
    st.switch_page("app.py")

time.sleep(1)
st.rerun()