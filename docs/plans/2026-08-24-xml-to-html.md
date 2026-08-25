# XML → HTML Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add `POST /api/xml-to-html` and a same-page UI tab that converts any well-formed XML into a browsable standalone HTML document (preview + download), usable from the frontend or direct API calls.

**Architecture:** New `backend/xml_to_html.py` parses XML with `xml.etree.ElementTree` and renders an escaped HTML tree document. Flask exposes `POST /api/xml-to-html` (JSON + multipart) without changing `/api/generate`. Next.js `page.tsx` adds an **API Generate | XML → HTML** mode switch; XML mode calls the new endpoint and shows `iframe` preview plus download/copy.

**Tech Stack:** Python 3 / Flask / pytest · Next.js 15 / React 18 / TypeScript · stdlib ElementTree only (no new pip deps)

**Spec:** [docs/specs/2026-08-24-xml-to-html-design.md](../specs/2026-08-24-xml-to-html-design.md)

---

## File map

| File | Role |
|------|------|
| Create `backend/xml_to_html.py` | `xml_to_html(xml_text: str) -> str`; `XmlToHtmlError` for bad input |
| Modify `backend/app.py` | Add `POST /api/xml-to-html` route |
| Create `backend/tests/test_xml_to_html.py` | Unit tests for converter |
| Modify `backend/tests/test_app.py` | API integration tests for new route |
| Modify `frontend/app/page.tsx` | Mode tab + XML→HTML UI |
| Modify `frontend/app/globals.css` | Tab + preview styles |
| Modify `README.md` | Document endpoint + UI tab |

---

### Task 1: Converter unit tests (TDD — fail first)

**Files:**
- Create: `backend/tests/test_xml_to_html.py`
- Create (later in Task 2): `backend/xml_to_html.py`

- [ ] **Step 1: Write failing unit tests**

Create `backend/tests/test_xml_to_html.py`:

```python
import pytest
from xml_to_html import xml_to_html, XmlToHtmlError


def test_simple_element_becomes_html_document():
    html = xml_to_html("<root>hello</root>")
    assert html.startswith("<!DOCTYPE html>")
    assert "<html" in html
    assert "root" in html
    assert "hello" in html


def test_nested_elements_and_attributes():
    xml = '<catalog><book id="1" lang="en">The Hobbit</book></catalog>'
    html = xml_to_html(xml)
    assert "catalog" in html
    assert "book" in html
    assert "id=" in html or "id" in html
    assert "1" in html
    assert "The Hobbit" in html


def test_escapes_special_characters_in_text():
    html = xml_to_html("<n>a&lt;b&amp;c</n>")
    # Parsed text is "a<b&c"; must be escaped in HTML output
    assert "a&lt;b&amp;c" in html
    assert "<script" not in html.lower() or html.lower().count("<script") == 0


def test_script_like_text_is_escaped_not_executed():
    html = xml_to_html("<code>MsgBox \"hi\"</code>")
    assert "MsgBox" in html
    assert "<script>" not in html.lower()


def test_invalid_xml_raises():
    with pytest.raises(XmlToHtmlError):
        xml_to_html("<root><unclosed>")


def test_empty_input_raises():
    with pytest.raises(XmlToHtmlError):
        xml_to_html("   ")
```

- [ ] **Step 2: Run tests — expect import/fail**

```bash
cd backend && source .venv/bin/activate && python -m pytest tests/test_xml_to_html.py -v
```

Expected: FAIL (module `xml_to_html` not found, or functions missing).

- [ ] **Step 3: Commit tests**

```bash
git add backend/tests/test_xml_to_html.py
git commit -m "test: add failing unit tests for xml_to_html converter"
```

---

### Task 2: Implement `xml_to_html.py`

**Files:**
- Create: `backend/xml_to_html.py`
- Test: `backend/tests/test_xml_to_html.py`

- [ ] **Step 1: Implement converter**

Create `backend/xml_to_html.py`:

```python
"""Convert well-formed XML text into a standalone browsable HTML document."""

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
```

- [ ] **Step 2: Run unit tests — expect pass**

```bash
cd backend && source .venv/bin/activate && python -m pytest tests/test_xml_to_html.py -v
```

