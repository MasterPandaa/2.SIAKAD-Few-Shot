import logging
from flask import jsonify
from marshmallow import ValidationError
from sqlalchemy.exc import IntegrityError
from werkzeug.exceptions import HTTPException
from siakad_app.extensions import db


def register_error_handlers(app):
    logger = logging.getLogger(__name__)

    @app.errorhandler(ValidationError)
    def handle_validation_error(err: ValidationError):
        return jsonify({'error': 'Validation error', 'messages': err.messages}), 400

    @app.errorhandler(IntegrityError)
    def handle_integrity_error(err: IntegrityError):
        db.session.rollback()
        logger.warning(f"Integrity error: {err}")
        return jsonify({'error': 'Data conflict (integrity error)'}), 409

    @app.errorhandler(ValueError)
    def handle_value_error(err: ValueError):
        return jsonify({'error': str(err)}), 400

    @app.errorhandler(HTTPException)
    def handle_http_exception(err: HTTPException):
        return jsonify({'error': err.description or 'HTTP error'}), err.code

    @app.errorhandler(Exception)
    def handle_uncaught_exception(err: Exception):
        logger.exception(f"Unhandled error: {err}")
        return jsonify({'error': 'Internal server error'}), 500
