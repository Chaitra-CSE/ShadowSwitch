import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import time

st.set_page_config(page_title="Failover Logic", page_icon="🔄", layout="wide")

# Custom CSS
st.markdown("""
<style>
    .stApp { background: linear-gradient(135deg, #0B0B1F 0%, #1A1B3A 100%); }
    .failover-box {
        background: rgba(30,30,50,0.8);
        backdrop-filter: blur(10px);
        padding: 2rem;
        border-radius: 20px;
        border: 2px solid #4ecdc4;
        text-align: center;
        margin: 1rem 0;
    }
    .timeline-event {
        background: rgba(20,20,40,0.6);
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid;
        margin: 0.5rem 0;
        animation: slideIn 0.3s ease;
    }
    @keyframes slideIn {
        from { transform: translateX(-20px); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
    }
    .attack-badge {
        display: inline-block;
        padding: 0.3rem 1rem;
        border-radius: 20px;
        font-weight: 600;
        font-size: 0.9rem;
    }
    .stMetric {
        background: rgba(30,30,50,0.6);
        padding: 1rem;
        border-radius: 10px;
        border: 1px solid #4ecdc4;
    }
</style>
""", unsafe_allow_html=True)

st.title("🔄 Automatic Failover Logic")
st.markdown("### Real-time Li-Fi ↔ RF Channel Switching with Attack Timeline")

# Initialize session state
if 'channel' not in st.session_state:
    st.session_state.channel = 'Li-Fi'
    st.session_state.signal = 95
    st.session_state.failovers = 0
    st.session_state.history = []
    st.session_state.attack_active = False
    st.session_state.attack_type = None
    st.session_state.last_update = time.time()
    st.session_state.timeline = []
    st.session_state.event_counter = 0
    st.session_state.attack_count = 0

# ===== OPTION 1: REAL-TIME AUTOMATIC UPDATES =====
current_time = time.time()
if current_time - st.session_state.last_update > 2:  # Update every 2 seconds
    # Store previous values for timeline
    old_signal = st.session_state.signal
    old_channel = st.session_state.channel
    
    # Random events that affect signal
    if not st.session_state.attack_active:
        # Normal fluctuation
        st.session_state.signal += np.random.normal(0, 2)
        
        # 15% chance of interference
        if np.random.random() < 0.15:
            attack_types = [
                "📡 RF INTERFERENCE", 
                "🌊 SIGNAL JAMMING", 
                "⚡ POWER DROP",
                "🔧 PHYSICAL OBSTRUCTION",
                "🎯 SPOOFING ATTACK",
                "📻 CHANNEL OVERLAP"
            ]
            st.session_state.attack_active = True
            st.session_state.attack_type = np.random.choice(attack_types)
            st.session_state.signal -= np.random.uniform(25, 40)
            st.session_state.attack_count += 1
            
            # Add to timeline
            st.session_state.event_counter += 1
            st.session_state.timeline.append({
                'time': datetime.now().strftime("%H:%M:%S"),
                'event': f"⚠️ {st.session_state.attack_type}",
                'signal': st.session_state.signal,
                'type': 'attack'
            })
    else:
        # Attack lasts 3-6 seconds
        if np.random.random() < 0.25:  # 25% chance to recover
            st.session_state.attack_active = False
            st.session_state.attack_type = None
            st.session_state.signal = np.random.uniform(85, 98)  # Recover to normal
            
            # Add recovery to timeline
            st.session_state.event_counter += 1
            st.session_state.timeline.append({
                'time': datetime.now().strftime("%H:%M:%S"),
                'event': "✅ SYSTEM RECOVERED",
                'signal': st.session_state.signal,
                'type': 'recovery'
            })
    
    # Keep signal in realistic range
    st.session_state.signal = max(15, min(100, st.session_state.signal))
    
    # Automatic failover logic
    if st.session_state.signal < 45 and st.session_state.channel == 'Li-Fi':
        st.session_state.channel = 'RF (Backup)'
        st.session_state.failovers += 1
        # Add failover to timeline
        st.session_state.event_counter += 1
        st.session_state.timeline.append({
            'time': datetime.now().strftime("%H:%M:%S"),
            'event': "🔄 FAILOVER TO RF CHANNEL",
            'signal': st.session_state.signal,
            'type': 'failover'
        })
    elif st.session_state.signal > 70 and st.session_state.channel == 'RF (Backup)':
        st.session_state.channel = 'Li-Fi'
        st.session_state.failovers += 1
        # Add recovery to timeline
        st.session_state.event_counter += 1
        st.session_state.timeline.append({
            'time': datetime.now().strftime("%H:%M:%S"),
            'event': "↩️ RETURN TO Li-Fi",
            'signal': st.session_state.signal,
            'type': 'recovery'
        })
    
    # Store history for graph
    st.session_state.history.append({
        'time': datetime.now().strftime("%H:%M:%S"),
        'signal': st.session_state.signal,
        'channel': st.session_state.channel
    })
    if len(st.session_state.history) > 30:
        st.session_state.history = st.session_state.history[-30:]
    
    # Keep only last 10 timeline events
    if len(st.session_state.timeline) > 10:
        st.session_state.timeline = st.session_state.timeline[-10:]
    
    st.session_state.last_update = current_time

