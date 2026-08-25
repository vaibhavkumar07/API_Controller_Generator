"""WSGI entrypoint for gunicorn: `gunicorn -w 2 -b 0.0.0.0:5002 wsgi:app`."""

from app import create_app

app = create_app()
