"""
Tests unitaires pour le pipeline de qualité de l'eau.
Vérifie l'intégrité des données à chaque couche.
"""


def test_bronze_resultats_exists(spark):
    """Vérifie que la table Bronze résultats existe."""
    df = spark.table("bronze_qualite_eau")
    count = df.count()
    assert count > 0, f"Table vide (count={count})"
    print(f"bronze_qualite_eau : {count:,} lignes")


def test_bronze_prelevements_exists(spark):
    """Vérifie que la table Bronze prélèvements existe."""
    df = spark.table("bronze_prelevements")
    count = df.count()
    assert count > 0, f"Table vide (count={count})"
    print(f"bronze_prelevements : {count:,} lignes")


def test_bronze_communes_exists(spark):
    """Vérifie que la table Bronze communes existe."""
    df = spark.table("bronze_communes")
    count = df.count()
    assert count > 0, f"Table vide (count={count})"
    print(f"bronze_communes : {count:,} lignes")


def test_bronze_columns(spark):
    """Vérifie les colonnes de la table Bronze."""
    df = spark.table("bronze_qualite_eau")
    colonnes_requises = [
        "cddept", "referenceprel", "cdparametresiseeaux",
        "cdparametre", "libmajparametre", "libminparametre",
        "qualitparam", "insituana", "rqana",
        "cdunitereferencesiseeaux", "cdunitereference",
        "valtraduite", "_source_file", "_year"
    ]
    manquantes = [c for c in colonnes_requises if c not in df.columns]
    assert len(manquantes) == 0, f"Colonnes manquantes : {manquantes}"
    print(f"Bronze : {len(df.columns)} colonnes OK")


def test_silver_exists(spark):
    """Vérifie que la table Silver existe."""
    df = spark.table("silver_qualite_eau")
    count = df.count()
    assert count > 0, f"Table vide (count={count})"
    print(f"silver_qualite_eau : {count:,} lignes")


def test_silver_has_dates(spark):
    """Vérifie que Silver contient les dates de prélèvement."""
    from pyspark.sql.functions import col
    df = spark.table("silver_qualite_eau")
    assert "date_prelevement" in df.columns, "Colonne date_prelevement manquante"
    avec_date = df.filter(col("date_prelevement").isNotNull()).count()
    total = df.count()
    pct = avec_date / total * 100
    assert pct > 95, f"Seulement {pct:.1f}% avec date"
    print(f"Silver : {pct:.1f}% avec date")


def test_silver_has_communes(spark):
    """Vérifie que Silver contient les communes."""
    from pyspark.sql.functions import col
    df = spark.table("silver_qualite_eau")
    assert "commune" in df.columns, "Colonne commune manquante"
    avec_commune = df.filter(col("commune").isNotNull()).count()
    total = df.count()
    pct = avec_commune / total * 100
    assert pct > 95, f"Seulement {pct:.1f}% avec commune"
    print(f"Silver : {pct:.1f}% avec commune")


def test_silver_no_null_department(spark):
    """Vérifie qu'il n'y a pas de département null."""
    from pyspark.sql.functions import col
    df = spark.table("silver_qualite_eau")
    null_count = df.filter(col("code_departement").isNull()).count()
    assert null_count == 0, f"{null_count} lignes avec département null"
    print("Silver : aucun département null")


def test_silver_categories_valid(spark):
    """Vérifie les catégories de paramètres."""
    df = spark.table("silver_qualite_eau")
    categories_valides = [
        "Microbiologie", "Pesticides", "Organoleptique",
        "Physico-chimique", "Désinfection", "Nitrates/Nitrites",
        "Métaux et minéraux", "Chimie minérale", "Radioactivité",
        "Métadonnée", "Autre"
    ]
    categories_db = [r[0] for r in df.select("categorie_parametre").distinct().collect()]
    invalides = [c for c in categories_db if c not in categories_valides]
    assert len(invalides) == 0, f"Catégories invalides : {invalides}"
    print(f"Silver : {len(categories_db)} catégories valides")


def test_silver_conformite_valid(spark):
    """Vérifie les valeurs de conformité."""
    df = spark.table("silver_qualite_eau")
    valides = ["Conforme", "Non conforme", "Non évalué"]
    db = [r[0] for r in df.select("est_conforme").distinct().collect()]
    invalides = [c for c in db if c not in valides]
    assert len(invalides) == 0, f"Invalides : {invalides}"
    print("Silver : conformités valides")


def test_gold_fact_count(spark):
    """Vérifie la cohérence fact/silver."""
    silver = spark.table("silver_qualite_eau").count()
    gold = spark.table("gold_fact_analyses").count()
    assert gold == silver, f"Écart : Silver={silver:,}, Gold={gold:,}"
    print(f"Gold fact : {gold:,} lignes = Silver")


def test_gold_dimensions_not_empty(spark):
    """Vérifie que toutes les dimensions contiennent des données."""
    dims = {
        "gold_dim_parametre": 1000,
        "gold_dim_departement": 90,
        "gold_dim_unite": 10,
        "gold_dim_prelevement": 100000,
        "gold_dim_commune": 30000,
    }
    for table, min_val in dims.items():
        count = spark.table(table).count()
        assert count >= min_val, f"{table} : {count} (min {min_val})"
        print(f"{table} : {count:,} lignes")


def test_gold_prelevement_has_dates(spark):
    """Vérifie que les prélèvements Gold ont des dates."""
    from pyspark.sql.functions import col
    df = spark.table("gold_dim_prelevement")
    avec_date = df.filter(col("date_prelevement").isNotNull()).count()
    total = df.count()
    pct = avec_date / total * 100
    assert pct > 95, f"Seulement {pct:.1f}% avec date"
    print(f"Gold prélèvements : {pct:.1f}% avec date")


def test_gold_departement_has_names(spark):
    """Vérifie que les départements ont des noms."""
    from pyspark.sql.functions import col
    df = spark.table("gold_dim_departement")
    sans_nom = df.filter(col("nom_departement").isNull()).count()
    total = df.count()
    pct = (total - sans_nom) / total * 100
    assert pct >= 90, f"Seulement {pct:.1f}% avec nom"
    print(f"Gold départements : {pct:.1f}% avec nom")


def test_gold_taux_conformite_range(spark):
    """Vérifie les taux de conformité [0-100]."""
    from pyspark.sql.functions import col
    df = spark.table("gold_dim_departement")
    hors = df.filter((col("taux_conformite") < 0) | (col("taux_conformite") > 100)).count()
    assert hors == 0, f"{hors} hors range"
    print("Gold : taux conformité dans [0-100]")


if __name__ == "__main__":
    tests = [
        test_bronze_resultats_exists,
        test_bronze_prelevements_exists,
        test_bronze_communes_exists,
        test_bronze_columns,
        test_silver_exists,
        test_silver_has_dates,
        test_silver_has_communes,
        test_silver_no_null_department,
        test_silver_categories_valid,
        test_silver_conformite_valid,
        test_gold_fact_count,
        test_gold_dimensions_not_empty,
        test_gold_prelevement_has_dates,
        test_gold_departement_has_names,
        test_gold_taux_conformite_range,
    ]

    print("=" * 60)
    print("EXÉCUTION DES TESTS")
    print("=" * 60)

    passed = failed = 0
    for test in tests:
        try:
            test(spark)
            passed += 1
        except AssertionError as e:
            print(f"ÉCHEC {test.__name__} : {e}")
            failed += 1
        except Exception as e:
            print(f"ERREUR {test.__name__} : {e}")
            failed += 1

    print(f"\nRÉSULTATS : {passed} passés, {failed} échoués")
