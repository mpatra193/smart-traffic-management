# dashboard/app.py
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

import streamlit as st
import cv2
import time
import json
from datetime import datetime
from collections import deque
from deep_translator import GoogleTranslator
from models.traffic_ai import get_signal_timing
from mock_data.simulator import is_emergency_vehicle
import importlib

import detector.detector
importlib.reload(detector.detector)
from detector.detector import detect_vehicles_in_frame, detect_vehicles_by_zone

import utils.stream_handler
importlib.reload(utils.stream_handler)
from utils.stream_handler import StreamHandler
import pandas as pd
import pydeck as pdk
import requests
import polyline
import networkx as nx

# --- PAGE CONFIG ---
st.set_page_config(page_title="Traffic Route Optimizer", layout="wide")

# Custom CSS to reduce the font size of metrics to prevent truncation
st.markdown("""
<style>
[data-testid="stMetricValue"] {
    font-size: 1.2rem !important;
}
</style>
""", unsafe_allow_html=True)

st.title("Traffic Route Optimizer")

# --- LANGUAGE ---
lang = st.sidebar.selectbox("Select Language", ["English", "Hindi", "Tamil"])

# Language selector already defined above this chunk

def translate_text(text, target_lang):
    if target_lang == "English":
        return text
    try:
        lang_code = {"Hindi": "hi", "Tamil": "ta"}.get(target_lang, "en")
        return GoogleTranslator(source='en', target=lang_code).translate(text)
    except Exception as e:
        return text

import heapq
import random

@st.cache_data(show_spinner=False, ttl=3600)
def get_osrm_route(waypoints):
    """Fetches actual road geometry through waypoints from OSRM.
    waypoints: list of (lat, lon) tuples.
    Returns list of [lon, lat] for PyDeck PathLayer.
    """
    coord_str = ";".join(f"{lon},{lat}" for lat, lon in waypoints)
    url = f"http://router.project-osrm.org/route/v1/driving/{coord_str}?overview=full&geometries=polyline"
    try:
        r = requests.get(url, timeout=6)
        data = r.json()
        if data.get('code') == 'Ok':
            decoded = polyline.decode(data['routes'][0]['geometry'])
            return [[p[1], p[0]] for p in decoded]
    except Exception:
        pass
    return None

def dijkstra(graph, weights, source, target):
    """
    (Deprecated - Now using networkx in main loop)
    """
    pass

