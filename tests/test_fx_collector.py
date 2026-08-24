"""
Tests unitaires du collecteur de taux de change.
"""
from unittest.mock import MagicMock, patch

import pytest

from src.collectors.fx_collector import FxCollectorError, fetch_fx_snapshot


def _make_response(payload):
    response = MagicMock()
    response.json.return_value = payload
    response.raise_for_status.return_value = None
    return response


@patch("src.collectors.fx_collector.requests.get")
def test_valid_rate_computes_xof_conversion(mock_get):
    mock_get.return_value = _make_response({"date": "2026-08-24", "rates": {"EUR": 0.86}})

    result = fetch_fx_snapshot()

    assert result["usd_eur_rate"] == 0.86
    assert result["usd_xof_rate"] == round(0.86 * 655.957, 4)


@patch("src.collectors.fx_collector.requests.get")
def test_implausible_rate_is_rejected(mock_get):
    mock_get.return_value = _make_response({"date": "2026-08-24", "rates": {"EUR": 5.0}})

    with pytest.raises(FxCollectorError):
        fetch_fx_snapshot()


@patch("src.collectors.fx_collector.requests.get")
def test_missing_rate_is_rejected(mock_get):
    mock_get.return_value = _make_response({"date": "2026-08-24", "rates": {}})

    with pytest.raises(FxCollectorError):
        fetch_fx_snapshot()
