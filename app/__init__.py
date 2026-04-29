import os
from flask import Flask


def create_app() -> Flask:
    templates_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "app", "templates")
    static_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "static")
    app = Flask(__name__, template_folder=templates_dir, static_folder=static_dir)
    app.config["JSON_AS_ASCII"] = False

    from app.routes import register_blueprints

    register_blueprints(app)
    return app
