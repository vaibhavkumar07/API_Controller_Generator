"""Enterprise-style XML→HTML conversion (schema-agnostic).

Inspired by multi-phase pipeline; production path is the complex engine:
- ui-component=tabs / accordion
- repeating records → tables
- interactive method/type attrs → buttons/inputs
- status keywords → success/danger/warning styles
"""

from __future__ import annotations

import html
import xml.etree.ElementTree as ET
from typing import Optional


class XmlToHtmlError(ValueError):
    """Raised when XML input is missing or not well-formed."""


def _local_name(tag: str) -> str:
    if tag.startswith("{") and "}" in tag:
        return tag.split("}", 1)[1]
    return tag


def _esc(value: str) -> str:
    return html.escape(value or "", quote=True)


def _text(element: ET.Element) -> str:
    return (element.text or "").strip()


class ComplexConversionEngine:
    def __init__(self) -> None:
        self.tab_count = 0
        self.accordion_count = 0

    def compute_dynamic_styling(self, element: ET.Element, text: str) -> str:
        classes: list[str] = []
        val_clean = (text or "").lower()
        if val_clean in ("active", "true", "success", "verified", "online"):
            classes.append("state-success")
        elif val_clean in ("inactive", "false", "danger", "error", "offline"):
            classes.append("state-danger")
        elif val_clean in ("pending", "warning", "hold"):
            classes.append("state-warning")
        return f' class="{" ".join(classes)}"' if classes else ""

    def process_node(self, element: ET.Element, parent_tag: Optional[str] = None) -> str:
        tag_lower = _local_name(element.tag).lower()
        text = _text(element)
        children = list(element)
        attribs = element.attrib
        class_attributes = self.compute_dynamic_styling(element, text)

        # Tabs
        if attribs.get("ui-component") == "tabs":
            self.tab_count += 1
            tid = self.tab_count
            tab_headers = "".join(
                f'<button type="button" class="tab-lnk" data-tab="t-{tid}-{i}">'
                f"{_esc(_local_name(c.tag).upper())}</button>"
                for i, c in enumerate(children)
            )
            tab_contents = "".join(
                f'<div id="t-{tid}-{i}" class="tab-pane">'
                f"{self.process_node(c, parent_tag=tag_lower)}</div>"
                for i, c in enumerate(children)
            )
            return (
                f'<div class="tabs-container">'
                f'<div class="tab-bar">{tab_headers}</div>'
                f"{tab_contents}</div>\n"
            )

        # Accordion
        if attribs.get("ui-component") == "accordion" or "collapse" in tag_lower:
            self.accordion_count += 1
            aid = self.accordion_count
            inner_body = "".join(
                self.process_node(c, parent_tag=tag_lower) for c in children
            ) or _esc(text)
            return f"""
            <div class="accordion-item">
                <button type="button" class="accordion-trigger" data-acc="acc-{aid}">
                    {_esc(tag_lower.upper())} [Click to Expand/Collapse]
                </button>
                <div id="acc-{aid}" class="accordion-panel" hidden>{inner_body}</div>
            </div>
            """

        # Buttons
        if "method" in attribs or "onclick" in attribs:
            action = attribs.get("method") or attribs.get("onclick") or ""
            label = text or tag_lower.title()
            return (
                f'<button type="button" class="action-btn" data-method="{_esc(action)}"'
                f"{class_attributes}>{_esc(label)}</button>\n"
            )

        # Inputs
        if "type" in attribs or "placeholder" in attribs:
            inp_type = attribs.get("type", "text")
            placeholder = attribs.get("placeholder", "")
            return (
                f'<div class="form-control"><label>{_esc(tag_lower.upper())}</label>'
                f'<input type="{_esc(inp_type)}" placeholder="{_esc(placeholder)}"></div>\n'
            )

        # Auto table
        if (
            len(children) > 1
            and all(len(list(child)) > 0 for child in children)
            and all(child.tag == children[0].tag for child in children)
        ):
            headers = [_local_name(sub.tag).upper() for sub in list(children[0])]
            head = "".join(f"<th>{_esc(h)}</th>" for h in headers)
            rows = []
            for record in children:
                cells = "".join(
                    f"<td>{_esc(_text(cell))}</td>" for cell in list(record)
                )
                rows.append(f"<tr>{cells}</tr>")
            return f"""
            <div class="table-wrap">
                <div class="table-caption">{_esc(_local_name(element.tag).upper())} DATA LEDGER</div>
                <table>
                    <thead><tr>{head}</tr></thead>
                    <tbody>{"".join(rows)}</tbody>
                </table>
            </div>
            """

        # Leaf
        if not children:
            if text:
                return (
                    f'<div class="kv-row"><span class="key">{_esc(tag_lower.title())}:</span> '
                    f"<span{class_attributes}>{_esc(text)}</span></div>\n"
                )
            return ""

        # Container
        nested_html = "".join(
            self.process_node(child, parent_tag=tag_lower) for child in children
        )
        wrapper = "main" if parent_tag is None else "section"
        meta = ""
        if attribs:
            # skip ui-component from meta display noise optionally show others
            meta_bits = [
                f"<span><strong>{_esc(k)}:</strong> {_esc(v)}</span>"
                for k, v in attribs.items()
                if k != "ui-component"
            ]
            if meta_bits:
                meta = f'<div class="container-meta">{" ".join(meta_bits)}</div>'

        return (
            f"<{wrapper}>\n"
            f'<div class="sec-title">{_esc(tag_lower.upper())} {meta}</div>\n'
            f"{nested_html}</{wrapper}>\n"
        )

    def convert(self, xml_string: str) -> str:
        root = ET.fromstring(xml_string)
        dynamic_body = self.process_node(root)
        return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Enterprise Complex Dashboard Output</title>
    <style>
        body {{ font-family: system-ui, sans-serif; background-color: #f8fafc; padding: 2rem; color: #1e293b; margin: 0; line-height: 1.5; }}
        main {{ max-width: 1100px; margin: 0 auto; background: white; border-radius: 12px; padding: 2.5rem; box-shadow: 0 4px 6px rgba(0,0,0,0.05); }}
        section {{ border: 1px solid #e2e8f0; padding: 1.5rem; border-radius: 8px; margin: 1rem 0; background-color: #fafafa; }}
        .sec-title {{ font-weight: 800; font-size: 1.1rem; color: #0f172a; margin-bottom: 1rem; border-bottom: 2px solid #e2e8f0; padding-bottom: 0.25rem; display: flex; justify-content: space-between; gap: 0.75rem; flex-wrap: wrap; align-items: center; }}
        .container-meta {{ font-size: 0.75rem; color: #64748b; display: inline-flex; gap: 0.75rem; flex-wrap: wrap; }}
        .kv-row {{ display: flex; padding: 0.4rem 0; border-bottom: 1px solid #f1f5f9; gap: 1rem; flex-wrap: wrap; }}
        .key {{ font-weight: 600; min-width: 150px; color: #475569; }}
        .state-success {{ color: #16a34a !important; font-weight: 700; }}
        .state-danger {{ color: #dc2626 !important; font-weight: 700; }}
        .state-warning {{ color: #ea580c !important; font-weight: 700; }}
        .tabs-container {{ margin: 1.5rem 0; border: 1px solid #cbd5e1; border-radius: 8px; overflow: hidden; }}
        .tab-bar {{ display: flex; background: #e2e8f0; border-bottom: 1px solid #cbd5e1; flex-wrap: wrap; }}
        .tab-lnk {{ background: none; border: none; padding: 0.75rem 1.5rem; cursor: pointer; font-weight: 600; color: #475569; }}
        .tab-lnk:hover {{ background: #cbd5e1; }}
        .tab-lnk.active {{ background: white; color: #2563eb; border-bottom: 2px solid #2563eb; }}
        .tab-pane {{ display: none; padding: 1.5rem; background: white; }}
        .tab-pane.active {{ display: block; }}
        .accordion-item {{ border: 1px solid #cbd5e1; border-radius: 6px; margin: 0.5rem 0; overflow: hidden; }}
        .accordion-trigger {{ width: 100%; text-align: left; background: #f1f5f9; border: none; padding: 1rem; font-weight: 700; cursor: pointer; }}
        .accordion-panel {{ padding: 1.5rem; border-top: 1px solid #cbd5e1; background: white; }}
        .table-wrap {{ margin-top: 1rem; overflow-x: auto; }}
        .table-caption {{ font-weight: 700; font-size: 0.85rem; color: #64748b; margin-bottom: 0.5rem; }}
        table {{ width: 100%; border-collapse: collapse; margin-top: 1rem; }}
        th {{ background: #f8fafc; padding: 12px; border-bottom: 2px solid #cbd5e1; text-align: left; }}
        td {{ padding: 12px; border-bottom: 1px solid #e2e8f0; }}
        .action-btn, button.action-btn {{ background: #2563eb; color: white; border: none; padding: 0.5rem 1.25rem; border-radius: 6px; font-weight: 600; cursor: pointer; margin-top: 10px; }}
        .form-control {{ margin: 10px 0; }}
        .form-control label {{ display: block; font-weight: 600; font-size: 0.85em; margin-bottom: 4px; }}
        input {{ padding: 0.5rem; border: 1px solid #cbd5e1; border-radius: 6px; width: 100%; max-width: 300px; }}
    </style>
</head>
<body>
{dynamic_body}
<script>
(function () {{
  function activateTab(container, btn) {{
    const tabId = btn.getAttribute('data-tab');
    container.querySelectorAll('.tab-pane').forEach(p => p.classList.remove('active'));
    container.querySelectorAll('.tab-lnk').forEach(b => b.classList.remove('active'));
    const pane = document.getElementById(tabId);
    if (pane) pane.classList.add('active');
    btn.classList.add('active');
  }}
  document.querySelectorAll('.tabs-container').forEach(container => {{
    container.querySelectorAll('.tab-lnk').forEach(btn => {{
      btn.addEventListener('click', () => activateTab(container, btn));
    }});
    const first = container.querySelector('.tab-lnk');
    if (first) activateTab(container, first);
  }});
  document.querySelectorAll('.accordion-trigger').forEach(btn => {{
    btn.addEventListener('click', () => {{
      const id = btn.getAttribute('data-acc');
      const panel = document.getElementById(id);
      if (!panel) return;
      panel.hidden = !panel.hidden;
    }});
  }});
}})();
</script>
</body>
</html>
"""


def xml_to_html(xml_text: str) -> str:
    if not xml_text or not str(xml_text).strip():
        raise XmlToHtmlError("XML input is required.")
    try:
        return ComplexConversionEngine().convert(xml_text.strip())
    except ET.ParseError as exc:
        raise XmlToHtmlError(f"Invalid XML: {exc}") from exc
