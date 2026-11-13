"""Membuat data contoh (sintetis) agar proyek bisa langsung dijalankan.
Ganti data/sdp_line14.csv dengan data pengukuran asli Panel SDP Line 14.
Kolom: voltage, current_r, current_s, current_t, power, power_factor
"""
import numpy as np
import pandas as pd
from config import DATA_PATH

rng = np.random.default_rng(42)
n = 3000
base = rng.uniform(40, 120, n)
skew = rng.random(n) < 0.4  # sebagian data dibuat tidak seimbang
dev = np.where(skew[:, None], rng.uniform(0.10, 0.35, (n, 3)), rng.uniform(0.0, 0.06, (n, 3)))
sign = rng.choice([-1, 1], (n, 3))
cur = base[:, None] * (1 + sign * dev)

voltage = rng.normal(380, 4, n) - skew * rng.uniform(0, 6, n)
pf = np.clip(rng.normal(0.9, 0.04, n) - skew * rng.uniform(0, 0.08, n), 0.6, 1.0)
power = np.sqrt(3) * voltage * cur.mean(axis=1) * pf / 1000  # kW

df = pd.DataFrame({
    "voltage": voltage.round(2),
    "current_r": cur[:, 0].round(2),
    "current_s": cur[:, 1].round(2),
    "current_t": cur[:, 2].round(2),
    "power": power.round(2),
    "power_factor": pf.round(3),
})
DATA_PATH.parent.mkdir(exist_ok=True)
df.to_csv(DATA_PATH, index=False)
print(f"Tersimpan: {DATA_PATH} ({len(df)} baris)")