# ─── 25 CCTV cameras forming a dense grid in Bhubaneswar, Odisha ───────────────
CCTV_POINTS = [
    # Row 0: Lat 20.26 (South)
    {"id": "CAM-01", "name": "Khandagiri Square",       "lat": 20.2589, "lon": 85.7831, "video": "intersection.mp4", "type": "4-way"},
    {"id": "CAM-02", "name": "Ganga Nagar",             "lat": 20.2590, "lon": 85.8120, "video": "intersection.mp4", "type": "4-way"},
    {"id": "CAM-03", "name": "AG Square",               "lat": 20.2625, "lon": 85.8318, "video": "intersection.mp4", "type": "4-way"},
    {"id": "CAM-04", "name": "Raj Mahal Square",        "lat": 20.2625, "lon": 85.8385, "video": "intersection.mp4", "type": "4-way"},
    {"id": "CAM-05", "name": "Kalpana Square",          "lat": 20.2543, "lon": 85.8432, "video": "intersection.mp4", "type": "4-way"},

    # Row 1: Lat 20.27
    {"id": "CAM-06", "name": "Fire Station Square",     "lat": 20.2721, "lon": 85.7981, "video": "intersection.mp4", "type": "4-way"},
    {"id": "CAM-07", "name": "Siripur Square",          "lat": 20.2730, "lon": 85.8100, "video": "intersection.mp4", "type": "4-way"},
    {"id": "CAM-08", "name": "Unit 4 Market",           "lat": 20.2730, "lon": 85.8250, "video": "intersection.mp4", "type": "2-way"},
    {"id": "CAM-09", "name": "Master Canteen",          "lat": 20.2666, "lon": 85.8436, "video": "intersection.mp4", "type": "4-way"},
    {"id": "CAM-10", "name": "Cuttack Road South",      "lat": 20.2710, "lon": 85.8450, "video": "intersection.mp4", "type": "2-way"},

    # Row 2: Lat 20.28
    {"id": "CAM-11", "name": "CRP Square",              "lat": 20.2853, "lon": 85.8080, "video": "intersection.mp4", "type": "4-way"},
    {"id": "CAM-12", "name": "Nayapalli",               "lat": 20.2850, "lon": 85.8150, "video": "intersection.mp4", "type": "2-way"},
    {"id": "CAM-13", "name": "Shastri Nagar",           "lat": 20.2850, "lon": 85.8250, "video": "intersection.mp4", "type": "4-way"},
    {"id": "CAM-14", "name": "Ram Mandir Square",       "lat": 20.2766, "lon": 85.8415, "video": "intersection.mp4", "type": "4-way"},
    {"id": "CAM-15", "name": "Bomikhal",                "lat": 20.2844, "lon": 85.8465, "video": "intersection.mp4", "type": "2-way"},

    # Row 3: Lat 20.29
    {"id": "CAM-16", "name": "Rental Colony",           "lat": 20.2910, "lon": 85.8050, "video": "intersection.mp4", "type": "2-way"},
    {"id": "CAM-17", "name": "IRC Village",             "lat": 20.2910, "lon": 85.8120, "video": "intersection.mp4", "type": "4-way"},
    {"id": "CAM-18", "name": "Acharya Vihar",           "lat": 20.2965, "lon": 85.8245, "video": "intersection.mp4", "type": "4-way"},
    {"id": "CAM-19", "name": "Rupali Square",           "lat": 20.2882, "lon": 85.8368, "video": "intersection.mp4", "type": "4-way"},
    {"id": "CAM-20", "name": "VSS Nagar",               "lat": 20.2910, "lon": 85.8450, "video": "intersection.mp4", "type": "2-way"},

    # Row 4: Lat 20.30
    {"id": "CAM-21", "name": "Baramunda",               "lat": 20.2711, "lon": 85.7932, "video": "intersection.mp4", "type": "2-way"},
    {"id": "CAM-22", "name": "Jayadev Vihar Square",    "lat": 20.3013, "lon": 85.8175, "video": "intersection.mp4", "type": "4-way"},
    {"id": "CAM-23", "name": "Sainik School",           "lat": 20.3010, "lon": 85.8250, "video": "intersection.mp4", "type": "2-way"},
    {"id": "CAM-24", "name": "Vani Vihar",              "lat": 20.2942, "lon": 85.8340, "video": "intersection.mp4", "type": "4-way"},
    {"id": "CAM-25", "name": "Rasulgarh Square",        "lat": 20.2982, "lon": 85.8491, "video": "intersection.mp4", "type": "4-way"},
]

# Road graph: which cameras are connected by direct roads
# (index-based, 0 = CAM-01 ... 24 = CAM-25)
ROAD_GRAPH = {
    0: [1, 20], 1: [0, 2, 10, 12], 2: [1, 3, 5], 3: [2, 4, 14], 4: [3, 7],
    5: [2, 6, 12], 6: [5, 7, 13], 7: [6, 8], 8: [7, 9], 9: [8, 19],
    10: [1, 11], 11: [10, 15], 12: [1, 5], 13: [6, 14], 14: [3, 13, 15],
    15: [11, 14, 16], 16: [15, 17], 17: [16, 18], 18: [17, 19], 19: [9, 18],
    20: [0, 21], 21: [20, 22], 22: [21, 23], 23: [22, 24], 24: [23]
}

# Pre-build NetworkX graph
G_ROAD = nx.Graph()
for node, neighbors in ROAD_GRAPH.items():
    for neighbor in neighbors:
        G_ROAD.add_edge(node, neighbor)

