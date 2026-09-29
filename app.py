"""Marine Sentinel Streamlit operator console. Run: streamlit run app.py."""
from __future__ import annotations

import base64
import hashlib
import sys
from io import BytesIO
from pathlib import Path

import numpy as np
import pandas as pd
import streamlit as st
from PIL import Image

ROOT = Path(__file__).parent
sys.path.insert(0, str(ROOT / "src"))

from marine_sentinel.api_client import MarineSentinelAPIError, analyze_image, generate_report, get_health, review_detection
from marine_sentinel.config import settings

st.set_page_config(page_title="Marine Sentinel | Mission Console", page_icon="🌊", layout="wide")

st.markdown(
    """<style>
    :root { --cyan:#58e6fa; --aqua:#13c9dc; --ink:#06111c; --panel:#0a2639; --line:#1d607a; --muted:#9bc1cb; }
    .stApp { background:radial-gradient(circle at 76% -8%,#155a71 0%,#08263a 34%,#040c15 100%); color:#e8f7fb; }
    [data-testid="stHeader"] { background:transparent; }
    [data-testid="stSidebar"] { background:linear-gradient(180deg,#072c43 0%,#051827 100%); border-right:1px solid #1d607a; }
    [data-testid="stSidebar"] [data-testid="stVerticalBlock"] { gap:.65rem; }
    h1,h2,h3 { color:var(--cyan)!important; letter-spacing:-.03em; }
    .hero { padding:1.6rem 1.8rem; border:1px solid #24728d; border-radius:18px; background:linear-gradient(112deg,rgba(8,44,65,.96),rgba(11,76,91,.62)); box-shadow:0 16px 44px rgba(0,0,0,.2); margin:0 0 1.05rem; }
    .hero h1 { margin:0!important; font-size:clamp(2rem,4vw,3.35rem)!important; }
    .eyebrow { color:#80e8f5; font-size:.72rem; font-weight:800; letter-spacing:.17em; margin-bottom:.45rem; }
    .hero-copy { margin:.55rem 0 0; max-width:800px; color:#c5e7ed; font-size:1.02rem; }
    .pulse { display:inline-block; width:9px; height:9px; border-radius:50%; background:#3ee6a0; box-shadow:0 0 14px #3ee6a0; margin-right:7px; }
    .side-brand { padding:15px 8px 11px; } .side-brand h2 { margin:0!important; font-size:1.35rem!important; }
    .side-brand p { color:#90c9d7; letter-spacing:.15em; font-size:.68rem; margin:.28rem 0 0; }
    .side-section { color:#75dce9; font-size:.7rem; font-weight:800; letter-spacing:.13em; text-transform:uppercase; margin:1rem 0 .25rem; }
    .status { padding:13px 14px; border:1px solid #246f86; border-radius:12px; background:rgba(7,45,64,.82); color:#c6eef4; font-size:.84rem; }
    .status strong { color:#f1feff; }
    .status.warn { border-color:#9b7924; background:rgba(70,51,10,.44); }
    .status.offline { border-color:#84445a; background:rgba(72,23,35,.45); }
    .workflow { display:flex; gap:.8rem; flex-wrap:wrap; margin:.4rem 0 1.25rem; }
    .workflow-step { border:1px solid #205c73; border-radius:999px; padding:.42rem .8rem; color:#b8e2e9; font-size:.8rem; background:#092638; }
    .workflow-step span { color:#56e5f6; font-weight:800; margin-right:.35rem; }
    .upload-zone { padding:1.45rem; border:1px dashed #3ac8d9; border-radius:18px; background:linear-gradient(135deg,rgba(8,52,70,.88),rgba(5,29,45,.82)); }
    .upload-zone h3 { margin:0 0 .35rem!important; }.upload-zone p { color:#b6dce3; margin:0 0 1rem; }
    [data-testid="stFileUploader"] { border:1px solid #20647c; border-radius:12px; padding:12px; background:#061d2e; }
    [data-testid="stFileUploader"] section { background:#0a354a; border-radius:9px; }
    div[data-testid="stMetric"] { background:linear-gradient(135deg,#103b52,#09283d); border:1px solid #1e6884; padding:16px; border-radius:14px; min-height:108px; }
    div[data-testid="stMetric"] label { color:#9ed5df!important; font-size:.78rem!important; text-transform:uppercase; letter-spacing:.07em; }
    .notice { padding:14px 16px; border-radius:12px; border-left:4px solid #3de0ee; background:#0a3448; color:#c9eef4; margin:.8rem 0; }
    .notice.good { border-color:#48e2a4; background:#0b3c3b; }.notice.warning { border-color:#f0bb55; background:#483615; }
    .image-label { color:#91cbd4; font-size:.75rem; font-weight:700; text-transform:uppercase; letter-spacing:.1em; margin:.4rem 0; }
    .target-card { min-height:82px; padding:14px; border-radius:13px; border:1px solid #22677f; background:linear-gradient(135deg,#0f4258,#092b40); text-align:center; color:#ccecf1; }
    .target-card b { font-size:1.55rem; color:#5de8f8; display:block; }.target-card span { font-size:.76rem; }
    .empty { padding:28px; border-radius:16px; border:1px dashed #2e8aa1; background:rgba(9,43,60,.72); text-align:center; color:#b9dde4; }
    .empty h3 { margin:0 0 .5rem!important; }.caption { color:#8ebfc9; font-size:.82rem; }
    .footer { color:#6eaeba; text-align:center; padding:1.5rem 0 .3rem; font-size:.78rem; }
    </style>""",
    unsafe_allow_html=True,
)


