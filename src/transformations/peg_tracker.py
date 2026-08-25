"""
Suivi du peg des stablecoins — section 11.2 du document projet.
Calcule l'écart par rapport à 1 USD pour USDT, USDC, DAI à chaque cycle,
et journalise les épisodes où l'écart dépasse le seuil d'alerte.
"""
import logging

from src.utils.config import STABLECOIN_SYMBOLS

logger = logging.getLogger("transformations.peg_tracker")

PEG_ALERT_THRESHOLD_PCT = 0.5  # section 11.2 : "par exemple 0,5 % sur une fenêtre donnée"


def compute_peg_records(coingecko_data: list) -> list:
    """
    Filtre les 3 stablecoins du périmètre et calcule leur écart de peg.
    Retourne une liste de dicts prête à insérer dans stablecoin_peg_history.
    """
    records = []
    for row in coingecko_data:
        if row["symbol"] not in STABLECOIN_SYMBOLS:
            continue

        price = row["price_usd"]
        deviation_pct = round((price - 1.0) / 1.0 * 100, 6)
        alert = abs(deviation_pct) > PEG_ALERT_THRESHOLD_PCT

        if alert:
            logger.warning(
                "Peg franchi pour %s : écart de %.4f%% (prix=%.6f)",
                row["symbol"], deviation_pct, price
            )

        records.append({
            "asset_id": row["asset_id"],
            "timestamp": row["timestamp"],
            "price_usd": price,
            "peg_deviation": deviation_pct,
            "seuil_alerte_franchi": alert,
        })

    return records
