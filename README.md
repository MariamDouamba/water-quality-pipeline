# Water Quality Pipeline

Pipeline de données pour l'analyse de la qualité de l'eau distribuée en France.

## Architecture du pipeline

```mermaid
flowchart LR
    A[data.gouv.fr\nAPI + ZIP] -->|3 fichiers| B[Bronze\n3 tables brutes]
    B -->|Nettoyage\nEnrichissement\nJointure| C[Silver\n1 table enrichie]
    C -->|Agrégation\nModélisation| D[Gold\nModèle en étoile\n6 dimensions]

    style A fill:#f1efe8,stroke:#5f5e5a,color:#2c2c2a
    style B fill:#faece7,stroke:#993c1d,color:#4a1b0c
    style C fill:#e1f5ee,stroke:#0f6e56,color:#04342c
    style D fill:#eeedfe,stroke:#534ab7,color:#26215c
```

## Modèle en étoile (Gold)

```mermaid
erDiagram
    FACT_ANALYSES ||--o{ DIM_PARAMETRE : "parametre_code"
    FACT_ANALYSES ||--o{ DIM_DEPARTEMENT : "departement_code"
    FACT_ANALYSES ||--o{ DIM_UNITE : "unite_code"
    FACT_ANALYSES ||--o{ DIM_PRELEVEMENT : "reference_prel"
    DIM_PRELEVEMENT ||--o{ DIM_COMMUNE : "code_insee"

    FACT_ANALYSES {
        long analyse_id PK
        string reference_prel FK
        string departement_code FK
        string parametre_code FK
        string unite_code FK
        date date_prelevement
        string commune
        string resultat_brut
        double valeur_numerique
        double limite_numerique
        string est_conforme
        string type_analyse
    }

    DIM_PARAMETRE {
        string cdparametresiseeaux PK
        int cdparametre
        string libelle_parametre
        string categorie_parametre
        string niveau_danger
        string limite_qualite
        string cas_number
    }

    DIM_DEPARTEMENT {
        string code_departement PK
        string nom_departement
        string region
        long nb_analyses
        double taux_conformite
    }

    DIM_UNITE {
        string cdunitereference PK
        string libelle_unite
        long nb_utilisations
    }

    DIM_PRELEVEMENT {
        string referenceprel PK
        date date_prelevement
        string heure_prelevement
        string commune
        string code_insee
        string conformite_bacterio
        string conformite_chimique
    }

    DIM_COMMUNE {
        string code_insee PK
        string nom_commune
        string nom_reseau
    }
```

## Pipeline CI/CD

```mermaid
flowchart TD
    A[Git Push sur main] --> B[GitHub Actions]
    B --> C[Validate Structure]
    B --> E[Security Check]
    C -->|OK| D[Test Configuration]

    C -->|Vérifie| C1[Notebooks existent]
    C -->|Lint| C2[flake8]
    D -->|Teste| D1[Catégories et danger]
    D -->|Teste| D2[Tables et encodage]
    E -->|Scanne| E1[Pas de secrets]

    style A fill:#f1efe8,stroke:#5f5e5a,color:#2c2c2a
    style B fill:#eeedfe,stroke:#534ab7,color:#26215c
    style C fill:#e6f1fb,stroke:#185fa5,color:#042c53
    style D fill:#e6f1fb,stroke:#185fa5,color:#042c53
    style E fill:#e6f1fb,stroke:#185fa5,color:#042c53
```

## Sources de données

| Fichier | Description | Volume |
|---------|-------------|--------|
| DIS_RESULT_2024.txt | Résultats d'analyses | 12.6M lignes |
| DIS_PLV_2024.txt | Prélèvements (dates, communes) | 408K lignes |
| DIS_COM_UDI_2024.txt | Communes et réseaux | 49K lignes |

Source : [data.gouv.fr](https://www.data.gouv.fr/fr/datasets/resultats-du-controle-sanitaire-de-leau-distribuee-commune-par-commune/)

## Stack technique

- **Cloud** : Azure / Databricks (Serverless)
- **Traitement** : PySpark
- **Stockage** : Delta Lake (architecture médaillon)
- **CI/CD** : GitHub Actions
- **Qualité** : Great Expectations

## Structure du projet

    water-quality-pipelines/
    ├── .github/
    │   └── workflows/
    │       └── ci.yml
    ├── notebooks/
    │   ├── 01_DLT_Ingestion_Qualite_Eau.py
    │   ├── 02_Silver_Transformation.py
    │   ├── 03_Gold_Agregations.py
    │   └── 04_Quality_Checks.py
    ├── config/
    │   └── pipeline_config.py
    ├── tests/
    │   └── test_pipeline.py
    ├── .gitignore
    ├── LICENSE
    └── README.md

## Catégories de paramètres

| Catégorie | Exemples | Volume |
|-----------|----------|--------|
| Pesticides | Atrazine, Glyphosate, Métolachlore | 6.2M |
| Microbiologie | E. coli, Entérocoques | 1.5M |
| Organoleptique | Turbidité, Odeur, Couleur | 1.5M |
| Physico-chimique | pH, Conductivité, Température | 1.3M |
| Désinfection | Chlore, Trihalométhanes | 830K |
| Nitrates/Nitrites | NO3, NO2, Ammonium | 524K |
| Métaux et minéraux | Plomb, Arsenic, Aluminium | 461K |
| Chimie minérale | Sulfates, Fluorures | 157K |
| Radioactivité | Tritium, Activité alpha/béta | 74K |

## Résultats clés

- 28 140 non-conformités détectées sur 12.6M analyses
- 17 543 prélèvements avec au moins une non-conformité
- Données couvrant toute l'année 2024 (2 jan - 31 déc)
- 34 811 communes et 101 départements analysés
- 4 niveaux de danger : Sanitaire critique, Sanitaire, Organoleptique, Surveillance

## Conventions de commits

- `feat:` nouvelle fonctionnalité
- `fix:` correction de bug
- `docs:` documentation
- `test:` ajout de tests
- `ci:` modifications CI/CD
- `refactor:` restructuration de code

## Auteur

Projet réalisé dans le cadre d'une formation Data Engineering.
