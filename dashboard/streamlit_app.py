"""
AquaStat — Dashboard Analytics Streamlit
Connecté à Databricks SQL Warehouse (gold tables)
Fallback données simulées si pas de connexion
"""
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import os
import requests as http_requests

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="AquaStat — Qualité de l'eau en France",
    page_icon="💧",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Custom CSS ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;0,700;1,400&family=DM+Sans:ital,wght@0,300;0,400;0,500;1,300&display=swap');

html, body, [class*="css"]           { font-family: 'DM Sans', sans-serif; }
.stApp                               { background: #0c0e12; }
[data-testid="stSidebar"]            { background: #0a0d14 !important;
                                       border-right: 1px solid rgba(255,255,255,0.05); }

h1, h2, h3, h4                       { font-family: 'Playfair Display', serif !important;
                                       color: #f0ece4 !important; font-weight: 400 !important; }

/* Metrics */
[data-testid="metric-container"]     { background: transparent; border: none; padding: 0 !important; }
[data-testid="metric-container"] label
                                     { color: #444c5e !important; font-size: 10px !important;
                                       letter-spacing: 0.15em; text-transform: uppercase; }
[data-testid="metric-container"] [data-testid="stMetricValue"]
                                     { color: #f0ece4 !important;
                                       font-family: 'Playfair Display', serif !important;
                                       font-size: 2.2rem !important; font-weight: 400 !important; }
[data-testid="metric-container"] [data-testid="stMetricDelta"]
                                     { color: #6b9e78 !important; }

/* Controls */
.stSelectbox label, .stSlider label  { color: #444c5e !important; font-size: 10px !important;
                                       letter-spacing: 0.12em; text-transform: uppercase; }
hr                                   { border-color: rgba(255,255,255,0.05) !important; }

/* Chapter heading */
.ch-label  { font-size: 10px; letter-spacing: 0.22em; text-transform: uppercase;
             color: #444c5e; margin-bottom: 4px; font-family: 'DM Sans', sans-serif; }
.ch-title  { font-family: 'Playfair Display', serif; font-size: 2rem; font-weight: 400;
             color: #f0ece4; margin: 0 0 6px; line-height: 1.15; }
.ch-accent { color: #c77b5a; font-style: italic; }
.ch-sub    { color: #5a6070; font-size: 13px; line-height: 1.65; max-width: 400px;
             margin-top: 6px; font-style: italic; }

/* Hero stat block */
.hero-stat       { margin-bottom: 0; }
.hero-stat-num   { font-family: 'Playfair Display', serif; font-size: 3rem;
                   color: #f0ece4; line-height: 1; letter-spacing: -0.02em; }
.hero-stat-label { font-size: 10px; letter-spacing: 0.18em; text-transform: uppercase;
                   color: #444c5e; margin-top: 4px; }

/* Map legend */
.legend-row   { display: flex; align-items: center; gap: 9px;
                margin-bottom: 8px; font-size: 11px; color: #7a8496; }
.legend-swatch{ width: 14px; height: 14px; border-radius: 3px; flex-shrink: 0; }
.legend-range { font-size: 10px; color: #444c5e; margin-left: auto; }

/* Parameter cards */
.param-card { background: #12151b; border: 1px solid rgba(255,255,255,0.05);
              border-radius: 10px; padding: 1.1rem 1.2rem; height: 100%; min-height: 120px; }
.param-icon { font-size: 1.2rem; margin-bottom: 8px; }
.param-name { font-family: 'Playfair Display', serif; font-size: 1rem;
              color: #f0ece4; margin-bottom: 5px; }
.param-desc { font-size: 11px; color: #444c5e; line-height: 1.55; font-style: italic; }

/* Commune ranking */
.rank-section-title { font-size: 10px; letter-spacing: 0.18em; text-transform: uppercase;
                      color: #444c5e; margin-bottom: 12px; }
.rank-section-hl    { font-family: 'Playfair Display', serif; font-size: 1.4rem;
                      color: #f0ece4; margin-bottom: 16px; display: block; }
.rank-row { display: flex; align-items: center; padding: 9px 0;
            border-bottom: 1px solid rgba(255,255,255,0.04); gap: 10px; }
.rank-num { font-family: 'Playfair Display', serif; font-size: 11px;
            color: #2c3040; width: 22px; flex-shrink: 0; }
.rank-info { flex: 1; min-width: 0; overflow: hidden; }
.rank-name { font-size: 13px; color: #c8c0b4; font-family: 'Playfair Display', serif;
             white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.rank-dept { font-size: 10px; color: #2c3040; letter-spacing: 0.1em;
             text-transform: uppercase; margin-top: 2px; }
.rank-bar-bg { width: 72px; height: 3px; background: rgba(255,255,255,0.05); border-radius: 2px; }
.rank-bar    { height: 3px; border-radius: 2px; }
.rank-pct    { font-size: 12px; width: 46px; text-align: right; flex-shrink: 0; }

/* Note box */
.note-box { font-size: 11px; color: #3d4455; line-height: 1.6; padding: 1rem 0;
            border-top: 1px solid rgba(255,255,255,0.04); }
.note-box b { color: #5a6070; letter-spacing: 0.1em; }

/* Badge */
.badge-live { display:inline-block; background:rgba(107,158,120,0.12);
              border:1px solid rgba(107,158,120,0.3); border-radius:100px;
              padding:2px 11px; font-size:10px; color:#6b9e78;
              font-family:'DM Sans',sans-serif; letter-spacing:0.1em; text-transform:uppercase; }
.badge-demo { display:inline-block; background:rgba(199,123,90,0.12);
              border:1px solid rgba(199,123,90,0.3); border-radius:100px;
              padding:2px 11px; font-size:10px; color:#c77b5a;
              font-family:'DM Sans',sans-serif; letter-spacing:0.1em; text-transform:uppercase; }
</style>
""", unsafe_allow_html=True)

# ── Plotly dark theme ──────────────────────────────────────────────────────────
_LAYOUT = dict(
    paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
    font=dict(family='DM Sans', color='#5a6070', size=11),
    margin=dict(t=30, b=40, l=50, r=20),
)
_AXIS = dict(
    gridcolor='rgba(255,255,255,0.04)', linecolor='rgba(255,255,255,0.06)',
    tickfont=dict(color='#2c3040', size=10), zerolinecolor='rgba(255,255,255,0.04)',
)

def styled(fig, h=340):
    fig.update_layout(**_LAYOUT, height=h)
    fig.update_xaxes(**_AXIS)
    fig.update_yaxes(**_AXIS)
    return fig

# ── Conformity tiers ───────────────────────────────────────────────────────────
TIER_ORDER  = ["Source (≥ 95 %)", "Conforme (88–95 %)", "Vigilance (80–88 %)", "Alerte (< 80 %)"]
TIER_COLORS = {
    "Source (≥ 95 %)":    "#1a3a5c",
    "Conforme (88–95 %)": "#3b5c48",
    "Vigilance (80–88 %)":"#6b4e2a",
    "Alerte (< 80 %)":    "#5c1f1f",
}
TIER_HEX = ["#1a3a5c", "#3b5c48", "#6b4e2a", "#5c1f1f"]

def conformite_tier(tc):
    tc = float(tc) if tc is not None else 0
    if tc >= 95: return "Source (≥ 95 %)"
    if tc >= 88: return "Conforme (88–95 %)"
    if tc >= 80: return "Vigilance (80–88 %)"
    return "Alerte (< 80 %)"

def normalize_dept_code(code):
    if str(code).upper() in ('02A', '2A'): return '2A'
    if str(code).upper() in ('02B', '2B'): return '2B'
    try:
        n = int(code)
        return f"{n:02d}" if n < 100 else f"{n:03d}"
    except Exception:
        return str(code)

# ── Credentials ────────────────────────────────────────────────────────────────
def _creds():
    try:
        if "databricks" in st.secrets:
            h = st.secrets["databricks"]["host"]
            p = st.secrets["databricks"]["http_path"]
            t = st.secrets["databricks"]["token"]
            if t:
                return h, p, t
    except Exception:
        pass
    return (os.getenv("DATABRICKS_HOST", ""),
            os.getenv("DATABRICKS_HTTP_PATH", ""),
            os.getenv("DATABRICKS_TOKEN", ""))

def _api_url():
    try:
        return st.secrets.get("api_url", "http://localhost:8000")
    except Exception:
        return os.getenv("API_URL", "http://localhost:8000")

# ── Databricks loader ──────────────────────────────────────────────────────────
@st.cache_data(ttl=3600, show_spinner=False)
def load_db(query):
    host, http_path, token = _creds()
    if not token:
        return None, "no_credentials"
    try:
        from databricks import sql
        with sql.connect(server_hostname=host, http_path=http_path, access_token=token) as conn:
            with conn.cursor() as cur:
                cur.execute(query)
                cols = [d[0] for d in cur.description]
                return pd.DataFrame(cur.fetchall(), columns=cols), "databricks"
    except Exception as e:
        return None, str(e)

@st.cache_data(ttl=3600, show_spinner=False)
def load_france_geojson():
    try:
        url = "https://raw.githubusercontent.com/gregoiredavid/france-geojson/master/departements-version-simplifiee.geojson"
        return http_requests.get(url, timeout=10).json()
    except Exception:
        return None

# ── Demo data ──────────────────────────────────────────────────────────────────
def _demo_temporal():
    m = ['Jan','Fév','Mar','Avr','Mai','Jun','Jul','Aoû','Sep','Oct','Nov','Déc']
    c = [24200,22800,26100,25400,27300,28900,31200,29800,26700,25100,23400,21700]
    return pd.DataFrame({'mois': m, 'nb_prelevements': c})

def _demo_params():
    p = ['Turbidité','E.coli','Nitrates','Chlore libre','pH',
         'Fluor','Pesticides','Arsenic','Plomb','Entérocoques',
         'Aluminium','Manganèse','Coliformes','Nitrites','Ammonium']
    c = [4820,3940,3210,2870,2430,2180,1950,1720,1540,1380,1240,1120,980,870,760]
    return pd.DataFrame({'nom_parametre': p, 'nb_nc': c})

def _demo_depts():
    noms  = ['Bouches-du-Rhône','Rhône','Gironde','Nord','Haute-Garonne',
             'Loire-Atlantique','Bas-Rhin','Alpes-Maritimes','Hérault','Ille-et-Vilaine',
             'Isère','Var','Marne','Loire','Seine-Maritime','Côte-d\'Or','Gard',
             'Finistère','Haute-Vienne','Paris']
    codes = ['13','69','33','59','31','44','67','06','34','35',
             '38','83','51','42','76','21','30','29','87','75']
    rng = np.random.default_rng(42)
    nb  = sorted(rng.integers(50000, 500000, 20).tolist(), reverse=True)
    tc  = [round(rng.uniform(78, 100), 1) for _ in range(20)]
    nc  = [int(n * (1 - t/100)) for n, t in zip(nb, tc)]
    return pd.DataFrame({'nom_departement': noms, 'code_dept': codes,
                         'nb_analyses': nb, 'nb_nc': nc, 'taux_conformite': tc})

def _demo_best():
    communes = ['Lyon','Saint-Paul','Jarrie','Clermont-Ferrand','Tours',
                'Boulogne-Billancourt','Annecy','Orléans','Cannes','Louveciennes']
    codes    = ['69','974','38','63','37','92','74','45','06','78']
    depts    = ['Rhône','La Réunion','Isère','Puy-de-Dôme','Indre-et-Loire',
                'Hauts-de-Seine','Haute-Savoie','Loiret','Alpes-Maritimes','Yvelines']
    return pd.DataFrame({'nom_commune': communes, 'code_dept': codes,
                         'nom_departement': depts, 'taux_conformite': [100.0]*10})

def _demo_worst():
    communes = ['Sennecey-le-Grand','Gueugnon','Villers-sur-Mer','Sinnamary','Vigeois',
                'Allassac','Romilly-sur-Seine','Mouans-Sartoux','St-Michel-de-Boulogne','Labastide-Rouairoux']
    codes    = ['71','71','14','973','19','19','10','06','07','81']
    depts    = ['Saône-et-Loire','Saône-et-Loire','Calvados','Guyane','Corrèze',
                'Corrèze','Aube','Alpes-Maritimes','Ardèche','Tarn']
    tc       = [6.3,10.7,16.4,25.5,30.8,30.9,44.9,47.1,48.0,48.2]
    return pd.DataFrame({'nom_commune': communes, 'code_dept': codes,
                         'nom_departement': depts, 'taux_conformite': tc})

# ── Main data loader ───────────────────────────────────────────────────────────
@st.cache_data(ttl=3600, show_spinner=False)
def get_all_data():
    source = "simulation"

    df_kpis, _ = load_db("""
        SELECT COUNT(*) AS total_analyses,
               SUM(CASE WHEN est_conforme = 'Non conforme' THEN 1 ELSE 0 END) AS total_nc,
               ROUND(SUM(CASE WHEN est_conforme = 'Conforme' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 1) AS taux_conformite
        FROM gold_fact_analyses
    """)

    df_temp, err = load_db("""
        SELECT DATE_FORMAT(date_prelevement, 'MMM') AS mois,
               MONTH(date_prelevement) AS mois_num,
               COUNT(*) AS nb_prelevements
        FROM gold_dim_prelevement
        WHERE date_prelevement IS NOT NULL
        GROUP BY 1, 2 ORDER BY 2
    """)
    if df_temp is None:
        df_temp = _demo_temporal()
    else:
        source = "databricks"

    df_params, _ = load_db("""
        SELECT p.libelle_parametre AS nom_parametre,
               COUNT(*) AS nb_nc
        FROM gold_fact_analyses f
        JOIN gold_dim_parametre p ON f.parametre_code = p.cdparametresiseeaux
        WHERE f.est_conforme = 'Non conforme'
        GROUP BY p.libelle_parametre
        ORDER BY nb_nc DESC LIMIT 20
    """)
    if df_params is None:
        df_params = _demo_params()

    df_depts, _ = load_db("""
        SELECT nom_departement,
               code_departement AS code_dept,
               nb_analyses,
               nb_non_conformes AS nb_nc,
               taux_conformite
        FROM gold_dim_departement
        ORDER BY nb_analyses DESC LIMIT 96
    """)
    if df_depts is None:
        df_depts = _demo_depts()

    df_best, _ = load_db("""
        SELECT f.commune AS nom_commune,
               f.departement_code AS code_dept,
               d.nom_departement,
               COUNT(*) AS nb_analyses,
               ROUND(SUM(CASE WHEN f.est_conforme = 'Conforme' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 1) AS taux_conformite
        FROM gold_fact_analyses f
        LEFT JOIN gold_dim_departement d ON f.departement_code = d.code_departement
        WHERE f.commune IS NOT NULL
        GROUP BY f.commune, f.departement_code, d.nom_departement
        HAVING COUNT(*) >= 200
        ORDER BY taux_conformite DESC, nb_analyses DESC
        LIMIT 10
    """)
    if df_best is None:
        df_best = _demo_best()

    df_worst, _ = load_db("""
        SELECT f.commune AS nom_commune,
               f.departement_code AS code_dept,
               d.nom_departement,
               COUNT(*) AS nb_analyses,
               ROUND(SUM(CASE WHEN f.est_conforme = 'Conforme' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 1) AS taux_conformite
        FROM gold_fact_analyses f
        LEFT JOIN gold_dim_departement d ON f.departement_code = d.code_departement
        WHERE f.commune IS NOT NULL
        GROUP BY f.commune, f.departement_code, d.nom_departement
        HAVING COUNT(*) >= 200
        ORDER BY taux_conformite ASC
        LIMIT 10
    """)
    if df_worst is None:
        df_worst = _demo_worst()

    return df_kpis, df_temp, df_params, df_depts, df_best, df_worst, source

# ── Parameter catalogue ────────────────────────────────────────────────────────
PARAMS_INFO = [
    {"icon": "∿",  "name": "pH",            "desc": "Acidité. Hors 6,5–9, l'eau corrode les conduites ou irrite les muqueuses."},
    {"icon": "◌",  "name": "Turbidité",     "desc": "Particules en suspension. Eau trouble = micro-organismes possibles."},
    {"icon": "≋",  "name": "Conductivité",  "desc": "Sels minéraux dissous. Une anomalie signale un changement de source ou une pollution."},
    {"icon": "⚡", "name": "E. coli",        "desc": "Bactérie fécale. Sa présence indique une contamination récente, risque digestif."},
    {"icon": "◎",  "name": "Entérocoques",  "desc": "Indicateur fécal complémentaire, plus persistant qu'E. coli dans le réseau."},
    {"icon": "—",  "name": "Coliformes",    "desc": "Famille bactérienne. Excès révèle un défaut de désinfection ou une intrusion."},
    {"icon": "△",  "name": "NH₄ (Ammonium)","desc": "Trace de pollution azotée, précurseur de nitrates. Surveille les effluents agricoles."},
    {"icon": "⊙",  "name": "Bact. aér.",    "desc": "Flore globale à 22 °C. Un pic traduit une stagnation ou un biofilm dans le réseau."},
    {"icon": "~",  "name": "Odeur",         "desc": "Test organoleptique. Une odeur persistante signale un traitement inadapté ou une contamination."},
]

# ── HTML builders ──────────────────────────────────────────────────────────────
def _param_card(info):
    return f"""
<div class="param-card">
  <div class="param-icon">{info['icon']}</div>
  <div class="param-name">{info['name']}</div>
  <div class="param-desc">{info['desc']}</div>
</div>"""

def _rank_row(rank, nom, code, dept, pct, is_best):
    bar_color = "#4a7c6f" if is_best else "#8b3030"
    pct_color = "#6b9e78" if is_best else "#c77b5a"
    bar_w     = min(100, max(2, float(pct) if pct is not None else 0))
    dept_str  = f"{code} · {str(dept).upper()}" if dept else code
    return f"""
<div class="rank-row">
  <span class="rank-num">{rank:02d}</span>
  <div class="rank-info">
    <div class="rank-name">{nom}</div>
    <div class="rank-dept">{dept_str}</div>
  </div>
  <div class="rank-bar-bg">
    <div class="rank-bar" style="width:{bar_w}%;background:{bar_color};"></div>
  </div>
  <span class="rank-pct" style="color:{pct_color};">{float(pct):.1f} %</span>
</div>"""

# ── SIDEBAR ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 💧 AquaStat")
    st.divider()
    st.caption("Contrôle sanitaire 2024 · data.gouv.fr")
    top_n = st.slider("Top N paramètres", 5, 20, 12)
    show_nc_only = st.checkbox("Depts avec non-conformités uniquement", value=False)
    st.divider()
    st.markdown(f"[FastAPI Docs]({_api_url()}/docs)")
    st.markdown("[GitHub](https://github.com/MariamDouamba/water-quality-pipeline)")

# ── LOAD ───────────────────────────────────────────────────────────────────────
with st.spinner("Chargement…"):
    df_kpis, df_temp, df_params, df_depts, df_best, df_worst, source = get_all_data()
    geojson = load_france_geojson()

is_live = source == "databricks"

# ── KPIs ───────────────────────────────────────────────────────────────────────
if df_kpis is not None and len(df_kpis) > 0:
    row      = df_kpis.iloc[0]
    total    = int(row['total_analyses'])
    total_nc = int(row['total_nc'])
    taux     = float(row['taux_conformite'])
else:
    total, total_nc, taux = 12_645_691, 28_140, 99.78

# ── HERO ───────────────────────────────────────────────────────────────────────
badge = f'<span class="badge-live">🟢 Live</span>' if is_live else f'<span class="badge-demo">🟡 Démo</span>'
st.markdown(f"""
<div style="padding: 2rem 0 1rem;">
  <div style="font-size:10px;letter-spacing:0.22em;text-transform:uppercase;color:#444c5e;margin-bottom:6px;">
    AQUASTAT — ATLAS DE LA QUALITÉ DE L'EAU EN FRANCE &nbsp;{badge}
  </div>
  <h1 style="font-family:'Playfair Display',serif;font-size:3rem;color:#f0ece4;font-weight:400;margin:0 0 4px;line-height:1.1;">
    L'eau de France,
  </h1>
  <h1 style="font-family:'Playfair Display',serif;font-size:3rem;color:#c77b5a;font-weight:400;font-style:italic;margin:0 0 1.5rem;line-height:1.1;">
    robinet par robinet.
  </h1>
  <p style="color:#5a6070;font-size:13px;font-style:italic;max-width:540px;line-height:1.7;margin:0;">
    37 000 communes. 9 paramètres. Un contrôle sanitaire permanent.
    Traité par le pipeline Databricks water-quality-pipeline, mis à jour annuellement.
  </p>
</div>
""", unsafe_allow_html=True)

h1, h2, h3, h4 = st.columns(4)
h1.metric("Communes", "34 811")
h2.metric("Prélèvements", f"{total//1000:,}k")
h3.metric("Non-conformes", f"{total_nc:,}")
h4.metric("Taux national", f"{taux} %")

st.markdown('<hr class="section-divider" style="margin:2rem 0;">', unsafe_allow_html=True)

# ── CHAPITRE 1 — LA CARTE ──────────────────────────────────────────────────────
col_l, col_r = st.columns([1, 2], gap="large")

with col_l:
    st.markdown("""
<div class="ch-label">Chapitre 1 / 4 — La cartographie</div>
<h2 class="ch-title">La France,<br><span class="ch-accent">territoire par territoire.</span></h2>
<p class="ch-sub">Chaque département coloré selon son niveau moyen de conformité.
Quatre niveaux reflètent la réalité sanitaire telle que calculée par le pipeline.</p>
""", unsafe_allow_html=True)

    st.markdown('<div style="margin-top:1.5rem;">', unsafe_allow_html=True)
    for tier, color in zip(TIER_ORDER, TIER_HEX):
        ranges = ["≥ 95 %", "88 – 95 %", "80 – 88 %", "< 80 %"]
        label  = tier.split(" (")[0]
        rang   = ranges[TIER_ORDER.index(tier)]
        st.markdown(f"""
<div class="legend-row">
  <div class="legend-swatch" style="background:{color};"></div>
  <span>{label}</span>
  <span class="legend-range">{rang}</span>
</div>""", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # Tier counts
    if df_depts is not None and 'taux_conformite' in df_depts.columns:
        df_tiers = df_depts.copy()
        df_tiers['tier'] = df_tiers['taux_conformite'].apply(conformite_tier)
        tier_counts = df_tiers['tier'].value_counts()
        st.markdown('<div style="margin-top:1.5rem;">', unsafe_allow_html=True)
        for tier in TIER_ORDER:
            cnt = tier_counts.get(tier, 0)
            label = tier.split(" (")[0]
            st.markdown(f"""
<div style="display:flex;justify-content:space-between;padding:4px 0;
 border-bottom:1px solid rgba(255,255,255,0.04);font-size:12px;color:#5a6070;">
  <span>{label}</span><span style="color:#f0ece4;">{cnt} depts</span>
</div>""", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

with col_r:
    if geojson and df_depts is not None and 'taux_conformite' in df_depts.columns:
        df_map = df_depts.copy()
        df_map['code_geo'] = df_map['code_dept'].apply(normalize_dept_code)
        df_map['taux_conformite'] = pd.to_numeric(df_map['taux_conformite'], errors='coerce')
        df_map['tier'] = df_map['taux_conformite'].apply(conformite_tier)
        df_map['tier'] = pd.Categorical(df_map['tier'], categories=TIER_ORDER, ordered=True)

        fig_map = px.choropleth(
            df_map,
            geojson=geojson,
            locations='code_geo',
            featureidkey='properties.code',
            color='tier',
            color_discrete_map=TIER_COLORS,
            category_orders={'tier': TIER_ORDER},
            hover_name='nom_departement',
            hover_data={
                'taux_conformite': ':.1f',
                'nb_analyses': ':,',
                'tier': False,
                'code_geo': False,
            },
            labels={'taux_conformite': 'Conformité %', 'nb_analyses': 'Analyses'},
        )
        fig_map.update_geos(fitbounds="locations", visible=False)
        fig_map.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            geo=dict(bgcolor='rgba(0,0,0,0)'),
            legend=dict(
                title=None,
                font=dict(color='#5a6070', size=11),
                bgcolor='rgba(0,0,0,0)',
                orientation='h',
                yanchor='bottom', y=-0.08,
                xanchor='left', x=0,
            ),
            margin=dict(t=0, b=0, l=0, r=0),
            height=500,
        )
        st.plotly_chart(fig_map, use_container_width=True)
    else:
        st.info("Carte non disponible.")

    st.markdown("""
<div class="note-box">
<b>NOTE</b> — Une non-conformité ponctuelle ne signifie pas que l'eau est impropre à la consommation.
Les seuils réglementaires sont volontairement prudents ; les seuils sanitaires effectifs sont nettement supérieurs.
Pour l'avis officiel sur votre eau, consultez l'ARS de votre région.
</div>""", unsafe_allow_html=True)

st.markdown('<hr class="section-divider" style="margin:2rem 0;">', unsafe_allow_html=True)

# ── CHAPITRE 2 — PARAMÈTRES ────────────────────────────────────────────────────
st.markdown("""
<div class="ch-label">Chapitre 2 / 4 — Que mesure-t-on ?</div>
<h2 class="ch-title">Neuf paramètres <span class="ch-accent">sous surveillance.</span></h2>
<p class="ch-sub">pH, turbidité, conductivité, bactéries coliformes, E. coli, entérocoques, ammonium,
bactéries aérobies revivifiables, odeur. Chacun a son seuil, son protocole, sa fréquence.</p>
""", unsafe_allow_html=True)

st.markdown('<div style="margin-top:1rem;">', unsafe_allow_html=True)
for i in range(0, 9, 3):
    cols = st.columns(3, gap="small")
    for j, col in enumerate(cols):
        if i + j < len(PARAMS_INFO):
            with col:
                st.markdown(_param_card(PARAMS_INFO[i + j]), unsafe_allow_html=True)
    st.markdown('<div style="height:8px;"></div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

st.markdown('<hr class="section-divider" style="margin:2rem 0;">', unsafe_allow_html=True)

# ── CHAPITRE 3 — LE PALMARÈS ───────────────────────────────────────────────────
st.markdown("""
<div class="ch-label">Chapitre 3 / 4 — Le palmarès des terroirs</div>
<h2 class="ch-title">Les <span class="ch-accent">exemplaires</span> et les <span class="ch-accent">fragiles.</span></h2>
<p class="ch-sub">La majorité des écarts se concentrent sur quelques communes — petites, isolées, parfois saisonnières.
Connaître la donnée, c'est la première étape pour la corriger.</p>
""", unsafe_allow_html=True)

st.markdown('<div style="height:1rem;"></div>', unsafe_allow_html=True)
col_best, col_worst = st.columns(2, gap="large")

with col_best:
    st.markdown("""
<div class="rank-section-title">Top conformité</div>
<span class="rank-section-hl">Les exemplaires</span>
""", unsafe_allow_html=True)
    if df_best is not None and len(df_best) > 0:
        html_best = ""
        for i, row in df_best.reset_index(drop=True).iterrows():
            html_best += _rank_row(
                i + 1,
                row.get('nom_commune', '—'),
                row.get('code_dept', ''),
                row.get('nom_departement', ''),
                row.get('taux_conformite', 100),
                True,
            )
        st.markdown(html_best, unsafe_allow_html=True)

with col_worst:
    st.markdown("""
<div class="rank-section-title">Bas du classement</div>
<span class="rank-section-hl">Les fragiles</span>
""", unsafe_allow_html=True)
    if df_worst is not None and len(df_worst) > 0:
        html_worst = ""
        for i, row in df_worst.reset_index(drop=True).iterrows():
            html_worst += _rank_row(
                i + 1,
                row.get('nom_commune', '—'),
                row.get('code_dept', ''),
                row.get('nom_departement', ''),
                row.get('taux_conformite', 0),
                False,
            )
        st.markdown(html_worst, unsafe_allow_html=True)

st.markdown('<hr class="section-divider" style="margin:2rem 0;">', unsafe_allow_html=True)

# ── CHAPITRE 4 — ÉVOLUTION & NC ────────────────────────────────────────────────
st.markdown("""
<div class="ch-label">Chapitre 4 / 4 — Lectures complémentaires</div>
<h2 class="ch-title">Vu <span class="ch-accent">autrement.</span></h2>
""", unsafe_allow_html=True)

col_ev, col_nc = st.columns(2, gap="large")

with col_ev:
    st.caption("Densité mensuelle — Prélèvements")
    fig_t = go.Figure()
    fig_t.add_trace(go.Bar(
        x=df_temp['mois'], y=df_temp['nb_prelevements'],
        marker_color='#1a3a5c',
        hovertemplate='<b>%{x}</b><br>%{y:,.0f} prélèvements<extra></extra>',
    ))
    st.plotly_chart(styled(fig_t, 300), use_container_width=True)

with col_nc:
    st.caption(f"Top {top_n} paramètres non conformes")
    df_p = df_params.head(top_n).sort_values('nb_nc')
    fig_p = go.Figure(go.Bar(
        x=df_p['nb_nc'], y=df_p['nom_parametre'],
        orientation='h',
        marker=dict(
            color=df_p['nb_nc'].tolist(),
            colorscale=[[0, '#1a3a5c'], [0.5, '#6b4e2a'], [1, '#5c1f1f']],
            showscale=False,
        ),
        hovertemplate='<b>%{y}</b><br>%{x:,.0f} NC<extra></extra>',
    ))
    st.plotly_chart(styled(fig_p, 300), use_container_width=True)

# Gauge + table
col_g, col_t = st.columns([1, 2], gap="large")

with col_g:
    fig_gauge = go.Figure(go.Indicator(
        mode="gauge+number",
        value=taux,
        number={'suffix': ' %', 'font': {'size': 36, 'color': '#f0ece4',
                'family': 'Playfair Display'}},
        title={'text': "Taux national pondéré", 'font': {'color': '#444c5e', 'size': 12,
               'family': 'DM Sans'}},
        gauge={
            'axis': {'range': [80, 100], 'tickfont': {'color': '#2c3040', 'size': 9}},
            'bar': {'color': '#1a3a5c', 'thickness': 0.28},
            'steps': [
                {'range': [80, 88], 'color': 'rgba(92,31,31,0.25)'},
                {'range': [88, 95], 'color': 'rgba(107,78,42,0.2)'},
                {'range': [95, 100],'color': 'rgba(26,58,92,0.2)'},
            ],
            'threshold': {'line': {'color': '#c77b5a', 'width': 2}, 'thickness': 0.8, 'value': 95},
        }
    ))
    fig_gauge.update_layout(
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#5a6070'), height=320,
        margin=dict(t=60, b=20, l=30, r=30)
    )
    st.plotly_chart(fig_gauge, use_container_width=True)

with col_t:
    if df_depts is not None and len(df_depts) > 0:
        df_d = df_depts.copy()
        if show_nc_only and 'nb_nc' in df_d.columns:
            df_d = df_d[df_d['nb_nc'] > 0]
        cols_show = [c for c in ['nom_departement','code_dept','nb_analyses','nb_nc','taux_conformite']
                     if c in df_d.columns]
        st.dataframe(
            df_d[cols_show].rename(columns={
                'nom_departement': 'Département',
                'code_dept': 'Code',
                'nb_analyses': 'Analyses',
                'nb_nc': 'Non-conformes',
                'taux_conformite': 'Conformité %',
            }),
            use_container_width=True, hide_index=True, height=310,
        )

# ── FOOTER ─────────────────────────────────────────────────────────────────────
st.markdown('<hr class="section-divider" style="margin:2.5rem 0 1rem;">', unsafe_allow_html=True)
st.markdown(f"""
<div style="display:flex;justify-content:space-between;align-items:flex-end;padding-bottom:2rem;">
  <div>
    <div style="font-family:'Playfair Display',serif;font-size:1.1rem;color:#f0ece4;">AquaStat</div>
    <div style="font-size:11px;color:#2c3040;margin-top:4px;line-height:1.6;">
      Atlas vivant de la qualité de l'eau en France. Source : data.gouv.fr / ARS,<br>
      traitement open-source via le pipeline Databricks water-quality-pipeline.
    </div>
  </div>
  <div style="text-align:right;font-size:11px;color:#2c3040;line-height:1.6;">
    Mariam Douamba · Simplon.co · 2026<br>
    Données 2024 · Contrôle sanitaire ARS
  </div>
</div>
""", unsafe_allow_html=True)
