from flask import Flask, render_template, jsonify, request
import requests
import time
import os
from pathlib import Path

from dotenv import load_dotenv

from classification import bp as classification_bp

# Baca variabel rahasia dari file .env (lihat .env.example)
load_dotenv(Path(__file__).resolve().parent / ".env")

app = Flask(__name__)

# API Load Classification (Random Forest): /api/classification/*
app.register_blueprint(classification_bp)


# =========================================================
# GOOGLE APPS SCRIPT CONFIGURATION
# =========================================================

GAS_URL = os.getenv("GAS_URL", "")

GAS_API_KEY = os.getenv("GAS_API_KEY", "")

if not GAS_URL or not GAS_API_KEY:
    print("PERINGATAN: GAS_URL / GAS_API_KEY belum diisi di .env, "
          "penyimpanan ke Google Sheets akan gagal.")


# =========================================================
# SYSTEM CONFIGURATION
# =========================================================

# ESP32/Gateway mengirim data setiap 10 detik
SAMPLING_INTERVAL = 10

# Batas status komunikasi berdasarkan umur paket terakhir (detik)
CONNECTION_LOST_TIMEOUT = 20
OFFLINE_TIMEOUT = 60

# Jadwal shift belum ditentukan dari data sistem
SHIFT_LABEL = "N/A"


# =========================================================
# DATA TERBARU
# =========================================================

latest_data = {

    "timestamp": "03 Sep 2026 14:32:16",

    # =========================
    # PHASE R
    # =========================

    "voltage_r": 221.2,
    "current_r": 12.3,
    "power_r": 2740,

    "energy_r_kwh": 125.4,
    "energy_r_wh": 125400,

    "frequency_r": 50.0,
    "pf_r": 0.95,
    "valid_r": True,

    # =========================
    # PHASE S
    # =========================

    "voltage_s": 220.8,
    "current_s": 11.8,
    "power_s": 2610,

    "energy_s_kwh": 124.8,
    "energy_s_wh": 124800,

    "frequency_s": 50.0,
    "pf_s": 0.94,
    "valid_s": True,

    # =========================
    # PHASE T
    # =========================

    "voltage_t": 221.0,
    "current_t": 12.0,
    "power_t": 2650,

    "energy_t_kwh": 125.1,
    "energy_t_wh": 125100,

    "frequency_t": 50.0,
    "pf_t": 0.96,
    "valid_t": True,

    # =========================
    # TOTAL
    # =========================

    "total_power": 8000,

    # =========================
    # DERIVED / DASHBOARD
    # (dihitung dari paket MQTT, lihat build_dashboard_fields)
    # =========================

    "sampling_interval": SAMPLING_INTERVAL,
    "last_packet": "--",
    "load_state": "Idle",
    "shift": SHIFT_LABEL,
    "system_status": "Waiting"
}


# =========================================================
# COMMUNICATION STATE
# =========================================================

# Waktu lokal Flask menerima paket MQTT terakhir.
# Berbeda dari timestamp yang dikirim ESP32.
last_data_received_monotonic = None


def get_connection_status():
    """
    Menentukan status komunikasi berdasarkan umur paket MQTT
    terakhir yang diterima Flask. Dihitung saat dashboard meminta
    data, jadi bisa berubah ke Connection Lost / Offline walaupun
    tidak ada paket baru.
    """

    if last_data_received_monotonic is None:
        return {
            "operation_status": "Waiting",
            "device_status": "Offline"
        }

    age = time.monotonic() - last_data_received_monotonic

    if age <= CONNECTION_LOST_TIMEOUT:
        return {
            "operation_status": "Monitoring",
            "device_status": "Online"
        }

    if age <= OFFLINE_TIMEOUT:
        return {
            "operation_status": "Connection Lost",
            "device_status": "Connection Lost"
        }

    return {
        "operation_status": "Offline",
        "device_status": "Offline"
    }


