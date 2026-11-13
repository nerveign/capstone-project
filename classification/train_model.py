"""Training Random Forest: fitur X -> label Y (Seimbang / Tidak Seimbang).

Jalankan dari root projek:  python -m classification.train_model
"""
import json
import joblib
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (accuracy_score, precision_score, recall_score,
                             f1_score, confusion_matrix)
from sklearn.model_selection import train_test_split

from .config import (CURRENT_COLS, DATA_PATH, FEATURES, METRICS_PATH,
                     MODEL_PATH, UNBALANCE_THRESHOLD)


def unbalance_percent(r, s, t):
    """Ketidakseimbangan (%) = deviasi maksimum dari rata-rata / rata-rata x 100."""
    avg = (r + s + t) / 3
    dev = pd.concat([(r - avg).abs(), (s - avg).abs(), (t - avg).abs()], axis=1).max(axis=1)
    return dev / avg * 100


def main():
    df = pd.read_csv(DATA_PATH).dropna()

    # Langkah 2: hitung ketidakseimbangan arus -> label Y
    df["unbalance_pct"] = unbalance_percent(*(df[c] for c in CURRENT_COLS))
    y = (df["unbalance_pct"] > UNBALANCE_THRESHOLD).astype(int)  # 1 = Tidak Seimbang

    # Langkah 3: fitur X
    X = df[FEATURES]

    X_tr, X_te, y_tr, y_te = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y)

    # Langkah 4: training
    model = RandomForestClassifier(
        n_estimators=200, random_state=42, class_weight="balanced", n_jobs=-1)
    model.fit(X_tr, y_tr)

    # Langkah 6: evaluasi
    pred = model.predict(X_te)
    metrics = {
        "accuracy": accuracy_score(y_te, pred),
        "precision": precision_score(y_te, pred, zero_division=0),
        "recall": recall_score(y_te, pred, zero_division=0),
        "f1": f1_score(y_te, pred, zero_division=0),
        "confusion_matrix": confusion_matrix(y_te, pred).tolist(),
        "feature_importance": dict(zip(FEATURES, map(float, model.feature_importances_))),
        "n_train": len(X_tr), "n_test": len(X_te),
        "threshold": UNBALANCE_THRESHOLD,
    }

    MODEL_PATH.parent.mkdir(exist_ok=True)
    joblib.dump(model, MODEL_PATH)
    METRICS_PATH.write_text(json.dumps(metrics, indent=2), encoding="utf-8")

    print(f"Model tersimpan: {MODEL_PATH}")
    for k in ("accuracy", "precision", "recall", "f1"):
        print(f"{k:>10}: {metrics[k]:.4f}")
    print("Confusion matrix [[TN FP] [FN TP]]:", metrics["confusion_matrix"])
    print("Feature importance:", metrics["feature_importance"])
    print("Muat ulang model di server yang sedang jalan: "
          "POST /api/classification/reload (atau restart server).")


if __name__ == "__main__":
    main()
