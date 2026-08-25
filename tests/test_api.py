"""
Tests des endpoints FastAPI (section 16). Les tests de validation
(avant tout accès base) sont de purs tests unitaires ; ceux qui lisent
de vraies données sont marqués 'integration'.
"""
import pytest
from fastapi.testclient import TestClient

from api.main import app

client = TestClient(app)


def test_cryptos_endpoint_returns_12_assets():
    response = client.get("/cryptos")
    assert response.status_code == 200
    assert len(response.json()) == 12


def test_unknown_symbol_returns_404_before_touching_db():
    response = client.get("/crypto/NOTREAL/latest")
    assert response.status_code == 404


def test_invalid_hours_param_returns_400():
    response = client.get("/crypto/BTC/history?hours=0")
    assert response.status_code == 400


@pytest.mark.integration
def test_health_endpoint_reports_ok_when_db_is_up():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


@pytest.mark.integration
def test_latest_endpoint_returns_expected_shape():
    response = client.get("/crypto/BTC/latest")
    assert response.status_code == 200
    body = response.json()
    assert body["symbol"] == "BTC"
    assert "price_usd" in body
