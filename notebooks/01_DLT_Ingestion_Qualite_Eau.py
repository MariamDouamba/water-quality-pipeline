# Databricks notebook source
# MAGIC %md
# MAGIC # 01 - Ingestion des données de qualité de l'eau (Bronze)
# MAGIC Ce notebook télécharge les 3 fichiers depuis l'API data.gouv.fr
# MAGIC et les stocke dans la couche Bronze en format Delta.
# MAGIC
# MAGIC Fichiers ingérés :
# MAGIC - DIS_RESULT_2024.txt : résultats d'analyses (12.6M lignes)
# MAGIC - DIS_PLV_2024.txt : prélèvements avec dates et communes (408K lignes)
# MAGIC - DIS_COM_UDI_2024.txt : correspondances communes/réseaux (49K lignes)

# COMMAND ----------

import requests
import zipfile
import io
import pandas as pd
from pyspark.sql.functions import current_timestamp, lit

# Configuration
DATASET_ID = "resultats-du-controle-sanitaire-de-leau-distribuee-commune-par-commune"
ANNEE = "2024"

# COMMAND ----------

# MAGIC %md
# MAGIC ## 1. Appel API data.gouv.fr

# COMMAND ----------

url = f"https://www.data.gouv.fr/api/1/datasets/{DATASET_ID}/"
response = requests.get(url, timeout=30)
response.raise_for_status()
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

if resource is None:
    titres_disponibles = [r['title'] for r in dataset['resources']]
    raise ValueError(
        f"Aucun fichier trouvé pour l'année {ANNEE}.\n"
        f"Fichiers disponibles dans le dataset : {titres_disponibles}\n"
        f"Vérifiez la valeur de ANNEE ou le nom du dataset."
    )

print(f"Fichier trouvé : {resource['title']}")
print(f"URL : {resource['url']}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 2. Téléchargement et extraction du ZIP

# COMMAND ----------

print(f"Téléchargement de {resource['title']}...")
zip_buffer = io.BytesIO()
with requests.get(resource['url'], stream=True, timeout=300) as r:
    r.raise_for_status()
    for bloc in r.iter_content(chunk_size=8 * 1024 * 1024):
        zip_buffer.write(bloc)
zip_buffer.seek(0)
zip_file = zipfile.ZipFile(zip_buffer)
file_list = zip_file.namelist()
print(f"Fichiers dans le ZIP : {file_list}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 3. Ingestion DIS_RESULT (résultats d'analyses) → Bronze

# COMMAND ----------

result_file = [f for f in file_list if "RESULT" in f.upper()][0]
print(f"Lecture de {result_file}...")

# Écriture chunk par chunk directement dans Delta
# pour éviter le plan d'exécution trop profond (DEADLINE_EXCEEDED sur Serverless)
chunk_size = 1_000_000
reader = pd.read_csv(
    zip_file.open(result_file), sep=',', encoding='latin-1',
    low_memory=False, on_bad_lines='skip', chunksize=chunk_size, dtype=str
)

for i, chunk in enumerate(reader):
    df_chunk = spark.createDataFrame(chunk.astype(str)) \
        .withColumn("_source_file", lit(result_file)) \
        .withColumn("_ingestion_timestamp", current_timestamp()) \
        .withColumn("_year", lit(ANNEE))

    if i == 0:
        df_chunk.write.format("delta").mode("overwrite") \
            .option("overwriteSchema", "true") \
            .partitionBy("cddept") \
            .saveAsTable("bronze_qualite_eau")
    else:
        df_chunk.write.format("delta").mode("append") \
            .saveAsTable("bronze_qualite_eau")

    print(f"   Chunk {i} : {len(chunk):,} lignes écrites")

print(f"bronze_qualite_eau : {spark.table('bronze_qualite_eau').count():,} lignes")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 4. Ingestion DIS_PLV (prélèvements) → Bronze

# COMMAND ----------

plv_file = [f for f in file_list if "PLV" in f.upper()][0]
print(f"Lecture de {plv_file}...")
plv_data = zip_file.read(plv_file)

df_plv_pd = pd.read_csv(
    io.BytesIO(plv_data), sep=',', encoding='latin-1',
    low_memory=False, on_bad_lines='skip', dtype=str
)
print(f"   {len(df_plv_pd):,} lignes, {len(df_plv_pd.columns)} colonnes")

df_plv_spark = spark.createDataFrame(df_plv_pd.astype(str))
df_plv_spark \
    .withColumn("_source_file", lit(plv_file)) \
    .withColumn("_ingestion_timestamp", current_timestamp()) \
    .write.format("delta").mode("overwrite") \
    .option("overwriteSchema", "true") \
    .saveAsTable("bronze_prelevements")

print(f"bronze_prelevements : {spark.table('bronze_prelevements').count():,} lignes")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 5. Ingestion DIS_COM_UDI (communes) → Bronze

# COMMAND ----------

com_file = [f for f in file_list if "COM" in f.upper()][0]
print(f"Lecture de {com_file}...")
com_data = zip_file.read(com_file)

df_com_pd = pd.read_csv(
    io.BytesIO(com_data), sep=',', encoding='latin-1',
    low_memory=False, on_bad_lines='skip', dtype=str
)
print(f"   {len(df_com_pd):,} lignes, {len(df_com_pd.columns)} colonnes")

df_com_spark = spark.createDataFrame(df_com_pd.astype(str))
df_com_spark \
    .withColumn("_source_file", lit(com_file)) \
    .withColumn("_ingestion_timestamp", current_timestamp()) \
    .write.format("delta").mode("overwrite") \
    .option("overwriteSchema", "true") \
    .saveAsTable("bronze_communes")

print(f"bronze_communes : {spark.table('bronze_communes').count():,} lignes")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 6. Résumé de l'ingestion

# COMMAND ----------

print("=" * 60)
print("INGESTION BRONZE TERMINÉE")
print("=" * 60)
print(f"""
Tables créées :
   - bronze_qualite_eau   : {spark.table('bronze_qualite_eau').count():,} lignes (résultats)
   - bronze_prelevements  : {spark.table('bronze_prelevements').count():,} lignes (prélèvements)
   - bronze_communes      : {spark.table('bronze_communes').count():,} lignes (communes)
""")
