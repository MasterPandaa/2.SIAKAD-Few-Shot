import logging

from flask import Blueprint, jsonify
from siakad_app.extensions import db
from siakad_app.models import Grade, Student, Subject, Teacher
from siakad_app.utils.decorators import roles_required
from sqlalchemy import func

logger = logging.getLogger(__name__)

dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.get("/stats")
@roles_required("ADMIN", "TEACHER")
def stats():
    students = db.session.query(func.count(Student.id)).scalar() or 0
    teachers = db.session.query(func.count(Teacher.id)).scalar() or 0
    subjects = db.session.query(func.count(Subject.id)).scalar() or 0
    return jsonify({"students": students, "teachers": teachers, "subjects": subjects})


@dashboard_bp.get("/avg-by-subject")
@roles_required("ADMIN", "TEACHER")
def avg_by_subject():
    # average of final score = (tugas + uts + uas)/3, aggregated per subject
    rows = (
        db.session.query(
            Subject.code,
            Subject.name,
            func.round(func.avg((Grade.tugas + Grade.uts + Grade.uas) / 3.0), 2).label(
                "avg_final"
            ),
        )
        .join(Grade, Grade.subject_id == Subject.id)
        .group_by(Subject.id)
        .order_by(Subject.name.asc())
        .all()
    )
    return jsonify(
        [
            {
                "code": code,
                "name": name,
                "average": float(avg) if avg is not None else 0.0,
            }
            for code, name, avg in rows
        ]
    )
