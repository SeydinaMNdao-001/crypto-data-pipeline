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


def get_latest_by_symbol(symbol: str, source: str = "coingecko"):
    """Dernier enregistrement connu pour un actif (source canonique : CoinGecko)."""
    query = """
        SELECT asset_id, symbol, timestamp, ingestion_time, price_usd, price_xof,
               volume_24h, market_cap, change_24h, source
        FROM crypto_market_snapshot
        WHERE symbol = %s AND source = %s
        ORDER BY ingestion_time DESC
        LIMIT 1
    """
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, (symbol, source))
            row = cur.fetchone()
            if row is None:
                return None
            columns = [desc[0] for desc in cur.description]
            return dict(zip(columns, row))


def get_history_by_symbol(symbol: str, hours: int, source: str = "coingecko"):
    """Historique d'un actif sur les N dernières heures."""
    query = """
        SELECT asset_id, symbol, timestamp, ingestion_time, price_usd, price_xof,
               volume_24h, market_cap, change_24h, source
        FROM crypto_market_snapshot
        WHERE symbol = %s AND source = %s
          AND ingestion_time >= NOW() - (%s || ' hours')::INTERVAL
        ORDER BY ingestion_time ASC
    """
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, (symbol, source, hours))
            rows = cur.fetchall()
            columns = [desc[0] for desc in cur.description]
            return [dict(zip(columns, r)) for r in rows]


def get_market_summary(source: str = "coingecko"):
    """Synthèse du marché à l'instant du dernier cycle de collecte."""
    query = """
        SELECT COUNT(DISTINCT symbol) AS total_assets,
               SUM(market_cap) AS total_market_cap_usd,
               AVG(change_24h) AS average_change_24h,
               MAX(ingestion_time) AS last_updated
        FROM crypto_market_snapshot
        WHERE source = %s
          AND ingestion_time = (
              SELECT MAX(ingestion_time) FROM crypto_market_snapshot WHERE source = %s
          )
    """
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, (source, source))
            row = cur.fetchone()
            columns = [desc[0] for desc in cur.description]
            return dict(zip(columns, row))


INSERT_PEG_SQL = """
    INSERT INTO stablecoin_peg_history
        (asset_id, timestamp, price_usd, peg_deviation, seuil_alerte_franchi)
    VALUES %s
"""


def insert_peg_records(records: list) -> int:
    """Insère les écarts de peg calculés dans stablecoin_peg_history."""
    if not records:
        return 0

    rows = [
        (r["asset_id"], r["timestamp"], r["price_usd"], r["peg_deviation"], r["seuil_alerte_franchi"])
        for r in records
    ]

    with get_connection() as conn:
        with conn.cursor() as cur:
            execute_values(cur, INSERT_PEG_SQL, rows)

    logger.info("Inséré %d lignes dans stablecoin_peg_history", len(rows))
    return len(rows)


