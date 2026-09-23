"""Convenient FastAPI entry point: `uvicorn main:app --reload`."""
from pathlib import Path
import sys

SOURCE_DIRECTORY = Path(__file__).parent / "src"
sys.path.insert(0, str(SOURCE_DIRECTORY))

from marine_sentinel.api.main import app

