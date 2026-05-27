import os

from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()
login_manager = LoginManager()


def create_app():
    app = Flask(__name__, instance_relative_config=True)

    os.makedirs(app.instance_path, exist_ok=True)

    # Для учебного проекта: простой secret key
    app.config["SECRET_KEY"] = os.environ.get("CATSHOP_SECRET_KEY", "dev-secret-key-change-me")
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(app.instance_path, "catshop.sqlite3")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config.setdefault("ADMIN_TOKEN", os.environ.get("CATSHOP_ADMIN_TOKEN", "admin"))

    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"

    from . import models  # noqa: F401
    from .routes import main_bp
    from .auth import auth_bp
    from .social import social_bp
    from .chat import chat_bp
    from .admin import admin_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(social_bp, url_prefix="/social")
    app.register_blueprint(chat_bp)
    app.register_blueprint(admin_bp)

    with app.app_context():
        db.create_all()
        models.seed_initial_data()

    return app

