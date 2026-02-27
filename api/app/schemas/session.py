"""
Schémas Pydantic pour les sessions sport
"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from uuid import UUID


class SessionSportBase(BaseModel):
    """Schéma de base pour une session sport"""
    id_utilisateur: UUID
    duree: Optional[int] = Field(None, gt=0)
    intensite: Optional[str] = Field(None, pattern="^(faible|moderee|elevee)$")
    date_session: Optional[datetime] = None


class SessionSportCreate(SessionSportBase):
    """Schéma pour créer une session sport"""
    pass


class SessionSportUpdate(BaseModel):
    """Schéma pour mettre à jour une session sport"""
    duree: Optional[int] = Field(None, gt=0)
    intensite: Optional[str] = Field(None, pattern="^(faible|moderee|elevee)$")
    date_session: Optional[datetime] = None


class SessionSportRead(SessionSportBase):
    """Schéma pour lire une session sport"""
    id_session: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
