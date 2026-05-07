"""
API FastAPI pour exposer les données de qualité de l'eau.
Documentation auto-générée sur http://localhost:8000/docs
"""
from fastapi import FastAPI, Query, HTTPException
from typing import Optional, List
from database import execute_query

app = FastAPI(
    title="API Qualité de l'Eau - France",
    description="""
    API pour accéder aux données de qualité de l'eau distribuée en France (2024).
    
    Sources : data.gouv.fr - Résultats du contrôle sanitaire de l'eau.
    
    Données :
    - 12.6 millions d'analyses
    - 291 604 prélèvements
    - 101 départements
    - 34 811 communes
    """,
    version="1.0.0",
)


# ---- ENDPOINTS STATISTIQUES ----

@app.get("/", tags=["Général"])
def accueil():
    """Page d'accueil de l'API."""
    return {
        "message": "API Qualité de l'Eau - France 2024",
        "documentation": "/docs",
        "endpoints": [
            "/stats",
            "/departements",
            "/departements/{code}",
            "/communes/top-non-conformes",
            "/parametres",
            "/parametres/non-conformites",
            "/prelevements/par-mois",
            "/analyses/non-conformes",
        ],
    }


@app.get("/stats", tags=["Statistiques"])
def statistiques_globales():
    """Retourne les statistiques globales du dataset."""
    stats = execute_query("""
        SELECT 
            COUNT(*) as total_analyses,
            SUM(CASE WHEN est_conforme = 'Non conforme' THEN 1 ELSE 0 END) as total_non_conformes
        FROM gold_fact_analyses
    """)[0]

    dept = execute_query("SELECT COUNT(*) as n FROM gold_dim_departement")[0]
    prel = execute_query("SELECT COUNT(*) as n FROM gold_dim_prelevement")[0]
    comm = execute_query("SELECT COUNT(*) as n FROM gold_dim_commune")[0]

    total = stats["total_analyses"]
    nc = stats["total_non_conformes"]

    return {
        "total_analyses": total,
        "total_prelevements": prel["n"],
        "total_departements": dept["n"],
        "total_communes": comm["n"],
        "total_non_conformites": nc,
        "taux_conformite_global": round((total - nc) / total * 100, 2),
    }


# ---- ENDPOINTS DÉPARTEMENTS ----

@app.get("/departements", tags=["Départements"])
def liste_departements(
    region: Optional[str] = Query(None, description="Filtrer par région"),
    order_by: str = Query("taux_conformite", description="Trier par: taux_conformite, nb_analyses, nom_departement"),
    limit: int = Query(101, description="Nombre max de résultats"),
):
    """Liste tous les départements avec leurs statistiques."""
    query = "SELECT * FROM gold_dim_departement"
    if region:
        query += f" WHERE region = '{region}'"
    query += f" ORDER BY {order_by} LIMIT {limit}"
    return execute_query(query)


@app.get("/departements/{code}", tags=["Départements"])
def detail_departement(code: str):
    """Détail d'un département par son code."""
    result = execute_query(f"""
        SELECT * FROM gold_dim_departement 
        WHERE code_departement = '{code}'
    """)
    if not result:
        raise HTTPException(status_code=404, detail=f"Département {code} non trouvé")
    return result[0]


@app.get("/departements/{code}/non-conformites", tags=["Départements"])
def non_conformites_departement(code: str, limit: int = 20):
    """Liste les non-conformités d'un département."""
    return execute_query(f"""
        SELECT f.date_prelevement, f.commune, f.parametre_code,
               f.resultat_brut, f.valeur_numerique, f.limite_numerique,
               p.libelle_parametre, p.categorie_parametre
        FROM gold_fact_analyses f
        JOIN gold_dim_parametre p ON f.parametre_code = p.cdparametresiseeaux
        WHERE f.departement_code = '{code}'
          AND f.est_conforme = 'Non conforme'
        ORDER BY f.date_prelevement DESC
        LIMIT {limit}
    """)


# ---- ENDPOINTS COMMUNES ----

@app.get("/communes/top-non-conformes", tags=["Communes"])
def top_communes_non_conformes(limit: int = 10):
    """Top des communes avec le plus de non-conformités."""
    return execute_query(f"""
        SELECT commune, departement_code, 
               COUNT(*) as nb_non_conformites,
               COUNT(DISTINCT parametre_code) as nb_parametres_nc
        FROM gold_fact_analyses
        WHERE est_conforme = 'Non conforme' AND commune IS NOT NULL
        GROUP BY commune, departement_code
        ORDER BY nb_non_conformites DESC
        LIMIT {limit}
    """)


