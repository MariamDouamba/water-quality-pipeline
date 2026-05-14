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

st.set_page_config(
    page_title="AquaStat — Observatoire de l'eau",
    page_icon="💧",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Design system ──────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;600;700&family=JetBrains+Mono:wght@300;400;600&family=DM+Sans:ital,wght@0,300;0,400;1,300&display=swap');

html, body, [class*="css"]      { font-family: 'DM Sans', sans-serif; }
.stApp                          { background: #040c18; }
[data-testid="stSidebar"]       { background: #03090f !important;
                                  border-right: 1px solid rgba(56,178,248,0.08); }
h1,h2,h3,h4 { font-family: 'Space Grotesk', sans-serif !important;
               color: #d4e4f0 !important; font-weight: 600 !important; }

[data-testid="metric-container"]  { background: transparent; border: none; padding: 0 !important; }
[data-testid="metric-container"] label
  { color: #3a7aaa !important; font-size: 9px !important;
    letter-spacing: 0.22em; text-transform: uppercase;
    font-family: 'JetBrains Mono', monospace !important; }
[data-testid="metric-container"] [data-testid="stMetricValue"]
  { color: #38b2f8 !important; font-family: 'JetBrains Mono', monospace !important;
    font-size: 2rem !important; font-weight: 600 !important; }
[data-testid="metric-container"] [data-testid="stMetricDelta"] { color: #4fbf8e !important; }

.stSelectbox label, .stSlider label
  { color: #3a7aaa !important; font-size: 9px !important;
    letter-spacing: 0.15em; text-transform: uppercase; }
hr { border-color: rgba(56,178,248,0.07) !important; }

.aq-tag   { font-family:'JetBrains Mono',monospace; font-size:9px; letter-spacing:0.18em;
            text-transform:uppercase; color:#3a7aaa; margin-bottom:6px; display:block; }
.aq-title { font-family:'Space Grotesk',sans-serif; font-size:2rem; font-weight:700;
            color:#d4e4f0; margin:0 0 6px; line-height:1.1; }
.aq-title-accent { color:#38b2f8; }
.aq-title-amber  { color:#e8b86d; }
.aq-body  { color:#3d6a8a; font-size:13px; line-height:1.7; max-width:420px; margin-top:8px; }

.kpi-block { padding:0; }
.kpi-val   { font-family:'JetBrains Mono',monospace; font-size:2.4rem;
             font-weight:600; color:#38b2f8; line-height:1; }
.kpi-val-alert { color:#e05c5c !important; }
.kpi-val-sm    { font-size:1.1rem !important; white-space:nowrap; overflow:hidden;
                 text-overflow:ellipsis; max-width:100%; }
.kpi-label { font-family:'JetBrains Mono',monospace; font-size:9px; letter-spacing:0.2em;
             text-transform:uppercase; color:#3a7aaa; margin-top:5px; }

.tier-row { display:flex; align-items:center; gap:8px; padding:7px 0;
            border-bottom:1px solid rgba(56,178,248,0.06); }
.tier-dot { width:10px; height:10px; border-radius:2px; flex-shrink:0; }
.tier-lbl { font-size:11px; color:#8ec8e8; flex:1; font-weight:500; }
.tier-bar-bg { width:50px; height:3px; background:rgba(56,178,248,0.08);
               border-radius:2px; flex-shrink:0; }
.tier-bar    { height:3px; border-radius:2px; }
.tier-cnt { font-family:'JetBrains Mono',monospace; font-size:10px;
            color:#38b2f8; width:50px; text-align:right; flex-shrink:0; }

.dept-panel { background:#0a1420; border:1px solid rgba(56,178,248,0.1);
              border-radius:12px; padding:1.2rem; height:100%; }
.dept-name  { font-family:'Space Grotesk',sans-serif; font-size:1.5rem; font-weight:700;
              color:#d4e4f0; margin:6px 0 4px; line-height:1.1; }
.dept-tier  { font-family:'JetBrains Mono',monospace; font-size:9px; letter-spacing:0.15em;
              text-transform:uppercase; padding:2px 8px; border-radius:3px; display:inline-block; }
.dept-tc    { font-family:'JetBrains Mono',monospace; font-size:2rem; font-weight:600;
              color:#38b2f8; margin:10px 0 0; line-height:1; }
.dept-stat-row { display:flex; gap:16px; margin-top:10px; padding-top:10px;
                 border-top:1px solid rgba(56,178,248,0.06); }
.dept-stat     { flex:1; }
.dept-stat-val { font-family:'JetBrains Mono',monospace; font-size:1.1rem; font-weight:600;
                 color:#d4e4f0; }
.dept-stat-lbl { font-family:'JetBrains Mono',monospace; font-size:8px; letter-spacing:0.15em;
                 text-transform:uppercase; color:#3a7aaa; margin-top:2px; }
.dept-section  { margin-top:14px; padding-top:10px; border-top:1px solid rgba(56,178,248,0.06); }
.dept-section-title { font-family:'JetBrains Mono',monospace; font-size:8px; letter-spacing:0.18em;
                      text-transform:uppercase; color:#3a7aaa; margin-bottom:8px; display:block; }
.dept-param-row { display:flex; justify-content:space-between; padding:5px 0;
                  border-bottom:1px solid rgba(56,178,248,0.04); }
.dept-param-name { font-size:11px; color:#8ec8e8; }
.dept-param-nc   { font-family:'JetBrains Mono',monospace; font-size:11px; color:#e05c5c; }
.dept-commune-row { display:flex; align-items:center; gap:8px; padding:5px 0;
                    border-bottom:1px solid rgba(56,178,248,0.04); }
.dept-commune-name { font-size:11px; color:#8ec8e8; flex:1; }
.dept-commune-pct  { font-family:'JetBrains Mono',monospace; font-size:11px; color:#e8b86d; }
.dept-empty { color:#2a5a8a; font-size:12px; font-style:italic; text-align:center;
              padding:2rem 0.5rem; line-height:1.6; }

.pcard { background:#0d1828; border:1px solid rgba(56,178,248,0.08);
         border-radius:10px; padding:1.1rem; min-height:128px; }
.pcard-code { font-family:'JetBrains Mono',monospace; font-size:9px; letter-spacing:0.18em;
              text-transform:uppercase; color:#3a7aaa; margin-bottom:8px; }
.pcard-name { font-family:'Space Grotesk',sans-serif; font-size:1rem; font-weight:600;
              color:#d4e4f0; margin-bottom:6px; }
.pcard-desc { font-size:11px; color:#3d6a8a; line-height:1.55; }

.rank-head-tag { font-family:'JetBrains Mono',monospace; font-size:9px; letter-spacing:0.2em;
                 text-transform:uppercase; color:#3a7aaa; margin-bottom:8px; display:block; }
.rank-head-val { font-family:'Space Grotesk',sans-serif; font-size:1.3rem; font-weight:700;
                 color:#d4e4f0; margin-bottom:14px; display:block; }
.rrow { display:flex; align-items:center; padding:8px 0;
        border-bottom:1px solid rgba(56,178,248,0.05); gap:10px; }
.rrow-num  { font-family:'JetBrains Mono',monospace; font-size:10px;
             color:#2a5a8a; width:22px; flex-shrink:0; }
.rrow-info { flex:1; min-width:0; }
.rrow-name { font-family:'Space Grotesk',sans-serif; font-size:13px; font-weight:600;
             color:#b8d0e8; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }
.rrow-dept { font-family:'JetBrains Mono',monospace; font-size:9px; letter-spacing:0.1em;
             text-transform:uppercase; color:#2a5a8a; margin-top:2px; }
.rrow-bar-bg { width:64px; height:3px; background:rgba(56,178,248,0.08); border-radius:2px; }
.rrow-bar    { height:3px; border-radius:2px; }
.rrow-pct    { font-family:'JetBrains Mono',monospace; font-size:11px;
               width:46px; text-align:right; flex-shrink:0; }

.aq-note { font-size:11px; color:#3d6a8a; line-height:1.6; padding:0.8rem 0;
           border-top:1px solid rgba(56,178,248,0.06); }
.last-update { font-family:'JetBrains Mono',monospace; font-size:9px; letter-spacing:0.12em;
               text-transform:uppercase; color:#2a5a8a; margin:0 0 8px; display:block; }

.badge-live { font-family:'JetBrains Mono',monospace; font-size:9px; letter-spacing:0.15em;
              text-transform:uppercase; background:rgba(79,191,142,0.1);
              border:1px solid rgba(79,191,142,0.25); border-radius:4px;
              padding:3px 10px; color:#4fbf8e; display:inline-block; }
.badge-demo { font-family:'JetBrains Mono',monospace; font-size:9px; letter-spacing:0.15em;
              text-transform:uppercase; background:rgba(232,184,109,0.1);
              border:1px solid rgba(232,184,109,0.25); border-radius:4px;
              padding:3px 10px; color:#e8b86d; display:inline-block; }
</style>
""", unsafe_allow_html=True)

# ── Plotly theme ───────────────────────────────────────────────────────────────
_LAYOUT = dict(
    paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
    font=dict(family='DM Sans', color='#3d6a8a', size=11),
    margin=dict(t=30, b=40, l=50, r=20),
)
_AXIS = dict(
    gridcolor='rgba(56,178,248,0.05)', linecolor='rgba(56,178,248,0.08)',
    tickfont=dict(color='#3a7aaa', size=10, family='JetBrains Mono'),
    zerolinecolor='rgba(56,178,248,0.05)',
)

def styled(fig, h=340):
    fig.update_layout(**_LAYOUT, height=h)
    fig.update_xaxes(**_AXIS)
    fig.update_yaxes(**_AXIS)
    return fig

# ── Tiers ──────────────────────────────────────────────────────────────────────
TIER_ORDER  = ["Optimal (≥ 95 %)", "Satisfaisant (88–95 %)", "Insuffisant (80–88 %)", "Critique (< 80 %)"]
TIER_COLORS = {"Optimal (≥ 95 %)":"#1565c0","Satisfaisant (88–95 %)":"#5b8dd9",
               "Insuffisant (80–88 %)":"#c88520","Critique (< 80 %)":"#c83030"}
TIER_HEX    = ["#1565c0","#5b8dd9","#c88520","#c83030"]
TIER_BORDER = ["#38b2f8","#7ab8f5","#e8b86d","#e05c5c"]
TIER_BG     = ["rgba(21,101,192,0.15)","rgba(91,141,217,0.15)",
               "rgba(200,133,32,0.15)","rgba(200,48,48,0.15)"]

def conformite_tier(tc):
    tc = float(tc) if tc is not None else 0
    if tc >= 95: return "Optimal (≥ 95 %)"
    if tc >= 88: return "Satisfaisant (88–95 %)"
    if tc >= 80: return "Insuffisant (80–88 %)"
    return "Critique (< 80 %)"

def normalize_dept_code(code):
    if str(code).upper() in ('02A','2A'): return '2A'
    if str(code).upper() in ('02B','2B'): return '2B'
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
            if t: return h, p, t
    except Exception:
        pass
    return (os.getenv("DATABRICKS_HOST",""),
            os.getenv("DATABRICKS_HTTP_PATH",""),
            os.getenv("DATABRICKS_TOKEN",""))

def _api_url():
    try:    return st.secrets.get("api_url","http://localhost:8000")
    except: return os.getenv("API_URL","http://localhost:8000")

# ── Loaders ────────────────────────────────────────────────────────────────────
@st.cache_data(ttl=3600, show_spinner=False)
def load_db(query):
    host, http_path, token = _creds()
    if not token: return None, "no_credentials"
    try:
        from databricks import sql
        with sql.connect(server_hostname=host, http_path=http_path,
                         access_token=token) as conn:
            with conn.cursor() as cur:
                cur.execute(query)
                cols = [d[0] for d in cur.description]
                return pd.DataFrame(cur.fetchall(), columns=cols), "databricks"
    except Exception as e:
        return None, str(e)

@st.cache_data(ttl=3600, show_spinner=False)
def load_france_geojson():
    try:
        url = ("https://raw.githubusercontent.com/gregoiredavid/"
               "france-geojson/master/departements-version-simplifiee.geojson")
        return http_requests.get(url, timeout=10).json()
    except Exception:
        return None

@st.cache_data(ttl=3600, show_spinner=False)
def load_dept_detail(dept_code):
    safe = str(dept_code).replace("'", "")
    df_params, _ = load_db(f"""
        SELECT p.libelle_parametre AS nom_parametre, COUNT(*) AS nb_nc
        FROM gold_fact_analyses f
        JOIN gold_dim_parametre p ON f.parametre_code = p.cdparametresiseeaux
        WHERE f.est_conforme = 'Non conforme'
          AND f.departement_code = '{safe}'
        GROUP BY p.libelle_parametre ORDER BY nb_nc DESC LIMIT 5
    """)
    df_communes, _ = load_db(f"""
        SELECT commune AS nom_commune,
               ROUND(
                 SUM(CASE WHEN est_conforme='Conforme' THEN 1 ELSE 0 END)*100.0/
                 NULLIF(SUM(CASE WHEN est_conforme IN ('Conforme','Non conforme') THEN 1 ELSE 0 END),0),
                 1
               ) AS taux_conformite,
               SUM(CASE WHEN est_conforme IN ('Conforme','Non conforme') THEN 1 ELSE 0 END) AS nb
        FROM gold_fact_analyses
        WHERE departement_code = '{safe}'
          AND est_conforme IN ('Conforme','Non conforme')
          AND commune IS NOT NULL
        GROUP BY commune
        HAVING SUM(CASE WHEN est_conforme IN ('Conforme','Non conforme') THEN 1 ELSE 0 END) >= 30
        ORDER BY taux_conformite ASC LIMIT 5
    """)
    return df_params, df_communes

@st.cache_data(ttl=3600, show_spinner=False)
def load_available_years():
    df, _ = load_db("""
        SELECT DISTINCT YEAR(date_prelevement) AS annee
        FROM gold_dim_prelevement
        WHERE date_prelevement IS NOT NULL
        ORDER BY annee DESC
    """)
    return df

@st.cache_data(ttl=3600, show_spinner=False)
def load_last_update():
    df, _ = load_db("""
        SELECT MAX(date_prelevement) AS derniere_maj
        FROM gold_dim_prelevement
        WHERE date_prelevement IS NOT NULL
    """)
    return df

@st.cache_data(ttl=3600, show_spinner=False)
def load_communes_all():
    df, _ = load_db("""
        SELECT f.commune AS nom_commune,
               f.departement_code AS code_dept,
               d.nom_departement,
               SUM(CASE WHEN f.est_conforme IN ('Conforme','Non conforme') THEN 1 ELSE 0 END) AS nb_analyses,
               ROUND(
                 SUM(CASE WHEN f.est_conforme='Conforme' THEN 1 ELSE 0 END)*100.0/
                 NULLIF(SUM(CASE WHEN f.est_conforme IN ('Conforme','Non conforme') THEN 1 ELSE 0 END),0),
                 1
               ) AS taux_conformite
        FROM gold_fact_analyses f
        LEFT JOIN gold_dim_departement d ON f.departement_code = d.code_departement
        WHERE f.commune IS NOT NULL
          AND f.est_conforme IN ('Conforme','Non conforme')
        GROUP BY f.commune, f.departement_code, d.nom_departement
        HAVING SUM(CASE WHEN f.est_conforme IN ('Conforme','Non conforme') THEN 1 ELSE 0 END) >= 30
        ORDER BY taux_conformite ASC
    """)
    return df

@st.cache_data(ttl=3600, show_spinner=False)
def load_monthly_trend(year=None):
    yf = f"AND YEAR(date_prelevement) = {int(year)}" if year else ""
    df, _ = load_db(f"""
        SELECT MONTH(date_prelevement) AS mois_num,
               DATE_FORMAT(date_prelevement, 'MMM') AS mois,
               ROUND(
                 SUM(CASE WHEN est_conforme = 'Conforme' THEN 1 ELSE 0 END)*100.0 /
                 NULLIF(SUM(CASE WHEN est_conforme IN ('Conforme','Non conforme') THEN 1 ELSE 0 END),0),
                 2
               ) AS taux_conformite
        FROM gold_fact_analyses
        WHERE date_prelevement IS NOT NULL {yf}
        GROUP BY 1, 2
        ORDER BY 1
    """)
    return df

# ── Demo data ──────────────────────────────────────────────────────────────────
def _demo_temporal():
    m = ['Jan','Fév','Mar','Avr','Mai','Jun','Jul','Aoû','Sep','Oct','Nov','Déc']
    c = [24200,22800,26100,25400,27300,28900,31200,29800,26700,25100,23400,21700]
    return pd.DataFrame({'mois':m,'nb_prelevements':c})

def _demo_params():
    p = ['Turbidité','E.coli','Nitrates','Chlore libre','pH','Fluor','Pesticides',
         'Arsenic','Plomb','Entérocoques','Aluminium','Manganèse','Coliformes','Nitrites','Ammonium']
    c = [4820,3940,3210,2870,2430,2180,1950,1720,1540,1380,1240,1120,980,870,760]
    return pd.DataFrame({'nom_parametre':p,'nb_nc':c})

def _demo_depts():
    noms  = ['Bouches-du-Rhône','Rhône','Gironde','Nord','Haute-Garonne',
             'Loire-Atlantique','Bas-Rhin','Alpes-Maritimes','Hérault','Ille-et-Vilaine',
             'Isère','Var','Marne','Loire','Seine-Maritime',"Côte-d'Or",'Gard',
             'Finistère','Haute-Vienne','Paris']
    codes = ['13','69','33','59','31','44','67','06','34','35',
             '38','83','51','42','76','21','30','29','87','75']
    rng = np.random.default_rng(42)
    nb  = sorted(rng.integers(50000,500000,20).tolist(),reverse=True)
    tc  = [round(rng.uniform(96,100),2) for _ in range(20)]
    nc  = [int(n*(1-t/100)) for n,t in zip(nb,tc)]
    return pd.DataFrame({'nom_departement':noms,'code_dept':codes,
                         'nb_analyses':nb,'nb_nc':nc,'taux_conformite':tc})

def _demo_top():
    return pd.DataFrame({
        'nom_commune':['Lyon','Clermont-Ferrand','Tours','Annecy','Orléans',
                       'Boulogne-Billancourt','Cannes','Jarrie','Saint-Paul','Louveciennes'],
        'code_dept':['69','63','37','74','45','92','06','38','974','78'],
        'nom_departement':['Rhône','Puy-de-Dôme','Indre-et-Loire','Haute-Savoie','Loiret',
                           'Hauts-de-Seine','Alpes-Maritimes','Isère','La Réunion','Yvelines'],
        'taux_conformite':[100.0,99.9,99.8,99.8,99.7,99.7,99.6,99.5,99.5,99.4],
    })

def _demo_bottom():
    return pd.DataFrame({
        'nom_commune':['Sennecey-le-Grand','Gueugnon','Villers-sur-Mer','Sinnamary','Vigeois',
                       'Allassac','Romilly-sur-Seine','Mouans-Sartoux','Vielmur-sur-Agout','Labastide-Rouairoux'],
        'code_dept':['71','71','14','973','19','19','10','06','81','81'],
        'nom_departement':['Saône-et-Loire','Saône-et-Loire','Calvados','Guyane','Corrèze',
                           'Corrèze','Aube','Alpes-Maritimes','Tarn','Tarn'],
        'taux_conformite':[6.3,10.7,16.4,25.5,30.8,30.9,44.9,47.1,47.8,48.2],
    })

def _demo_communes_all():
    rng = np.random.default_rng(42)
    n   = 700
    taux = np.concatenate([
        rng.uniform(99.0, 100.0, int(n*0.52)),
        rng.uniform(95.0,  99.0, int(n*0.30)),
        rng.uniform(88.0,  95.0, int(n*0.09)),
        rng.uniform(80.0,  88.0, int(n*0.05)),
        rng.uniform( 0.0,  80.0, int(n*0.04)),
    ])
    nb = np.exp(rng.uniform(np.log(30), np.log(60000), len(taux))).astype(int)
    depts = ['13','69','33','59','31','44','67','06','34','35','38','83','51','42','76','21','30','29','87','75']
    dnames= ['Bouches-du-Rhône','Rhône','Gironde','Nord','Haute-Garonne','Loire-Atlantique',
             'Bas-Rhin','Alpes-Maritimes','Hérault','Ille-et-Vilaine','Isère','Var','Marne',
             'Loire','Seine-Maritime',"Côte-d'Or",'Gard','Finistère','Haute-Vienne','Paris']
    idx   = rng.integers(0, len(depts), len(taux))
    return pd.DataFrame({
        'nom_commune'   : [f"Commune_{i:04d}" for i in range(len(taux))],
        'code_dept'     : [depts[i]  for i in idx],
        'nom_departement': [dnames[i] for i in idx],
        'nb_analyses'   : nb,
        'taux_conformite': np.round(taux, 1),
    })

# ── Chargement principal ───────────────────────────────────────────────────────
@st.cache_data(ttl=3600, show_spinner=False)
def get_all_data(year=None):
    source = "simulation"
    yf = f"AND YEAR(date_prelevement) = {int(year)}" if year else ""

    df_kpis, _ = load_db("""
        SELECT COUNT(*) AS total_analyses,
               COUNT(DISTINCT commune) AS nb_communes,
               SUM(CASE WHEN est_conforme = 'Non conforme' THEN 1 ELSE 0 END) AS total_nc,
               ROUND(
                 SUM(CASE WHEN est_conforme = 'Conforme' THEN 1 ELSE 0 END)*100.0 /
                 NULLIF(SUM(CASE WHEN est_conforme IN ('Conforme','Non conforme') THEN 1 ELSE 0 END),0),
                 2
               ) AS taux_conformite
        FROM gold_fact_analyses
    """)

    df_temp, _ = load_db(f"""
        SELECT DATE_FORMAT(date_prelevement,'MMM') AS mois,
               MONTH(date_prelevement) AS mois_num,
               COUNT(*) AS nb_prelevements
        FROM gold_dim_prelevement
        WHERE date_prelevement IS NOT NULL {yf}
        GROUP BY 1,2 ORDER BY 2
    """)
    if df_temp is None:
        df_temp = _demo_temporal()
    else:
        source = "databricks"

    df_params, _ = load_db("""
        SELECT p.libelle_parametre AS nom_parametre, COUNT(*) AS nb_nc
        FROM gold_fact_analyses f
        JOIN gold_dim_parametre p ON f.parametre_code = p.cdparametresiseeaux
        WHERE f.est_conforme = 'Non conforme'
        GROUP BY p.libelle_parametre ORDER BY nb_nc DESC LIMIT 20
    """)
    if df_params is None:
        df_params = _demo_params()

    df_depts, _ = load_db("""
        SELECT nom_departement, code_departement AS code_dept,
               nb_analyses, nb_non_conformes AS nb_nc, taux_conformite
        FROM gold_dim_departement ORDER BY nb_analyses DESC LIMIT 96
    """)
    if df_depts is None:
        df_depts = _demo_depts()

    df_top, _ = load_db("""
        SELECT f.commune AS nom_commune, f.departement_code AS code_dept,
               d.nom_departement,
               SUM(CASE WHEN f.est_conforme IN ('Conforme','Non conforme') THEN 1 ELSE 0 END) AS nb_analyses,
               ROUND(
                 SUM(CASE WHEN f.est_conforme='Conforme' THEN 1 ELSE 0 END)*100.0/
                 NULLIF(SUM(CASE WHEN f.est_conforme IN ('Conforme','Non conforme') THEN 1 ELSE 0 END),0),1
               ) AS taux_conformite
        FROM gold_fact_analyses f
        LEFT JOIN gold_dim_departement d ON f.departement_code=d.code_departement
        WHERE f.commune IS NOT NULL AND f.est_conforme IN ('Conforme','Non conforme')
        GROUP BY f.commune,f.departement_code,d.nom_departement
        HAVING SUM(CASE WHEN f.est_conforme IN ('Conforme','Non conforme') THEN 1 ELSE 0 END)>=200
        ORDER BY taux_conformite DESC, nb_analyses DESC LIMIT 10
    """)
    if df_top is None:
        df_top = _demo_top()

    df_bottom, _ = load_db("""
        SELECT f.commune AS nom_commune, f.departement_code AS code_dept,
               d.nom_departement,
               SUM(CASE WHEN f.est_conforme IN ('Conforme','Non conforme') THEN 1 ELSE 0 END) AS nb_analyses,
               ROUND(
                 SUM(CASE WHEN f.est_conforme='Conforme' THEN 1 ELSE 0 END)*100.0/
                 NULLIF(SUM(CASE WHEN f.est_conforme IN ('Conforme','Non conforme') THEN 1 ELSE 0 END),0),1
               ) AS taux_conformite
        FROM gold_fact_analyses f
        LEFT JOIN gold_dim_departement d ON f.departement_code=d.code_departement
        WHERE f.commune IS NOT NULL AND f.est_conforme IN ('Conforme','Non conforme')
        GROUP BY f.commune,f.departement_code,d.nom_departement
        HAVING SUM(CASE WHEN f.est_conforme IN ('Conforme','Non conforme') THEN 1 ELSE 0 END)>=200
        ORDER BY taux_conformite ASC LIMIT 10
    """)
    if df_bottom is None:
        df_bottom = _demo_bottom()

    return df_kpis, df_temp, df_params, df_depts, df_top, df_bottom, source

# ── Constructeurs HTML ──────────────────────────────────────────────────────────
def _ranking_row(rank, nom, code, dept, pct, good):
    bar_color = "#38b2f8" if good else "#e05c5c"
    pct_color = "#38b2f8" if good else "#e05c5c"
    bar_w     = min(100, max(1, float(pct) if pct is not None else 0))
    dept_str  = f"{code} — {str(dept).upper()}" if dept else code
    return f"""<div class="rrow">
  <span class="rrow-num">{rank:02d}</span>
  <div class="rrow-info">
    <div class="rrow-name">{nom}</div>
    <div class="rrow-dept">{dept_str}</div>
  </div>
  <div class="rrow-bar-bg"><div class="rrow-bar" style="width:{bar_w}%;background:{bar_color};"></div></div>
  <span class="rrow-pct" style="color:{pct_color};">{float(pct):.1f}&nbsp;%</span>
</div>"""

def _dept_panel(dept_row, df_p, df_c):
    nom  = dept_row['nom_departement']
    tc   = float(dept_row['taux_conformite'])
    nb   = int(dept_row['nb_analyses'])
    nc   = int(dept_row['nb_nc'])
    tier = conformite_tier(tc)
    idx  = TIER_ORDER.index(tier)
    tier_color = TIER_BORDER[idx]
    tier_bg    = TIER_BG[idx]
    tier_lbl   = tier.split(" (")[0]

    params_html = ""
    if df_p is not None and len(df_p) > 0:
        for _, row in df_p.iterrows():
            params_html += f"""<div class="dept-param-row">
  <span class="dept-param-name">{row['nom_parametre']}</span>
  <span class="dept-param-nc">{int(row['nb_nc']):,} NC</span>
</div>"""
    else:
        params_html = '<p style="color:#2a5a8a;font-size:11px;font-style:italic;">Aucune non-conformité détectée</p>'

    communes_html = ""
    if df_c is not None and len(df_c) > 0:
        for _, row in df_c.iterrows():
            communes_html += f"""<div class="dept-commune-row">
  <span class="dept-commune-name">{row['nom_commune']}</span>
  <span class="dept-commune-pct">{float(row['taux_conformite']):.1f} %</span>
</div>"""
    else:
        communes_html = '<p style="color:#2a5a8a;font-size:11px;font-style:italic;">Données insuffisantes</p>'

    return f"""<div class="dept-panel">
  <span class="aq-tag">Département sélectionné</span>
  <div class="dept-name">{nom}</div>
  <span class="dept-tier" style="background:{tier_bg};color:{tier_color};border:1px solid {tier_color}44;">{tier_lbl}</span>
  <div class="dept-tc">{tc:.2f} %</div>
  <div class="dept-stat-row">
    <div class="dept-stat">
      <div class="dept-stat-val">{nb:,}</div>
      <div class="dept-stat-lbl">Analyses évaluées</div>
    </div>
    <div class="dept-stat">
      <div class="dept-stat-val" style="color:#e05c5c;">{nc:,}</div>
      <div class="dept-stat-lbl">Non-conformes</div>
    </div>
  </div>
  <div class="dept-section">
    <span class="dept-section-title">Indicateurs à risque</span>
    {params_html}
  </div>
  <div class="dept-section">
    <span class="dept-section-title">Communes les plus touchées</span>
    {communes_html}
  </div>
</div>"""

# ── PRÉ-SIDEBAR : années & dernière mise à jour ────────────────────────────────
_df_years_avail = load_available_years()
_years_list = []
if _df_years_avail is not None and len(_df_years_avail) > 0:
    _years_list = sorted(_df_years_avail['annee'].dropna().astype(int).tolist(), reverse=True)

_df_last_upd = load_last_update()
_last_update_str = ""
if _df_last_upd is not None and len(_df_last_upd) > 0:
    _lu = _df_last_upd.iloc[0].get('derniere_maj')
    if _lu is not None:
        _last_update_str = str(_lu)[:10]

# ── SIDEBAR ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 💧 AquaStat")
    st.divider()

    selected_year = None
    if len(_years_list) > 1:
        _year_opts = ["Toutes les années"] + [str(y) for y in _years_list]
        _year_sel  = st.selectbox("Année", _year_opts)
        selected_year = None if _year_sel == "Toutes les années" else int(_year_sel)
    elif len(_years_list) == 1:
        st.caption(f"Données {_years_list[0]}")

    top_n   = st.slider("Indicateurs NC à afficher", 5, 20, 12)
    nc_only = st.checkbox(
        "Carte : dép. avec NC uniquement", value=False,
        help="Masque les départements sans non-conformité sur la carte et dans le tableau",
    )
    st.divider()

    if _last_update_str:
        st.markdown(f'<span class="last-update">Données au {_last_update_str}</span>',
                    unsafe_allow_html=True)
    st.markdown(f"[API REST]({_api_url()}/docs) · [GitHub](https://github.com/MariamDouamba/water-quality-pipeline)")

# ── CHARGEMENT ─────────────────────────────────────────────────────────────────
with st.spinner("Chargement…"):
    df_kpis, df_temp, df_params, df_depts, df_top, df_bottom, source = get_all_data(year=selected_year)
    geojson        = load_france_geojson()
    df_trend       = load_monthly_trend(year=selected_year)
    df_communes_all = load_communes_all()
    if df_communes_all is None:
        df_communes_all = _demo_communes_all()

is_live = source == "databricks"

# Résolution des KPIs
if df_kpis is not None and len(df_kpis) > 0:
    r            = df_kpis.iloc[0]
    total        = int(r['total_analyses'])
    total_nc     = int(r['total_nc'])
    taux         = float(r['taux_conformite'])
    nb_communes  = int(r['nb_communes']) if 'nb_communes' in r.index else 34_811
else:
    total, total_nc, taux, nb_communes = 12_645_691, 28_140, 99.78, 34_811

nb_prelevements   = int(df_temp['nb_prelevements'].sum()) if is_live else 291_604
top_param         = df_params.iloc[0]['nom_parametre'] if df_params is not None and len(df_params) > 0 else "Turbidité"
top_param_nc      = int(df_params.iloc[0]['nb_nc'])    if df_params is not None and len(df_params) > 0 else 4820
top_param_display = (top_param[:16] + "…") if len(top_param) > 18 else top_param

# ═══════════════════════════════════════════════════════════════════════════════
# BLOC 1 — EN-TÊTE
# ═══════════════════════════════════════════════════════════════════════════════
badge = ('<span class="badge-live">LIVE · Databricks</span>'
         if is_live else '<span class="badge-demo">DÉMO · Données simulées</span>')

_year_label = f" · {selected_year}" if selected_year else " · 2024"

st.markdown(f"""
<div style="padding:2rem 0 0.5rem;">
  <div style="display:flex;align-items:center;gap:12px;margin-bottom:1rem;">
    <span style="font-family:'JetBrains Mono',monospace;font-size:9px;
                 letter-spacing:0.22em;text-transform:uppercase;color:#3a7aaa;">
      AQUASTAT — OBSERVATOIRE DE LA QUALITÉ DE L'EAU EN FRANCE{_year_label}
    </span>
    {badge}
  </div>
  <h1 style="font-family:'Space Grotesk',sans-serif;font-size:2.8rem;
             font-weight:700;color:#d4e4f0;margin:0;line-height:1.05;">
    Chaque goutte <span style="color:#38b2f8;">analysée.</span>
  </h1>
  <p style="color:#3d6a8a;font-size:13px;line-height:1.75;max-width:560px;margin:12px 0 0;">
    AquaStat agrège les résultats du contrôle sanitaire officiel de l'eau potable distribué
    aux robinets français. Données brutes data.gouv.fr, transformées par le pipeline Databricks.
  </p>
</div>
""", unsafe_allow_html=True)

# ── 6 KPIs live ────────────────────────────────────────────────────────────────
def _kpi(col, val, lbl, alert=False, small=False):
    cls = "kpi-val"
    if alert: cls += " kpi-val-alert"
    if small: cls += " kpi-val-sm"
    col.markdown(f"""<div class="kpi-block">
  <div class="{cls}">{val}</div>
  <div class="kpi-label">{lbl}</div>
</div>""", unsafe_allow_html=True)

k1,k2,k3,k4,k5,k6 = st.columns(6)
_kpi(k1, f"{total/1_000_000:.1f}M", "Analyses totales")
_kpi(k2, f"{nb_prelevements:,}",    "Prélèvements")
_kpi(k3, f"{nb_communes:,}",        "Communes")
_kpi(k4, f"{total_nc:,}",           "Non-conformités", alert=True)
_kpi(k5, f"{taux:.2f} %",           "Taux conformité")
_kpi(k6, top_param_display,         f"Param. prioritaire · {top_param_nc:,} NC", small=True)

st.markdown('<hr style="margin:2rem 0;border-color:rgba(56,178,248,0.07);">', unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
# BLOC 2 — CARTE INTERACTIVE
# ═══════════════════════════════════════════════════════════════════════════════
col_leg, col_map_c, col_detail = st.columns([1, 2, 1], gap="medium")

with col_leg:
    st.markdown("""
<span class="aq-tag">Répartition géographique</span>
<h2 class="aq-title" style="font-size:1.4rem;">Conformité<br>par <span class="aq-title-accent">département.</span></h2>
<p class="aq-body" style="font-size:12px;">Cliquez sur un département pour afficher ses indicateurs détaillés.</p>
""", unsafe_allow_html=True)

    if df_depts is not None and 'taux_conformite' in df_depts.columns:
        df_t       = df_depts.copy()
        df_t['tier'] = df_t['taux_conformite'].apply(conformite_tier)
        cnt          = df_t['tier'].value_counts()
        total_depts  = max(len(df_t), 1)

        st.markdown('<div style="margin-top:1rem;">', unsafe_allow_html=True)
        for tier, color, border in zip(TIER_ORDER, TIER_HEX, TIER_BORDER):
            lbl   = tier.split(" (")[0]
            n     = cnt.get(tier, 0)
            pct_w = round(n / total_depts * 100)
            st.markdown(f"""<div class="tier-row">
  <div class="tier-dot" style="background:{color};box-shadow:0 0 0 1px {border}33;"></div>
  <span class="tier-lbl">{lbl}</span>
  <div class="tier-bar-bg"><div class="tier-bar" style="width:{pct_w}%;background:{color};"></div></div>
  <span class="tier-cnt">{n} dép.</span>
</div>""", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # Jauge [80–100] avec zones par tier
    fig_gauge = go.Figure(go.Indicator(
        mode="gauge+number",
        value=taux,
        number={'suffix':' %','font':{'size':24,'color':'#38b2f8','family':'JetBrains Mono'}},
        title={'text':"Taux national",'font':{'color':'#3a7aaa','size':10,'family':'JetBrains Mono'}},
        gauge={
            'axis':{'range':[80,100],'tickvals':[80,88,95,100],
                    'tickfont':{'color':'#3a7aaa','size':9,'family':'JetBrains Mono'}},
            'bar':{'color':'#38b2f8','thickness':0.22},
            'steps':[
                {'range':[80.0,88.0],'color':'rgba(200,133,32,0.20)'},
                {'range':[88.0,95.0],'color':'rgba(91,141,217,0.20)'},
                {'range':[95.0,100], 'color':'rgba(56,178,248,0.12)'},
            ],
            'threshold':{'line':{'color':'#e8b86d','width':2},'thickness':0.8,'value':95},
        }
    ))
    fig_gauge.update_layout(
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#3d6a8a'), height=200,
        margin=dict(t=40, b=10, l=20, r=20)
    )
    st.plotly_chart(fig_gauge, use_container_width=True)

# ── Carte cliquable ─────────────────────────────────────────────────────────────
with col_map_c:
    selected_code = None

    if geojson and df_depts is not None and 'taux_conformite' in df_depts.columns:
        df_map = df_depts.copy()
        if nc_only and 'nb_nc' in df_map.columns:
            df_map = df_map[df_map['nb_nc'] > 0]
        df_map['code_geo']        = df_map['code_dept'].apply(normalize_dept_code)
        df_map['taux_conformite'] = pd.to_numeric(df_map['taux_conformite'], errors='coerce')

        tc_vals   = df_map['taux_conformite'].dropna()
        range_low = min(float(tc_vals.min()) - 3.0, 90.0) if len(tc_vals) > 0 else 90.0

        fig_map = px.choropleth(
            df_map,
            geojson=geojson,
            locations='code_geo',
            featureidkey='properties.code',
            color='taux_conformite',
            color_continuous_scale=[
                [0.00,"#c83030"],[0.30,"#c88520"],
                [0.55,"#5b8dd9"],[1.00,"#38b2f8"],
            ],
            range_color=[range_low, 100.0],
            hover_name='nom_departement',
            hover_data={'taux_conformite':':.2f','nb_analyses':':,','code_geo':False},
            labels={'taux_conformite':'Conformité %','nb_analyses':'Analyses'},
        )
        fig_map.update_geos(fitbounds="locations", visible=False)
        fig_map.update_traces(marker_line_color='rgba(4,12,24,0.7)', marker_line_width=0.4)
        fig_map.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            geo=dict(bgcolor='rgba(0,0,0,0)'),
            coloraxis_colorbar=dict(
                title=dict(text="Conformité %",
                           font=dict(color='#3a7aaa',size=10,family='JetBrains Mono')),
                tickfont=dict(color='#3a7aaa',size=9,family='JetBrains Mono'),
                thickness=10, len=0.55, x=1.01,
            ),
            margin=dict(t=10,b=10,l=0,r=0),
            height=430,
        )

        event = st.plotly_chart(
            fig_map, use_container_width=True,
            on_select="rerun", key="aquastat_map",
        )
        if event and event.selection and event.selection.points:
            selected_code = event.selection.points[0].get('location')
    else:
        st.info("Carte non disponible.")

    st.markdown("""<div class="aq-note">
<b>Avertissement</b> — Un taux de non-conformité, même élevé, ne signifie pas que l'eau est impropre
à la consommation. Les seuils réglementaires sont volontairement prudents. En cas de doute, consultez l'ARS.
</div>""", unsafe_allow_html=True)

# ── Panneau de détail ───────────────────────────────────────────────────────────
with col_detail:
    if selected_code and df_depts is not None:
        dept_rows = df_depts[df_depts['code_dept'].apply(normalize_dept_code) == selected_code]
        if len(dept_rows) > 0:
            dept_row = dept_rows.iloc[0]
            raw_code = dept_row['code_dept']
            with st.spinner("Chargement…"):
                df_p, df_c = load_dept_detail(raw_code)
            st.markdown(_dept_panel(dept_row, df_p, df_c), unsafe_allow_html=True)
        else:
            st.markdown('<div class="dept-panel"><p class="dept-empty">Département non trouvé dans les données.</p></div>', unsafe_allow_html=True)
    else:
        st.markdown("""<div class="dept-panel">
<p class="dept-empty">
  Cliquez sur un département<br>pour afficher ses<br>indicateurs détaillés.
</p>
</div>""", unsafe_allow_html=True)

st.markdown('<hr style="margin:2rem 0;border-color:rgba(56,178,248,0.07);">', unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
# BLOC 3 — ANALYSE APPROFONDIE DES COMMUNES
# ═══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<span class="aq-tag">Analyse approfondie</span>
<h2 class="aq-title">Communes <span class="aq-title-accent">sous la loupe.</span></h2>
<p class="aq-body">Distribution des taux de conformité, relation taille/qualité et recherche par commune
sur l'ensemble des points de distribution avec au moins 30 analyses évaluées.</p>
""", unsafe_allow_html=True)

_ca = df_communes_all.copy()
_ca['tier'] = _ca['taux_conformite'].apply(conformite_tier)

ca1, ca2 = st.columns(2, gap="large")

with ca1:
    st.markdown('<span class="aq-tag">Distribution des taux de conformité</span>', unsafe_allow_html=True)
    _bins   = [0, 50, 80, 88, 95, 99, 100.01]
    _labels = ['< 50 %', '50–80 %', '80–88 %', '88–95 %', '95–99 %', '≥ 99 %']
    _colors = ['#c83030', '#c83030', '#c88520', '#5b8dd9', '#1565c0', '#38b2f8']
    _counts, _ = np.histogram(_ca['taux_conformite'].dropna(), bins=_bins)
    _total_c   = int(_counts.sum()) or 1
    fig_hist = go.Figure(go.Bar(
        x=_labels, y=_counts,
        marker_color=_colors,
        text=[f"{v:,}" for v in _counts],
        textposition='outside',
        textfont=dict(color='#8ec8e8', size=10, family='JetBrains Mono'),
        hovertemplate='<b>%{x}</b><br>%{y:,} communes · %{customdata:.1f} %<extra></extra>',
        customdata=_counts / _total_c * 100,
    ))
    fig_hist.update_layout(
        **_LAYOUT, height=300,
        yaxis_title="Communes",
        bargap=0.15,
    )
    fig_hist.update_xaxes(**_AXIS)
    fig_hist.update_yaxes(**_AXIS)
    st.plotly_chart(fig_hist, use_container_width=True)
    st.markdown(
        f'<p style="font-size:11px;color:#2a5a8a;margin-top:-12px;">'
        f'{len(_ca):,} communes analysées · seuil min. 30 analyses évaluées</p>',
        unsafe_allow_html=True,
    )

with ca2:
    st.markdown('<span class="aq-tag">Taille vs conformité — chaque point est une commune</span>',
                unsafe_allow_html=True)
    fig_sc = px.scatter(
        _ca,
        x='nb_analyses', y='taux_conformite',
        color='tier',
        color_discrete_map=TIER_COLORS,
        log_x=True,
        opacity=0.55,
        hover_name='nom_commune',
        hover_data={
            'nom_departement': True,
            'nb_analyses': ':,',
            'taux_conformite': ':.1f',
            'tier': False,
            'code_dept': False,
        },
        labels={'nb_analyses': 'Analyses évaluées (échelle log)', 'taux_conformite': 'Conformité %'},
    )
    fig_sc.update_traces(marker=dict(size=5))
    fig_sc.update_layout(
        **_LAYOUT, height=300,
        legend=dict(
            title=None, orientation='h', y=-0.28,
            font=dict(color='#8ec8e8', size=10, family='JetBrains Mono'),
            bgcolor='rgba(0,0,0,0)',
        ),
    )
    fig_sc.update_xaxes(**_AXIS)
    fig_sc.update_yaxes(**_AXIS)
    st.plotly_chart(fig_sc, use_container_width=True)

# ── Recherche de commune ────────────────────────────────────────────────────────
st.markdown('<span class="aq-tag" style="margin-top:0.5rem;display:block;">Rechercher une commune</span>',
            unsafe_allow_html=True)
_search_col, _ = st.columns([2, 3])
with _search_col:
    _search_q = st.text_input("", placeholder="Ex : Lyon, Montpellier, Brest…",
                               label_visibility="collapsed")

if _search_q and len(_search_q.strip()) >= 2:
    _mask = _ca['nom_commune'].str.contains(_search_q.strip(), case=False, na=False)
    _found = _ca[_mask][['nom_commune','nom_departement','code_dept','nb_analyses','taux_conformite','tier']]\
               .sort_values('taux_conformite').head(25)
    if len(_found) > 0:
        st.dataframe(
            _found.rename(columns={
                'nom_commune':'Commune','nom_departement':'Département','code_dept':'Code',
                'nb_analyses':'Analyses','taux_conformite':'Conformité %','tier':'Niveau',
            }),
            use_container_width=True, hide_index=True,
            height=min(42*len(_found)+40, 340),
        )
    else:
        st.markdown('<p style="color:#2a5a8a;font-size:12px;font-style:italic;">Aucune commune trouvée.</p>',
                    unsafe_allow_html=True)
else:
    st.markdown(
        '<p style="color:#2a5a8a;font-size:11px;">Tapez au moins 2 caractères pour lancer la recherche.</p>',
        unsafe_allow_html=True,
    )

st.markdown('<hr style="margin:2rem 0;border-color:rgba(56,178,248,0.07);">', unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
# BLOC 4 — CLASSEMENT COMMUNES
# ═══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<span class="aq-tag">Classement — Communes (min. 200 analyses évaluées)</span>
<h2 class="aq-title">Meilleures et <span class="aq-title-amber">moins bonnes</span> performances.</h2>
<p class="aq-body">Seules les communes disposant d'au moins 200 analyses évaluées sont incluses
pour garantir la représentativité statistique du classement.</p>
""", unsafe_allow_html=True)

st.markdown('<div style="height:1rem;"></div>', unsafe_allow_html=True)
col_top, col_bot = st.columns(2, gap="large")

with col_top:
    st.markdown('<span class="rank-head-tag">Taux de conformité · Top 10</span>'
                '<span class="rank-head-val" style="color:#38b2f8;">En tête du classement</span>',
                unsafe_allow_html=True)
    if df_top is not None and len(df_top) > 0:
        st.markdown("".join(
            _ranking_row(i+1, r['nom_commune'], r.get('code_dept',''),
                         r.get('nom_departement',''), r.get('taux_conformite',100), True)
            for i, r in df_top.reset_index(drop=True).iterrows()
        ), unsafe_allow_html=True)

with col_bot:
    st.markdown('<span class="rank-head-tag">Taux de conformité · Bas du classement</span>'
                '<span class="rank-head-val" style="color:#e05c5c;">Points de vigilance</span>',
                unsafe_allow_html=True)
    if df_bottom is not None and len(df_bottom) > 0:
        st.markdown("".join(
            _ranking_row(i+1, r['nom_commune'], r.get('code_dept',''),
                         r.get('nom_departement',''), r.get('taux_conformite',0), False)
            for i, r in df_bottom.reset_index(drop=True).iterrows()
        ), unsafe_allow_html=True)

st.markdown('<hr style="margin:2rem 0;border-color:rgba(56,178,248,0.07);">', unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
# BLOC 5 — ANALYSES DÉTAILLÉES
# ═══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<span class="aq-tag">Analyses détaillées</span>
<h2 class="aq-title">Cadence et <span class="aq-title-accent">non-conformités.</span></h2>
""", unsafe_allow_html=True)

c1, c2 = st.columns(2, gap="large")

with c1:
    _tag_yr = f" · {selected_year}" if selected_year else ""
    st.markdown(f'<span class="aq-tag">Prélèvements par mois{_tag_yr}</span>', unsafe_allow_html=True)

    fig_t = go.Figure()
    fig_t.add_trace(go.Bar(
        x=df_temp['mois'], y=df_temp['nb_prelevements'],
        marker=dict(color=df_temp['nb_prelevements'].tolist(),
                    colorscale=[[0,'#1a3a7a'],[1,'#38b2f8']], showscale=False),
        hovertemplate='<b>%{x}</b> · %{y:,.0f} prélèvements<extra></extra>',
        name='Prélèvements',
    ))

    _has_trend = (df_trend is not None and len(df_trend) > 0
                  and 'taux_conformite' in df_trend.columns
                  and 'mois' in df_trend.columns)
    if _has_trend:
        fig_t.add_trace(go.Scatter(
            x=df_trend['mois'], y=df_trend['taux_conformite'],
            mode='lines+markers',
            line=dict(color='#e8b86d', width=2),
            marker=dict(color='#e8b86d', size=5, symbol='circle'),
            hovertemplate='<b>%{x}</b> · %{y:.2f} % conformité<extra></extra>',
            name='Conformité %',
            yaxis='y2',
        ))
        fig_t.update_layout(
            yaxis2=dict(
                overlaying='y', side='right',
                range=[97, 100.5], showgrid=False,
                tickfont=dict(color='#e8b86d', size=9, family='JetBrains Mono'),
                ticksuffix=' %',
            )
        )

    st.plotly_chart(styled(fig_t, 280), use_container_width=True)

with c2:
    st.markdown(f'<span class="aq-tag">Top {top_n} indicateurs non conformes</span>',
                unsafe_allow_html=True)
    df_p = df_params.head(top_n).sort_values('nb_nc')
    fig_p = go.Figure(go.Bar(
        x=df_p['nb_nc'], y=df_p['nom_parametre'], orientation='h',
        marker=dict(color=df_p['nb_nc'].tolist(),
                    colorscale=[[0,'#1a3a7a'],[0.5,'#c88520'],[1,'#c83030']], showscale=False),
        hovertemplate='<b>%{y}</b> · %{x:,.0f} NC<extra></extra>',
    ))
    st.plotly_chart(styled(fig_p, 280), use_container_width=True)

# ── Tableau + export CSV ────────────────────────────────────────────────────────
if df_depts is not None:
    df_d = df_depts.copy()
    if nc_only and 'nb_nc' in df_d.columns:
        df_d = df_d[df_d['nb_nc'] > 0]
    cols_show = [c for c in ['nom_departement','code_dept','nb_analyses','nb_nc','taux_conformite']
                 if c in df_d.columns]
    export_df = df_d[cols_show].rename(columns={
        'nom_departement':'Département','code_dept':'Code',
        'nb_analyses':'Analyses','nb_nc':'Non-conformes','taux_conformite':'Conformité %',
    })

    col_tbl_title, col_tbl_dl = st.columns([5, 1])
    with col_tbl_title:
        st.markdown('<span class="aq-tag" style="display:block;margin-bottom:8px;">Données par département</span>',
                    unsafe_allow_html=True)
    with col_tbl_dl:
        st.download_button(
            "⬇ CSV",
            data=export_df.to_csv(index=False).encode('utf-8'),
            file_name="aquastat_departements.csv",
            mime="text/csv",
        )

    st.dataframe(export_df, use_container_width=True, hide_index=True, height=320)

# ── Méthodologie ────────────────────────────────────────────────────────────────
with st.expander("Méthodologie & sources de données"):
    st.markdown("""
**Calcul du taux de conformité**

Le taux est calculé uniquement sur les analyses dont le résultat est évalué (Conforme ou Non conforme).
Les analyses catégorisées *Non évalué* (environ 18 % du total) sont exclues du dénominateur.

**Formule :**
```
Taux = Σ(Conforme) / Σ(Conforme + Non conforme) × 100
```

**Sources :**
- Données brutes : data.gouv.fr — Résultats du contrôle sanitaire de l'eau potable en France
- Pipeline ETL : Databricks Unity Catalog (tables bronze → silver → gold)
- Géofrontières : gregoiredavid/france-geojson (INSEE 2024)

**Interprétation :**
Un taux de 99,72 % signifie que sur 100 analyses évaluées, 99,72 sont conformes aux seuils réglementaires.
Un résultat *Non conforme* ne signifie pas que l'eau est dangereuse — les seuils européens sont volontairement prudents.
""")

# ═══════════════════════════════════════════════════════════════════════════════
# PIED DE PAGE
# ═══════════════════════════════════════════════════════════════════════════════
st.markdown('<hr style="margin:2.5rem 0 1rem;border-color:rgba(56,178,248,0.07);">', unsafe_allow_html=True)
_footer_update = f" · Données au {_last_update_str}" if _last_update_str else ""
st.markdown(f"""
<div style="display:flex;justify-content:space-between;align-items:flex-end;padding-bottom:2rem;">
  <div>
    <span style="font-family:'Space Grotesk',sans-serif;font-size:1.1rem;
                 font-weight:700;color:#d4e4f0;">AquaStat</span>
    <p style="font-family:'JetBrains Mono',monospace;font-size:9px;letter-spacing:0.15em;
              text-transform:uppercase;color:#2a5a8a;margin:6px 0 0;line-height:1.8;">
      Source · data.gouv.fr / ARS — Contrôle sanitaire{_footer_update}<br>
      Pipeline · Databricks Unity Catalog · water-quality-pipeline
    </p>
  </div>
  <div style="text-align:right;font-family:'JetBrains Mono',monospace;font-size:9px;
              letter-spacing:0.12em;text-transform:uppercase;color:#2a5a8a;line-height:1.8;">
    Mariam Douamba<br>Simplon.co · 2026
  </div>
</div>
""", unsafe_allow_html=True)
