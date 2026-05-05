# Databricks notebook source
# MAGIC %md
# MAGIC # 01 - Ingestion des données de qualité de l'eau (Bronze)
# MAGIC Ce notebook télécharge les données depuis l'API data.gouv.fr
# MAGIC et les stocke dans la couche Bronze en format Delta.

# COMMAND ----------

import requests
import zipfile
import io
import os
import pandas as pd

# Configuration
DATASET_ID = "resultats-du-controle-sanitaire-de-leau-distribuee-commune-par-commune"
ANNEE = "2024"

# COMMAND ----------

# MAGIC %md
# MAGIC ## 1. Appel API data.gouv.fr

# COMMAND ----------

url = f"https://www.data.gouv.fr/api/1/datasets/{DATASET_ID}/"
response = requests.get(url)
dataset = response.json()

# Trouver le fichier de l'année souhaitée
resource = None
for r in dataset['resources']:
    if f"dis-{ANNEE}.zip" == r['title'].lower():
        resource = r
        break

if resource is None:
    for r in dataset['resources']:
        if ANNEE in r['title'] and 'dept' not in r['title'].lower():
            resource = r
            break

print(f"Fichier trouvé : {resource['title']}")
print(f"URL : {resource['url']}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 2. Téléchargement et extraction

# COMMAND ----------

print(f"Téléchargement de {resource['title']}...")
response = requests.get(resource['url'], stream=True)
zip_file = zipfile.ZipFile(io.BytesIO(response.content))
file_list = zip_file.namelist()
print(f"Fichiers dans le ZIP : {file_list}")

# Identifier le fichier de résultats
result_file = [f for f in file_list if "RESULT" in f.upper()][0]
print(f"Fichier de résultats : {result_file}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 3. Chargement et sauvegarde en Bronze (Delta)

# COMMAND ----------

# Lire le CSV par chunks et sauvegarder en CSV propre dans le Workspace
csv_data = zip_file.read(result_file)

workspace_dir = f"/Workspace/Users/{spark.conf.get('spark.databricks.workspaceUrl', 'user')}/bronze_csv"
os.makedirs(workspace_dir, exist_ok=True)

chunk_size = 500_000
reader = pd.read_csv(
    io.BytesIO(csv_data),
    sep=',',
    encoding='latin-1',
    low_memory=False,
    on_bad_lines='skip',
    chunksize=chunk_size,
    dtype=str
)

for i, chunk in enumerate(reader):
    csv_path = f"{workspace_dir}/part_{i:03d}.csv"
    chunk.to_csv(csv_path, index=False, header=(i == 0))
    print(f"Chunk {i} : {len(chunk):,} lignes")

# COMMAND ----------

# Lire avec Spark et sauvegarder en Delta
from pyspark.sql.functions import current_timestamp, lit

df_bronze = spark.read \
    .option("header", "true") \
    .option("inferSchema", "false") \
    .csv(f"{workspace_dir}/part_000.csv")

colonnes = df_bronze.columns
from functools import reduce
from pyspark.sql import DataFrame

all_files = sorted([f for f in os.listdir(workspace_dir) if f.endswith('.csv')])
dfs = []
for f in all_files:
    path = f"{workspace_dir}/{f}"
    if f == "part_000.csv":
        df = spark.read.option("header", "true").option("inferSchema", "false").csv(path)
    else:
        df = spark.read.option("header", "false").option("inferSchema", "false").csv(path)
        df = df.toDF(*colonnes)
    dfs.append(df)

df_bronze_all = reduce(DataFrame.unionAll, dfs)

# Ajouter métadonnées
df_bronze_final = df_bronze_all \
    .withColumn("_source_file", lit(result_file)) \
    .withColumn("_ingestion_timestamp", current_timestamp()) \
    .withColumn("_year", lit(ANNEE))

# Sauvegarder en Delta
df_bronze_final.write \
    .format("delta") \
    .mode("overwrite") \
    .option("overwriteSchema", "true") \
    .saveAsTable("bronze_qualite_eau")

print(f"Table bronze_qualite_eau créée : {df_bronze_final.count():,} lignes")
