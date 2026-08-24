"""
Contexte FCFA / UEMOA — section 11.5 : prix en FCFA, résumé du peg,
comparatif volatilité crypto/FCFA, encart réglementaire BCEAO.
"""
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from api_client import get_cryptos, get_fx_rate_history, get_latest, get_peg_history, get_ranking
from theme import COLORS

st.title("🇸🇳 Contexte FCFA / UEMOA")

# --- 1. Prix et variations en FCFA -----------------------------------
st.subheader("Prix en FCFA")
cryptos = get_cryptos()
rows = []
for c in cryptos:
    try:
        latest = get_latest(c["symbol"])
        rows.append({
            "Symbole": c["symbol"],
            "Prix (FCFA)": latest["price_xof"],
            "Prix (USD)": latest["price_usd"],
            "Variation 24h (%)": latest["change_24h"],
        })
    except Exception:
        continue

df = pd.DataFrame(rows).sort_values("Prix (FCFA)", ascending=False)
st.dataframe(
    df, use_container_width=True, hide_index=True,
    column_config={
        "Prix (FCFA)": st.column_config.NumberColumn(format="%.2f FCFA"),
        "Prix (USD)": st.column_config.NumberColumn(format="$%.4f"),
        "Variation 24h (%)": st.column_config.NumberColumn(format="%.2f%%"),
    },
)
st.caption(
    "La variation en % est identique en FCFA et en USD — un taux de change "
    "fixe ne modifie pas un pourcentage, seulement la valeur absolue affichée."
)

st.divider()

# --- 2. Résumé du peg des stablecoins ---------------------------------
st.subheader("Stabilité des stablecoins (résumé)")
peg_hist = get_peg_history(hours=24)
if peg_hist:
    peg_df = pd.DataFrame(peg_hist)
    peg_df["timestamp"] = pd.to_datetime(peg_df["timestamp"])
    cols = st.columns(3)
    for i, symbol in enumerate(["USDT", "USDC", "DAI"]):
        sub = peg_df[peg_df["symbol"] == symbol].sort_values("timestamp")
        if sub.empty:
            continue
        latest_dev = sub.iloc[-1]["peg_deviation"]
        n_alerts = int(sub["seuil_alerte_franchi"].sum())
        with cols[i]:
            st.metric(symbol, f"{latest_dev:+.4f}%", f"{n_alerts} alerte(s) / 24h")
    st.caption("Détail complet : voir la page « Stablecoins ».")
else:
    st.info("Historique de peg encore trop court.")

st.divider()

# --- 3. Comparatif volatilité crypto / stabilité FCFA -------------------
st.subheader("Volatilité : cryptos vs FCFA")

ranking = get_ranking(metric="volatility", days=1)
fx_hist = get_fx_rate_history(hours=168)

labels = [r["symbol"] for r in ranking]
values = [r["rolling_volatility"] * 100 if r["rolling_volatility"] is not None else 0 for r in ranking]

fcfa_volatility = None
if len(fx_hist) >= 3:
    fx_df = pd.DataFrame(fx_hist)
    fx_df["pct_return"] = fx_df["usd_xof_rate"].pct_change()
    computed = fx_df["pct_return"].std()
    if pd.notna(computed):
        fcfa_volatility = computed * 100

if fcfa_volatility is not None:
    labels.append("FCFA (vs USD)")
    values.append(fcfa_volatility)

colors = [COLORS["accent_indigo"] if l == "FCFA (vs USD)" else COLORS["accent_gold"] for l in labels]

fig = go.Figure(go.Bar(x=labels, y=values, marker_color=colors))
fig.update_layout(
    plot_bgcolor=COLORS["bg"], paper_bgcolor=COLORS["bg"],
    font=dict(family="IBM Plex Sans", color=COLORS["text_primary"]),
    xaxis=dict(gridcolor=COLORS["surface_alt"]),
    yaxis=dict(gridcolor=COLORS["surface_alt"], title="Volatilité glissante (%)"),
    margin=dict(l=10, r=10, t=20, b=10), height=380,
)
st.plotly_chart(fig, use_container_width=True)

st.caption(
    "Le FCFA est arrimé à l'euro par traité, à un taux fixe (1 EUR = 655,957 XOF) : "
    "sa volatilité face à l'euro est nulle par construction, pas par mesure. "
    "La barre 'FCFA (vs USD)', quand elle apparaît, mesure sa variation face au "
    "dollar — qui provient uniquement des fluctuations EUR/USD, historiquement "
    "bien plus faibles que celles des crypto-actifs. Elle n'apparaît qu'une fois "
    "assez d'historique de taux accumulé."
)

st.divider()

# --- 4. Encart réglementaire -------------------------------------------
st.subheader("Position de la BCEAO")
st.info(
    "**Ce que dit la BCEAO, à la date de vérification ci-dessous :** "
    "la Banque centrale des États de l'Afrique de l'Ouest ne reconnaît "
    "pas les crypto-actifs comme une monnaie, ni comme un produit "
    "réglementé. Son gouverneur, Jean-Claude Kassi Brou, l'a rappelé "
    "fin juillet 2026 en résumant la position de l'institution : "
    "*« Ce n'est pas une monnaie. Ce n'est pas réglementé. »* Il appelle "
    "les usagers de l'UEMOA à la prudence.\n\n"
    "Aucun cadre réglementaire n'est en vigueur à ce jour pour les "
    "crypto-actifs dans la zone UEMOA. La BCEAO a mis en place un comité "
    "dédié (C-CRYPTO) chargé d'en élaborer un, sans calendrier annoncé. "
    "Le 8 mai 2026, elle a organisé à Dakar une conférence internationale "
    "sur les crypto-actifs et les innovations numériques, signe d'un "
    "engagement actif sur le sujet."
)
st.caption(
    "Dernière vérification : 23 août 2026 — "
    "[Communiqué BCEAO](https://www.bceao.int/fr/communique-presse/conference-internationale-2026-de-la-bceao-sur-le-theme-crypto-actifs-et) · "
    "[Agence Ecofin](https://www.agenceecofin.com/actualites-finance/2407-140478-uemoa-la-reglementation-des-cryptoactifs-reste-en-preparation-la-bceao-appelle-a-la-prudence)\n\n"
    "Cette section est fournie à titre informatif uniquement — ce n'est ni un "
    "conseil réglementaire, ni un conseil en investissement. La réglementation "
    "étant en évolution active, elle doit être relue et mise à jour périodiquement."
)
