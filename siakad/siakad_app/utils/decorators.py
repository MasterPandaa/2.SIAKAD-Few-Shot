from functools import wraps

from flask import jsonify
from flask_jwt_extended import get_jwt, get_jwt_identity, verify_jwt_in_request
from siakad_app.extensions import db
from siakad_app.models import User


def roles_required(*roles):
    roles_set = set(r.upper() for r in roles)

    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            verify_jwt_in_request()
            claims = get_jwt()
            role = claims.get("role")
            if role not in roles_set:
                return jsonify({"error": "Forbidden"}), 403
            return fn(*args, **kwargs)

        return decorator

    return wrapper


def current_user():
    verify_jwt_in_request()
    uid = get_jwt_identity()
    if uid is None:
        return None
    return db.session.get(User, uid)
