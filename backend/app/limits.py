"""Shared input size validation helpers."""

from __future__ import annotations

from flask import current_app, jsonify


def input_too_large(text: str):
    limit = current_app.config["MAX_INPUT_LENGTH"]
    if len(text) > limit:
        return jsonify({"error": f"Input exceeds the {limit // 1000}k character limit."}), 400
    return None


def file_too_large(size: int):
    limit = current_app.config["MAX_FILE_SIZE"]
    if size > limit:
        return jsonify({"error": "Uploaded file exceeds the 5 MB limit."}), 400
    return None
