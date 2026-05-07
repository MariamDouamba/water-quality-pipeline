"""
Connexion à Databricks SQL Warehouse.
"""
import os
from databricks import sql
from dotenv import load_dotenv

load_dotenv()

DATABRICKS_HOST = os.getenv("DATABRICKS_HOST")
DATABRICKS_HTTP_PATH = os.getenv("DATABRICKS_HTTP_PATH")
DATABRICKS_TOKEN = os.getenv("DATABRICKS_TOKEN")


def get_connection():
    """Crée une connexion au SQL Warehouse Databricks."""
    if DATABRICKS_TOKEN:
        return sql.connect(
            server_hostname=DATABRICKS_HOST,
            http_path=DATABRICKS_HTTP_PATH,
            access_token=DATABRICKS_TOKEN,
        )
    else:
        raise Exception("DATABRICKS_TOKEN non défini dans .env")


def execute_query(query: str):
    """Exécute une requête SQL et retourne les résultats."""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(query)
        columns = [desc[0] for desc in cursor.description]
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        return [dict(zip(columns, row)) for row in rows]
    except Exception as e:
        print(f"ERREUR SQL : {e}")
        raise e