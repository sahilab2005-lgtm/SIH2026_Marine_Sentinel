from dataclasses import asdict, dataclass

from marine_sentinel.config import settings


@dataclass(frozen=True)
class SurveyMetadata:
    latitude: float
    longitude: float
    resolution_m_per_pixel: float
    mission_id: str = settings.default_mission_id


@dataclass(frozen=True)
class Detection:
    x: int
    y: int
    width: int
    height: int
    label: str
    confidence: float
    detector: str

    def as_dict(self) -> dict:
        return asdict(self)
