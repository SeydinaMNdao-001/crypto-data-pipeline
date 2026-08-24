"""
Routes stablecoins — section 13 : /stablecoins/peg-history.
"""
from fastapi import APIRouter, HTTPException

from src.utils.config import ASSETS
from src.utils.db import get_peg_history
from api.schemas.crypto import PegHistoryPoint

router = APIRouter()

ASSET_ID_TO_SYMBOL = {a["coingecko_id"]: a["symbol"] for a in ASSETS}


@router.get("/stablecoins/peg-history", response_model=list[PegHistoryPoint])
def peg_history(hours: int = 24):
    if hours <= 0 or hours > 720:
        raise HTTPException(status_code=400, detail="Le paramètre 'hours' doit être entre 1 et 720")

    rows = get_peg_history(hours=hours)
    return [
        {
            "symbol": ASSET_ID_TO_SYMBOL.get(r["asset_id"], r["asset_id"]),
            "timestamp": r["timestamp"],
            "price_usd": float(r["price_usd"]),
            "peg_deviation": float(r["peg_deviation"]),
            "seuil_alerte_franchi": r["seuil_alerte_franchi"],
        }
        for r in rows
    ]
