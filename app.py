import streamlit as st
import random
import numpy as np
import time

st.set_page_config(
    page_title="ShadowSwitch - Li-Fi/RF IoT Defense",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ─────────────────────────────────────────────
#  SESSION STATE ROUTER
# ─────────────────────────────────────────────
if "page" not in st.session_state:
    st.session_state.page = "home"

def go(page):
    st.session_state.page = page
    st.rerun()

# ─────────────────────────────────────────────
#  SHARED BACKDROP + BASE CSS
# ─────────────────────────────────────────────
def inject_base_css():
    st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;600;700;900&family=Rajdhani:wght@300;400;500;600;700&display=swap');

*, *::before, *::after { box-sizing: border-box; }

html, body, .stApp {
    background: #020814 !important;
    font-family: 'Rajdhani', sans-serif;
    color: #e0e8ff;
    min-height: 100vh;
}

/* ── BACKGROUND ── */
.bg-grid {
    position: fixed; top: 0; left: 0; width: 100%; height: 100%;
    background-image:
        linear-gradient(rgba(0,200,255,0.04) 1px, transparent 1px),
        linear-gradient(90deg, rgba(0,200,255,0.04) 1px, transparent 1px);
    background-size: 60px 60px;
    pointer-events: none; z-index: 0;
}
.bg-orb-1 {
    position: fixed; width: 600px; height: 600px; border-radius: 50%;
    background: radial-gradient(circle, rgba(0,160,255,0.12) 0%, transparent 70%);
    top: -200px; right: -100px; pointer-events: none; z-index: 0;
    animation: orbPulse 8s ease-in-out infinite;
}
.bg-orb-2 {
    position: fixed; width: 500px; height: 500px; border-radius: 50%;
    background: radial-gradient(circle, rgba(120,0,255,0.10) 0%, transparent 70%);
    bottom: -150px; left: -100px; pointer-events: none; z-index: 0;
    animation: orbPulse 10s ease-in-out infinite reverse;
}
.bg-orb-3 {
    position: fixed; width: 300px; height: 300px; border-radius: 50%;
    background: radial-gradient(circle, rgba(0,255,180,0.08) 0%, transparent 70%);
    top: 50%; left: 50%; transform: translate(-50%,-50%);
    pointer-events: none; z-index: 0;
    animation: orbPulse 12s ease-in-out infinite;
}
@keyframes orbPulse {
    0%,100% { transform: scale(1); opacity: 1; }
    50%      { transform: scale(1.15); opacity: 0.7; }
}
.scanline {
    position: fixed; top: 0; left: 0; width: 100%; height: 100%;
    background: repeating-linear-gradient(
        0deg,transparent,transparent 2px,
        rgba(0,200,255,0.012) 2px,rgba(0,200,255,0.012) 4px
    );
    pointer-events: none; z-index: 1;
    animation: scanMove 8s linear infinite;
}
@keyframes scanMove {
    0%   { background-position: 0 0; }
    100% { background-position: 0 100px; }
}

/* ── HIDE STREAMLIT CHROME ── */
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 2rem 3rem !important; position: relative; z-index: 10; }

/* ── UTILS ── */
@keyframes blink {
    0%,100% { opacity: 1; }
    50%      { opacity: 0.3; }
}

.section-header {
    font-family: 'Orbitron', monospace;
    font-size: 0.7rem; font-weight: 700; letter-spacing: 5px;
    color: rgba(0,200,255,0.75); text-transform: uppercase;
    margin: 1.6rem 0 1rem;
    display: flex; align-items: center; gap: 1rem;
}
.section-header::after {
    content:''; flex:1; height:1px;
    background: linear-gradient(90deg, rgba(0,200,255,0.35), transparent);
}

