# detector/detector.py
import torch
from ultralytics import YOLO

# Load model ONCE (not per frame)
model = YOLO('yolo11n.pt')  # or yolov8s.pt / yolo11s.pt for better accuracy
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

def detect_vehicles_by_zone(frame, crossing_type="2-way"):
    """
    Returns (counts_dict, annotated_frame).
    counts_dict: {'left': count, 'right': count} (maps to NS/EW in app)
    annotated_frame: Image with YOLO bounding boxes drawn.
    """
    h, w = frame.shape[:2]
    counts = {"left": 0, "right": 0}

    results = model(frame, verbose=False, device=device)
    annotated_frame = results[0].plot()  # Draw YOLO bounding boxes!

    for result in results:
        for box, cls in zip(result.boxes.xyxy, result.boxes.cls):
            if int(cls) not in VEHICLE_CLASSES:
                continue
            x1, y1, x2, y2 = map(int, box)
            cx = (x1 + x2) // 2  # center x
            cy = (y1 + y2) // 2  # center y

            if crossing_type == "4-way":
                # Divide by diagonals: if closer to vertical axis -> NS ('left'), else EW ('right')
                # Scaled by aspect ratio
                if abs(cx - w/2) / w < abs(cy - h/2) / h:
                    counts["left"] += 1  # Top/Bottom (North-South)
                else:
                    counts["right"] += 1  # Left/Right (East-West)
            else:
                # Standard 2-way (Left vs Right)
                if cx < w // 2:
                    counts["left"] += 1
                else:
                    counts["right"] += 1

    return counts, annotated_frame