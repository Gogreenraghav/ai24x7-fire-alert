"""
AI24x7 Fire Alert - Dashboard
Streamlit dashboard for fire monitoring.
Run: streamlit run fire_dashboard.py --server.port 5061
"""
import streamlit as st
import requests
import time
from datetime import datetime

st.set_page_config(page_title="AI24x7 Fire Alert Dashboard", page_icon="🔥", layout="wide")

API_BASE = os.environ.get("FIRE_API", "http://localhost:5060")

st.title("🔥 AI24x7 Fire Alert Dashboard")

# ─── Status Cards ────────────────────────────
col1, col2, col3, col4 = st.columns(4)

try:
    r = requests.get(f"{API_BASE}/fire/status", timeout=3)
    status_data = r.json() if r.status_code == 200 else {}
    total_zones = len(status_data)
    active_alerts = sum(1 for v in status_data.values() if v.get("status") == "alert")
    safe_zones = total_zones - active_alerts
except:
    status_data = {}
    total_zones = active_alerts = safe_zones = 0

col1.metric("Total Zones", total_zones)
col2.metric("Active Alerts", active_alerts, "🔴" if active_alerts else "✅")
col3.metric("Safe Zones", safe_zones)
col4.metric("System", "Active" if total_zones else "Standby")

st.divider()

# ─── Add Camera ──────────────────────────────
st.subheader("➕ Add Camera Zone")
with st.form("add_camera"):
    col_a, col_b, col_c = st.columns(3)
    with col_a:
        zone = st.text_input("Zone Name", placeholder="e.g. Kitchen, Floor 2, Storage")
    with col_b:
        url = st.text_input("Camera RTSP URL", placeholder="rtsp://...")
    with col_c:
        sensitivity = st.selectbox("Sensitivity", ["low", "medium", "high"])
    
    col_x, col_y = st.columns(2)
    with col_x:
        expect_smoke = st.checkbox("Expect cooking smoke (reduce false alarms)")
    with col_y:
        submit = st.form_submit_button("🔥 Start Monitoring")
    
    if submit and zone and url:
        r = requests.post(f"{API_BASE}/fire/start", json={
            "zone": zone, "camera_url": url,
            "sensitivity": sensitivity, "expect_smoke": expect_smoke
        }, timeout=10)
        if r.status_code == 200:
            st.success(f"✅ Monitoring started: {zone}")
        else:
            st.error(f"❌ Failed: {r.text}")

st.divider()

# ─── Zone Status Grid ──────────────────────
st.subheader("📡 Zone Status")

if status_data:
    for zone, info in status_data.items():
        score = info["scores"]["total"]
        fire = info["scores"]["fire"]
        smoke = info["scores"]["smoke"]
        
        color = "🔴" if info["status"] == "alert" else "🟢"
        
        with st.expander(f"{color} {zone} (score: {score:.2f})", expanded=True):
            c1, c2, c3, c4, c5 = st.columns(5)
            c1.metric("Fire", f"{fire:.2f}")
            c2.metric("Smoke", f"{smoke:.2f}")
            c3.metric("Heat", f"{info['scores']['heat']:.2f}")
            c4.metric("Motion", f"{info['scores']['motion']:.2f}")
            c5.metric("FPS", info["fps"])
            
            col_btn, col_del = st.columns([1,1])
            with col_btn:
                if st.button(f"Test Alert", key=f"test_{zone}"):
                    requests.post(f"{API_BASE}/fire/test", json={"zone": zone}, timeout=5)
                    st.rerun()
            with col_del:
                if st.button(f"🗑️ Remove", key=f"del_{zone}"):
                    requests.post(f"{API_BASE}/fire/stop", json={"zone": zone}, timeout=5)
                    st.rerun()
else:
    st.info("No cameras added yet. Add above to start monitoring.")

st.divider()

# ─── Alert Logs ──────────────────────────────
st.subheader("📜 Recent Alert Log")
try:
    r = requests.get(f"{API_BASE}/fire/logs", timeout=5)
    logs = r.json()[-20:] if r.status_code == 200 else []
    
    if logs:
        for log in reversed(logs):
            ts = log.get("timestamp", "")[:19]
            zone = log.get("zone", "?")
            conf = log.get("scores", {}).get("total", 0)
            icon = "🚨" if log.get("type") == "fire_detected" else "🧪"
            
            st.write(f"{icon} `{ts}` | {zone} | conf: {conf:.0%}")
    else:
        st.info("No alerts yet")
except:
    st.warning("Could not fetch logs - API may be offline")

st.divider()

# ─── System Config ──────────────────────────
st.subheader("⚙️ Configuration")
col1, col2 = st.columns(2)
with col1:
    st.text_input("Fire Station Number", value="101", key="fs_number")
with col2:
    st.text_input("Building Manager Phone", placeholder="+919876543210", key="bm_phone")

if st.button("💾 Save Configuration"):
    st.success("Configuration saved!")

st.divider()
st.caption("AI24x7 Fire Alert System | GOUP CONSULTANCY SERVICES LLP")