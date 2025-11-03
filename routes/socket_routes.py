from flask_socketio import SocketIO
import time
import numpy as np
import pandas as pd
from models.models import Signal
import paho.mqtt.client as mqtt
import json
import math

socketio = SocketIO(cors_allowed_origins="*")

# --------------------------------------
# MQTT Setup
# --------------------------------------
BROKER = "broker.hivemq.com"
PORT = 1883
mqtt_client = mqtt.Client()
mqtt_client.connect(BROKER, PORT, 60)

# --------------------------------------
# Globals
# --------------------------------------
signal_df = None
is_city_loaded = False
is_active = False
current_city = None
active_signals = set()
last_nearest_signal = None
last_lat = None
last_lon = None
first_fix = True   # ✅ Used to skip first coord for direction

# --------------------------------------
# Helpers
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

def get_bearing(lat1, lon1, lat2, lon2):
    φ1, φ2 = math.radians(lat1), math.radians(lat2)
    Δλ = math.radians(lon2 - lon1)
    y = math.sin(Δλ) * math.cos(φ2)
    x = math.cos(φ1) * math.sin(φ2) - math.sin(φ1) * math.cos(φ2) * math.cos(Δλ)
    θ = math.atan2(y, x)
    return (math.degrees(θ) + 360) % 360

def get_compass_direction(bearing):
    if bearing >= 315 or bearing < 45:
        return "NORTH"
    elif 45 <= bearing < 135:
        return "EAST"
    elif 135 <= bearing < 225:
        return "SOUTH"
    elif 225 <= bearing < 315:
        return "WEST"
    else:
        return "UNKNOWN"

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
    global signal_df, is_city_loaded, is_active, current_city
    global active_signals, last_nearest_signal, last_lat, last_lon, first_fix

    lat = data.get("x")
    lon = data.get("y")
    city = data.get("city")
    sent_time = data.get("sent_time")
    acc = data.get("acc")

    now = time.time()
    delay_ms = int((now - sent_time) * 1000)
    print(f"\n📍 {city} ({lat}, {lon}) | Acc: {acc}m | Delay: {delay_ms} ms")

    # Step 1️⃣: Load signals for the city
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
            "signal_topic": s.topic
        } for s in signals])
        current_city = city
        is_city_loaded = True
        is_active = True
        print(f"✅ Loaded {len(signal_df)} signals for {city}")

    if not is_active:
        return

    # Step 2️⃣: Compute direction
    if last_lat is not None and last_lon is not None:
        bearing = get_bearing(last_lat, last_lon, lat, lon)
        direction = get_compass_direction(bearing)
    else:
        direction = "INITIAL"

    # Update last position
    last_lat, last_lon = lat, lon

    # Skip alert on very first fix
    if first_fix:
        print("🧭 First coordinate received — waiting for next to determine direction.")
        first_fix = False
        return

    # Step 3️⃣: Nearest signal
    signal_df = calculate_distances(lat, lon, signal_df)
    nearest = signal_df.iloc[0]
    nearest_name = nearest["signal_name"]
    nearest_dist_km = nearest["distance_km"]

    # Step 4️⃣: Publish MQTT if close
    PRE_ALERT_DIST_KM = 0.5
    if nearest_dist_km <= PRE_ALERT_DIST_KM and nearest_name not in active_signals:
        print(f"🚨 ALERT: Ambulance approaching {nearest_name} | Distance: {nearest_dist_km*1000:.0f} m | Direction: {direction}")
        active_signals.add(nearest_name)
        last_nearest_signal = nearest_name

        payload = {
            "signal_topic": nearest["signal_topic"],
            "distKM": round(float(nearest_dist_km), 3),
            "direction": direction,
            "state": "approaching",
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        }

        topic = f"traffic/{nearest['signal_topic']}"
        mqtt_client.publish(topic, json.dumps(payload))
        print(f"📤 Published to MQTT topic '{topic}': {payload}")

    # Step 5️⃣: Reset after passing
    if last_nearest_signal and nearest_name == last_nearest_signal and nearest_dist_km > PRE_ALERT_DIST_KM:
        print(f"✅ Passed {last_nearest_signal}. Recomputing nearby signals list...")
        last_nearest_signal = None
        active_signals.clear()

    # Step 6️⃣: Log nearest signals
    print("🚦 Top 3 nearest signals:")
    print(signal_df[["signal_name", "distance_km"]].head(3))

    socketio.emit("nearest_signals", {
        "top10": signal_df.head(10)[["signal_name", "lat", "lon", "distance_km"]].to_dict(orient="records")
    })


@socketio.on("reset_city")
def handle_reset():
    global signal_df, is_city_loaded, is_active, current_city
    global active_signals, last_nearest_signal, last_lat, last_lon, first_fix
    signal_df = None
    is_city_loaded = False
    is_active = False
    current_city = None
    active_signals.clear()
    last_nearest_signal = None
    last_lat = None
    last_lon = None
    first_fix = True
    print("🔁 Reset complete — system ready for next session.")