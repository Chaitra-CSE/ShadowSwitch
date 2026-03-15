import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime
import time

st.set_page_config(page_title="Live Telemetry", page_icon="📡", layout="wide")

# Custom CSS
st.markdown("""
<style>
    .stApp {
        background: linear-gradient(135deg, #0a1f3a 0%, #1a2f3a 100%);
        font-family: 'Orbitron', sans-serif;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Metric Cards */
    .metric-card {
        background: rgba(20, 30, 50, 0.9);
        backdrop-filter: blur(10px);
        padding: 2rem;
        border-radius: 20px;
        border: 2px solid #4ecdc4;
        text-align: center;
        box-shadow: 0 10px 20px rgba(0,0,0,0.5);
        transition: all 0.3s ease;
    }
    
    .metric-card:hover {
        transform: translateY(-5px);
        border-color: #ff6b6b;
        box-shadow: 0 20px 30px rgba(0,0,0,0.6), 0 0 50px #4ecdc4;
    }
    
    .metric-title {
        color: #b0e0e6;
        font-size: 1rem;
        text-transform: uppercase;
        letter-spacing: 2px;
        margin-bottom: 0.5rem;
    }
    
    .metric-value {
        font-size: 3rem;
        font-weight: 800;
        color: white;
        text-shadow: 0 0 20px #4ecdc4;
    }
    
    .metric-unit {
        font-size: 1rem;
        color: #b0e0e6;
    }
    
    /* Channel Indicator */
    .channel-badge {
        display: inline-block;
        padding: 0.3rem 1rem;
        border-radius: 20px;
        font-weight: 600;
        margin-top: 0.5rem;
    }
    
    .channel-lifi {
        background: rgba(78, 205, 196, 0.2);
        border: 1px solid #4ecdc4;
        color: #4ecdc4;
    }
    
    .channel-rf {
        background: rgba(255, 107, 107, 0.2);
        border: 1px solid #ff6b6b;
        color: #ff6b6b;
    }
    
    /* Back button */
    .stButton button {
        background: #4ecdc4 !important;
        color: black !important;
        font-weight: 600 !important;
        border: none !important;
        border-radius: 10px !important;
        padding: 0.5rem 2rem !important;
        font-size: 1rem !important;
        margin-top: 2rem !important;
    }
    
    .stButton button:hover {
        background: #ff6b6b !important;
        color: white !important;
        transform: scale(1.05) !important;
    }
    
    /* Graph container */
    .graph-container {
        background: rgba(20, 30, 50, 0.9);
        backdrop-filter: blur(10px);
        border-radius: 20px;
        padding: 1.5rem;
        border: 2px solid #4ecdc4;
        margin: 2rem 0;
    }
    
    h1, h2, h3 {
        color: white !important;
        text-shadow: 0 0 20px #4ecdc4;
    }
</style>
""", unsafe_allow_html=True)

# Title
st.title("📡 Live Telemetry Monitoring")
st.markdown("### Real-time Li-Fi / RF Signal Analysis")

# Initialize session state for data storage
if 'telemetry_data' not in st.session_state:
    st.session_state.telemetry_data = {
        'timestamps': [],
        'signal': [],
        'packet_loss': [],
        'latency': [],
        'channel': []
    }

# Generate new telemetry data
def generate_telemetry():
    # Simulate signal with occasional drops
    if np.random.random() < 0.1:  # 10% chance of interference
        signal = np.random.uniform(60, 75)
        packet_loss = np.random.uniform(10, 25)
        latency = np.random.uniform(50, 100)
        channel = '⚠️ RF Interference'
    else:
        signal = np.random.normal(92, 5)
        packet_loss = np.random.normal(2, 1)
        latency = np.random.normal(15, 5)
        channel = 'Li-Fi'
    
    # Keep values in range
    signal = max(45, min(100, signal))
    packet_loss = max(0, min(30, packet_loss))
    latency = max(5, min(150, latency))
    
    return {
        'signal': round(signal, 1),
        'packet_loss': round(packet_loss, 1),
        'latency': round(latency, 1),
        'channel': channel
    }

# Generate new reading
new_data = generate_telemetry()
current_time = datetime.now().strftime("%H:%M:%S")

