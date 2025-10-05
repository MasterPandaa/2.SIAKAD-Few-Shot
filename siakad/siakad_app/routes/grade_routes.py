import logging
from flask import Blueprint, request, jsonify, render_template
from flask_jwt_extended import jwt_required
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError

from siakad_app.extensions import db
from siakad_app.models import Grade, Student, Subject
from siakad_app.schemas import GradeSchema
from siakad_app.utils.decorators import roles_required, current_user

logger = logging.getLogger(__name__)

grade_bp = Blueprint('grades', __name__)


def _teacher_can_access_subject(user, subject_id: int) -> bool:
    if user.role == 'ADMIN':
        return True
    if user.role == 'TEACHER':
        subj = db.session.get(Subject, subject_id)
        return subj is not None and subj.teacher_id == user.teacher_id
    return False


@grade_bp.post('/')
@roles_required('ADMIN', 'TEACHER')
def upsert_grade():
    # Create or update grade for a student-subject pair
    try:
        payload = GradeSchema().load(request.get_json() or {})
        user = current_user()

        if not db.session.get(Student, payload['student_id']):
            return jsonify({'error': 'student_id tidak ditemukan'}), 400
        if not db.session.get(Subject, payload['subject_id']):
            return jsonify({'error': 'subject_id tidak ditemukan'}), 400

        if not _teacher_can_access_subject(user, payload['subject_id']):
            return jsonify({'error': 'Forbidden'}), 403

        grade = Grade.query.filter_by(student_id=payload['student_id'], subject_id=payload['subject_id']).first()
        if grade is None:
            grade = Grade(
                student_id=payload['student_id'],
                subject_id=payload['subject_id'],
                tugas=payload['tugas'], uts=payload['uts'], uas=payload['uas']
            )
            db.session.add(grade)
        else:
            grade.tugas = Grade._score(payload['tugas'])
            grade.uts = Grade._score(payload['uts'])
            grade.uas = Grade._score(payload['uas'])

        db.session.commit()
        logger.info(f"Grade upserted: student={grade.student_id} subject={grade.subject_id}")
        return jsonify(grade.to_dict()), 201
    except IntegrityError:
        db.session.rollback()
        return jsonify({'error': 'Integrity error'}), 409
    except ValueError as e:
        return jsonify({'error': str(e)}), 400


@grade_bp.put('/<int:grade_id>')
@grade_bp.patch('/<int:grade_id>')
@roles_required('ADMIN', 'TEACHER')
def update_grade(grade_id: int):
    g = db.session.get(Grade, grade_id)
    if not g:
        return jsonify({'error': 'Not found'}), 404

    user = current_user()
    if not _teacher_can_access_subject(user, g.subject_id):
        return jsonify({'error': 'Forbidden'}), 403

    data = request.get_json() or {}
    try:
        if 'tugas' in data:
            g.tugas = Grade._score(data['tugas'])
        if 'uts' in data:
            g.uts = Grade._score(data['uts'])
        if 'uas' in data:
            g.uas = Grade._score(data['uas'])
        db.session.commit()
        logger.info(f"Grade updated: id={g.id}")
        return jsonify(g.to_dict())
    except ValueError as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400


@grade_bp.get('/student/<int:student_id>')
@roles_required('ADMIN', 'TEACHER', 'STUDENT')
def list_grades_for_student(student_id: int):
    user = current_user()
    if user.role == 'STUDENT' and user.student_id != student_id:
        return jsonify({'error': 'Forbidden'}), 403

    grades = Grade.query.filter_by(student_id=student_id).all()
    return jsonify([g.to_dict(include_subject=True) for g in grades])


@grade_bp.get('/me')
@roles_required('STUDENT')
def my_grades():
    user = current_user()
    grades = Grade.query.filter_by(student_id=user.student_id).all()
    return jsonify([g.to_dict(include_subject=True) for g in grades])


@grade_bp.get('/subject/<int:subject_id>')
@roles_required('ADMIN', 'TEACHER')
def list_grades_for_subject(subject_id: int):
    user = current_user()
    if not _teacher_can_access_subject(user, subject_id):
        return jsonify({'error': 'Forbidden'}), 403
    grades = Grade.query.filter_by(subject_id=subject_id).all()
    return jsonify([g.to_dict(include_student=True) for g in grades])


@grade_bp.get('/transcript/<int:student_id>')
@roles_required('ADMIN', 'TEACHER', 'STUDENT')
def transcript(student_id: int):
    user = current_user()
    if user.role == 'STUDENT' and user.student_id != student_id:
        return jsonify({'error': 'Forbidden'}), 403

    student = db.session.get(Student, student_id)
    if not student:
        return jsonify({'error': 'Student not found'}), 404

    items = [g.to_dict(include_subject=True) for g in Grade.query.filter_by(student_id=student_id).all()]
    avg = round(sum(i['final'] for i in items) / len(items), 2) if items else 0.0
    return jsonify({'student': student.to_dict(), 'grades': items, 'average': avg})


@grade_bp.get('/class-report')
@roles_required('ADMIN', 'TEACHER')
def class_report():
    class_name = (request.args.get('class_name') or '').strip()
    if not class_name:
        return jsonify({'error': 'class_name is required'}), 400

    # Aggregate grades by student and subject in the class
    students = Student.query.filter_by(class_name=class_name).order_by(Student.name.asc()).all()
    student_ids = [s.id for s in students]

    grades = Grade.query.filter(Grade.student_id.in_(student_ids)).all() if student_ids else []

    # Structure: {student_id: {subject_code: final}}
    subjects = {s.id: s for s in Subject.query.all()}
    subject_codes = {sid: subjects[sid].code for sid in subjects}

    table = {}
    for g in grades:
        table.setdefault(g.student_id, {})[subject_codes.get(g.subject_id, str(g.subject_id))] = g.final_score

    # If HTML requested explicitly
    if 'text/html' in (request.headers.get('Accept') or ''):
        # Build a sorted set of subject codes present
        all_codes = sorted({code for row in table.values() for code in row.keys()})
        return render_template('reports/class_report.html', class_name=class_name, students=students, table=table, subjects=all_codes)

    # JSON response
    return jsonify({
        'class_name': class_name,
        'students': [s.to_dict() for s in students],
        'grades': table,
    })
