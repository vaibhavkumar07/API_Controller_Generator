"""POST /xml-to-html — convert well-formed XML to HTML."""

from __future__ import annotations

from flask import Blueprint, jsonify

from app.limits import input_too_large
from app.request_utils import decode_utf8_xml, read_text_and_file
from xml_to_html import XmlToHtmlError, xml_to_html

bp = Blueprint("xml_to_html", __name__)


@bp.post("/xml-to-html")
def convert_xml_to_html():
    """
    Convert well-formed XML into a standalone HTML document.
    ---
    tags:
      - Transform
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
            xmlText:
              type: string
              description: Well-formed XML text
      - in: formData
        name: xmlText
        type: string
        required: false
      - in: formData
        name: file
        type: file
        description: UTF-8 .xml file
        required: false
    responses:
      200:
        description: Converted HTML document
        schema:
          type: object
          properties:
            html:
              type: string
      400:
        description: Missing, invalid, or oversize XML
        schema:
          type: object
          properties:
            error:
              type: string
      500:
        description: Unexpected conversion failure
        schema:
          type: object
          properties:
            error:
              type: string
    """
    xml_text, _, err = read_text_and_file("xmlText", file_decoder=decode_utf8_xml)
    if err:
        return err

    if not xml_text.strip():
        return jsonify({"error": "xmlText or uploaded XML file is required."}), 400

    oversized = input_too_large(xml_text)
    if oversized:
        return oversized

    try:
        html_doc = xml_to_html(xml_text)
        return jsonify({"html": html_doc})
    except XmlToHtmlError as exc:
        return jsonify({"error": str(exc)}), 400
    except Exception as exc:
        return jsonify({"error": str(exc)}), 500
