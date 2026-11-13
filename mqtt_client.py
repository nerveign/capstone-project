import json
import os
from pathlib import Path
import requests
import paho.mqtt.client as mqtt
from dotenv import load_dotenv


# =========================================================
# MQTT CONFIGURATION (dibaca dari file .env, lihat .env.example)
# =========================================================

load_dotenv(Path(__file__).resolve().parent / ".env")


def _env_int(name, default):
    raw = os.getenv(name, "").strip()

    if not raw:
        return default

    try:
        return int(raw)
    except ValueError:
        raise SystemExit(f"{name} di .env harus berupa angka, bukan {raw!r}")


MQTT_BROKER = os.getenv("MQTT_BROKER", "").strip() or "localhost"
MQTT_PORT = _env_int("MQTT_PORT", 1883)
MQTT_TOPIC = os.getenv("MQTT_TOPIC", "").strip() or "spm/sdp14/data"
MQTT_USERNAME = os.getenv("MQTT_USERNAME", "").strip()
MQTT_PASSWORD = os.getenv("MQTT_PASSWORD", "")

FLASK_URL = (
    os.getenv("FLASK_URL", "").strip()
    or "http://127.0.0.1:5000/api/mqtt-data"
)


# =========================================================
# MQTT CALLBACK
# =========================================================

def on_connect(client, userdata, flags, reason_code, properties=None):

    print("====================================")
    print("MQTT CONNECTED")
    print("Broker :", MQTT_BROKER)
    print("Topic  :", MQTT_TOPIC)
    print("Reason :", reason_code)

    result, mid = client.subscribe(MQTT_TOPIC, qos=1)

    if result == mqtt.MQTT_ERR_SUCCESS:
        print("SUBSCRIBE BERHASIL")
    else:
        print("SUBSCRIBE GAGAL")
        print("Error :", result)

    print("====================================")


def on_message(client, userdata, msg):

    try:

        # =================================================
        # AMBIL PAYLOAD MQTT
        # =================================================

        payload = msg.payload.decode("utf-8")

        print()
        print("====================================")
        print("DATA MQTT DITERIMA")
        print("Topic :", msg.topic)
        print("Payload :", payload)

        # =================================================
        # PARSE JSON
        # =================================================

        data = json.loads(payload)

        if not isinstance(data, dict):
            print("ERROR: Payload bukan JSON object")
            return

        print("Data :", data)

        # =================================================
        # KIRIM DATA KE FLASK
        # =================================================

        response = requests.post(
            FLASK_URL,
            json=data,
            timeout=5
        )

        # =================================================
        # CEK RESPONSE FLASK
        # =================================================

        if response.ok:

            print("DATA BERHASIL DIKIRIM KE FLASK")
            print("Status :", response.status_code)

        else:

            print("FLASK ERROR")
            print("Status :", response.status_code)
            print("Response :", response.text)

        print("====================================")

    except json.JSONDecodeError:

        print("ERROR: Payload MQTT bukan JSON valid")

    except requests.exceptions.RequestException as error:

        print("ERROR KONEKSI KE FLASK:", error)

    except Exception as error:

        print("MQTT DATA ERROR:", error)


# =========================================================
# CREATE MQTT CLIENT
# =========================================================

client = mqtt.Client(
    mqtt.CallbackAPIVersion.VERSION2,
    client_id="SPM-Flask-Backend"
)

client.on_connect = on_connect
client.on_message = on_message

if MQTT_USERNAME:
    client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD or None)


# =========================================================
# CONNECT TO MQTT BROKER
# =========================================================

print("Menghubungkan ke MQTT Broker...")

client.connect(
    MQTT_BROKER,
    MQTT_PORT,
    60
)


# =========================================================
# MQTT LOOP
# =========================================================

client.loop_forever()