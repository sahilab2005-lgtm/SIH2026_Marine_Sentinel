"""Command-line inference for a sonar image; writes an annotated image and JSON detections."""
import argparse
import json
from pathlib import Path

from ultralytics import YOLO

ROOT = Path(__file__).resolve().parents[1]

parser = argparse.ArgumentParser(description="Run Marine Sentinel YOLO inference")
parser.add_argument("image", help="Path to a side-scan sonar image")
parser.add_argument("--weights", default=str(ROOT / "models" / "best.pt"))
parser.add_argument("--confidence", type=float, default=0.55)
args = parser.parse_args()

model = YOLO(args.weights)
result = model(args.image, conf=args.confidence, save=True)[0]
items = []
for box in result.boxes:
    x1, y1, x2, y2 = [round(value, 1) for value in box.xyxy[0].tolist()]
    cls = int(box.cls[0])
    items.append({"class": result.names[cls], "confidence": round(float(box.conf[0]), 4),
                  "bbox_xyxy_pixels": [x1, y1, x2, y2]})
output = ROOT / "results" / "latest_detections.json"
output.parent.mkdir(exist_ok=True)
output.write_text(json.dumps(items, indent=2), encoding="utf-8")
print(f"{len(items)} detections saved to {output}")
