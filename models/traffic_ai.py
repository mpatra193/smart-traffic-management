# models/traffic_ai.py

def get_signal_timing(ns_count, ew_count, is_emergency=False):
    """
    India-Trained Logic: Adjusts signal timing based on North-South vs East-West flow.
    ns_count = left + right lanes (vertical flow)
    ew_count = center lane (horizontal flow)
    """
    if is_emergency:
        return {
            "green_ns": 60,
            "green_ew": 10,
            "mode": "🚑 EMERGENCY OVERRIDE",
            "wait_saved": 45
        }
    
    total = ns_count + ew_count
    if total == 0:
        return {
            "green_ns": 25,
            "green_ew": 35,
            "mode": "🌿 LIGHT TRAFFIC",
            "wait_saved": 5
        }

    ratio = ns_count / (ew_count + 1)  # avoid div by zero

    if ratio > 2.0:
        return {
            "green_ns": 50,
            "green_ew": 15,
            "mode": "🚦 NS HEAVY FLOW",
            "wait_saved": 25
        }
    elif ratio > 1.2:
        return {
            "green_ns": 40,
            "green_ew": 25,
            "mode": "🚗 NS MODERATE",
            "wait_saved": 15
        }
    elif ratio < 0.5:
        return {
            "green_ns": 15,
            "green_ew": 50,
            "mode": "🚦 EW HEAVY FLOW",
            "wait_saved": 25
        }
    else:
        return {
            "green_ns": 30,
            "green_ew": 30,
            "mode": "🌿 BALANCED FLOW",
            "wait_saved": 10
        }