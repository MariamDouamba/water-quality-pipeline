# Databricks notebook source
# MAGIC %md
# MAGIC # 03 - Agrégations Gold (Modèle en étoile)
# MAGIC Création des tables de faits et 6 dimensions pour l'analyse.
# MAGIC
# MAGIC Tables créées :
# MAGIC - fact_analyses : table de faits (12.6M lignes)
# MAGIC - dim_parametre : 1 386 paramètres
# MAGIC - dim_departement : 101 départements avec noms et régions
# MAGIC - dim_unite : 45 unités de mesure
# MAGIC - dim_prelevement : 291K prélèvements avec dates et communes
# MAGIC - dim_commune : 34K communes avec réseaux

# COMMAND ----------

from pyspark.sql.functions import (
    col, count, sum as spark_sum, avg, round as spark_round,
    when, desc, monotonically_increasing_id,
    countDistinct, first, lit
)
from pyspark.sql import Row

# COMMAND ----------

# MAGIC %md
# MAGIC ## 1. Chargement Silver

# COMMAND ----------

df_silver = spark.table("silver_qualite_eau")
print(f"Silver chargé : {df_silver.count():,} lignes")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 2. Dimension : dim_parametre

# COMMAND ----------

dim_parametre = df_silver \
    .groupBy("cdparametresiseeaux") \
    .agg(
        first("cdparametre").alias("cdparametre"),
        first("libminparametre").alias("libelle_parametre"),
        first("categorie_parametre").alias("categorie_parametre"),
        first("niveau_danger").alias("niveau_danger"),
        first("cdunitereferencesiseeaux").alias("unite_libelle"),
        first("cdunitereference").alias("unite_code"),
        first("limitequal").alias("limite_qualite"),
        first("refqual").alias("reference_qualite"),
        first("casparam").alias("cas_number"),
        first("qualitparam").alias("type_parametre")
    ) \
    .withColumn("type_parametre",
        when(col("type_parametre") == "O", "Organoleptique")
        .when(col("type_parametre") == "N", "Numérique")
        .otherwise("Autre")
    )

nb_params = dim_parametre.count()
print(f"{nb_params} paramètres")
dim_parametre.groupBy("categorie_parametre").count().orderBy(desc("count")).show()

dim_parametre.write.format("delta").mode("overwrite") \
    .option("overwriteSchema", "true").saveAsTable("gold_dim_parametre")
print("gold_dim_parametre sauvegardée !")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 3. Dimension : dim_departement

# COMMAND ----------

