# Backend for API Controller Generator

## Setup

1. Create a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Run the server:

```bash
python app.py
```

## API

POST /api/generate

Supports raw JSON/text input and PDF uploads. When sending a PDF, use `multipart/form-data` with the `file` field and optional `inputText`.

Request body:

```json
{
  "inputText": "GET /api/quizzes\nResponse:\n[ ... ]",
  "language": "csharp"
}
```

Response:

```json
{
  "controllerCode": "..."
}
```
