"""
Tests d'intégration PostgreSQL — section 16. Nécessitent que
'docker compose up -d' tourne (contient PostgreSQL réel, pas simulé).
"""
import pytest

from src.utils.db import insert_snapshot_records

pytestmark = pytest.mark.integration


def test_insert_and_read_round_trip(db_connection):
    record = [{
        "asset_id": "test-roundtrip", "symbol": "TEST", "timestamp": "2026-01-01T00:00:00+00:00",
        "ingestion_time": "2026-01-01T00:00:01+00:00", "price_usd": 42.0, "volume_24h": 1.0,
        "market_cap": 1.0, "change_24h": 0.0, "source": "test",
    }]

    insert_snapshot_records(record)

    with db_connection.cursor() as cur:
        cur.execute("SELECT price_usd FROM crypto_market_snapshot WHERE asset_id = 'test-roundtrip'")
        row = cur.fetchone()

    assert row is not None
    assert float(row[0]) == 42.0

    with db_connection.cursor() as cur:
        cur.execute("DELETE FROM crypto_market_snapshot WHERE asset_id = 'test-roundtrip'")
    db_connection.commit()


def test_duplicate_insert_does_not_create_duplicate_rows(db_connection):
    """
    Simule un retry Airflow qui réinsère le même cycle de collecte —
    ne doit produire qu'une seule ligne, pas deux (section 15 : idempotence).
    """
    record = [{
        "asset_id": "test-idempotence", "symbol": "TEST", "timestamp": "2026-01-01T00:00:00+00:00",
        "ingestion_time": "2026-01-01T00:00:01+00:00", "price_usd": 1.0, "volume_24h": 1.0,
        "market_cap": 1.0, "change_24h": 0.0, "source": "test",
    }]

    insert_snapshot_records(record)
    insert_snapshot_records(record)  # le "retry" qui rejoue la même insertion

    with db_connection.cursor() as cur:
        cur.execute(
            "SELECT COUNT(*) FROM crypto_market_snapshot WHERE asset_id = 'test-idempotence'"
        )
        count = cur.fetchone()[0]

    assert count == 1  # pas 2 — c'est exactement ce que la contrainte UNIQUE garantit

    with db_connection.cursor() as cur:
        cur.execute("DELETE FROM crypto_market_snapshot WHERE asset_id = 'test-idempotence'")
    db_connection.commit()
