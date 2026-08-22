"""
Vue générale — section 14 : les 12 actifs, marché global, volumes, évolution.
Rafraîchissement automatique toutes les 30 secondes.
"""
import pandas as pd
import streamlit as st

import plotly.graph_objects as go

from api_client import get_cryptos, get_latest, get_market_history, get_market_summary
from theme import COLORS


def _insert_gap_breaks(df, timestamp_col="timestamp", value_col="total_market_cap_usd", gap_threshold_minutes=5):
    """
    Insère un point 'trou' (valeur None) quand l'écart entre deux mesures
    dépasse le seuil — pour que le graphique montre une vraie coupure
    plutôt qu'une ligne droite trompeuse entre deux points éloignés dans le temps.
    """
    df = df.copy()
    df[timestamp_col] = pd.to_datetime(df[timestamp_col])
    gaps = df[timestamp_col].diff() > pd.Timedelta(minutes=gap_threshold_minutes)
    if not gaps.any():
        return df
    break_rows = df[gaps].copy()
    break_rows[timestamp_col] = break_rows[timestamp_col] - pd.Timedelta(seconds=1)
    break_rows[value_col] = None
    return pd.concat([df, break_rows]).sort_values(timestamp_col).reset_index(drop=True)

st.title("🌍 Vue générale du marché")
st.caption("Actualisation automatique toutes les 30 secondes")


@st.fragment(run_every="30s")
def render_market_view():
    # On vide le cache à chaque cycle pour garantir des données vraiment
    # fraîches à chaque rafraîchissement, plutôt que de dépendre du hasard
    # entre le TTL du cache (30s) et le rythme du fragment (30s aussi).
    get_market_summary.clear()
    get_cryptos.clear()
    get_latest.clear()

    try:
        summary = get_market_summary()
    except Exception as exc:
        st.error(f"Impossible de joindre l'API ({exc}). Vérifie qu'elle tourne sur le port 8000.")
        st.stop()

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Actifs suivis", summary["total_assets"])
    col2.metric("Capitalisation totale", f"${summary['total_market_cap_usd']:,.0f}")
    col3.metric("Variation moyenne 24h", f"{summary['average_change_24h']:.2f}%")
    col4.metric("Dernière mise à jour", summary["last_updated"][11:19] + " UTC")

    st.subheader("Évolution de la capitalisation totale")
    history = get_market_history(hours=6)
    if len(history) < 2:
        st.info("Historique encore trop court pour une courbe — le pipeline vient tout juste de démarrer.")
    else:
        hist_df = pd.DataFrame(history)
        hist_df = _insert_gap_breaks(hist_df)
        fig_evo = go.Figure(go.Scatter(
            x=hist_df["timestamp"],
            y=hist_df["total_market_cap_usd"],
            mode="lines",
            line=dict(color=COLORS["accent_gold"], width=2),
            
        ))
        fig_evo.update_layout(
            plot_bgcolor=COLORS["bg"],
            paper_bgcolor=COLORS["bg"],
            font=dict(family="IBM Plex Sans", color=COLORS["text_primary"]),
            xaxis=dict(gridcolor=COLORS["surface_alt"], title=None),
            yaxis=dict(gridcolor=COLORS["surface_alt"], title="Cap. totale (USD)"),
            margin=dict(l=10, r=10, t=20, b=10),
            height=320,
        )
        st.plotly_chart(fig_evo, use_container_width=True)

    st.divider()
    st.subheader("Les 12 actifs")

    cryptos = get_cryptos()
    rows = []
    for c in cryptos:
        try:
            latest = get_latest(c["symbol"])
            rows.append({
                "Symbole": c["symbol"],
                "Catégorie": c["category"],
                "Prix (USD)": latest["price_usd"],
                "Prix (XOF)": latest["price_xof"],
                "Variation 24h (%)": latest["change_24h"],
                "Volume 24h (USD)": latest["volume_24h"],
                "Market Cap (USD)": latest["market_cap"],
            })
        except Exception:
            continue

    df = pd.DataFrame(rows).sort_values("Market Cap (USD)", ascending=False)

    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Prix (USD)": st.column_config.NumberColumn(format="$%.4f"),
            "Prix (XOF)": st.column_config.NumberColumn(format="%.2f FCFA"),
            "Variation 24h (%)": st.column_config.NumberColumn(format="%.2f%%"),
            "Volume 24h (USD)": st.column_config.NumberColumn(format="$%,.0f"),
            "Market Cap (USD)": st.column_config.NumberColumn(format="$%,.0f"),
        },
    )

    st.subheader("Variation 24h par actif")
    chart_df = df.sort_values("Variation 24h (%)", ascending=True)
    colors = [COLORS["positive"] if v >= 0 else COLORS["negative"] for v in chart_df["Variation 24h (%)"]]


    fig = go.Figure(go.Bar(
        x=chart_df["Variation 24h (%)"],
        y=chart_df["Symbole"],
        orientation="h",
        marker_color=colors,
        text=chart_df["Variation 24h (%)"].map(lambda v: f"{v:+.2f}%"),
        textposition="outside",
    ))
    fig.update_layout(
        plot_bgcolor=COLORS["bg"],
        paper_bgcolor=COLORS["bg"],
        font=dict(family="IBM Plex Sans", color=COLORS["text_primary"]),
        xaxis=dict(gridcolor=COLORS["surface_alt"], zerolinecolor=COLORS["accent_gold"]),
        yaxis=dict(gridcolor="rgba(0,0,0,0)"),
        margin=dict(l=10, r=10, t=30, b=10),
        height=420,
    )
    st.plotly_chart(fig, use_container_width=True)

render_market_view()