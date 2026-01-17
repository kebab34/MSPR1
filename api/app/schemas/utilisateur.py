"""
Schémas Pydantic pour les utilisateurs
"""

from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime
from uuid import UUID


class UtilisateurBase(BaseModel):
    """Schéma de base pour un utilisateur"""
    email: EmailStr
    nom: Optional[str] = None
    prenom: Optional[str] = None
    age: Optional[int] = Field(None, gt=0, lt=150)
    sexe: Optional[str] = Field(None, pattern="^(M|F|Autre)$")
    poids: Optional[float] = Field(None, gt=0)
    taille: Optional[float] = Field(None, gt=0)
    objectifs: Optional[List[str]] = []
    type_abonnement: str = Field("freemium", pattern="^(freemium|premium|premium\\+|B2B)$")


class UtilisateurCreate(UtilisateurBase):
    """Schéma pour créer un utilisateur"""
    pass


class UtilisateurUpdate(BaseModel):
    """Schéma pour mettre à jour un utilisateur"""
    nom: Optional[str] = None
    prenom: Optional[str] = None
    age: Optional[int] = Field(None, gt=0, lt=150)
    sexe: Optional[str] = Field(None, pattern="^(M|F|Autre)$")
    poids: Optional[float] = Field(None, gt=0)
    taille: Optional[float] = Field(None, gt=0)
    objectifs: Optional[List[str]] = None
    type_abonnement: Optional[str] = Field(None, pattern="^(freemium|premium|premium\\+|B2B)$")


class UtilisateurRead(UtilisateurBase):
    """Schéma pour lire un utilisateur"""
    id_utilisateur: UUID
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


