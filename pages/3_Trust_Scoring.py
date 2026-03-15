import streamlit as st
import plotly.graph_objects as go
import numpy as np
import time

st.set_page_config(page_title="Trust Scoring", page_icon="📊", layout="wide")

st.markdown("""
<style>
    .stApp { background: linear-gradient(135deg, #1a2a1a, #2a3a2a); }
    .trust-box {
        background: rgba(20,40,20,0.8);
        padding: 3rem;
        border-radius: 30px;
        border: 2px solid #4ecdc4;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

st.title("📊 Dynamic Trust Scoring")
st.markdown("### Real-time Device Trust Assessment (0-100)")

if 'trust' not in st.session_state:
    st.session_state.trust = 95
    st.session_state.history = []

# Update trust
change = np.random.normal(0, 2)
st.session_state.trust = max(0, min(100, st.session_state.trust + change))
st.session_state.history.append(st.session_state.trust)
if len(st.session_state.history) > 50:
    st.session_state.history.pop(0)

# Determine color
if st.session_state.trust >= 85:
    color = '#4ecdc4'
    status = 'SECURE'
elif st.session_state.trust >= 70:
    color = '#ffb86b'
    status = 'MONITOR'
elif st.session_state.trust >= 50:
    color = '#ff6b6b'
    status = 'RISKY'
else:
    color = '#ff4444'
    status = 'CRITICAL'

# Gauge
fig = go.Figure(go.Indicator(
    mode="gauge+number",
    value=st.session_state.trust,
    domain={'x': [0, 1], 'y': [0, 1]},
    title={'text': f"Trust Score - {status}", 'font': {'color': 'white'}},
    gauge={
        'axis': {'range': [0, 100], 'tickcolor': 'white'},
        'bar': {'color': color},
        'steps': [
            {'range': [0, 30], 'color': '#440000'},
            {'range': [30, 50], 'color': '#884444'},
            {'range': [50, 70], 'color': '#aa8844'},
            {'range': [70, 85], 'color': '#aacc44'},
            {'range': [85, 100], 'color': '#44aa44'}
        ]
    }
))
fig.update_layout(height=400, paper_bgcolor='rgba(0,0,0,0)', font={'color': 'white'})
st.plotly_chart(fig, use_container_width=True)

# History
hist_fig = go.Figure()
hist_fig.add_trace(go.Scatter(
    y=st.session_state.history,
    mode='lines+markers',
    line=dict(color=color, width=3),
    fill='tozeroy'
))
hist_fig.update_layout(
    height=200,
    plot_bgcolor='rgba(0,0,0,0)',
    paper_bgcolor='rgba(0,0,0,0)',
    font=dict(color='white'),
    title="Trust History"
)
st.plotly_chart(hist_fig, use_container_width=True)



if st.button("← Back to Home"):
    st.switch_page("app.py")

time.sleep(1)
st.rerun()