"""
Schémas Pydantic pour le journal alimentaire
"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import date, time, datetime
from uuid import UUID


class JournalAlimentaireBase(BaseModel):
    """Schéma de base pour une entrée du journal alimentaire"""
    id_utilisateur: UUID
    id_aliment: Optional[UUID] = None
    id_recette: Optional[UUID] = None
    date: date
    heure: Optional[time] = None
    quantite: float = Field(..., gt=0)
    calories_totales: Optional[float] = Field(None, ge=0)
    repas: Optional[str] = Field(None, pattern="^(petit_dejeuner|dejeuner|diner|collation|autre)$")


class JournalAlimentaireCreate(JournalAlimentaireBase):
    """Schéma pour créer une entrée du journal"""
    pass


class JournalAlimentaireUpdate(BaseModel):
    """Schéma pour mettre à jour une entrée du journal"""
    date: Optional[date] = None
    heure: Optional[time] = None
    quantite: Optional[float] = Field(None, gt=0)
    calories_totales: Optional[float] = Field(None, ge=0)
    repas: Optional[str] = Field(None, pattern="^(petit_dejeuner|dejeuner|diner|collation|autre)$")


class JournalAlimentaireRead(JournalAlimentaireBase):
    """Schéma pour lire une entrée du journal"""
    id_journal: UUID
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

