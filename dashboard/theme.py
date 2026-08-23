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
        </style>
    """, unsafe_allow_html=True)
