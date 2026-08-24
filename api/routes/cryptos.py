from fastapi import APIRouter, HTTPException

from src.utils.config import ASSETS
from src.utils.db import get_history_by_symbol, get_latest_by_symbol
from api.schemas.crypto import CryptoInfo, CryptoMetrics, CryptoSnapshot

router = APIRouter()

VALID_SYMBOLS = {a["symbol"] for a in ASSETS}


@router.get("/cryptos", response_model=list[CryptoInfo])
def list_cryptos():
    """Liste les 12 actifs disponibles dans le périmètre du MVP."""
    return [
        {"symbol": a["symbol"], "asset_id": a["coingecko_id"], "category": a["category"]}
        for a in ASSETS
    ]


@router.get("/crypto/{symbol}/latest", response_model=CryptoSnapshot)
def get_latest(symbol: str):
    symbol = symbol.upper()
    if symbol not in VALID_SYMBOLS:
        raise HTTPException(status_code=404, detail=f"Actif inconnu: {symbol}")

    row = get_latest_by_symbol(symbol)
    if row is None:
        raise HTTPException(status_code=404, detail=f"Aucune donnée pour {symbol} pour l'instant")
    return row


@router.get("/crypto/{symbol}/history", response_model=list[CryptoSnapshot])
def get_history(symbol: str, hours: int = 24):
    symbol = symbol.upper()
    if symbol not in VALID_SYMBOLS:
        raise HTTPException(status_code=404, detail=f"Actif inconnu: {symbol}")
    if hours <= 0 or hours > 720:
        raise HTTPException(status_code=400, detail="Le paramètre 'hours' doit être entre 1 et 720")

    return get_history_by_symbol(symbol, hours)



from src.utils.db import get_metrics_by_symbol


@router.get("/crypto/{symbol}/metrics", response_model=CryptoMetrics)
def get_metrics(symbol: str, days: int = 7):
    symbol = symbol.upper()
    if symbol not in VALID_SYMBOLS:
        raise HTTPException(status_code=404, detail=f"Actif inconnu: {symbol}")
    if days <= 0 or days > 90:
        raise HTTPException(status_code=400, detail="Le paramètre 'days' doit être entre 1 et 90")

    metrics = get_metrics_by_symbol(symbol, lookback_days=days)
    if metrics is None:
        raise HTTPException(status_code=404, detail=f"Pas assez de données pour calculer les indicateurs de {symbol}")
    return metrics

