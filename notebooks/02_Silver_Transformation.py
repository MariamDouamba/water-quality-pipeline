# Databricks notebook source
# MAGIC %md
# MAGIC # 02 - Transformations Silver
# MAGIC Nettoyage, correction d'encodage, enrichissement et classification
# MAGIC des données de qualité de l'eau.

# COMMAND ----------

from pyspark.sql.functions import (
    col, trim, when, regexp_replace, regexp_extract,
    current_timestamp, lit, lower, count, desc
)
from pyspark.sql.types import DoubleType, IntegerType

# COMMAND ----------

# MAGIC %md
# MAGIC ## 1. Chargement des données Bronze

# COMMAND ----------

df = spark.table("bronze_qualite_eau")
print(f"Bronze chargé : {df.count():,} lignes, {len(df.columns)} colonnes")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 2. Nettoyage de base

# COMMAND ----------

# Supprimer la colonne inutile (100% null)
df = df.drop("libwebparametre")

# Remplacer les "NULL" texte par de vrais null
for c in df.columns:
    if not c.startswith("_"):
        df = df.withColumn(c, when(col(c) == "NULL", None).otherwise(col(c)))

# Nettoyer les espaces
for c in df.columns:
    if not c.startswith("_"):
        df = df.withColumn(c, trim(col(c)))

# Convertir les types
df = df.withColumn("valtraduite", col("valtraduite").cast(DoubleType()))
df = df.withColumn("cdparametre", col("cdparametre").cast(IntegerType()))

