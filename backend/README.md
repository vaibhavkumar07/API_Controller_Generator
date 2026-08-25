# Backend

Flask app factory with versioned Blueprints.

## Run

```bash
source .venv/bin/activate
pip install -r requirements.txt

# debug
python run.py

# production-style
gunicorn -w 2 -b 0.0.0.0:5002 wsgi:app
```

- API: `http://localhost:5002/api/v1/...`
- Docs: `http://localhost:5002/api/docs`
- Health: `http://localhost:5002/health`

## Tests

```bash
python -m pytest tests/ -v
```
