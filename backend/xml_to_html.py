"""Convert well-formed XML text into a standalone HTML table document.

Columns:
  _ — element text content
  $ — attribute values (space-joined, document order)
"""

from __future__ import annotations

import html
import xml.etree.ElementTree as ET


class XmlToHtmlError(ValueError):
    """Raised when XML input is missing or not well-formed."""


def _cell(value: str) -> str:
    text = (value or "").strip()
    if not text:
        return "&nbsp;"
    return html.escape(text)


def _attr_cell(elem: ET.Element) -> str:
    if not elem.attrib:
        return "&nbsp;"
    return html.escape(" ".join(elem.attrib.values()))


def _collect_rows(elem: ET.Element, rows: list[str]) -> None:
    text = (elem.text or "").strip()
    if text or elem.attrib:
        rows.append(f"<tr><td>{_cell(text)}</td><td>{_attr_cell(elem)}</td></tr>")
    for child in list(elem):
        _collect_rows(child, rows)


def xml_to_html(xml_text: str) -> str:
    if not xml_text or not str(xml_text).strip():
        raise XmlToHtmlError("XML input is required.")
    try:
        root = ET.fromstring(xml_text.strip())
    except ET.ParseError as exc:
        raise XmlToHtmlError(f"Invalid XML: {exc}") from exc

    rows: list[str] = []
    _collect_rows(root, rows)
    rows.append("<tr><td>&nbsp;</td><td>&nbsp;</td></tr>")
    table = (
        "<table border='1'>"
        "<tr><th>_</th><th>$</th></tr>"
        + "".join(rows)
        + "</table>"
    )
    return (
        "<!DOCTYPE html>\n"
        "<html>\n"
        "    <head>\n"
        "        <meta charset='UTF-8'>\n"
        "        <title>XML To HTML</title>\n"
        "    </head>\n"
        "    <body>\n"
        f"        {table}\n"
        "    </body>\n"
        "</html>"
    )
