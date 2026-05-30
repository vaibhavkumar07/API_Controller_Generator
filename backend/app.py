from flask import Flask, request, jsonify
from flask_cors import CORS
from parser import extract_text_from_pdf, parse_input
from generator import generate_controller, generate_classes

app = Flask(__name__)
CORS(app)

MAX_INPUT_LENGTH = 50_000
MAX_FILE_SIZE = 5_242_880  # 5 MB


@app.route("/api/generate", methods=["POST"])
def generate():
    input_text = ""
    language = "csharp"
    classes_lang = "javascript"

    if request.content_type and request.content_type.startswith("multipart/form-data"):
        uploaded_file = request.files.get("file")
        input_text = request.form.get("inputText", "")
        language = request.form.get("language", "csharp")
        classes_lang = request.form.get("classesLang", "javascript")
        if uploaded_file:
            uploaded_file.stream.seek(0, 2)
            size = uploaded_file.stream.tell()
            uploaded_file.stream.seek(0)
            if size > MAX_FILE_SIZE:
                return jsonify({"error": "Uploaded file exceeds the 5 MB limit."}), 400
            text_from_pdf = extract_text_from_pdf(uploaded_file.stream)
            input_text = input_text or text_from_pdf
    else:
        data = request.get_json(silent=True) or {}
        input_text = data.get("inputText", "")
        language = data.get("language", "csharp")
        classes_lang = data.get("classesLang", "javascript")

    if not input_text or not language:
        return jsonify({"error": "inputText or uploaded PDF is required, and language must be selected."}), 400

    if len(input_text) > MAX_INPUT_LENGTH:
        return jsonify({"error": f"Input exceeds the {MAX_INPUT_LENGTH // 1000}k character limit."}), 400

    try:
        endpoints = parse_input(input_text)
        if not endpoints:
            return jsonify({"error": "No API endpoints were detected in the input."}), 400

        controller_code = generate_controller(endpoints, language)
        classes_code = generate_classes(endpoints, classes_lang)
        return jsonify({
            "controllerCode": controller_code,
            "classesCode": classes_code,
            "language": language,
            "classesLang": classes_lang,
        })
    except Exception as exc:
        return jsonify({"error": str(exc)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5002, debug=True)
