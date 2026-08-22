"""
Point d'entrée du dashboard — section 14 du document projet.
Chaque page correspond à une des 6 vues attendues.
"""
import streamlit as st

st.set_page_config(
    page_title="Crypto Pipeline MVP — Dakar / UEMOA",
    page_icon="📊",
    layout="wide",
)

pages = {
    "Marché": [
        st.Page("pages/vue_generale.py", title="Vue générale", icon="🌍", default=True),
        st.Page("pages/crypto_explorer.py", title="Crypto Explorer", icon="🔍"),
        st.Page("pages/comparaison.py", title="Comparaison", icon="⚖️"),
    ],
    "Sénégal / UEMOA": [
        st.Page("pages/stablecoins.py", title="Stablecoins", icon="🪙"),
        st.Page("pages/contexte_fcfa.py", title="Contexte FCFA / UEMOA", icon="🇸🇳"),
    ],
    "Technique": [
        st.Page("pages/qualite_pipeline.py", title="Qualité Pipeline", icon="⚙️"),
    ],
}

nav = st.navigation(pages)
nav.run()
