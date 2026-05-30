# Classes Panel — Design Spec
**Date:** 2026-05-30  
**Status:** Approved

---

## Overview

Add a third output panel ("Classes") that generates client-side caller code alongside the existing controller output. Both panels are generated from the same raw input in a single backend call. Each panel has its own independent language selector in its header.

---

## Architecture

### Approach
Unified endpoint (Approach 1): single `POST /api/generate` call returns both `controllerCode` and `classesCode`. Language change in either panel header triggers full re-generation.

### Files Changed

| File | Change |
|---|---|
| `backend/generator.py` | Add `generate_classes(endpoints, language)` |
| `backend/app.py` | Accept `classesLang`, return `classesCode` |
| `frontend/app/page.tsx` | New layout, classes panel, dual selectors, new state |
| `frontend/app/globals.css` | `.input-section`, `.outputs-row` layout classes |

---

## Backend

### API Contract

**Request** (multipart or JSON):
```json
{
  "inputText": "GET /api/users\nPOST /api/users",
  "language": "csharp",
  "classesLang": "javascript"
}
```
`classesLang` defaults to `"javascript"` if omitted — backward compatible.

**Response:**
```json
{
  "controllerCode": "...",
  "classesCode": "...",
  "language": "csharp",
  "classesLang": "javascript"
}
```

### `generator.py` — `generate_classes(endpoints, language)`

`SUPPORTED_CLASS_LANGUAGES = {"javascript", "typescript", "python", "csharp", "java"}`

Generates one caller function per endpoint. Each function includes error handling.

| Language | HTTP client | Error handling |
|---|---|---|
| `javascript` | `fetch` async/await | try/catch, throw on non-2xx |
| `typescript` | `fetch` async/await | try/catch, typed response cast, `Promise<void>` return type |
| `python` | `requests` | try/except `RequestException`, `raise_for_status()` |
| `csharp` | `HttpClient` async | try/catch `Exception`, `EnsureSuccessStatusCode()` |
| `java` | `java.net.http.HttpClient` | throws declaration, check status code |

Method coverage: GET, POST, PUT, DELETE (unsupported methods emit a comment placeholder).

POST/PUT functions include a sample request body derived from the endpoint model name.

### `app.py` changes

Extract `classesLang` from both multipart form-data and JSON paths. Call `generate_classes(endpoints, classes_lang)`. Include `classesCode` and `classesLang` in response JSON.

---

## Frontend

### Layout

```
page-shell
├── hero-panel (unchanged)
├── input-section (full width)
│   └── card input-card
│       ├── textarea (API endpoint input)
│       ├── PDF upload row
│       └── controls-row: [Generate button]
└── outputs-row (flex row, gap 1rem)
    ├── card controller-card (flex: 1)
    │   ├── header: "Controller" + language <select>
    │   ├── output-actions: Copy | Download | Clear
    │   └── <pre> controller code </pre>
    └── card classes-card (flex: 1)
        ├── header: "Classes" + language <select>
        ├── output-actions: Copy | Download | Clear
        └── <pre> classes code </pre>
```

Language selector moves from input card to each output card header. Generate button stays in input card.

### State

```typescript
// existing
const [inputText, setInputText] = useState(defaultInput);
const [language, setLanguage] = useState("csharp");       // controller lang
const [output, setOutput] = useState("");
const [status, setStatus] = useState("Ready to generate.");
const [isLoading, setIsLoading] = useState(false);
const [uploadedFile, setUploadedFile] = useState<File | null>(null);

// new
const [classesLang, setClassesLang] = useState("javascript");
const [classesOutput, setClassesOutput] = useState("");
```

### Language Arrays

```typescript
const controllerLanguages = [
  { value: "csharp", label: "C# (.NET)" },
  { value: "java", label: "Java (Spring Boot)" },
  { value: "python", label: "Python (Flask)" },
];

const classesLanguages = [
  { value: "javascript", label: "JavaScript" },
  { value: "typescript", label: "TypeScript" },
  { value: "python", label: "Python" },
  { value: "csharp", label: "C#" },
  { value: "java", label: "Java" },
];
```

### `handleGenerate` update

Sends `classesLang` in request. On success sets both `output` and `classesOutput`. Status: `"Controller and classes generated successfully."` On error: clears both outputs.

### Language change re-generation

`useEffect` watches `[language, classesLang]` — if either output already exists, re-triggers `handleGenerate` automatically.

### Per-panel actions

| Action | Controller | Classes |
|---|---|---|
| Copy | copies `output` | copies `classesOutput` |
| Download | `controller-{lang}.txt` | `classes-{lang}.txt` |
| Clear | clears `output` | clears `classesOutput` |

### CSS additions (`globals.css`)

```css
.input-section {
  width: 100%;
  margin-bottom: 1rem;
}

.outputs-row {
  display: flex;
  gap: 1rem;
  width: 100%;
}

.outputs-row > .card {
  flex: 1;
  min-width: 0;
}
```

---

## Error Handling

- Invalid `classesLang` → backend returns 400 with error message
- Backend down → frontend shows "Server request failed. Is the backend running?"
- No endpoints detected → 400 from existing parse guard (unchanged)
- Empty `classesCode` → classes panel shows placeholder text

---

## Out of Scope

- Streaming output
- Per-panel independent regeneration (both always regenerate together)
- Saving/history of generated outputs
