"""
Collecteur Binance — sections 6 et 8 du document projet.
Source complémentaire de prix (endpoint public, sans clé API).
USDT est exclu : il n'a pas de paire contre lui-même sur Binance.
"""
import json
import logging
from datetime import datetime, timezone

import requests
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from src.utils.config import ASSETS, BINANCE_BASE_URL


logger = logging.getLogger("collectors.binance")

REQUIRED_FIELDS = ["symbol", "lastPrice", "quoteVolume", "priceChangePercent", "closeTime"]

from datetime import timedelta

MAX_STALENESS = timedelta(minutes=10)




class BinanceCollectorError(Exception):
    """Levée quand la collecte Binance échoue après tous les retries."""


def _tradable_assets():
    """Actifs du périmètre disposant d'une paire directe contre USDT sur Binance."""
    return [a for a in ASSETS if a["binance_pair"]]


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    retry=retry_if_exception_type(requests.exceptions.RequestException),
    reraise=True,
)
def _call_binance_ticker(pairs: list) -> list:
    """Appel brut à /api/v3/ticker/24hr avec retry + backoff exponentiel."""
    response = requests.get(
        f"{BINANCE_BASE_URL}/api/v3/ticker/24hr",
        params={"symbols": json.dumps(pairs, separators=(",", ":"))},
        timeout=10,
    )
    response.raise_for_status()
    return response.json()


def _validate_record(record: dict) -> bool:
    missing = [f for f in REQUIRED_FIELDS if record.get(f) is None]
    if missing:
        logger.warning("Champs manquants pour %s: %s", record.get("symbol"), missing)
        return False

    try:
        price = float(record["lastPrice"])
    except (TypeError, ValueError):
        logger.warning("Prix illisible pour %s", record.get("symbol"))
        return False

    if price <= 0:
        logger.warning(
            "Prix nul ou négatif pour %s — paire probablement inactive sur Binance",
            record.get("symbol")
        )
        return False

    close_time = datetime.fromtimestamp(record["closeTime"] / 1000, tz=timezone.utc)
    age = datetime.now(timezone.utc) - close_time
    if age > MAX_STALENESS:
        logger.warning(
            "Donnée obsolète pour %s : dernière activité il y a %s — paire peu liquide sur Binance",
            record.get("symbol"), age
        )
        return False

    return True


def fetch_binance_snapshot() -> list:
    """
    Récupère un instantané Binance pour les actifs du périmètre disposant
    d'une paire USDT. Retourne une liste normalisée (source='binance').
    """
    tradable = _tradable_assets()
    pair_to_asset = {a["binance_pair"]: a for a in tradable}
    pairs = list(pair_to_asset.keys())

    try:
        raw_data = _call_binance_ticker(pairs)
    except requests.exceptions.RequestException as exc:
        logger.error("Échec de la collecte Binance après retries: %s", exc)
        raise BinanceCollectorError(str(exc)) from exc

    ingestion_time = datetime.now(timezone.utc)
    snapshot = []

    for record in raw_data:
        if not _validate_record(record):
            continue

        asset = pair_to_asset.get(record["symbol"])
        if not asset:
            continue

        close_time = datetime.fromtimestamp(record["closeTime"] / 1000, tz=timezone.utc)

        snapshot.append({
            "asset_id": asset["coingecko_id"],
            "symbol": asset["symbol"],
            "timestamp": close_time.isoformat(),
            "ingestion_time": ingestion_time.isoformat(),
            "price_usd": float(record["lastPrice"]),
            "volume_24h": float(record["quoteVolume"]),
            "market_cap": None,  # Non fourni par paire sur Binance
            "change_1h": None,   # Non disponible sur cet endpoint
            "change_24h": float(record["priceChangePercent"]),
            "source": "binance",
        })

    collected_symbols = {r["symbol"] for r in snapshot}
    expected_symbols = {a["symbol"] for a in tradable}
    missing_assets = expected_symbols - collected_symbols
    if missing_assets:
        logger.warning("Actifs absents de la réponse Binance: %s", missing_assets)

    logger.info(
        "Snapshot Binance: %d/%d actifs collectés (USDT exclu, pas de paire)",
        len(snapshot), len(tradable)
    )
    return snapshot


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    data = fetch_binance_snapshot()
    for row in data:
        print(row)
