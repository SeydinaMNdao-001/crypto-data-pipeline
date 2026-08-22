"""
Connexion et écriture PostgreSQL — section 9 du document projet.
"""
import logging
from contextlib import contextmanager

import psycopg2
from psycopg2.extras import execute_values

from src.utils.config import POSTGRES_CONFIG

logger = logging.getLogger("utils.db")


@contextmanager
def get_connection():
    conn = psycopg2.connect(
        user=POSTGRES_CONFIG["user"],
        password=POSTGRES_CONFIG["password"],
        dbname=POSTGRES_CONFIG["dbname"],
        host=POSTGRES_CONFIG["host"],
        port=POSTGRES_CONFIG["port"],
    )
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


INSERT_SNAPSHOT_SQL = """
    INSERT INTO crypto_market_snapshot
        (asset_id, symbol, timestamp, ingestion_time, price_usd, price_xof,
         volume_24h, market_cap, change_24h, source)
    VALUES %s
"""


def insert_snapshot_records(records: list, fx_rate: float = None) -> int:
    """
    Insère une liste de dicts normalisés (sortie des collecteurs) dans
    crypto_market_snapshot. Si fx_rate (USD -> XOF) est fourni, calcule
    price_xof au passage. Retourne le nombre de lignes insérées.
    """
    if not records:
        return 0

    rows = []
    for r in records:
        price_xof = round(r["price_usd"] * fx_rate, 4) if fx_rate else None
        rows.append((
            r["asset_id"], r["symbol"], r["timestamp"], r["ingestion_time"],
            r["price_usd"], price_xof, r["volume_24h"], r["market_cap"],
            r["change_24h"], r["source"],
        ))

    with get_connection() as conn:
        with conn.cursor() as cur:
            execute_values(cur, INSERT_SNAPSHOT_SQL, rows)

    logger.info("Inséré %d lignes dans crypto_market_snapshot", len(rows))
    return len(rows)
