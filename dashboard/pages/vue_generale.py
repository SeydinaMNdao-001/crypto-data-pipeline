"""
Vue générale — section 14 : les 12 actifs, marché global, volumes, évolution.
"""
import pandas as pd
import streamlit as st

from api_client import get_cryptos, get_latest, get_market_summary

st.title("🌍 Vue générale du marché")

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
st.bar_chart(df.set_index("Symbole")["Variation 24h (%)"])
