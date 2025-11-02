from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='user')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class DriverApplication(db.Model):
    __tablename__ = 'driver_application'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)  # ✅ fixed here

    firstname = db.Column(db.String(50), nullable=False)
    middlename = db.Column(db.String(50))
    lastname = db.Column(db.String(50), nullable=False)
    dob = db.Column(db.String(20), nullable=False)
    aadharno = db.Column(db.String(20), unique=True, nullable=False)
    address = db.Column(db.String(255), nullable=False)
    phoneno = db.Column(db.String(15), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    ambulancenumber = db.Column(db.String(50), nullable=False)

    # ✅ new field
    isApproved = db.Column(db.Boolean, default=False, nullable=False)

    user = db.relationship('User', backref=db.backref('applications', lazy=True))

# class Signal(db.Model):
#     __tablename__ = 'signals'

#     id = db.Column(db.Integer, primary_key=True, autoincrement=True)
#     name = db.Column(db.String(100), nullable=True)
#     latitude = db.Column(db.Float, nullable=False)
#     longitude = db.Column(db.Float, nullable=False)
#     topic = db.Column(db.String(100))
#     city = db.Column(db.String(100), nullable=False)

#     def __repr__(self):
#         return f"<Signal {self.name} ({self.city})>"
    
class Signal(db.Model):
    __tablename__ = "signals"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    topic = db.Column(db.String(100), nullable=False)
    city = db.Column(db.String(50), nullable=False)
