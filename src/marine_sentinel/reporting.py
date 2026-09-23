from datetime import datetime, timezone
import math

import pandas as pd

from marine_sentinel.config import EARTH_METRES_PER_DEGREE_LATITUDE, settings
from marine_sentinel.schemas import Detection, SurveyMetadata


def build_report(detections: list[Detection], metadata: SurveyMetadata) -> pd.DataFrame:
    rows = []
    longitude_scale = EARTH_METRES_PER_DEGREE_LATITUDE * max(math.cos(math.radians(metadata.latitude)), .1)
    for index, item in enumerate(detections, 1):
        latitude = metadata.latitude - (item.y + item.height / 2) * metadata.resolution_m_per_pixel / EARTH_METRES_PER_DEGREE_LATITUDE
        longitude = metadata.longitude + (item.x + item.width / 2) * metadata.resolution_m_per_pixel / longitude_scale
        rows.append({"anomaly_id": f"MS-{index:03d}", "classification": item.label,
                     "confidence_percent": round(item.confidence * 100, 1), "latitude": round(latitude, 7),
                     "longitude": round(longitude, 7), "width_m": round(item.width * metadata.resolution_m_per_pixel, 2),
                     "length_m": round(item.height * metadata.resolution_m_per_pixel, 2),
                     "priority": "HIGH" if item.confidence >= settings.priority_high_confidence else "REVIEW", "detector": item.detector,
                     "bbox_pixels": f"{item.x},{item.y},{item.width},{item.height}"})
    return pd.DataFrame(rows)


def report_payload(report: pd.DataFrame, metadata: SurveyMetadata, image_name: str, mode: str) -> dict:
    return {"generated_at": datetime.now(timezone.utc).isoformat(), "mission_id": metadata.mission_id,
            "source_image": image_name, "survey_start": metadata.__dict__, "detector_mode": mode,
            "anomalies": report.to_dict(orient="records")}
