# routes/signal_routes.py
from flask import Blueprint, request, jsonify
from models.models import db, Signal

signal_routes = Blueprint("signal_routes", __name__)

@signal_routes.route("/add", methods=["POST"])
def add_signal():
    """
    Add a new traffic signal to the database.
    Expected JSON:
    {
        "name": "Signal 1",
        "latitude": 18.5204,
        "longitude": 73.8567,
        "topic": "signal/1",
        "city": "Pune"
    }
    """
    try:
        data = request.get_json()

        name = data.get("name")
        latitude = data.get("latitude")
        longitude = data.get("longitude")
        topic = data.get("topic")
        city = data.get("city")

        if not all([name, latitude, longitude, city]):
            return jsonify({"error": "Missing required fields"}), 400

        new_signal = Signal(
            name=name,
            latitude=latitude,
            longitude=longitude,
            topic=topic,
            city=city
        )

        db.session.add(new_signal)
        db.session.commit()

        return jsonify({"message": "Signal added successfully"}), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@signal_routes.route("/all", methods=["GET"])
def get_all_signals():
    """Fetch all signals from the database."""
    signals = Signal.query.all()
    result = [
        {
            "id": s.id,
            "name": s.name,
            "latitude": s.latitude,
            "longitude": s.longitude,
            "topic": s.topic,
            "city": s.city
        }
        for s in signals
    ]
    return jsonify(result), 200