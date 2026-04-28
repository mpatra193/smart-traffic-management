# mock_data/simulator.py
import random
import time

def is_emergency_vehicle():
    """Disabled emergency vehicle simulation"""
    return False

def get_mock_gps():
    """Fake GPS near Chennai"""
    return {
        "lat": 13.0827 + random.uniform(-0.003, 0.003),
        "lng": 80.2707 + random.uniform(-0.003, 0.003),
        "vehicle_id": f"AMB-{random.randint(1000, 9999)}",
        "speed_kmph": random.randint(40, 60),
        "timestamp": time.strftime("%H:%M:%S")
    }