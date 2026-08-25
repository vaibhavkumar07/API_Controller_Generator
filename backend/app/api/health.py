"""Health check endpoint."""

from __future__ import annotations

from flask import Blueprint, jsonify

bp = Blueprint("health", __name__)


@bp.get("/health")
def health():
    """
    Health check
    ---
    tags:
      - Health
    responses:
      200:
        description: Service is healthy
        schema:
          type: object
          properties:
            status:
              type: string
              example: ok
    """
    return jsonify({"status": "ok"})
