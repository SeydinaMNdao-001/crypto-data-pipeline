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


def build_peg_gauge_figure(deviation_pct, threshold_pct, colors):
    """
    Jauge horizontale : une zone 'sûre' teintée autour de zéro, un marqueur
    losange positionné à l'écart actuel, coloré selon qu'il dépasse ou non
    le seuil d'alerte. Élément visuel spécifique au suivi de peg (section 11.2).
    """
    import plotly.graph_objects as go

    range_max = max(threshold_pct * 2.5, abs(deviation_pct) * 1.3, 0.1)
    marker_color = colors["positive"] if abs(deviation_pct) <= threshold_pct else colors["negative"]

    fig = go.Figure()
    fig.add_shape(type="rect", x0=-threshold_pct, x1=threshold_pct, y0=-0.5, y1=0.5,
                  fillcolor="rgba(79, 155, 114, 0.12)", line=dict(width=0))
    fig.add_shape(type="line", x0=-range_max, x1=range_max, y0=0, y1=0,
                  line=dict(color=colors["surface_alt"], width=2))
    fig.add_shape(type="line", x0=0, x1=0, y0=-0.6, y1=0.6,
                  line=dict(color=colors["accent_gold"], width=1, dash="dot"))
    fig.add_trace(go.Scatter(
        x=[deviation_pct], y=[0], mode="markers",
        marker=dict(size=18, color=marker_color, symbol="diamond",
                    line=dict(color=colors["text_primary"], width=1)),
        showlegend=False,
        hovertemplate=f"Écart : {deviation_pct:+.4f}%<extra></extra>",
    ))
    fig.update_layout(
        xaxis=dict(range=[-range_max, range_max], showgrid=False, zeroline=False,
                   tickfont=dict(size=10, color=colors["text_muted"])),
        yaxis=dict(visible=False, range=[-1, 1]),
        plot_bgcolor=colors["bg"], paper_bgcolor=colors["bg"],
        height=110, margin=dict(l=20, r=20, t=10, b=25),
    )
    return fig
