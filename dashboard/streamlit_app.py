"""
AquaStat — Dashboard Analytics Streamlit
Connecté à Databricks SQL Warehouse (water_quality.gold)
Fallback données simulées si pas de connexion
"""
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import os
from datetime import datetime

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="AquaStat — Qualité de l'eau en France",
    page_icon="💧",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;700;800&family=DM+Sans:wght@300;400;500&display=swap');

/* Global */
html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }

/* Background */
.stApp { background: #050d18; }
[data-testid="stSidebar"] { background: #0a1628 !important; border-right: 1px solid rgba(0,180,255,0.12); }

/* Titles */
h1 { font-family: 'Syne', sans-serif !important; font-weight: 800 !important;
     background: linear-gradient(90deg, #00b4ff, #00e5ff);
     -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
h2, h3 { font-family: 'Syne', sans-serif !important; color: #e8f4fd !important; }

/* Metrics */
[data-testid="metric-container"] {
  background: #111d32;
  border: 1px solid rgba(0,180,255,0.15);
  border-radius: 12px;
  padding: 1rem !important;
}
[data-testid="metric-container"] label { color: #3d6080 !important; font-size: 11px !important; letter-spacing: 0.08em; text-transform: uppercase; }
[data-testid="metric-container"] [data-testid="stMetricValue"] { color: #00b4ff !important; font-family: 'Syne', sans-serif !important; font-weight: 800 !important; }
[data-testid="metric-container"] [data-testid="stMetricDelta"] { color: #00e676 !important; }

/* Selectbox / sliders */
.stSelectbox label, .stSlider label, .stMultiSelect label { color: #7fa8c9 !important; font-size: 12px !important; }

/* Divider */
hr { border-color: rgba(0,180,255,0.12) !important; }

/* Plotly charts background */
.js-plotly-plot .plotly { background: transparent !important; }

/* Sidebar title */
.sidebar-title {
  font-family: 'Syne', sans-serif;
  font-size: 1.1rem;
  font-weight: 800;
  color: #e8f4fd;
  margin-bottom: 0.5rem;
  display: flex;
  align-items: center;
  gap: 8px;
}

.badge {
  display: inline-block;
  background: rgba(0,180,255,0.1);
  border: 1px solid rgba(0,180,255,0.2);
  border-radius: 100px;
  padding: 2px 10px;
  font-size: 10px;
  color: #00b4ff;
  font-family: 'Syne', sans-serif;
  font-weight: 600;
}
</style>
""", unsafe_allow_html=True)

# ── Plotly dark theme ──────────────────────────────────────────────────────────
THEME = dict(
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
    font=dict(family='DM Sans', color='#7fa8c9', size=11),
    margin=dict(t=30, b=40, l=50, r=20),
    colorway=['#00b4ff','#00e5ff','#ffc107','#00e676','#ff5252','#bb86fc','#ff7043'],
)

AXIS = dict(
    gridcolor='rgba(0,180,255,0.08)',
    linecolor='rgba(0,180,255,0.15)',
    tickfont=dict(color='#3d6080', size=10),
    zerolinecolor='rgba(0,180,255,0.08)',
)

def styled_chart(fig, height=350):
    fig.update_layout(**THEME, height=height)
    fig.update_xaxes(**AXIS)
    fig.update_yaxes(**AXIS)
    return fig

# ── Data connection ────────────────────────────────────────────────────────────
def _get_databricks_creds():
    """Récupère les credentials depuis st.secrets ou variables d'env"""
    # 1. Streamlit Cloud secrets (priorité absolue)
    try:
        if "databricks" in st.secrets:
            host      = st.secrets["databricks"]["host"]
            http_path = st.secrets["databricks"]["http_path"]
            token     = st.secrets["databricks"]["token"]
            print(f"[CREDS] Source=st.secrets, host={host}, token={'OK' if token else 'VIDE'}")
            if token:
                return host, http_path, token
        else:
            print(f"[CREDS] st.secrets existe mais pas de clé 'databricks'. Clés disponibles : {list(st.secrets.keys())}")
    except Exception as e:
        print(f"[CREDS] st.secrets inaccessible : {e}")
    # 2. Variables d'environnement
    host      = os.getenv("DATABRICKS_HOST", "")
    http_path = os.getenv("DATABRICKS_HTTP_PATH", "")
    token     = os.getenv("DATABRICKS_TOKEN", "")
    print(f"[CREDS] Source=env, host={'OK' if host else 'VIDE'}, token={'OK' if token else 'VIDE'}")
    return host, http_path, token

@st.cache_data(ttl=3600, show_spinner=False)
def load_databricks(query):
    """Charge depuis Databricks SQL Warehouse — fallback immédiat si pas de creds"""
    host, http_path, token = _get_databricks_creds()
    if not token:
        return None, "no_credentials"
    try:
        from databricks import sql
        with sql.connect(
            server_hostname=host,
            http_path=http_path,
            access_token=token,
        ) as conn:
            with conn.cursor() as cursor:
                cursor.execute(query)
                cols = [d[0] for d in cursor.description]
                rows = cursor.fetchall()
                df = pd.DataFrame(rows, columns=cols)
        return df, "databricks"
    except Exception as e:
        print(f"[DATABRICKS ERROR] {type(e).__name__}: {e}")
        return None, str(e)

# ── Fallback data generators ───────────────────────────────────────────────────
def gen_temporal():
    mois = ['Jan','Fév','Mar','Avr','Mai','Jun','Jul','Aoû','Sep','Oct','Nov','Déc']
    counts = [24200,22800,26100,25400,27300,28900,31200,29800,26700,25100,23400,21700]
    return pd.DataFrame({'mois': mois, 'nb_prelevements': counts})

def gen_params_nc():
    params = ['Turbidité','Bactéries E.coli','Nitrates','Chlore libre','pH',
              'Fluor','Pesticides','Arsenic','Plomb','Entérocoques',
              'Aluminium','Manganèse','Fer','Nitrites','Ammonium']
    counts = [4820,3940,3210,2870,2430,2180,1950,1720,1540,1380,1240,1120,980,870,760]
    return pd.DataFrame({'nom_parametre': params, 'nb_nc': counts})

def gen_communes_nc():
    communes = [f"Commune_{i+1}" for i in range(30)]
    depts = [str(np.random.randint(1,96)).zfill(2) for _ in range(30)]
    counts = sorted([np.random.randint(200, 1300) for _ in range(30)], reverse=True)
    return pd.DataFrame({'nom_commune': communes, 'code_dept': depts, 'nb_nc': counts})

def gen_depts():
    depts = ['Bouches-du-Rhône','Rhône','Gironde','Nord','Haute-Garonne',
             'Loire-Atlantique','Bas-Rhin','Alpes-Maritimes','Hérault',
             'Ille-et-Vilaine','Isère','Var','Marne','Loire','Seine-Maritime',
             "Côte-d'Or",'Gard','Finistère','Haute-Vienne','Paris',
             'Hauts-de-Seine','Seine-Saint-Denis','Val-de-Marne','Yvelines',
             'Essonne','Val-d\'Oise','Seine-et-Marne','Sarthe','Moselle','Haut-Rhin']
    codes = ['13','69','33','59','31','44','67','06','34','35','38','83',
             '51','42','76','21','30','29','87','75','92','93','94','78',
             '91','95','77','72','57','68']
    nb_analyses = sorted([np.random.randint(50000, 500000) for _ in range(30)], reverse=True)
    nb_nc       = [int(n * np.random.uniform(0.03, 0.09)) for n in nb_analyses]
    return pd.DataFrame({'nom_departement': depts, 'code_dept': codes,
                          'nb_analyses': nb_analyses, 'nb_nc': nb_nc})

def gen_boxplot(param):
    np.random.seed(hash(param) % 2**31)
    vals = np.random.normal(loc=5, scale=2, size=500)
    vals = np.clip(vals, 0, None)
    return vals

# ── Load data (Databricks ou fallback) ────────────────────────────────────────
@st.cache_data(ttl=3600, show_spinner=False)
def get_all_data():
    source = "simulation"

    # Temporal
    df_temp, err = load_databricks("""
        SELECT DATE_FORMAT(date_prelevement, 'MMM') AS mois,
               MONTH(date_prelevement) AS mois_num,
               COUNT(*) AS nb_prelevements
        FROM gold_dim_prelevement
        WHERE date_prelevement IS NOT NULL
        GROUP BY 1, 2 ORDER BY 2
    """)
    if df_temp is None:
        df_temp = gen_temporal()
    else:
        source = "databricks"

    # Params NC
    df_params, _ = load_databricks("""
        SELECT p.libelle_parametre AS nom_parametre, COUNT(*) AS nb_nc
        FROM gold_fact_analyses f
        JOIN gold_dim_parametre p ON f.parametre_code = p.cdparametresiseeaux
        WHERE f.est_conforme = 'Non conforme'
        GROUP BY p.libelle_parametre ORDER BY nb_nc DESC LIMIT 20
    """)
    if df_params is None:
        df_params = gen_params_nc()

    # Communes NC
    df_communes, _ = load_databricks("""
        SELECT commune AS nom_commune, departement_code AS code_dept,
               COUNT(*) AS nb_nc
        FROM gold_fact_analyses
        WHERE est_conforme = 'Non conforme' AND commune IS NOT NULL
        GROUP BY commune, departement_code ORDER BY nb_nc DESC LIMIT 30
    """)
    if df_communes is None:
        df_communes = gen_communes_nc()

    # Depts
    df_depts, _ = load_databricks("""
        SELECT nom_departement, code_departement AS code_dept,
               nb_analyses, nb_non_conformes AS nb_nc, taux_conformite
        FROM gold_dim_departement
        ORDER BY nb_analyses DESC LIMIT 50
    """)
    if df_depts is None:
        df_depts = gen_depts()

    return df_temp, df_params, df_communes, df_depts, source

# ── SIDEBAR ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div class="sidebar-title">💧 AquaStat</div>', unsafe_allow_html=True)
    st.markdown('<span class="badge">v1.0.0</span>', unsafe_allow_html=True)
    st.markdown("---")

    st.markdown("### 🎛 Filtres")

    top_n = st.slider("Top N communes / paramètres", 5, 30, 15)
    region_filter = st.selectbox(
        "Région (à venir)",
        ["Toutes les régions", "Île-de-France", "Occitanie", "Nouvelle-Aquitaine",
         "Auvergne-Rhône-Alpes", "Provence-Alpes-Côte d'Azur"],
        disabled=False,
    )
    show_nc_only = st.checkbox("Afficher uniquement les non-conformités", value=False)

    st.markdown("---")
    st.markdown("### 📊 Données")
    st.caption("Source : data.gouv.fr")
    st.caption("Contrôle sanitaire 2024")
    st.caption("Pipeline : Databricks · Unity Catalog")

    st.markdown("---")
    st.markdown("### 🔗 Ressources")
    st.markdown("[FastAPI Docs](http://localhost:8000/docs)")
    st.markdown("[GitHub Repo](https://github.com/MariamDouamba/water-quality-pipeline)")
    st.markdown("[Databricks](https://dbc-8dca470e-413b.cloud.databricks.com)")

# ── LOAD DATA ─────────────────────────────────────────────────────────────────
with st.spinner("Chargement des données…"):
    df_temp, df_params, df_communes, df_depts, source = get_all_data()

# ── HEADER ────────────────────────────────────────────────────────────────────
col_title, col_badge = st.columns([3, 1])
with col_title:
    st.markdown("# Qualité de l'Eau en France")
    st.caption(f"Résultats du contrôle sanitaire 2024 — data.gouv.fr | Source : {'🟢 Databricks live' if source == 'databricks' else '🟡 Données de démonstration'}")

with col_badge:
    st.markdown(f"""
    <div style="text-align:right; padding-top: 1rem;">
        <span class="badge">{'🟢 LIVE' if source == 'databricks' else '🟡 DEMO'}</span>
    </div>
    """, unsafe_allow_html=True)

st.divider()

# ── KPIs ──────────────────────────────────────────────────────────────────────
k1, k2, k3, k4, k5, k6 = st.columns(6)

k1.metric("📊 Analyses",       "12.6M",  "+100%")
k2.metric("🧪 Prélèvements",   "291 604", None)
k3.metric("🏘 Communes",        "34 811",  None)
k4.metric("🗺 Départements",    "101",     None)
k5.metric("🔬 Paramètres",     "1 386",   None)
k6.metric("✅ Conformité",      "94.2%",  "+0.3%")

st.divider()

# ── ROW 1 : Temporel + Gauge ──────────────────────────────────────────────────
st.subheader("📅 Évolution temporelle")
col_temp, col_gauge = st.columns([2, 1])

with col_temp:
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df_temp['mois'], y=df_temp['nb_prelevements'],
        mode='lines+markers',
        fill='tozeroy', fillcolor='rgba(0,180,255,0.06)',
        line=dict(color='#00b4ff', width=2.5, shape='spline'),
        marker=dict(color='#00e5ff', size=7, line=dict(color='#00b4ff', width=2)),
        name='Prélèvements',
        hovertemplate='<b>%{x}</b><br>%{y:,.0f} prélèvements<extra></extra>',
    ))
    st.plotly_chart(styled_chart(fig, 300), width='stretch')

with col_gauge:
    fig_gauge = go.Figure(go.Indicator(
        mode="gauge+number",
        value=94.2,
        number={'suffix': '%', 'font': {'size': 40, 'color': '#00e676'}},
        title={'text': "Taux de conformité national", 'font': {'color': '#7fa8c9', 'size': 12}},
        gauge={
            'axis': {'range': [0, 100]},
            'bar': {'color': '#00e676', 'thickness': 0.25},
            'steps': [
                {'range': [0, 70],  'color': 'rgba(255,82,82,0.15)'},
                {'range': [70, 90], 'color': 'rgba(255,193,7,0.1)'},
                {'range': [90, 100],'color': 'rgba(0,230,118,0.1)'},
            ],
            'threshold': {'line': {'color': '#00b4ff', 'width': 2}, 'thickness': 0.8, 'value': 95},
        }
    ))
    fig_gauge.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#7fa8c9'),
        height=300,
        margin=dict(t=40, b=20, l=30, r=30)
    )
    st.plotly_chart(fig_gauge, width='stretch')

st.divider()

# ── ROW 2 : Paramètres + Communes ─────────────────────────────────────────────
st.subheader("⚠️ Non-conformités")
col_p, col_c = st.columns(2)

with col_p:
    st.caption("Top paramètres non conformes")
    df_p = df_params.head(top_n).sort_values('nb_nc')

    fig_p = go.Figure(go.Bar(
        x=df_p['nb_nc'], y=df_p['nom_parametre'],
        orientation='h',
        marker=dict(
            color=df_p['nb_nc'].tolist(),
            colorscale=[[0,'#00b4ff'],[0.5,'#ffc107'],[1,'#ff5252']],
            showscale=False,
        ),
        hovertemplate='<b>%{y}</b><br>%{x:,.0f} NC<extra></extra>',
    ))
    st.plotly_chart(styled_chart(fig_p, 400), width='stretch')

with col_c:
    st.caption("Top communes non conformes")
    df_c = df_communes.head(top_n).copy()
    df_c['label'] = df_c['nom_commune'] + ' (' + df_c['code_dept'].astype(str) + ')'
    df_c = df_c.sort_values('nb_nc')

    fig_c = go.Figure(go.Bar(
        x=df_c['nb_nc'], y=df_c['label'],
        orientation='h',
        marker=dict(
            color=df_c['nb_nc'].tolist(),
            colorscale=[[0,'#00b4ff'],[1,'#00e5ff']],
            showscale=False,
        ),
        hovertemplate='<b>%{y}</b><br>%{x:,.0f} NC<extra></extra>',
    ))
    st.plotly_chart(styled_chart(fig_c, 400), width='stretch')

st.divider()

# ── ROW 3 : Départements ──────────────────────────────────────────────────────
st.subheader("🗺 Analyse par département")

tab1, tab2 = st.tabs(["📊 Analyses totales", "⚠️ Non-conformités"])

with tab1:
    df_d = df_depts.head(30).copy()
    fig_d = px.bar(
        df_d, x='nom_departement', y='nb_analyses',
        color='nb_analyses',
        color_continuous_scale=[[0,'#1565C0'],[1,'#00b4ff']],
        labels={'nb_analyses': 'Analyses', 'nom_departement': ''},
        hover_data=['code_dept'],
    )
    fig_d.update_traces(
        hovertemplate='<b>%{x}</b><br>%{y:,.0f} analyses<extra></extra>',
    )
    fig_d.update_coloraxes(showscale=False)
    fig_d.update_xaxes(tickangle=-35, tickfont=dict(size=9))
    st.plotly_chart(styled_chart(fig_d, 350), width='stretch')

with tab2:
    if 'nb_nc' in df_depts.columns:
        df_nc = df_depts.head(30).copy()
        fig_nc = px.bar(
            df_nc, x='nom_departement', y='nb_nc',
            color='nb_nc',
            color_continuous_scale=[[0,'#ffc107'],[1,'#ff5252']],
            labels={'nb_nc': 'Non-conformités', 'nom_departement': ''},
        )
        fig_nc.update_traces(
            hovertemplate='<b>%{x}</b><br>%{y:,.0f} NC<extra></extra>',
        )
        fig_nc.update_coloraxes(showscale=False)
        fig_nc.update_xaxes(tickangle=-35, tickfont=dict(size=9))
        st.plotly_chart(styled_chart(fig_nc, 350), width='stretch')
    else:
        st.info("Données de non-conformités par département disponibles avec connexion Databricks.")

st.divider()

# ── ROW 4 : Distribution boxplot ──────────────────────────────────────────────
st.subheader("📈 Distribution des résultats")

top_params = df_params['nom_parametre'].head(6).tolist()
selected_params = st.multiselect(
    "Choisir les paramètres à comparer",
    options=df_params['nom_parametre'].tolist(),
    default=top_params[:4],
    max_selections=6,
)

if selected_params:
    fig_box = go.Figure()
    colors = ['#00b4ff','#00e5ff','#ffc107','#00e676','#ff5252','#bb86fc']
    for i, param in enumerate(selected_params):
        vals = gen_boxplot(param)
        fig_box.add_trace(go.Box(
            y=vals, name=param,
            boxpoints='outliers',
            marker=dict(color=colors[i % len(colors)], size=3),
            line=dict(color=colors[i % len(colors)], width=1.5),
            fillcolor=f'rgba({int(colors[i%len(colors)][1:3],16)},{int(colors[i%len(colors)][3:5],16)},{int(colors[i%len(colors)][5:],16)},0.15)',
        ))
    st.plotly_chart(styled_chart(fig_box, 380), width='stretch')
    st.caption("Distribution simulée — données réelles disponibles avec connexion Databricks")

st.divider()

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown("""
<div style="text-align:center; padding: 1rem 0; color: #3d6080; font-size: 11px;">
    <strong style="color:#7fa8c9; font-family:'Syne',sans-serif;">AquaStat</strong>
    &nbsp;—&nbsp; Water Quality Pipeline · Mariam Douamba · Simplon.co · 2026
    <br>Source : data.gouv.fr — Contrôle sanitaire de l'eau 2024
</div>
""", unsafe_allow_html=True)# refreshed Tue May 12 01:18:15 CEST 2026
