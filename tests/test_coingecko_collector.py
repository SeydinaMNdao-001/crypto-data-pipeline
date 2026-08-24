"""
Tests unitaires du collecteur CoinGecko (section 16). Aucun appel réseau
réel — les réponses HTTP sont simulées avec unittest.mock.
"""
from unittest.mock import MagicMock, patch

import pytest
import requests

from src.collectors.coingecko_collector import (
    CoinGeckoCollectorError,
    fetch_coingecko_snapshot,
)
from src.utils.config import ASSETS


def _make_response(payload, status_ok=True):
    response = MagicMock()
    response.json.return_value = payload
    if status_ok:
        response.raise_for_status.return_value = None
    else:
        response.raise_for_status.side_effect = requests.exceptions.HTTPError("500")
    return response


def _valid_record(coingecko_id, symbol):
    return {
        "id": coingecko_id,
        "symbol": symbol.lower(),
        "current_price": 100.0,
        "market_cap": 1_000_000.0,
        "total_volume": 500_000.0,
        "price_change_percentage_24h": 1.5,
        "price_change_percentage_1h_in_currency": 0.1,
        "last_updated": "2026-08-24T10:00:00.000Z",
    }


@patch("src.collectors.coingecko_collector.requests.get")
def test_fetch_returns_normalized_records_for_all_assets(mock_get):
    payload = [_valid_record(a["coingecko_id"], a["symbol"]) for a in ASSETS]
    mock_get.return_value = _make_response(payload)

    result = fetch_coingecko_snapshot()

    assert len(result) == len(ASSETS)
    assert result[0]["source"] == "coingecko"
    assert result[0]["price_usd"] == 100.0


@patch("src.collectors.coingecko_collector.requests.get")
def test_record_missing_required_field_is_rejected(mock_get):
    payload = [{
        "id": "bitcoin", "symbol": "btc", "current_price": None,
        "market_cap": 1_000_000.0, "total_volume": 500_000.0,
    }]
    mock_get.return_value = _make_response(payload)

    result = fetch_coingecko_snapshot()

    assert result == []  # prix manquant -> enregistrement rejeté


@patch("src.collectors.coingecko_collector.requests.get")
def test_persistent_http_failure_raises_after_retries(mock_get):
    mock_get.side_effect = requests.exceptions.ConnectionError("network down")

    with pytest.raises(CoinGeckoCollectorError):
        fetch_coingecko_snapshot()

    assert mock_get.call_count == 3  # stop_after_attempt(3)