# --- ROUTING & CAMERA CONTROLS ---
st.sidebar.markdown("---")
cam_names = [cam["name"] for cam in CCTV_POINTS]
active_cam_name = st.sidebar.selectbox("View Live Feed From:", cam_names, index=5)
st.sidebar.markdown("---")
st.sidebar.subheader("Emergency Routing")
source_cam_name = st.sidebar.selectbox("From (Source)", cam_names, index=0)
dest_cam_name = st.sidebar.selectbox("To (Destination)", cam_names, index=24)

st.sidebar.markdown("---")
st.sidebar.subheader("Stream Source (Tier 1)")
custom_url = st.sidebar.text_input("Custom Stream URL (RTSP/YouTube)", value="", help="Leave blank to use public defaults / offline video")
stream_status = st.sidebar.empty()

active_cam_idx = cam_names.index(active_cam_name)
active_cam = CCTV_POINTS[active_cam_idx]
source_idx = cam_names.index(source_cam_name)
dest_idx = cam_names.index(dest_cam_name)

# --- VIDEO SETUP ---
video_path = os.path.join(os.path.dirname(__file__), "..", "data", active_cam["video"])

if 'stream_handler' not in st.session_state:
    st.session_state.stream_handler = StreamHandler(primary_url=custom_url, default_video_path=video_path)
    st.session_state.stream_handler.start()
else:
    if st.session_state.stream_handler.primary_url != custom_url or st.session_state.stream_handler.default_video_path != video_path:
        st.session_state.stream_handler.stop()
        st.session_state.stream_handler = StreamHandler(primary_url=custom_url, default_video_path=video_path)
        st.session_state.stream_handler.start()

cap = st.session_state.stream_handler

# --- LOGGING SETUP ---
LOG_FILE = os.path.join(os.path.dirname(__file__), "..", "data", "traffic_log.jsonl")
os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)

# --- DASHBOARD PLACEHOLDERS SETUP ---
if 'history_time' not in st.session_state:
    st.session_state.history_time = deque(maxlen=50)
    st.session_state.history_ns = deque(maxlen=50)
    st.session_state.history_ew = deque(maxlen=50)

st.markdown("---")

# 1. High-Level KPI Row
kpi_col1, kpi_col2, kpi_col3 = st.columns(3)
with kpi_col1:
    kpi_total_vehicles = st.empty()
with kpi_col2:
    kpi_mode = st.empty()
with kpi_col3:
    kpi_wait_saved = st.empty()

st.markdown("---")

# 2. Live Monitoring Section
feed_col1, feed_col2 = st.columns([1, 1])

with feed_col1:
    st.subheader(translate_text("Live Video Feed", lang))
    video_feed = st.empty()
    emerg_alert = st.empty()

with feed_col2:
    st.subheader(translate_text("Bhubaneswar Map & Routing", lang))
    map_feed = st.empty()

st.markdown("---")

# 3. Analytics & Trends Section
st.subheader(translate_text("System Analytics", lang))
chart_col1, chart_col2 = st.columns([1, 1])

with chart_col1:
    st.markdown("**Traffic Volume Trend (Last 50 frames)**")
    volume_container = st.empty()

with chart_col2:
    st.markdown("**Optimal Green Light Allocation**")
    efficiency_container = st.empty()

frame_skip = 5
frame_count = 0
last_map_state = None
last_dijkstra_path = []
last_osrm_route = []

# --- Initialize City Traffic State ---
# This gives each camera its own independent traffic level that drifts over time
city_traffic = [{"ns": random.randint(2, 12), "ew": random.randint(2, 12)} for _ in range(25)]

