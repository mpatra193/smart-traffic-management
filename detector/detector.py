# detector/detector.py
import torch
from ultralytics import YOLO
import os

# Load model ONCE (not per frame)
# Use yolov8n.pt from this directory, or fall back to download
_model_dir = os.path.dirname(os.path.abspath(__file__))
_model_candidates = [
    os.path.join(_model_dir, 'yolov8n.pt'),
    'yolov8n.pt',
    'yolov8n',  # triggers fresh download
]

model = None
for _mp in _model_candidates:
    try:
        model = YOLO(_mp)
        # Force a fuse test to catch incompatible weights early
        _ = model.model
        break
    except Exception as e:
        print(f"Could not load {_mp}: {e}")
        model = None

if model is None:
    raise RuntimeError("No compatible YOLO model found")

VEHICLE_CLASSES = [2, 3, 5, 7]  # car, motorcycle, bus, truck

# Check GPU availability
if torch.cuda.is_available():
    device = "cuda"
elif hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
    device = "mps"
else:
    device = "cpu"

print(f"Using device for YOLO: {device}")

def detect_vehicles_in_frame(frame):
    """
    Returns total vehicle count in frame.
    """
    results = model.predict(frame, verbose=False, device=device, imgsz=640)
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

    results = model.predict(frame, verbose=False, device=device, imgsz=640)
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