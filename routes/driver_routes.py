from flask import Blueprint, request, jsonify
from models.models import db, DriverApplication, User
from flask_jwt_extended import jwt_required, get_jwt_identity

driver_routes = Blueprint('driver_routes', __name__)

@driver_routes.route('/apply_for_driver', methods=['POST'])
@jwt_required()
def apply_for_driver():
    data = request.get_json()
    current_user = get_jwt_identity()
    print(current_user)
    # user_email = current_user.get('email')
    # print(user_email)
    user = User.query.filter_by(email=current_user).first()
    if not user:
        return jsonify({"message": "User not found"}), 404

    # Check if user already applied
    existing = DriverApplication.query.filter_by(user_id=user.id).first()
    if existing:
        return jsonify({"message": "Application already submitted"}), 400

    new_application = DriverApplication(
        user_id=user.id,
        firstname=data.get('firstname'),
        middlename=data.get('middlename'),
        lastname=data.get('lastname'),
        dob=data.get('dob'),
        aadharno=data.get('aadharno'),
        address=data.get('address'),
        phoneno=data.get('phoneno'),
        email=data.get('email'),
        ambulancenumber=data.get('ambulancenumber'),
        isApproved=False  # default status when applying
    )

    db.session.add(new_application)
    db.session.commit()

    return jsonify({"message": "Application submitted successfully!"}), 201