dept_data = [
    ("001","Ain","Auvergne-Rhône-Alpes"),("002","Aisne","Hauts-de-France"),
    ("003","Allier","Auvergne-Rhône-Alpes"),("004","Alpes-de-Haute-Provence","Provence-Alpes-Côte d'Azur"),
    ("005","Hautes-Alpes","Provence-Alpes-Côte d'Azur"),("006","Alpes-Maritimes","Provence-Alpes-Côte d'Azur"),
    ("007","Ardèche","Auvergne-Rhône-Alpes"),("008","Ardennes","Grand Est"),
    ("009","Ariège","Occitanie"),("010","Aube","Grand Est"),
    ("011","Aude","Occitanie"),("012","Aveyron","Occitanie"),
    ("013","Bouches-du-Rhône","Provence-Alpes-Côte d'Azur"),("014","Calvados","Normandie"),
    ("015","Cantal","Auvergne-Rhône-Alpes"),("016","Charente","Nouvelle-Aquitaine"),
    ("017","Charente-Maritime","Nouvelle-Aquitaine"),("018","Cher","Centre-Val de Loire"),
    ("019","Corrèze","Nouvelle-Aquitaine"),("021","Côte-d'Or","Bourgogne-Franche-Comté"),
    ("022","Côtes-d'Armor","Bretagne"),("023","Creuse","Nouvelle-Aquitaine"),
    ("024","Dordogne","Nouvelle-Aquitaine"),("025","Doubs","Bourgogne-Franche-Comté"),
    ("026","Drôme","Auvergne-Rhône-Alpes"),("027","Eure","Normandie"),
    ("028","Eure-et-Loir","Centre-Val de Loire"),("029","Finistère","Bretagne"),
    ("030","Gard","Occitanie"),("031","Haute-Garonne","Occitanie"),
    ("032","Gers","Occitanie"),("033","Gironde","Nouvelle-Aquitaine"),
    ("034","Hérault","Occitanie"),("035","Ille-et-Vilaine","Bretagne"),
    ("036","Indre","Centre-Val de Loire"),("037","Indre-et-Loire","Centre-Val de Loire"),
    ("038","Isère","Auvergne-Rhône-Alpes"),("039","Jura","Bourgogne-Franche-Comté"),
    ("040","Landes","Nouvelle-Aquitaine"),("041","Loir-et-Cher","Centre-Val de Loire"),
    ("042","Loire","Auvergne-Rhône-Alpes"),("043","Haute-Loire","Auvergne-Rhône-Alpes"),
    ("044","Loire-Atlantique","Pays de la Loire"),("045","Loiret","Centre-Val de Loire"),
    ("046","Lot","Occitanie"),("047","Lot-et-Garonne","Nouvelle-Aquitaine"),
    ("048","Lozère","Occitanie"),("049","Maine-et-Loire","Pays de la Loire"),
    ("050","Manche","Normandie"),("051","Marne","Grand Est"),
    ("052","Haute-Marne","Grand Est"),("053","Mayenne","Pays de la Loire"),
    ("054","Meurthe-et-Moselle","Grand Est"),("055","Meuse","Grand Est"),
    ("056","Morbihan","Bretagne"),("057","Moselle","Grand Est"),
    ("058","Nièvre","Bourgogne-Franche-Comté"),("059","Nord","Hauts-de-France"),
    ("060","Oise","Hauts-de-France"),("061","Orne","Normandie"),
    ("062","Pas-de-Calais","Hauts-de-France"),("063","Puy-de-Dôme","Auvergne-Rhône-Alpes"),
    ("064","Pyrénées-Atlantiques","Nouvelle-Aquitaine"),("065","Hautes-Pyrénées","Occitanie"),
    ("066","Pyrénées-Orientales","Occitanie"),("067","Bas-Rhin","Grand Est"),
    ("068","Haut-Rhin","Grand Est"),("069","Rhône","Auvergne-Rhône-Alpes"),
    ("070","Haute-Saône","Bourgogne-Franche-Comté"),("071","Saône-et-Loire","Bourgogne-Franche-Comté"),
    ("072","Sarthe","Pays de la Loire"),("073","Savoie","Auvergne-Rhône-Alpes"),
    ("074","Haute-Savoie","Auvergne-Rhône-Alpes"),("075","Paris","Île-de-France"),
    ("076","Seine-Maritime","Normandie"),("077","Seine-et-Marne","Île-de-France"),
    ("078","Yvelines","Île-de-France"),("079","Deux-Sèvres","Nouvelle-Aquitaine"),
    ("080","Somme","Hauts-de-France"),("081","Tarn","Occitanie"),
    ("082","Tarn-et-Garonne","Occitanie"),("083","Var","Provence-Alpes-Côte d'Azur"),
    ("084","Vaucluse","Provence-Alpes-Côte d'Azur"),("085","Vendée","Pays de la Loire"),
    ("086","Vienne","Nouvelle-Aquitaine"),("087","Haute-Vienne","Nouvelle-Aquitaine"),
    ("088","Vosges","Grand Est"),("089","Yonne","Bourgogne-Franche-Comté"),
    ("090","Territoire de Belfort","Bourgogne-Franche-Comté"),
    ("091","Essonne","Île-de-France"),("092","Hauts-de-Seine","Île-de-France"),
    ("093","Seine-Saint-Denis","Île-de-France"),("094","Val-de-Marne","Île-de-France"),
    ("095","Val-d'Oise","Île-de-France"),
    ("971","Guadeloupe","Guadeloupe"),("972","Martinique","Martinique"),
    ("973","Guyane","Guyane"),("974","La Réunion","La Réunion"),
    ("976","Mayotte","Mayotte"),
    ("02A","Corse-du-Sud","Corse"),("02B","Haute-Corse","Corse")
]

df_dept_ref = spark.createDataFrame(
    [Row(code_departement=d[0], nom_departement=d[1], region=d[2]) for d in dept_data]
)

dim_departement = df_silver.groupBy("code_departement").agg(
    count("*").alias("nb_analyses"),
    countDistinct("referenceprel").alias("nb_prelevements"),
    countDistinct("commune").alias("nb_communes"),
    spark_sum(when(col("est_conforme") == "Conforme", 1).otherwise(0)).alias("nb_conformes"),
    spark_sum(when(col("est_conforme") == "Non conforme", 1).otherwise(0)).alias("nb_non_conformes")
).join(df_dept_ref, "code_departement", "left") \
.withColumn("taux_conformite",
    spark_round(col("nb_conformes") / (col("nb_conformes") + col("nb_non_conformes")) * 100, 2)
).select("code_departement", "nom_departement", "region",
         "nb_analyses", "nb_prelevements", "nb_communes",
         "nb_conformes", "nb_non_conformes", "taux_conformite")

print(f"{dim_departement.count()} départements")
dim_departement.orderBy("taux_conformite").show(5, truncate=False)

