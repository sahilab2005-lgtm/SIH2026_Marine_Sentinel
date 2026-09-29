"""HTTP API for side-scan sonar analysis and geotagged anomaly reporting."""
from __future__ import annotations

import base64
import csv
import json
import uuid
from io import BytesIO, StringIO
from typing import Literal

import cv2
import numpy as np
import pandas as pd
from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.responses import Response
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image, UnidentifiedImageError
from pydantic import BaseModel

from marine_sentinel.config import MODEL_PATH, settings
from marine_sentinel.detector import detect, load_yolo
from marine_sentinel.processing import prepare_sonar, quality_metrics
from marine_sentinel.reporting import build_report, report_payload
from marine_sentinel.schemas import SurveyMetadata
from marine_sentinel.visuals import draw_overlay

app = FastAPI(
    title="Marine Sentinel API",
    version="1.0.0",
    description="Local inference and anomaly reporting for side-scan sonar imagery.",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=list(settings.api_allowed_origins),
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

# Prototype session store. Reviews remain available for the life of this API process.
_analyses: dict[str, dict] = {}


class ReviewRequest(BaseModel):
    anomaly_id: str
    decision: Literal["Verified", "Rejected"]


def _png_base64(image: np.ndarray) -> str:
    """Encode an OpenCV/NumPy image as a JSON-safe PNG data payload."""
    if image.ndim == 3:
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
    success, encoded = cv2.imencode(".png", image)
    if not success:
        raise RuntimeError("Could not encode processed sonar image.")
    return base64.b64encode(encoded.tobytes()).decode("ascii")


@app.get("/health")
def health() -> dict:
    """Return a lightweight readiness check without running inference."""
    yolo_ready = load_yolo() is not None
    return {
        "status": "ok",
        "model_weights_present": MODEL_PATH.exists(),
        "yolo_ready": yolo_ready,
        "inference_mode": "YOLO" if yolo_ready else "candidate_filter",
    }


@app.post("/api/v1/analyze")
async def analyze_sonar(
    image: UploadFile = File(..., description="Side-scan sonar image: PNG, JPG, JPEG, or TIFF."),
    mission_id: str = Form(settings.default_mission_id),
    latitude: float = Form(...),
    longitude: float = Form(...),
    resolution_m_per_pixel: float = Form(..., gt=0),
) -> dict:
    """Run the full processing, detection, geotagging, and reporting pipeline."""
    if image.content_type not in {"image/png", "image/jpeg", "image/tiff", "image/jpg"}:
        raise HTTPException(status_code=415, detail="Upload a PNG, JPG, JPEG, or TIFF sonar image.")
    payload = await image.read()
    if not payload:
        raise HTTPException(status_code=400, detail="The uploaded image is empty.")
    if len(payload) > settings.api_max_upload_bytes:
        raise HTTPException(status_code=413, detail="Image exceeds the configured local API upload limit.")

    try:
        source = np.array(Image.open(BytesIO(payload)).convert("RGB"))
    except (UnidentifiedImageError, OSError) as error:
        raise HTTPException(status_code=400, detail="The uploaded file is not a readable image.") from error

    metadata = SurveyMetadata(latitude, longitude, resolution_m_per_pixel, mission_id.strip() or settings.default_mission_id)
    processed = prepare_sonar(source)
    detections, raw_detections, mode, threshold = detect(source, processed)
    report = build_report(detections, metadata)
    analysis_id = uuid.uuid4().hex
    records = report.to_dict(orient="records")
    _analyses[analysis_id] = {
        "source_image": image.filename or "sonar_image",
        "mode": mode,
        "metadata": metadata,
        "report": records,
        "reviews": {row["anomaly_id"]: "Pending" for row in records},
    }

    return {
        "analysis_id": analysis_id,
        "source_image": image.filename or "sonar_image",
        "detector_mode": mode,
        "auto_threshold": threshold,
        "detected_target_count": len(detections),
        "raw_proposal_count": len(raw_detections),
        "diagnostics": quality_metrics(processed),
        "report": report.to_dict(orient="records"),
        "report_payload": report_payload(report, metadata, image.filename or "sonar_image", mode),
        "processed_image_png_base64": _png_base64(processed),
        "overlay_image_png_base64": _png_base64(draw_overlay(processed, detections)),
    }


@app.post("/api/v1/analyses/{analysis_id}/review")
def review_detection(analysis_id: str, review: ReviewRequest) -> dict:
    """Record an operator's verification decision for a detected anomaly."""
    analysis = _analyses.get(analysis_id)
    if analysis is None:
        raise HTTPException(status_code=404, detail="Analysis not found or API was restarted.")
    if review.anomaly_id not in analysis["reviews"]:
        raise HTTPException(status_code=404, detail="Detection does not belong to this analysis.")
    analysis["reviews"][review.anomaly_id] = review.decision
    return {"analysis_id": analysis_id, "anomaly_id": review.anomaly_id,
            "decision": review.decision, "review_counts": _review_counts(analysis)}


def _review_counts(analysis: dict) -> dict[str, int]:
    return {status.lower(): sum(value == status for value in analysis["reviews"].values())
            for status in ("Pending", "Verified", "Rejected")}


@app.get("/api/v1/analyses/{analysis_id}/report")
def generate_verified_report(analysis_id: str, format: Literal["json", "csv"] = "json") -> Response:
    """Generate a field report containing only operator-verified detections."""
    analysis = _analyses.get(analysis_id)
    if analysis is None:
        raise HTTPException(status_code=404, detail="Analysis not found or API was restarted.")
    verified = [row for row in analysis["report"]
                if analysis["reviews"].get(row["anomaly_id"]) == "Verified"]
    if not verified:
        raise HTTPException(status_code=409, detail="Verify at least one detection before generating a report.")
    if format == "csv":
        text = StringIO(newline="")
        writer = csv.DictWriter(text, fieldnames=list(verified[0].keys()))
        writer.writeheader()
        writer.writerows(verified)
        content = text.getvalue().encode("utf-8")
        media_type = "text/csv"
        filename = "marine_sentinel_verified_report.csv"
    else:
        payload = report_payload(
            pd.DataFrame(verified), analysis["metadata"],
            analysis["source_image"], analysis["mode"],
        )
        payload["operator_review"] = {"verified_count": len(verified),
                                      "excluded_count": len(analysis["report"]) - len(verified)}
        content = json.dumps(payload, indent=2).encode("utf-8")
        media_type = "application/json"
        filename = "marine_sentinel_verified_report.json"
    return Response(content=content, media_type=media_type,
                    headers={"Content-Disposition": f'attachment; filename="{filename}"'})