def to_float(value, default=0.0):
    """Ubah ke float; nilai kosong/tidak valid jadi default."""

    try:
        return float(value or 0)
    except (TypeError, ValueError):
        return default


def build_dashboard_fields(data):
    """Hitung field turunan dashboard dari satu paket data MQTT."""

    # Last Packet: jam dari timestamp, mis. "03 Sep 2026 14:32:16" -> "14:32:16"
    timestamp = str(data.get("timestamp") or "")
    parts = timestamp.split()

    if not timestamp:
        last_packet = "--"
    elif len(parts) >= 4:
        last_packet = parts[-1]
    else:
        last_packet = timestamp

    # Load State: Idle jika tidak ada daya terpakai
    load_state = "Idle" if to_float(data.get("total_power")) <= 0 else "Active"

    # System Status: Normal jika minimal satu fasa valid
    any_phase_valid = any(
        bool(data.get(f"valid_{phase}", False))
        for phase in ("r", "s", "t")
    )

    return {
        "sampling_interval": SAMPLING_INTERVAL,
        "last_packet": last_packet,
        "load_state": load_state,
        "shift": SHIFT_LABEL,
        "system_status": "Normal" if any_phase_valid else "Data Error"
    }


# =========================================================
# GOOGLE SHEETS INTERVAL
# =========================================================

GOOGLE_SHEET_INTERVAL = 180  # 3 menit = 180 detik

# Waktu terakhir data berhasil dikirim ke Google Sheets
last_google_sheet_send = 0

# =========================================================
# POWER HISTORY
# =========================================================

power_history = [
    {"time": "14:17", "value": 45},
    {"time": "14:20", "value": 52},
    {"time": "14:23", "value": 58},
    {"time": "14:26", "value": 55},
    {"time": "14:29", "value": 63},
    {"time": "14:32", "value": 48}
]


# =========================================================
# LOAD PROFILE
# =========================================================

load_profile = [
    {"time": "00:00", "value": 12},
    {"time": "04:00", "value": 17},
    {"time": "08:00", "value": 45},
    {"time": "12:00", "value": 82},
    {"time": "16:00", "value": 78},
    {"time": "20:00", "value": 43},
    {"time": "24:00", "value": 18}
]


# =========================================================
# SYSTEM EVENTS
# =========================================================

system_events = [
    {
        "time": "27 Okt 2026 14:22",
        "message": "Over Current",
        "severity": "Warning"
    }
]


# =========================================================
# AI ANALYTICS STATUS
# =========================================================

ai_status = {

    "system_status": "Ready",

    "anomaly_detection": {
        "status": "Waiting Model",
        "model": None
    },

    "load_prediction": {
        "status": "Waiting Model",
        "model": None
    },

    "energy_forecast": {
        "status": "Waiting Model",
        "model": None
    }

}


# =========================================================
# ENERGY SUMMARY
# =========================================================

energy_summary = {

    "energy": 125.48,
    "active_power": 8.62,
    "power_factor": 0.92,
    "frequency": 49.98

}


# =========================================================
# SEND DATA TO GOOGLE APPS SCRIPT
# =========================================================

