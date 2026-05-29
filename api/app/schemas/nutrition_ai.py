"""
Schémas Pydantic pour les fonctionnalités IA nutrition
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from enum import Enum


class ObjectifNutrition(str, Enum):
    PERTE_POIDS = "perte_de_poids"
    PRISE_MASSE = "prise_de_masse"
    EQUILIBRE = "equilibre_nutritionnel"
    PERFORMANCE = "performance_sportive"
    MAINTIEN = "maintien"


class AlimentDetecte(BaseModel):
    nom: str
    quantite_estimee: str
    calories: float = Field(ge=0)
    proteines: float = Field(ge=0)
    glucides: float = Field(ge=0)
    lipides: float = Field(ge=0)
    fibres: float = Field(ge=0)


class AnalyseNutritionRequest(BaseModel):
    objectif: ObjectifNutrition = ObjectifNutrition.EQUILIBRE
    allergies: List[str] = []
    notes_utilisateur: Optional[str] = None


class AnalyseNutritionResponse(BaseModel):
    aliments_detectes: List[AlimentDetecte]
    total_calories: float
    total_proteines: float
    total_glucides: float
    total_lipides: float
    total_fibres: float
    desequilibres_detectes: List[str]
    suggestions_amelioration: List[str]
    score_nutritionnel: int = Field(ge=0, le=100, description="Score de 0 à 100")
    message_global: str


class PlanRepasRequest(BaseModel):
    objectif: ObjectifNutrition = ObjectifNutrition.EQUILIBRE
    budget_quotidien: Optional[float] = Field(None, ge=0, description="Budget en euros/jour")
    allergies: List[str] = []
    preferences_alimentaires: List[str] = []
    regime: Optional[str] = Field(None, description="Ex: végétarien, vegan, sans gluten")
    calories_cibles: Optional[float] = Field(None, ge=800, le=5000)
    nb_jours: int = Field(7, ge=1, le=14, description="Nombre de jours du plan")
    poids: Optional[float] = Field(None, gt=0)
    taille: Optional[float] = Field(None, gt=0)
    age: Optional[int] = Field(None, gt=0, lt=150)
    sexe: Optional[str] = Field(None, pattern="^(M|F|Autre)$")


class RepasJour(BaseModel):
    petit_dejeuner: str
    dejeuner: str
    diner: str
    collations: Optional[str] = None
    calories_estimees: float
    proteines_estimees: float
    glucides_estimees: float
    lipides_estimees: float


class PlanRepasResponse(BaseModel):
    plan: dict[str, RepasJour]
    calories_moyennes_par_jour: float
    conseils_generaux: List[str]
    liste_courses: List[str]
    message_personnalise: str
