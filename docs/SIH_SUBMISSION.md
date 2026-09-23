# Marine Sentinel: SIH Prototype Summary

## Problem addressed

Manual review of side-scan sonar logs is slow and can miss ghost nets, crab pots and other anthropogenic hazards hidden among seabed texture, speckle noise and acoustic shadows. Marine Sentinel converts sonar imagery into prioritised, localised review targets for conservation and marine-operations teams.

## Proposed solution

Marine Sentinel is a local-first AI dashboard that accepts a side-scan sonar image, conditions it for acoustic noise, detects anomalies, automatically separates strong predictions from weak acoustic noise for each image, and exports a structured hazard report. It is designed to run on an onboard laptop, AUV companion computer or edge device without relying on cloud connectivity.

## Functional modules

| Module | Prototype capability |
|---|---|
| Sonar ingestion | Upload PNG, JPG, JPEG, TIFF images |
| Noise filtering | Non-local-means speckle suppression and CLAHE local-contrast enhancement |
| AI detection | YOLO detector for Crab-Pot / Maybe-Crab-Pot classes when trained weights are added |
| Fallback operation | Acoustic-anomaly candidate detection so the system remains usable before model training |
| Confidence review | Per-target confidence, image-calibrated confidence separation, non-maximum suppression and HIGH/REVIEW priority |
| Geotagging | Converts image locations to approximate latitude/longitude from survey origin and metres-per-pixel metadata |
| Reporting | Downloadable CSV and JSON containing ID, class, confidence, coordinates, dimensions, bounding box and priority |

## Data and model

The repository includes a YOLO-format sonar dataset with `Crab-Pot` and `Maybe-Crab-Pot` labels:

- Training images: 5,721
- Validation images: 555
- Test images: 398

The lightweight YOLO11n architecture is proposed because it offers a good speed/accuracy tradeoff for later edge deployment. The detector is intentionally modular: replacing `models/best.pt` with a future model requires no dashboard change.

## Innovation / impact

- Reduces the search area sent to human experts instead of demanding full manual review.
- Gives a cleanup team machine-readable, geographical hand-off data rather than only annotated images.
- Makes uncertainty visible through confidence and review priority, reducing unsafe overclaiming from noisy acoustic scenes.
- Uses a local-first architecture suitable for intermittent offshore connectivity.

## Technology stack

Python, Streamlit, OpenCV, Ultralytics YOLO, NumPy, Pandas and Pillow.

## Future scope

Train with a larger multi-class Indian coastal sonar dataset; add shadow-shape validation, sequential ping metadata ingestion, segmentation for tangled nets, GIS map layers, and quantised ONNX/TensorRT deployment for AUV hardware.