dim_departement.write.format("delta").mode("overwrite") \
    .option("overwriteSchema", "true").saveAsTable("gold_dim_departement")
print("gold_dim_departement sauvegardée !")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 4. Dimension : dim_unite

# COMMAND ----------

dim_unite = df_silver.groupBy("cdunitereference").agg(
    first("cdunitereferencesiseeaux").alias("libelle_unite"),
    count("*").alias("nb_utilisations")
)
print(f"{dim_unite.count()} unités")

dim_unite.write.format("delta").mode("overwrite") \
    .option("overwriteSchema", "true").saveAsTable("gold_dim_unite")
print("gold_dim_unite sauvegardée !")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 5. Dimension : dim_prelevement (enrichie)

# COMMAND ----------

dim_prelevement = df_silver.groupBy("referenceprel").agg(
    first("code_departement").alias("departement_code"),
    first("date_prelevement").alias("date_prelevement"),
    first("heure_prelevement").alias("heure_prelevement"),
    first("commune").alias("commune"),
    first("code_insee").alias("code_insee"),
    first("code_reseau").alias("code_reseau"),
    first("conclusion_prelevement").alias("conclusion_prelevement"),
    first("conformite_bacterio").alias("conformite_bacterio"),
    first("conformite_chimique").alias("conformite_chimique"),
    count("*").alias("nb_analyses"),
    countDistinct("cdparametresiseeaux").alias("nb_params_testes"),
    spark_sum(when(col("est_conforme") == "Conforme", 1).otherwise(0)).alias("nb_conformes"),
    spark_sum(when(col("est_conforme") == "Non conforme", 1).otherwise(0)).alias("nb_non_conformes")
).withColumn("prelevement_conforme",
    when(col("nb_non_conformes") == 0, "Conforme").otherwise("Non conforme")
)

nb_prel = dim_prelevement.count()
print(f"{nb_prel:,} prélèvements")
dim_prelevement.selectExpr("min(date_prelevement) as min", "max(date_prelevement) as max").show()
dim_prelevement.groupBy("prelevement_conforme").count().orderBy(desc("count")).show()

dim_prelevement.write.format("delta").mode("overwrite") \
    .option("overwriteSchema", "true").saveAsTable("gold_dim_prelevement")
print("gold_dim_prelevement sauvegardée !")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 6. Dimension : dim_commune

# COMMAND ----------

df_com = spark.table("bronze_communes")

dim_commune = df_com.select(
    col("inseecommune").alias("code_insee"),
    col("nomcommune").alias("nom_commune"),
    col("cdreseau").alias("code_reseau"),
    col("nomreseau").alias("nom_reseau")
).dropDuplicates(["code_insee"]) \
.withColumn("nom_commune",
    when(col("nom_commune") == "nan", None).otherwise(col("nom_commune"))
)

nb_com = dim_commune.count()
print(f"{nb_com:,} communes")
dim_commune.show(5, truncate=False)

dim_commune.write.format("delta").mode("overwrite") \
    .option("overwriteSchema", "true").saveAsTable("gold_dim_commune")
print("gold_dim_commune sauvegardée !")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 7. Table de faits : fact_analyses

# COMMAND ----------

fact_analyses = df_silver.select(
    monotonically_increasing_id().alias("analyse_id"),
    col("referenceprel").alias("reference_prel"),
    col("referenceanl").alias("reference_analyse"),
    col("code_departement").alias("departement_code"),
    col("cdparametresiseeaux").alias("parametre_code"),
    col("cdunitereference").alias("unite_code"),
    col("date_prelevement"),
    col("commune"),
    col("type_analyse"),
    col("rqana").alias("resultat_brut"),
    col("valtraduite").alias("valeur_numerique"),
    col("limite_numerique"),
    col("est_conforme"),
    col("_year").alias("annee")
)

nb_faits = fact_analyses.count()
print(f"{nb_faits:,} lignes")
fact_analyses.show(5, truncate=25)

fact_analyses.write.format("delta").mode("overwrite") \
    .option("overwriteSchema", "true").saveAsTable("gold_fact_analyses")
print("gold_fact_analyses sauvegardée !")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 8. Résumé

# COMMAND ----------

print("=" * 60)
print("MODÈLE EN ÉTOILE COMPLET !")
print("=" * 60)
print(f"""
Tables créées :
   - gold_fact_analyses     : {nb_faits:,} lignes
   - gold_dim_parametre     : {nb_params} paramètres
   - gold_dim_departement   : {dim_departement.count()} départements
   - gold_dim_unite         : {dim_unite.count()} unités
   - gold_dim_prelevement   : {nb_prel:,} prélèvements
   - gold_dim_commune       : {nb_com:,} communes
""")
