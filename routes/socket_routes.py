from flask_socketio import SocketIO
import time
import numpy as np
import pandas as pd
from models.models import Signal  # ✅ Assuming your Signal model exists

socketio = SocketIO(cors_allowed_origins="*")

# --------------------------------------
# Global variables
# --------------------------------------
signal_df = None
is_city_loaded = False
is_active = False
current_city = None


# --------------------------------------
# Helper function: Haversine formula
# --------------------------------------
def calculate_distances(lat, lon, df):
    """Compute distance (in km) between (lat, lon) and all points in df."""
    R = 6371  # Earth radius in km
    lat1, lon1 = np.radians(lat), np.radians(lon)
    lats2, lons2 = np.radians(df["lat"].values), np.radians(df["lon"].values)

    dlat = lats2 - lat1
    dlon = lons2 - lon1

    a = np.sin(dlat / 2) ** 2 + np.cos(lat1) * np.cos(lats2) * np.sin(dlon / 2) ** 2
    c = 2 * np.arcsin(np.sqrt(a))
    df["distance_km"] = R * c
    return df.sort_values(by="distance_km").reset_index(drop=True)


# --------------------------------------
# Socket Event Handlers
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

    lat = data.get("x")
    lon = data.get("y")
    city = data.get("city")
    sent_time = data.get("sent_time")
    acc = data.get("acc")

    now = time.time()
    delay_ms = int((now - sent_time) * 1000)

    print(f"📍 Received {acc} {city} ({lat}, {lon}) | Delay: {delay_ms} ms")

    # --------------------------------------------------
    # 1️⃣ City initialization (only once)
    # --------------------------------------------------
    if not is_city_loaded:
        print(f"🏙️ Loading signals for city: {city}")

        signals = Signal.query.filter_by(city=city).all()

        if not signals:
            print("⚠️ No signals found for this city.")
            return

        data_list = [{
            "id": s.id,
            "lat": s.lat,
            "lon": s.lon,
            "signal_name": s.signal_name
        } for s in signals]

        signal_df = pd.DataFrame(data_list)
        current_city = city
        is_city_loaded = True
        is_active = True
        print(f"✅ Loaded {len(signal_df)} signals for {city}")

    # --------------------------------------------------
    # 2️⃣ Skip if inactive
    # --------------------------------------------------
    if not is_active:
        print("⚠️ System inactive — skipping processing.")
        return

    # --------------------------------------------------
    # 3️⃣ Distance update logic
    # --------------------------------------------------
    if signal_df is not None:
        signal_df = calculate_distances(lat, lon, signal_df)
        top10 = signal_df.head(10)

        print("\n🚑 Top 3 nearest signals:")
        print(top10[["signal_name", "distance_km"]].head(3))

        # Optionally send updated top 10 to frontend
        socketio.emit("nearest_signals", {
            "top10": top10[["signal_name", "lat", "lon", "distance_km"]].to_dict(orient="records")
        })


@socketio.on("reset_city")
def handle_reset():
    """Reset system for new ambulance session."""
    global signal_df, is_city_loaded, current_city, is_active
    signal_df = None
    is_city_loaded = False
    is_active = False
    current_city = None
    print("🔁 Reset complete — system ready for next session.")