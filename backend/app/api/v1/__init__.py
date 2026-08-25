"""API v1 blueprint package."""

from __future__ import annotations

from flask import Blueprint

from app.api.v1.generate import bp as generate_bp
from app.api.v1.xml_to_html import bp as xml_to_html_bp

v1_bp = Blueprint("api_v1", __name__, url_prefix="/api/v1")
v1_bp.register_blueprint(generate_bp)
v1_bp.register_blueprint(xml_to_html_bp)
