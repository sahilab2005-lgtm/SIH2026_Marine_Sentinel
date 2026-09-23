# Trained model location

The Streamlit dashboard loads its real YOLO detector automatically from this exact path:

```text
models/best.pt
```

Train with [the Colab notebook](../notebooks/train_marine_sentinel_colab.ipynb), download `best.pt`, and copy it here. Restart the FastAPI backend; the dashboard will show **API + YOLO ONLINE**.
