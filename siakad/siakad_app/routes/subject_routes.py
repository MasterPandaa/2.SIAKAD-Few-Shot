import logging
from flask import Blueprint, request, jsonify
from sqlalchemy.exc import IntegrityError
from sqlalchemy import or_

from siakad_app.extensions import db
from siakad_app.models import Subject, Teacher
from siakad_app.schemas import SubjectSchema
from siakad_app.utils.decorators import roles_required

logger = logging.getLogger(__name__)

subject_bp = Blueprint('subjects', __name__)


@subject_bp.get('/')
@roles_required('ADMIN', 'TEACHER')
def list_subjects():
    q = (request.args.get('q') or '').strip()
    page = int(request.args.get('page', 1))
    per_page = min(int(request.args.get('per_page', 20)), 100)

    query = Subject.query
    if q:
        like = f"%{q}%"
        query = query.filter(or_(Subject.name.ilike(like), Subject.code.ilike(like)))

    pagination = query.order_by(Subject.name.asc()).paginate(page=page, per_page=per_page, error_out=False)
    return jsonify({
        'items': [s.to_dict() for s in pagination.items],
        'total': pagination.total,
        'page': pagination.page,
        'pages': pagination.pages,
    })


@subject_bp.post('/')
@roles_required('ADMIN')
def create_subject():
    try:
        payload = SubjectSchema().load(request.get_json() or {})
        if payload.get('teacher_id') and not db.session.get(Teacher, payload['teacher_id']):
            return jsonify({'error': 'teacher_id tidak ditemukan'}), 400
        sub = Subject(code=payload['code'], name=payload['name'], sks=payload['sks'], teacher_id=payload.get('teacher_id'))
        db.session.add(sub)
        db.session.commit()
        logger.info(f"Subject created: {sub.code}")
        return jsonify(sub.to_dict()), 201
    except IntegrityError:
        db.session.rollback()
        return jsonify({'error': 'Kode mata pelajaran sudah ada'}), 409
    except ValueError as e:
        return jsonify({'error': str(e)}), 400


@subject_bp.get('/<int:subject_id>')
@roles_required('ADMIN', 'TEACHER')
def get_subject(subject_id: int):
    s = db.session.get(Subject, subject_id)
    if not s:
        return jsonify({'error': 'Not found'}), 404
    return jsonify(s.to_dict())


@subject_bp.put('/<int:subject_id>')
@subject_bp.patch('/<int:subject_id>')
@roles_required('ADMIN')
def update_subject(subject_id: int):
    s = db.session.get(Subject, subject_id)
    if not s:
        return jsonify({'error': 'Not found'}), 404

    data = request.get_json() or {}
    try:
        if 'code' in data:
            s.code = Subject._validate_code(data['code'])
        if 'name' in data:
            s.name = Subject._validate_name(data['name'])
        if 'sks' in data:
            s.sks = Subject._validate_sks(data['sks'])
        if 'teacher_id' in data:
            tid = data.get('teacher_id')
            if tid is not None and tid != '':
                if not db.session.get(Teacher, tid):
                    return jsonify({'error': 'teacher_id tidak ditemukan'}), 400
                s.teacher_id = tid
            else:
                s.teacher_id = None
        db.session.commit()
        logger.info(f"Subject updated: {s.code}")
        return jsonify(s.to_dict())
    except IntegrityError:
        db.session.rollback()
        return jsonify({'error': 'Kode mata pelajaran sudah ada'}), 409
    except ValueError as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400


@subject_bp.delete('/<int:subject_id>')
@roles_required('ADMIN')
def delete_subject(subject_id: int):
    s = db.session.get(Subject, subject_id)
    if not s:
        return jsonify({'error': 'Not found'}), 404
    db.session.delete(s)
    db.session.commit()
    logger.info(f"Subject deleted: {s.code}")
    return jsonify({'message': 'Deleted'})
