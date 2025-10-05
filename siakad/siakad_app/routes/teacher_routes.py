import logging
from flask import Blueprint, request, jsonify
from sqlalchemy.exc import IntegrityError
from sqlalchemy import or_

from siakad_app.extensions import db
from siakad_app.models import Teacher
from siakad_app.schemas import TeacherSchema
from siakad_app.utils.decorators import roles_required, current_user

logger = logging.getLogger(__name__)

teacher_bp = Blueprint('teachers', __name__)


@teacher_bp.get('/')
@roles_required('ADMIN')
def list_teachers():
    q = (request.args.get('q') or '').strip()
    page = int(request.args.get('page', 1))
    per_page = min(int(request.args.get('per_page', 20)), 100)

    query = Teacher.query
    if q:
        like = f"%{q}%"
        query = query.filter(or_(Teacher.name.ilike(like), Teacher.nip.ilike(like)))

    pagination = query.order_by(Teacher.name.asc()).paginate(page=page, per_page=per_page, error_out=False)
    return jsonify({
        'items': [t.to_dict(include_subjects=False) for t in pagination.items],
        'total': pagination.total,
        'page': pagination.page,
        'pages': pagination.pages,
    })


@teacher_bp.get('/me')
@roles_required('TEACHER')
def get_my_profile():
    user = current_user()
    if not user or not user.teacher:
        return jsonify({'error': 'Teacher profile not found'}), 404
    return jsonify(user.teacher.to_dict())


@teacher_bp.post('/')
@roles_required('ADMIN')
def create_teacher():
    try:
        payload = TeacherSchema().load(request.get_json() or {})
        t = Teacher(nip=payload['nip'], name=payload['name'], phone=payload.get('phone'), address=payload.get('address'))
        db.session.add(t)
        db.session.commit()
        logger.info(f"Teacher created: {t.nip}")
        return jsonify(t.to_dict(include_subjects=False)), 201
    except IntegrityError:
        db.session.rollback()
        return jsonify({'error': 'NIP already exists'}), 409
    except ValueError as e:
        return jsonify({'error': str(e)}), 400


@teacher_bp.get('/<int:teacher_id>')
@roles_required('ADMIN', 'TEACHER')
def get_teacher(teacher_id: int):
    t = db.session.get(Teacher, teacher_id)
    if not t:
        return jsonify({'error': 'Not found'}), 404
    user = current_user()
    if user.role == 'TEACHER' and user.teacher_id != t.id:
        return jsonify({'error': 'Forbidden'}), 403
    return jsonify(t.to_dict())


@teacher_bp.put('/<int:teacher_id>')
@teacher_bp.patch('/<int:teacher_id>')
@roles_required('ADMIN')
def update_teacher(teacher_id: int):
    t = db.session.get(Teacher, teacher_id)
    if not t:
        return jsonify({'error': 'Not found'}), 404

    data = request.get_json() or {}
    try:
        if 'nip' in data:
            t.nip = Teacher._validate_nip(data['nip'])
        if 'name' in data:
            t.name = Teacher._validate_name(data['name'])
        if 'phone' in data:
            t.phone = Teacher._validate_phone(data['phone'])
        if 'address' in data:
            t.address = (data.get('address') or '').strip()
        db.session.commit()
        logger.info(f"Teacher updated: {t.nip}")
        return jsonify(t.to_dict(include_subjects=False))
    except IntegrityError:
        db.session.rollback()
        return jsonify({'error': 'NIP already exists'}), 409
    except ValueError as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400


@teacher_bp.delete('/<int:teacher_id>')
@roles_required('ADMIN')
def delete_teacher(teacher_id: int):
    t = db.session.get(Teacher, teacher_id)
    if not t:
        return jsonify({'error': 'Not found'}), 404
    db.session.delete(t)
    db.session.commit()
    logger.info(f"Teacher deleted: {t.nip}")
    return jsonify({'message': 'Deleted'})
