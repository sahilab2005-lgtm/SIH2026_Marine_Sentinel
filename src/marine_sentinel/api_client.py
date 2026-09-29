"""Small HTTP client used by the Streamlit operator dashboard."""
from __future__ import annotations

from typing import Any

import requests

from marine_sentinel.config import settings


class MarineSentinelAPIError(RuntimeError):
    """Raised when the local FastAPI service is unavailable or rejects a request."""


def get_health() -> dict[str, Any]:
    try:
        response = requests.get(f"{settings.api_base_url}/health", timeout=settings.api_health_timeout_seconds)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as error:
        raise MarineSentinelAPIError("FastAPI backend is not running.") from error


def analyze_image(
    image_name: str, image_bytes: bytes, mission_id: str, latitude: float, longitude: float, resolution_m_per_pixel: float,
) -> dict[str, Any]:
    files = {"image": (image_name, image_bytes, _content_type(image_name))}
    data = {
        "mission_id": mission_id,
        "latitude": str(latitude),
        "longitude": str(longitude),
        "resolution_m_per_pixel": str(resolution_m_per_pixel),
    }
    try:
        response = requests.post(f"{settings.api_base_url}/api/v1/analyze", files=files, data=data,
                                 timeout=settings.api_analysis_timeout_seconds)
        if not response.ok:
            detail = response.json().get("detail", response.text)
            raise MarineSentinelAPIError(f"Backend analysis failed: {detail}")
        return response.json()
    except requests.RequestException as error:
        raise MarineSentinelAPIError("Could not reach FastAPI backend. Start it with `python -m uvicorn marine_sentinel.api.main:app --reload`.") from error


def review_detection(analysis_id: str, anomaly_id: str, decision: str) -> dict[str, Any]:
    try:
        response = requests.post(
            f"{settings.api_base_url}/api/v1/analyses/{analysis_id}/review",
            json={"anomaly_id": anomaly_id, "decision": decision},
            timeout=settings.api_health_timeout_seconds,
        )
        if not response.ok:
            raise MarineSentinelAPIError(response.json().get("detail", "Could not save operator review."))
        return response.json()
    except requests.RequestException as error:
        raise MarineSentinelAPIError("Could not save review to the FastAPI backend.") from error


def generate_report(analysis_id: str, report_format: str) -> bytes:
    try:
        response = requests.get(
            f"{settings.api_base_url}/api/v1/analyses/{analysis_id}/report",
            params={"format": report_format}, timeout=settings.api_health_timeout_seconds,
        )
        if not response.ok:
            try:
                detail = response.json().get("detail", "Could not generate report.")
            except ValueError:
                detail = "Could not generate report."
            raise MarineSentinelAPIError(detail)
        return response.content
    except requests.RequestException as error:
        raise MarineSentinelAPIError("Could not generate report through the FastAPI backend.") from error


def _content_type(filename: str) -> str:
    extension = filename.lower().rsplit(".", 1)[-1]
    return {"png": "image/png", "jpg": "image/jpeg", "jpeg": "image/jpeg", "tif": "image/tiff", "tiff": "image/tiff"}.get(extension, "application/octet-stream")
