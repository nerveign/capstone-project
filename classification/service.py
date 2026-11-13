"""Logika inference Random Forest (tanpa Flask).

Model dimuat malas (saat pertama dipakai), jadi dashboard tetap bisa jalan
walaupun pandas/scikit-learn belum terpasang atau file model belum ada.
"""
import json
import math
import threading

from .config import FEATURES, LABELS, METRICS_PATH, MODEL_PATH

_lock = threading.Lock()
_state = {"model": None, "loaded": False, "error": None}


class ModelUnavailable(RuntimeError):
    """Model belum dilatih / gagal dimuat."""


def load_model(force=False):
    """Muat model ke memori (di-cache). force=True memuat ulang dari disk."""
    with _lock:
        if _state["loaded"] and not force:
            return _state["model"]
        _state.update(model=None, error=None)
        if MODEL_PATH.exists():
            try:
                import joblib
                _state["model"] = joblib.load(MODEL_PATH)
            except Exception as exc:  # dependency hilang / file rusak / versi tidak cocok
                _state["error"] = f"{type(exc).__name__}: {exc}"
        _state["loaded"] = True
        return _state["model"]


def status():
    model = load_model()
    metrics = None
    if METRICS_PATH.exists():
        metrics = json.loads(METRICS_PATH.read_text(encoding="utf-8"))
    return {
        "model_loaded": model is not None,
        "features": FEATURES,
        "metrics": metrics,
        "error": _state["error"],
    }


def parse_features(body):
    """Ambil FEATURES dari body JSON. Raise ValueError kalau tidak valid."""
    try:
        row = {f: float(body[f]) for f in FEATURES}
    except (KeyError, TypeError, ValueError):
        raise ValueError(f"Isi semua fitur numerik: {', '.join(FEATURES)}") from None
    if not all(math.isfinite(v) for v in row.values()):
        raise ValueError("Nilai fitur harus berupa angka yang valid.")
    return row


def predict(row):
    model = load_model()
    if model is None:
        detail = f" ({_state['error']})" if _state["error"] else ""
        raise ModelUnavailable(
            "Model belum dilatih atau gagal dimuat. "
            f"Jalankan: python -m classification.train_model{detail}")
    import pandas as pd
    X = pd.DataFrame([row], columns=FEATURES)
    proba = model.predict_proba(X)[0]
    cls = int(proba.argmax())
    return {
        "label": LABELS[cls],
        "class_id": cls,
        "probability": {LABELS[int(c)]: float(p) for c, p in zip(model.classes_, proba)},
    }
