"""
Client HTTP vers l'API FastAPI — le dashboard ne touche jamais la base
de données directement, il passe par l'API comme n'importe quel autre
consommateur externe (section 13).
"""
import os

import requests
import streamlit as st

API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")


@st.cache_data(ttl=30)
def get_cryptos():
    r = requests.get(f"{API_BASE_URL}/cryptos", timeout=5)
    r.raise_for_status()
    return r.json()


@st.cache_data(ttl=30)
def get_latest(symbol: str):
    r = requests.get(f"{API_BASE_URL}/crypto/{symbol}/latest", timeout=5)
    r.raise_for_status()
    return r.json()


@st.cache_data(ttl=30)
def get_history(symbol: str, hours: int = 24):
    r = requests.get(f"{API_BASE_URL}/crypto/{symbol}/history", params={"hours": hours}, timeout=5)
    r.raise_for_status()
    return r.json()


@st.cache_data(ttl=30)
def get_metrics(symbol: str, days: int = 7):
    r = requests.get(f"{API_BASE_URL}/crypto/{symbol}/metrics", params={"days": days}, timeout=5)
    r.raise_for_status()
    return r.json()


@st.cache_data(ttl=30)
def get_market_summary():
    r = requests.get(f"{API_BASE_URL}/market/summary", timeout=5)
    r.raise_for_status()
    return r.json()


@st.cache_data(ttl=30)
def get_ranking(metric: str = "change_24h", days: int = 1):
    r = requests.get(f"{API_BASE_URL}/market/ranking", params={"metric": metric, "days": days}, timeout=5)
    r.raise_for_status()
    return r.json()


@st.cache_data(ttl=30)
def get_market_history(hours: int = 24):
    r = requests.get(f"{API_BASE_URL}/market/history", params={"hours": hours}, timeout=5)
    r.raise_for_status()
    return r.json()