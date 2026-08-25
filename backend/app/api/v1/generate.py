"""POST /generate — controller + client code generation."""

from __future__ import annotations

from flask import Blueprint, jsonify

from app.limits import file_too_large, input_too_large
from generator import generate_classes, generate_controller
from parser import extract_text_from_pdf, parse_input

bp = Blueprint("generate", __name__)


@bp.post("/generate")
def generate():
    """
    Generate controller and client caller code from API endpoint definitions.
    ---
    tags:
      - Generate
    consumes:
      - application/json
      - multipart/form-data
    parameters:
      - in: body
        name: body
        required: false
        schema:
          type: object
          properties:
            inputText:
              type: string
              description: Free-text endpoint definitions
            language:
              type: string
              enum: [csharp, java, python]
              default: csharp
            classesLang:
              type: string
              enum: [javascript, typescript, python, csharp, java]
              default: javascript
      - in: formData
        name: inputText
        type: string
        required: false
      - in: formData
        name: language
        type: string
        required: false
      - in: formData
        name: classesLang
        type: string
        required: false
      - in: formData
        name: file
        type: file
        description: PDF containing endpoint definitions
        required: false
    responses:
      200:
        description: Generated code
        schema:
          type: object
          properties:
            controllerCode:
              type: string
            classesCode:
              type: string
            language:
              type: string
            classesLang:
              type: string
      400:
        description: Missing input, no endpoints, or oversize
        schema:
          type: object
          properties:
            error:
              type: string
      500:
        description: Generation failure
        schema:
          type: object
          properties:
            error:
              type: string
    """
    from flask import request

    language = "csharp"
    classes_lang = "javascript"
    input_text = ""

    if request.content_type and request.content_type.startswith("multipart/form-data"):
        uploaded_file = request.files.get("file")
        input_text = request.form.get("inputText", "") or ""
        language = request.form.get("language", "csharp") or "csharp"
        classes_lang = request.form.get("classesLang", "javascript") or "javascript"
        if uploaded_file:
            uploaded_file.stream.seek(0, 2)
            size = uploaded_file.stream.tell()
            uploaded_file.stream.seek(0)
            err = file_too_large(size)
            if err:
                return err
            text_from_pdf = extract_text_from_pdf(uploaded_file.stream)
            input_text = input_text or text_from_pdf
    else:
        data = request.get_json(silent=True) or {}
        input_text = data.get("inputText", "") or ""
        language = data.get("language", "csharp") or "csharp"
        classes_lang = data.get("classesLang", "javascript") or "javascript"

    if not input_text or not language:
        return jsonify(
            {"error": "inputText or uploaded PDF is required, and language must be selected."}
        ), 400

    oversized = input_too_large(input_text)
    if oversized:
        return oversized

    try:
        endpoints = parse_input(input_text)
        if not endpoints:
            return jsonify({"error": "No API endpoints were detected in the input."}), 400

        controller_code = generate_controller(endpoints, language)
        classes_code = generate_classes(endpoints, classes_lang)
        return jsonify(
            {
                "controllerCode": controller_code,
                "classesCode": classes_code,
                "language": language,
                "classesLang": classes_lang,
            }
        )
    except Exception as exc:
        return jsonify({"error": str(exc)}), 500