def clear_analysis() -> None:
    for key in ("image", "image_name", "image_bytes", "processed", "overlay", "report", "mode",
                "diagnostics", "report_payload", "raw_detection_count", "auto_threshold", "analysis_signature",
                "analysis_id", "review_statuses", "generated_csv", "generated_json"):
        st.session_state.pop(key, None)


def decode_image(encoded: str, mode: str | None = None) -> np.ndarray:
    image = Image.open(BytesIO(base64.b64decode(encoded)))
    return np.array(image.convert(mode)) if mode else np.array(image)


try:
    backend_health = get_health()
except MarineSentinelAPIError:
    backend_health = None

with st.sidebar:
    st.markdown('<div class="side-brand"><h2>🌊 Marine Sentinel</h2><p>SONAR OPERATIONS CONSOLE</p></div>', unsafe_allow_html=True)
    st.divider()
    st.markdown('<p class="side-section">Mission configuration</p>', unsafe_allow_html=True)
    mission_id = st.text_input("Mission ID", settings.default_mission_id, help="Included in every exported report.")
    with st.expander("📍 Survey origin & scale", expanded=True):
        latitude = st.number_input("Start latitude", value=settings.default_latitude, format="%.6f")
        longitude = st.number_input("Start longitude", value=settings.default_longitude, format="%.6f")
        resolution = st.number_input("Ground resolution (m / pixel)", settings.min_resolution_m_per_pixel,
                                     settings.max_resolution_m_per_pixel, settings.default_resolution_m_per_pixel,
                                     settings.resolution_step)
    st.markdown('<p class="side-section">Inference status</p>', unsafe_allow_html=True)
    if backend_health and backend_health["yolo_ready"]:
        st.markdown('<div class="status"><span class="pulse"></span><strong>API + YOLO ONLINE</strong><br>Local model inference is ready.</div>', unsafe_allow_html=True)
    elif backend_health:
        st.markdown('<div class="status warn"><strong>API ONLINE · REVIEW MODE</strong><br>Add <code>models/best.pt</code> to enable YOLO.</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="status offline"><strong>API OFFLINE</strong><br>Start FastAPI before analysis.</div>', unsafe_allow_html=True)
    st.markdown('<div class="notice"><b>Automatic confidence calibration</b><br>Each scan uses its own prediction distribution to separate stronger targets from acoustic noise.</div>', unsafe_allow_html=True)
    st.caption("Local-first processing · No cloud upload")

st.markdown('<section class="hero"><div class="eyebrow">SIH 2026 · UNDERWATER INTELLIGENCE PLATFORM</div><h1>Marine Debris & Anomaly Detection</h1><p class="hero-copy">Turn side-scan sonar imagery into explainable, geotagged hazard intelligence for marine cleanup and autonomous underwater operations.</p></section>', unsafe_allow_html=True)
st.markdown('<div class="workflow"><div class="workflow-step"><span>01</span>Upload sonar scan</div><div class="workflow-step"><span>02</span>AI anomaly review</div><div class="workflow-step"><span>03</span>Export field report</div><div class="workflow-step"><span>04</span>Mission diagnostics</div></div>', unsafe_allow_html=True)

upload_tab, analysis_tab, report_tab, system_tab = st.tabs(["Upload mission scan", "Detection intelligence", "Export report", "System health"])

with upload_tab:
    st.markdown('<div class="upload-zone"><h3>Start a new sonar mission</h3><p>Upload one raw side-scan sonar image. The local FastAPI service will condition the scan, run the model, and prepare a geotagged response.</p>', unsafe_allow_html=True)
    upload = st.file_uploader("Side-scan sonar image", type=["png", "jpg", "jpeg", "tif", "tiff"], label_visibility="collapsed")
    st.markdown('</div>', unsafe_allow_html=True)
    if upload is None:
        clear_analysis()
        st.info("Supported formats: PNG, JPG, JPEG, TIFF. Your image stays on this computer.")
    else:
        image_bytes = upload.getvalue()
        source_image = np.array(Image.open(BytesIO(image_bytes)).convert("RGB"))
        st.session_state.update(image=source_image, image_name=upload.name, image_bytes=image_bytes)
        preview, details = st.columns([3, 2])
        with preview:
            st.image(source_image, use_container_width=True, caption=f"Mission input · {upload.name}")
        with details:
            st.markdown("### Scan ready")
            st.markdown('<div class="notice good"><b>Local upload secured</b><br>Your sonar scan is ready for API analysis. No cloud storage is used.</div>', unsafe_allow_html=True)
            st.caption(f"Image dimensions: {source_image.shape[1]} × {source_image.shape[0]} px")
            st.caption(f"Mission ID: {mission_id}")

