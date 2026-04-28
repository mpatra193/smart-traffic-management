# detector/detector.py
import torch
from ultralytics import YOLO

# Load model ONCE (not per frame)
model = YOLO('yolov8n.pt')  # or yolov8s.pt for better accuracy
VEHICLE_CLASSES = [2, 3, 5, 7]  # car, motorcycle, bus, truck

# Check GPU availability
device = "cpu"
print(f"Using device: {device}")
model.to(device)

def detect_vehicles_in_frame(frame):
    """
    Returns total vehicle count in frame.
    """
    results = model(frame, verbose=False, device=device)
    count = 0
    for result in results:
        for cls in result.boxes.cls:
            if int(cls) in VEHICLE_CLASSES:
                count += 1
    return count

def detect_vehicles_by_zone(frame):
    """
    Returns dict: {'left': count, 'right': count}
    Divides frame into 2 vertical lanes.
    """
    h, w = frame.shape[:2]
    zones = {
        "left": (0, w // 2),
        "right": (w // 2, w)
    }
    counts = {"left": 0, "right": 0}

    results = model(frame, verbose=False, device=device)
    for result in results:
        for box, cls in zip(result.boxes.xyxy, result.boxes.cls):
            if int(cls) not in VEHICLE_CLASSES:
                continue
            x1, y1, x2, y2 = map(int, box)
            cx = (x1 + x2) // 2  # center x
            for zone, (start, end) in zones.items():
                if start <= cx < end:
                    counts[zone] += 1
                    break
    return counts