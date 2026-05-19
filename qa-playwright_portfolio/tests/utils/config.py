from __future__ import annotations

import os


def get_app_base_url() -> str:
    return os.getenv("APP_BASE_URL", "http://localhost:5500").rstrip("/")


def get_api_base_url() -> str:
    return os.getenv("API_BASE_URL", "http://localhost:8000").rstrip("/")
