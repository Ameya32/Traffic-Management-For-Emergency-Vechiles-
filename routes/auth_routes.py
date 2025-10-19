from flask import Blueprint, request, jsonify
from models.models import db, User
from flask_bcrypt import Bcrypt
from flask_jwt_extended import (
    create_access_token, jwt_required, get_jwt_identity
)
from datetime import timedelta

bcrypt = Bcrypt()
auth_routes = Blueprint('auth_routes', __name__)

# ========================= REGISTER =========================
@auth_routes.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    role = data.get('role', 'user')  # default = user

    # Check if user already exists
    existing_user = User.query.filter_by(email=email).first()
    if existing_user:
        return jsonify({"message": "Email already registered"}), 400

    # Hash password before saving
    hashed_pw = bcrypt.generate_password_hash(password).decode('utf-8')
    new_user = User(email=email, password=hashed_pw, role=role)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({"message": "User registered successfully!"}), 201


# ========================= LOGIN =========================
@auth_routes.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    user = User.query.filter_by(email=email).first()

    if not user or not bcrypt.check_password_hash(user.password, password):
        return jsonify({"message": "Invalid credentials"}), 401

    # Create JWT token valid for 1 hour
    access_token = create_access_token(
        identity={'email': user.email, 'role': user.role},
        expires_delta=timedelta(hours=2)
    )

    return jsonify({
        "message": "Login successful",
        "token": access_token,
        "role": user.role
    }), 200
