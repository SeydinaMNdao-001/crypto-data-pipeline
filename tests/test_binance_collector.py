"""
Tests unitaires du collecteur Binance — y compris un test de non-régression
sur le bug historique du formatage JSON du paramètre 'symbols' (l'incident
des espaces qui causaient une 400 chez Binance, rencontré en phase Collecte).
"""
from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock, patch

from src.collectors.binance_collector import fetch_binance_snapshot


def _make_response(payload):
    response = MagicMock()
    response.json.return_value = payload
    response.raise_for_status.return_value = None
    return response


def _fresh_ticker(symbol, price="100.0"):
    now_ms = int(datetime.now(timezone.utc).timestamp() * 1000)
    return {
        "symbol": symbol, "lastPrice": price, "quoteVolume": "1000000",
        "priceChangePercent": "2.5", "closeTime": now_ms,
    }


@patch("src.collectors.binance_collector.requests.get")
def test_fresh_tickers_are_accepted(mock_get):
    mock_get.return_value = _make_response([_fresh_ticker("BTCUSDT")])

    result = fetch_binance_snapshot()

    assert len(result) == 1
    assert result[0]["symbol"] == "BTC"


@patch("src.collectors.binance_collector.requests.get")
def test_zero_price_ticker_is_rejected(mock_get):
    ticker = _fresh_ticker("DAIUSDT", price="0.0")
    mock_get.return_value = _make_response([ticker])

    result = fetch_binance_snapshot()

    assert result == []


@patch("src.collectors.binance_collector.requests.get")
def test_stale_ticker_is_rejected(mock_get):
    stale_ms = int((datetime.now(timezone.utc) - timedelta(minutes=30)).timestamp() * 1000)
    ticker = {
        "symbol": "DAIUSDT", "lastPrice": "1.0", "quoteVolume": "1000",
        "priceChangePercent": "0.0", "closeTime": stale_ms,
    }
    mock_get.return_value = _make_response([ticker])

    result = fetch_binance_snapshot()

    assert result == []


@patch("src.collectors.binance_collector.requests.get")
def test_symbols_param_has_no_spaces(mock_get):
    """Garantit qu'on ne réintroduit jamais le bug de formatage JSON."""
    mock_get.return_value = _make_response([])

    fetch_binance_snapshot()

    sent_params = mock_get.call_args.kwargs["params"]
    assert ", " not in sent_params["symbols"]
