"""
Thème visuel du dashboard — palette, typographie, et menu de navigation
entièrement personnalisé (remplace le menu auto-généré de Streamlit).
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

CHART_PALETTE = [
    "#C9A24B", "#5B6EE8", "#4F9B72", "#C1594A", "#4FA8C9", "#B87FC9",
]


def apply_custom_styles():
    st.markdown("""
        <style>
        /* ---- Sidebar : largeur + fond dégradé ---- */
        [data-testid="stSidebar"][aria-expanded="true"] > div:first-child {
            width: 300px;
        }
        [data-testid="stSidebar"][aria-expanded="false"] > div:first-child {
            width: 300px;
            margin-left: -300px;
        }
        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, #17212F 0%, #101823 55%);
            border-right: 1px solid rgba(201, 162, 75, 0.15);
            box-shadow: 6px 0 30px rgba(0,0,0,0.35);
        }

        /* ---- Bloc de marque ---- */
        .nav-brand {
            display: flex; align-items: center; gap: 0.8rem;
            padding: 1.3rem 1rem 1.1rem 1rem;
            margin: -1rem -1rem 0.4rem -1rem;
            background: radial-gradient(120% 100% at 0% 0%, rgba(201,162,75,0.14) 0%, rgba(201,162,75,0) 65%);
            border-bottom: 1px solid rgba(201,162,75,0.22);
        }
        .nav-brand-icon {
            width: 44px; height: 44px; border-radius: 13px; flex-shrink: 0;
            display: flex; align-items: center; justify-content: center;
            font-size: 1.5rem;
            background: linear-gradient(135deg, rgba(201,162,75,0.28), rgba(91,110,232,0.18));
            border: 1px solid rgba(201,162,75,0.4);
        }
        .nav-brand-title {
            font-family: 'Fraunces', serif; font-weight: 600; font-size: 1.2rem;
            color: #EDEAE0; line-height: 1.15;
        }
        .nav-brand-subtitle {
            display: flex; align-items: center; gap: 0.4rem;
            font-family: 'IBM Plex Mono', monospace; font-size: 0.7rem;
            color: #8C93A6; letter-spacing: 0.05em; text-transform: uppercase;
            margin-top: 0.25rem;
        }
        .status-dot {
            width: 7px; height: 7px; border-radius: 50%;
            background: #4F9B72; display: inline-block;
            animation: pulse-dot 2s infinite;
        }
        @keyframes pulse-dot {
            0%   { box-shadow: 0 0 0 0 rgba(79,155,114,0.55); }
            70%  { box-shadow: 0 0 0 7px rgba(79,155,114,0); }
            100% { box-shadow: 0 0 0 0 rgba(79,155,114,0); }
        }

        /* ---- Libellés de section ---- */
        .nav-section-label {
            display: flex; align-items: center; gap: 0.5rem;
            font-family: 'IBM Plex Mono', monospace; font-size: 0.66rem;
            letter-spacing: 0.14em; text-transform: uppercase;
            color: #8C93A6; margin: 1.2rem 0.3rem 0.4rem 0.3rem;
        }
        .nav-section-label::after {
            content: ""; flex: 1; height: 1px;
            background: rgba(201,162,75,0.18);
        }

        /* ---- Liens de navigation (pilules) ---- */
        [data-testid="stPageLink"] {
            border-radius: 0.6rem !important;
            padding: 0.15rem 0.4rem !important;
            margin-bottom: 0.15rem !important;
            border: 1px solid transparent !important;
            transition: all 0.18s ease !important;
        }
        [data-testid="stPageLink"]:hover {
            background: rgba(201, 162, 75, 0.09) !important;
            border: 1px solid rgba(201, 162, 75, 0.28) !important;
            transform: translateX(4px);
        }
        [data-testid="stPageLink"] p {
            font-family: 'IBM Plex Sans', sans-serif !important;
            font-size: 0.92rem !important;
        }
        [data-testid="stPageLink"][aria-current="page"] {
            background: linear-gradient(90deg, rgba(201,162,75,0.2), rgba(201,162,75,0.02)) !important;
            border: 1px solid rgba(201,162,75,0.45) !important;
            box-shadow: inset 3px 0 0 0 #C9A24B;
        }

        /* ---- Pied de menu ---- */
        .nav-footer {
            margin-top: 1.4rem; padding-top: 0.9rem;
            border-top: 1px solid rgba(201,162,75,0.15);
            font-family: 'IBM Plex Mono', monospace; font-size: 0.68rem;
            color: #8C93A6;
        }

        /* ---- Reste de l'app (inchangé) ---- */
        [data-testid="stMetric"] {
            background-color: #17212F;
            border: 1px solid rgba(201, 162, 75, 0.15);
            border-radius: 0.5rem;
            padding: 1rem 1.2rem;
        }
        [data-testid="stMetricValue"] { font-family: 'IBM Plex Mono', monospace; }
        [data-testid="stMetricLabel"] {
            color: #8C93A6; text-transform: uppercase;
            letter-spacing: 0.05em; font-size: 0.75rem;
        }
        h1, h2, h3 {
            font-family: 'Fraunces', serif !important;
            border-bottom: 1px solid rgba(201, 162, 75, 0.2);
            padding-bottom: 0.3rem;
        }
        [data-testid="stDataFrame"] { font-family: 'IBM Plex Mono', monospace; }
        </style>
    """, unsafe_allow_html=True)


def render_custom_nav(pages: dict):
    """Construit le menu latéral entièrement à la main (remplace le menu
    auto-généré par st.navigation, caché via position='hidden')."""
    with st.sidebar:
        st.markdown("""
            <div class="nav-brand">
                <div class="nav-brand-icon">📊</div>
                <div>
                    <div class="nav-brand-title">Crypto Pipeline</div>
                    <div class="nav-brand-subtitle">
                        <span class="status-dot"></span> MVP · Dakar / UEMOA
                    </div>
                </div>
            </div>
        """, unsafe_allow_html=True)

        for group_name, group_pages in pages.items():
            st.markdown(f'<div class="nav-section-label">{group_name}</div>', unsafe_allow_html=True)
            for page in group_pages:
                st.page_link(page)

        st.markdown(
            '<div class="nav-footer">🟢 Pipeline actif — cycle 1 min</div>',
            unsafe_allow_html=True,
        )
