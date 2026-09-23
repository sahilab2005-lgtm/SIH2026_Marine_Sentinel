"""Evaluate trained Marine Sentinel weights only on the held-out YOLO test split."""
from pathlib import Path

from ultralytics import YOLO

ROOT = Path(__file__).resolve().parents[1]
weights = ROOT / "models" / "best.pt"
if not weights.exists():
    raise FileNotFoundError("Train first, then copy weights to models/best.pt")

model = YOLO(str(weights))
metrics = model.val(data=str(ROOT / "config" / "dataset.yaml"), split="test", imgsz=640, conf=.25)
print(f"Test mAP50: {metrics.box.map50:.3f}")
print(f"Test mAP50-95: {metrics.box.map:.3f}")
