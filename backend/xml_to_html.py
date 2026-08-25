"""Convert well-formed XML text into a standalone browsable HTML document."""

from __future__ import annotations

import html
import xml.etree.ElementTree as ET


class XmlToHtmlError(ValueError):
    """Raised when XML input is missing or not well-formed."""


def _local_name(tag: str) -> str:
    if tag.startswith("{") and "}" in tag:
        return tag.split("}", 1)[1]
    return tag


def _render_node(elem: ET.Element) -> str:
    name = html.escape(_local_name(elem.tag), quote=True)
    attrs = "".join(
        f'<span class="xml-attr">{html.escape(k, quote=True)}='
        f'"{html.escape(v, quote=True)}"</span>'
        for k, v in elem.attrib.items()
    )
    parts = [
        '<section class="xml-node">',
        f'<div class="xml-tag"><span class="xml-name">{name}</span>{attrs}</div>',
    ]
    text = (elem.text or "").strip()
    if text:
        parts.append(f'<pre class="xml-text">{html.escape(text)}</pre>')
    for child in list(elem):
        parts.append(_render_node(child))
        tail = (child.tail or "").strip()
        if tail:
            parts.append(f'<pre class="xml-text">{html.escape(tail)}</pre>')
    parts.append("</section>")
    return "".join(parts)


def xml_to_html(xml_text: str) -> str:
    if not xml_text or not str(xml_text).strip():
        raise XmlToHtmlError("XML input is required.")
    try:
        root = ET.fromstring(xml_text.strip())
    except ET.ParseError as exc:
        raise XmlToHtmlError(f"Invalid XML: {exc}") from exc

    title = html.escape(_local_name(root.tag))
    body = _render_node(root)
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1"/>
<title>{title}</title>
<style>
  body {{ font-family: system-ui, sans-serif; margin: 1.5rem; line-height: 1.45; color: #1a1a1a; background: #fafafa; }}
  .xml-node {{ margin: 0.35rem 0 0.35rem 1rem; padding-left: 0.75rem; border-left: 2px solid #ccc; }}
  .xml-node:first-child {{ margin-left: 0; }}
  .xml-tag {{ font-family: ui-monospace, monospace; font-size: 0.95rem; }}
  .xml-name {{ font-weight: 700; color: #0b5; }}
  .xml-attr {{ margin-left: 0.5rem; font-size: 0.8rem; color: #555; background: #eee; padding: 0.1rem 0.35rem; border-radius: 3px; }}
  .xml-text {{ margin: 0.35rem 0; padding: 0.5rem 0.75rem; background: #fff; border: 1px solid #e0e0e0; border-radius: 4px; white-space: pre-wrap; word-break: break-word; font-family: ui-monospace, monospace; font-size: 0.85rem; }}
</style>
</head>
<body>
<h1>{title}</h1>
{body}
</body>
</html>
"""
