"""Server Flask: dashboard + API inference Random Forest."""
import json
import joblib
import pandas as pd
from flask import Flask, jsonify, request, send_from_directory

from config import FEATURES, LABELS, METRICS_PATH, MODEL_PATH

app = Flask(__name__, static_folder="static", static_url_path="/static")


def load_model():
    return joblib.load(MODEL_PATH) if MODEL_PATH.exists() else None


model = load_model()


@app.get("/")
def index():
    return send_from_directory("static", "index.html")


@app.get("/api/status")
def status():
    metrics = json.loads(METRICS_PATH.read_text()) if METRICS_PATH.exists() else None
    return jsonify(model_loaded=model is not None, features=FEATURES, metrics=metrics)


@app.post("/api/reload")
def reload_model():
    global model
    model = load_model()
    return jsonify(model_loaded=model is not None)


@app.post("/api/predict")
def predict():
    if model is None:
        return jsonify(error="Model belum dilatih. Jalankan train_model.py."), 503
    body = request.get_json(silent=True) or {}
    try:
        row = {f: float(body[f]) for f in FEATURES}
    except (KeyError, TypeError, ValueError):
        return jsonify(error=f"Isi semua fitur numerik: {', '.join(FEATURES)}"), 400

    X = pd.DataFrame([row], columns=FEATURES)
    proba = model.predict_proba(X)[0]
    cls = int(proba.argmax())
    return jsonify(
        label=LABELS[cls],
        class_id=cls,
        probability={LABELS[int(c)]: float(p) for c, p in zip(model.classes_, proba)},
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
