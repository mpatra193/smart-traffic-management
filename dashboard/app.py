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
import importlib
import detector.detector
importlib.reload(detector.detector)
from detector.detector import detect_vehicles_in_frame, detect_vehicles_by_zone
import pandas as pd
import pydeck as pdk
import requests
import polyline

# --- PAGE CONFIG ---
st.set_page_config(page_title="🚦 Traffic Route Optimizer", layout="wide")
st.title("🚦 Traffic Route Optimizer")

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
    Dijkstra's shortest path.
    graph   : dict {node_id: [neighbor_id, ...]}
    weights : dict {node_id: congestion_score}  (higher = more congested)
    Edge cost = avg congestion of the two endpoints.
    Returns ordered list of node IDs on the shortest path.
    """
    dist = {n: float('inf') for n in graph}
    prev = {n: None for n in graph}
    dist[source] = 0
    heap = [(0, source)]

    while heap:
        d, u = heapq.heappop(heap)
        if d > dist[u]:
            continue
        if u == target:
            break
        for v in graph[u]:
            edge_cost = (weights.get(u, 1) + weights.get(v, 1)) / 2
            nd = dist[u] + edge_cost
            if nd < dist[v]:
                dist[v] = nd
                prev[v] = u
                heapq.heappush(heap, (nd, v))

    # Reconstruct path
    path, node = [], target
    while node is not None:
        path.append(node)
        node = prev[node]
    path.reverse()
    return path if path[0] == source else []

# ─── 25 CCTV cameras forming a dense grid in Bandra, Mumbai ───────────────
CCTV_POINTS = [
    # Area 1: SV Road North (Intersection video)
    {"id": "CAM-01", "name": "SV Road & Station Rd",          "lat": 19.0540, "lon": 72.8376, "video": "intersection.mp4", "type": "2-way"},
    {"id": "CAM-02", "name": "SV Road & Hill Road",           "lat": 19.0572, "lon": 72.8361, "video": "intersection.mp4", "type": "2-way"},
    {"id": "CAM-03", "name": "SV Road & Linking Road",        "lat": 19.0604, "lon": 72.8347, "video": "intersection.mp4", "type": "2-way"},
    {"id": "CAM-04", "name": "SV Road & Perry Cross Road",    "lat": 19.0636, "lon": 72.8368, "video": "intersection.mp4", "type": "2-way"},
    {"id": "CAM-05", "name": "SV Road & Mount Mary Steps",    "lat": 19.0661, "lon": 72.8382, "video": "intersection.mp4", "type": "2-way"},
    
    # Area 2: Linking Road (Singapore video - 4-way)
    {"id": "CAM-06", "name": "Linking Road & Waterfield Road","lat": 19.0610, "lon": 72.8305, "video": "vecteezy_time-lapse-of-singapore-city_3397592.mov", "type": "4-way"},
    {"id": "CAM-07", "name": "Linking Road & 33rd Road",      "lat": 19.0650, "lon": 72.8340, "video": "vecteezy_time-lapse-of-singapore-city_3397592.mov", "type": "4-way"},
    {"id": "CAM-08", "name": "Linking Road & 14th Road",      "lat": 19.0680, "lon": 72.8335, "video": "vecteezy_time-lapse-of-singapore-city_3397592.mov", "type": "4-way"},
    {"id": "CAM-09", "name": "Linking Road & Main Avenue",    "lat": 19.0710, "lon": 72.8340, "video": "vecteezy_time-lapse-of-singapore-city_3397592.mov", "type": "4-way"},
    {"id": "CAM-10", "name": "Linking Road & Santa Cruz N",   "lat": 19.0740, "lon": 72.8350, "video": "vecteezy_time-lapse-of-singapore-city_3397592.mov", "type": "4-way"},

    # Area 3: Hill Road & Turner (Vietnam video - 2-way dense)
    {"id": "CAM-11", "name": "Hill Road & St Andrews Road",   "lat": 19.0558, "lon": 72.8291, "video": "vecteezy_ho-chi-minh-city-traffic-at-intersection-vietnam_1793410.mov", "type": "2-way"},
    {"id": "CAM-12", "name": "Turner Road & Hill Road",       "lat": 19.0542, "lon": 72.8258, "video": "vecteezy_ho-chi-minh-city-traffic-at-intersection-vietnam_1793410.mov", "type": "2-way"},
    {"id": "CAM-13", "name": "Waterfield Road & Turner Road", "lat": 19.0570, "lon": 72.8310, "video": "vecteezy_ho-chi-minh-city-traffic-at-intersection-vietnam_1793410.mov", "type": "2-way"},
    {"id": "CAM-14", "name": "Ambedkar Road & Pali Naka",     "lat": 19.0625, "lon": 72.8290, "video": "vecteezy_ho-chi-minh-city-traffic-at-intersection-vietnam_1793410.mov", "type": "2-way"},
    {"id": "CAM-15", "name": "Pali Hill & Perry Cross Road",  "lat": 19.0651, "lon": 72.8315, "video": "vecteezy_ho-chi-minh-city-traffic-at-intersection-vietnam_1793410.mov", "type": "2-way"},
    
    # Area 4: Carter Road (Singapore video - 4-way)
    {"id": "CAM-16", "name": "Carter Road & Chapel Road",     "lat": 19.0648, "lon": 72.8257, "video": "vecteezy_time-lapse-of-singapore-city_3397592.mov", "type": "4-way"},
    {"id": "CAM-17", "name": "Carter Road & Union Park",      "lat": 19.0700, "lon": 72.8250, "video": "vecteezy_time-lapse-of-singapore-city_3397592.mov", "type": "4-way"},
    {"id": "CAM-18", "name": "Carter Road & Joggers Park",    "lat": 19.0730, "lon": 72.8260, "video": "vecteezy_time-lapse-of-singapore-city_3397592.mov", "type": "4-way"},
    {"id": "CAM-19", "name": "Carter Road & Rizvi College",   "lat": 19.0760, "lon": 72.8270, "video": "vecteezy_time-lapse-of-singapore-city_3397592.mov", "type": "4-way"},
    {"id": "CAM-20", "name": "Carter Road & Khar Danda",      "lat": 19.0790, "lon": 72.8280, "video": "vecteezy_time-lapse-of-singapore-city_3397592.mov", "type": "4-way"},

    # Area 5: Highway / Major Junctions (Vietnam video - 2-way dense)
    {"id": "CAM-21", "name": "WEH & Bandra East",             "lat": 19.0550, "lon": 72.8450, "video": "vecteezy_ho-chi-minh-city-traffic-at-intersection-vietnam_1793410.mov", "type": "2-way"},
    {"id": "CAM-22", "name": "WEH & Kalanagar Junction",      "lat": 19.0580, "lon": 72.8470, "video": "vecteezy_ho-chi-minh-city-traffic-at-intersection-vietnam_1793410.mov", "type": "2-way"},
    {"id": "CAM-23", "name": "WEH & BKC Connector",           "lat": 19.0620, "lon": 72.8490, "video": "vecteezy_ho-chi-minh-city-traffic-at-intersection-vietnam_1793410.mov", "type": "2-way"},
    {"id": "CAM-24", "name": "WEH & Vakola Flyover",          "lat": 19.0680, "lon": 72.8520, "video": "vecteezy_ho-chi-minh-city-traffic-at-intersection-vietnam_1793410.mov", "type": "2-way"},
    {"id": "CAM-25", "name": "WEH & Santa Cruz Airport",      "lat": 19.0750, "lon": 72.8550, "video": "vecteezy_ho-chi-minh-city-traffic-at-intersection-vietnam_1793410.mov", "type": "2-way"},
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

# --- ROUTING & CAMERA CONTROLS ---
st.sidebar.markdown("---")
cam_names = [cam["name"] for cam in CCTV_POINTS]
active_cam_name = st.sidebar.selectbox("🎥 View Live Feed From:", cam_names, index=5)
st.sidebar.markdown("---")
st.sidebar.subheader("🚑 Emergency Routing")
source_cam_name = st.sidebar.selectbox("From (Source)", cam_names, index=0)
dest_cam_name = st.sidebar.selectbox("To (Destination)", cam_names, index=24)

active_cam_idx = cam_names.index(active_cam_name)
active_cam = CCTV_POINTS[active_cam_idx]
source_idx = cam_names.index(source_cam_name)
dest_idx = cam_names.index(dest_cam_name)

# --- VIDEO SETUP ---
video_path = os.path.join(os.path.dirname(__file__), "..", "data", active_cam["video"])
cap = cv2.VideoCapture(video_path)

if not cap.isOpened():
    st.error("❌ Could not open video/webcam. Check path or connection.")
    st.stop()

# --- LOGGING SETUP ---
LOG_FILE = os.path.join(os.path.dirname(__file__), "..", "data", "traffic_log.jsonl")
os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)

# --- DASHBOARD PLACEHOLDERS SETUP ---
st.markdown("---")
col1, col2, col3 = st.columns([1, 1.5, 1.5])

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

with col3:
    st.subheader(translate_text("🗺️ Mumbai Intersection", lang))
    map_feed = st.empty()

frame_skip = 5
frame_count = 0
last_map_state = None
last_dijkstra_path = []
last_osrm_route = []

# --- Initialize City Traffic State ---
# This gives each camera its own independent traffic level that drifts over time
city_traffic = [{"ns": random.randint(2, 12), "ew": random.randint(2, 12)} for _ in range(25)]

# --- MAIN LOOP ---
while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

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

    annotated_rgb = cv2.cvtColor(annotated_frame, cv2.COLOR_BGR2RGB)
    video_feed.image(annotated_rgb, width='stretch')

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
                status = f"🔴 Heavy Traffic ({score} vehicles)"
            elif score > 8:
                color = [255, 200, 40, 240]  # Yellow
                status = f"🟡 Moderate Traffic ({score} vehicles)"
            else:
                color = [40, 200, 40, 240]   # Green
                status = f"🟢 Clear Traffic ({score} vehicles)"

            cctv_rows.append({
                "lat": cam["lat"], "lon": cam["lon"],
                "color": color, "radius": 12,
                "label": f"📹 {cam['id']} — {cam['name']}\n{status}"
            })

        # --- Step 2: Dijkstra — least-congested path from user-selected Source to Destination ---
        dijk_path = dijkstra(ROAD_GRAPH, cam_scores, source=source_idx, target=dest_idx)

        # --- Step 3: If path changed, call OSRM for real road geometry ---
        if dijk_path and dijk_path != last_dijkstra_path:
            last_dijkstra_path = dijk_path
            waypoints = [(CCTV_POINTS[i]["lat"], CCTV_POINTS[i]["lon"]) for i in dijk_path]
            osrm_path = get_osrm_route(waypoints)
            last_osrm_route = osrm_path if osrm_path else []

        # --- Step 4: Build layers ---
        cctv_df = pd.DataFrame(cctv_rows)

        # Mark cameras ON the Dijkstra path with a larger white ring
        dijk_ids = {CCTV_POINTS[i]["id"] for i in last_dijkstra_path}
        cctv_df["on_path"] = cctv_df.apply(
            lambda r: 18 if any(r["label"].startswith(f"📹 {d}") for d in dijk_ids) else 12,
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

        # Centre map between all cameras
        mid = CCTV_POINTS[4]  # Hill Road camera ~ geographic center
        view_state = pdk.ViewState(
            latitude=mid["lat"],
            longitude=mid["lon"],
            zoom=14.2,
            pitch=40
        )

        map_feed.pydeck_chart(pdk.Deck(
            layers=[path_layer, cctv_layer],
            initial_view_state=view_state,
            tooltip={"text": "{label}"}
        ))

    time.sleep(0.00001)

# --- END ---
cap.release()
st.success(translate_text("✅ Simulation Complete — Ready for Deployment Across India!", lang))