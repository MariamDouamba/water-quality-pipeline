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
.stApp                          { background: #050f0f; }
[data-testid="stSidebar"]       { background: #040c0c !important;
                                  border-right: 1px solid rgba(0,207,180,0.08); }
h1,h2,h3,h4 { font-family: 'Space Grotesk', sans-serif !important;
               color: #d4e8e5 !important; font-weight: 600 !important; }

[data-testid="metric-container"]  { background: transparent; border: none; padding: 0 !important; }
[data-testid="metric-container"] label
  { color: #4a9990 !important; font-size: 9px !important;
    letter-spacing: 0.22em; text-transform: uppercase;
    font-family: 'JetBrains Mono', monospace !important; }
[data-testid="metric-container"] [data-testid="stMetricValue"]
  { color: #00cfb4 !important; font-family: 'JetBrains Mono', monospace !important;
    font-size: 2rem !important; font-weight: 600 !important; }
[data-testid="metric-container"] [data-testid="stMetricDelta"] { color: #4fbf8e !important; }

.stSelectbox label, .stSlider label
  { color: #4a9990 !important; font-size: 9px !important;
    letter-spacing: 0.15em; text-transform: uppercase; }
hr { border-color: rgba(0,207,180,0.07) !important; }

.aq-tag   { font-family:'JetBrains Mono',monospace; font-size:9px; letter-spacing:0.18em;
            text-transform:uppercase; color:#4a9990; margin-bottom:6px; display:block; }
.aq-title { font-family:'Space Grotesk',sans-serif; font-size:2rem; font-weight:700;
            color:#d4e8e5; margin:0 0 6px; line-height:1.1; }
.aq-title-accent { color:#00cfb4; }
.aq-title-amber  { color:#e8b86d; }
.aq-body  { color:#4d7a75; font-size:13px; line-height:1.7; max-width:420px; margin-top:8px; }

.kpi-block { padding:0; }
.kpi-val   { font-family:'JetBrains Mono',monospace; font-size:2.4rem;
             font-weight:600; color:#00cfb4; line-height:1; }
.kpi-val-alert { color:#e05c5c !important; }
.kpi-label { font-family:'JetBrains Mono',monospace; font-size:9px; letter-spacing:0.2em;
             text-transform:uppercase; color:#4a9990; margin-top:5px; }

.tier-row { display:flex; align-items:center; gap:10px; padding:7px 0;
            border-bottom:1px solid rgba(0,207,180,0.06); }
.tier-dot { width:14px; height:14px; border-radius:3px; flex-shrink:0; }
.tier-lbl { font-size:12px; color:#8ecec8; flex:1; font-weight:500; }
.tier-rng { font-family:'JetBrains Mono',monospace; font-size:10px; color:#4a9990; }
.tier-cnt { font-family:'JetBrains Mono',monospace; font-size:10px;
            color:#00cfb4; width:60px; text-align:right; }

/* Panneau de détail département */
.dept-panel { background:#0a1a1a; border:1px solid rgba(0,207,180,0.1);
              border-radius:12px; padding:1.2rem; height:100%; }
.dept-name  { font-family:'Space Grotesk',sans-serif; font-size:1.5rem; font-weight:700;
              color:#d4e8e5; margin:6px 0 4px; line-height:1.1; }
.dept-tier  { font-family:'JetBrains Mono',monospace; font-size:9px; letter-spacing:0.15em;
              text-transform:uppercase; padding:2px 8px; border-radius:3px; display:inline-block; }
.dept-tc    { font-family:'JetBrains Mono',monospace; font-size:2rem; font-weight:600;
              color:#00cfb4; margin:10px 0 0; line-height:1; }
.dept-stat-row { display:flex; gap:16px; margin-top:10px; padding-top:10px;
                 border-top:1px solid rgba(0,207,180,0.06); }
.dept-stat     { flex:1; }
.dept-stat-val { font-family:'JetBrains Mono',monospace; font-size:1.1rem; font-weight:600;
                 color:#d4e8e5; }
.dept-stat-lbl { font-family:'JetBrains Mono',monospace; font-size:8px; letter-spacing:0.15em;
                 text-transform:uppercase; color:#4a9990; margin-top:2px; }
.dept-section  { margin-top:14px; padding-top:10px; border-top:1px solid rgba(0,207,180,0.06); }
.dept-section-title { font-family:'JetBrains Mono',monospace; font-size:8px; letter-spacing:0.18em;
                      text-transform:uppercase; color:#4a9990; margin-bottom:8px; display:block; }
.dept-param-row { display:flex; justify-content:space-between; padding:5px 0;
                  border-bottom:1px solid rgba(0,207,180,0.04); }
.dept-param-name { font-size:11px; color:#8ecec8; }
.dept-param-nc   { font-family:'JetBrains Mono',monospace; font-size:11px; color:#e05c5c; }
.dept-commune-row { display:flex; align-items:center; gap:8px; padding:5px 0;
                    border-bottom:1px solid rgba(0,207,180,0.04); }
.dept-commune-name { font-size:11px; color:#8ecec8; flex:1; }
.dept-commune-pct  { font-family:'JetBrains Mono',monospace; font-size:11px; color:#e8b86d; }
.dept-empty { color:#3a7070; font-size:12px; font-style:italic; text-align:center;
              padding:2rem 0.5rem; line-height:1.6; }

.pcard { background:#0d1f1f; border:1px solid rgba(0,207,180,0.08);
         border-radius:10px; padding:1.1rem; min-height:128px; }
.pcard-code { font-family:'JetBrains Mono',monospace; font-size:9px; letter-spacing:0.18em;
              text-transform:uppercase; color:#4a9990; margin-bottom:8px; }
.pcard-name { font-family:'Space Grotesk',sans-serif; font-size:1rem; font-weight:600;
              color:#d4e8e5; margin-bottom:6px; }
.pcard-desc { font-size:11px; color:#4d7a75; line-height:1.55; }

.rank-head-tag { font-family:'JetBrains Mono',monospace; font-size:9px; letter-spacing:0.2em;
                 text-transform:uppercase; color:#4a9990; margin-bottom:8px; display:block; }
.rank-head-val { font-family:'Space Grotesk',sans-serif; font-size:1.3rem; font-weight:700;
                 color:#d4e8e5; margin-bottom:14px; display:block; }
.rrow { display:flex; align-items:center; padding:8px 0;
        border-bottom:1px solid rgba(0,207,180,0.05); gap:10px; }
.rrow-num  { font-family:'JetBrains Mono',monospace; font-size:10px;
             color:#3a7070; width:22px; flex-shrink:0; }
.rrow-info { flex:1; min-width:0; }
.rrow-name { font-family:'Space Grotesk',sans-serif; font-size:13px; font-weight:600;
             color:#b8d4d1; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }
.rrow-dept { font-family:'JetBrains Mono',monospace; font-size:9px; letter-spacing:0.1em;
             text-transform:uppercase; color:#3a7070; margin-top:2px; }
.rrow-bar-bg { width:64px; height:3px; background:rgba(0,207,180,0.08); border-radius:2px; }
.rrow-bar    { height:3px; border-radius:2px; }
.rrow-pct    { font-family:'JetBrains Mono',monospace; font-size:11px;
               width:46px; text-align:right; flex-shrink:0; }

.aq-note { font-size:11px; color:#4d7a75; line-height:1.6; padding:0.8rem 0;
           border-top:1px solid rgba(0,207,180,0.06); }

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
    font=dict(family='DM Sans', color='#4d7a75', size=11),
    margin=dict(t=30, b=40, l=50, r=20),
)
_AXIS = dict(
    gridcolor='rgba(0,207,180,0.05)', linecolor='rgba(0,207,180,0.08)',
    tickfont=dict(color='#4a9990', size=10, family='JetBrains Mono'),
    zerolinecolor='rgba(0,207,180,0.05)',
)

def styled(fig, h=340):
    fig.update_layout(**_LAYOUT, height=h)
    fig.update_xaxes(**_AXIS)
    fig.update_yaxes(**_AXIS)
    return fig

# ── Tiers ──────────────────────────────────────────────────────────────────────
TIER_ORDER  = ["Optimal (≥ 95 %)", "Satisfaisant (88–95 %)", "Insuffisant (80–88 %)", "Critique (< 80 %)"]
TIER_COLORS = {"Optimal (≥ 95 %)":"#00917a","Satisfaisant (88–95 %)":"#1e7ab0",
               "Insuffisant (80–88 %)":"#c88520","Critique (< 80 %)":"#c83030"}
TIER_HEX    = ["#00917a","#1e7ab0","#c88520","#c83030"]
TIER_BORDER = ["#00cfb4","#4ab0e8","#e8b86d","#e05c5c"]
TIER_BG     = ["rgba(0,145,122,0.15)","rgba(30,122,176,0.15)",
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
    """Charge les indicateurs détaillés d'un département au clic sur la carte."""
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
        'taux_conformite':[100.0]*10,
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

# ── Chargement principal ───────────────────────────────────────────────────────
@st.cache_data(ttl=3600, show_spinner=False)
def get_all_data():
    source = "simulation"

    # KPIs — taux calculé uniquement sur les analyses évaluées (exclut 'Non évalué')
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

    df_temp, _ = load_db("""
        SELECT DATE_FORMAT(date_prelevement,'MMM') AS mois,
               MONTH(date_prelevement) AS mois_num,
               COUNT(*) AS nb_prelevements
        FROM gold_dim_prelevement
        WHERE date_prelevement IS NOT NULL
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

# ── Répertoire des indicateurs ─────────────────────────────────────────────────
INDICATORS = [
    {"code":"pH",   "name":"Potentiel hydrogène",
     "desc":"Acidité de l'eau. Hors de la plage 6,5–9, le réseau se corrode et des irritations apparaissent."},
    {"code":"NTU",  "name":"Turbidité",
     "desc":"Matières en suspension. Une eau trouble peut masquer des micro-organismes et réduire l'efficacité de la désinfection."},
    {"code":"µS/cm","name":"Conductivité",
     "desc":"Concentration en sels minéraux dissous. Toute variation soudaine signale un changement de source ou une intrusion."},
    {"code":"UFC",  "name":"E. coli",
     "desc":"Indicateur de contamination fécale récente. Sa détection déclenche une alerte sanitaire immédiate."},
    {"code":"UFC",  "name":"Entérocoques",
     "desc":"Indicateur fécal plus résistant que E. coli. Utile pour détecter les contaminations anciennes dans le réseau."},
    {"code":"UFC",  "name":"Bactéries coliformes",
     "desc":"Famille bactérienne large. Un excès révèle un défaut de désinfection ou une intrusion d'eau extérieure."},
    {"code":"mg/L", "name":"Ammonium (NH₄⁺)",
     "desc":"Traceur de pollution azotée agricole ou industrielle, précurseur de la formation de nitrites en réseau."},
    {"code":"UFC",  "name":"Bactéries aérobies",
     "desc":"Flore bactérienne globale à 22 °C. Un pic trahit une stagnation prolongée ou un biofilm dans la canalisation."},
    {"code":"seuil","name":"Odeur et saveur",
     "desc":"Tests organoleptiques réglementés. Une anomalie persistante indique un sous-dosage ou une contamination chimique."},
]

# ── Constructeurs HTML ──────────────────────────────────────────────────────────
def _indicator_card(info):
    return f"""<div class="pcard">
  <div class="pcard-code">{info['code']}</div>
  <div class="pcard-name">{info['name']}</div>
  <div class="pcard-desc">{info['desc']}</div>
</div>"""

def _ranking_row(rank, nom, code, dept, pct, good):
    bar_color = "#00cfb4" if good else "#e05c5c"
    pct_color = "#00cfb4" if good else "#e05c5c"
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
    """Génère le HTML du panneau de détail département."""
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
        params_html = '<p style="color:#3a7070;font-size:11px;font-style:italic;">Aucune non-conformité détectée</p>'

    communes_html = ""
    if df_c is not None and len(df_c) > 0:
        for _, row in df_c.iterrows():
            communes_html += f"""<div class="dept-commune-row">
  <span class="dept-commune-name">{row['nom_commune']}</span>
  <span class="dept-commune-pct">{float(row['taux_conformite']):.1f} %</span>
</div>"""
    else:
        communes_html = '<p style="color:#3a7070;font-size:11px;font-style:italic;">Données insuffisantes</p>'

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

# ── SIDEBAR ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 💧 AquaStat")
    st.divider()
    st.caption("Contrôle sanitaire 2024 · data.gouv.fr")
    top_n   = st.slider("Indicateurs à afficher", 5, 20, 12)
    nc_only = st.checkbox("Départements avec NC uniquement", value=False)
    st.divider()
    st.markdown(f"[API REST]({_api_url()}/docs) · [GitHub](https://github.com/MariamDouamba/water-quality-pipeline)")

# ── CHARGEMENT ─────────────────────────────────────────────────────────────────
with st.spinner("Chargement…"):
    df_kpis, df_temp, df_params, df_depts, df_top, df_bottom, source = get_all_data()
    geojson = load_france_geojson()

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

nb_prelevements = int(df_temp['nb_prelevements'].sum()) if is_live else 291_604
top_param = df_params.iloc[0]['nom_parametre'] if df_params is not None and len(df_params) > 0 else "Turbidité"
top_param_nc = int(df_params.iloc[0]['nb_nc']) if df_params is not None and len(df_params) > 0 else 4820

# ═══════════════════════════════════════════════════════════════════════════════
# BLOC 1 — EN-TÊTE
# ═══════════════════════════════════════════════════════════════════════════════
badge = ('<span class="badge-live">LIVE · Databricks</span>'
         if is_live else '<span class="badge-demo">DÉMO · Données simulées</span>')

st.markdown(f"""
<div style="padding:2rem 0 0.5rem;">
  <div style="display:flex;align-items:center;gap:12px;margin-bottom:1rem;">
    <span style="font-family:'JetBrains Mono',monospace;font-size:9px;
                 letter-spacing:0.22em;text-transform:uppercase;color:#4a9990;">
      AQUASTAT — OBSERVATOIRE DE LA QUALITÉ DE L'EAU EN FRANCE · 2024
    </span>
    {badge}
  </div>
  <h1 style="font-family:'Space Grotesk',sans-serif;font-size:2.8rem;
             font-weight:700;color:#d4e8e5;margin:0;line-height:1.05;">
    Chaque goutte <span style="color:#00cfb4;">analysée.</span>
  </h1>
  <p style="color:#4d7a75;font-size:13px;line-height:1.75;max-width:560px;margin:12px 0 0;">
    AquaStat agrège les résultats du contrôle sanitaire officiel de l'eau potable distribué
    aux robinets français. Données brutes data.gouv.fr, transformées par le pipeline Databricks.
  </p>
</div>
""", unsafe_allow_html=True)

# ── 6 KPIs live ────────────────────────────────────────────────────────────────
def _kpi(col, val, lbl, alert=False):
    cls = "kpi-val kpi-val-alert" if alert else "kpi-val"
    col.markdown(f"""<div class="kpi-block">
  <div class="{cls}">{val}</div>
  <div class="kpi-label">{lbl}</div>
</div>""", unsafe_allow_html=True)

k1,k2,k3,k4,k5,k6 = st.columns(6)
_kpi(k1, f"{total/1_000_000:.1f}M",          "Analyses totales")
_kpi(k2, f"{nb_prelevements:,}",              "Prélèvements")
_kpi(k3, f"{nb_communes:,}",                  "Communes")
_kpi(k4, f"{total_nc:,}",                     "Non-conformités", alert=True)
_kpi(k5, f"{taux:.2f} %",                     "Taux conformité")
_kpi(k6, top_param,                           f"Paramètre prioritaire · {top_param_nc:,} NC")

st.markdown('<hr style="margin:2rem 0;border-color:rgba(0,207,180,0.07);">', unsafe_allow_html=True)

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
        df_t  = df_depts.copy()
        df_t['tier'] = df_t['taux_conformite'].apply(conformite_tier)
        cnt   = df_t['tier'].value_counts()
        ranges = ["≥ 95 %","88–95 %","80–88 %","< 80 %"]
        st.markdown('<div style="margin-top:1rem;">', unsafe_allow_html=True)
        for tier, color, border, rng in zip(TIER_ORDER, TIER_HEX, TIER_BORDER, ranges):
            lbl = tier.split(" (")[0]
            n   = cnt.get(tier, 0)
            st.markdown(f"""<div class="tier-row">
  <div class="tier-dot" style="background:{color};box-shadow:0 0 0 1px {border}33;"></div>
  <span class="tier-lbl">{lbl}</span>
  <span class="tier-rng">{rng}</span>
  <span class="tier-cnt">{n} dép.</span>
</div>""", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # Jauge
    fig_gauge = go.Figure(go.Indicator(
        mode="gauge+number",
        value=taux,
        number={'suffix':' %','font':{'size':24,'color':'#00cfb4','family':'JetBrains Mono'}},
        title={'text':"Taux national 2024",'font':{'color':'#4a9990','size':10,'family':'JetBrains Mono'}},
        gauge={
            'axis':{'range':[95,100],'tickfont':{'color':'#4a9990','size':9,'family':'JetBrains Mono'}},
            'bar':{'color':'#00cfb4','thickness':0.22},
            'steps':[
                {'range':[95.0,97.5],'color':'rgba(200,133,32,0.20)'},
                {'range':[97.5,99.0],'color':'rgba(0,145,122,0.15)'},
                {'range':[99.0,100], 'color':'rgba(0,207,180,0.12)'},
            ],
            'threshold':{'line':{'color':'#e8b86d','width':2},'thickness':0.8,'value':99},
        }
    ))
    fig_gauge.update_layout(
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#4d7a75'), height=200,
        margin=dict(t=40, b=10, l=20, r=20)
    )
    st.plotly_chart(fig_gauge, use_container_width=True)

# ── Carte cliquable ─────────────────────────────────────────────────────────────
with col_map_c:
    selected_code = None  # code_geo du département cliqué

    if geojson and df_depts is not None and 'taux_conformite' in df_depts.columns:
        df_map = df_depts.copy()
        df_map['code_geo']        = df_map['code_dept'].apply(normalize_dept_code)
        df_map['taux_conformite'] = pd.to_numeric(df_map['taux_conformite'], errors='coerce')

        tc_vals  = df_map['taux_conformite'].dropna()
        range_low = min(float(tc_vals.min()) - 3.0, 90.0)

        fig_map = px.choropleth(
            df_map,
            geojson=geojson,
            locations='code_geo',
            featureidkey='properties.code',
            color='taux_conformite',
            color_continuous_scale=[
                [0.00,"#c83030"],[0.30,"#c88520"],
                [0.55,"#1e7ab0"],[1.00,"#00cfb4"],
            ],
            range_color=[range_low, 100.0],
            hover_name='nom_departement',
            hover_data={'taux_conformite':':.2f','nb_analyses':':,','code_geo':False},
            labels={'taux_conformite':'Conformité %','nb_analyses':'Analyses'},
        )
        fig_map.update_geos(fitbounds="locations", visible=False)
        fig_map.update_traces(marker_line_color='rgba(5,15,15,0.7)', marker_line_width=0.4)
        fig_map.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            geo=dict(bgcolor='rgba(0,0,0,0)'),
            coloraxis_colorbar=dict(
                title=dict(text="Conformité %",
                           font=dict(color='#4a9990',size=10,family='JetBrains Mono')),
                tickfont=dict(color='#4a9990',size=9,family='JetBrains Mono'),
                thickness=10, len=0.55, x=1.01,
            ),
            margin=dict(t=10,b=10,l=0,r=0),
            height=430,
        )

        # ← Clic sur la carte
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
            # Utilise le code_dept original (non normalisé) pour la requête SQL
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

st.markdown('<hr style="margin:2rem 0;border-color:rgba(0,207,180,0.07);">', unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
# BLOC 3 — INDICATEURS RÉGLEMENTAIRES
# ═══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<span class="aq-tag">Référentiel technique</span>
<h2 class="aq-title">9 indicateurs <span class="aq-title-amber">réglementaires.</span></h2>
<p class="aq-body">Le contrôle sanitaire de l'eau repose sur neuf mesures obligatoires,
chacune ciblant un risque sanitaire précis défini par la directive européenne sur l'eau potable.</p>
""", unsafe_allow_html=True)

for row_start in range(0, 9, 3):
    cols = st.columns(3, gap="small")
    for j, col in enumerate(cols):
        idx = row_start + j
        if idx < len(INDICATORS):
            with col:
                st.markdown(_indicator_card(INDICATORS[idx]), unsafe_allow_html=True)
    st.markdown('<div style="height:8px;"></div>', unsafe_allow_html=True)

st.markdown('<hr style="margin:2rem 0;border-color:rgba(0,207,180,0.07);">', unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
# BLOC 4 — CLASSEMENT COMMUNES
# ═══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<span class="aq-tag">Classement 2024 — Communes (min. 200 analyses évaluées)</span>
<h2 class="aq-title">Meilleures et <span class="aq-title-amber">moins bonnes</span> performances.</h2>
<p class="aq-body">Seules les communes disposant d'au moins 200 analyses évaluées sont incluses
pour garantir la représentativité statistique du classement.</p>
""", unsafe_allow_html=True)

st.markdown('<div style="height:1rem;"></div>', unsafe_allow_html=True)
col_top, col_bot = st.columns(2, gap="large")

with col_top:
    st.markdown('<span class="rank-head-tag">Taux de conformité · Top 10</span>'
                '<span class="rank-head-val" style="color:#00cfb4;">En tête du classement</span>',
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

st.markdown('<hr style="margin:2rem 0;border-color:rgba(0,207,180,0.07);">', unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
# BLOC 5 — ANALYSES DÉTAILLÉES
# ═══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<span class="aq-tag">Analyses détaillées</span>
<h2 class="aq-title">Cadence et <span class="aq-title-accent">non-conformités.</span></h2>
""", unsafe_allow_html=True)

c1, c2 = st.columns(2, gap="large")

with c1:
    st.markdown('<span class="aq-tag">Prélèvements par mois</span>', unsafe_allow_html=True)
    fig_t = go.Figure(go.Bar(
        x=df_temp['mois'], y=df_temp['nb_prelevements'],
        marker=dict(color=df_temp['nb_prelevements'].tolist(),
                    colorscale=[[0,'#1a6b5e'],[1,'#00cfb4']], showscale=False),
        hovertemplate='<b>%{x}</b> · %{y:,.0f} prélèvements<extra></extra>',
    ))
    st.plotly_chart(styled(fig_t, 280), use_container_width=True)

with c2:
    st.markdown(f'<span class="aq-tag">Top {top_n} indicateurs non conformes</span>',
                unsafe_allow_html=True)
    df_p = df_params.head(top_n).sort_values('nb_nc')
    fig_p = go.Figure(go.Bar(
        x=df_p['nb_nc'], y=df_p['nom_parametre'], orientation='h',
        marker=dict(color=df_p['nb_nc'].tolist(),
                    colorscale=[[0,'#1a6b5e'],[0.5,'#c88520'],[1,'#c83030']], showscale=False),
        hovertemplate='<b>%{y}</b> · %{x:,.0f} NC<extra></extra>',
    ))
    st.plotly_chart(styled(fig_p, 280), use_container_width=True)

if df_depts is not None:
    st.markdown('<span class="aq-tag" style="display:block;margin-bottom:8px;">Données par département</span>',
                unsafe_allow_html=True)
    df_d = df_depts.copy()
    if nc_only and 'nb_nc' in df_d.columns:
        df_d = df_d[df_d['nb_nc'] > 0]
    cols_show = [c for c in ['nom_departement','code_dept','nb_analyses','nb_nc','taux_conformite']
                 if c in df_d.columns]
    st.dataframe(
        df_d[cols_show].rename(columns={
            'nom_departement':'Département','code_dept':'Code',
            'nb_analyses':'Analyses','nb_nc':'Non-conformes','taux_conformite':'Conformité %',
        }),
        use_container_width=True, hide_index=True, height=320,
    )

# ═══════════════════════════════════════════════════════════════════════════════
# PIED DE PAGE
# ═══════════════════════════════════════════════════════════════════════════════
st.markdown('<hr style="margin:2.5rem 0 1rem;border-color:rgba(0,207,180,0.07);">', unsafe_allow_html=True)
st.markdown(f"""
<div style="display:flex;justify-content:space-between;align-items:flex-end;padding-bottom:2rem;">
  <div>
    <span style="font-family:'Space Grotesk',sans-serif;font-size:1.1rem;
                 font-weight:700;color:#d4e8e5;">AquaStat</span>
    <p style="font-family:'JetBrains Mono',monospace;font-size:9px;letter-spacing:0.15em;
              text-transform:uppercase;color:#3a7070;margin:6px 0 0;line-height:1.8;">
      Source · data.gouv.fr / ARS — Contrôle sanitaire 2024<br>
      Pipeline · Databricks Unity Catalog · water-quality-pipeline
    </p>
  </div>
  <div style="text-align:right;font-family:'JetBrains Mono',monospace;font-size:9px;
              letter-spacing:0.12em;text-transform:uppercase;color:#3a7070;line-height:1.8;">
    Mariam Douamba<br>Simplon.co · 2026
  </div>
</div>
""", unsafe_allow_html=True)
