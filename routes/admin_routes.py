from flask import Blueprint, jsonify
from models.models import db, DriverApplication, User
from flask_jwt_extended import jwt_required, get_jwt_identity

admin_routes = Blueprint('admin_routes', __name__)

# ========================= GET ALL PENDING DRIVER APPLICATIONS =========================
@admin_routes.route('/pending_applications', methods=['GET'])
@jwt_required()
def get_pending_applications():
    current_user = get_jwt_identity()
    user_email = current_user

    # ✅ Check if admin
    user = User.query.filter_by(email=user_email).first()
    if not user:
        return jsonify({"message": "User not found"}), 404

    if user.role.lower() != "admin":
        return jsonify({"message": "Access denied. Admins only."}), 403

    pending_apps = DriverApplication.query.filter_by(isApproved=False).all()
    if not pending_apps:
        return jsonify({"message": "No pending applications"}), 200

    applications_list = [
        {
            "id": app.id,
            "user_id": app.user_id,
            "firstname": app.firstname,
            "middlename": app.middlename,
            "lastname": app.lastname,
            "dob": app.dob,
            "aadharno": app.aadharno,
            "address": app.address,
            "phoneno": app.phoneno,
            "email": app.email,
            "ambulancenumber": app.ambulancenumber,
            "isApproved": app.isApproved
        }
        for app in pending_apps
    ]

    return jsonify(applications_list), 200


# ========================= GET SINGLE PENDING APPLICATION BY USER ID =========================
@admin_routes.route('/pending_applications/<int:user_id>', methods=['GET'])
@jwt_required()
def get_pending_application_by_user(user_id):
    current_user = get_jwt_identity()
    user_email = current_user

    # ✅ Check if admin
    user = User.query.filter_by(email=user_email).first()
    if not user:
        return jsonify({"message": "User not found"}), 404

    if user.role.lower() != "admin":
        return jsonify({"message": "Access denied. Admins only."}), 403

    # ✅ Fetch single application
    app = DriverApplication.query.filter_by(user_id=user_id, isApproved=False).first()

    if not app:
        return jsonify({"message": "No pending application found for this user"}), 404

    application_data = {
        "id": app.id,
        "user_id": app.user_id,
        "firstname": app.firstname,
        "middlename": app.middlename,
        "lastname": app.lastname,
        "dob": app.dob,
        "aadharno": app.aadharno,
        "address": app.address,
        "phoneno": app.phoneno,
        "email": app.email,
        "ambulancenumber": app.ambulancenumber,
        "isApproved": app.isApproved
    }

    return jsonify(application_data), 200

# ========================= APPROVE DRIVER APPLICATION =========================
@admin_routes.route('/approve_application/<int:user_id>', methods=['POST'])
@jwt_required()
def approve_driver_application(user_id):
    current_user = get_jwt_identity()
    user_email = current_user

    # ✅ Check admin
    user = User.query.filter_by(email=user_email).first()
    if not user:
        return jsonify({"message": "User not found"}), 404
    if user.role.lower() != "admin":
        return jsonify({"message": "Access denied. Admins only."}), 403

    # ✅ Find application
    app = DriverApplication.query.filter_by(user_id=user_id, isApproved=False).first()
    if not app:
        return jsonify({"message": "No pending application found for this user"}), 404

    # ✅ Approve it
    app.isApproved = True
    db.session.commit()

    return jsonify({"message": f"Application for user_id {user_id} approved successfully"}), 200
