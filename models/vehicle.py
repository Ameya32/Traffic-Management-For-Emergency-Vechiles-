from app import db

class Vehicle(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    vehicle_no = db.Column(db.String(20), unique=True)
    driver_name = db.Column(db.String(50))
    approved = db.Column(db.Boolean, default=False)
