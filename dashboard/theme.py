"""
Palette et styles additionnels du dashboard — au-delà de config.toml,
pour les cartes KPI, séparateurs et accents.
"""
import streamlit as st

COLORS = {
    "bg": "#101823",
    "surface": "#17212F",
    "surface_alt": "#1E2A3B",
    "accent_gold": "#C9A24B",
    "accent_indigo": "#5B6EE8",
    "positive": "#4F9B72",
    "negative": "#C1594A",
    "text_primary": "#EDEAE0",
    "text_muted": "#8C93A6",
}


def apply_custom_styles():
    st.markdown(f"""
        <style>
        [data-testid="stMetric"] {{
            background-color: {COLORS['surface']};
            border: 1px solid rgba(201, 162, 75, 0.15);
            border-radius: 0.5rem;
            padding: 1rem 1.2rem;
        }}
        [data-testid="stMetricValue"] {{
            font-family: 'IBM Plex Mono', monospace;
        }}
        [data-testid="stMetricLabel"] {{
            color: {COLORS['text_muted']};
            text-transform: uppercase;
            letter-spacing: 0.05em;
            font-size: 0.75rem;
        }}
        h1, h2, h3 {{
            font-family: 'Fraunces', serif !important;
            border-bottom: 1px solid rgba(201, 162, 75, 0.2);
            padding-bottom: 0.3rem;
        }}
        [data-testid="stSidebar"] {{
            background-color: {COLORS['surface']};
            border-right: 1px solid rgba(201, 162, 75, 0.1);
        }}
                [data-testid="stDataFrame"] {{
            font-family: 'IBM Plex Mono', monospace;
        }}
        [data-testid="stSidebarNavItems"] {{
            padding-top: 0.3rem;
        }}
        [data-testid="stSidebarNavItems"] li {{
            margin-bottom: 0.15rem;
        }}
        [data-testid="stSidebarNavItems"] a {{
            border-radius: 0.4rem;
            transition: background-color 0.15s ease;
        }}
        [data-testid="stSidebarNavItems"] a:hover {{
            background-color: rgba(201, 162, 75, 0.10);
        }}
        [data-testid="stSidebarNavItems"] a[aria-current="page"] {{
            background-color: rgba(201, 162, 75, 0.16);
            border-left: 2px solid {COLORS['accent_gold']};
        }}
        [data-testid="stSidebarNavItems"] span {{
            font-family: 'IBM Plex Sans', sans-serif;
            font-size: 0.88rem;
        }}
        </style>
    """, unsafe_allow_html=True)

# Palette pour comparer plusieurs actifs sur un même graphique — dérivée
# de la palette principale (variations d'or, indigo, sauge, terracotta)
# plutôt que des couleurs Plotly par défaut qui casseraient l'identité visuelle.
CHART_PALETTE = [
    "#C9A24B",  # or
    "#5B6EE8",  # indigo
    "#4F9B72",  # sauge
    "#C1594A",  # terracotta
    "#4FA8C9",  # sarcelle
    "#B87FC9",  # mauve
]
