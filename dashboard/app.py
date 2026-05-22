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

from detector.detector import detect_vehicles_in_frame, detect_vehicles_by_zone

import utils.stream_handler
importlib.reload(utils.stream_handler)
from utils.stream_handler import StreamHandler
import pandas as pd
import pydeck as pdk
import requests
import polyline

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
import math

# ─── ROUTING CONSTANTS ──────────────────────────────────────────────────────────
AVERAGE_SPEED_KPH = 60.0          # assumed avg vehicle speed
CCTV_PROXIMITY_KM = 0.5           # how close a CCTV must be to "see" a route
WAIT_PER_VEHICLE_SEC = 2.5        # estimated wait per queued vehicle at intersection

def haversine_km(lat1, lon1, lat2, lon2):
    """Great-circle distance between two lat/lon points in km."""
    R = 6371.0
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (math.sin(dlat / 2) ** 2 +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
         math.sin(dlon / 2) ** 2)
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

@st.cache_data(show_spinner=False, ttl=3600)
def get_osrm_alternatives(src_lat, src_lon, dst_lat, dst_lon):
    """Ask OSRM for up to 3 real-road alternative routes.
    Routes follow ACTUAL roads — no dependency on our camera graph.
    """
    url = (
        f"http://router.project-osrm.org/route/v1/driving/"
        f"{src_lon},{src_lat};{dst_lon},{dst_lat}"
        f"?overview=full&geometries=polyline&alternatives=3"
    )
    try:
        r = requests.get(url, timeout=10)
        data = r.json()
        if data.get('code') != 'Ok':
            return []
        results = []
        for route in data['routes']:
            decoded = polyline.decode(route['geometry'])
            results.append({
                "geometry": [[p[1], p[0]] for p in decoded],  # [lon,lat] for PyDeck
                "coords": decoded,                              # [(lat,lon)] for matching
                "distance_km": route['distance'] / 1000.0,
                "duration_min": route['duration'] / 60.0,
            })
        return results
    except Exception:
        return []

def find_nearby_cctvs(route_coords, cctv_points, radius_km=CCTV_PROXIMITY_KM):
    """Find which CCTVs sit within radius_km of any point on the route.
    Samples every 5th polyline point for speed.
    """
    nearby = set()
    sampled = route_coords[::5] if len(route_coords) > 10 else route_coords
    for ci, cam in enumerate(cctv_points):
        clat, clon = cam["lat"], cam["lon"]
        for rlat, rlon in sampled:
            if haversine_km(rlat, rlon, clat, clon) <= radius_km:
                nearby.add(ci)
                break
    return sorted(nearby)

def estimate_route_time(route_distance_km, nearby_cctv_indices, cam_scores):
    """Total estimated travel time in minutes.
    = drive_time (distance ÷ 60 kph) + wait times at congested CCTV intersections.
    """
    drive_time_min = (route_distance_km / AVERAGE_SPEED_KPH) * 60.0
    total_wait_sec = 0.0
    for ci in nearby_cctv_indices:
        vehicles = cam_scores.get(ci, 0)
        total_wait_sec += vehicles * WAIT_PER_VEHICLE_SEC
    total_wait_min = total_wait_sec / 60.0
    return drive_time_min + total_wait_min, drive_time_min, total_wait_min

# ─── 75 CCTV cameras covering all crossings within 100km ───────────────────────
from data.camera_network import CCTV_POINTS

# --- ROUTING & CAMERA CONTROLS ---
st.sidebar.markdown("---")
cam_names = [cam["name"] for cam in CCTV_POINTS]
active_cam_name = st.sidebar.selectbox("View Live Feed From:", cam_names, index=5)
st.sidebar.markdown("---")
st.sidebar.subheader("Route Planning")
source_cam_name = st.sidebar.selectbox("From (Source)", cam_names, index=0)
dest_cam_name = st.sidebar.selectbox("To (Destination)", cam_names, index=min(24, len(cam_names)-1))

st.sidebar.markdown("---")
st.sidebar.subheader("Stream Source (Tier 1)")
custom_url = st.sidebar.text_input("Custom Stream URL (RTSP/YouTube)", value="", help="Leave blank to use public defaults / offline video")
stream_status = st.sidebar.empty()

