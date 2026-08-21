from pathlib import Path

from flask import Flask

from app.extensions import csrf, db, login_manager, migrate
from config import Config
from app.transactions import transactions

def create_app(test_config: dict | None = None):
    app = Flask(__name__)
    app.config.from_object(Config)

    if test_config is not None:
        app.config.update(test_config)

    Path(app.instance_path).mkdir(parents=True, exist_ok=True)

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    csrf.init_app(app)

    from app import models  # noqa: F401
    from app.auth import auth
    from app.routes import main

    app.register_blueprint(main)
    app.register_blueprint(auth)
    app.register_blueprint(transactions)

    return app