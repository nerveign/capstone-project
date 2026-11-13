# Load Classification – Random Forest (Ketidakseimbangan Arus, Panel SDP Line 14)

Alur: data pengukuran → hitung % ketidakseimbangan arus R/S/T → label Y (Seimbang / Tidak Seimbang)
→ fitur X (voltage, power, power_factor) → training Random Forest → klasifikasi → evaluasi
(accuracy, precision, recall, F1-score).

Halaman dashboard: menu **Load Classification** (`/classification`).

## Struktur
- `config.py` – kolom, fitur, ambang batas ketidakseimbangan
- `service.py` – memuat model & inference (tanpa Flask)
- `routes.py` – API Flask (Blueprint, didaftarkan di `app.py`)
- `train_model.py` – training + evaluasi, menyimpan model dan metrics
- `generate_sample_data.py` – membuat data contoh sintetis
- `data/sdp_line14.csv` – dataset (ganti dengan data asli)
- `model/random_forest.joblib`, `model/metrics.json` – hasil training

## Perintah (jalankan dari root projek)
```bash
python -m classification.generate_sample_data   # lewati jika sudah punya data asli (menimpa CSV!)
python -m classification.train_model            # latih ulang & simpan model + metrics
```
Setelah training, restart server atau panggil `POST /api/classification/reload`.

## Data asli
Simpan CSV di `data/sdp_line14.csv` dengan kolom:
`voltage, current_r, current_s, current_t, power, power_factor`.
Jika nama kolom berbeda, ubah di `config.py`.

## Catatan
- Rumus ketidakseimbangan: deviasi maksimum arus fasa dari rata-rata ÷ rata-rata × 100.
- `UNBALANCE_THRESHOLD` (default 10%) di `config.py` adalah nilai awal; sesuaikan dengan standar Anda.
- Arus R/S/T hanya dipakai untuk membuat label, tidak menjadi fitur X.
- Data contoh bersifat sintetis, jadi skor evaluasinya tidak mewakili kondisi panel sebenarnya.

## API
- `GET  /api/classification/status` – status model dan metrik
- `POST /api/classification/reload` – muat ulang model dari disk
- `POST /api/classification/predict` – body JSON `{"voltage":380,"power":45,"power_factor":0.9}`
