# API Controller Generator

A full-stack tool that generates server-side controller code **and** client-side caller code from API endpoint definitions.

## Structure

- `frontend/` — Next.js + TypeScript UI
- `backend/` — Flask API (parsing + code generation)

---

## Setup

### Backend

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

Backend runs on `http://localhost:5002`.

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend runs on `http://localhost:3000`.

---

## Usage

1. Paste API endpoint definitions into the **Input** box (or upload a PDF)
2. Click **Generate**
3. **Controller** panel — server-side controller code; pick language from its dropdown (C#, Java, Python)
4. **Classes** panel — client-side caller code; pick language from its dropdown (JavaScript, TypeScript, Python, C#, Java)
5. Use **Copy**, **Download**, or **Clear** per panel independently
6. Changing a language dropdown after generation auto-regenerates that output

### Supported input formats

```
GET /api/users
POST /api/users
PUT /api/users/{id}
DELETE /api/users/{id}
```

Plain text, JSON with endpoint fields, or a PDF document containing endpoint definitions.

---

## Backend API

Base URL: `http://localhost:5002`

### `POST /api/generate`

Generate controller and client caller code from endpoint definitions.

#### JSON request

```http
POST /api/generate
Content-Type: application/json

{
  "inputText": "GET /api/users\nPOST /api/users",
  "language": "csharp",
  "classesLang": "javascript"
}
```

#### Multipart request (PDF upload)

```http
POST /api/generate
Content-Type: multipart/form-data

file=<pdf>
language=csharp
classesLang=javascript
```

#### Parameters

| Field | Type | Required | Default | Values |
|---|---|---|---|---|
| `inputText` | string | yes* | — | Free-text endpoint definitions |
| `file` | file | yes* | — | PDF containing endpoint definitions |
| `language` | string | no | `csharp` | `csharp`, `java`, `python` |
| `classesLang` | string | no | `javascript` | `javascript`, `typescript`, `python`, `csharp`, `java` |

\* Either `inputText` or `file` is required. If both are provided, `inputText` takes precedence.

**Limits:** `inputText` max 50,000 characters. PDF max 5 MB.

#### Response `200 OK`

```json
{
  "controllerCode": "[Route(\"api/[controller]\")]\npublic class UsersController ...",
  "classesCode": "const BASE_URL = 'http://localhost:5001';\n\nasync function getUsers() ...",
  "language": "csharp",
  "classesLang": "javascript"
}
```

#### Error responses

| Status | Cause |
|---|---|
| `400` | Missing input, no endpoints detected, input too large |
| `500` | Unsupported language value or internal generation error |

#### Example — curl

```bash
curl -X POST http://localhost:5002/api/generate \
  -H "Content-Type: application/json" \
  -d '{
    "inputText": "GET /api/users\nPOST /api/users\nDELETE /api/users/{id}",
    "language": "python",
    "classesLang": "typescript"
  }'
```

#### Example — JavaScript fetch

```js
const res = await fetch("http://localhost:5002/api/generate", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({
    inputText: "GET /api/products\nPOST /api/products",
    language: "java",
    classesLang: "javascript",
  }),
});
const { controllerCode, classesCode } = await res.json();
```

---

## Running Tests

```bash
cd backend
source .venv/bin/activate
python -m pytest tests/ -v
```

29 tests covering generator logic (JS, TS, Python, C#, Java) and the API endpoint.
