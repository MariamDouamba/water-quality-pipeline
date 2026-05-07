# Databricks notebook source
# MAGIC %md
# MAGIC # 05 - Setup Unity Catalog
# MAGIC Organisation des tables en catalogue structuré :
# MAGIC water_quality.bronze / silver / gold

# COMMAND ----------

# MAGIC %md
# MAGIC ## 1. Créer le catalogue et les schémas

# COMMAND ----------

spark.sql("CREATE CATALOG IF NOT EXISTS water_quality")
spark.sql("USE CATALOG water_quality")

spark.sql("CREATE SCHEMA IF NOT EXISTS bronze")
spark.sql("CREATE SCHEMA IF NOT EXISTS silver")
spark.sql("CREATE SCHEMA IF NOT EXISTS gold")

print("Catalogue et schémas créés !")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 2. Migrer les tables Bronze

# COMMAND ----------

spark.sql("""
    CREATE TABLE IF NOT EXISTS water_quality.bronze.qualite_eau
    AS SELECT * FROM workspace.default.bronze_qualite_eau
""")
spark.sql("""
    CREATE TABLE IF NOT EXISTS water_quality.bronze.prelevements
    AS SELECT * FROM workspace.default.bronze_prelevements
""")
spark.sql("""
    CREATE TABLE IF NOT EXISTS water_quality.bronze.communes
    AS SELECT * FROM workspace.default.bronze_communes
""")
print("Tables Bronze migrées !")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 3. Migrer les tables Silver et Gold

# COMMAND ----------

spark.sql("""
    CREATE TABLE IF NOT EXISTS water_quality.silver.qualite_eau
    AS SELECT * FROM workspace.default.silver_qualite_eau
""")
print("Table Silver migrée !")

tables_gold = {
    "fact_analyses": "gold_fact_analyses",
    "dim_parametre": "gold_dim_parametre",
    "dim_departement": "gold_dim_departement",
    "dim_unite": "gold_dim_unite",
    "dim_prelevement": "gold_dim_prelevement",
    "dim_commune": "gold_dim_commune",
}

for new_name, old_name in tables_gold.items():
    spark.sql(f"""
        CREATE TABLE IF NOT EXISTS water_quality.gold.{new_name}
        AS SELECT * FROM workspace.default.{old_name}
    """)
    print(f"gold.{new_name} migrée !")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 4. Documentation des tables

# COMMAND ----------

spark.sql("COMMENT ON TABLE water_quality.bronze.qualite_eau IS 'Données brutes : 12.6M résultats analyses qualité eau France 2024'")
spark.sql("COMMENT ON TABLE water_quality.bronze.prelevements IS 'Données brutes : 408K prélèvements avec dates et communes'")
spark.sql("COMMENT ON TABLE water_quality.bronze.communes IS 'Données brutes : 49K correspondances communes/réseaux'")
spark.sql("COMMENT ON TABLE water_quality.silver.qualite_eau IS 'Données nettoyées : 12.6M analyses avec dates, communes, catégories et conformité'")
spark.sql("COMMENT ON TABLE water_quality.gold.fact_analyses IS 'Table de faits : 12.6M résultats avec clés vers les 5 dimensions'")
spark.sql("COMMENT ON TABLE water_quality.gold.dim_parametre IS 'Dimension : 1386 paramètres avec catégorie et niveau de danger'")
spark.sql("COMMENT ON TABLE water_quality.gold.dim_departement IS 'Dimension : 101 départements avec noms, régions et taux conformité'")
spark.sql("COMMENT ON TABLE water_quality.gold.dim_prelevement IS 'Dimension : 291K prélèvements avec dates et conformité officielle'")
spark.sql("COMMENT ON TABLE water_quality.gold.dim_commune IS 'Dimension : 34K communes avec codes INSEE et réseaux'")
spark.sql("COMMENT ON TABLE water_quality.gold.dim_unite IS 'Dimension : 45 unités de mesure'")

print("Descriptions ajoutées !")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 5. Vérification

# COMMAND ----------

for schema in ["bronze", "silver", "gold"]:
    tables = spark.sql(f"SHOW TABLES IN water_quality.{schema}").collect()
    print(f"\n{schema.upper()} ({len(tables)} tables) :")
    for t in tables:
        count = spark.table(f"water_quality.{schema}.{t.tableName}").count()
        print(f"  - {t.tableName} : {count:,} lignes")