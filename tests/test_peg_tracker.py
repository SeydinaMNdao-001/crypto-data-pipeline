"""
Tests unitaires du calcul d'écart de peg (section 16 : tests des transformations).
"""
from src.transformations.peg_tracker import PEG_ALERT_THRESHOLD_PCT, compute_peg_records


def _row(symbol, price_usd):
    return {
        "asset_id": symbol.lower(), "symbol": symbol,
        "timestamp": "2026-08-24T10:00:00+00:00",
        "price_usd": price_usd, "source": "coingecko",
    }


def test_non_stablecoins_are_ignored():
    data = [_row("BTC", 77000.0), _row("USDT", 1.001)]

    result = compute_peg_records(data)

    assert len(result) == 1
    assert result[0]["asset_id"] == "usdt"


def test_deviation_within_threshold_is_not_flagged():
    result = compute_peg_records([_row("USDC", 1.002)])
    assert result[0]["seuil_alerte_franchi"] is False


def test_deviation_beyond_threshold_is_flagged():
    result = compute_peg_records([_row("DAI", 1.008)])  # 0.8% > seuil 0.5%
    assert result[0]["seuil_alerte_franchi"] is True
    assert result[0]["peg_deviation"] > PEG_ALERT_THRESHOLD_PCT
