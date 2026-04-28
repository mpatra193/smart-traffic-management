# dashboard/app.py
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

import streamlit as st
import cv2
import time
import json
from datetime import datetime
from deep_translator import GoogleTranslator
from models.traffic_ai import get_signal_timing
from mock_data.simulator import is_emergency_vehicle
from detector.detector import detect_vehicles_in_frame, detect_vehicles_by_zone  # ← FIXED IMPORT

# --- PAGE CONFIG ---
st.set_page_config(page_title="🚦 TrafficFlow AI - AIoT Hackathon", layout="wide")
st.title("🚦 Smart Traffic Signal Control for Indian Roads")

# --- LANGUAGE ---
lang = st.sidebar.selectbox("Select Language", ["English", "Hindi", "Tamil"])

# --- INPUT SOURCE SELECTOR ---
input_source = st.sidebar.radio(
    "Select Input Source",
    ["Video File", "Live Webcam"]
)

def translate_text(text, target_lang):
    if target_lang == "English":
        return text
    try:
        lang_code = {"Hindi": "hi", "Tamil": "ta"}.get(target_lang, "en")
        return GoogleTranslator(source='en', target=lang_code).translate(text)
    except Exception as e:
        return text

# --- VIDEO SETUP ---
if input_source == "Video File":
    video_path = os.path.join(os.path.dirname(__file__), "..", "data", "intersection.mp4")
    cap = cv2.VideoCapture(video_path)
else:  # Live Webcam
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        st.warning("⚠️ Webcam not found. Switching to demo video...")
        input_source = "Video File"
        video_path = os.path.join(os.path.dirname(__file__), "..", "data", "intersection.mp4")
        cap = cv2.VideoCapture(video_path)

if not cap.isOpened():
    st.error("❌ Could not open video/webcam. Check path or connection.")
    st.stop()

# --- LOGGING SETUP ---
LOG_FILE = os.path.join(os.path.dirname(__file__), "..", "data", "traffic_log.json")
os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)

# --- DASHBOARD PLACEHOLDERS SETUP ---
st.markdown("---")
col1, col2 = st.columns(2)

with col1:
    st.subheader(translate_text("🚦 Real-Time Signal Control", lang))
    mode_metric = st.empty()
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Sub-columns for stable layout (labels never redraw)
    col_label, col_val = st.columns([2, 1])
    
    with col_label:
        st.write(translate_text("**🟢 North-South Green:**", lang))
        st.write(translate_text("**🟢 East-West Green:**", lang))
        st.write(translate_text("**🚗 Total Vehicles:**", lang))
        st.write(translate_text("**⬅️ Left Lane:**", lang))
        st.write(translate_text("**➡️ Right Lane:**", lang))
        
    with col_val:
        ns_green = st.empty()
        ew_green = st.empty()
        tot_veh_metric = st.empty()
        left_lane = st.empty()
        right_lane = st.empty()
        
    emerg_alert = st.empty()
    wait_saved = st.empty()

with col2:
    st.subheader(translate_text("📹 Live Feed", lang))
    video_feed = st.empty()

frame_skip = 5
frame_count = 0

# --- MAIN LOOP ---
while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    frame_count += 1
    if frame_count % frame_skip != 0:
        continue  # Skip this frame

    # 🚗 REAL VEHICLE DETECTION (NOT RANDOM!)
    zone_counts = detect_vehicles_by_zone(frame)
    ns_count = zone_counts["left"]   # Assign left half of screen to North-South
    ew_count = zone_counts["right"]  # Assign right half of screen to East-West
    total_vehicles = ns_count + ew_count

    # 🚑 EMERGENCY SIMULATION (Can upgrade to visual detection later)
    emergency = is_emergency_vehicle()

    # 🧠 AI DECISION (Lane-aware, India-trained)
    signal_plan = get_signal_timing(ns_count, ew_count, emergency)

    # 📊 LOG DATA
    log_entry = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "ns_vehicles": ns_count,
        "ew_vehicles": ew_count,
        "total_vehicles": total_vehicles,
        "green_ns": signal_plan["green_ns"],
        "green_ew": signal_plan["green_ew"],
        "mode": signal_plan["mode"],
        "emergency": emergency,
        "wait_saved_sec": signal_plan["wait_saved"]
    }

    try:
        with open(LOG_FILE, "a") as f:
            f.write(json.dumps(log_entry) + "\n")
    except Exception as e:
        st.warning(f"⚠️ Log write failed: {e}")

    # 🖥️ UPDATE DASHBOARD
    mode_metric.metric(translate_text("Mode", lang), translate_text(signal_plan["mode"], lang))
    
    # Only update the numbers, leaves the text completely untouched
    ns_green.write(f"**{signal_plan['green_ns']} sec**")
    ew_green.write(f"**{signal_plan['green_ew']} sec**")
    tot_veh_metric.write(f"**{total_vehicles}**")
    left_lane.write(f"**{zone_counts['left']}**")
    right_lane.write(f"**{zone_counts['right']}**")
    
    if emergency:
        emerg_alert.warning(translate_text("🚑 EMERGENCY VEHICLE DETECTED — GREEN WAVE ACTIVATED", lang))
    else:
        emerg_alert.empty()
        
    wait_saved.success(translate_text(f"⏱️ Estimated Wait Time Saved: {signal_plan['wait_saved']} sec", lang))

    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    video_feed.image(frame_rgb, use_container_width=True)

    time.sleep(0.00001)

# --- END ---
cap.release()
st.success(translate_text("✅ Simulation Complete — Ready for Deployment Across India!", lang))