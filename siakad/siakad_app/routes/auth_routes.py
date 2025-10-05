import logging

from flask import Blueprint, jsonify, request
from flask_jwt_extended import create_access_token, jwt_required
from siakad_app.extensions import db
from siakad_app.models import Student, Teacher, User
from siakad_app.schemas import LoginSchema, RegisterUserSchema
from siakad_app.utils.decorators import current_user, roles_required
from sqlalchemy.exc import IntegrityError

logger = logging.getLogger(__name__)

auth_bp = Blueprint("auth", __name__)


@auth_bp.post("/login")
def login():
    data = LoginSchema().load(request.get_json() or {})
    user = User.query.filter_by(username=data["username"].strip()).first()
    if not user or not user.check_password(data["password"]):
        return jsonify({"error": "Invalid credentials"}), 401

    claims = {
        "role": user.role,
        "student_id": user.student_id,
        "teacher_id": user.teacher_id,
    }
    token = create_access_token(identity=user.id, additional_claims=claims)
    logger.info(f"User logged in: {user.username} ({user.role})")
    return jsonify({"access_token": token, "user": user.to_dict()})


@auth_bp.post("/register")
@roles_required("ADMIN")
def register():
    try:
        data = RegisterUserSchema().load(request.get_json() or {})

        if User.query.filter_by(username=data["username"].strip()).first():
            return jsonify({"error": "Username already exists"}), 409

        # Validate links
        if data.get("student_id"):
            if not db.session.get(Student, data["student_id"]):
                return jsonify({"error": "student_id tidak ditemukan"}), 400
        if data.get("teacher_id"):
            if not db.session.get(Teacher, data["teacher_id"]):
                return jsonify({"error": "teacher_id tidak ditemukan"}), 400

        user = User(
            username=data["username"],
            role=data["role"],
            student_id=data.get("student_id"),
            teacher_id=data.get("teacher_id"),
        )
        user.set_password(data["password"])
        db.session.add(user)
        db.session.commit()

        logger.info(f"User registered: {user.username} ({user.role})")
        return jsonify(user.to_dict()), 201
    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "Integrity error creating user"}), 409


@auth_bp.get("/me")
@jwt_required()
def me():
    user = current_user()
    if not user:
        return jsonify({"error": "Unauthorized"}), 401

    data = user.to_dict()
    if user.role == "STUDENT" and user.student:
        data["student"] = user.student.to_dict()
    if user.role == "TEACHER" and user.teacher:
        data["teacher"] = user.teacher.to_dict(include_subjects=False)
    return jsonify(data)
