"""Train the Marine Sentinel YOLO detector on the included labeled sonar dataset."""
from pathlib import Path

from ultralytics import YOLO

ROOT = Path(__file__).resolve().parents[1]

if __name__ == "__main__":
    model = YOLO("yolo11n.pt")
    model.train(
        data=str(ROOT / "config" / "dataset.yaml"),
        epochs=10,
        imgsz=640,
        batch=8,
        patience=20,
        optimizer="auto",
        cos_lr=True,
        degrees=8,
        translate=.08,
        scale=.30,
        fliplr=True,
        mosaic=.30,
        mixup=.05,
        seed=42,
        project=str(ROOT / "results"),
        name="marine_sentinel_yolo",
    )
    print("Training complete. Copy results/marine_sentinel_yolo/weights/best.pt to models/best.pt")