# Supprimer les doublons
nb_avant = df.count()
df = df.dropDuplicates()
nb_apres = df.count()
print(f"Doublons supprimés : {nb_avant - nb_apres:,}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 3. Correction de l'encodage

# COMMAND ----------

colonnes_texte = ["libmajparametre", "libminparametre", "rqana",
                  "cdunitereferencesiseeaux", "limitequal", "refqual"]

corrections = {
    "Ã©": "é", "Ã¨": "è", "Ãª": "ê", "Ã ": "à",
    "Ã¢": "â", "Ã®": "î", "Ã´": "ô", "Ã¹": "ù",
    "Ã»": "û", "Ã§": "ç", "Ã‰": "É", "Ã€": "À",
    "Ã": "À", "Âµ": "µ", "Â°": "°", "Â²": "²",
}

for colonne in colonnes_texte:
    for mauvais, bon in corrections.items():
        df = df.withColumn(colonne, regexp_replace(col(colonne), mauvais, bon))

# Correction du caractère À + espace insécable
for colonne in ["libmajparametre", "libminparametre", "rqana"]:
    df = df.withColumn(colonne,
        regexp_replace(col(colonne), u"\u00c0\u00a0 ", u"\u00e0 "))
    df = df.withColumn(colonne,
        regexp_replace(col(colonne), u"\u00c0\u00a0", u"\u00e0 "))

# COMMAND ----------

# MAGIC %md
# MAGIC ## 4. Enrichissement : catégories et conformité

# COMMAND ----------

# ---- Catégorisation des paramètres ----
micro = ["CTF", "ECOLI", "ENTERO", "GT22_68", "GT36_44",
         "COLIF", "STPHY", "PSAR", "SPCLOS", "STRF", "BSIR",
         "GT22_72", "GT36_48", "LEGPN", "LEGSP"]

pesticides = [
    "ATRZ", "ATZ", "ADET", "ADSP", "A2H", "SMZ", "SIMZ", "SHYD",
    "TBZ", "TBZDES", "TBZH", "MTBZ",
    "MTC", "METOL", "MTCESA", "MTCOA", "METZCL",
    "LNCE", "LNDI", "CLRTOL", "ISOPR", "DIURO",
    "ALDRI", "DIELDR", "DDT", "HCH", "CLRDC", "HEP", "HEPET", "LNDN",
    "GLPHOS", "AMPA",
    "BFNX", "BOSCALI", "CNPA", "DMTE", "FLUMIOX", "METIL", "PPTP",
    "PENOXU", "SULFRN", "MTMI", "FLONIC",
    "CLMQT", "MEPIQT", "PROPZN", "ASULAME", "PESTOT"
]

organo = ["ASP", "COULQ", "SAVQ", "ODEQ", "TURBI",
          "TURBNFU", "ODQ", "COULF", "ODEUR25", "SAV25", "COULR"]

physico = ["PH", "COND", "TEMP", "TAC", "TH", "O2DIS",
           "CDT25", "TEAU", "TAIR", "TEMP_PH",
           "TA", "CO3", "HCO3", "CALCOC2", "COT", "OXYD"]

desinfection = ["CL2LIB", "CL2TOT", "CL2COMB", "CLO2",
                "THM4", "CLF", "BRF", "DCLMBR", "DBRMCL",
                "CLVYL", "ACRYL", "EPICL", "BRATE"]

nitrates = ["NO3", "NO2", "NH4", "NO3_NO2"]

metaux = ["PBT", "ALTMICR", "CUTMICR", "FET", "CRTOTR",
          "MNMICR", "NIMICR", "ASTMICR", "BMG", "CDMICR",
          "MN", "CA", "MG", "K", "NA",
          "SETMICR", "SBMICR", "BATMICR", "HGMICR", "ALTOT", "ZN"]

chimie_minerale = ["SO4", "CL", "FLUOR", "SIO2", "DUR"]

df = df.withColumn("categorie_parametre",
    when(col("cdparametresiseeaux").isin(micro), "Microbiologie")
    .when(col("cdparametresiseeaux").isin(pesticides), "Pesticides")
    .when(col("cdparametresiseeaux").isin(organo), "Organoleptique")
    .when(col("cdparametresiseeaux").isin(physico), "Physico-chimique")
    .when(col("cdparametresiseeaux").isin(desinfection), "Désinfection")
    .when(col("cdparametresiseeaux").isin(nitrates), "Nitrates/Nitrites")
    .when(col("cdparametresiseeaux").isin(metaux), "Métaux et minéraux")
    .when(col("cdparametresiseeaux").isin(chimie_minerale), "Chimie minérale")
    .otherwise("Autre")
)

# Classification automatique des "Autre" par libellé et unité
df = df.withColumn("categorie_parametre",
    when(col("categorie_parametre") != "Autre", col("categorie_parametre"))
    .when((col("cdunitereferencesiseeaux") == "µg/L") &
          (col("limitequal").contains("0,1")), "Pesticides")
    .when(lower(col("libminparametre")).rlike(
        "arsenic|sodium|sélénium|antimoine|baryum|mercure|chrome|nickel|zinc|"
        "cuivre|plomb|cadmium|aluminium|fer |manganèse|bore |strontium|vanadium|cobalt|"
        "uranium|molybdène|thallium|étain"), "Métaux et minéraux")
    .when(lower(col("libminparametre")).rlike(
        "trihalomé|chloroforme|bromoforme|chlorite|chlorate|bromate|chloramine"), "Désinfection")
    .when(lower(col("libminparametre")).rlike(
        "bactéri|coliform|entéro|escherichia|spore|légionell|crypto|giardia|virus"), "Microbiologie")
    .when(lower(col("libminparametre")).rlike(
        "odeur|saveur|couleur|aspect|turbid|coloration|goût"), "Organoleptique")
    .when(lower(col("libminparametre")).rlike(
        "conductiv|tempéra|oxygène|carbone organ|oxydabil"), "Physico-chimique")
    .when(lower(col("libminparametre")).rlike(
        "sulfate|fluorur|silice|dureté|phosph|cyanur"), "Chimie minérale")
    .when(lower(col("libminparametre")).rlike(
        "nitrate|nitrite|ammonium"), "Nitrates/Nitrites")
    .when(lower(col("libminparametre")).rlike(
        "activité|tritium|dose indicative|radon|radium|alpha glob|béta glob|bêta"), "Radioactivité")
    .when(col("cdunitereferencesiseeaux").isin("Bq/L", "mSv/a"), "Radioactivité")
    .when(lower(col("libminparametre")).rlike(
        "ph d|pluviomé|anhydride|co2|équilibre calco|résidu"), "Physico-chimique")
    .when(lower(col("libminparametre")).rlike(
        "accréditation|prélèvement sous|acréditation"), "Métadonnée")
    .when(col("cdunitereferencesiseeaux") == "µg/L", "Pesticides")
    .otherwise("Autre")
)

# COMMAND ----------

# MAGIC %md
# MAGIC ## 5. Conformité et niveau de danger

# COMMAND ----------

# ---- Type d'analyse et département ----
df = df.withColumn("type_analyse",
    when(col("insituana") == "L", "Laboratoire")
    .when(col("insituana") == "T", "Terrain")
    .otherwise("Autre")
)
df = df.withColumn("code_departement", col("cddept"))

# ---- Conformité ----
df = df.withColumn("limite_numerique",
    regexp_extract(col("limitequal"), "(\\d+[\\.,]?\\d*)", 1)
).withColumn("limite_numerique",
    regexp_replace(col("limite_numerique"), ",", ".").cast("double")
)

df = df.withColumn("est_conforme",
    when(col("rqana").startswith("<"), "Conforme")
    .when(col("rqana").isin("Aspect normal", "Aucun changement anormal",
                             "Saveur normale", "Inodore"), "Conforme")
    .when(col("rqana") == "0", "Conforme")
    .when((col("limite_numerique").isNotNull()) & (col("valtraduite").isNotNull()) &
          (col("valtraduite") <= col("limite_numerique")), "Conforme")
    .when((col("limite_numerique").isNotNull()) & (col("valtraduite").isNotNull()) &
          (col("valtraduite") > col("limite_numerique")), "Non conforme")
    .otherwise("Non évalué")
)

# ---- Niveau de danger ----
sanitaire_critique = ["ECOLI", "ENTERO", "CTF", "COLIF", "STRF",
                      "BSIR", "SPCLOS", "PSAR", "LEGPN", "LEGSP"]
sanitaire = ["NO3", "NO2", "NH4", "NO3_NO2",
             "PBT", "ASTMICR", "CDMICR", "CRTOTR", "HGMICR",
             "ATRZ", "ATZ", "SIMZ", "SMZ", "GLPHOS", "AMPA",
             "ALDRI", "DIELDR", "DDT", "HCH", "CLRDC",
             "BRATE", "CLVYL", "ACRYL", "EPICL", "PESTOT", "THM4"]
organo_danger = ["ASP", "COULQ", "SAVQ", "ODEQ", "TURBI",
                 "TURBNFU", "ODQ", "COULF", "ODEUR25", "SAV25"]

df = df.withColumn("niveau_danger",
    when(col("cdparametresiseeaux").isin(sanitaire_critique), "Sanitaire critique")
    .when(col("cdparametresiseeaux").isin(sanitaire), "Sanitaire")
    .when(col("cdparametresiseeaux").isin(organo_danger), "Organoleptique")
    .otherwise("Surveillance")
)

# Enrichir niveau_danger pour les classifications automatiques
df = df.withColumn("niveau_danger",
    when(col("niveau_danger") != "Surveillance", col("niveau_danger"))
    .when(lower(col("libminparametre")).rlike(
        "escherichia|entéro|coliform|légionell|crypto|giardia|virus"), "Sanitaire critique")
    .when(lower(col("libminparametre")).rlike(
        "arsenic|plomb|mercure|cadmium|chrome|nitrate|nitrite|pesticide|cyanur"), "Sanitaire")
    .when(col("categorie_parametre") == "Pesticides", "Sanitaire")
    .when(col("categorie_parametre") == "Radioactivité", "Sanitaire")
    .when(col("categorie_parametre") == "Organoleptique", "Organoleptique")
    .otherwise("Surveillance")
)

# COMMAND ----------

# MAGIC %md
# MAGIC ## 6. Sauvegarde de la table Silver

# COMMAND ----------

# Vérifications
print("Distribution des catégories :")
df.groupBy("categorie_parametre").count().orderBy(desc("count")).show()

print("Distribution des niveaux de danger :")
df.groupBy("niveau_danger").count().orderBy(desc("count")).show()

print("Distribution de la conformité :")
df.groupBy("est_conforme").count().orderBy(desc("count")).show()

# Sauvegarde
df.write \
    .format("delta") \
    .mode("overwrite") \
    .option("overwriteSchema", "true") \
    .saveAsTable("silver_qualite_eau")

print(f"Table silver_qualite_eau sauvegardée : {df.count():,} lignes, {len(df.columns)} colonnes")
