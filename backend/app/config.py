"""Application configuration from environment variables."""

from __future__ import annotations

import os


class Config:
    MAX_INPUT_LENGTH = int(os.environ.get("MAX_INPUT_LENGTH", "50000"))
    MAX_FILE_SIZE = int(os.environ.get("MAX_FILE_SIZE", str(5_242_880)))
    CORS_ORIGINS = os.environ.get("CORS_ORIGINS", "*")
    FLASK_DEBUG = os.environ.get("FLASK_DEBUG", "0") in ("1", "true", "True", "yes")
    PORT = int(os.environ.get("PORT", "5002"))
