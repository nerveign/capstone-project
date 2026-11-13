# Random Forest – Klasifikasi Ketidakseimbangan Arus (Panel SDP Line 14)

Alur: data pengukuran → hitung % ketidakseimbangan arus R/S/T → label Y (Seimbang / Tidak Seimbang)
→ fitur X (voltage, power, power_factor) → training Random Forest → klasifikasi → evaluasi
(accuracy, precision, recall, F1-score).

## Struktur
- `config.py` – kolom, fitur, ambang batas ketidakseimbangan
- `generate_sample_data.py` – membuat data contoh sintetis
- `train_model.py` – training + evaluasi, menyimpan model dan metrics
- `app.py` – server Flask (dashboard + API)
- `static/index.html` – dashboard
- `data/sdp_line14.csv` – dataset (ganti dengan data asli)

## Cara menjalankan
```bash
pip install -r requirements.txt
python generate_sample_data.py   # lewati jika sudah punya data asli
python train_model.py
python app.py
```
Buka http://localhost:5000

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
- `GET /api/status` – status model dan metrik
- `POST /api/predict` – body JSON `{"voltage":380,"power":45,"power_factor":0.9}`
