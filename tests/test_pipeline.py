"""
Tests unitaires pour le pipeline de qualité de l'eau.
Ces tests vérifient l'intégrité des données à chaque couche.
Exécutables avec pytest ou directement dans Databricks.
"""

import sys
sys.path.append("../config")


def test_bronze_table_exists(spark):
    """Vérifie que la table Bronze existe et contient des données."""
    df = spark.table("bronze_qualite_eau")
    count = df.count()
    assert count > 0, f"La table Bronze est vide (count={count})"
    print(f"✅ Bronze : {count:,} lignes")


def test_bronze_columns(spark):
    """Vérifie que la table Bronze a les colonnes attendues."""
    df = spark.table("bronze_qualite_eau")
    colonnes_requises = [
        "cddept", "referenceprel", "cdparametresiseeaux",
        "cdparametre", "libmajparametre", "libminparametre",
        "qualitparam", "insituana", "rqana",
        "cdunitereferencesiseeaux", "cdunitereference",
        "valtraduite", "_source_file", "_year"
    ]
    colonnes_manquantes = [c for c in colonnes_requises if c not in df.columns]
    assert len(colonnes_manquantes) == 0, f"Colonnes manquantes : {colonnes_manquantes}"
    print(f"✅ Bronze : {len(df.columns)} colonnes présentes")


def test_silver_table_exists(spark):
    """Vérifie que la table Silver existe et contient des données."""
    df = spark.table("silver_qualite_eau")
    count = df.count()
    assert count > 0, f"La table Silver est vide (count={count})"
    print(f"✅ Silver : {count:,} lignes")


def test_silver_no_null_department(spark):
    """Vérifie qu'il n'y a pas de département null dans Silver."""
    from pyspark.sql.functions import col
    df = spark.table("silver_qualite_eau")
    null_count = df.filter(col("code_departement").isNull()).count()
    assert null_count == 0, f"{null_count} lignes avec département null"
    print(f"✅ Silver : aucun département null")


def test_silver_categories_valid(spark):
    """Vérifie que les catégories de paramètres sont valides."""
    from pyspark.sql.functions import col
    df = spark.table("silver_qualite_eau")
    categories_valides = [
        "Microbiologie", "Pesticides", "Organoleptique",
        "Physico-chimique", "Désinfection", "Nitrates/Nitrites",
        "Métaux et minéraux", "Chimie minérale", "Radioactivité",
        "Métadonnée", "Autre"
    ]
    categories_db = [row[0] for row in df.select("categorie_parametre").distinct().collect()]
    invalides = [c for c in categories_db if c not in categories_valides]
    assert len(invalides) == 0, f"Catégories invalides : {invalides}"
    print(f"✅ Silver : {len(categories_db)} catégories valides")


def test_silver_conformite_valid(spark):
    """Vérifie que les valeurs de conformité sont valides."""
    df = spark.table("silver_qualite_eau")
    conformites_valides = ["Conforme", "Non conforme", "Non évalué"]
    conformites_db = [row[0] for row in df.select("est_conforme").distinct().collect()]
    invalides = [c for c in conformites_db if c not in conformites_valides]
    assert len(invalides) == 0, f"Conformités invalides : {invalides}"
    print(f"✅ Silver : conformités valides")


def test_silver_valtraduite_positive(spark):
    """Vérifie que les valeurs numériques sont positives ou nulles."""
    from pyspark.sql.functions import col
    df = spark.table("silver_qualite_eau")
    negatifs = df.filter(col("valtraduite") < 0).count()
    assert negatifs == 0, f"{negatifs} valeurs négatives trouvées"
    print(f"✅ Silver : toutes les valeurs >= 0")


def test_gold_fact_count_matches_silver(spark):
    """Vérifie que la table de faits Gold a le même nombre de lignes que Silver."""
    silver_count = spark.table("silver_qualite_eau").count()
    gold_count = spark.table("gold_fact_analyses").count()
    assert gold_count == silver_count, \
        f"Écart : Silver={silver_count:,}, Gold={gold_count:,}"
    print(f"✅ Gold fact : {gold_count:,} lignes (= Silver)")


def test_gold_dimensions_not_empty(spark):
    """Vérifie que toutes les tables de dimensions contiennent des données."""
    dimensions = {
        "gold_dim_parametre": 1000,
        "gold_dim_departement": 90,
        "gold_dim_unite": 10,
        "gold_dim_prelevement": 100000,
    }
    for table, min_expected in dimensions.items():
        count = spark.table(table).count()
        assert count >= min_expected, \
            f"{table} : {count} lignes (min attendu : {min_expected})"
        print(f"✅ {table} : {count:,} lignes")


def test_gold_departement_has_names(spark):
    """Vérifie que les départements ont des noms."""
    from pyspark.sql.functions import col
    df = spark.table("gold_dim_departement")
    sans_nom = df.filter(col("nom_departement").isNull()).count()
    total = df.count()
    pct = (total - sans_nom) / total * 100
    assert pct >= 90, f"Seulement {pct:.1f}% des départements ont un nom"
    print(f"✅ Gold départements : {pct:.1f}% avec nom")


def test_gold_taux_conformite_range(spark):
    """Vérifie que les taux de conformité sont entre 0 et 100."""
    from pyspark.sql.functions import col
    df = spark.table("gold_dim_departement")
    hors_range = df.filter(
        (col("taux_conformite") < 0) | (col("taux_conformite") > 100)
    ).count()
    assert hors_range == 0, f"{hors_range} départements avec taux hors [0-100]"
    print(f"✅ Gold : taux de conformité dans [0-100]")


# ---- Exécution dans Databricks ----
if __name__ == "__main__":
    tests = [
        test_bronze_table_exists,
        test_bronze_columns,
        test_silver_table_exists,
        test_silver_no_null_department,
        test_silver_categories_valid,
        test_silver_conformite_valid,
        test_silver_valtraduite_positive,
        test_gold_fact_count_matches_silver,
        test_gold_dimensions_not_empty,
        test_gold_departement_has_names,
        test_gold_taux_conformite_range,
    ]
    
    print("=" * 60)
    print("EXÉCUTION DES TESTS")
    print("=" * 60)
    
    passed = 0
    failed = 0
    for test in tests:
        try:
            test(spark)
            passed += 1
        except AssertionError as e:
            print(f"❌ {test.__name__} : {e}")
            failed += 1
        except Exception as e:
            print(f"❌ {test.__name__} : Erreur inattendue - {e}")
            failed += 1
    
    print(f"\n{'=' * 60}")
    print(f"RÉSULTATS : {passed} passés, {failed} échoués")
    print(f"{'=' * 60}")
