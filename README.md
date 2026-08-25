# API Framework

Full-stack toolkit: generate server controller + client caller code from API endpoint definitions, and convert well-formed XML into standalone HTML.

## Structure

- `frontend/` — Next.js + TypeScript UI (tool switcher + panels)
- `backend/` — Flask app factory, versioned Blueprints (`/api/v1`), OpenAPI via Flasgger

---

## Setup

### Backend

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

**Local debug**

```bash
python run.py
```

**Production-style (gunicorn)**

```bash
gunicorn -w 2 -b 0.0.0.0:5002 wsgi:app
```

Backend default: `http://localhost:5002`.

**Environment variables (optional)**

| Variable | Default | Meaning |
|---|---|---|
| `PORT` | `5002` | Port used by `run.py` |
| `FLASK_DEBUG` | `0` | `1`/`true` enables Flask debug in `run.py` |
| `MAX_INPUT_LENGTH` | `50000` | Max characters for text inputs |
| `MAX_FILE_SIZE` | `5242880` | Max upload bytes (5 MB) |
| `CORS_ORIGINS` | `*` | Comma-separated origins, or `*` |

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Optional: `NEXT_PUBLIC_API_BASE=http://localhost:5002` (default).

Frontend: `http://localhost:3000`.

---

## Usage

1. Open the app — brand header shows **API Generate** / **XML → HTML** and an **API Docs** link (Swagger UI).
2. **API Generate** — paste endpoints (or upload PDF), click **Generate**, use Controller/Classes panels (copy / download / clear).
3. **XML → HTML** — paste or upload XML, **Convert**, then preview / download / copy.
4. Interactive API docs: [http://localhost:5002/api/docs](http://localhost:5002/api/docs)

### Supported generate input formats

```
GET /api/users
POST /api/users
PUT /api/users/{id}
DELETE /api/users/{id}
```

Plain text, JSON with endpoint fields, or a PDF containing endpoint definitions.

---

## Backend API

Base URL: `http://localhost:5002`

Canonical routes are under **`/api/v1`**. Legacy aliases `/api/generate` and `/api/xml-to-html` still work.

| Method | Path | Purpose |
|---|---|---|
| `GET` | `/health` | Liveness `{ "status": "ok" }` |
| `GET` | `/api/docs` | Swagger UI |
| `GET` | `/api/apispec.json` | OpenAPI JSON |
| `POST` | `/api/v1/generate` | Controller + classes codegen |
| `POST` | `/api/v1/xml-to-html` | XML → HTML |

### `POST /api/v1/generate`

#### JSON request

```http
POST /api/v1/generate
Content-Type: application/json

{
  "inputText": "GET /api/users\nPOST /api/users",
  "language": "csharp",
  "classesLang": "javascript"
}
```

#### Multipart request (PDF upload)

```http
POST /api/v1/generate
Content-Type: multipart/form-data

file=<pdf>
language=csharp
classesLang=javascript
```

| Field | Type | Required | Default | Values |
|---|---|---|---|---|
| `inputText` | string | yes* | — | Free-text endpoint definitions |
| `file` | file | yes* | — | PDF containing endpoint definitions |
| `language` | string | no | `csharp` | `csharp`, `java`, `python` |
| `classesLang` | string | no | `javascript` | `javascript`, `typescript`, `python`, `csharp`, `java` |

\* Either `inputText` or `file` is required. Non-empty `inputText` wins over PDF text.

**Limits:** 50k characters / 5 MB file (override via env).

#### Response `200 OK`

```json
{
  "controllerCode": "...",
  "classesCode": "...",
  "language": "csharp",
  "classesLang": "javascript"
}
```

#### Example — curl

```bash
curl -X POST http://localhost:5002/api/v1/generate \
  -H "Content-Type: application/json" \
  -d '{
    "inputText": "GET /api/users\nPOST /api/users",
    "language": "python",
    "classesLang": "typescript"
  }'
```

### `POST /api/v1/xml-to-html`

#### JSON request

```http
POST /api/v1/xml-to-html
Content-Type: application/json

{
  "xmlText": "<catalog><book id=\"1\">The Hobbit</book></catalog>"
}
```

#### Multipart request

```http
POST /api/v1/xml-to-html
Content-Type: multipart/form-data

file=<file.xml>
xmlText=<optional override>
```

\* Either `xmlText` or `file` is required. Non-empty `xmlText` wins.

#### Response `200 OK`

```json
{ "html": "<!DOCTYPE html>..." }
```

#### Example — curl

```bash
curl -X POST http://localhost:5002/api/v1/xml-to-html \
  -H "Content-Type: application/json" \
  -d '{"xmlText":"<catalog><book id=\"1\">The Hobbit</book></catalog>"}'
```

---

## Running Tests

```bash
cd backend
source .venv/bin/activate
python -m pytest tests/ -v
```

44 tests covering generators, XML→HTML, versioned + legacy API routes, health, and Swagger docs.

---

## License

MIT © [Vaibhavkumar Yadav](https://github.com/vaibhavkumar07)
