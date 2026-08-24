"""
Qualité Pipeline — section 15 : fraîcheur, erreurs, latence, taux de réussite.
"""
import pandas as pd
import streamlit as st

from api_client import get_pipeline_quality
from theme import COLORS

st.title("⚙️ Qualité Pipeline")

window_label = st.selectbox("Fenêtre d'analyse", ["1h", "6h", "24h", "7 jours"], index=2)
window_hours_map = {"1h": 1, "6h": 6, "24h": 24, "7 jours": 168}
hours = window_hours_map[window_label]

data = get_pipeline_quality(hours=hours)

st.subheader("Par source")
for s in data["by_source"]:
    with st.container(border=True):
        cols = st.columns(4)
        cols[0].metric("Source", s["source"])

        rate = s["success_rate_pct"]
        rate_color = "🟢" if rate >= 95 else ("🟡" if rate >= 80 else "🔴")
        cols[1].metric("Taux de réussite", f"{rate_color} {rate:.1f}%", f"{s['actual_cycles']}/{s['expected_cycles']} cycles")

        mins = s["minutes_since_last"]
        if mins is not None:
            freshness_color = "🟢" if mins <= 3 else ("🟡" if mins <= 10 else "🔴")
            cols[2].metric("Fraîcheur", f"{freshness_color} {mins:.1f} min", "depuis la dernière collecte")
        else:
            cols[2].metric("Fraîcheur", "—")

        lat = s["avg_latency_seconds"]
        cols[3].metric("Latence de collecte", f"{lat:.1f} s" if lat is not None else "—", "source → ingestion")

st.caption(
    "Taux de réussite = nombre de cycles réellement observés / nombre de "
    "cycles attendus (1 par minute). Un incident d'orchestration ou une "
    "coupure réseau fait mécaniquement baisser ce chiffre sur la fenêtre "
    "concernée — c'est voulu, pas un défaut d'affichage."
)

st.divider()
st.subheader("Cycles incomplets récents")
st.caption(
    "Un cycle est 'incomplet' s'il contient moins d'actifs que prévu "
    "(12 pour CoinGecko, ~8+ pour Binance) — signe qu'une partie de la "
    "réponse API a échoué la validation pour ce cycle précis."
)

incomplete = data["incomplete_cycles"]
if not incomplete:
    st.success("Aucun cycle incomplet sur la période — toutes les collectes ont renvoyé le nombre d'actifs attendu.")
else:
    inc_df = pd.DataFrame(incomplete)
    st.dataframe(inc_df, use_container_width=True, hide_index=True)
