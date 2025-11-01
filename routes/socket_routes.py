# routes/socket_routes.py
from flask_socketio import SocketIO
import time

# ✅ Create a single socketio instance (initialized later in app.py)
socketio = SocketIO(cors_allowed_origins="*")

# WebSocket Event Handlers
@socketio.on("connect")
def handle_connect():
    print("✅ Client connected")

@socketio.on("disconnect")
def handle_disconnect():
    print("❌ Client disconnected")

@socketio.on("send_coords")
def handle_coords(data):
    x = data.get("x")
    y = data.get("y")
    city=data.get('city')
    sent_time = data.get("sent_time")
    acc = data.get("acc")

    now = time.time()
    delay_ms = int((now - sent_time) * 1000)
    print(f"📍 Received {acc} {city} ({x}, {y}) at {time.strftime('%H:%M:%S')} | Delay: {delay_ms} ms")

    # Optionally send back delay
    socketio.emit("coords_received", {"x": x, "y": y, "delay_ms": delay_ms})
