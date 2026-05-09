from flask import Flask, request, jsonify
from flask_cors import CORS
from parser import extract_text_from_pdf, parse_input
from generator import generate_controller

app = Flask(__name__)
CORS(app)

@app.route("/api/generate", methods=["POST"])
def generate():
    input_text = ""
    language = "csharp"

    if request.content_type and request.content_type.startswith("multipart/form-data"):
        uploaded_file = request.files.get("file")
        input_text = request.form.get("inputText", "")
        language = request.form.get("language", "csharp")
        if uploaded_file:
            text_from_pdf = extract_text_from_pdf(uploaded_file.stream)
            input_text = input_text or text_from_pdf
    else:
        data = request.get_json(silent=True) or {}
        input_text = data.get("inputText", "")
        language = data.get("language", "csharp")

    if not input_text or not language:
        return jsonify({"error": "inputText or uploaded PDF is required, and language must be selected."}), 400

    try:
        endpoints = parse_input(input_text)
        if not endpoints:
            return jsonify({"error": "No API endpoints were detected in the input."}), 400

        controller_code = generate_controller(endpoints, language)
        return jsonify({"controllerCode": controller_code, "language": language})
    except Exception as exc:
        return jsonify({"error": str(exc)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5002, debug=True)
