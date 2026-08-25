"""Shared JSON / multipart request parsing."""

from __future__ import annotations

from typing import Any, Callable, Optional, Tuple

from flask import request

from app.limits import file_too_large


def _is_multipart() -> bool:
    return bool(request.content_type and request.content_type.startswith("multipart/form-data"))


def read_text_and_file(
    text_field: str,
    *,
    file_decoder: Optional[Callable[[bytes], Tuple[Optional[str], Optional[tuple]]]] = None,
) -> Tuple[str, dict[str, Any], Optional[tuple]]:
    """
    Read primary text from JSON or multipart form.

    Returns (text, extra_form_or_json_fields, error_response_or_None).
    error_response is a (response, status) tuple when validation fails.
    """
    extras: dict[str, Any] = {}

    if _is_multipart():
        text = request.form.get(text_field, "") or ""
        for key in request.form:
            if key != text_field:
                extras[key] = request.form.get(key)
        uploaded = request.files.get("file")
        if uploaded:
            uploaded.stream.seek(0, 2)
            size = uploaded.stream.tell()
            uploaded.stream.seek(0)
            err = file_too_large(size)
            if err:
                return "", extras, err
            raw = uploaded.read()
            if file_decoder:
                decoded, decode_err = file_decoder(raw)
                if decode_err:
                    return "", extras, decode_err
                text = text or (decoded or "")
            else:
                text = text or raw.decode("utf-8", errors="replace")
        return text, extras, None

    data = request.get_json(silent=True) or {}
    text = data.get(text_field, "") or ""
    extras = {k: v for k, v in data.items() if k != text_field}
    return text, extras, None


def decode_utf8_xml(raw: bytes) -> Tuple[Optional[str], Optional[tuple]]:
    try:
        return raw.decode("utf-8"), None
    except UnicodeDecodeError:
        from flask import jsonify

        return None, (jsonify({"error": "Uploaded file must be UTF-8 text XML."}), 400)