active_cam_idx = cam_names.index(active_cam_name)
active_cam = CCTV_POINTS[active_cam_idx]
source_idx = cam_names.index(source_cam_name)
dest_idx = cam_names.index(dest_cam_name)

# --- MANUAL TRAFFIC OVERRIDE (collapsible sidebar section) ---
st.sidebar.markdown("---")
with st.sidebar.expander("🚦 Manual Traffic Control", expanded=False):
    st.caption("Override congestion at any crossing. Set to 0 to use auto-simulation.")

    # Global multiplier for quick adjustment
    global_boost = st.slider("Global traffic multiplier", 0.0, 3.0, 1.0, 0.1,
                             help="Multiply ALL crossing traffic by this factor")

    # Persist overrides across reruns
    if 'traffic_overrides' not in st.session_state:
        st.session_state.traffic_overrides = {}

    # Group cameras by zone prefix for cleaner UI
    zone_labels = {
        "BBS": "🏙️ Bhubaneswar",
        "NH16": "🛣️ NH16 (BBS→CTC)",
        "CTC": "🏛️ Cuttack",
        "SOU": "⬇️ Khordha/Jatni",
        "NH316": "🛤️ NH316 (BBS→Puri)",
        "PURI": "🕌 Puri",
        "KNK": "☀️ Konark",
    }

    for prefix, label in zone_labels.items():
        zone_cams = [(i, c) for i, c in enumerate(CCTV_POINTS) if c["id"].startswith(prefix)]
        if not zone_cams:
            continue
        st.markdown(f"**{label}**")
        for i, cam in zone_cams:
            key = f"tov_{i}"
            default = st.session_state.traffic_overrides.get(i, 0)
            val = st.slider(
                cam['name'], 0, 60, default, 1, key=key,
                help=f"Total vehicles at {cam['name']}. 0 = auto."
            )
            st.session_state.traffic_overrides[i] = val

# Retrieve overrides and global boost for use in main loop
traffic_overrides = st.session_state.get('traffic_overrides', {})
if 'global_boost' not in dir():
    global_boost = 1.0

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
    st.subheader(translate_text("Odisha 100km Network & Routing", lang))
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
last_scored_routes = []  # cached OSRM routes with time estimates