image = st.session_state.get("image")
analysis_signature = None
if image is not None:
    analysis_signature = hashlib.sha256(
        st.session_state.image_bytes + f"|{mission_id}|{latitude:.6f}|{longitude:.6f}|{resolution:.4f}".encode()
    ).hexdigest()

if image is not None and backend_health is not None and st.session_state.get("analysis_signature") != analysis_signature:
    with st.spinner("FastAPI is conditioning sonar texture and running local inference..."):
        try:
            result = analyze_image(st.session_state.image_name, st.session_state.image_bytes, mission_id, latitude, longitude, resolution)
            st.session_state.update(
                processed=decode_image(result["processed_image_png_base64"]),
                overlay=decode_image(result["overlay_image_png_base64"], "RGB"),
                report=pd.DataFrame(result["report"]), mode=result["detector_mode"],
                raw_detection_count=result["raw_proposal_count"], auto_threshold=result["auto_threshold"],
                diagnostics=result["diagnostics"], report_payload=result["report_payload"],
                analysis_signature=analysis_signature, analysis_id=result["analysis_id"],
                review_statuses={row["anomaly_id"]: "Pending" for row in result["report"]},
                generated_csv=None, generated_json=None,
            )
        except MarineSentinelAPIError as error:
            st.session_state.update(report=pd.DataFrame(), mode="API unavailable", raw_detection_count=0,
                                    auto_threshold=None, diagnostics={}, report_payload={}, processed=image, overlay=image,
                                    analysis_signature=analysis_signature)
            st.error(str(error))

with analysis_tab:
    if image is None:
        st.markdown('<div class="empty"><h3>Awaiting sonar scan</h3><p>Upload a mission image to activate the detection workspace.</p></div>', unsafe_allow_html=True)
    elif backend_health is None:
        st.markdown('<div class="empty"><h3>FastAPI backend is offline</h3><p>Start <code>python -m uvicorn main:app --reload</code>, refresh the dashboard, then upload your scan again.</p></div>', unsafe_allow_html=True)
    else:
        report = st.session_state.get("report", pd.DataFrame())
        raw_count = st.session_state.get("raw_detection_count", 0)
        diagnostics = st.session_state.get("diagnostics", {})
        mode = st.session_state.get("mode", "Awaiting analysis")
        st.markdown('<div class="notice good"><b>LIVE LOCAL INFERENCE</b><br>Every overlay and count is returned by the FastAPI analysis service for this uploaded image.</div>', unsafe_allow_html=True)
        metrics = st.columns(4)
        metrics[0].metric("Detected targets", len(report))
        metrics[1].metric("Raw model signals", raw_count)
        metrics[2].metric("Mean confidence", f"{report.confidence_percent.mean():.0f}%" if not report.empty else "—")
        metrics[3].metric("Inference engine", "YOLO" if backend_health["yolo_ready"] else "Review filter")
        visual_left, visual_right = st.columns(2)
        with visual_left:
            st.markdown('<p class="image-label">Acoustic conditioning output</p>', unsafe_allow_html=True)
            st.image(st.session_state.get("processed", image), clamp=True, use_container_width=True, caption="Speckle reduction + contrast normalization")
        with visual_right:
            st.markdown('<p class="image-label">AI detection overlay</p>', unsafe_allow_html=True)
            st.image(st.session_state.get("overlay", image), use_container_width=True, caption=mode)
        if report.empty:
            st.markdown('<div class="empty"><h3>No exportable debris target</h3><p>The current scan did not contain a sufficiently strong model prediction. Weak sonar texture is excluded to reduce false alarms.</p></div>', unsafe_allow_html=True)
        else:
            st.markdown("### Detection queue")
            class_counts = report["classification"].value_counts()
            cards = st.columns(min(len(class_counts), 4))
            for column, (label, count) in zip(cards, class_counts.items()):
                column.markdown(f'<div class="target-card"><b>{count}</b><span>{label}</span></div>', unsafe_allow_html=True)
            threshold = st.session_state.get("auto_threshold")
            cutoff = f"{threshold:.0%}" if threshold is not None else "image-calibrated"
            st.markdown(f'<div class="notice"><b>Model verdict · {len(report)} target(s) detected</b><br>Confidence separation was calculated from this scan’s own prediction distribution (cutoff: {cutoff}).</div>', unsafe_allow_html=True)
            st.caption("Review each detection before generating the field report. Decisions are recorded by FastAPI.")
            statuses = st.session_state.get("review_statuses", {})
            for _, detection in report.iterrows():
                anomaly_id = detection["anomaly_id"]
                status = statuses.get(anomaly_id, "Pending")
                st.markdown(f"**{anomaly_id} · {detection['classification']}** — {detection['confidence_percent']}% confidence · Review: **{status}**")
                _, verify_col, reject_col = st.columns([5, 1, 1])
                try:
                    if verify_col.button("✓ Verify", key=f"verify_{analysis_signature}_{anomaly_id}", disabled=status == "Verified"):
                        result = review_detection(st.session_state.analysis_id, anomaly_id, "Verified")
                        st.session_state.review_statuses[anomaly_id] = result["decision"]
                        st.session_state.generated_csv = st.session_state.generated_json = None
                        st.rerun()
                    if reject_col.button("✕ Reject", key=f"reject_{analysis_signature}_{anomaly_id}", disabled=status == "Rejected"):
                        result = review_detection(st.session_state.analysis_id, anomaly_id, "Rejected")
                        st.session_state.review_statuses[anomaly_id] = result["decision"]
                        st.session_state.generated_csv = st.session_state.generated_json = None
                        st.rerun()
                except MarineSentinelAPIError as error:
                    st.error(str(error))
            statuses = st.session_state.get("review_statuses", {}).values()
            st.caption(f"{sum(value == 'Verified' for value in statuses)} verified · {sum(value == 'Pending' for value in statuses)} pending · {sum(value == 'Rejected' for value in statuses)} rejected")

