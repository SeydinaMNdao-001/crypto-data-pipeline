"""
Fixtures partagées — les tests marqués 'integration' ont besoin de
PostgreSQL réellement démarré (docker compose up -d).
"""
import psycopg2
import pytest

from src.utils.config import POSTGRES_CONFIG


@pytest.fixture
def db_connection():
    try:
        conn = psycopg2.connect(**POSTGRES_CONFIG)
    except Exception as exc:
        pytest.skip(f"PostgreSQL non accessible — lance 'docker compose up -d' ({exc})")
    yield conn
    conn.close()
