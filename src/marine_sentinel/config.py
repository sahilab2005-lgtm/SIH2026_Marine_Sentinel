"""Environment-backed configuration shared by the frontend and backend."""
from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

try:
    from dotenv import load_dotenv
except ImportError:
    load_dotenv = None


PROJECT_ROOT = Path(__file__).resolve().parents[2]
if load_dotenv is not None:
    load_dotenv(PROJECT_ROOT / ".env")
else:
    for line in (PROJECT_ROOT / ".env").read_text(encoding="utf-8").splitlines():
        if "=" in line and not line.lstrip().startswith("#"):
            key, value = line.split("=", 1)
            os.environ.setdefault(key.strip(), value.strip())


def _required(name: str) -> str:
    value = os.getenv(name)
    if value is None or not value.strip():
        raise RuntimeError(f"Missing {name}. Copy .env.example to .env and set its values.")
    return value.strip()


def _path(name: str) -> Path:
    value = Path(_required(name))
    return value if value.is_absolute() else PROJECT_ROOT / value


@dataclass(frozen=True)
class Settings:
    model_path: Path
    results_directory: Path
    api_base_url: str
    api_host: str
    api_port: int
    api_allowed_origins: tuple[str, ...]
    api_max_upload_bytes: int
    api_health_timeout_seconds: float
    api_analysis_timeout_seconds: float
    default_mission_id: str
    default_latitude: float
    default_longitude: float
    default_resolution_m_per_pixel: float
    min_resolution_m_per_pixel: float
    max_resolution_m_per_pixel: float
    resolution_step: float
    earth_metres_per_degree_latitude: float
    yolo_proposal_confidence: float
    candidate_adaptive_block_size: int
    candidate_adaptive_constant: int
    candidate_kernel_size: int
    candidate_min_area_pixels: int
    candidate_max_area_ratio: float
    candidate_min_dimension_pixels: int
    candidate_nms_score_threshold: float
    candidate_nms_iou_threshold: float
    priority_high_confidence: float
    sonar_denoise_strength: int
    sonar_denoise_template_window: int
    sonar_denoise_search_window: int
    sonar_clahe_clip_limit: float
    sonar_clahe_tile_grid: int
    sonar_dropout_pixel_value: int


settings = Settings(
    model_path=_path("MODEL_PATH"),
    results_directory=_path("RESULTS_DIRECTORY"),
    api_base_url=_required("MARINE_SENTINEL_API_URL").rstrip("/"),
    api_host=_required("API_HOST"),
    api_port=int(_required("API_PORT")),
    api_allowed_origins=tuple(origin.strip() for origin in _required("API_ALLOWED_ORIGINS").split(",") if origin.strip()),
    api_max_upload_bytes=int(_required("API_MAX_UPLOAD_BYTES")),
    api_health_timeout_seconds=float(_required("API_HEALTH_TIMEOUT_SECONDS")),
    api_analysis_timeout_seconds=float(_required("API_ANALYSIS_TIMEOUT_SECONDS")),
    default_mission_id=_required("DEFAULT_MISSION_ID"),
    default_latitude=float(_required("DEFAULT_LATITUDE")),
    default_longitude=float(_required("DEFAULT_LONGITUDE")),
    default_resolution_m_per_pixel=float(_required("DEFAULT_RESOLUTION_M_PER_PIXEL")),
    min_resolution_m_per_pixel=float(_required("MIN_RESOLUTION_M_PER_PIXEL")),
    max_resolution_m_per_pixel=float(_required("MAX_RESOLUTION_M_PER_PIXEL")),
    resolution_step=float(_required("RESOLUTION_STEP")),
    earth_metres_per_degree_latitude=float(_required("EARTH_METRES_PER_DEGREE_LATITUDE")),
    yolo_proposal_confidence=float(_required("YOLO_PROPOSAL_CONFIDENCE")),
    candidate_adaptive_block_size=int(_required("CANDIDATE_ADAPTIVE_BLOCK_SIZE")),
    candidate_adaptive_constant=int(_required("CANDIDATE_ADAPTIVE_CONSTANT")),
    candidate_kernel_size=int(_required("CANDIDATE_KERNEL_SIZE")),
    candidate_min_area_pixels=int(_required("CANDIDATE_MIN_AREA_PIXELS")),
    candidate_max_area_ratio=float(_required("CANDIDATE_MAX_AREA_RATIO")),
    candidate_min_dimension_pixels=int(_required("CANDIDATE_MIN_DIMENSION_PIXELS")),
    candidate_nms_score_threshold=float(_required("CANDIDATE_NMS_SCORE_THRESHOLD")),
    candidate_nms_iou_threshold=float(_required("CANDIDATE_NMS_IOU_THRESHOLD")),
    priority_high_confidence=float(_required("PRIORITY_HIGH_CONFIDENCE")),
    sonar_denoise_strength=int(_required("SONAR_DENOISE_STRENGTH")),
    sonar_denoise_template_window=int(_required("SONAR_DENOISE_TEMPLATE_WINDOW")),
    sonar_denoise_search_window=int(_required("SONAR_DENOISE_SEARCH_WINDOW")),
    sonar_clahe_clip_limit=float(_required("SONAR_CLAHE_CLIP_LIMIT")),
    sonar_clahe_tile_grid=int(_required("SONAR_CLAHE_TILE_GRID")),
    sonar_dropout_pixel_value=int(_required("SONAR_DROPOUT_PIXEL_VALUE")),
)

MODEL_PATH = settings.model_path
RESULTS_DIRECTORY = settings.results_directory
EARTH_METRES_PER_DEGREE_LATITUDE = settings.earth_metres_per_degree_latitude
