# Databricks notebook source
# MAGIC %md
# MAGIC # 04 - Contrôle qualité avec Great Expectations
# MAGIC Validation de la qualité des données à chaque couche.

# COMMAND ----------

# MAGIC %md
# MAGIC ## 1. Installation de Great Expectations

# COMMAND ----------

# MAGIC %pip install great_expectations==0.18.8

# COMMAND ----------

import great_expectations as gx
from great_expectations.dataset import SparkDFDataset

# COMMAND ----------

# MAGIC %md
# MAGIC ## 2. Validation de la couche Bronze

# COMMAND ----------

df_bronze = spark.table("bronze_qualite_eau")
ge_bronze = SparkDFDataset(df_bronze)

print("=== VALIDATION BRONZE ===\n")

# Vérifier que la table n'est pas vide
result = ge_bronze.expect_table_row_count_to_be_between(min_value=10000000, max_value=20000000)
print(f"Nombre de lignes entre 10M et 20M : {'PASS' if result.success else 'FAIL'}")

# Vérifier les colonnes obligatoires
for col_name in ["cddept", "referenceprel", "cdparametresiseeaux", "rqana", "valtraduite"]:
    result = ge_bronze.expect_column_to_exist(col_name)
    print(f"Colonne '{col_name}' existe : {'PASS' if result.success else 'FAIL'}")

# Vérifier qu'il n'y a pas de null sur les colonnes clés
for col_name in ["cddept", "referenceprel"]:
    result = ge_bronze.expect_column_values_to_not_be_null(col_name)
    print(f"'{col_name}' non null : {'PASS' if result.success else 'FAIL'}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 3. Validation de la couche Silver

# COMMAND ----------

df_silver = spark.table("silver_qualite_eau")
ge_silver = SparkDFDataset(df_silver)

print("=== VALIDATION SILVER ===\n")

# Nombre de lignes cohérent avec Bronze
result = ge_silver.expect_table_row_count_to_be_between(min_value=10000000, max_value=15000000)
print(f"Nombre de lignes [10M-15M] : {'PASS' if result.success else 'FAIL'}")

# Colonnes enrichies existent
for col_name in ["categorie_parametre", "est_conforme", "niveau_danger",
                 "date_prelevement", "commune", "code_departement"]:
    result = ge_silver.expect_column_to_exist(col_name)
    print(f"Colonne '{col_name}' existe : {'PASS' if result.success else 'FAIL'}")

# Pas de null sur les colonnes clés
for col_name in ["code_departement", "referenceprel", "date_prelevement"]:
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

# Valeurs numériques >= 0
result = ge_silver.expect_column_values_to_be_between(
    "valtraduite", min_value=0, max_value=None,
    mostly=0.99  # 99% des valeurs
)
print(f"Valeurs >= 0 (99%) : {'PASS' if result.success else 'FAIL'}")

# Nombre de départements
from pyspark.sql.functions import col, countDistinct
nb_dept = df_silver.select(countDistinct("code_departement")).first()[0]
assert nb_dept >= 95, f"Seulement {nb_dept} départements"
print(f"Départements >= 95 : PASS ({nb_dept})")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 4. Validation de la couche Gold

# COMMAND ----------

print("=== VALIDATION GOLD ===\n")

# Fact table
df_fact = spark.table("gold_fact_analyses")
ge_fact = SparkDFDataset(df_fact)

result = ge_fact.expect_table_row_count_to_equal(df_silver.count())
print(f"Fact = Silver count : {'PASS' if result.success else 'FAIL'}")

for col_name in ["analyse_id", "reference_prel", "departement_code",
                 "parametre_code", "date_prelevement", "est_conforme"]:
    result = ge_fact.expect_column_to_exist(col_name)
    print(f"Colonne '{col_name}' existe : {'PASS' if result.success else 'FAIL'}")

# Dimensions
dims = {
    "gold_dim_parametre": ("cdparametresiseeaux", 1000),
    "gold_dim_departement": ("code_departement", 90),
    "gold_dim_unite": ("cdunitereference", 10),
    "gold_dim_prelevement": ("referenceprel", 100000),
    "gold_dim_commune": ("code_insee", 30000),
}

for table, (pk, min_rows) in dims.items():
    df = spark.table(table)
    ge_df = SparkDFDataset(df)

    count = df.count()
    result_count = count >= min_rows
    print(f"\n{table} :")
    print(f"  Lignes >= {min_rows} : {'PASS' if result_count else 'FAIL'} ({count:,})")

    result = ge_df.expect_column_values_to_be_unique(pk)
    print(f"  PK '{pk}' unique : {'PASS' if result.success else 'FAIL'}")

# Taux conformité dans [0, 100]
df_dept = spark.table("gold_dim_departement")
ge_dept = SparkDFDataset(df_dept)
result = ge_dept.expect_column_values_to_be_between("taux_conformite", min_value=0, max_value=100)
print(f"\nTaux conformité [0-100] : {'PASS' if result.success else 'FAIL'}")

# Dates dans la bonne plage
df_prel = spark.table("gold_dim_prelevement")
ge_prel = SparkDFDataset(df_prel)
result = ge_prel.expect_column_values_to_be_between(
    "date_prelevement", min_value="2024-01-01", max_value="2024-12-31"
)
print(f"Dates dans 2024 : {'PASS' if result.success else 'FAIL'}")

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
  Gold   : cohérence fact/silver, dimensions, unicité PK, plages
""")
