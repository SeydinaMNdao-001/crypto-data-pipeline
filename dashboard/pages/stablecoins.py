"""
Stablecoins — section 11.2 : écart de peg, historique, épisodes d'alerte.
"""
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from api_client import get_peg_history
from theme import COLORS
from utils import build_peg_gauge_figure, insert_gap_breaks

PEG_ALERT_THRESHOLD_PCT = 0.5  # cohérent avec src/transformations/peg_tracker.py

st.title("🪙 Stablecoins — suivi du peg")
st.caption("USDT, USDC, DAI — écart par rapport à 1,00 USD")

selected_stablecoins = st.multiselect(
    "Stablecoins à afficher",
    ["USDT", "USDC", "DAI"],
    default=["USDT", "USDC", "DAI"],
)

if not selected_stablecoins:
    st.warning("Sélectionne au moins un stablecoin pour continuer.")
    st.stop()


history = get_peg_history(hours=24)

if len(history) < 3:
    st.info("Historique de peg encore trop court — le suivi vient de démarrer.")
    st.stop()

df = pd.DataFrame(history)
df["timestamp"] = pd.to_datetime(df["timestamp"])

st.subheader("Écart actuel")
cols = st.columns(len(selected_stablecoins))
for i, symbol in enumerate(selected_stablecoins):
    latest = df[df["symbol"] == symbol].sort_values("timestamp").iloc[-1]
    with cols[i]:
        st.metric(symbol, f"{latest['peg_deviation']:+.4f}%")
        fig = build_peg_gauge_figure(latest["peg_deviation"], PEG_ALERT_THRESHOLD_PCT, COLORS)
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

st.divider()
st.subheader("Historique des écarts (24h)")

fig_hist = go.Figure()
palette = {"USDT": COLORS["accent_gold"], "USDC": COLORS["accent_indigo"], "DAI": COLORS["positive"]}

for symbol in selected_stablecoins:
    sub = df[df["symbol"] == symbol].sort_values("timestamp")
    sub = insert_gap_breaks(sub, value_cols=["peg_deviation"])
    fig_hist.add_trace(go.Scatter(
        x=sub["timestamp"], y=sub["peg_deviation"],
        mode="lines", name=symbol, line=dict(color=palette[symbol], width=1.5),
    ))

fig_hist.add_hrect(y0=-PEG_ALERT_THRESHOLD_PCT, y1=PEG_ALERT_THRESHOLD_PCT,
                    fillcolor="rgba(79, 155, 114, 0.08)", line_width=0)
fig_hist.add_hline(y=0, line_dash="dot", line_color=COLORS["text_muted"])
fig_hist.update_layout(
    plot_bgcolor=COLORS["bg"], paper_bgcolor=COLORS["bg"],
    font=dict(family="IBM Plex Sans", color=COLORS["text_primary"]),
    xaxis=dict(gridcolor=COLORS["surface_alt"], title=None),
    yaxis=dict(gridcolor=COLORS["surface_alt"], title="Écart (%)"),
    margin=dict(l=10, r=10, t=20, b=10), height=380,
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
)
st.plotly_chart(fig_hist, use_container_width=True)

st.divider()
st.subheader("Épisodes de franchissement de seuil")
alerts = df[df["seuil_alerte_franchi"]].sort_values("timestamp", ascending=False)
if alerts.empty:
    st.success(f"Aucun franchissement du seuil ({PEG_ALERT_THRESHOLD_PCT}%) sur les dernières 24h.")
else:
    st.dataframe(
        alerts[["symbol", "timestamp", "price_usd", "peg_deviation"]],
        use_container_width=True, hide_index=True,
    )
