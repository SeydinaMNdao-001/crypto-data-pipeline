"""
Export Parquet partitionné — section 8/9 du document projet (stockage analytique).
Chaque appel ajoute un nouveau fichier dans la partition du jour correspondant
(année/mois/jour, basé sur ingestion_time en UTC), sans jamais réécrire
les fichiers déjà présents — c'est un append-only, pas une mise à jour.
"""
import logging
from datetime import datetime
import uuid

import pandas as pd
import pyarrow as pa
import pyarrow.dataset as ds

from src.utils.config import PARQUET_BASE_PATH

logger = logging.getLogger("utils.parquet_writer")


def write_snapshot_to_parquet(records: list, fx_rate: float = None, base_path: str = None) -> int:
    """
    Écrit une liste de dicts (sortie des collecteurs) dans l'archive Parquet
    partitionnée par date. Retourne le nombre de lignes écrites.
    """
    if not records:
        return 0

    base_path = base_path or PARQUET_BASE_PATH
    rows = []
    for r in records:
        price_xof = round(r["price_usd"] * fx_rate, 4) if fx_rate else None
        ingestion_dt = datetime.fromisoformat(r["ingestion_time"])
        rows.append({
            "asset_id": r["asset_id"],
            "symbol": r["symbol"],
            "timestamp": r["timestamp"],
            "ingestion_time": r["ingestion_time"],
            "price_usd": r["price_usd"],
            "price_xof": price_xof,
            "volume_24h": r["volume_24h"],
            "market_cap": r["market_cap"],
            "change_24h": r["change_24h"],
            "source": r["source"],
            "year": ingestion_dt.year,
            "month": ingestion_dt.month,
            "day": ingestion_dt.day,
        })

    df = pd.DataFrame(rows)
    table = pa.Table.from_pandas(df, preserve_index=False)

    ds.write_dataset(
        table,
        base_dir=base_path,
        format="parquet",
        partitioning=["year", "month", "day"],
        partitioning_flavor="hive",
        existing_data_behavior="overwrite_or_ignore",
        basename_template=f"part-{uuid.uuid4().hex}-{{i}}.parquet",
    )

    logger.info("Écrit %d lignes dans l'archive Parquet (%s)", len(rows), base_path)
    return len(rows)