# Store data
st.session_state.telemetry_data['timestamps'].append(current_time)
st.session_state.telemetry_data['signal'].append(new_data['signal'])
st.session_state.telemetry_data['packet_loss'].append(new_data['packet_loss'])
st.session_state.telemetry_data['latency'].append(new_data['latency'])
st.session_state.telemetry_data['channel'].append(new_data['channel'])

# Keep last 30 readings
if len(st.session_state.telemetry_data['timestamps']) > 30:
    for key in st.session_state.telemetry_data:
        st.session_state.telemetry_data[key] = st.session_state.telemetry_data[key][-30:]

# Top Metrics Row
col1, col2, col3 = st.columns(3)

with col1:
    # Determine signal color
    if new_data['signal'] >= 85:
        signal_color = "#4ecdc4"
    elif new_data['signal'] >= 70:
        signal_color = "#ffb86b"
    else:
        signal_color = "#ff6b6b"
    
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-title">📶 Li-Fi SIGNAL</div>
        <div class="metric-value" style="color: {signal_color};">{new_data['signal']}<span class="metric-unit">%</span></div>
        <div class="channel-badge {'channel-lifi' if 'Li-Fi' in new_data['channel'] else 'channel-rf'}">
            {new_data['channel']}
        </div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    # Determine packet loss severity
    if new_data['packet_loss'] < 5:
        pl_color = "#4ecdc4"
        pl_text = "NORMAL"
    elif new_data['packet_loss'] < 15:
        pl_color = "#ffb86b"
        pl_text = "ELEVATED"
    else:
        pl_color = "#ff6b6b"
        pl_text = "CRITICAL"
    
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-title">📉 PACKET LOSS</div>
        <div class="metric-value" style="color: {pl_color};">{new_data['packet_loss']}<span class="metric-unit">%</span></div>
        <div style="color: {pl_color}; font-weight: 600; margin-top: 0.5rem;">{pl_text}</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    # Determine latency severity
    if new_data['latency'] < 30:
        lat_color = "#4ecdc4"
        lat_text = "FAST"
    elif new_data['latency'] < 80:
        lat_color = "#ffb86b"
        lat_text = "MODERATE"
    else:
        lat_color = "#ff6b6b"
        lat_text = "SLOW"
    
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-title">⏱️ LATENCY</div>
        <div class="metric-value" style="color: {lat_color};">{new_data['latency']}<span class="metric-unit">ms</span></div>
        <div style="color: {lat_color}; font-weight: 600; margin-top: 0.5rem;">{lat_text}</div>
    </div>
    """, unsafe_allow_html=True)

# Live Graph
st.markdown("<br>", unsafe_allow_html=True)
st.markdown('<div class="graph-container">', unsafe_allow_html=True)
st.markdown("### 🌊 Live Signal Waveform")

# Create the graph
fig = go.Figure()

# Signal trace
fig.add_trace(go.Scatter(
    x=st.session_state.telemetry_data['timestamps'],
    y=st.session_state.telemetry_data['signal'],
    mode='lines+markers',
    name='Signal Strength',
    line=dict(color='#4ecdc4', width=3),
    marker=dict(size=8, color=st.session_state.telemetry_data['signal'], 
                colorscale=[[0, '#ff6b6b'], [0.5, '#ffb86b'], [1, '#4ecdc4']],
                showscale=True,
                colorbar=dict(title="Signal %", tickfont=dict(color='white')))
))

# Packet loss trace (scaled for visibility)
fig.add_trace(go.Scatter(
    x=st.session_state.telemetry_data['timestamps'],
    y=[x * 3 for x in st.session_state.telemetry_data['packet_loss']],
    mode='lines',
    name='Packet Loss (x3)',
    line=dict(color='#ff6b6b', width=2, dash='dash')
))

# Add threshold line
fig.add_hline(y=70, line_dash="dash", line_color="#ffb86b", 
              annotation_text="Warning Threshold", annotation_position="bottom right")

fig.update_layout(
    height=400,
    plot_bgcolor='rgba(0,0,0,0)',
    paper_bgcolor='rgba(0,0,0,0)',
    font=dict(color='white', size=12),
    hovermode='x unified',
    showlegend=True,
    legend=dict(
        yanchor="top",
        y=0.99,
        xanchor="left",
        x=0.01,
        bgcolor='rgba(0,0,0,0.5)',
        font=dict(color='white')
    ),
    margin=dict(l=40, r=40, t=40, b=40)
)

fig.update_xaxes(gridcolor='rgba(255,255,255,0.1)', tickfont=dict(color='white'))
fig.update_yaxes(gridcolor='rgba(255,255,255,0.1)', tickfont=dict(color='white'), range=[0, 100])

st.plotly_chart(fig, use_container_width=True)
st.markdown('</div>', unsafe_allow_html=True)

# Real-time Stats Table
st.markdown("<br>", unsafe_allow_html=True)
col1, col2 = st.columns(2)

with col1:
    st.markdown('<div class="graph-container">', unsafe_allow_html=True)
    st.markdown("### 📊 Recent Readings")
    
    # Create a DataFrame for recent readings
    recent_df = pd.DataFrame({
        'Time': st.session_state.telemetry_data['timestamps'][-10:],
        'Signal %': st.session_state.telemetry_data['signal'][-10:],
        'Loss %': st.session_state.telemetry_data['packet_loss'][-10:],
        'Latency ms': st.session_state.telemetry_data['latency'][-10:],
        'Channel': st.session_state.telemetry_data['channel'][-10:]
    })
    
    st.dataframe(
        recent_df,
        use_container_width=True,
        height=300,
        column_config={
            "Signal %": st.column_config.NumberColumn(format="%.1f"),
            "Loss %": st.column_config.NumberColumn(format="%.1f"),
            "Latency ms": st.column_config.NumberColumn(format="%.0f"),
        }
    )
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.markdown('<div class="graph-container">', unsafe_allow_html=True)
    st.markdown("### 📈 Statistics")
    
    if len(st.session_state.telemetry_data['signal']) > 0:
        avg_signal = np.mean(st.session_state.telemetry_data['signal'][-10:])
        avg_loss = np.mean(st.session_state.telemetry_data['packet_loss'][-10:])
        avg_latency = np.mean(st.session_state.telemetry_data['latency'][-10:])
        max_loss = max(st.session_state.telemetry_data['packet_loss'][-10:])
        stability = "Stable" if avg_loss < 5 else "Unstable" if avg_loss > 15 else "Moderate"
        
        st.markdown(f"""
        <div style="padding: 1rem;">
            <p style="color: #b0e0e6;">📊 10-Point Average:</p>
            <p style="color: white;">Signal: {avg_signal:.1f}%</p>
            <p style="color: white;">Loss: {avg_loss:.1f}%</p>
            <p style="color: white;">Latency: {avg_latency:.0f}ms</p>
            <p style="color: white;">Peak Loss: {max_loss:.1f}%</p>
            <p style="color: white;">Status: <span style="color: {'#4ecdc4' if stability == 'Stable' else '#ffb86b' if stability == 'Moderate' else '#ff6b6b'}; font-weight: 600;">{stability}</span></p>
        </div>
        """, unsafe_allow_html=True)
        
        # Mini gauge for stability
        stability_value = 100 - (avg_loss * 3)
        stability_value = max(0, min(100, stability_value))
        
        gauge_fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=stability_value,
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': "Connection Quality", 'font': {'color': 'white'}},
            gauge={
                'axis': {'range': [0, 100], 'tickcolor': 'white'},
                'bar': {'color': '#4ecdc4' if stability_value > 70 else '#ffb86b' if stability_value > 40 else '#ff6b6b'},
                'steps': [
                    {'range': [0, 40], 'color': '#440000'},
                    {'range': [40, 70], 'color': '#884422'},
                    {'range': [70, 100], 'color': '#224422'}
                ]
            }
        ))
        gauge_fig.update_layout(height=200, paper_bgcolor='rgba(0,0,0,0)', font={'color': 'white'})
        st.plotly_chart(gauge_fig, use_container_width=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

# Auto-refresh and back button
col1, col2, col3 = st.columns([1, 1, 1])
with col2:
    if st.button("← BACK TO HOME", use_container_width=True):
        st.switch_page("app.py")

# Auto-refresh every 2 seconds
time.sleep(2)
st.rerun()