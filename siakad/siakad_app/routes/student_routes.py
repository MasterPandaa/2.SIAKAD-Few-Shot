import logging
from datetime import date

from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required
from siakad_app.extensions import db
from siakad_app.models import Student
from siakad_app.schemas import StudentSchema
from siakad_app.utils.decorators import current_user, roles_required
from sqlalchemy import or_
from sqlalchemy.exc import IntegrityError

logger = logging.getLogger(__name__)

student_bp = Blueprint("students", __name__)


@student_bp.get("/")
@roles_required("ADMIN", "TEACHER")
def list_students():
    q = (request.args.get("q") or "").strip()
    class_name = (request.args.get("class_name") or "").strip()
    page = int(request.args.get("page", 1))
    per_page = min(int(request.args.get("per_page", 20)), 100)

    query = Student.query
    if q:
        like = f"%{q}%"
        query = query.filter(
            or_(Student.name.ilike(like), Student.nis.ilike(like)))
    if class_name:
        query = query.filter(Student.class_name == class_name)

    pagination = query.order_by(Student.name.asc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    return jsonify(
        {
            "items": [s.to_dict() for s in pagination.items],
            "total": pagination.total,
            "page": pagination.page,
            "pages": pagination.pages,
        }
    )


@student_bp.get("/me")
@roles_required("STUDENT")
def get_my_profile():
    user = current_user()
    if not user or not user.student:
        return jsonify({"error": "Student profile not found"}), 404
    return jsonify(user.student.to_dict())


@student_bp.post("/")
@roles_required("ADMIN")
def create_student():
    try:
        payload = StudentSchema().load(request.get_json() or {})
        student = Student(
            nis=payload["nis"],
            name=payload["name"],
            birth_date=payload["birth_date"],
            address=payload.get("address") or "",
            gender=payload["gender"],
            parent_phone=payload.get("parent_phone") or "",
            class_name=payload["class_name"],
        )
        db.session.add(student)
        db.session.commit()
        logger.info(f"Student created: {student.nis}")
        return jsonify(student.to_dict()), 201
    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "NIS already exists"}), 409
    except ValueError as e:
        return jsonify({"error": str(e)}), 400


@student_bp.get("/<int:student_id>")
@roles_required("ADMIN", "TEACHER", "STUDENT")
def get_student(student_id: int):
    s = db.session.get(Student, student_id)
    if not s:
        return jsonify({"error": "Not found"}), 404

    user = current_user()
    if user.role == "STUDENT" and (not user.student_id or user.student_id != s.id):
        return jsonify({"error": "Forbidden"}), 403

    return jsonify(s.to_dict())


@student_bp.put("/<int:student_id>")
@student_bp.patch("/<int:student_id>")
@roles_required("ADMIN")
def update_student(student_id: int):
    s = db.session.get(Student, student_id)
    if not s:
        return jsonify({"error": "Not found"}), 404

    data = request.get_json() or {}
    try:
        # partial validation
        if "nis" in data:
            s.nis = Student._validate_nis(data["nis"])
        if "name" in data:
            s.name = Student._validate_name(data["name"])
        if "birth_date" in data:
            if isinstance(data["birth_date"], str):
                s.birth_date = date.fromisoformat(data["birth_date"])
            else:
                s.birth_date = data["birth_date"]
        if "address" in data:
            s.address = (data.get("address") or "").strip()
        if "gender" in data:
            s.gender = Student._validate_gender(data["gender"])
        if "parent_phone" in data:
            s.parent_phone = Student._validate_phone(data["parent_phone"])
        if "class_name" in data:
            s.class_name = Student._validate_class_name(data["class_name"])
        db.session.commit()
        logger.info(f"Student updated: {s.nis}")
        return jsonify(s.to_dict())
    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "NIS already exists"}), 409
    except ValueError as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400


@student_bp.delete("/<int:student_id>")
@roles_required("ADMIN")
def delete_student(student_id: int):
    s = db.session.get(Student, student_id)
    if not s:
        return jsonify({"error": "Not found"}), 404
    db.session.delete(s)
    db.session.commit()
    logger.info(f"Student deleted: {s.nis}")
    return jsonify({"message": "Deleted"})
