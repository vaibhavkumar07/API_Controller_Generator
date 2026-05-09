# API Controller Generator

This repository contains a full-stack tool for generating controller code from API endpoint definitions.

## Structure

- `frontend/` - Next.js + TypeScript user interface
- `backend/` - Flask API service for parsing input and generating controller code

## Setup

### Backend

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Open the frontend on `http://localhost:3000` and the backend on `http://localhost:5000`.

## Usage

- Paste endpoint definitions into the input box
- Or upload a PDF containing API definitions
- Choose the target language
- Click Generate
- Copy or download the generated controller code
