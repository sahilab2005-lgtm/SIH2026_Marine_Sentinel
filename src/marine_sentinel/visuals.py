import cv2
import numpy as np

from marine_sentinel.schemas import Detection


def draw_overlay(processed: np.ndarray, detections: list[Detection]) -> np.ndarray:
    canvas = cv2.cvtColor(processed, cv2.COLOR_GRAY2RGB)
    for index, item in enumerate(detections, 1):
        cv2.rectangle(canvas, (item.x, item.y), (item.x + item.width, item.y + item.height), (255, 52, 52), 2)
        label = f"A-{index:02d} {item.label} {item.confidence:.0%}"
        cv2.rectangle(canvas, (item.x, max(0, item.y - 23)),
                      (min(canvas.shape[1], item.x + max(170, len(label) * 8)), item.y), (120, 25, 25), -1)
        cv2.putText(canvas, label, (item.x + 3, max(15, item.y - 7)), cv2.FONT_HERSHEY_SIMPLEX,
                    .45, (255, 255, 255), 1, cv2.LINE_AA)
    return canvas
