"""
Connexion à Databricks SQL Warehouse.
"""
import os
from databricks import sql
from dotenv import load_dotenv

load_dotenv()

# Configuration Databricks
# Ces valeurs se trouvent dans Databricks :
# SQL Warehouses → ton warehouse → Connection details
DATABRICKS_HOST = os.getenv("DATABRICKS_HOST", "dbc-8dca470e-413b.cloud.databricks.com")
DATABRICKS_HTTP_PATH = os.getenv("DATABRICKS_HTTP_PATH", "/sql/1.0/warehouses/xxxxxx")
DATABRICKS_TOKEN = os.getenv("DATABRICKS_TOKEN", "")


def get_connection():
    """Crée une connexion au SQL Warehouse Databricks."""
    return sql.connect(
        server_hostname=DATABRICKS_HOST,
        http_path=DATABRICKS_HTTP_PATH,
        access_token=DATABRICKS_TOKEN,
    )


def execute_query(query: str):
    """Exécute une requête SQL et retourne les résultats."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(query)
    columns = [desc[0] for desc in cursor.description]
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return [dict(zip(columns, row)) for row in rows]