def get_metrics_by_symbol(symbol: str, source: str = "coingecko", lookback_days: int = 7):
    """
    Calcule les indicateurs analytiques (section 10) pour un actif, à la volée,
    via des fonctions fenêtrées PostgreSQL — rien n'est pré-calculé ni stocké.
    """
    query = """
        WITH history AS (
            SELECT ingestion_time, price_usd
            FROM crypto_market_snapshot
            WHERE symbol = %s AND source = %s
              AND ingestion_time >= NOW() - (%s || ' days')::INTERVAL
            ORDER BY ingestion_time
        ),
        returns AS (
            SELECT
                ingestion_time,
                price_usd,
                (price_usd - LAG(price_usd) OVER (ORDER BY ingestion_time))
                    / NULLIF(LAG(price_usd) OVER (ORDER BY ingestion_time), 0) AS pct_return
            FROM history
        ),
        enriched AS (
            SELECT
                ingestion_time,
                price_usd,
                AVG(price_usd) OVER (
                    ORDER BY ingestion_time
                    RANGE BETWEEN INTERVAL '7 days' PRECEDING AND CURRENT ROW
                ) AS moving_avg_7d,
                STDDEV(pct_return) OVER (
                    ORDER BY ingestion_time
                    RANGE BETWEEN INTERVAL '7 days' PRECEDING AND CURRENT ROW
                ) AS rolling_volatility,
                MAX(price_usd) OVER (
                    ORDER BY ingestion_time
                    ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
                ) AS running_max
            FROM returns
        ),
        drawdowns AS (
            SELECT (price_usd - running_max) / NULLIF(running_max, 0) AS drawdown
            FROM enriched
        )
        SELECT
            (SELECT price_usd FROM enriched ORDER BY ingestion_time DESC LIMIT 1) AS price_usd,
            (SELECT change_24h FROM crypto_market_snapshot
                WHERE symbol = %s AND source = %s ORDER BY ingestion_time DESC LIMIT 1) AS change_24h_pct,
            (SELECT price_usd FROM crypto_market_snapshot
                WHERE symbol = %s AND source = %s
                ORDER BY ABS(EXTRACT(EPOCH FROM (ingestion_time - (NOW() - INTERVAL '1 hour'))))
                LIMIT 1) AS price_1h_ago,
            (SELECT moving_avg_7d FROM enriched ORDER BY ingestion_time DESC LIMIT 1) AS moving_average_7d,
            (SELECT rolling_volatility FROM enriched ORDER BY ingestion_time DESC LIMIT 1) AS rolling_volatility,
            (SELECT MIN(drawdown) FROM drawdowns) AS max_drawdown
    """
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, (symbol, source, lookback_days, symbol, source, symbol, source))
            row = cur.fetchone()
            if row is None or row[0] is None:
                return None
            columns = [desc[0] for desc in cur.description]
            result = dict(zip(columns, row))

    price_usd = float(result["price_usd"])
    price_1h_ago = float(result["price_1h_ago"]) if result["price_1h_ago"] else None
    change_1h_pct = round((price_usd - price_1h_ago) / price_1h_ago * 100, 4) if price_1h_ago else None

    return {
        "symbol": symbol,
        "price_usd": price_usd,
        "change_1h_pct": change_1h_pct,
        "change_24h_pct": float(result["change_24h_pct"]) if result["change_24h_pct"] is not None else None,
        "moving_average_7d": float(result["moving_average_7d"]) if result["moving_average_7d"] else None,
        "rolling_volatility": float(result["rolling_volatility"]) if result["rolling_volatility"] else None,
        "max_drawdown_pct": round(float(result["max_drawdown"]) * 100, 4) if result["max_drawdown"] is not None else None,
    }


def get_market_ranking(metric: str = "change_24h", source: str = "coingecko", lookback_days: int = 1):
    """
    Classe les 12 actifs selon un indicateur (section 10). Une seule requête
    calcule les métriques des 12 actifs à la fois, plutôt que 12 appels
    séparés à get_metrics_by_symbol (évite le problème classique du "N+1").
    """
    query = """
        WITH history AS (
            SELECT symbol, ingestion_time, price_usd, volume_24h, change_24h,
                   (price_usd - LAG(price_usd) OVER (PARTITION BY symbol ORDER BY ingestion_time))
                     / NULLIF(LAG(price_usd) OVER (PARTITION BY symbol ORDER BY ingestion_time), 0) AS pct_return
            FROM crypto_market_snapshot
            WHERE source = %s
              AND ingestion_time >= NOW() - (%s || ' days')::INTERVAL
        ),
        latest AS (
            SELECT DISTINCT ON (symbol) symbol, price_usd, volume_24h, change_24h, ingestion_time
            FROM history
            ORDER BY symbol, ingestion_time DESC
        ),
        vol AS (
            SELECT symbol, STDDEV(pct_return) AS rolling_volatility
            FROM history
            GROUP BY symbol
        )
        SELECT l.symbol, l.price_usd, l.change_24h, l.volume_24h, v.rolling_volatility
        FROM latest l
        JOIN vol v USING (symbol)
    """
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, (source, lookback_days))
            rows = cur.fetchall()
            columns = [desc[0] for desc in cur.description]
            results = [dict(zip(columns, r)) for r in rows]

    metric_map = {"change_24h": "change_24h", "volatility": "rolling_volatility", "volume": "volume_24h"}
    sort_field = metric_map.get(metric, "change_24h")

    def sort_key(item):
        value = item[sort_field]
        return float(value) if value is not None else float("-inf")

    ranked = sorted(results, key=sort_key, reverse=True)

    output = []
    for i, r in enumerate(ranked, start=1):
        output.append({
            "rank": i,
            "symbol": r["symbol"],
            "price_usd": float(r["price_usd"]),
            "change_24h_pct": float(r["change_24h"]) if r["change_24h"] is not None else None,
            "rolling_volatility": float(r["rolling_volatility"]) if r["rolling_volatility"] is not None else None,
            "volume_24h": float(r["volume_24h"]) if r["volume_24h"] is not None else None,
        })
    return output
