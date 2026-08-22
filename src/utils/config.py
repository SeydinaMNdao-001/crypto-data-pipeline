"""
Configuration centrale du projet : liste des actifs et variables d'environnement.
Section 5.1 du document projet : les 12 actifs retenus pour le MVP.
"""
import os
from dotenv import load_dotenv

load_dotenv()

ASSETS = [
    {"symbol": "BTC",  "coingecko_id": "bitcoin",     "binance_pair": "BTCUSDT",  "category": "reference"},
    {"symbol": "ETH",  "coingecko_id": "ethereum",    "binance_pair": "ETHUSDT",  "category": "reference"},
    {"symbol": "USDT", "coingecko_id": "tether",      "binance_pair": None,       "category": "stablecoin"},
    {"symbol": "USDC", "coingecko_id": "usd-coin",    "binance_pair": "USDCUSDT", "category": "stablecoin"},
    {"symbol": "DAI",  "coingecko_id": "dai",         "binance_pair": "DAIUSDT",  "category": "stablecoin"},
    {"symbol": "TRX",  "coingecko_id": "tron",        "binance_pair": "TRXUSDT",  "category": "circulation"},
    {"symbol": "BNB",  "coingecko_id": "binancecoin", "binance_pair": "BNBUSDT",  "category": "large_cap"},
    {"symbol": "SOL",  "coingecko_id": "solana",      "binance_pair": "SOLUSDT",  "category": "large_cap"},
    {"symbol": "XRP",  "coingecko_id": "ripple",      "binance_pair": "XRPUSDT",  "category": "large_cap"},
    {"symbol": "ADA",  "coingecko_id": "cardano",     "binance_pair": "ADAUSDT",  "category": "large_cap"},
    {"symbol": "DOGE", "coingecko_id": "dogecoin",    "binance_pair": "DOGEUSDT", "category": "speculative"},
    {"symbol": "LTC",  "coingecko_id": "litecoin",    "binance_pair": "LTCUSDT",  "category": "legacy"},
]

STABLECOIN_SYMBOLS = ["USDT", "USDC", "DAI"]

COINGECKO_API_KEY = os.getenv("COINGECKO_API_KEY")
COINGECKO_BASE_URL = "https://api.coingecko.com/api/v3"

BINANCE_BASE_URL = "https://data-api.binance.vision"

POSTGRES_CONFIG = {
    "user": os.getenv("POSTGRES_USER"),
    "password": os.getenv("POSTGRES_PASSWORD"),
    "dbname": os.getenv("POSTGRES_DB"),
    "host": os.getenv("POSTGRES_HOST"),
    "port": os.getenv("POSTGRES_PORT"),
}

XOF_EUR_FIXED_RATE = float(os.getenv("XOF_EUR_FIXED_RATE", "655.957"))
PARQUET_BASE_PATH = os.getenv("PARQUET_BASE_PATH", "data/crypto_market_snapshot")