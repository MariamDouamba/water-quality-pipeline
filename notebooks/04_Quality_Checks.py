# Databricks notebook source
# MAGIC %md
# MAGIC # 04 - Contrôle qualité avec Great Expectations
# MAGIC Validation de la qualité des données à chaque couche.
# MAGIC On utilise PandasDataset avec un échantillon pour la compatibilité Serverless.

# COMMAND ----------

# MAGIC %md
# MAGIC ## 1. Installation de Great Expectations

# COMMAND ----------

# MAGIC %pip install great_expectations==0.18.8

# COMMAND ----------

import great_expectations as gx
from great_expectations.dataset import PandasDataset

# COMMAND ----------

# MAGIC %md
# MAGIC ## 2. Validation de la couche Bronze

# COMMAND ----------

df_bronze = spark.table("bronze_qualite_eau")
ge_bronze = PandasDataset(df_bronze.limit(100000).toPandas())

print("=== VALIDATION BRONZE ===\n")

result = ge_bronze.expect_table_row_count_to_be_between(min_value=50000, max_value=200000)
print(f"Échantillon chargé : {'PASS' if result.success else 'FAIL'}")

for col_name in ["cddept", "referenceprel", "cdparametresiseeaux", "rqana", "valtraduite"]:
    result = ge_bronze.expect_column_to_exist(col_name)
    print(f"Colonne '{col_name}' existe : {'PASS' if result.success else 'FAIL'}")

for col_name in ["cddept", "referenceprel"]:
    result = ge_bronze.expect_column_values_to_not_be_null(col_name)
    print(f"'{col_name}' non null : {'PASS' if result.success else 'FAIL'}")

# Vérifier le nombre total de lignes (sans échantillon)
total = df_bronze.count()
assert total > 10000000, f"Bronze trop petit : {total}"
print(f"\nTotal Bronze : {total:,} lignes - PASS")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 3. Validation de la couche Silver

# COMMAND ----------

df_silver = spark.table("silver_qualite_eau")
ge_silver = PandasDataset(df_silver.limit(100000).toPandas())

print("=== VALIDATION SILVER ===\n")

# Colonnes enrichies existent
for col_name in ["categorie_parametre", "est_conforme", "niveau_danger",
                 "date_prelevement", "commune", "code_departement"]:
    result = ge_silver.expect_column_to_exist(col_name)
    print(f"Colonne '{col_name}' existe : {'PASS' if result.success else 'FAIL'}")

# Pas de null sur les colonnes clés
for col_name in ["code_departement", "referenceprel"]:
    result = ge_silver.expect_column_values_to_not_be_null(col_name)
    print(f"'{col_name}' non null : {'PASS' if result.success else 'FAIL'}")

# Valeurs attendues pour categorie_parametre
result = ge_silver.expect_column_values_to_be_in_set(
    "categorie_parametre",
    ["Microbiologie", "Pesticides", "Organoleptique", "Physico-chimique",
     "Désinfection", "Nitrates/Nitrites", "Métaux et minéraux",
     "Chimie minérale", "Radioactivité", "Métadonnée", "Autre"]
)
print(f"Catégories valides : {'PASS' if result.success else 'FAIL'}")

# Valeurs attendues pour est_conforme
result = ge_silver.expect_column_values_to_be_in_set(
    "est_conforme",
    ["Conforme", "Non conforme", "Non évalué"]
)
print(f"Conformité valide : {'PASS' if result.success else 'FAIL'}")

# Valeurs attendues pour niveau_danger
result = ge_silver.expect_column_values_to_be_in_set(
    "niveau_danger",
    ["Sanitaire critique", "Sanitaire", "Organoleptique", "Surveillance"]
)
print(f"Niveaux danger valides : {'PASS' if result.success else 'FAIL'}")

# Nombre total
total_silver = df_silver.count()
print(f"\nTotal Silver : {total_silver:,} lignes")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 4. Validation de la couche Gold

# COMMAND ----------

print("=== VALIDATION GOLD ===\n")

# Fact table
df_fact = spark.table("gold_fact_analyses")
ge_fact = PandasDataset(df_fact.limit(100000).toPandas())

for col_name in ["analyse_id", "reference_prel", "departement_code",
                 "parametre_code", "date_prelevement", "est_conforme"]:
    result = ge_fact.expect_column_to_exist(col_name)
    print(f"Fact '{col_name}' existe : {'PASS' if result.success else 'FAIL'}")

# Vérifier cohérence fact = silver
fact_count = df_fact.count()
silver_count = df_silver.count()
match = fact_count == silver_count
print(f"\nFact ({fact_count:,}) = Silver ({silver_count:,}) : {'PASS' if match else 'FAIL'}")

# Dimensions
dims = {
    "gold_dim_parametre": 1000,
    "gold_dim_departement": 90,
    "gold_dim_unite": 10,
    "gold_dim_prelevement": 100000,
    "gold_dim_commune": 30000,
}

print("\nDimensions :")
for table, min_rows in dims.items():
    count = spark.table(table).count()
    status = "PASS" if count >= min_rows else "FAIL"
    print(f"  {table} : {count:,} lignes - {status}")

# Taux conformité dans [0, 100]
from pyspark.sql.functions import col
df_dept = spark.table("gold_dim_departement")
hors_range = df_dept.filter(
    (col("taux_conformite") < 0) | (col("taux_conformite") > 100)
).count()
print(f"\nTaux conformité [0-100] : {'PASS' if hors_range == 0 else 'FAIL'}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 5. Résumé

# COMMAND ----------

print("=" * 60)
print("CONTRÔLE QUALITÉ TERMINÉ")
print("=" * 60)
print("""
Validations effectuées :
  Bronze : existence, colonnes, non-nullité
  Silver : enrichissement, catégories, conformité, dates
  Gold   : cohérence fact/silver, dimensions, plages
""")