# ---- ENDPOINTS PARAMÈTRES ----

@app.get("/parametres", tags=["Paramètres"])
def liste_parametres(
    categorie: Optional[str] = Query(None, description="Filtrer par catégorie"),
    danger: Optional[str] = Query(None, description="Filtrer par niveau de danger"),
):
    """Liste les paramètres de qualité."""
    query = "SELECT * FROM gold_dim_parametre WHERE 1=1"
    if categorie:
        query += f" AND categorie_parametre = '{categorie}'"
    if danger:
        query += f" AND niveau_danger = '{danger}'"
    query += " ORDER BY categorie_parametre, libelle_parametre"
    return execute_query(query)


@app.get("/parametres/non-conformites", tags=["Paramètres"])
def parametres_non_conformes(limit: int = 15):
    """Paramètres causant le plus de non-conformités."""
    return execute_query(f"""
        SELECT p.libelle_parametre, p.categorie_parametre, p.niveau_danger,
               COUNT(*) as nb_non_conformites
        FROM gold_fact_analyses f
        JOIN gold_dim_parametre p ON f.parametre_code = p.cdparametresiseeaux
        WHERE f.est_conforme = 'Non conforme'
        GROUP BY p.libelle_parametre, p.categorie_parametre, p.niveau_danger
        ORDER BY nb_non_conformites DESC
        LIMIT {limit}
    """)


# ---- ENDPOINTS TEMPORELS ----

@app.get("/prelevements/par-mois", tags=["Temporel"])
def prelevements_par_mois():
    """Nombre de prélèvements et non-conformités par mois."""
    return execute_query("""
        SELECT MONTH(date_prelevement) as mois,
               COUNT(*) as nb_analyses,
               SUM(CASE WHEN est_conforme = 'Non conforme' THEN 1 ELSE 0 END) as nb_non_conformes,
               ROUND(SUM(CASE WHEN est_conforme = 'Non conforme' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) as taux_nc
        FROM gold_fact_analyses
        WHERE date_prelevement IS NOT NULL
        GROUP BY MONTH(date_prelevement)
        ORDER BY mois
    """)


@app.get("/analyses/non-conformes", tags=["Analyses"])
def analyses_non_conformes(
    departement: Optional[str] = None,
    categorie: Optional[str] = None,
    limit: int = 50,
):
    """Liste les analyses non conformes avec filtres optionnels."""
    query = """
        SELECT f.date_prelevement, f.commune, f.departement_code,
               f.parametre_code, f.resultat_brut, f.valeur_numerique,
               f.limite_numerique, p.libelle_parametre, p.categorie_parametre,
               p.niveau_danger
        FROM gold_fact_analyses f
        JOIN gold_dim_parametre p ON f.parametre_code = p.cdparametresiseeaux
        WHERE f.est_conforme = 'Non conforme'
    """
    if departement:
        query += f" AND f.departement_code = '{departement}'"
    if categorie:
        query += f" AND p.categorie_parametre = '{categorie}'"
    query += f" ORDER BY f.date_prelevement DESC LIMIT {limit}"
    return execute_query(query)


from fastapi.responses import StreamingResponse
import io
import csv


@app.get("/export/departements", tags=["Export"])
def export_departements_csv():
    """Exporte les départements en CSV."""
    data = execute_query("""
        SELECT code_departement, nom_departement, region,
               nb_analyses, nb_conformes, nb_non_conformes, taux_conformite
        FROM gold_dim_departement
        ORDER BY taux_conformite ASC
    """)

    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=data[0].keys())
    writer.writeheader()
    writer.writerows(data)

    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=departements.csv"}
    )


@app.get("/export/non-conformites", tags=["Export"])
def export_non_conformites_csv():
    """Exporte les non-conformités en CSV."""
    data = execute_query("""
        SELECT f.date_prelevement, f.commune, f.departement_code,
               f.parametre_code, f.resultat_brut, f.valeur_numerique,
               f.limite_numerique
        FROM gold_fact_analyses f
        WHERE f.est_conforme = 'Non conforme'
        ORDER BY f.date_prelevement DESC
        LIMIT 1000
    """)

    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=data[0].keys())
    writer.writeheader()
    writer.writerows(data)

    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=non_conformites.csv"}
    )


# ---- LANCEMENT ----
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)