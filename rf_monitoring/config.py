"""Konfigurasi bersama untuk training dan inference."""
from pathlib import Path

BASE_DIR = Path(__file__).parent
DATA_PATH = BASE_DIR / "data" / "sdp_line14.csv"
MODEL_PATH = BASE_DIR / "model" / "random_forest.joblib"
METRICS_PATH = BASE_DIR / "model" / "metrics.json"

# Kolom arus fasa pada dataset (untuk menghitung label Y)
CURRENT_COLS = ["current_r", "current_s", "current_t"]

# Fitur X (energi dan frekuensi tidak dipakai)
FEATURES = ["voltage", "power", "power_factor"]

# Batas persentase ketidakseimbangan arus. Sesuaikan dengan standar/kebijakan Anda.
UNBALANCE_THRESHOLD = 10.0

LABELS = {0: "Seimbang", 1: "Tidak Seimbang"}
