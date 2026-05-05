"""
Configuration centralisée du pipeline de qualité de l'eau.
Toutes les constantes et paramètres sont définis ici.
"""

# ---- Source de données ----
DATASET_ID = "resultats-du-controle-sanitaire-de-leau-distribuee-commune-par-commune"
API_BASE_URL = "https://www.data.gouv.fr/api/1/datasets"
ANNEE = "2024"

# ---- Fichiers source ----
SOURCE_FILES = {
    "resultats": "DIS_RESULT_2024.txt",
    "prelevements": "DIS_PLV_2024.txt",
    "communes": "DIS_COM_UDI_2024.txt",
}

# ---- Tables Delta ----
TABLES = {
    "bronze_resultats": "bronze_qualite_eau",
    "bronze_prelevements": "bronze_prelevements",
    "bronze_communes": "bronze_communes",
    "silver": "silver_qualite_eau",
    "gold_fact": "gold_fact_analyses",
    "gold_dim_parametre": "gold_dim_parametre",
    "gold_dim_departement": "gold_dim_departement",
    "gold_dim_unite": "gold_dim_unite",
    "gold_dim_prelevement": "gold_dim_prelevement",
    "gold_dim_commune": "gold_dim_commune",
}

# ---- Catégories de paramètres ----
CATEGORIES = {
    "Microbiologie": [
        "CTF", "ECOLI", "ENTERO", "GT22_68", "GT36_44",
        "COLIF", "STPHY", "PSAR", "SPCLOS", "STRF", "BSIR",
        "GT22_72", "GT36_48", "LEGPN", "LEGSP"
    ],
    "Pesticides": [
        "ATRZ", "ATZ", "ADET", "ADSP", "A2H", "SMZ", "SIMZ", "SHYD",
        "TBZ", "TBZDES", "TBZH", "MTBZ",
        "MTC", "METOL", "MTCESA", "MTCOA", "METZCL",
        "LNCE", "LNDI", "CLRTOL", "ISOPR", "DIURO",
        "ALDRI", "DIELDR", "DDT", "HCH", "CLRDC", "HEP", "HEPET", "LNDN",
        "GLPHOS", "AMPA", "BFNX", "BOSCALI", "CNPA", "DMTE", "FLUMIOX",
        "METIL", "PPTP", "PENOXU", "SULFRN", "MTMI", "FLONIC",
        "CLMQT", "MEPIQT", "PROPZN", "ASULAME", "PESTOT"
    ],
    "Organoleptique": [
        "ASP", "COULQ", "SAVQ", "ODEQ", "TURBI",
        "TURBNFU", "ODQ", "COULF", "ODEUR25", "SAV25", "COULR"
    ],
    "Physico-chimique": [
        "PH", "COND", "TEMP", "TAC", "TH", "O2DIS",
        "CDT25", "TEAU", "TAIR", "TEMP_PH",
        "TA", "CO3", "HCO3", "CALCOC2", "COT", "OXYD"
    ],
    "Désinfection": [
        "CL2LIB", "CL2TOT", "CL2COMB", "CLO2",
        "THM4", "CLF", "BRF", "DCLMBR", "DBRMCL",
        "CLVYL", "ACRYL", "EPICL", "BRATE"
    ],
    "Nitrates/Nitrites": ["NO3", "NO2", "NH4", "NO3_NO2"],
    "Métaux et minéraux": [
        "PBT", "ALTMICR", "CUTMICR", "FET", "CRTOTR",
        "MNMICR", "NIMICR", "ASTMICR", "BMG", "CDMICR",
        "MN", "CA", "MG", "K", "NA",
        "SETMICR", "SBMICR", "BATMICR", "HGMICR", "ALTOT", "ZN"
    ],
    "Chimie minérale": ["SO4", "CL", "FLUOR", "SIO2", "DUR"],
}

# ---- Niveaux de danger ----
DANGER_LEVELS = {
    "Sanitaire critique": [
        "ECOLI", "ENTERO", "CTF", "COLIF", "STRF",
        "BSIR", "SPCLOS", "PSAR", "LEGPN", "LEGSP"
    ],
    "Sanitaire": [
        "NO3", "NO2", "NH4", "NO3_NO2",
        "PBT", "ASTMICR", "CDMICR", "CRTOTR", "HGMICR",
        "ATRZ", "ATZ", "SIMZ", "SMZ", "GLPHOS", "AMPA",
        "ALDRI", "DIELDR", "DDT", "HCH", "CLRDC",
        "BRATE", "CLVYL", "ACRYL", "EPICL", "PESTOT", "THM4"
    ],
    "Organoleptique": [
        "ASP", "COULQ", "SAVQ", "ODEQ", "TURBI",
        "TURBNFU", "ODQ", "COULF", "ODEUR25", "SAV25"
    ],
}

# ---- Encodage ----
ENCODING_CORRECTIONS = {
    "Ã©": "é", "Ã¨": "è", "Ãª": "ê", "Ã ": "à",
    "Ã¢": "â", "Ã®": "î", "Ã´": "ô", "Ã¹": "ù",
    "Ã»": "û", "Ã§": "ç", "Ã‰": "É", "Ã€": "À",
    "Ã": "À", "Âµ": "µ", "Â°": "°", "Â²": "²",
}

# ---- Colonnes PLV à garder ----
PLV_COLUMNS_KEEP = [
    "referenceprel", "dateprel", "heureprel",
    "nomcommuneprinc", "inseecommuneprinc", "cdreseau",
    "conclusionprel", "plvconformitebacterio", "plvconformitechimique"
]

# ---- Colonnes PLV à écarter ----
PLV_COLUMNS_DROP = [
    "cdreseauamont", "nomreseauamont", "pourcentdebit",
    "plvconformitereferencebact", "plvconformitereferencechim"
]
