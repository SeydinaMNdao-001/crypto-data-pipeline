"""
Collecteur de taux de change USD/EUR/XOF — sections 6 et 11.1 du document projet.
Le FCFA (XOF) est arrimé à l'euro à parité fixe (1 EUR = 655.957 XOF) : seule la
conversion USD/EUR est un taux de marché réel. Elle vient de Frankfurter (taux
officiels de la Banque Centrale Européenne, gratuit, sans clé).
"""
import logging
from datetime import datetime, timezone

import requests
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from src.utils.config import XOF_EUR_FIXED_RATE

logger = logging.getLogger("collectors.fx")

FRANKFURTER_URL = "https://api.frankfurter.dev/v1/latest"

# Plage de plausibilité pour USD/EUR (section 8 : contrôle des valeurs aberrantes).
# Historiquement, ce taux évolue entre 0.6 et 1.3 sur les 20 dernières années.
MIN_PLAUSIBLE_RATE = 0.6
MAX_PLAUSIBLE_RATE = 1.3


class FxCollectorError(Exception):
    """Levée quand la collecte du taux de change échoue après tous les retries."""


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    retry=retry_if_exception_type(requests.exceptions.RequestException),
    reraise=True,
)
def _call_frankfurter() -> dict:
    """Appel brut à Frankfurter avec retry + backoff exponentiel."""
    response = requests.get(
        FRANKFURTER_URL,
        params={"base": "USD", "symbols": "EUR"},
        timeout=10,
    )
    response.raise_for_status()
    return response.json()


def fetch_fx_snapshot() -> dict:
    """
    Récupère le taux USD/EUR du jour et calcule USD/XOF via la parité fixe EUR/XOF.
    """
    try:
        raw_data = _call_frankfurter()
    except requests.exceptions.RequestException as exc:
        logger.error("Échec de la collecte du taux de change après retries: %s", exc)
        raise FxCollectorError(str(exc)) from exc

    usd_eur_rate = raw_data.get("rates", {}).get("EUR")

    if usd_eur_rate is None:
        logger.error("Taux EUR absent de la réponse Frankfurter: %s", raw_data)
        raise FxCollectorError("Taux USD/EUR manquant dans la réponse")

    if not (MIN_PLAUSIBLE_RATE <= usd_eur_rate <= MAX_PLAUSIBLE_RATE):
        logger.error("Taux USD/EUR implausible: %s", usd_eur_rate)
        raise FxCollectorError(f"Taux USD/EUR hors plage plausible: {usd_eur_rate}")

    usd_xof_rate = usd_eur_rate * XOF_EUR_FIXED_RATE
    ingestion_time = datetime.now(timezone.utc)

    snapshot = {
        "rate_date": raw_data.get("date"),
        "ingestion_time": ingestion_time.isoformat(),
        "usd_eur_rate": usd_eur_rate,
        "eur_xof_fixed_rate": XOF_EUR_FIXED_RATE,
        "usd_xof_rate": round(usd_xof_rate, 4),
        "source": "frankfurter+fixed_peg",
    }

    logger.info(
        "Taux du jour (%s) : 1 USD = %.4f EUR = %.2f XOF",
        snapshot["rate_date"], usd_eur_rate, snapshot["usd_xof_rate"]
    )
    return snapshot


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    fx = fetch_fx_snapshot()
    print(fx)
