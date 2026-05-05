# Water Quality Pipeline

Pipeline de données pour l'analyse de la qualité de l'eau distribuée en France.

## Architecture du pipeline

```mermaid
flowchart LR
    A[data.gouv.fr\nAPI + ZIP] -->|Ingestion| B[Bronze\nDonnées brutes]
    B -->|Nettoyage\nEnrichissement| C[Silver\nDonnées nettoyées]
    C -->|Agrégation\nModélisation| D[Gold\nModèle en étoile]
    
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

    FACT_ANALYSES {
        long analyse_id PK
        string reference_prel FK
        string departement_code FK
        string parametre_code FK
        string unite_code FK
        string resultat_brut
        double valeur_numerique
        double limite_numerique
        string est_conforme
        string type_analyse
        string annee
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
        int population
        long nb_analyses
        long nb_conformes
        double taux_conformite
    }

    DIM_UNITE {
        string cdunitereference PK
        string libelle_unite
        long nb_utilisations
    }

    DIM_PRELEVEMENT {
        string referenceprel PK
        string departement_code
        int nb_analyses
        int nb_params_testes
        string prelevement_conforme
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
    C -->|Vérifie| C2[Config existe]
    C -->|Lint| C3[flake8]
    D -->|Teste| D1[Catégories]
    D -->|Teste| D2[Niveaux de danger]
    D -->|Teste| D3[Tables config]
    E -->|Scanne| E1[Pas de secrets]
    E -->|Scanne| E2[Pas de credentials]

    style A fill:#f1efe8,stroke:#5f5e5a,color:#2c2c2a
    style B fill:#eeedfe,stroke:#534ab7,color:#26215c
    style C fill:#e6f1fb,stroke:#185fa5,color:#042c53
    style D fill:#e6f1fb,stroke:#185fa5,color:#042c53
    style E fill:#e6f1fb,stroke:#185fa5,color:#042c53
```

## Source de données

- **Dataset** : [Résultats du contrôle sanitaire de l'eau](https://www.data.gouv.fr/fr/datasets/resultats-du-controle-sanitaire-de-leau-distribuee-commune-par-commune/)
- **Volume** : 12.6 millions d'analyses (2024)
- **Couverture** : 101 départements français

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
    │       └── ci.yml                             # Pipeline CI/CD (3jobs)
    ├── notebooks/
    │   ├── 01_DLT_Ingestion_Qualite_Eau.py        # Bronze : ingestion API
    │   ├── 02_Silver_Transformation.py            # Silver : nettoyage
    │   └── 03_Gold_Agregations.py                 # Gold : modèle en étoile
    ├── config/
    │   └── pipeline_config.py                     # Configuration centralisée  
    ├── tests/
    │   └── test_pipeline.py                       # Tests unitaires 
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
- 17 543 prélèvements avec au moins une non-conformité (sur 291 604)
- Taux de conformité moyen : environ 99%
- 4 niveaux de danger : Sanitaire critique, Sanitaire, Organoleptique, Surveillance

## Conventions de commits (Semantic Release)

- `feat:` nouvelle fonctionnalité
- `fix:` correction de bug
- `docs:` documentation
- `test:` ajout de tests
- `ci:` modifications CI/CD
- `refactor:` restructuration de code

## Auteur

Projet réalisé dans le cadre d'une formation Data Engineering.