Expected: all PASS. If `test_escapes_special_characters_in_text` fails because input used entities, adjust the test to use raw characters via a CDATA-free string built in Python:

```python
html_out = xml_to_html("<n>a<b&c</n>")  # invalid — use:
html_out = xml_to_html("<n>a&lt;b&amp;c</n>")
```

Keep assertion on escaped output containing `a&lt;b&amp;c`. If the script-like test is too strict on `<script`, keep only `assert "<script>" not in html.lower()`.

- [ ] **Step 3: Commit**

```bash
git add backend/xml_to_html.py backend/tests/test_xml_to_html.py
git commit -m "feat: add xml_to_html converter for browsable HTML trees"
```

---

### Task 3: API route + integration tests (TDD)

**Files:**
- Modify: `backend/tests/test_app.py`
- Modify: `backend/app.py`

- [ ] **Step 1: Add failing API tests to `backend/tests/test_app.py`**

Append:

```python
def test_xml_to_html_json_success(client):
    resp = client.post(
        "/api/xml-to-html",
        json={"xmlText": "<root><child>hi</child></root>"},
    )
    assert resp.status_code == 200
    data = resp.get_json()
    assert "html" in data
    assert "<!DOCTYPE html>" in data["html"]
    assert "child" in data["html"]
    assert "hi" in data["html"]


def test_xml_to_html_missing_input_returns_400(client):
    resp = client.post("/api/xml-to-html", json={})
    assert resp.status_code == 400
    assert "error" in resp.get_json()


def test_xml_to_html_invalid_xml_returns_400(client):
    resp = client.post("/api/xml-to-html", json={"xmlText": "<root><x>"})
    assert resp.status_code == 400
    assert "error" in resp.get_json()


def test_xml_to_html_multipart_file(client):
    data = {
        "file": (io.BytesIO(b"<note><body>ok</body></note>"), "note.xml"),
    }
    resp = client.post(
        "/api/xml-to-html",
        data=data,
        content_type="multipart/form-data",
    )
    assert resp.status_code == 200
    assert "ok" in resp.get_json()["html"]
```

Add at top of `test_app.py` if missing:

```python
import io
```

- [ ] **Step 2: Run new tests — expect fail (404)**

```bash
cd backend && source .venv/bin/activate && python -m pytest tests/test_app.py -k xml_to_html -v
```

Expected: FAIL (404 or route missing).

- [ ] **Step 3: Implement route in `backend/app.py`**

Add import:

```python
from xml_to_html import xml_to_html, XmlToHtmlError
```

Add route (keep existing `/api/generate` untouched):

```python
@app.route("/api/xml-to-html", methods=["POST"])
def convert_xml_to_html():
    xml_text = ""

    if request.content_type and request.content_type.startswith("multipart/form-data"):
        uploaded_file = request.files.get("file")
        xml_text = request.form.get("xmlText", "") or ""
        if uploaded_file:
            uploaded_file.stream.seek(0, 2)
            size = uploaded_file.stream.tell()
            uploaded_file.stream.seek(0)
            if size > MAX_FILE_SIZE:
                return jsonify({"error": "Uploaded file exceeds the 5 MB limit."}), 400
            file_bytes = uploaded_file.read()
            try:
                file_text = file_bytes.decode("utf-8")
            except UnicodeDecodeError:
                return jsonify({"error": "Uploaded file must be UTF-8 text XML."}), 400
            xml_text = xml_text or file_text
    else:
        data = request.get_json(silent=True) or {}
        xml_text = data.get("xmlText", "") or ""

    if not xml_text.strip():
        return jsonify({"error": "xmlText or uploaded XML file is required."}), 400

    if len(xml_text) > MAX_INPUT_LENGTH:
        return jsonify({"error": f"Input exceeds the {MAX_INPUT_LENGTH // 1000}k character limit."}), 400

    try:
        html_doc = xml_to_html(xml_text)
        return jsonify({"html": html_doc})
    except XmlToHtmlError as exc:
        return jsonify({"error": str(exc)}), 400
    except Exception as exc:
        return jsonify({"error": str(exc)}), 500
```

- [ ] **Step 4: Run API + full backend tests**

```bash
cd backend && source .venv/bin/activate && python -m pytest tests/ -v
```

Expected: all PASS (existing generate tests still green).