/* ── STATUS BAR ── */
.status-bar {
    background: rgba(5,15,35,0.88);
    border: 1px solid rgba(0,200,255,0.15);
    border-radius: 12px;
    padding: 0.85rem 1.8rem;
    display: flex; align-items: center; justify-content: space-between;
    margin: 0.8rem 0;
    font-family: 'Rajdhani', sans-serif;
    font-size: 0.85rem; letter-spacing: 2px;
    color: rgba(180,200,255,0.7);
}
.status-online { display: flex; align-items: center; gap: 0.5rem; color: #00ff96; font-weight: 600; }
.status-dot {
    width: 8px; height: 8px; border-radius: 50%;
    background: #00ff96; box-shadow: 0 0 10px #00ff96;
    animation: blink 1.5s infinite;
}

/* ── TICKER ── */
.ticker-wrap {
    overflow: hidden;
    background: rgba(0,200,255,0.06);
    border-top: 1px solid rgba(0,200,255,0.15);
    border-bottom: 1px solid rgba(0,200,255,0.15);
    padding: 0.6rem 0; margin: 1rem 0;
}
.ticker-text {
    display: inline-block; white-space: nowrap;
    animation: ticker 30s linear infinite;
    font-family: 'Orbitron', monospace;
    font-size: 0.65rem; letter-spacing: 3px;
    color: rgba(0,200,255,0.75);
}
@keyframes ticker {
    0%   { transform: translateX(0); }
    100% { transform: translateX(-50%); }
}

/* ── HERO ── */
.hero-wrapper {
    text-align: center;
    padding: 3.5rem 2rem 2.5rem;
    background: linear-gradient(180deg, rgba(0,20,50,0.85) 0%, rgba(2,8,20,0.9) 100%);
    border-radius: 24px;
    border: 1px solid rgba(0,200,255,0.25);
    box-shadow: 0 0 60px rgba(0,150,255,0.12), inset 0 1px 0 rgba(255,255,255,0.06);
    margin-bottom: 1.5rem; position: relative; overflow: hidden;
}
.hero-wrapper::before {
    content:''; position: absolute; top: 0; left: 0; right: 0; height: 2px;
    background: linear-gradient(90deg, transparent, #00c8ff, #7b00ff, #00c8ff, transparent);
    background-size: 200% auto;
    animation: borderSlide 4s linear infinite;
}
@keyframes borderSlide {
    0%   { background-position: -200% 0; }
    100% { background-position:  200% 0; }
}
.hero-badge {
    display: inline-block;
    background: rgba(0,200,255,0.1);
    border: 1px solid rgba(0,200,255,0.4);
    border-radius: 50px; padding: 0.3rem 1.2rem;
    font-size: 0.75rem; letter-spacing: 4px;
    color: #00c8ff; text-transform: uppercase; margin-bottom: 1.2rem;
}
.hero-title {
    font-family: 'Orbitron', monospace;
    font-size: 4.5rem; font-weight: 900; letter-spacing: 8px;
    color: #fff;
    text-shadow: 0 0 20px rgba(0,200,255,0.6), 0 0 60px rgba(0,150,255,0.3);
    line-height: 1; margin-bottom: 1rem;
}
.hero-title span {
    background: linear-gradient(135deg, #00c8ff, #7b00ff, #ff0080);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;
}
.hero-sub {
    font-family: 'Rajdhani', sans-serif;
    font-size: 1.1rem; font-weight: 500; letter-spacing: 5px;
    color: rgba(200,220,255,0.8); text-transform: uppercase;
}
.hero-line {
    width: 120px; height: 2px;
    background: linear-gradient(90deg, transparent, #00c8ff, transparent);
    margin: 1.2rem auto 0;
}

/* ── PAGE HERO (sub-pages) ── */
.page-hero {
    padding: 2rem 2.5rem;
    background: linear-gradient(180deg, rgba(0,20,50,0.85) 0%, rgba(2,8,20,0.9) 100%);
    border-radius: 20px;
    border: 1px solid rgba(0,200,255,0.2);
    margin-bottom: 1.5rem; position: relative; overflow: hidden;
    display: flex; align-items: center; gap: 1.5rem;
}
.page-hero::before {
    content:''; position:absolute; top:0; left:0; right:0; height:2px;
    background: linear-gradient(90deg, transparent, #00c8ff, #7b00ff, transparent);
}
.page-hero-icon { font-size: 3rem; }
.page-hero-title {
    font-family: 'Orbitron', monospace;
    font-size: 1.8rem; font-weight: 900; letter-spacing: 4px;
    color: #fff; text-shadow: 0 0 20px rgba(0,200,255,0.5);
}
.page-hero-sub {
    font-family: 'Rajdhani', sans-serif;
    font-size: 0.9rem; letter-spacing: 3px;
    color: rgba(180,210,255,0.6); text-transform: uppercase; margin-top: 0.3rem;
}

/* ── NAV CARDS (HOME) ── */
div[data-testid="column"] { padding: 0 6px !important; }

.stButton > button {
    background: rgba(5,18,45,0.88) !important;
    border: 1px solid rgba(0,200,255,0.22) !important;
    border-radius: 18px !important;
    width: 100% !important;
    height: 190px !important;
    cursor: pointer !important;
    transition: all 0.28s ease !important;
    box-shadow: 0 8px 32px rgba(0,0,0,0.45) !important;
    color: #e0e8ff !important;
    font-family: 'Rajdhani', sans-serif !important;
    font-size: 0.95rem !important;
    font-weight: 600 !important;
    letter-spacing: 1px !important;
    white-space: pre-wrap !important;
    line-height: 1.6 !important;
}
.stButton > button:hover {
    transform: translateY(-7px) !important;
    border-color: rgba(0,200,255,0.65) !important;
    box-shadow:
        0 22px 55px rgba(0,0,0,0.55),
        0 0 35px rgba(0,200,255,0.22),
        inset 0 -2px 0 #00c8ff !important;
    background: rgba(0,28,62,0.95) !important;
    color: #ffffff !important;
}
.stButton > button:focus {
    border-color: rgba(123,0,255,0.6) !important;
    outline: none !important;
}

/* Bottom back button style */
.bottom-back-btn {
    margin-top: 3rem;
    margin-bottom: 2rem;
    text-align: center;
}
.bottom-back-btn > button {
    height: 48px !important;
    width: 200px !important;
    border-radius: 30px !important;
    font-family: 'Orbitron', monospace !important;
    font-size: 0.75rem !important;
    letter-spacing: 3px !important;
    background: rgba(0,200,255,0.1) !important;
    border: 1px solid rgba(0,200,255,0.4) !important;
    color: #00c8ff !important;
    transition: all 0.3s ease !important;
}
.bottom-back-btn > button:hover {
    background: rgba(0,200,255,0.2) !important;
    border-color: #00c8ff !important;
    box-shadow: 0 0 20px rgba(0,200,255,0.3) !important;
    transform: scale(1.05) !important;
}

/* ── STAT CARDS ── */
.stats-row {
    display: grid; grid-template-columns: repeat(4,1fr);
    gap: 1rem; margin: 1rem 0 1.2rem;
}
.stat-card {
    background: rgba(5,15,35,0.85);
    border: 1px solid rgba(0,200,255,0.2);
    border-radius: 16px; padding: 1.4rem 1rem;
    text-align: center; position: relative; overflow: hidden;
    transition: all 0.3s ease;
    box-shadow: 0 8px 30px rgba(0,0,0,0.3);
}
.stat-card:hover {
    transform: translateY(-4px);
    border-color: rgba(0,200,255,0.5);
    box-shadow: 0 15px 40px rgba(0,0,0,0.4), 0 0 20px rgba(0,200,255,0.15);
}
.stat-glow {
    position: absolute; top: 0; left: 50%; transform: translateX(-50%);
    width: 60%; height: 1px;
    background: linear-gradient(90deg, transparent, #00c8ff, transparent);
}
.stat-value {
    font-family: 'Orbitron', monospace;
    font-size: 2.2rem; font-weight: 900; color: #fff;
    text-shadow: 0 0 20px rgba(0,200,255,0.5);
    margin: 0.5rem 0 0.3rem;
}
.stat-label {
    font-family: 'Rajdhani', sans-serif;
    font-size: 0.75rem; font-weight: 600; letter-spacing: 3px;
    color: rgba(150,180,255,0.7); text-transform: uppercase;
}
.stat-indicator {
    display: inline-block; width: 6px; height: 6px; border-radius: 50%;
    background: #00c8ff; box-shadow: 0 0 8px #00c8ff;
    margin-right: 5px; animation: blink 2s infinite; vertical-align: middle;
}

/* ── INFO / DATA CARDS (sub-pages) ── */
.info-card {
    background: rgba(5,15,35,0.85);
    border: 1px solid rgba(0,200,255,0.2);
    border-radius: 16px; padding: 1.5rem;
    margin-bottom: 1rem; position: relative; overflow: hidden;
    box-shadow: 0 8px 30px rgba(0,0,0,0.3);
}
.info-card h4 {
    font-family: 'Orbitron', monospace;
    font-size: 0.75rem; letter-spacing: 3px;
    color: #00c8ff; text-transform: uppercase; margin-bottom: 1rem;
}
.info-card p, .info-card li {
    font-family: 'Rajdhani', sans-serif;
    font-size: 1rem; color: rgba(200,220,255,0.8); letter-spacing: 1px; line-height: 1.7;
}

/* badge pill */
.badge {
    display: inline-block; border-radius: 50px; padding: 0.25rem 0.9rem;
    font-family: 'Orbitron', monospace; font-size: 0.6rem; letter-spacing: 2px;
    font-weight: 700; text-transform: uppercase; margin: 0.2rem;
}
.badge-green  { background: rgba(0,255,150,0.12); border: 1px solid rgba(0,255,150,0.35); color: #00ff96; }
.badge-red    { background: rgba(255,50,80,0.12);  border: 1px solid rgba(255,50,80,0.35);  color: #ff3252; }
.badge-blue   { background: rgba(0,200,255,0.12);  border: 1px solid rgba(0,200,255,0.35);  color: #00c8ff; }
.badge-purple { background: rgba(123,0,255,0.12);  border: 1px solid rgba(123,0,255,0.35);  color: #b060ff; }
.badge-orange { background: rgba(255,170,0,0.12);  border: 1px solid rgba(255,170,0,0.35);  color: #ffaa00; }
</style>
""", unsafe_allow_html=True)

    # Backdrop HTML (same on every page)
    st.markdown("""
<div class="bg-grid"></div>
<div class="bg-orb-1"></div>
<div class="bg-orb-2"></div>
<div class="bg-orb-3"></div>
<div class="scanline"></div>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
#  SHARED WIDGETS
# ─────────────────────────────────────────────
TICKER = ("● LI-FI: NOMINAL &nbsp;|&nbsp; ● RF 2.4GHz: ACTIVE &nbsp;|&nbsp; "
          "● THREAT LEVEL: LOW &nbsp;|&nbsp; ● DEVICES: 6/6 ONLINE &nbsp;|&nbsp; "
          "● ML ACCURACY: 98.3% &nbsp;|&nbsp; ● FAILOVER: READY &nbsp;|&nbsp; "
          "● PACKETS: 1,482,901 &nbsp;|&nbsp; ● UPTIME: 99.97% &nbsp;|&nbsp; ")

def render_ticker():
    st.markdown(f"""
<div class="ticker-wrap">
  <span class="ticker-text">{TICKER * 3}</span>
</div>""", unsafe_allow_html=True)

def render_status_bar():
    st.markdown("""
<div class="status-bar">
  <div class="status-online"><div class="status-dot"></div>SYSTEM OPERATIONAL</div>
  <span>ENCRYPTION: AES-256-GCM</span>
  <span>UPTIME: 99.97%</span>
  <span>LATENCY: 0.8ms</span>
  <span>NODE: ALPHA-7</span>
</div>""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
#  PAGE: HOME
# ─────────────────────────────────────────────
def page_home():
    inject_base_css()

    # Hero
    st.markdown("""
<div class="hero-wrapper">
  <div class="hero-badge">⚡ ACTIVE PROTECTION SYSTEM v2.4</div>
  <div class="hero-title">SHADOW<span>SWITCH</span></div>
  <div class="hero-sub">Resilient Li-Fi / RF IoT Defence Framework</div>
  <div class="hero-line"></div>
</div>""", unsafe_allow_html=True)

    render_ticker()
    render_status_bar()

    # ── NAV CARDS ──
    st.markdown('<div class="section-header">◈ NAVIGATION MODULES</div>', unsafe_allow_html=True)

    nav = [
        ("home_telem",   "telemetry",  "🛰️",  "LIVE\nTELEMETRY",  "Real-time signal streams"),
        ("home_trust",   "trust",      "🔐",  "TRUST\nSCORING",   "Device trust analytics"),
        ("home_dash",    "dashboard",  "🖥️",  "COMMAND\nDASHBOARD","Control & overview hub"),
        ("home_ml",      "ml",         "🧠",  "ML\nDETECTION",    "Anomaly classification"),
        ("home_fail",    "failover",   "⚡",  "FAILOVER\nLOGIC",  "Auto-switch protocols"),
    ]
    cols = st.columns(5)
    for col, (key, page, icon, title, desc) in zip(cols, nav):
        with col:
            label = f"{icon}\n\n{title}\n\n{desc}"
            if st.button(label, key=key, use_container_width=True):
                go(page)

    # ── SYSTEM METRICS ──
    st.markdown('<div class="section-header">◈ SYSTEM METRICS</div>', unsafe_allow_html=True)
    st.markdown("""
<div class="stats-row">
  <div class="stat-card">
    <div class="stat-glow"></div>
    <div class="stat-label"><span class="stat-indicator"></span>LI-FI BAND</div>
    <div class="stat-value">THz</div>
    <div style="font-size:.72rem;color:rgba(0,200,255,.5);letter-spacing:2px;margin-top:.3rem;">OPTICAL WIRELESS</div>
  </div>
  <div class="stat-card">
    <div class="stat-glow"></div>
    <div class="stat-label"><span class="stat-indicator"></span>RF BAND</div>
    <div class="stat-value" style="color:#00ff96;text-shadow:0 0 20px rgba(0,255,150,.5);">2.4GHz</div>
    <div style="font-size:.72rem;color:rgba(0,255,150,.5);letter-spacing:2px;margin-top:.3rem;">FALLBACK ACTIVE</div>
  </div>
  <div class="stat-card">
    <div class="stat-glow"></div>
    <div class="stat-label"><span class="stat-indicator"></span>ACTIVE DEVICES</div>
    <div class="stat-value" style="color:#c800ff;text-shadow:0 0 20px rgba(200,0,255,.5);">6</div>
    <div style="font-size:.72rem;color:rgba(200,0,255,.5);letter-spacing:2px;margin-top:.3rem;">ALL NODES ONLINE</div>
  </div>
  <div class="stat-card">
    <div class="stat-glow"></div>
    <div class="stat-label"><span class="stat-indicator"></span>THREATS BLOCKED</div>
    <div class="stat-value" style="color:#ff3252;text-shadow:0 0 20px rgba(255,50,80,.5);">127</div>
    <div style="font-size:.72rem;color:rgba(255,50,80,.5);letter-spacing:2px;margin-top:.3rem;">LAST 24 HOURS</div>
  </div>
</div>""", unsafe_allow_html=True)

    # Mini stats row
    mc = st.columns(6)
    mini = [
        ("⚡","LATENCY","0.8ms","#00c8ff"),
        ("🔒","ENCRYPT","AES-256","#7b00ff"),
        ("📶","SIGNAL","–42 dBm","#00ff96"),
        ("🛡️","TRUST AVG","94.2%","#00c8ff"),
        ("🔄","FAILOVERS","3","#ffaa00"),
        ("🧠","ML ACC","98.3%","#00ff96"),
    ]
    for col,(icon,lbl,val,clr) in zip(mc,mini):
        with col:
            st.markdown(f"""
<div style="background:rgba(5,15,35,.85);border:1px solid rgba(0,200,255,.15);
     border-radius:12px;padding:1rem .5rem;text-align:center;">
  <div style="font-size:1.4rem;">{icon}</div>
  <div style="font-family:'Orbitron',monospace;font-size:1rem;font-weight:900;
       color:{clr};text-shadow:0 0 15px {clr};">{val}</div>
  <div style="font-size:.65rem;letter-spacing:2px;color:rgba(150,180,255,.6);
       margin-top:.2rem;">{lbl}</div>
</div>""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
#  PAGE: LIVE TELEMETRY
# ─────────────────────────────────────────────
def page_telemetry():
    inject_base_css()

    st.markdown("""
<div class="page-hero">
  <div class="page-hero-icon">🛰️</div>
  <div>
    <div class="page-hero-title">LIVE TELEMETRY</div>
    <div class="page-hero-sub">Real-time Li-Fi &amp; RF signal monitoring</div>
  </div>
</div>""", unsafe_allow_html=True)

    render_ticker()

    # Live signal chart
    st.markdown('<div class="section-header">◈ SIGNAL STREAMS</div>', unsafe_allow_html=True)

    import pandas as pd
    t = np.linspace(0, 4*np.pi, 200)
    lifi  = 60 + 15*np.sin(t) + np.random.normal(0,2,200)
    rf    = 45 + 10*np.cos(t*0.8) + np.random.normal(0,3,200)
    noise = 10 + np.random.normal(0,2,200)
    df = pd.DataFrame({"Li-Fi (THz)": lifi, "RF 2.4GHz": rf, "Noise Floor": noise})
    st.line_chart(df, height=280, use_container_width=True)

    # Device table
    st.markdown('<div class="section-header">◈ DEVICE STATUS</div>', unsafe_allow_html=True)
    devices = [
        ("DEV-001","Smart Sensor","Li-Fi","–38 dBm","98.2%","🟢 ONLINE"),
        ("DEV-002","Gateway Node","RF","–45 dBm","94.7%","🟢 ONLINE"),
        ("DEV-003","Camera Unit","Li-Fi","–41 dBm","97.1%","🟢 ONLINE"),
        ("DEV-004","Edge Controller","RF","–52 dBm","89.3%","🟡 MARGINAL"),
        ("DEV-005","Relay Hub","Li-Fi","–36 dBm","99.0%","🟢 ONLINE"),
        ("DEV-006","Sensor Array","RF","–60 dBm","72.5%","🔴 WEAK"),
    ]
    cols_h = st.columns([1.2,1.8,1,1.2,1,1.2])
    headers = ["DEVICE ID","TYPE","CHANNEL","SIGNAL","TRUST","STATUS"]
    for c,h in zip(cols_h, headers):
        with c:
            st.markdown(f"<div style='font-family:Orbitron,monospace;font-size:.6rem;letter-spacing:2px;color:#00c8ff;padding:.5rem 0;border-bottom:1px solid rgba(0,200,255,.2);'>{h}</div>", unsafe_allow_html=True)
    for row in devices:
        row_cols = st.columns([1.2,1.8,1,1.2,1,1.2])
        for c,val in zip(row_cols, row):
            with c:
                st.markdown(f"<div style='font-family:Rajdhani,sans-serif;font-size:.9rem;color:rgba(200,220,255,.85);padding:.4rem 0;border-bottom:1px solid rgba(255,255,255,.04);letter-spacing:1px;'>{val}</div>", unsafe_allow_html=True)

    # Packet stats
    st.markdown('<div class="section-header">◈ PACKET ANALYSIS</div>', unsafe_allow_html=True)
    pc = st.columns(3)
    pstats = [
        ("1,482,901","TOTAL PACKETS","#00c8ff"),
        ("1,481,204","CLEAN PACKETS","#00ff96"),
        ("1,697","FLAGGED PACKETS","#ff3252"),
    ]
    for col,(val,lbl,clr) in zip(pc, pstats):
        with col:
            st.markdown(f"""
<div class="stat-card">
  <div class="stat-glow"></div>
  <div class="stat-label">{lbl}</div>
  <div class="stat-value" style="color:{clr};text-shadow:0 0 20px {clr};">{val}</div>
</div>""", unsafe_allow_html=True)
    
    # ===== BACK TO HOME BUTTON (BOTTOM) =====
    st.markdown("---")
    st.markdown('<div class="bottom-back-btn">', unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        if st.button("← BACK TO HOME", key="back_telemetry", use_container_width=True):
            go("home")
    st.markdown('</div>', unsafe_allow_html=True)


# ─────────────────────────────────────────────
#  PAGE: TRUST SCORING
# ─────────────────────────────────────────────
def page_trust():
    inject_base_css()

    st.markdown("""
<div class="page-hero">
  <div class="page-hero-icon">🔐</div>
  <div>
    <div class="page-hero-title">TRUST SCORING</div>
    <div class="page-hero-sub">Dynamic device trust &amp; reputation engine</div>
  </div>
</div>""", unsafe_allow_html=True)

    render_ticker()

    st.markdown('<div class="section-header">◈ TRUST OVERVIEW</div>', unsafe_allow_html=True)
    tc = st.columns(4)
    trust_stats = [
        ("94.2%","AVG TRUST SCORE","#00c8ff"),
        ("5","HIGH TRUST","#00ff96"),
        ("1","LOW TRUST","#ff3252"),
        ("0","BLACKLISTED","#7b00ff"),
    ]
    for col,(val,lbl,clr) in zip(tc, trust_stats):
        with col:
            st.markdown(f"""
<div class="stat-card">
  <div class="stat-glow"></div>
  <div class="stat-label">{lbl}</div>
  <div class="stat-value" style="color:{clr};text-shadow:0 0 20px {clr};">{val}</div>
</div>""", unsafe_allow_html=True)

    # Trust score bars
    st.markdown('<div class="section-header">◈ DEVICE TRUST SCORES</div>', unsafe_allow_html=True)
    trust_devices = [
        ("DEV-001","Smart Sensor",     99, "#00ff96", "TRUSTED"),
        ("DEV-002","Gateway Node",     94, "#00ff96", "TRUSTED"),
        ("DEV-003","Camera Unit",      97, "#00ff96", "TRUSTED"),
        ("DEV-004","Edge Controller",  82, "#ffaa00", "MODERATE"),
        ("DEV-005","Relay Hub",        98, "#00ff96", "TRUSTED"),
        ("DEV-006","Sensor Array",     61, "#ff3252", "LOW"),
    ]
    for dev_id, dtype, score, clr, label in trust_devices:
        bar_pct = score
        st.markdown(f"""
<div style="background:rgba(5,15,35,.85);border:1px solid rgba(0,200,255,.15);
     border-radius:12px;padding:1rem 1.5rem;margin-bottom:.6rem;display:flex;align-items:center;gap:1.5rem;">
  <div style="min-width:90px;font-family:Orbitron,monospace;font-size:.65rem;letter-spacing:2px;color:#00c8ff;">{dev_id}</div>
  <div style="min-width:140px;font-family:Rajdhani,sans-serif;font-size:.95rem;color:rgba(200,220,255,.8);">{dtype}</div>
  <div style="flex:1;background:rgba(0,200,255,.08);border-radius:50px;height:10px;overflow:hidden;">
    <div style="width:{bar_pct}%;height:100%;background:linear-gradient(90deg,{clr},{clr}aa);border-radius:50px;box-shadow:0 0 10px {clr};"></div>
  </div>
  <div style="min-width:50px;text-align:right;font-family:Orbitron,monospace;font-size:.9rem;font-weight:900;color:{clr};">{score}%</div>
  <div style="min-width:80px;text-align:center;font-family:Orbitron,monospace;font-size:.6rem;letter-spacing:2px;
       padding:.25rem .6rem;border-radius:50px;background:{clr}22;border:1px solid {clr}66;color:{clr};">{label}</div>
</div>""", unsafe_allow_html=True)

    # Trust factors
    st.markdown('<div class="section-header">◈ TRUST FACTORS</div>', unsafe_allow_html=True)
    fc = st.columns(2)
    with fc[0]:
        st.markdown("""
<div class="info-card">
  <h4>🔍 POSITIVE SIGNALS</h4>
  <ul>
    <li>Consistent signal strength &amp; timing</li>
    <li>Valid MAC &amp; device fingerprint</li>
    <li>Low packet loss ratio (&lt; 0.5%)</li>
    <li>Authenticated channel handshake</li>
    <li>Behavioural baseline conformity</li>
  </ul>
</div>""", unsafe_allow_html=True)
    with fc[1]:
        st.markdown("""
<div class="info-card">
  <h4>⚠️ RISK INDICATORS</h4>
  <ul>
    <li>Sudden signal anomalies or spikes</li>
    <li>Unknown device fingerprint</li>
    <li>High packet loss or corruption</li>
    <li>Failed authentication attempts</li>
    <li>Deviation from usage baseline</li>
  </ul>
</div>""", unsafe_allow_html=True)
    
    # ===== BACK TO HOME BUTTON (BOTTOM) =====
    st.markdown("---")
    st.markdown('<div class="bottom-back-btn">', unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        if st.button("← BACK TO HOME", key="back_trust", use_container_width=True):
            go("home")
    st.markdown('</div>', unsafe_allow_html=True)


# ─────────────────────────────────────────────
#  PAGE: DASHBOARD
# ─────────────────────────────────────────────
def page_dashboard():
    inject_base_css()

    st.markdown("""
<div class="page-hero">
  <div class="page-hero-icon">🖥️</div>
  <div>
    <div class="page-hero-title">COMMAND DASHBOARD</div>
    <div class="page-hero-sub">Unified situational awareness &amp; control hub</div>
  </div>
</div>""", unsafe_allow_html=True)

    render_ticker()
    render_status_bar()

    # KPI row
    st.markdown('<div class="section-header">◈ KEY PERFORMANCE INDICATORS</div>', unsafe_allow_html=True)
    st.markdown("""
<div class="stats-row">
  <div class="stat-card">
    <div class="stat-glow"></div>
    <div class="stat-label"><span class="stat-indicator"></span>SYSTEM HEALTH</div>
    <div class="stat-value" style="color:#00ff96;text-shadow:0 0 20px rgba(0,255,150,.5);">99.97%</div>
    <div style="font-size:.72rem;color:rgba(0,255,150,.5);letter-spacing:2px;margin-top:.3rem;">ALL SYSTEMS GO</div>
  </div>
  <div class="stat-card">
    <div class="stat-glow"></div>
    <div class="stat-label"><span class="stat-indicator"></span>ACTIVE CHANNELS</div>
    <div class="stat-value" style="color:#00c8ff;text-shadow:0 0 20px rgba(0,200,255,.5);">2</div>
    <div style="font-size:.72rem;color:rgba(0,200,255,.5);letter-spacing:2px;margin-top:.3rem;">LI-FI + RF</div>
  </div>
  <div class="stat-card">
    <div class="stat-glow"></div>
    <div class="stat-label"><span class="stat-indicator"></span>ALERTS TODAY</div>
    <div class="stat-value" style="color:#ffaa00;text-shadow:0 0 20px rgba(255,170,0,.5);">4</div>
    <div style="font-size:.72rem;color:rgba(255,170,0,.5);letter-spacing:2px;margin-top:.3rem;">2 RESOLVED</div>
  </div>
  <div class="stat-card">
    <div class="stat-glow"></div>
    <div class="stat-label"><span class="stat-indicator"></span>DATA THROUGHPUT</div>
    <div class="stat-value" style="color:#b060ff;text-shadow:0 0 20px rgba(176,96,255,.5);">2.4Gbps</div>
    <div style="font-size:.72rem;color:rgba(176,96,255,.5);letter-spacing:2px;margin-top:.3rem;">PEAK: 3.1GBPS</div>
  </div>
</div>""", unsafe_allow_html=True)

    # Two column layout
    left, right = st.columns([1.6, 1])

    with left:
        st.markdown('<div class="section-header">◈ THROUGHPUT (24H)</div>', unsafe_allow_html=True)
        import pandas as pd
        hours = list(range(24))
        lifi_tp  = [1.8+0.6*np.sin(h/3)+0.1*np.random.randn() for h in hours]
        rf_tp    = [0.6+0.2*np.cos(h/4)+0.05*np.random.randn() for h in hours]
        df_tp = pd.DataFrame({"Li-Fi Gbps": lifi_tp, "RF Gbps": rf_tp}, index=hours)
        st.area_chart(df_tp, height=220, use_container_width=True)

    with right:
        st.markdown('<div class="section-header">◈ RECENT EVENTS</div>', unsafe_allow_html=True)
        events = [
            ("🟢","00:02","DEV-001 authenticated"),
            ("🟡","00:08","DEV-006 signal weak"),
            ("🔴","00:15","Intrusion attempt blocked"),
            ("🔵","00:22","Failover tested — OK"),
            ("🟢","00:31","ML model retrained"),
            ("🟡","00:45","DEV-004 high latency"),
        ]
        for dot, ts, msg in events:
            st.markdown(f"""
<div style="display:flex;align-items:center;gap:.8rem;padding:.5rem 0;
     border-bottom:1px solid rgba(0,200,255,.07);">
  <span style="font-size:.9rem;">{dot}</span>
  <span style="font-family:Orbitron,monospace;font-size:.6rem;color:rgba(0,200,255,.6);min-width:45px;">{ts}</span>
  <span style="font-family:Rajdhani,sans-serif;font-size:.9rem;color:rgba(200,220,255,.8);">{msg}</span>
</div>""", unsafe_allow_html=True)

    # Channel comparison
    st.markdown('<div class="section-header">◈ CHANNEL STATUS</div>', unsafe_allow_html=True)
    ch_cols = st.columns(2)
    channels = [
        ("🔵 LI-FI CHANNEL","PRIMARY","THz Band","–38 dBm","Active","99.2%","#00c8ff"),
        ("🟣 RF CHANNEL","FAILOVER","2.4GHz Band","–45 dBm","Standby","94.7%","#b060ff"),
    ]
    for col, (name,role,band,sig,state,trust,clr) in zip(ch_cols, channels):
        with col:
            st.markdown(f"""
<div class="info-card" style="border-color:{clr}44;">
  <h4>{name}</h4>
  <p>
    <span class="badge badge-blue">{role}</span>
    <span class="badge badge-green">{state}</span>
  </p>
  <br>
  <p>Band &nbsp;&nbsp;: <b style="color:{clr};">{band}</b></p>
  <p>Signal : <b style="color:{clr};">{sig}</b></p>
  <p>Trust &nbsp;: <b style="color:{clr};">{trust}</b></p>
</div>""", unsafe_allow_html=True)
    
    # ===== BACK TO HOME BUTTON (BOTTOM) =====
    st.markdown("---")
    st.markdown('<div class="bottom-back-btn">', unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        if st.button("← BACK TO HOME", key="back_dashboard", use_container_width=True):
            go("home")
    st.markdown('</div>', unsafe_allow_html=True)


# ─────────────────────────────────────────────
#  PAGE: ML DETECTION
# ─────────────────────────────────────────────
def page_ml():
    inject_base_css()

    st.markdown("""
<div class="page-hero">
  <div class="page-hero-icon">🧠</div>
  <div>
    <div class="page-hero-title">ML DETECTION</div>
    <div class="page-hero-sub">Anomaly detection &amp; threat classification engine</div>
  </div>
</div>""", unsafe_allow_html=True)

    render_ticker()

    # Model stats
    st.markdown('<div class="section-header">◈ MODEL PERFORMANCE</div>', unsafe_allow_html=True)
    mc = st.columns(4)
    mstats = [
        ("98.3%","ACCURACY","#00ff96"),
        ("1.7%","FALSE POSITIVE","#ffaa00"),
        ("0.3ms","INFERENCE TIME","#00c8ff"),
        ("127","THREATS CAUGHT","#ff3252"),
    ]
    for col,(val,lbl,clr) in zip(mc, mstats):
        with col:
            st.markdown(f"""
<div class="stat-card">
  <div class="stat-glow"></div>
  <div class="stat-label">{lbl}</div>
  <div class="stat-value" style="color:{clr};text-shadow:0 0 20px {clr};">{val}</div>
</div>""", unsafe_allow_html=True)

    # Anomaly feed + confusion
    left, right = st.columns([1.6,1])

    with left:
        st.markdown('<div class="section-header">◈ ANOMALY DETECTION FEED</div>', unsafe_allow_html=True)
        import pandas as pd
        t2 = np.linspace(0, 6*np.pi, 300)
        normal_sig = 50 + 8*np.sin(t2) + np.random.normal(0,2,300)
        # inject anomalies
        anomaly_sig = normal_sig.copy()
        for idx in [60,130,210,270]:
            anomaly_sig[idx:idx+5] += np.random.uniform(25,45,5)
        df_ml = pd.DataFrame({"Normal Baseline": normal_sig, "Detected Signal": anomaly_sig})
        st.line_chart(df_ml, height=250, use_container_width=True)

    with right:
        st.markdown('<div class="section-header">◈ THREAT CATEGORIES</div>', unsafe_allow_html=True)
        threats = [
            ("Replay Attack",       "42", "#ff3252"),
            ("Signal Spoofing",     "31", "#ffaa00"),
            ("Jamming Attempt",     "28", "#ff3252"),
            ("Eavesdropping",       "15", "#b060ff"),
            ("MitM Attempt",        "8",  "#ff3252"),
            ("Anomalous Beacon",    "3",  "#ffaa00"),
        ]
        for tname, cnt, clr in threats:
            pct = int(cnt) / 127 * 100
            st.markdown(f"""
<div style="margin-bottom:.5rem;">
  <div style="display:flex;justify-content:space-between;margin-bottom:.3rem;">
    <span style="font-family:Rajdhani,sans-serif;font-size:.9rem;color:rgba(200,220,255,.8);">{tname}</span>
    <span style="font-family:Orbitron,monospace;font-size:.7rem;color:{clr};">{cnt}</span>
  </div>
  <div style="background:rgba(0,200,255,.08);border-radius:50px;height:6px;">
    <div style="width:{pct:.0f}%;height:100%;background:{clr};border-radius:50px;box-shadow:0 0 8px {clr};"></div>
  </div>
</div>""", unsafe_allow_html=True)

    # Model details
    st.markdown('<div class="section-header">◈ MODEL ARCHITECTURE</div>', unsafe_allow_html=True)
    mc2 = st.columns(2)
    with mc2[0]:
        st.markdown("""
<div class="info-card">
  <h4>🔬 ARCHITECTURE DETAILS</h4>
  <p>Model Type &nbsp;&nbsp;: Ensemble (RF + LSTM)</p>
  <p>Input Features : 24-dim signal vector</p>
  <p>Training Data &nbsp;: 2.1M labelled samples</p>
  <p>Update Cycle &nbsp;: Every 6 hours</p>
  <p>Deployment &nbsp;&nbsp;: Edge inference (TFLite)</p>
</div>""", unsafe_allow_html=True)
    with mc2[1]:
        st.markdown("""
<div class="info-card">
  <h4>📊 CONFUSION MATRIX SUMMARY</h4>
  <p>True Positive &nbsp;: <b style="color:#00ff96;">96.8%</b></p>
  <p>True Negative &nbsp;: <b style="color:#00ff96;">99.5%</b></p>
  <p>False Positive : <b style="color:#ffaa00;">1.7%</b></p>
  <p>False Negative : <b style="color:#ff3252;">0.3%</b></p>
  <p>F1 Score &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;: <b style="color:#00c8ff;">0.981</b></p>
</div>""", unsafe_allow_html=True)
    
    # ===== BACK TO HOME BUTTON (BOTTOM) =====
    st.markdown("---")
    st.markdown('<div class="bottom-back-btn">', unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        if st.button("← BACK TO HOME", key="back_ml", use_container_width=True):
            go("home")
    st.markdown('</div>', unsafe_allow_html=True)


# ─────────────────────────────────────────────
#  PAGE: FAILOVER LOGIC
# ─────────────────────────────────────────────
def page_failover():
    inject_base_css()

    st.markdown("""
<div class="page-hero">
  <div class="page-hero-icon">⚡</div>
  <div>
    <div class="page-hero-title">FAILOVER LOGIC</div>
    <div class="page-hero-sub">Autonomous channel switching &amp; resilience engine</div>
  </div>
</div>""", unsafe_allow_html=True)

    render_ticker()

    # Failover stats
    st.markdown('<div class="section-header">◈ FAILOVER STATISTICS</div>', unsafe_allow_html=True)
    fc = st.columns(4)
    fstats = [
        ("3","FAILOVERS TODAY","#ffaa00"),
        ("12ms","AVG SWITCH TIME","#00c8ff"),
        ("100%","SUCCESS RATE","#00ff96"),
        ("0","DATA LOSS EVENTS","#ff3252"),
    ]
    for col,(val,lbl,clr) in zip(fc, fstats):
        with col:
            st.markdown(f"""
<div class="stat-card">
  <div class="stat-glow"></div>
  <div class="stat-label">{lbl}</div>
  <div class="stat-value" style="color:{clr};text-shadow:0 0 20px {clr};">{val}</div>
</div>""", unsafe_allow_html=True)

    # Channel selector simulation
    st.markdown('<div class="section-header">◈ CHANNEL CONTROL</div>', unsafe_allow_html=True)
    fl, fr = st.columns([1,1])
    with fl:
        st.markdown("""
<div class="info-card">
  <h4>🔵 PRIMARY: LI-FI</h4>
  <p>Status &nbsp;&nbsp;&nbsp;: <b style="color:#00ff96;">ACTIVE</b></p>
  <p>Frequency : <b style="color:#00c8ff;">THz Band</b></p>
  <p>Latency &nbsp;: <b style="color:#00c8ff;">0.8ms</b></p>
  <p>Throughput: <b style="color:#00c8ff;">2.4 Gbps</b></p>
  <p>Resilience: <b style="color:#00c8ff;">High (line-of-sight)</b></p>
  <p>Triggers failover when SNR &lt; 15dB or packet loss &gt; 2%</p>
</div>""", unsafe_allow_html=True)
    with fr:
        st.markdown("""
<div class="info-card">
  <h4>🟣 FAILOVER: RF 2.4GHz</h4>
  <p>Status &nbsp;&nbsp;&nbsp;: <b style="color:#ffaa00;">STANDBY</b></p>
  <p>Frequency : <b style="color:#b060ff;">2.4 GHz</b></p>
  <p>Latency &nbsp;: <b style="color:#b060ff;">4.2ms</b></p>
  <p>Throughput: <b style="color:#b060ff;">0.6 Gbps</b></p>
  <p>Resilience: <b style="color:#b060ff;">Medium (NLOS capable)</b></p>
  <p>Activates automatically on primary channel failure</p>
</div>""", unsafe_allow_html=True)

    # Failover event log
    st.markdown('<div class="section-header">◈ FAILOVER EVENT LOG</div>', unsafe_allow_html=True)
    events = [
        ("08:14:32","Li-Fi → RF","SNR drop below threshold","12ms","✅ SUCCESS"),
        ("11:47:05","Li-Fi → RF","Physical obstruction detected","9ms","✅ SUCCESS"),
        ("14:22:18","RF → Li-Fi","Primary channel restored","7ms","✅ SUCCESS"),
        ("00:00:00","Scheduled test","Automated failover test","11ms","✅ SUCCESS"),
    ]
    headers = ["TIME","TRANSITION","TRIGGER","SWITCH TIME","RESULT"]
    hcols = st.columns([1,1.2,2,1,1])
    for c,h in zip(hcols, headers):
        with c:
            st.markdown(f"<div style='font-family:Orbitron,monospace;font-size:.6rem;letter-spacing:2px;color:#00c8ff;padding:.5rem 0;border-bottom:1px solid rgba(0,200,255,.2);'>{h}</div>", unsafe_allow_html=True)
    for ts, trans, trig, sw, res in events:
        rcols = st.columns([1,1.2,2,1,1])
        vals = [ts, trans, trig, sw, res]
        for c,v in zip(rcols, vals):
            with c:
                st.markdown(f"<div style='font-family:Rajdhani,sans-serif;font-size:.9rem;color:rgba(200,220,255,.85);padding:.45rem 0;border-bottom:1px solid rgba(255,255,255,.04);letter-spacing:1px;'>{v}</div>", unsafe_allow_html=True)

    # Decision logic
    st.markdown('<div class="section-header">◈ DECISION LOGIC</div>', unsafe_allow_html=True)
    st.markdown("""
<div class="info-card">
  <h4>⚙️ AUTOMATED SWITCHING RULES</h4>
  <p>1. Monitor Li-Fi SNR every 50ms — if SNR &lt; 15dB for 3 consecutive readings → trigger failover</p>
  <p>2. Monitor packet loss ratio — if loss &gt; 2% over 1s window → trigger failover</p>
  <p>3. On ML anomaly score &gt; 0.85 (potential attack) → isolate and switch channel immediately</p>
  <p>4. RF channel kept warm (beacon exchange every 500ms) for &lt; 10ms switch latency</p>
  <p>5. Auto-restore to Li-Fi when SNR &gt; 25dB stable for 5 seconds</p>
</div>""", unsafe_allow_html=True)
    
    # ===== BACK TO HOME BUTTON (BOTTOM) =====
    st.markdown("---")
    st.markdown('<div class="bottom-back-btn">', unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        if st.button("← BACK TO HOME", key="back_failover", use_container_width=True):
            go("home")
    st.markdown('</div>', unsafe_allow_html=True)


# ─────────────────────────────────────────────
#  ROUTER
# ─────────────────────────────────────────────
page = st.session_state.page

if page == "home":
    page_home()
elif page == "telemetry":
    page_telemetry()
elif page == "trust":
    page_trust()
elif page == "dashboard":
    page_dashboard()
elif page == "ml":
    page_ml()
elif page == "failover":
    page_failover()
else:
    go("home")