@echo off
rem Jalankan dashboard. Buat venv + install dependency otomatis kalau belum ada.
cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" (
    echo [setup] Membuat virtual environment...
    py -m venv .venv || python -m venv .venv
)

".venv\Scripts\python.exe" -m pip install --quiet -r requirements.txt

echo [run] Buka http://localhost:5000
".venv\Scripts\python.exe" app.py
