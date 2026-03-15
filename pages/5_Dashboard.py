import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np

st.set_page_config(page_title="Dashboard", page_icon="📱", layout="wide")

st.markdown("""
<style>
    .stApp { background: linear-gradient(135deg, #1a2a2a, #2a3a3a); }
    .dash-card {
        background: rgba(20,40,40,0.8);
        padding: 1.5rem;
        border-radius: 20px;
        border: 2px solid #4ecdc4;
        text-align: center;
        margin: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)

st.title("📱 Command Dashboard")
st.markdown("### Complete IoT Defense Overview")

# Device data
devices = pd.DataFrame({
    'Device': ['CAM_07', 'SENSOR_12', 'CTRL_03', 'METER_09', 'ARM_05', 'HVAC_02'],
    'Trust': [95, 87, 92, 72, 89, 79],
    'Signal': [94, 88, 96, 76, 91, 82],
    'Status': ['SECURE', 'SECURE', 'SECURE', 'MONITOR', 'SECURE', 'MONITOR']
})

# Device grid
cols = st.columns(3)
for i, row in devices.iterrows():
    with cols[i % 3]:
        color = '#4ecdc4' if row['Status'] == 'SECURE' else '#ffb86b'
        st.markdown(f"""
        <div class="dash-card">
            <h3 style="color:{color};">{row['Device']}</h3>
            <h1 style="font-size:3rem;">{row['Trust']}</h1>
            <p>📶 {row['Signal']}% • {row['Status']}</p>
        </div>
        """, unsafe_allow_html=True)

# Chart
fig = px.bar(devices, x='Device', y='Trust', color='Status',
             color_discrete_map={'SECURE': '#4ecdc4', 'MONITOR': '#ffb86b'})
fig.update_layout(
    plot_bgcolor='rgba(0,0,0,0)',
    paper_bgcolor='rgba(0,0,0,0)',
    font=dict(color='white'),
    title="Device Trust Scores"
)
st.plotly_chart(fig, use_container_width=True)

if st.button("← Back to Home"):
    st.switch_page("app.py")