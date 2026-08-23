"""
Crypto Explorer — section 14 : historique détaillé d'un actif au choix.
"""
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from api_client import get_cryptos, get_history, get_metrics
from theme import COLORS
from utils import insert_gap_breaks

st.title("🔍 Crypto Explorer")

cryptos = get_cryptos()
symbols = [c["symbol"] for c in cryptos]
default_index = symbols.index("BTC") if "BTC" in symbols else 0

col_select, col_window, col_currency = st.columns([2, 2, 1])
with col_select:
    symbol = st.selectbox("Actif", symbols, index=default_index)
with col_window:
    window_label = st.selectbox("Fenêtre", ["1h", "6h", "24h", "7 jours", "30 jours"], index=2)
with col_currency:
    show_xof = st.toggle("Afficher en FCFA", value=False)

window_hours_map = {"1h": 1, "6h": 6, "24h": 24, "7 jours": 168, "30 jours": 720}
hours = window_hours_map[window_label]
days_for_metrics = min(max(hours // 24, 1), 90)

try:
    metrics = get_metrics(symbol, days=days_for_metrics)
except Exception:
    metrics = None

if metrics:
    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("Prix actuel", f"${metrics['price_usd']:,.4f}")
    col2.metric("Variation 1h", f"{metrics['change_1h_pct']:+.2f}%" if metrics['change_1h_pct'] is not None else "—")
    col3.metric("Variation 24h", f"{metrics['change_24h_pct']:+.2f}%" if metrics['change_24h_pct'] is not None else "—")
    col4.metric("Volatilité glissante", f"{metrics['rolling_volatility']*100:.3f}%" if metrics['rolling_volatility'] is not None else "—")
    col5.metric("Drawdown max", f"{metrics['max_drawdown_pct']:.2f}%" if metrics['max_drawdown_pct'] is not None else "—")
else:
    st.info(f"Indicateurs pas encore disponibles pour {symbol} (historique trop court).")

st.divider()

history = get_history(symbol, hours=hours)

if len(history) < 2:
    st.info(f"Historique encore trop court pour {symbol} sur cette fenêtre.")
else:
    hist_df = pd.DataFrame(history)
    hist_df = insert_gap_breaks(hist_df, value_cols=["price_usd", "price_xof"])

    value_col = "price_xof" if show_xof else "price_usd"
    currency_label = "Prix (FCFA)" if show_xof else "Prix (USD)"
    price_format = "%.2f FCFA" if show_xof else "$%.4f"

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=hist_df["timestamp"],
        y=hist_df[value_col],
        mode="lines",
        name=currency_label,
        line=dict(color=COLORS["accent_gold"], width=2),
    ))

    if not show_xof and metrics and metrics.get("moving_average_7d") is not None:
        fig.add_hline(
            y=metrics["moving_average_7d"],
            line_dash="dot",
            line_color=COLORS["accent_indigo"],
            annotation_text="Moyenne mobile",
            annotation_font_color=COLORS["accent_indigo"],
        )

    fig.update_layout(
        plot_bgcolor=COLORS["bg"],
        paper_bgcolor=COLORS["bg"],
        font=dict(family="IBM Plex Sans", color=COLORS["text_primary"]),
        xaxis=dict(gridcolor=COLORS["surface_alt"], title=None),
        yaxis=dict(gridcolor=COLORS["surface_alt"], title=currency_label),
        margin=dict(l=10, r=10, t=20, b=10),
        height=450,
    )
    st.plotly_chart(fig, use_container_width=True)
