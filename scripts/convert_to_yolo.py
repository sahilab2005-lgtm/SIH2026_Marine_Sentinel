import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATASET = ROOT / "dataset" / "ghost_pot"
OUTPUT = ROOT / "dataset" / "yolo"

CLASS_MAP = {
    "Crab-Pot": 0,
    "Maybe-Crab-Pot": 1,
}

for split in ["train", "valid", "test"]:

    split_dir = DATASET / split

    images_out = OUTPUT / "images" / split
    labels_out = OUTPUT / "labels" / split

    images_out.mkdir(parents=True, exist_ok=True)
    labels_out.mkdir(parents=True, exist_ok=True)

    jsonl_files = list(split_dir.glob("*.jsonl"))

    if not jsonl_files:
        print(f"No JSONL file found in {split_dir}")
        continue

    jsonl_file = jsonl_files[0]

    print(f"\nProcessing {split}...")

    with open(jsonl_file, "r", encoding="utf-8") as f:

        for line in f:

            if not line.strip():
                continue

            data = json.loads(line)

            filename = data["file_name"]
            objects = data["objects"]

            image_path = split_dir / filename

            if not image_path.exists():
                print(f"WARNING: Image not found: {filename}")
                continue

            shutil.copy2(
                image_path,
                images_out / filename
            )

            yolo_lines = []

            for bbox, category in zip(
                objects["bbox"],
                objects["category"]
            ):

                if category not in CLASS_MAP:
                    continue

                class_id = CLASS_MAP[category]

                x, y, w, h = bbox

                # Convert [x, y, width, height]
                # to YOLO center format

                center_x = x + w / 2
                center_y = y + h / 2

                # Normalize for 640x640 images

                center_x /= 640
                center_y /= 640
                w /= 640
                h /= 640

                yolo_lines.append(
                    f"{class_id} "
                    f"{center_x:.6f} "
                    f"{center_y:.6f} "
                    f"{w:.6f} "
                    f"{h:.6f}"
                )

            label_file = labels_out / f"{Path(filename).stem}.txt"

            with open(label_file, "w", encoding="utf-8") as out:
                out.write("\n".join(yolo_lines))

    print(f"{split} conversion complete!")

print("\n==============================")
print("YOLO conversion completed!")
print("==============================")
