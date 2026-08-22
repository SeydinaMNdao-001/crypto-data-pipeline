"""
Point d'entrée FastAPI — section 13 du document projet.
"""
from fastapi import FastAPI

from api.routes import cryptos, health, market

app = FastAPI(
    title="Crypto Market Pipeline API",
    description="API de consultation des données crypto collectées par le pipeline MVP",
    version="0.1.0",
)

app.include_router(health.router, tags=["health"])
app.include_router(cryptos.router, tags=["cryptos"])
app.include_router(market.router, tags=["market"])
