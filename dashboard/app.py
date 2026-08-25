"""
Point d'entrée du dashboard — section 14 du document projet.
Chaque page correspond à une des 6 vues attendues.
"""
import streamlit as st

from theme import apply_custom_styles

st.set_page_config(
    page_title="Crypto Pipeline MVP — Dakar / UEMOA",
    page_icon="📊",
    layout="wide",
)

apply_custom_styles()

with st.sidebar:
    st.markdown(
        """
        <div style="display:flex;align-items:center;gap:0.6rem;
                    padding:0.8rem 0 1.2rem 0;
                    border-bottom:1px solid rgba(201,162,75,0.25);
                    margin-bottom:0.6rem;">
            <div style="font-size:1.7rem;">📊</div>
            <div>
                <div style="font-family:'Fraunces',serif;font-size:1.05rem;
                            color:#EDEAE0;line-height:1.15;">
                    Crypto Pipeline
                </div>
                <div style="font-family:'IBM Plex Mono',monospace;font-size:0.68rem;
                            color:#8C93A6;letter-spacing:0.06em;text-transform:uppercase;">
                    MVP · Dakar / UEMOA
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
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

with st.sidebar:
    st.markdown(
        """
        <div style="margin-top:1rem;padding-top:0.8rem;
                    border-top:1px solid rgba(201,162,75,0.15);
                    font-family:'IBM Plex Mono',monospace;font-size:0.7rem;
                    color:#8C93A6;">
            🟢 Pipeline actif — cycle 1 min
        </div>
        """,
        unsafe_allow_html=True,
    )

nav.run()
