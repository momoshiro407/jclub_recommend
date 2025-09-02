from flask import Flask
from .extensions import db, migrate
import os


def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # init extensions
    db.init_app(app)
    migrate.init_app(app, db)

    # register blueprints
    from .routes import bp as api_bp
    app.register_blueprint(api_bp)

    # import models so flask-migrate can detect them
    from . import models  # noqa: F401

    # register CLI commands
    from .cli import register_commands
    register_commands(app)

    return app
