"""
Fonctions utilitaires partagées entre les pages du dashboard.
"""
import pandas as pd


def insert_gap_breaks(df, timestamp_col="timestamp", value_cols=None, gap_threshold_minutes=5):
    """
    Insère un point 'trou' (valeurs None) quand l'écart entre deux mesures
    dépasse le seuil — pour que le graphique montre une vraie coupure
    plutôt qu'une ligne droite trompeuse entre deux points éloignés dans le temps.
    """
    if value_cols is None:
        value_cols = [c for c in df.columns if c != timestamp_col]

    df = df.copy()
    df[timestamp_col] = pd.to_datetime(df[timestamp_col])
    gaps = df[timestamp_col].diff() > pd.Timedelta(minutes=gap_threshold_minutes)
    if not gaps.any():
        return df

    break_rows = df[gaps].copy()
    break_rows[timestamp_col] = break_rows[timestamp_col] - pd.Timedelta(seconds=1)
    for col in value_cols:
        break_rows[col] = None

    return pd.concat([df, break_rows]).sort_values(timestamp_col).reset_index(drop=True)
