"""
Comparaison — section 14 : plusieurs actifs indexés à 100, pour comparer
des tendances plutôt que des prix bruts (échelles très différentes sinon).
"""
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from api_client import get_cryptos, get_history, get_metrics
from theme import CHART_PALETTE, COLORS
from utils import insert_gap_breaks

st.title("⚖️ Comparaison")

cryptos = get_cryptos()
symbols = [c["symbol"] for c in cryptos]
default_selection = [s for s in ["BTC", "ETH", "SOL"] if s in symbols] or symbols[:3]

col_select, col_window = st.columns([3, 1])
with col_select:
    selected = st.multiselect("Actifs à comparer", symbols, default=default_selection, max_selections=6)
with col_window:
    window_label = st.selectbox("Fenêtre", ["1h", "6h", "24h", "7 jours"], index=2)

window_hours_map = {"1h": 1, "6h": 6, "24h": 24, "7 jours": 168}
hours = window_hours_map[window_label]

if len(selected) < 2:
    st.info("Sélectionne au moins 2 actifs pour comparer leurs tendances.")
    st.stop()

fig = go.Figure()
metrics_rows = []

for i, symbol in enumerate(selected):
    history = get_history(symbol, hours=hours)
    if len(history) < 2:
        st.warning(f"Historique trop court pour {symbol} sur cette fenêtre — actif ignoré.")
        continue

    hist_df = pd.DataFrame(history)
    hist_df["timestamp"] = pd.to_datetime(hist_df["timestamp"])
    hist_df = hist_df.sort_values("timestamp")

    base_price = hist_df["price_usd"].iloc[0]
    hist_df["indexed"] = hist_df["price_usd"] / base_price * 100
    hist_df = insert_gap_breaks(hist_df, value_cols=["indexed"])

    color = CHART_PALETTE[i % len(CHART_PALETTE)]
    fig.add_trace(go.Scatter(
        x=hist_df["timestamp"], y=hist_df["indexed"],
        mode="lines", name=symbol, line=dict(color=color, width=2),
    ))

    try:
        m = get_metrics(symbol, days=max(hours // 24, 1))
        metrics_rows.append({
            "Actif": symbol,
            "Prix (USD)": m["price_usd"],
            "Variation 24h (%)": m["change_24h_pct"],
            "Volatilité glissante (%)": round(m["rolling_volatility"] * 100, 4) if m["rolling_volatility"] is not None else None,
        })
    except Exception:
        continue

fig.add_hline(y=100, line_dash="dot", line_color=COLORS["text_muted"])
fig.update_layout(
    plot_bgcolor=COLORS["bg"],
    paper_bgcolor=COLORS["bg"],
    font=dict(family="IBM Plex Sans", color=COLORS["text_primary"]),
    xaxis=dict(gridcolor=COLORS["surface_alt"], title=None),
    yaxis=dict(gridcolor=COLORS["surface_alt"], title="Performance indexée (base 100)"),
    margin=dict(l=10, r=10, t=20, b=10),
    height=450,
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
)
st.plotly_chart(fig, use_container_width=True)

st.caption(
    "Base 100 au début de la fenêtre sélectionnée — permet de comparer des "
    "tendances entre actifs de prix très différents (ex: BTC à 77 000$ vs "
    "DOGE à 0,09$) sans que l'échelle n'écrase les plus petits."
)

if metrics_rows:
    st.subheader("Indicateurs sur la période")
    st.dataframe(
        pd.DataFrame(metrics_rows),
        use_container_width=True,
        hide_index=True,
        column_config={
            "Prix (USD)": st.column_config.NumberColumn(format="$%.4f"),
            "Variation 24h (%)": st.column_config.NumberColumn(format="%.2f%%"),
            "Volatilité glissante (%)": st.column_config.NumberColumn(format="%.4f%%"),
        },
    )
