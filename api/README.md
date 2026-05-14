# API Qualité de l'Eau

API REST pour accéder aux données de qualité de l'eau en France, construite avec FastAPI et connectée à Databricks.

## Installation

```bash
cd api
pip install -r requirements.txt
```

## Configuration

Crée un fichier `.env` dans le dossier `api/` :

```env
DATABRICKS_HOST=dbc-8dca470e-413b.cloud.databricks.com
DATABRICKS_HTTP_PATH=/sql/1.0/warehouses/ton-warehouse-id
DATABRICKS_TOKEN=ton-token-databricks
```

Pour obtenir ces valeurs :
1. Databricks → SQL Warehouses → clique sur ton warehouse → Connection details
2. Databricks → Settings → Developer → Access tokens → Generate new token

## Lancement

```bash
uvicorn main:app --reload
```

L'API sera disponible sur http://localhost:8000

## Documentation

La documentation interactive (Swagger) est auto-générée :
- http://localhost:8000/docs (Swagger UI)
- http://localhost:8000/redoc (ReDoc)

## Endpoints disponibles

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| GET | / | Accueil |
| GET | /stats | Statistiques globales |
| GET | /departements | Liste des départements |
| GET | /departements/{code} | Détail d'un département |
| GET | /departements/{code}/non-conformites | Non-conformités d'un département |
| GET | /communes/top-non-conformes | Top communes non conformes |
| GET | /parametres | Liste des paramètres |
| GET | /parametres/non-conformites | Paramètres les plus non conformes |
| GET | /prelevements/par-mois | Analyses par mois |
| GET | /analyses/non-conformes | Détail des non-conformités |

## Stack

- **Framework** : FastAPI
- **Serveur** : Uvicorn
- **Base de données** : Databricks SQL (Delta Lake Gold)
- **Connecteur** : `databricks-sql-connector`
