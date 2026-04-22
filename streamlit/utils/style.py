import streamlit as st

GLOBAL_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
}

#MainMenu { visibility: hidden; }
footer { visibility: hidden; }
header { visibility: hidden; }

.main .block-container {
    padding: 1.5rem 2rem 3rem 2rem;
    max-width: 1400px;
}

/* ── Page Header ── */
.page-header {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    border-radius: 16px;
    padding: 1.6rem 2rem;
    margin-bottom: 1.8rem;
    color: white;
    display: flex;
    align-items: center;
    gap: 1rem;
    box-shadow: 0 8px 32px rgba(102,126,234,0.28);
}
.page-header-icon { font-size: 2.4rem; line-height: 1; }
.page-header-text h1 {
    font-size: 1.75rem; font-weight: 700; margin: 0; color: white; line-height: 1.2;
}
.page-header-text p { font-size: 0.88rem; margin: 0.25rem 0 0 0; opacity: 0.85; }

/* ── KPI Cards ── */
.kpi-row {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
    gap: 1rem;
    margin-bottom: 1.6rem;
}
.kpi-card {
    background: #1e1e2e;
    border-radius: 14px;
    padding: 1.2rem 1.4rem;
    border: 1px solid #334155;
    box-shadow: 0 2px 8px rgba(0,0,0,0.2);
    transition: box-shadow 0.2s, transform 0.2s;
    cursor: default;
}
.kpi-card:hover {
    box-shadow: 0 6px 20px rgba(102,126,234,0.2);
    transform: translateY(-2px);
}
.kpi-icon { font-size: 1.5rem; margin-bottom: 0.3rem; }
.kpi-value { font-size: 1.9rem; font-weight: 800; color: #f8fafc; line-height: 1; }
.kpi-label { font-size: 0.78rem; color: #94a3b8; font-weight: 500; margin-top: 0.3rem; text-transform: uppercase; letter-spacing: 0.04em; }

/* ── Badges ── */
.badge {
    display: inline-block;
    padding: 0.22rem 0.6rem;
    border-radius: 999px;
    font-size: 0.75rem;
    font-weight: 600;
    letter-spacing: 0.025em;
    white-space: nowrap;
}
.badge-freemium  { background:#f1f5f9; color:#475569; border:1px solid #e2e8f0; }
.badge-premium   { background:#dbeafe; color:#1d4ed8; border:1px solid #bfdbfe; }
.badge-premiumplus { background:#ede9fe; color:#6d28d9; border:1px solid #ddd6fe; }
.badge-b2b       { background:#d1fae5; color:#065f46; border:1px solid #a7f3d0; }
.badge-user      { background:#334155; color:#e2e8f0; border:1px solid #475569; }
.badge-admin     { background:#4c1d95; color:#e9d5ff; border:1px solid #6d28d9; }

.badge-debutant      { background:#d1fae5; color:#065f46; border:1px solid #a7f3d0; }
.badge-intermediaire { background:#fef3c7; color:#92400e; border:1px solid #fde68a; }
.badge-avance        { background:#fee2e2; color:#991b1b; border:1px solid #fca5a5; }

.badge-cardio      { background:#dbeafe; color:#1d4ed8; border:1px solid #bfdbfe; }
.badge-force       { background:#fee2e2; color:#991b1b; border:1px solid #fca5a5; }
.badge-flexibilite { background:#d1fae5; color:#065f46; border:1px solid #a7f3d0; }
.badge-autre       { background:#f1f5f9; color:#475569; border:1px solid #e2e8f0; }

.badge-faible   { background:#d1fae5; color:#065f46; border:1px solid #a7f3d0; }
.badge-moderee  { background:#fef3c7; color:#92400e; border:1px solid #fde68a; }
.badge-elevee   { background:#fee2e2; color:#991b1b; border:1px solid #fca5a5; }

.badge-m       { background:#dbeafe; color:#1d4ed8; border:1px solid #bfdbfe; }
.badge-f       { background:#fce7f3; color:#9d174d; border:1px solid #fbcfe8; }
.badge-autre-g { background:#f1f5f9; color:#475569; border:1px solid #e2e8f0; }

/* ── Info card ── */
.info-card {
    background: #1e293b;
    border-radius: 14px;
    padding: 1.4rem 1.6rem;
    border: 1px solid #334155;
    box-shadow: 0 2px 8px rgba(0,0,0,0.2);
    margin-bottom: 1rem;
}
.info-card-title {
    font-size: 1rem; font-weight: 700; color: #f1f5f9; margin-bottom: 0.9rem;
    padding-bottom: 0.6rem; border-bottom: 2px solid #334155;
}
.info-row {
    display: flex; justify-content: space-between; align-items: center;
    padding: 0.4rem 0; border-bottom: 1px solid #334155; font-size: 0.87rem;
}
.info-row:last-child { border-bottom: none; }
.info-row-label { color: #94a3b8; font-weight: 500; }
.info-row-value { color: #f1f5f9; font-weight: 600; }

/* ── Macro bars ── */
.macro-bar-wrap { margin: 0.45rem 0; }
.macro-bar-label {
    display: flex; justify-content: space-between;
    font-size: 0.79rem; color: #475569; margin-bottom: 0.2rem; font-weight: 500;
}
.macro-bar-bg {
    background: #f1f5f9; border-radius: 999px; height: 7px; overflow: hidden;
}
.macro-bar-fill { height: 100%; border-radius: 999px; }

/* ── Section header ── */
.section-hdr {
    font-size: 1rem; font-weight: 700; color: #ffffff;
    margin: 1.6rem 0 0.8rem 0; display: flex; align-items: center; gap: 0.4rem;
    padding-left: 0.6rem; border-left: 3px solid #667eea;
}

/* Grille accueil "Fonctionnalités" : 2 × 3, toutes les cartes même hauteur (2 lignes égales) */
.fe-wrap {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    grid-template-rows: 1fr 1fr;
    gap: 1rem;
    margin-bottom: 0.75rem;
    min-height: min(70vh, 40rem);
    max-width: 100%;
    box-sizing: border-box;
}
@media (max-width: 900px) {
    .fe-wrap {
        grid-template-columns: 1fr;
        grid-template-rows: none;
        min-height: unset;
    }
}
@media (min-width: 601px) and (max-width: 900px) {
    .fe-wrap {
        grid-template-columns: repeat(2, 1fr);
        grid-template-rows: none;
        min-height: unset;
    }
    .fe-card { min-height: 12rem; }
}
.fe-card {
    display: flex;
    flex-direction: column;
    min-height: 0;
    height: 100%;
    background: #1e293b;
    border-radius: 14px;
    padding: 1.5rem;
    border: 1px solid #334155;
    box-shadow: 0 2px 8px rgba(0,0,0,0.2);
    box-sizing: border-box;
    transition: box-shadow 0.2s, border-color 0.2s;
    overflow: auto;
}
.fe-card:hover {
    box-shadow: 0 4px 16px rgba(102, 126, 234, 0.2);
    border-color: #475569;
}
.fe-card-icon {
    width: 46px;
    height: 46px;
    border-radius: 12px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.4rem;
    margin-bottom: 0.8rem;
    flex-shrink: 0;
}
.fe-card-title {
    font-size: 1rem;
    font-weight: 700;
    color: #f1f5f9;
    margin: 0 0 0.4rem 0;
    flex-shrink: 0;
}
.fe-card-desc {
    font-size: 0.85rem;
    color: #94a3b8;
    line-height: 1.5;
    margin: 0;
    flex: 1 1 auto;
    min-height: 0;
}

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #1e293b 0%, #0f172a 100%) !important;
}
[data-testid="stSidebar"] .stMarkdown,
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] span,
[data-testid="stSidebar"] label { color: #94a3b8 !important; }
[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3 { color: #f1f5f9 !important; }
[data-testid="stSidebar"] .stSuccess > div { background: rgba(16,185,129,0.15) !important; color: #6ee7b7 !important; border: 1px solid rgba(16,185,129,0.3) !important; }
[data-testid="stSidebar"] .stError > div { background: rgba(239,68,68,0.15) !important; color: #fca5a5 !important; }
[data-testid="stSidebar"] hr { border-color: #334155 !important; }
[data-testid="stSidebar"] a { color: #818cf8 !important; }
[data-testid="stSidebarNav"] a { color: #94a3b8 !important; border-radius: 8px; }
[data-testid="stSidebarNav"] a:hover { background: rgba(102,126,234,0.15) !important; color: white !important; }

/* ── Tabs (thème sombre) ── */
.stTabs [data-baseweb="tab-list"] { gap: 6px; background: #0f172a; border-radius: 10px; padding: 4px; border:1px solid #334155; }
.stTabs [data-baseweb="tab"] {
    border-radius: 8px; padding: 0.45rem 1.2rem; font-weight: 500;
    background: transparent; border: none; color: #94a3b8;
}
.stTabs [aria-selected="true"] {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
    color: white !important;
}

/* ── Metrics ── */
div[data-testid="metric-container"] {
    background: white;
    border: 1px solid #e2e8f0;
    border-radius: 12px;
    padding: 1rem 1.2rem;
    box-shadow: 0 2px 8px rgba(0,0,0,0.04);
}
div[data-testid="metric-container"] [data-testid="stMetricValue"] {
    font-size: 1.7rem; font-weight: 700; color: #1e293b;
}
div[data-testid="metric-container"] [data-testid="stMetricLabel"] {
    font-size: 0.78rem; color: #64748b; font-weight: 500; text-transform: uppercase; letter-spacing: 0.04em;
}

/* ── Buttons ── */
.stButton > button {
    border-radius: 10px; font-weight: 500; transition: all 0.2s;
    border: 1.5px solid #e2e8f0; background: white; color: #374151;
}
.stButton > button[kind="primary"],
.stButton > button[kind="secondaryFormSubmit"] {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
    border: none !important; color: white !important;
}
.stButton > button:hover {
    transform: translateY(-1px);
    box-shadow: 0 4px 12px rgba(102,126,234,0.25);
}

/* ── Dataframe ── */
[data-testid="stDataFrame"] iframe { border-radius: 10px; }

/* ── Formulaires (évite texte thème clair sur fond clair) ── */
[data-testid="stForm"] {
    background: #1e293b !important;
    border-radius: 14px;
    padding: 1.4rem 1.6rem;
    border: 1px solid #334155;
    box-shadow: 0 2px 8px rgba(0,0,0,0.2);
}
[data-testid="stForm"] p,
[data-testid="stForm"] label,
[data-testid="stForm"] [data-baseweb="form-control-container"] p,
[data-testid="stForm"] [data-baseweb="form-control-container"] label,
div[data-baseweb="select"] + label,
div[data-baseweb="input"] + label { color: #e2e8f0 !important; }
</style>
"""


def inject_css():
    st.markdown(GLOBAL_CSS, unsafe_allow_html=True)


def page_header(icon: str, title: str, subtitle: str = ""):
    sub = f"<p>{subtitle}</p>" if subtitle else ""
    st.markdown(f"""
    <div class="page-header">
        <div class="page-header-icon">{icon}</div>
        <div class="page-header-text"><h1>{title}</h1>{sub}</div>
    </div>
    """, unsafe_allow_html=True)


def kpi_cards(items: list):
    html = "".join(
        f'<div class="kpi-card">'
        f'<div class="kpi-icon">{i["icon"]}</div>'
        f'<div class="kpi-value">{i["value"]}</div>'
        f'<div class="kpi-label">{i["label"]}</div>'
        f'</div>'
        for i in items
    )
    st.markdown(f'<div class="kpi-row">{html}</div>', unsafe_allow_html=True)


def badge(value: str) -> str:
    if not value:
        return "<span>—</span>"
    css_key = (str(value).lower()
               .replace(" ", "").replace("+", "plus")
               .replace("é", "e").replace("è", "e").replace("ê", "e")
               .replace("ô", "o"))
    return f'<span class="badge badge-{css_key}">{value}</span>'


def macro_bar(label: str, value: float, max_val: float, color: str) -> str:
    try:
        pct = min(100, (float(value) / float(max_val) * 100)) if max_val else 0
        val_str = f"{float(value):.1f}g"
    except Exception:
        pct, val_str = 0, "—"
    return (
        f'<div class="macro-bar-wrap">'
        f'<div class="macro-bar-label"><span>{label}</span><span>{val_str}</span></div>'
        f'<div class="macro-bar-bg">'
        f'<div class="macro-bar-fill" style="width:{pct:.0f}%;background:{color};"></div>'
        f'</div></div>'
    )


def section_header(icon: str, title: str):
    st.markdown(f'<div class="section-hdr">{icon} {title}</div>', unsafe_allow_html=True)
