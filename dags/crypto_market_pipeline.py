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
    def summarize(coingecko_data: list, binance_data: list, fx_data: dict) -> None:
        """
        Étape temporaire : le stockage réel (PostgreSQL/Parquet) arrive en
        phase 4 (section 9). Pour l'instant, on journalise un résumé du cycle.
        """
        total = len(coingecko_data) + len(binance_data)
        logger.info(
            "Cycle terminé : %d lignes CoinGecko, %d lignes Binance, taux USD/XOF=%.2f. Total: %d",
            len(coingecko_data), len(binance_data), fx_data["usd_xof_rate"], total,
        )

    coingecko_result = collect_coingecko()
    binance_result = collect_binance()
    fx_result = collect_fx()

    summarize(coingecko_result, binance_result, fx_result)


crypto_market_pipeline()
