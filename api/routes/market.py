from typing import Literal

from fastapi import APIRouter, HTTPException

from src.utils.db import get_market_summary
from api.schemas.crypto import MarketSummary

router = APIRouter()


@router.get("/market/summary", response_model=MarketSummary)
def market_summary():
    """Synthèse du marché sur les 12 actifs, au dernier cycle de collecte."""
    return get_market_summary()



from src.utils.db import get_market_ranking
from api.schemas.crypto import RankingEntry


@router.get("/market/ranking", response_model=list[RankingEntry])
def market_ranking(
    metric: Literal["change_24h", "volatility", "volume"] = "change_24h",
    days: int = 1,
):
    """Classe les 12 actifs par rendement, volatilité ou volume (section 10)."""
    if days <= 0 or days > 90:
        raise HTTPException(status_code=400, detail="Le paramètre 'days' doit être entre 1 et 90")
    return get_market_ranking(metric=metric, lookback_days=days)



from src.utils.db import get_market_cap_history
from api.schemas.crypto import MarketHistoryPoint


@router.get("/market/history", response_model=list[MarketHistoryPoint])
def market_history(hours: int = 24):
    if hours <= 0 or hours > 720:
        raise HTTPException(status_code=400, detail="Le paramètre 'hours' doit être entre 1 et 720")
    return get_market_cap_history(hours=hours)




from src.utils.db import get_fx_rate_history
from api.schemas.crypto import FxRatePoint


@router.get("/market/fx-history", response_model=list[FxRatePoint])
def fx_history(hours: int = 168):
    if hours <= 0 or hours > 2160:
        raise HTTPException(status_code=400, detail="Le paramètre 'hours' doit être entre 1 et 2160")
    return get_fx_rate_history(hours=hours)