with report_tab:
    report = st.session_state.get("report", pd.DataFrame())
    if image is None:
        st.markdown('<div class="empty"><h3>No mission report yet</h3><p>Upload and analyse a sonar image first.</p></div>', unsafe_allow_html=True)
    elif report.empty:
        st.markdown('<div class="empty"><h3>No reportable anomaly</h3><p>The selected scan has no validated target to export.</p></div>', unsafe_allow_html=True)
    else:
        verified_count = sum(value == "Verified" for value in st.session_state.get("review_statuses", {}).values())
        st.markdown(f"### Field hand-off package · {verified_count} verified target(s)")
        st.caption("FastAPI generates the report from verified detections only. Verify targets in the Detection intelligence tab first.")
        if st.button("Generate verified report", type="primary", disabled=verified_count == 0):
            try:
                st.session_state.generated_csv = generate_report(st.session_state.analysis_id, "csv")
                st.session_state.generated_json = generate_report(st.session_state.analysis_id, "json")
            except MarineSentinelAPIError as error:
                st.error(str(error))
        if st.session_state.get("generated_csv") and st.session_state.get("generated_json"):
            csv_column, json_column = st.columns(2)
            csv_column.download_button("Download verified CSV report", st.session_state.generated_csv,
                                       "marine_sentinel_verified_report.csv", "text/csv", use_container_width=True)
            json_column.download_button("Download verified JSON report", st.session_state.generated_json,
                                        "marine_sentinel_verified_report.json", "application/json", use_container_width=True)

with system_tab:
    st.markdown("### System health & pipeline")
    system_left, system_right = st.columns([3, 2])
    with system_left:
        st.markdown('<div class="notice"><b>Pipeline</b><br>Sonar image → noise suppression → local contrast normalization → FastAPI model inference → image-calibrated filtering → geotag conversion → overlay and report export.</div>', unsafe_allow_html=True)
        if image is not None and st.session_state.get("diagnostics"):
            diagnostics = st.session_state.diagnostics
            health_metrics = st.columns(3)
            health_metrics[0].metric("Mean backscatter", diagnostics["mean_backscatter"])
            health_metrics[1].metric("Texture contrast", diagnostics["texture_contrast"])
            health_metrics[2].metric("Dropout ratio", f"{diagnostics['dropout_ratio_percent']}%")
    with system_right:
        if backend_health:
            model_status = "YOLO model loaded" if backend_health["yolo_ready"] else "Candidate review filter active"
            st.markdown(f'<div class="status"><span class="pulse"></span><strong>Backend healthy</strong><br>{model_status}<br><br>API endpoint: <code>{settings.api_base_url}</code></div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="status offline"><strong>Backend unavailable</strong><br>Start the FastAPI service to run analysis.</div>', unsafe_allow_html=True)

st.markdown('<div class="footer">MARINE SENTINEL · LOCAL-FIRST SONAR INTELLIGENCE · SIH PROTOTYPE</div>', unsafe_allow_html=True)
