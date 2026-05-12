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
    initial_sidebar_state="expanded",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;700;800&family=DM+Sans:wght@300;400;500&display=swap');

html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }
.stApp { background: #050d18; }
[data-testid="stSidebar"] { background: #0a1628 !important; border-right: 1px solid rgba(0,180,255,0.12); }

h1 { font-family: 'Syne', sans-serif !important; font-weight: 800 !important;
     background: linear-gradient(90deg, #00b4ff, #00e5ff);
     -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
h2, h3 { font-family: 'Syne', sans-serif !important; color: #e8f4fd !important; }

[data-testid="metric-container"] {
  background: #111d32; border: 1px solid rgba(0,180,255,0.15);
  border-radius: 12px; padding: 1rem !important;
}
[data-testid="metric-container"] label { color: #3d6080 !important; font-size: 11px !important; letter-spacing: 0.08em; text-transform: uppercase; }
[data-testid="metric-container"] [data-testid="stMetricValue"] { color: #00b4ff !important; font-family: 'Syne', sans-serif !important; font-weight: 800 !important; }
[data-testid="metric-container"] [data-testid="stMetricDelta"] { color: #00e676 !important; }

.stSelectbox label, .stSlider label, .stMultiSelect label { color: #7fa8c9 !important; font-size: 12px !important; }
hr { border-color: rgba(0,180,255,0.12) !important; }

.sidebar-title { font-family: 'Syne', sans-serif; font-size: 1.1rem; font-weight: 800;
  color: #e8f4fd; margin-bottom: 0.5rem; display: flex; align-items: center; gap: 8px; }
.badge { display: inline-block; background: rgba(0,180,255,0.1); border: 1px solid rgba(0,180,255,0.2);
  border-radius: 100px; padding: 2px 10px; font-size: 10px; color: #00b4ff;
  font-family: 'Syne', sans-serif; font-weight: 600; }
.badge-live { background: rgba(0,230,118,0.1); border-color: rgba(0,230,118,0.3); color: #00e676; }
.badge-demo { background: rgba(255,193,7,0.1); border-color: rgba(255,193,7,0.3); color: #ffc107; }

.section-card { background: #0d1f38; border: 1px solid rgba(0,180,255,0.1);
  border-radius: 16px; padding: 1.5rem; margin-bottom: 1rem; }
</style>
""", unsafe_allow_html=True)

# ── Plotly dark theme ──────────────────────────────────────────────────────────
THEME = dict(
    paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
    font=dict(family='DM Sans', color='#7fa8c9', size=11),
    margin=dict(t=30, b=40, l=50, r=20),
    colorway=['#00b4ff','#00e5ff','#ffc107','#00e676','#ff5252','#bb86fc','#ff7043'],
)
AXIS = dict(
    gridcolor='rgba(0,180,255,0.08)', linecolor='rgba(0,180,255,0.15)',
    tickfont=dict(color='#3d6080', size=10), zerolinecolor='rgba(0,180,255,0.08)',
)

def styled_chart(fig, height=350):
    fig.update_layout(**THEME, height=height)
    fig.update_xaxes(**AXIS)
    fig.update_yaxes(**AXIS)
    return fig

# ── Credentials ────────────────────────────────────────────────────────────────
def _get_databricks_creds():
    try:
        if "databricks" in st.secrets:
            h = st.secrets["databricks"]["host"]
            p = st.secrets["databricks"]["http_path"]
            t = st.secrets["databricks"]["token"]
            if t:
                return h, p, t
    except Exception:
        pass
    return (
        os.getenv("DATABRICKS_HOST", ""),
        os.getenv("DATABRICKS_HTTP_PATH", ""),
        os.getenv("DATABRICKS_TOKEN", ""),
    )

def _get_api_url():
    try:
        return st.secrets.get("api_url", "http://localhost:8000")
    except Exception:
        return os.getenv("API_URL", "http://localhost:8000")

@st.cache_data(ttl=3600, show_spinner=False)
def load_databricks(query):
    host, http_path, token = _get_databricks_creds()
    if not token:
        return None, "no_credentials"
    try:
        from databricks import sql
        with sql.connect(server_hostname=host, http_path=http_path, access_token=token) as conn:
            with conn.cursor() as cur:
                cur.execute(query)
                cols = [d[0] for d in cur.description]
                rows = cur.fetchall()
                return pd.DataFrame(rows, columns=cols), "databricks"
    except Exception as e:
        return None, str(e)

@st.cache_data(ttl=3600, show_spinner=False)
def load_france_geojson():
    try:
        url = "https://raw.githubusercontent.com/gregoiredavid/france-geojson/master/departements-version-simplifiee.geojson"
        return http_requests.get(url, timeout=10).json()
    except Exception:
        return None

def normalize_dept_code(code):
    """Convertit 001→01, 02A→2A, 971→971"""
    if str(code).upper() in ('02A', '2A'):
        return '2A'
    if str(code).upper() in ('02B', '2B'):
        return '2B'
    try:
        n = int(code)
        return f"{n:02d}" if n < 100 else f"{n:03d}"
    except Exception:
        return str(code)

# ── Fallback data ──────────────────────────────────────────────────────────────
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
    noms = ['Bouches-du-Rhône','Rhône','Gironde','Nord','Haute-Garonne',
            'Loire-Atlantique','Bas-Rhin','Alpes-Maritimes','Hérault','Ille-et-Vilaine',
            'Isère','Var','Marne','Loire','Seine-Maritime','Côte-d\'Or','Gard',
            'Finistère','Haute-Vienne','Paris']
    codes = ['13','69','33','59','31','44','67','06','34','35',
             '38','83','51','42','76','21','30','29','87','75']
    nb = sorted([np.random.randint(50000,500000) for _ in range(20)], reverse=True)
    nc = [int(n*np.random.uniform(0.03,0.09)) for n in nb]
    tc = [round((n-c)/n*100, 2) for n, c in zip(nb, nc)]
    return pd.DataFrame({'nom_departement': noms, 'code_dept': codes,
                         'nb_analyses': nb, 'nb_nc': nc, 'taux_conformite': tc})

# ── Load all data ──────────────────────────────────────────────────────────────
@st.cache_data(ttl=3600, show_spinner=False)
def get_all_data():
    source = "simulation"

    # KPIs
    df_kpis, _ = load_databricks("""
        SELECT COUNT(*) AS total_analyses,
               SUM(CASE WHEN est_conforme = 'Non conforme' THEN 1 ELSE 0 END) AS total_nc,
               ROUND(SUM(CASE WHEN est_conforme = 'Conforme' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 1) AS taux_conformite
        FROM gold_fact_analyses
    """)

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
        SELECT p.libelle_parametre AS nom_parametre,
               p.categorie_parametre,
               COUNT(*) AS nb_nc
        FROM gold_fact_analyses f
        JOIN gold_dim_parametre p ON f.parametre_code = p.cdparametresiseeaux
        WHERE f.est_conforme = 'Non conforme'
        GROUP BY p.libelle_parametre, p.categorie_parametre
        ORDER BY nb_nc DESC LIMIT 20
    """)
    if df_params is None:
        df_params = gen_params_nc()

    # Communes NC
    df_communes, _ = load_databricks("""
        SELECT commune AS nom_commune,
               departement_code AS code_dept,
               COUNT(*) AS nb_nc
        FROM gold_fact_analyses
        WHERE est_conforme = 'Non conforme' AND commune IS NOT NULL
        GROUP BY commune, departement_code
        ORDER BY nb_nc DESC LIMIT 30
    """)
    if df_communes is None:
        df_communes = gen_communes_nc()

    # Depts
    df_depts, _ = load_databricks("""
        SELECT nom_departement,
               code_departement AS code_dept,
               nb_analyses,
               nb_non_conformes AS nb_nc,
               taux_conformite
        FROM gold_dim_departement
        ORDER BY nb_analyses DESC LIMIT 96
    """)
    if df_depts is None:
        df_depts = gen_depts()

    return df_kpis, df_temp, df_params, df_communes, df_depts, source

# ── SIDEBAR ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div class="sidebar-title">💧 AquaStat</div>', unsafe_allow_html=True)
    st.markdown('<span class="badge">v1.0.0</span>', unsafe_allow_html=True)
    st.markdown("---")
    st.markdown("### 🎛 Filtres")
    top_n = st.slider("Top N communes / paramètres", 5, 30, 15)
    show_nc_only = st.checkbox("Afficher uniquement les départements non conformes", value=False)
    st.markdown("---")
    st.markdown("### 📊 Données")
    st.caption("Source : data.gouv.fr")
    st.caption("Contrôle sanitaire 2024")
    st.caption("Pipeline : Databricks · Unity Catalog")
    st.markdown("---")
    st.markdown("### 🔗 Ressources")
    api_url = _get_api_url()
    st.markdown(f"[FastAPI Docs]({api_url}/docs)")
    st.markdown("[GitHub Repo](https://github.com/MariamDouamba/water-quality-pipeline)")
    st.markdown("[Databricks](https://dbc-8dca470e-413b.cloud.databricks.com)")

# ── LOAD DATA ─────────────────────────────────────────────────────────────────
with st.spinner("Chargement des données…"):
    df_kpis, df_temp, df_params, df_communes, df_depts, source = get_all_data()
    geojson = load_france_geojson()

is_live = source == "databricks"

# ── HEADER ────────────────────────────────────────────────────────────────────
col_title, col_badge = st.columns([3, 1])
with col_title:
    st.markdown("# Qualité de l'Eau en France")
    st.caption(f"Résultats du contrôle sanitaire 2024 — data.gouv.fr | Source : {'🟢 Databricks live' if is_live else '🟡 Données de démonstration'}")
with col_badge:
    badge_class = "badge badge-live" if is_live else "badge badge-demo"
    badge_text  = "🟢 LIVE" if is_live else "🟡 DEMO"
    st.markdown(f'<div style="text-align:right;padding-top:1rem"><span class="{badge_class}">{badge_text}</span></div>', unsafe_allow_html=True)

st.divider()

# ── KPIs ──────────────────────────────────────────────────────────────────────
if df_kpis is not None and len(df_kpis) > 0:
    row = df_kpis.iloc[0]
    total   = int(row['total_analyses'])
    total_nc = int(row['total_nc'])
    taux    = float(row['taux_conformite'])
else:
    total, total_nc, taux = 12_645_691, 28_140, 99.78

k1, k2, k3, k4, k5, k6 = st.columns(6)
k1.metric("📊 Analyses",     f"{total/1_000_000:.1f}M")
k2.metric("🧪 Prélèvements", "291 604")
k3.metric("🏘 Communes",      "34 811")
k4.metric("🗺 Départements",  "101")
k5.metric("⚠️ Non-conformes", f"{total_nc:,}")
k6.metric("✅ Conformité",    f"{taux}%", "+0.3%")

st.divider()

# ── CARTE + GAUGE ──────────────────────────────────────────────────────────────
st.subheader("🗺 Carte de la conformité par département")
col_map, col_gauge = st.columns([3, 1])

with col_map:
    if geojson and df_depts is not None and 'taux_conformite' in df_depts.columns:
        df_map = df_depts.copy()
        df_map['code_geo'] = df_map['code_dept'].apply(normalize_dept_code)
        df_map['taux_conformite'] = pd.to_numeric(df_map['taux_conformite'], errors='coerce')

        fig_map = px.choropleth(
            df_map,
            geojson=geojson,
            locations='code_geo',
            featureidkey='properties.code',
            color='taux_conformite',
            color_continuous_scale=[
                [0.00, '#ff5252'],
                [0.70, '#ffc107'],
                [0.95, '#00b4ff'],
                [1.00, '#00e676'],
            ],
            range_color=[95, 100],
            hover_name='nom_departement',
            hover_data={'taux_conformite': ':.2f%', 'nb_analyses': ':,', 'code_geo': False},
            labels={'taux_conformite': 'Conformité (%)'},
        )
        fig_map.update_geos(fitbounds="locations", visible=False)
        fig_map.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            geo=dict(bgcolor='rgba(0,0,0,0)'),
            coloraxis_colorbar=dict(
                title="Conformité %",
                tickfont=dict(color='#7fa8c9', size=10),
                title_font=dict(color='#7fa8c9'),
                len=0.6,
            ),
            margin=dict(t=10, b=10, l=0, r=0),
            height=420,
        )
        st.plotly_chart(fig_map, use_container_width=True)
    else:
        st.info("Carte non disponible (GeoJSON ou données non chargés).")

with col_gauge:
    fig_gauge = go.Figure(go.Indicator(
        mode="gauge+number",
        value=taux,
        number={'suffix': '%', 'font': {'size': 38, 'color': '#00e676'}},
        title={'text': "Taux national", 'font': {'color': '#7fa8c9', 'size': 13}},
        gauge={
            'axis': {'range': [90, 100], 'tickfont': {'color': '#3d6080', 'size': 9}},
            'bar': {'color': '#00e676', 'thickness': 0.25},
            'steps': [
                {'range': [90, 95], 'color': 'rgba(255,82,82,0.15)'},
                {'range': [95, 98], 'color': 'rgba(255,193,7,0.1)'},
                {'range': [98, 100],'color': 'rgba(0,230,118,0.1)'},
            ],
            'threshold': {'line': {'color': '#00b4ff', 'width': 2}, 'thickness': 0.8, 'value': 99},
        }
    ))
    fig_gauge.update_layout(
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#7fa8c9'), height=420,
        margin=dict(t=60, b=20, l=30, r=30)
    )
    st.plotly_chart(fig_gauge, use_container_width=True)

st.divider()

# ── ÉVOLUTION TEMPORELLE ───────────────────────────────────────────────────────
st.subheader("📅 Évolution temporelle des prélèvements")
fig_temp = go.Figure()
fig_temp.add_trace(go.Scatter(
    x=df_temp['mois'], y=df_temp['nb_prelevements'],
    mode='lines+markers',
    fill='tozeroy', fillcolor='rgba(0,180,255,0.06)',
    line=dict(color='#00b4ff', width=2.5, shape='spline'),
    marker=dict(color='#00e5ff', size=7, line=dict(color='#00b4ff', width=2)),
    hovertemplate='<b>%{x}</b><br>%{y:,.0f} prélèvements<extra></extra>',
))
st.plotly_chart(styled_chart(fig_temp, 280), use_container_width=True)

st.divider()

# ── NON-CONFORMITÉS ────────────────────────────────────────────────────────────
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
        hovertemplate='<b>%{y}</b><br>%{x:,.0f} non-conformités<extra></extra>',
    ))
    st.plotly_chart(styled_chart(fig_p, 420), use_container_width=True)

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
        hovertemplate='<b>%{y}</b><br>%{x:,.0f} non-conformités<extra></extra>',
    ))
    st.plotly_chart(styled_chart(fig_c, 420), use_container_width=True)

st.divider()

# ── DÉPARTEMENTS ──────────────────────────────────────────────────────────────
st.subheader("🗺 Analyse par département")

df_d = df_depts.copy()
if show_nc_only and 'nb_nc' in df_d.columns:
    df_d = df_d[df_d['nb_nc'] > 0]

tab1, tab2, tab3 = st.tabs(["📊 Analyses totales", "⚠️ Non-conformités", "📋 Tableau complet"])

with tab1:
    fig_d = px.bar(
        df_d.head(30), x='nom_departement', y='nb_analyses',
        color='nb_analyses',
        color_continuous_scale=[[0,'#1565C0'],[1,'#00b4ff']],
        labels={'nb_analyses': 'Analyses', 'nom_departement': ''},
    )
    fig_d.update_traces(hovertemplate='<b>%{x}</b><br>%{y:,.0f} analyses<extra></extra>')
    fig_d.update_coloraxes(showscale=False)
    fig_d.update_xaxes(tickangle=-35, tickfont=dict(size=9))
    st.plotly_chart(styled_chart(fig_d, 380), use_container_width=True)

with tab2:
    if 'nb_nc' in df_d.columns:
        fig_nc = px.bar(
            df_d.head(30), x='nom_departement', y='nb_nc',
            color='nb_nc',
            color_continuous_scale=[[0,'#ffc107'],[1,'#ff5252']],
            labels={'nb_nc': 'Non-conformités', 'nom_departement': ''},
        )
        fig_nc.update_traces(hovertemplate='<b>%{x}</b><br>%{y:,.0f} NC<extra></extra>')
        fig_nc.update_coloraxes(showscale=False)
        fig_nc.update_xaxes(tickangle=-35, tickfont=dict(size=9))
        st.plotly_chart(styled_chart(fig_nc, 380), use_container_width=True)

with tab3:
    cols_show = [c for c in ['nom_departement','code_dept','nb_analyses','nb_nc','taux_conformite'] if c in df_d.columns]
    st.dataframe(
        df_d[cols_show].rename(columns={
            'nom_departement': 'Département',
            'code_dept': 'Code',
            'nb_analyses': 'Analyses',
            'nb_nc': 'Non-conformes',
            'taux_conformite': 'Conformité %',
        }),
        use_container_width=True, hide_index=True, height=400,
    )

st.divider()

# ── FOOTER ────────────────────────────────────────────────────────────────────
st.markdown("""
<div style="text-align:center; padding: 1rem 0; color: #3d6080; font-size: 11px;">
    <strong style="color:#7fa8c9; font-family:'Syne',sans-serif;">AquaStat</strong>
    &nbsp;—&nbsp; Water Quality Pipeline · Mariam Douamba · Simplon.co · 2026
    <br>Source : data.gouv.fr — Contrôle sanitaire de l'eau 2024
</div>
""", unsafe_allow_html=True)