def send_to_google_sheet(data):

    payload = {

        "api_key": GAS_API_KEY,

        "timestamp":
            data.get("timestamp", ""),


        # =================================================
        # PHASE R
        # =================================================

        "voltage_r":
            data.get("voltage_r", 0),

        "current_r":
            data.get("current_r", 0),

        "power_r":
            data.get("power_r", 0),

        "energy_r_kwh":
            data.get("energy_r_kwh", 0),

        "energy_r_wh":
            data.get("energy_r_wh", 0),

        "frequency_r":
            data.get("frequency_r", 0),

        "pf_r":
            data.get("pf_r", 0),

        "valid_r":
            data.get("valid_r", False),


        # =================================================
        # PHASE S
        # =================================================

        "voltage_s":
            data.get("voltage_s", 0),

        "current_s":
            data.get("current_s", 0),

        "power_s":
            data.get("power_s", 0),

        "energy_s_kwh":
            data.get("energy_s_kwh", 0),

        "energy_s_wh":
            data.get("energy_s_wh", 0),

        "frequency_s":
            data.get("frequency_s", 0),

        "pf_s":
            data.get("pf_s", 0),

        "valid_s":
            data.get("valid_s", False),


        # =================================================
        # PHASE T
        # =================================================

        "voltage_t":
            data.get("voltage_t", 0),

        "current_t":
            data.get("current_t", 0),

        "power_t":
            data.get("power_t", 0),

        "energy_t_kwh":
            data.get("energy_t_kwh", 0),

        "energy_t_wh":
            data.get("energy_t_wh", 0),

        "frequency_t":
            data.get("frequency_t", 0),

        "pf_t":
            data.get("pf_t", 0),

        "valid_t":
            data.get("valid_t", False),


        # =================================================
        # TOTAL POWER
        # =================================================

        "total_power":
            data.get("total_power", 0)

    }


    try:

        response = requests.post(

            GAS_URL,

            json=payload,

            timeout=10

        )


        print("====================================")
        print("GOOGLE SHEETS RESPONSE")
        print("Status  :", response.status_code)
        print("Response:", response.text)
        print("====================================")


        if not response.ok:

            return False


        # Coba membaca response JSON
        try:

            result = response.json()

            return (
                result.get("status")
                == "success"
            )

        except ValueError:

            return False


    except requests.RequestException as error:

        print(
            "GOOGLE SHEETS ERROR:",
            error
        )

        return False


# =========================================================
# DASHBOARD
# =========================================================

@app.route("/")
def home():

    return render_template(
        "index.html"
    )


# =========================================================
# API: LATEST DATA
# =========================================================

@app.route("/api/latest")
def get_latest_data():

    # operation_status & device_status dihitung saat diminta,
    # supaya ikut berubah bila paket MQTT berhenti datang.
    return jsonify({

        **latest_data,

        **get_connection_status(),

        "power_history":
            power_history,

        "load_profile":
            load_profile,

        "ai_status":
            ai_status,

        "events":
            system_events,

        "energy_summary":
            energy_summary

    })

# =========================================================
# API: MQTT DATA RECEIVER
# =========================================================

