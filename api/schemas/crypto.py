"""
Schémas de réponse de l'API — définissent le contrat de données exposé.
"""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class CryptoInfo(BaseModel):
    symbol: str
    asset_id: str
    category: str


class CryptoSnapshot(BaseModel):
    asset_id: str
    symbol: str
    timestamp: datetime
    ingestion_time: datetime
    price_usd: float
    price_xof: Optional[float] = None
    volume_24h: Optional[float] = None
    market_cap: Optional[float] = None
    change_24h: Optional[float] = None
    source: str


class MarketSummary(BaseModel):
    total_assets: int
    total_market_cap_usd: float
    average_change_24h: float
    last_updated: datetime


class CryptoMetrics(BaseModel):
    symbol: str
    price_usd: float
    change_1h_pct: Optional[float] = None
    change_24h_pct: Optional[float] = None
    moving_average_7d: Optional[float] = None
    rolling_volatility: Optional[float] = None
    max_drawdown_pct: Optional[float] = None


class RankingEntry(BaseModel):
    rank: int
    symbol: str
    price_usd: float
    change_24h_pct: Optional[float] = None
    rolling_volatility: Optional[float] = None
    volume_24h: Optional[float] = None
