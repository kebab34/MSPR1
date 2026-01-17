"""
Schémas Pydantic pour les sessions sport
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import date, time, datetime
from uuid import UUID


class SessionExerciceBase(BaseModel):
    """Schéma pour un exercice dans une session"""
    id_exercice: UUID
    serie: int = Field(..., gt=0)
    repetitions: Optional[int] = Field(None, gt=0)
    poids: Optional[float] = Field(None, ge=0)
    duree_secondes: Optional[int] = Field(None, gt=0)
    repos_secondes: Optional[int] = Field(None, ge=0)
    ordre: Optional[int] = None


class SessionSportBase(BaseModel):
    """Schéma de base pour une session sport"""
    id_utilisateur: UUID
    date: date
    heure_debut: Optional[time] = None
    heure_fin: Optional[time] = None
    duree_minutes: Optional[int] = Field(None, gt=0)
    intensite: Optional[str] = Field(None, pattern="^(faible|moderee|elevee|tres_elevee)$")
    calories_brûlees: Optional[float] = Field(None, ge=0)
    notes: Optional[str] = None


class SessionSportCreate(SessionSportBase):
    """Schéma pour créer une session sport"""
    exercices: Optional[List[SessionExerciceBase]] = []


class SessionSportUpdate(BaseModel):
    """Schéma pour mettre à jour une session sport"""
    date: Optional[date] = None
    heure_debut: Optional[time] = None
    heure_fin: Optional[time] = None
    duree_minutes: Optional[int] = Field(None, gt=0)
    intensite: Optional[str] = Field(None, pattern="^(faible|moderee|elevee|tres_elevee)$")
    calories_brûlees: Optional[float] = Field(None, ge=0)
    notes: Optional[str] = None


class SessionSportRead(SessionSportBase):
    """Schéma pour lire une session sport"""
    id_session: UUID
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


