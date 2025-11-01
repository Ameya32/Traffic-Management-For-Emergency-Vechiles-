from flask import Blueprint, request, jsonify
from models.models import db, DriverApplication, User
from flask_jwt_extended import jwt_required, get_jwt_identity,get_jwt

driver_routes = Blueprint('driver_routes', __name__)

@driver_routes.route('/apply_for_driver', methods=['POST'])
@jwt_required()
def apply_for_driver():
    data = request.get_json()
    current_user_email_identity = get_jwt_identity()
    claims = get_jwt()   
    print(current_user_email_identity)
    user_id_from_token = claims.get('user_id')
    print(user_id_from_token)
    user = User.query.filter_by(email=current_user_email_identity).first()
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

@driver_routes.route('/is_approved_by_admin', methods=['GET'])
@jwt_required()
def is_approved_by_admin():
    # ✅ Extract both identity (email) and claims (user_id)
    current_user_email_identity = get_jwt_identity()
    claims = get_jwt()
    user_id_from_token = claims.get('user_id')

    # ✅ Fetch user from DB
    user = User.query.filter_by(email=current_user_email_identity).first()
    if not user:
        return jsonify({"message": "User not found"}), 404

    # ✅ Verify user role
    if user.role.lower() != "ambulance":
        return jsonify({"message": "Access denied. Only ambulance drivers allowed."}), 403

    # ✅ Fetch their driver application
    application = DriverApplication.query.filter_by(user_id=user_id_from_token).first()
    if not application:
        return jsonify({"approved": False, "message": "No application found"}), 200

    # ✅ Return approval status
    if application.isApproved:
        return jsonify({"approved": True, "message": "Application approved by admin"}), 200
    else:
        return jsonify({"approved": False, "message": "Application not approved yet"}), 200