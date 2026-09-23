from functools import lru_cache
import os
from pathlib import Path

import cv2
import numpy as np

from marine_sentinel.config import MODEL_PATH, settings
from marine_sentinel.schemas import Detection

# Keep Ultralytics' small settings file inside this project. This avoids a
# Windows permission issue in AppData and makes local launches reproducible.
_ultralytics_settings_path = MODEL_PATH.parent.parent / ".cache" / "ultralytics"
_ultralytics_settings_path.mkdir(parents=True, exist_ok=True)
_ultralytics_settings = str(_ultralytics_settings_path)
os.environ.setdefault("YOLO_CONFIG_DIR", _ultralytics_settings)
os.environ.setdefault("ULTRALYTICS_CONFIG_DIR", _ultralytics_settings)


@lru_cache(maxsize=1)
def load_yolo(weights: Path = MODEL_PATH):
    if not weights.exists():
        return None
    try:
        from ultralytics import YOLO
        return YOLO(str(weights))
    except Exception:
        return None


def _image_calibrated_threshold(detections: list[Detection]) -> float | None:
    """Separate weak and strong predictions using this image's score distribution.

    The largest natural gap in the model's ordered confidence values separates
    the strong prediction cluster from weak noise. It avoids a manually chosen
    dashboard threshold and lets each sonar image keep the number of objects
    supported by its predictions.
    """
    if not detections:
        return None
    scores = np.sort(np.asarray([item.confidence for item in detections], dtype=np.float32))[::-1]
    if len(scores) == 1:
        return float(scores[0])
    gap_index = int(np.argmax(scores[:-1] - scores[1:]))
    return float((scores[gap_index] + scores[gap_index + 1]) / 2)


def _candidate_detections(processed: np.ndarray) -> list[Detection]:
    """Generate review candidates when no trained model is installed.

    This is deliberately labelled as candidate filtering in the interface, not ML classification.
    """
    # Candidate score combines bright return, compact target shape and adjacent low-return shadow.
    # It is intentionally image-dependent and never substitutes for a trained detector.
    threshold = cv2.adaptiveThreshold(processed, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                      cv2.THRESH_BINARY, settings.candidate_adaptive_block_size,
                                      settings.candidate_adaptive_constant)
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE,
                                       (settings.candidate_kernel_size, settings.candidate_kernel_size))
    cleaned = cv2.morphologyEx(threshold, cv2.MORPH_OPEN, kernel)
    component_count, _, statistics, _ = cv2.connectedComponentsWithStats(cleaned, 8)
    image_height, image_width = processed.shape
    proposals, boxes, scores = [], [], []
    for x, y, width, height, area in statistics[1:component_count]:
        if (area < settings.candidate_min_area_pixels
                or area > image_width * image_height * settings.candidate_max_area_ratio
                or width < settings.candidate_min_dimension_pixels
                or height < settings.candidate_min_dimension_pixels):
            continue
        compactness = min(area / max(width * height, 1), 1.0)
        intensity = float(processed[y:y + height, x:x + width].mean()) / 255
        shadow_end = min(image_height, y + height * 2)
        shadow_region = processed[y:shadow_end, x:min(image_width, x + width)]
        shadow_score = 1.0 - float(shadow_region.mean()) / 255 if shadow_region.size else 0.0
        confidence = min(.95, .28 + .34 * compactness + .24 * intensity + .14 * shadow_score)
        proposals.append(Detection(int(x), int(y), int(width), int(height), "Acoustic anomaly",
                                   round(confidence, 3), "CV candidate filter"))
        boxes.append([int(x), int(y), int(width), int(height)])
        scores.append(float(confidence))
    # NMS removes overlapping proposals but does not impose a fixed target count.
    kept = cv2.dnn.NMSBoxes(boxes, scores, settings.candidate_nms_score_threshold,
                             settings.candidate_nms_iou_threshold) if boxes else []
    return sorted((proposals[int(index)] for index in np.array(kept).reshape(-1)),
                  key=lambda item: item.confidence, reverse=True)


def detect(image: np.ndarray, processed: np.ndarray) -> tuple[list[Detection], list[Detection], str, float | None]:
    """Return image-calibrated detections, raw model predictions, mode and cutoff."""
    model = load_yolo()
    if model is None:
        raw_detections = _candidate_detections(processed)
        cutoff = _image_calibrated_threshold(raw_detections)
        accepted = [item for item in raw_detections if cutoff is not None and item.confidence >= cutoff]
        return accepted, raw_detections, "Candidate filter (YOLO runtime unavailable)", cutoff

    raw_detections = []
    # The proposal floor retains meaningful model predictions; the
    # image-calibrated cutoff below decides the exported target count.
    for result in model(image, conf=settings.yolo_proposal_confidence, verbose=False):
        for box in result.boxes:
            x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())
            class_id = int(box.cls[0])
            label = result.names[class_id]
            raw_detections.append(Detection(x1, y1, x2 - x1, y2 - y1, label,
                                            round(float(box.conf[0]), 3), "YOLO"))
    cutoff = _image_calibrated_threshold(raw_detections)
    accepted = [item for item in raw_detections if cutoff is not None and item.confidence >= cutoff]
    return accepted, raw_detections, "YOLO object detector", cutoff