- [ ] **Step 5: Commit**

```bash
git add backend/app.py backend/tests/test_app.py
git commit -m "feat: add POST /api/xml-to-html endpoint"
```

---

### Task 4: Frontend mode tab + XML → HTML UI

**Files:**
- Modify: `frontend/app/page.tsx`
- Modify: `frontend/app/globals.css`

- [ ] **Step 1: Add mode state and XML state alongside existing generate state**

In `frontend/app/page.tsx`, after existing `useState` hooks, add:

```tsx
type AppMode = "generate" | "xmlToHtml";

const [mode, setMode] = useState<AppMode>("generate");
const [xmlText, setXmlText] = useState(`<catalog>
  <book id="1">The Hobbit</book>
</catalog>`);
const [xmlFile, setXmlFile] = useState<File | null>(null);
const [htmlOutput, setHtmlOutput] = useState("");
const [xmlStatus, setXmlStatus] = useState("Ready to convert XML.");
const [xmlLoading, setXmlLoading] = useState(false);
```

- [ ] **Step 2: Add convert / download / copy / clear handlers**

```tsx
async function handleXmlConvert() {
  if (!xmlText.trim() && !xmlFile) return;
  setXmlStatus("Converting XML to HTML...");
  setXmlLoading(true);
  try {
    let response: Response;
    if (xmlFile) {
      const formData = new FormData();
      formData.append("file", xmlFile);
      if (xmlText.trim()) formData.append("xmlText", xmlText);
      response = await fetch("http://localhost:5002/api/xml-to-html", {
        method: "POST",
        body: formData,
      });
    } else {
      response = await fetch("http://localhost:5002/api/xml-to-html", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ xmlText }),
      });
    }
    const json = await response.json();
    if (!response.ok) {
      setXmlStatus(json.error || "Conversion failed.");
      setHtmlOutput("");
    } else {
      setHtmlOutput(json.html || "");
      setXmlStatus("HTML generated successfully.");
    }
  } catch {
    setXmlStatus("Server request failed. Is the backend running?");
    setHtmlOutput("");
  } finally {
    setXmlLoading(false);
  }
}

function handleHtmlDownload() {
  const blob = new Blob([htmlOutput], { type: "text/html;charset=utf-8" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = "converted.html";
  a.click();
  URL.revokeObjectURL(url);
  setXmlStatus("Downloaded converted.html.");
}

function handleHtmlCopy() {
  navigator.clipboard.writeText(htmlOutput);
  setXmlStatus("Copied HTML to clipboard.");
}

function handleXmlClear() {
  setXmlText("");
  setXmlFile(null);
  setHtmlOutput("");
  setXmlStatus("Cleared.");
}
```

- [ ] **Step 3: Render mode switch and conditional panels**

At the top of the main return (before existing generate UI), add tabs. Wrap the existing generate UI in `mode === "generate"` and add XML panel for `mode === "xmlToHtml"`:

```tsx
<div className="mode-tabs" role="tablist">
  <button
    type="button"
    role="tab"
    className={mode === "generate" ? "mode-tab active" : "mode-tab"}
    aria-selected={mode === "generate"}
    onClick={() => setMode("generate")}
  >
    API Generate
  </button>
  <button
    type="button"
    role="tab"
    className={mode === "xmlToHtml" ? "mode-tab active" : "mode-tab"}
    aria-selected={mode === "xmlToHtml"}
    onClick={() => setMode("xmlToHtml")}
  >
    XML → HTML
  </button>
</div>

{mode === "generate" ? (
  <>{/* existing generate JSX unchanged */}</>
) : (
  <div className="xml-panel">
    <label className="field-label">XML input</label>
    <textarea
      value={xmlText}
      onChange={(e) => setXmlText(e.target.value)}
      rows={12}
      spellCheck={false}
    />
    <input
      type="file"
      accept=".xml,text/xml,application/xml"
      onChange={(e) => setXmlFile(e.target.files?.[0] ?? null)}
    />
    <div className="actions">
      <button type="button" onClick={handleXmlConvert} disabled={xmlLoading}>
        {xmlLoading ? "Converting…" : "Convert"}
      </button>
      <button type="button" onClick={handleHtmlDownload} disabled={!htmlOutput}>
        Download
      </button>
      <button type="button" onClick={handleHtmlCopy} disabled={!htmlOutput}>
        Copy
      </button>
      <button type="button" onClick={handleXmlClear}>
        Clear
      </button>
    </div>
    <p className="status">{xmlStatus}</p>
    {htmlOutput ? (
      <iframe
        className="html-preview"
        title="HTML preview"
        sandbox=""
        srcDoc={htmlOutput}
      />
    ) : null}
  </div>
)}
```