# --- Initialize City Traffic State ---
city_traffic = [{"ns": random.randint(0, 20), "ew": random.randint(0, 20)} for _ in range(len(CCTV_POINTS))]

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

    # ═══════════════════════════════════════════════════════════════════════════
    # 🗺️ UPDATE MAP — OSRM routing + live CCTV-based re-ranking every frame
    # ═══════════════════════════════════════════════════════════════════════════

    # --- Step 1: ALWAYS update per-camera congestion scores (they drift) ---
    cam_scores = {}
    cctv_rows = []

    for i, cam in enumerate(CCTV_POINTS):
        override = traffic_overrides.get(i, 0)
        if override > 0:
            cam_ns = override // 2
            cam_ew = override - cam_ns
        elif i == active_cam_idx:
            cam_ns = ns_count
            cam_ew = ew_count
        else:
            city_traffic[i]["ns"] = max(0, min(30, city_traffic[i]["ns"] + random.choice([-3, -2, -1, 0, 0, 1, 2, 3])))
            city_traffic[i]["ew"] = max(0, min(30, city_traffic[i]["ew"] + random.choice([-3, -2, -1, 0, 0, 1, 2, 3])))
            cam_ns = city_traffic[i]["ns"]
            cam_ew = city_traffic[i]["ew"]

        score = int((cam_ns + cam_ew) * global_boost)
        cam_scores[i] = max(score, 0.1)

        if score > 15:
            color = [220, 40, 40, 240]
            status = f"Heavy ({score} veh) ~{score * WAIT_PER_VEHICLE_SEC:.0f}s wait"
        elif score > 8:
            color = [255, 200, 40, 240]
            status = f"Moderate ({score} veh) ~{score * WAIT_PER_VEHICLE_SEC:.0f}s wait"
        else:
            color = [40, 200, 40, 240]
            status = f"Clear ({score} veh)"

        cctv_rows.append({
            "lat": cam["lat"], "lon": cam["lon"],
            "color": color, "radius": 12,
            "name": f"{cam['id']} — {cam['name']}\n{status}"
        })

    # --- Step 2: Fetch OSRM routes ONLY when source/dest changes (expensive) ---
    route_key = f"{source_idx}_{dest_idx}"
    if route_key != last_map_state:
        last_map_state = route_key
        src = CCTV_POINTS[source_idx]
        dst = CCTV_POINTS[dest_idx]
        cached_osrm = get_osrm_alternatives(src["lat"], src["lon"], dst["lat"], dst["lon"])
        # Pre-compute nearby CCTVs per route (geometry doesn't change)
        cached_nearby = []
        for route in cached_osrm:
            cached_nearby.append(find_nearby_cctvs(route["coords"], CCTV_POINTS))
        st.session_state['cached_osrm'] = cached_osrm
        st.session_state['cached_nearby'] = cached_nearby

    osrm_routes = st.session_state.get('cached_osrm', [])
    nearby_per_route = st.session_state.get('cached_nearby', [])

    # --- Step 3: ALWAYS re-score routes against CURRENT congestion ---
    scored_routes = []
    for idx, route in enumerate(osrm_routes):
        nearby = nearby_per_route[idx] if idx < len(nearby_per_route) else []
        total_min, drive_min, wait_min = estimate_route_time(
            route["distance_km"], nearby, cam_scores
        )
        scored_routes.append({
            "geometry": route["geometry"],
            "distance_km": route["distance_km"],
            "total_min": total_min,
            "drive_min": drive_min,
            "wait_min": wait_min,
            "num_cctvs": len(nearby),
            "nearby_cctvs": nearby,
        })

    # Sort by total estimated time — best route first
    scored_routes.sort(key=lambda r: r["total_min"])

    # --- Step 4: Build map layers ---
    cctv_df = pd.DataFrame(cctv_rows)

    all_route_cctvs = set()
    for sr in scored_routes:
        all_route_cctvs.update(sr["nearby_cctvs"])
    on_route_ids = {CCTV_POINTS[ci]["id"] for ci in all_route_cctvs}
    cctv_df["on_path"] = cctv_df.apply(
        lambda r: 18 if any(r["name"].startswith(d) for d in on_route_ids) else 12,
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

    # Color-coded routes: best=green, 2nd=yellow, 3rd=orange
    route_colors = [
        [0, 230, 118, 240],
        [255, 214, 10, 200],
        [255, 145, 77, 180],
    ]
    route_widths = [5, 3, 2]
    route_layer_data = []
    for idx, sr in enumerate(scored_routes):
        rank = "⭐ FASTEST" if idx == 0 else f"Alt {idx}"
        label = (
            f"{rank} | {sr['distance_km']:.1f}km | "
            f"Drive {sr['drive_min']:.1f}min + "
            f"Wait {sr['wait_min']:.1f}min = "
            f"TOTAL {sr['total_min']:.1f}min | "
            f"{sr['num_cctvs']} CCTVs"
        )
        route_layer_data.append({
            "path": sr["geometry"],
            "color": route_colors[idx % len(route_colors)],
            "width": route_widths[idx % len(route_widths)],
            "name": label,
        })

    path_layer = pdk.Layer(
        "PathLayer",
        route_layer_data,
        width_min_pixels=2,
        get_width="width",
        width_scale=1,
        get_path="path",
        get_color="color",
        pickable=True
    )

    # Centre map on midpoint between source and destination
    src = CCTV_POINTS[source_idx]
    dst = CCTV_POINTS[dest_idx]
    mid_lat = (src["lat"] + dst["lat"]) / 2
    mid_lon = (src["lon"] + dst["lon"]) / 2
    span = haversine_km(src["lat"], src["lon"], dst["lat"], dst["lon"])
    if span > 80:
        zoom = 9.0
    elif span > 40:
        zoom = 9.5
    elif span > 15:
        zoom = 10.5
    elif span > 5:
        zoom = 11.5
    else:
        zoom = 12.5

    view_state = pdk.ViewState(
        latitude=mid_lat, longitude=mid_lon,
        zoom=zoom, pitch=40
    )

    map_feed.pydeck_chart(pdk.Deck(
        layers=[path_layer, cctv_layer],
        initial_view_state=view_state,
        tooltip={"text": "{name}"}
    ))

    time.sleep(0.00001)

# --- END ---
if 'stream_handler' in st.session_state:
    st.session_state.stream_handler.stop()
st.success(translate_text("Simulation Complete — Ready for Deployment Across India!", lang))