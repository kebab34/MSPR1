"""
Schémas Pydantic pour les mesures biométriques
"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import date, time, datetime
from uuid import UUID


class MesureBiometriqueBase(BaseModel):
    """Schéma de base pour une mesure biométrique"""
    id_utilisateur: UUID
    date: date
    heure: Optional[time] = None
    poids: Optional[float] = Field(None, gt=0)
    frequence_cardiaque_rest: Optional[int] = Field(None, gt=0, lt=300)
    frequence_cardiaque_max: Optional[int] = Field(None, gt=0, lt=300)
    duree_sommeil_heures: Optional[float] = Field(None, ge=0, le=24)
    qualite_sommeil: Optional[int] = Field(None, ge=1, le=10)
    calories_brûlees_jour: Optional[float] = Field(None, ge=0)
    pas: Optional[int] = Field(None, ge=0)
    distance_km: Optional[float] = Field(None, ge=0)
    notes: Optional[str] = None


class MesureBiometriqueCreate(MesureBiometriqueBase):
    """Schéma pour créer une mesure biométrique"""
    pass


class MesureBiometriqueUpdate(BaseModel):
    """Schéma pour mettre à jour une mesure biométrique"""
    date: Optional[date] = None
    heure: Optional[time] = None
    poids: Optional[float] = Field(None, gt=0)
    frequence_cardiaque_rest: Optional[int] = Field(None, gt=0, lt=300)
    frequence_cardiaque_max: Optional[int] = Field(None, gt=0, lt=300)
    duree_sommeil_heures: Optional[float] = Field(None, ge=0, le=24)
    qualite_sommeil: Optional[int] = Field(None, ge=1, le=10)
    calories_brûlees_jour: Optional[float] = Field(None, ge=0)
    pas: Optional[int] = Field(None, ge=0)
    distance_km: Optional[float] = Field(None, ge=0)
    notes: Optional[str] = None


class MesureBiometriqueRead(MesureBiometriqueBase):
    """Schéma pour lire une mesure biométrique"""
    id_mesure: UUID
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

