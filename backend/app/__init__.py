import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from flask_migrate import Migrate
from dotenv import load_dotenv

_db = SQLAlchemy()
_login_manager = LoginManager()
_bcrypt = Bcrypt()
_migrate = Migrate()


def create_app() -> Flask:
    load_dotenv()

    app = Flask(__name__, template_folder="templates", static_folder="static")

    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-secret")
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL", "sqlite:///dev.db")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    _db.init_app(app)
    _login_manager.init_app(app)
    _bcrypt.init_app(app)
    _migrate.init_app(app, _db)

    _login_manager.login_view = "auth.login"

    try:
        from .controllers.public import public_bp
        from .controllers.auth import auth_bp
        from .controllers.teacher import teacher_bp
        from .controllers.student import student_bp

        app.register_blueprint(public_bp)
        app.register_blueprint(auth_bp, url_prefix="/auth")
        app.register_blueprint(teacher_bp, url_prefix="/teacher")
        app.register_blueprint(student_bp, url_prefix="/student")
    except Exception:
        pass

    with app.app_context():
        try:
            from .models import user, classroom, assignment, submission  # noqa: F401
        except Exception:
            pass

    return app


db = _db
login_manager = _login_manager
bcrypt = _bcrypt