@app.route("/api/mqtt-data", methods=["POST"])
def receive_mqtt_data():

    global latest_data
    global last_google_sheet_send
    global last_data_received_monotonic  # tanpa ini, yang terisi hanya variabel lokal

    # =====================================================
    # AMBIL DATA MQTT
    # =====================================================

    data = request.get_json(silent=True)

    # =====================================================
    # CHECK DATA
    # =====================================================

    if not data:

        return jsonify({
            "status": "error",
            "message": "Data MQTT kosong"
        }), 400


    # =====================================================
    # UPDATE REALTIME DATA
    # =====================================================

    latest_data.update(data)

    # Catat kapan Flask menerima paket (untuk status Online/Offline)
    last_data_received_monotonic = time.monotonic()

    # Hitung field turunan: sampling interval, last packet,
    # load state, shift, system status
    latest_data.update(build_dashboard_fields(data))


    print("====================================")
    print("DATA MQTT MASUK KE FLASK")
    print(data)
    print("====================================")


    # =====================================================
    # GOOGLE SHEETS TIMER
    # =====================================================

    current_time = time.monotonic()

    elapsed_time = (
        current_time - last_google_sheet_send
    )


    # =====================================================
    # CEK APAKAH SUDAH 3 MENIT
    # =====================================================

    if (
        last_google_sheet_send == 0
        or
        elapsed_time >= GOOGLE_SHEET_INTERVAL
    ):

        print("====================================")
        print("GOOGLE SHEETS")
        print("STATUS : WAKTUNYA SIMPAN")
        print("Mengirim data ke Google Sheets...")
        print("====================================")


        # =================================================
        # KIRIM KE GOOGLE SHEETS
        # =================================================

        google_ok = send_to_google_sheet(data)


        # =================================================
        # JIKA BERHASIL
        # =================================================

        if google_ok:

            last_google_sheet_send = current_time

            print("====================================")
            print("GOOGLE SHEETS")
            print("STATUS : SUCCESS")
            print("Data berhasil disimpan")
            print("Next save : 3 menit lagi")
            print("====================================")


            return jsonify({

                "status": "success",

                "message":
                    "Data MQTT diterima Flask "
                    "dan disimpan ke Google Sheets",

                "google_sheet":
                    "success",

                "next_save_seconds":
                    GOOGLE_SHEET_INTERVAL

            }), 200


        # =================================================
        # JIKA GOOGLE SHEETS GAGAL
        # =================================================

        else:

            print("====================================")
            print("GOOGLE SHEETS")
            print("STATUS : FAILED")
            print("Data realtime tetap berjalan")
            print("Akan mencoba lagi pada data berikutnya")
            print("====================================")


            return jsonify({

                "status": "warning",

                "message":
                    "Data MQTT diterima Flask "
                    "tetapi gagal disimpan ke Google Sheets",

                "google_sheet":
                    "failed"

            }), 502


    # =====================================================
    # BELUM 3 MENIT
    # =====================================================

    else:

        remaining_time = (
            GOOGLE_SHEET_INTERVAL - elapsed_time
        )

        remaining_seconds = max(
            0,
            int(remaining_time)
        )


        print("====================================")
        print("GOOGLE SHEETS")
        print("STATUS : SKIP")
        print(
            "Belum waktunya menyimpan ke Google Sheets"
        )
        print(
            "Next save sekitar",
            remaining_seconds,
            "detik lagi"
        )
        print("====================================")


        # =================================================
        # PENTING:
        # Tetap return 200 karena MQTT/Flask BERHASIL
        # =================================================

        return jsonify({

            "status": "success",

            "message":
                "Data MQTT diterima Flask "
                "dan dashboard diperbarui",

            "google_sheet":
                "skipped",

            "next_save_seconds":
                remaining_seconds

        }), 200


# =========================================================
# API: HISTORICAL DATA
# =========================================================

@app.route("/api/history")
def get_history():

    return jsonify({

        "data":
            power_history

    })


# =========================================================
# API: SYSTEM EVENTS
# =========================================================

@app.route("/api/events")
def get_events():

    return jsonify({

        "events":
            system_events

    })


# =========================================================
# API: AI STATUS
# =========================================================

@app.route("/api/ai-status")
@app.route("/api/ai_status")
def get_ai_status():

    return jsonify(
        ai_status
    )


# =========================================================
# API: ENERGY SUMMARY
# =========================================================

@app.route("/api/energy-summary")
def get_energy_summary():

    return jsonify(
        energy_summary
    )


# =========================================================
# API: SYSTEM HEALTH
# =========================================================

@app.route("/api/health")
def health():

    connection_status = get_connection_status()

    return jsonify({

        "status":
            "online",

        "backend":
            "Flask",

        "device":
            connection_status["device_status"],

        "operation_status":
            connection_status["operation_status"]

    })


# =========================================================
# API: TEST
# =========================================================

@app.route("/api/test")
def test_api():

    return jsonify({

        "message":
            "API Flask aktif",

        "status":
            "OK"

    })


# =========================================================
# AI ANALYTICS PAGES
# =========================================================

@app.route("/anomaly")
def anomaly():

    return render_template(
        "anomaly.html"
    )


@app.route("/prediction")
def prediction():

    return render_template(
        "prediction.html"
    )


@app.route("/classification")
def classification():

    return render_template(
        "classification.html"
    )


# =========================================================
# RUN SERVER
# =========================================================

if __name__ == "__main__":

    app.run(

        host="0.0.0.0",

        port=5000,

        debug=True

    )