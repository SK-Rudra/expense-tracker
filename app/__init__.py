from pathlib import Path

from flask import Flask

from app.extensions import db, migrate
from config import Config


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    Path(app.instance_path).mkdir(parents=True, exist_ok=True)

    db.init_app(app)
    migrate.init_app(app, db)
    from app import models  # noqa: F401

    from app.routes import main

    app.register_blueprint(main)

    return app