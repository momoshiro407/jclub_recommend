from flask import Flask
from .extensions import db, migrate
from .clubs.routes import bp as clubs_bp
from .questions.routes import bp as questions_bp
from .recommend.routes import bp as recommend_bp
from flask_cors import CORS
from .cli import register_commands
import os


def create_app():
    app = Flask(__name__)
    CORS(app)  # フロントエンドからのCORS対応
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # extensionsの初期化
    db.init_app(app)
    migrate.init_app(app, db)

    # BluePrintの登録
    app.register_blueprint(clubs_bp, url_prefix='/clubs')
    app.register_blueprint(questions_bp, url_prefix='/questions')
    app.register_blueprint(recommend_bp, url_prefix='/recommend')

    # CLIコマンドの登録
    register_commands(app)

    return app
