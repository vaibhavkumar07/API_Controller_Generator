"""Flask application factory."""

from __future__ import annotations

from flask import Flask
from flask_cors import CORS
from flasgger import Swagger

from app.api.health import bp as health_bp
from app.api.v1 import v1_bp
from app.api.v1.generate import generate as generate_view
from app.api.v1.xml_to_html import convert_xml_to_html as xml_view
from app.config import Config


def create_app(config_object: type = Config) -> Flask:
    application = Flask(__name__)
    application.config.from_object(config_object)
    application.config["MAX_INPUT_LENGTH"] = config_object.MAX_INPUT_LENGTH
    application.config["MAX_FILE_SIZE"] = config_object.MAX_FILE_SIZE

    origins = config_object.CORS_ORIGINS
    if origins == "*":
        CORS(application)
    else:
        CORS(application, origins=[o.strip() for o in origins.split(",") if o.strip()])

    application.register_blueprint(health_bp)
    application.register_blueprint(v1_bp)

    # Legacy aliases — same handlers, unversioned paths
    application.add_url_rule("/api/generate", view_func=generate_view, methods=["POST"], endpoint="legacy_generate")
    application.add_url_rule(
        "/api/xml-to-html",
        view_func=xml_view,
        methods=["POST"],
        endpoint="legacy_xml_to_html",
    )

    Swagger(
        application,
        template={
            "openapi": "3.0.3",
            "info": {
                "title": "API Framework",
                "description": (
                    "Code generation and XML→HTML transform APIs. "
                    "Canonical paths are under /api/v1. Legacy /api/* aliases remain supported."
                ),
                "version": "1.0.0",
            },
            "tags": [
                {"name": "Generate", "description": "Controller and client code generation"},
                {"name": "Transform", "description": "XML to HTML conversion"},
                {"name": "Health", "description": "Service health"},
            ],
        },
        config={
            "headers": [],
            "specs": [
                {
                    "endpoint": "apispec",
                    "route": "/api/apispec.json",
                    "rule_filter": lambda rule: True,
                    "model_filter": lambda tag: True,
                }
            ],
            "static_url_path": "/flasgger_static",
            "swagger_ui": True,
            "specs_route": "/api/docs",
        },
    )

    return application
