# Marine Sentinel

AI-powered detection of marine debris and anomalies in side-scan sonar imagery, developed as a Smart India Hackathon prototype.

Marine Sentinel uses a two-service local architecture: the Streamlit dashboard is the operator interface, while a FastAPI backend performs sonar conditioning, YOLO inference, geotagging, and report generation.

## Features

- Local-first Streamlit operator dashboard: upload → analyse → export.
- YOLO detection of `Crab-Pot` and `Maybe-Crab-Pot` targets.
- Image-calibrated confidence separation to reduce weak acoustic-noise proposals.
- Sonar preprocessing: speckle reduction and contrast normalization.
- Bounding-box dimensions, priority scoring, and approximate latitude/longitude.
- Downloadable field-ready CSV and JSON anomaly reports.

## Project structure

```text
MarineDebrisAI/
├── app.py                     # Streamlit dashboard (API client)
├── config/dataset.yaml        # YOLO dataset configuration
├── src/marine_sentinel/       # Core processing, API, and frontend client modules
├── scripts/                   # Setup, backend, dashboard, train, evaluate utilities
├── notebooks/                 # Google Colab training notebook
├── tests/                     # Automated tests
├── docs/                      # SIH submission notes
├── deliverables/              # SIH presentation deck
├── models/                    # Local trained weights (not committed)
├── dataset/                   # Local training data (not committed)
└── results/                   # Local training and inference outputs (not committed)
```

## Run locally

Create an environment once, then open **two PowerShell terminals** in the project folder:

```powershell
.\scripts\setup_dashboard.ps1
.\scripts\run_backend.ps1
```

In the second terminal:

```powershell
.\scripts\run_dashboard.ps1
```

The backend API is available at `http://127.0.0.1:8000/docs`; the dashboard is available at the local URL printed by Streamlit.

Or use an existing Python environment:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python -m uvicorn marine_sentinel.api.main:app --app-dir src --reload
# In a second terminal:
streamlit run app.py
```

Place trained weights at `models/best.pt`. The dashboard will then use YOLO locally; nothing is uploaded to the cloud.

## Configuration

All operational values are stored locally in `.env`, including API host/port, model path, upload limit, survey defaults, and detection/preprocessing settings. `.env` is never uploaded to GitHub. Teammates copy `.env.example` to `.env` and adjust their local values.

## Training and evaluation

The local `dataset/` and `models/` folders are deliberately excluded from GitHub because they are large. To retrain on a GPU, open [notebooks/train_marine_sentinel_colab.ipynb](notebooks/train_marine_sentinel_colab.ipynb) in Google Colab.

```powershell
python scripts/train.py
python scripts/evaluate.py
python scripts/predict.py path\to\sonar_image.jpg
```

`evaluate.py` uses only the held-out test split. Copy the resulting `best.pt` to `models/best.pt` before running the dashboard.

## Important limitation

This is a prototype. Model predictions should be verified by a marine operator before cleanup or navigation decisions are made.
