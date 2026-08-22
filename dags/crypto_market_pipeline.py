"""
DAG principal du pipeline crypto — sections 7 et 8 du document projet.
Orchestre les 3 collecteurs (CoinGecko, Binance, FX) toutes les minutes.
"""
from __future__ import annotations

import logging

import pendulum

from airflow.sdk import dag, task

from src.collectors.coingecko_collector import fetch_coingecko_snapshot, CoinGeckoCollectorError
from src.collectors.binance_collector import fetch_binance_snapshot, BinanceCollectorError
from src.collectors.fx_collector import fetch_fx_snapshot, FxCollectorError

logger = logging.getLogger("dags.crypto_market_pipeline")


@dag(
    dag_id="crypto_market_pipeline",
    description="Collecte quasi temps réel des 12 crypto-actifs (CoinGecko + Binance + FX)",
    schedule="* * * * *",  # toutes les minutes — section 15
    start_date=pendulum.datetime(2026, 8, 22, tz="UTC"),
    catchup=False,
    max_active_runs=1,
    default_args={
        "retries": 1,
        "retry_delay": pendulum.duration(seconds=30),
        "execution_timeout": pendulum.duration(minutes=2),
    },
    tags=["crypto", "mvp", "collecte"],
)
def crypto_market_pipeline():

    @task()
    def collect_coingecko() -> list:
        try:
            return fetch_coingecko_snapshot()
        except CoinGeckoCollectorError as exc:
            logger.error("Tâche CoinGecko en échec: %s", exc)
            raise

    @task()
    def collect_binance() -> list:
        try:
            return fetch_binance_snapshot()
        except BinanceCollectorError as exc:
            logger.error("Tâche Binance en échec: %s", exc)
            raise

    @task()
    def collect_fx() -> dict:
        try:
            return fetch_fx_snapshot()
        except FxCollectorError as exc:
            logger.error("Tâche FX en échec: %s", exc)
            raise

    @task()
    def load_to_postgres(coingecko_data: list, binance_data: list, fx_data: dict) -> None:
        """
        Écrit les deux sources dans crypto_market_snapshot, avec conversion
        XOF appliquée au passage (section 9).
        """
        from src.utils.db import insert_snapshot_records

        fx_rate = fx_data["usd_xof_rate"]
        n_coingecko = insert_snapshot_records(coingecko_data, fx_rate=fx_rate)
        n_binance = insert_snapshot_records(binance_data, fx_rate=fx_rate)

        logger.info(
            "Chargement terminé : %d lignes CoinGecko + %d lignes Binance = %d total",
            n_coingecko, n_binance, n_coingecko + n_binance,
        )

    coingecko_result = collect_coingecko()
    binance_result = collect_binance()
    fx_result = collect_fx()

    load_to_postgres(coingecko_result, binance_result, fx_result)


crypto_market_pipeline()
