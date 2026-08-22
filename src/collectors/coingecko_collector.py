"""
Collecteur CoinGecko — sections 6 et 8 du document projet.
Récupère en un seul appel les données de marché des 12 actifs du périmètre,
avec retry/backoff, timeout, et validation des champs obligatoires.
"""
import logging
from datetime import datetime, timezone

import requests
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from src.utils.config import ASSETS, COINGECKO_API_KEY, COINGECKO_BASE_URL

logger = logging.getLogger("collectors.coingecko")

REQUIRED_FIELDS = ["id", "symbol", "current_price", "market_cap", "total_volume"]


class CoinGeckoCollectorError(Exception):
    """Levée quand la collecte CoinGecko échoue après tous les retries."""


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    retry=retry_if_exception_type(requests.exceptions.RequestException),
    reraise=True,
)
def _call_coingecko_markets(ids: str) -> list:
    """Appel brut à l'endpoint /coins/markets avec retry + backoff exponentiel."""
    response = requests.get(
        f"{COINGECKO_BASE_URL}/coins/markets",
        params={
            "vs_currency": "usd",
            "ids": ids,
            "price_change_percentage": "1h,24h",
            "x_cg_demo_api_key": COINGECKO_API_KEY,
        },
        timeout=10,
    )
    response.raise_for_status()
    return response.json()


def _validate_record(record: dict) -> bool:
    """Contrôle des champs obligatoires (section 8 : validation)."""
    missing = [f for f in REQUIRED_FIELDS if record.get(f) is None]
    if missing:
        logger.warning("Champs manquants pour %s: %s", record.get("id"), missing)
        return False
    return True


def fetch_coingecko_snapshot() -> list:
    """
    Récupère un instantané de marché pour les 12 actifs du périmètre.
    Retourne une liste de dicts normalisés selon le schéma crypto_market_snapshot (section 9).
    """
    ids_param = ",".join(a["coingecko_id"] for a in ASSETS)

    try:
        raw_data = _call_coingecko_markets(ids_param)
    except requests.exceptions.RequestException as exc:
        logger.error("Échec de la collecte CoinGecko après retries: %s", exc)
        raise CoinGeckoCollectorError(str(exc)) from exc

    ingestion_time = datetime.now(timezone.utc)
    symbol_by_id = {a["coingecko_id"]: a["symbol"] for a in ASSETS}
    snapshot = []

    for record in raw_data:
        if not _validate_record(record):
            continue

        snapshot.append({
            "asset_id": record["id"],
            "symbol": symbol_by_id.get(record["id"], record["symbol"].upper()),
            "timestamp": record.get("last_updated"),
            "ingestion_time": ingestion_time.isoformat(),
            "price_usd": record["current_price"],
            "volume_24h": record["total_volume"],
            "market_cap": record["market_cap"],
            "change_1h": record.get("price_change_percentage_1h_in_currency"),
            "change_24h": record.get("price_change_percentage_24h"),
            "source": "coingecko",
        })

    collected_ids = {r["asset_id"] for r in snapshot}
    expected_ids = {a["coingecko_id"] for a in ASSETS}
    missing_assets = expected_ids - collected_ids
    if missing_assets:
        logger.warning("Actifs absents de la réponse CoinGecko: %s", missing_assets)

    logger.info("Snapshot CoinGecko: %d/%d actifs collectés", len(snapshot), len(ASSETS))
    return snapshot


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    data = fetch_coingecko_snapshot()
    for row in data:
        print(row)
