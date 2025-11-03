from flask_socketio import SocketIO
import time
import numpy as np
import pandas as pd
from models.models import Signal
import paho.mqtt.client as mqtt
import json

socketio = SocketIO(cors_allowed_origins="*")

# --------------------------------------
# MQTT Setup
# --------------------------------------
BROKER = "broker.hivemq.com"
PORT = 1883

mqtt_client = mqtt.Client()
mqtt_client.connect(BROKER, PORT, 60)

# --------------------------------------
# Global variables
# --------------------------------------
signal_df = None
is_city_loaded = False
is_active = False
current_city = None
active_signals = set()
last_nearest_signal = None

# --------------------------------------
# Helper function: Haversine formula
# --------------------------------------
def calculate_distances(lat, lon, df):
    R = 6371
    lat1, lon1 = np.radians(lat), np.radians(lon)
    lats2, lons2 = np.radians(df["lat"].values), np.radians(df["lon"].values)

    dlat = lats2 - lat1
    dlon = lons2 - lon1

    a = np.sin(dlat / 2) ** 2 + np.cos(lat1) * np.cos(lats2) * np.sin(dlon / 2) ** 2
    c = 2 * np.arcsin(np.sqrt(a))
    df["distance_km"] = R * c
    return df.sort_values(by="distance_km").reset_index(drop=True)

# --------------------------------------
# Socket Events
# --------------------------------------
@socketio.on("connect")
def handle_connect():
    print("✅ Client connected")

@socketio.on("disconnect")
def handle_disconnect():
    print("❌ Client disconnected")

@socketio.on("send_coords")
def handle_coords(data):
    global signal_df, is_city_loaded, is_active, current_city, active_signals, last_nearest_signal

    lat = data.get("x")
    lon = data.get("y")
    city = data.get("city")
    sent_time = data.get("sent_time")
    acc = data.get("acc")
    direction = data.get("direction", "N")  # optional, can be sent from client

    now = time.time()
    delay_ms = int((now - sent_time) * 1000)

    print(f"\n📍 {city} ({lat}, {lon}) | Acc: {acc}m | Delay: {delay_ms} ms")

    # ------------------------------
    # Step 1️⃣ Load city signals once
    # ------------------------------
    if not is_city_loaded:
        print(f"🏙️ Loading signals for city: {city}")
        signals = Signal.query.filter_by(city=city).all()
        if not signals:
            print("⚠️ No signals found for this city.")
            return

        signal_df = pd.DataFrame([{
            "id": s.id,
            "signal_name": s.name,
            "lat": s.latitude,
            "lon": s.longitude,
            "signal_topic": s.topic,  # assuming this field exists
            #"pre_distKm": s.pre_distKm      # optional: pre-alert distance if stored
        } for s in signals])

        current_city = city
        is_city_loaded = True
        is_active = True
        print(f"✅ Loaded {len(signal_df)} signals for {city}")

    if not is_active:
        return

    # ------------------------------
    # Step 2️⃣ Compute nearest signals
    # ------------------------------
    signal_df = calculate_distances(lat, lon, signal_df)
    nearest = signal_df.iloc[0]
    nearest_name = nearest["signal_name"]
    nearest_dist_km = nearest["distance_km"]

    # ------------------------------
    # Step 3️⃣ Dummy alert + MQTT publish
    # ------------------------------
    PRE_ALERT_DIST_KM = 0.5

    if nearest_dist_km <= PRE_ALERT_DIST_KM and nearest_name not in active_signals:
        print(f"📡 DUMMY ALERT: Ambulance approaching {nearest_name} | Distance: {nearest_dist_km*1000:.0f} m")
        active_signals.add(nearest_name)
        last_nearest_signal = nearest_name

        # Prepare MQTT payload
        payload = {
            "signal_topic": nearest["signal_topic"],
            "distKM": round(nearest_dist_km, 3),
            "direction": direction,
            "state": "approaching"
        }

        TOPIC = f"traffic/{nearest["signal_topic"]}"
        print(TOPIC)
        mqtt_client.publish(TOPIC, json.dumps(payload))
        print(f"📤 Published to MQTT: {payload}")

    # Reset if passed
    if last_nearest_signal and nearest_name == last_nearest_signal and nearest_dist_km > PRE_ALERT_DIST_KM:
        print(f"✅ Passed {last_nearest_signal}. Recomputing nearby signals list...")
        last_nearest_signal = None
        active_signals.clear()

    # ------------------------------
    # Step 4️⃣ Log top 3 for monitoring
    # ------------------------------
    print("🚦 Top 3 nearest signals:")
    print(signal_df[["signal_name", "distance_km"]].head(3))

    # Optionally emit to frontend
    socketio.emit("nearest_signals", {
        "top10": signal_df.head(10)[["signal_name", "lat", "lon", "distance_km"]].to_dict(orient="records")
    })


@socketio.on("reset_city")
def handle_reset():
    global signal_df, is_city_loaded, is_active, current_city, active_signals, last_nearest_signal
    signal_df = None
    is_city_loaded = False
    is_active = False
    current_city = None
    active_signals.clear()
    last_nearest_signal = None
    print("🔁 Reset complete — system ready for next session.")