Reuse existing class names from generate UI where they already match (`actions`, `status`, etc.) so the tab looks consistent.

- [ ] **Step 4: Add CSS in `frontend/app/globals.css`**

```css
.mode-tabs {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 1rem;
}

.mode-tab {
  border: 1px solid #ccc;
  background: #f5f5f5;
  padding: 0.4rem 0.9rem;
  cursor: pointer;
  border-radius: 4px 4px 0 0;
}

.mode-tab.active {
  background: #fff;
  border-bottom-color: #fff;
  font-weight: 600;
}

.html-preview {
  width: 100%;
  min-height: 28rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  background: #fff;
  margin-top: 0.75rem;
}
```

- [ ] **Step 5: Manual smoke check**

```bash
# terminal 1
cd backend && source .venv/bin/activate && python app.py

# terminal 2
cd frontend && npm run dev
```

Verify: tab switch keeps generate state; Convert shows preview; Download saves `converted.html`; curl still works:

```bash
curl -s -X POST http://localhost:5002/api/xml-to-html \
  -H "Content-Type: application/json" \
  -d '{"xmlText":"<root>ok</root>"}' | head -c 200
```

- [ ] **Step 6: Commit**

```bash
git add frontend/app/page.tsx frontend/app/globals.css
git commit -m "feat: add XML to HTML tab with preview and download"
```

---

### Task 5: README docs

**Files:**
- Modify: `README.md`

- [ ] **Step 1: Document the feature**

After the existing `/api/generate` section, add:

```markdown
### `POST /api/xml-to-html`

Convert well-formed XML into a standalone browsable HTML document.

#### JSON request

```http
POST /api/xml-to-html
Content-Type: application/json

{ "xmlText": "<catalog><book id=\"1\">The Hobbit</book></catalog>" }
```

#### Multipart request

```http
POST /api/xml-to-html
Content-Type: multipart/form-data

file=<file.xml>
xmlText=<optional override>
```

\* Either `xmlText` or `file` is required. Non-empty `xmlText` wins over file contents.

**Limits:** same as generate — 50k characters / 5 MB file.

#### Response `200 OK`

```json
{ "html": "<!DOCTYPE html>..." }
```

#### Example — curl

```bash
curl -X POST http://localhost:5002/api/xml-to-html \
  -H "Content-Type: application/json" \
  -d '{"xmlText":"<root><item>hi</item></root>"}'
```

#### UI

In the frontend, switch to the **XML → HTML** tab, paste or upload XML, click **Convert**, then preview / download / copy.
```

Also update the top Usage section with a short bullet about the XML → HTML tab.

- [ ] **Step 2: Commit**

```bash
git add README.md
git commit -m "docs: document XML to HTML API and UI tab"
```

---

## Spec coverage checklist

| Spec requirement | Task |
|------------------|------|
| `xml_to_html.py` converter | Task 2 |
| `POST /api/xml-to-html` JSON + multipart | Task 3 |
| Limits 50k / 5 MB | Task 3 |
| Errors 400/500 `{ error }` | Task 3 |
| Escape text; no script execution | Tasks 1–2 |
| Generic XML (not VB-specific) | Tasks 1–2 |
| Same-page mode tab | Task 4 |
| Preview + download + copy | Task 4 |
| API usable without frontend | Tasks 3, 5 |
| Unit + API tests | Tasks 1, 3 |
| README | Task 5 |
| Do not break `/api/generate` | Task 3 full pytest |

---

## Self-review notes

- No TBD/placeholder steps; function names consistent (`xml_to_html`, `XmlToHtmlError`, field `xmlText`, response `html`).
- Plan uses `docs/plans/` (not `docs/superpowers/plans/`) because `docs/superpowers/` is gitignored in this repo.
