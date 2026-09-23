import io

import numpy as np
from fastapi.testclient import TestClient
from PIL import Image

from marine_sentinel.api.main import app


def test_health_endpoint_reports_service_status():
    response = TestClient(app).get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_analyze_rejects_non_image_upload():
    response = TestClient(app).post(
        "/api/v1/analyze",
        files={"image": ("not_sonar.txt", b"not an image", "text/plain")},
        data={"latitude": "18.922", "longitude": "72.8347", "resolution_m_per_pixel": "0.1"},
    )

    assert response.status_code == 415


def test_analyze_returns_report_for_valid_image():
    image = Image.fromarray(np.full((32, 32, 3), 128, dtype=np.uint8))
    data = io.BytesIO()
    image.save(data, format="PNG")

    response = TestClient(app).post(
        "/api/v1/analyze",
        files={"image": ("sonar.png", data.getvalue(), "image/png")},
        data={"mission_id": "TEST-001", "latitude": "18.922", "longitude": "72.8347", "resolution_m_per_pixel": "0.1"},
    )

    body = response.json()
    assert response.status_code == 200
    assert body["source_image"] == "sonar.png"
    assert "report" in body
    assert body["overlay_image_png_base64"]
