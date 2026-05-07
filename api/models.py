"""
Modèles Pydantic pour la validation des données.
"""
from pydantic import BaseModel
from typing import Optional
from datetime import date


class Departement(BaseModel):
    code_departement: str
    nom_departement: Optional[str]
    region: Optional[str]
    nb_analyses: int
    nb_prelevements: int
    nb_communes: int
    nb_conformes: int
    nb_non_conformes: int
    taux_conformite: Optional[float]


class Parametre(BaseModel):
    cdparametresiseeaux: str
    libelle_parametre: Optional[str]
    categorie_parametre: Optional[str]
    niveau_danger: Optional[str]
    unite_libelle: Optional[str]
    limite_qualite: Optional[str]


class Prelevement(BaseModel):
    referenceprel: str
    departement_code: Optional[str]
    date_prelevement: Optional[date]
    commune: Optional[str]
    conformite_bacterio: Optional[str]
    conformite_chimique: Optional[str]
    nb_analyses: int
    prelevement_conforme: Optional[str]


class NonConformite(BaseModel):
    commune: Optional[str]
    departement_code: Optional[str]
    parametre_code: Optional[str]
    resultat_brut: Optional[str]
    valeur_numerique: Optional[float]
    limite_numerique: Optional[float]
    date_prelevement: Optional[date]


class StatsResponse(BaseModel):
    total_analyses: int
    total_prelevements: int
    total_communes: int
    total_departements: int
    total_non_conformites: int
    taux_conformite_global: float