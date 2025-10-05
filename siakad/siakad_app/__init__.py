import logging
from flask import Flask, jsonify, render_template
from sqlalchemy.engine import url as sa_url
import pymysql

from config import Config
from .extensions import db, migrate, jwt, bcrypt
from .utils.errors import register_error_handlers


def ensure_database_exists(db_uri: str):
    try:
        u = sa_url.make_url(db_uri)
        db_name = u.database
        if not db_name:
            return
        conn = pymysql.connect(host=u.host, user=u.username, password=u.password, port=u.port or 3306,
                               autocommit=True)
        with conn.cursor() as cur:
            cur.execute(f"CREATE DATABASE IF NOT EXISTS `{db_name}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;")
        conn.close()
    except Exception as e:
        logging.getLogger(__name__).warning(f"Could not ensure database exists: {e}")


def register_blueprints(app: Flask):
    from .routes.auth_routes import auth_bp
    from .routes.student_routes import student_bp
    from .routes.teacher_routes import teacher_bp
    from .routes.subject_routes import subject_bp
    from .routes.grade_routes import grade_bp
    from .routes.dashboard_routes import dashboard_bp

    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(student_bp, url_prefix='/students')
    app.register_blueprint(teacher_bp, url_prefix='/teachers')
    app.register_blueprint(subject_bp, url_prefix='/subjects')
    app.register_blueprint(grade_bp, url_prefix='/grades')
    app.register_blueprint(dashboard_bp, url_prefix='/dashboard')


def create_app() -> Flask:
    app = Flask(__name__, template_folder='templates', static_folder='static')
    app.config.from_object(Config)

    # Validate and configure logging
    Config.validate()
    Config.configure_logging()

    logger = logging.getLogger(__name__)

    # Optionally create database
    if app.config.get('AUTO_CREATE_DB'):
        ensure_database_exists(app.config['SQLALCHEMY_DATABASE_URI'])

    # Init extensions
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    bcrypt.init_app(app)

    # Register error handlers and blueprints
    register_error_handlers(app)
    register_blueprints(app)

    @app.get('/')
    def index_page():
        return render_template('index.html')

    # Create tables on first run (simple bootstrap)
    with app.app_context():
        db.create_all()
        logger.info('Database tables ensured')

    return app
