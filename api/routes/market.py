from fastapi import APIRouter

from src.utils.db import get_market_summary
from api.schemas.crypto import MarketSummary

router = APIRouter()


@router.get("/market/summary", response_model=MarketSummary)
def market_summary():
    """Synthèse du marché sur les 12 actifs, au dernier cycle de collecte."""
    return get_market_summary()
