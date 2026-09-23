import glob
import json
from collections import Counter

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "dataset" / "ghost_pot"

counter = Counter()
jsonl_count = 0

for jsonl_path in glob.glob(
    str(BASE / "**" / "*.jsonl"),
    recursive=True
):

    jsonl_count += 1

    print("Reading:", jsonl_path)

    with open(jsonl_path, "r", encoding="utf-8") as f:

        for line in f:

            line = line.strip()

            if not line:
                continue

            data = json.loads(line)

            objects = data.get("objects", {})

            categories = objects.get("category", [])

            for category in categories:
                counter[category] += 1


print("\n" + "=" * 50)
print("ORIGINAL DATASET CLASS CHECK")
print("=" * 50)

print("JSONL files found:", jsonl_count)

for category, count in counter.items():
    print(f"{category}: {count}")

print("=" * 50)