# ===== MAIN DISPLAY - TOP METRICS =====
col1, col2, col3 = st.columns(3)

with col1:
    channel_color = '#4ecdc4' if st.session_state.channel == 'Li-Fi' else '#ff6b6b'
    channel_emoji = '📡' if st.session_state.channel == 'Li-Fi' else '📻'
    st.markdown(f"""
    <div class="failover-box">
        <h3 style="color: {channel_color}; margin:0;">{channel_emoji} CURRENT CHANNEL</h3>
        <h1 style="color: {channel_color}; font-size: 2.5rem; margin:0.5rem 0;">{st.session_state.channel}</h1>
        <div class="attack-badge" style="background: {channel_color}20; border: 1px solid {channel_color};">
            {'🔄 Active' if st.session_state.channel == 'RF (Backup)' else '✅ Primary'}
        </div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    if st.session_state.signal >= 70:
        signal_color = '#4ecdc4'
        signal_status = "EXCELLENT"
    elif st.session_state.signal >= 45:
        signal_color = '#ffb86b'
        signal_status = "WARNING"
    else:
        signal_color = '#ff6b6b'
        signal_status = "CRITICAL"
    
    st.markdown(f"""
    <div class="failover-box">
        <h3 style="color: {signal_color}; margin:0;">📶 SIGNAL STRENGTH</h3>
        <h1 style="color: {signal_color}; font-size: 2.5rem; margin:0.5rem 0;">{st.session_state.signal:.1f}%</h1>
        <div class="attack-badge" style="background: {signal_color}20; border: 1px solid {signal_color};">
            {signal_status}
        </div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    status = "⚠️ FAILOVER ACTIVE" if st.session_state.channel == 'RF (Backup)' else "✅ STABLE"
    status_color = '#ff6b6b' if st.session_state.channel == 'RF (Backup)' else '#4ecdc4'
    st.markdown(f"""
    <div class="failover-box">
        <h3 style="color: {status_color}; margin:0;">🔄 SYSTEM STATUS</h3>
        <h2 style="color: {status_color}; margin:0.5rem 0;">{status}</h2>
        <p style="color: white; font-size: 1.2rem; margin:0;">Total Failovers: {st.session_state.failovers}</p>
    </div>
    """, unsafe_allow_html=True)

# Attack indicator
if st.session_state.attack_active:
    st.error(f"⚠️ **ACTIVE THREAT DETECTED:** {st.session_state.attack_type}")

# ===== OPTION 3: ATTACK TIMELINE =====
st.markdown("---")
st.markdown("### 📅 EVENT TIMELINE")

if st.session_state.timeline:
    # Create columns for timeline
    for event in reversed(st.session_state.timeline):
        if event['type'] == 'attack':
            color = '#ff6b6b'
            icon = '⚠️'
            bg_color = 'rgba(255,107,107,0.1)'
        elif event['type'] == 'failover':
            color = '#ffb86b'
            icon = '🔄'
            bg_color = 'rgba(255,184,107,0.1)'
        else:  # recovery
            color = '#4ecdc4'
            icon = '✅'
            bg_color = 'rgba(78,205,196,0.1)'
        
        st.markdown(f"""
        <div class="timeline-event" style="border-left-color: {color}; background: {bg_color};">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div>
                    <span style="color: {color}; font-weight: 600;">{icon} {event['event']}</span>
                    <br>
                    <small style="color: #888;">{event['time']}</small>
                </div>
                <div style="text-align: right;">
                    <span style="color: white; font-weight: 600;">Signal: {event['signal']:.1f}%</span>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
else:
    st.info("⏳ Waiting for events... Click refresh or wait for automatic updates")

# ===== LIVE SIGNAL GRAPH =====
st.markdown("---")
st.markdown("### 📊 Signal History & Thresholds")

if st.session_state.history and len(st.session_state.history) > 1:
    df = pd.DataFrame(st.session_state.history)
    fig = go.Figure()
    
    # Signal trace
    fig.add_trace(go.Scatter(
        x=df['time'],
        y=df['signal'],
        mode='lines+markers',
        name='Signal Strength',
        line=dict(color='#4ecdc4', width=3),
        marker=dict(
            size=8,
            color=[ '#ff6b6b' if c == 'RF (Backup)' else '#4ecdc4' for c in df['channel'] ],
            symbol='circle'
        ),
        fill='tozeroy',
        fillcolor='rgba(78, 205, 196, 0.1)'
    ))
    
    # Threshold lines
    fig.add_hline(y=70, line_dash="dash", line_color="#ffb86b", 
                  annotation_text="⚠️ Warning (70%)", annotation_position="bottom right")
    fig.add_hline(y=45, line_dash="dash", line_color="#ff6b6b", 
                  annotation_text="🔴 Failover (45%)", annotation_position="bottom right")
    
    # Shade regions
    fig.add_hrect(y0=70, y1=100, line_width=0, fillcolor="rgba(78, 205, 196, 0.1)", 
                  annotation_text="Safe Zone", annotation_position="top left")
    fig.add_hrect(y0=45, y1=70, line_width=0, fillcolor="rgba(255, 184, 107, 0.1)", 
                  annotation_text="Warning Zone", annotation_position="top left")
    fig.add_hrect(y0=0, y1=45, line_width=0, fillcolor="rgba(255, 107, 107, 0.1)", 
                  annotation_text="Critical Zone", annotation_position="top left")
    
    fig.update_layout(
        height=400,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white', size=12),
        showlegend=True,
        hovermode='x unified',
        margin=dict(l=40, r=40, t=40, b=40)
    )
    
    fig.update_xaxes(gridcolor='rgba(255,255,255,0.1)', tickfont=dict(color='white'), tickangle=45)
    fig.update_yaxes(gridcolor='rgba(255,255,255,0.1)', tickfont=dict(color='white'), range=[0, 100])
    
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("📡 Collecting signal data... Please wait a moment")

# ===== STATISTICS =====
st.markdown("---")
st.markdown("### 📊 Failover Statistics")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        label="🔄 Total Failovers",
        value=st.session_state.failovers,
        delta="+1" if st.session_state.channel == 'RF (Backup)' else "0",
        delta_color="inverse"
    )

with col2:
    st.metric("⚠️ Attacks Detected", st.session_state.attack_count)

with col3:
    avg_signal = np.mean([h['signal'] for h in st.session_state.history]) if st.session_state.history else 0
    st.metric("📶 Avg Signal", f"{avg_signal:.1f}%")

with col4:
    uptime = len(st.session_state.history) * 2 if st.session_state.history else 0
    st.metric("⏱️ Monitoring Time", f"{uptime}s")

# ===== MANUAL CONTROLS (Optional - for demo) =====
st.markdown("---")
with st.expander("🛠️ Manual Controls (For Demo Purposes)"):
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📡 FORCE RF INTERFERENCE", use_container_width=True):
            st.session_state.signal = 35
            st.session_state.attack_active = True
            st.session_state.attack_type = "Manual RF Interference"
            st.session_state.attack_count += 1
            st.rerun()
    
    with col2:
        if st.button("🔋 SIMULATE POWER DROP", use_container_width=True):
            st.session_state.signal = 25
            st.session_state.attack_active = True
            st.session_state.attack_type = "Manual Power Drop"
            st.session_state.attack_count += 1
            st.rerun()
    
    with col3:
        if st.button("✅ RESET TO NORMAL", use_container_width=True):
            st.session_state.signal = 95
            st.session_state.attack_active = False
            st.session_state.attack_type = None
            st.rerun()

# ===== BACK BUTTON =====
st.markdown("---")
col1, col2, col3 = st.columns(3)
with col2:
    if st.button("← BACK TO HOME", use_container_width=True):
        st.switch_page("app.py")

# ===== AUTO-REFRESH =====
time.sleep(2)
st.rerun()