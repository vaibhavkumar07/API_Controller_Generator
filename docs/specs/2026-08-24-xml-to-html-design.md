# XML → HTML Design

**Date:** 2026-08-24  
**Branch:** `feature/xmltohtml`  
**Status:** Approved for implementation planning

## Problem

Users need to turn well-formed XML into a standalone, browsable HTML file. Example input: legacy VBScript embedded in XML. The converter must not be VBScript-specific — any well-formed XML file or text must work. Clients must be able to call the backend API directly (curl/Postman) or use the Next.js UI.

## Goals

- Accept XML via paste, `.xml` upload, or API-only JSON/multipart
- Emit a complete HTML document that opens in a browser and mirrors XML structure
- Preserve text node content (including script/code) as readable escaped text — never execute it
- Fit existing Flask + Next.js patterns without changing `/api/generate` behavior

## Non-goals

- VBScript → JavaScript translation or execution
- XSLT, XSD validation, or schema-specific mapping
- Syntax highlighting
- Auth, rate limiting, OpenAPI
- Changing the existing controller/classes generator API

## Approach

Dedicated module + new route (Approach 1):

- `backend/xml_to_html.py` — parse and render
- `POST /api/xml-to-html` — HTTP surface
- Frontend mode tab on the existing `/` page

## Architecture

```
Frontend tab ──┐
               ├──► POST /api/xml-to-html ──► xml_to_html.py ──► { html }
curl/Postman ──┘
```

Existing `POST /api/generate` stays unchanged.

## API

**Endpoint:** `POST /api/xml-to-html`  
**Base URL:** `http://localhost:5002`

### JSON

```http
POST /api/xml-to-html
Content-Type: application/json

{ "xmlText": "<catalog><book id=\"1\">The Hobbit</book></catalog>" }
```

### Multipart

```http
POST /api/xml-to-html
Content-Type: multipart/form-data

file=<file.xml>
xmlText=<optional override>
```

Precedence: non-empty `xmlText` wins over file contents (same pattern as `/api/generate`).

### Limits

Reuse existing constants from `app.py`:

- `MAX_INPUT_LENGTH` = 50,000 characters
- `MAX_FILE_SIZE` = 5 MB

### Success `200`

```json
{ "html": "<!DOCTYPE html>..." }
```

### Errors

| Status | Cause |
|--------|--------|
| 400 | Missing input, oversize, malformed XML |
| 500 | Unexpected conversion failure |

Body: `{ "error": "..." }`

## Conversion rules (`xml_to_html.py`)

- Parse with stdlib `xml.etree.ElementTree` (no external entity expansion)
- Malformed XML → raise/return clear error → API `400`
- Element → nested `<section class="xml-node">` with tag name
- Attributes → escaped label chips next to the tag name
- Text / tail → escaped content in a block (monospace-friendly CSS for long code/script text)
- Output: full HTML document (`<!DOCTYPE html>`, charset, title from root tag name, light indent CSS)
- No `<script>` in generated output; text that looks like script is escaped display only

## Frontend

File: `frontend/app/page.tsx` (+ `globals.css` as needed)

- Top mode switch: **API Generate** | **XML → HTML**
- Generate mode: current UI unchanged; state kept when switching tabs
- XML → HTML mode:
  - Textarea for paste + file input (`accept` for `.xml` / XML MIME types)
  - **Convert** → `POST http://localhost:5002/api/xml-to-html` (JSON if no file; `FormData` if file)
  - Preview: `iframe` with `srcDoc={html}` and restrictive `sandbox`
  - **Download** `converted.html` via Blob, **Copy** source, **Clear**

## Testing

- `backend/tests/test_xml_to_html.py` — unit: nested tree, attributes, text escaping (`<`, `&`), invalid XML
- Extend `backend/tests/test_app.py` — JSON success, multipart `.xml`, missing input `400`, invalid XML `400`

## Documentation

Update root `README.md` with `POST /api/xml-to-html` (JSON, multipart, curl). Mention UI tab.

## Clarification (product)

Legacy VBScript-in-XML is a motivating example only. Implementation is schema-agnostic: all well-formed XML files/text are supported the same way.