# --- MAIN LOOP ---
while cap.running:
    ret, frame = cap.read()
    if not ret:
        time.sleep(0.05)
        continue
        
    stream_status.info(f"Current Source:\n{cap.get_source_type()}")

    frame_count += 1
    if frame_count % frame_skip != 0:
        continue  # Skip this frame

    # 🚗 REAL VEHICLE DETECTION (NOT RANDOM!)
    zone_counts, annotated_frame = detect_vehicles_by_zone(frame, crossing_type=active_cam["type"])
    ns_count = zone_counts["left"]   # Assign left dict key to North-South
    ew_count = zone_counts["right"]  # Assign right dict key to East-West
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
        st.warning(f"Log write failed: {e}")

    # 🖥️ UPDATE DASHBOARD
    # KPI Row
    kpi_total_vehicles.metric("Total Network Congestion", total_vehicles)
    kpi_mode.metric("Active Signal Mode", translate_text(signal_plan["mode"], lang))
    kpi_wait_saved.metric("Estimated Wait Time Saved", f"{signal_plan['wait_saved']} sec")

    if emergency:
        emerg_alert.warning(translate_text("EMERGENCY VEHICLE DETECTED — GREEN WAVE ACTIVATED", lang))
    else:
        emerg_alert.empty()

    # Video Feed
    annotated_rgb = cv2.cvtColor(annotated_frame, cv2.COLOR_BGR2RGB)
    video_feed.image(annotated_rgb, width='stretch')
    
    # Analytics Row
    st.session_state.history_time.append(datetime.now().strftime("%H:%M:%S"))
    st.session_state.history_ns.append(ns_count)
    st.session_state.history_ew.append(ew_count)
    
    with volume_container.container():
        # Determine current trend
        if ns_count > ew_count + 5:
            trend_msg = "**North-South** traffic is currently dominating the intersection."
        elif ew_count > ns_count + 5:
            trend_msg = "**East-West** traffic is currently dominating the intersection."
        else:
            trend_msg = "Traffic flow is currently **balanced**."
            
        st.info(trend_msg)
        
        df_vol = pd.DataFrame({
            "Time": list(st.session_state.history_time),
            "North-South": list(st.session_state.history_ns),
            "East-West": list(st.session_state.history_ew)
        }).set_index("Time")
        
        st.line_chart(df_vol, height=200)

    with efficiency_container.container():
        st.markdown("### Recommended Time")
        ec1, ec2 = st.columns(2)
        ec1.metric("North-South", f"{signal_plan['green_ns']} sec", f"{ns_count} vehicles waiting", delta_color="off")
        ec2.metric("East-West", f"{signal_plan['green_ew']} sec", f"{ew_count} vehicles waiting", delta_color="off")
        
        total_time = signal_plan['green_ns'] + signal_plan['green_ew']
        if total_time > 0:
            ns_pct = signal_plan['green_ns'] / total_time
            ew_pct = signal_plan['green_ew'] / total_time
            st.markdown(f"**North-South Priority ({int(ns_pct*100)}%)**")
            st.progress(float(ns_pct))
            st.markdown(f"**East-West Priority ({int(ew_pct*100)}%)**")
            st.progress(float(ew_pct))

    # 🗺️ UPDATE MAP — Dijkstra + OSRM on 25 CCTVs, Bandra West
    current_map_state = f"{ns_count}_{ew_count}_{source_idx}_{dest_idx}_{active_cam_idx}"

    if current_map_state != last_map_state:
        last_map_state = current_map_state

        # --- Step 1: Generate per-camera congestion scores ---
        cam_scores = {}   # node_index -> total vehicles seen
        cctv_rows = []

        for i, cam in enumerate(CCTV_POINTS):
            if i == active_cam_idx:
                # Active camera gets EXACT counts from the live video feed
                cam_ns = ns_count
                cam_ew = ew_count
            else:
                # Other cameras get a random walk to simulate independent city traffic
                city_traffic[i]["ns"] = max(1, city_traffic[i]["ns"] + random.choice([-1, 0, 1]))
                city_traffic[i]["ew"] = max(1, city_traffic[i]["ew"] + random.choice([-1, 0, 1]))
                cam_ns = city_traffic[i]["ns"]
                cam_ew = city_traffic[i]["ew"]

            score = cam_ns + cam_ew          # total traffic = Dijkstra cost
            cam_scores[i] = max(score, 0.1)

            # Color Logic based on TOTAL volume (Congestion Level)
            if score > 15:
                color = [220, 40, 40, 240]   # Red
                status = f"Heavy Traffic ({score} vehicles)"
            elif score > 8:
                color = [255, 200, 40, 240]  # Yellow
                status = f"Moderate Traffic ({score} vehicles)"
            else:
                color = [40, 200, 40, 240]   # Green
                status = f"Clear Traffic ({score} vehicles)"

            cctv_rows.append({
                "lat": cam["lat"], "lon": cam["lon"],
                "color": color, "radius": 12,
                "label": f"{cam['id']} — {cam['name']}\n{status}"
            })

        # --- Step 2: Dijkstra — least-congested path from user-selected Source to Destination ---
        # Update edge weights in NetworkX graph
        for u, v in G_ROAD.edges():
            w_u = cam_scores.get(u, 1)
            w_v = cam_scores.get(v, 1)
            
            # Exponential penalty to aggressively avoid red nodes (heavy traffic)
            cost_u = w_u * 10 if w_u > 15 else w_u
            cost_v = w_v * 10 if w_v > 15 else w_v
            
            G_ROAD[u][v]['weight'] = 1.0 + ((cost_u + cost_v) / 2)
            
        try:
            dijk_path = nx.shortest_path(G_ROAD, source=source_idx, target=dest_idx, weight='weight')
        except nx.NetworkXNoPath:
            dijk_path = []

        # --- Step 3: If path changed, call OSRM for real road geometry ---
        if dijk_path and dijk_path != last_dijkstra_path:
            last_dijkstra_path = dijk_path
            # Convert to tuple of tuples so it's hashable for st.cache_data
            waypoints = tuple((CCTV_POINTS[i]["lat"], CCTV_POINTS[i]["lon"]) for i in dijk_path)
            osrm_path = get_osrm_route(waypoints)
            last_osrm_route = osrm_path if osrm_path else []

        # --- Step 4: Build layers ---
        cctv_df = pd.DataFrame(cctv_rows)

        # Mark cameras ON the Dijkstra path with a larger white ring
        dijk_ids = {CCTV_POINTS[i]["id"] for i in last_dijkstra_path}
        cctv_df["on_path"] = cctv_df.apply(
            lambda r: 18 if any(r["label"].startswith(f"{d}") for d in dijk_ids) else 12,
            axis=1
        )

        cctv_layer = pdk.Layer(
            "ScatterplotLayer",
            cctv_df,
            get_position=["lon", "lat"],
            get_fill_color="color",
            get_line_color=[255, 255, 255, 255],
            get_radius="on_path",
            stroked=True,
            line_width_min_pixels=2,
            pickable=True,
            auto_highlight=True
        )

        # White Dijkstra shortest path (via OSRM road geometry)
        route_layer_data = []
        if last_osrm_route:
            route_layer_data = [{"path": last_osrm_route, "color": [255, 255, 255, 230]}]

        path_layer = pdk.Layer(
            "PathLayer",
            route_layer_data,
            width_min_pixels=4,
            get_path="path",
            get_color="color",
            pickable=False
        )

        # Centre map on Jayadev Vihar (Row 4, Col 1 roughly middle)
        mid = CCTV_POINTS[21]  # Jayadev Vihar Square
        view_state = pdk.ViewState(
            latitude=mid["lat"],
            longitude=mid["lon"],
            zoom=12.5,
            pitch=45
        )

        map_feed.pydeck_chart(pdk.Deck(
            layers=[path_layer, cctv_layer],
            initial_view_state=view_state,
            tooltip={"text": "{label}"}
        ))

    time.sleep(0.00001)

# --- END ---
if 'stream_handler' in st.session_state:
    st.session_state.stream_handler.stop()
st.success(translate_text("Simulation Complete — Ready for Deployment Across India!", lang))