"""
Schémas Pydantic pour les recommandations sportives (MongoDB).
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum
from uuid import UUID


class ObjectifSport(str, Enum):
    PERTE_GRAISSE = "perte_de_graisse"
    RENFORCEMENT = "renforcement_musculaire"
    ENDURANCE = "endurance"
    SANTE_GENERALE = "sante_generale"
    SOUPLESSE = "souplesse"


class NiveauForme(str, Enum):
    DEBUTANT = "debutant"
    INTERMEDIAIRE = "intermediaire"
    AVANCE = "avance"


class WorkoutRequest(BaseModel):
    utilisateur_id: str = Field(..., description="UUID utilisateur depuis le backend principal")
    objectif: ObjectifSport = ObjectifSport.SANTE_GENERALE
    niveau: NiveauForme = NiveauForme.DEBUTANT
    equipements_disponibles: List[str] = Field(
        default=[],
        description="Ex: ['haltères', 'tapis', 'barre de traction']"
    )
    activites_preferees: List[str] = Field(
        default=[],
        description="Ex: ['course', 'natation', 'yoga']"
    )
    duree_seance_min: int = Field(30, ge=15, le=120, description="Durée souhaitée en minutes")
    jours_par_semaine: int = Field(3, ge=1, le=7)
    limitations_physiques: List[str] = Field(
        default=[],
        description="Ex: ['douleur genou', 'hernie discale']"
    )
    poids: Optional[float] = Field(None, gt=0)
    age: Optional[int] = Field(None, gt=0, lt=150)
    frequence_cardiaque_repos: Optional[int] = Field(None, gt=30, lt=200)


class Exercice(BaseModel):
    nom: str
    type: str
    series: Optional[int] = None
    repetitions: Optional[str] = None
    duree_secondes: Optional[int] = None
    repos_secondes: int = 60
    intensite: str = "modérée"
    instructions: str
    muscles_cibles: List[str] = []
    adaptation_limitations: Optional[str] = None


class SeanceEntrainement(BaseModel):
    titre: str
    duree_estimee_min: int
    echauffement: List[str]
    exercices_principaux: List[Exercice]
    retour_au_calme: List[str]
    calories_estimees: Optional[int] = None
    niveau_difficulte: str


class ProgrammeSemaine(BaseModel):
    lundi: Optional[SeanceEntrainement] = None
    mardi: Optional[SeanceEntrainement] = None
    mercredi: Optional[SeanceEntrainement] = None
    jeudi: Optional[SeanceEntrainement] = None
    vendredi: Optional[SeanceEntrainement] = None
    samedi: Optional[SeanceEntrainement] = None
    dimanche: Optional[SeanceEntrainement] = None


class WorkoutResponse(BaseModel):
    id: Optional[str] = None
    utilisateur_id: str
    objectif: str
    programme_semaine: ProgrammeSemaine
    conseils_progression: List[str]
    conseils_recuperation: List[str]
    objectifs_semaine: List[str]
    message_motivant: str
    created_at: datetime = Field(default_factory=datetime.utcnow)


class FeedbackRequest(BaseModel):
    recommendation_id: str
    utilisateur_id: str
    note: int = Field(..., ge=1, le=5, description="Note de 1 à 5")
    commentaire: Optional[str] = None
    seances_completees: int = Field(0, ge=0)
    difficulte_ressentie: Optional[str] = Field(
        None, pattern="^(trop_facile|adapte|trop_difficile)$"
    )


class FeedbackResponse(BaseModel):
    message: str
    recommendation_id: str
