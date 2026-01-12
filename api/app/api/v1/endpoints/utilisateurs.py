"""
Endpoints pour la gestion des utilisateurs
"""

from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from uuid import UUID
from app.core.database import supabase_admin
from app.schemas.utilisateur import UtilisateurCreate, UtilisateurUpdate, UtilisateurRead

router = APIRouter()


@router.get("", response_model=List[UtilisateurRead])
async def get_utilisateurs(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    type_abonnement: Optional[str] = None
):
    """Récupérer la liste des utilisateurs"""
    try:
        query = supabase_admin.table("utilisateurs").select("*")
        
        if type_abonnement:
            query = query.eq("type_abonnement", type_abonnement)
        
        result = query.range(skip, skip + limit - 1).execute()
        return result.data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la récupération: {str(e)}")


@router.get("/{utilisateur_id}", response_model=UtilisateurRead)
async def get_utilisateur(utilisateur_id: UUID):
    """Récupérer un utilisateur par son ID"""
    try:
        result = supabase_admin.table("utilisateurs").select("*").eq("id_utilisateur", str(utilisateur_id)).execute()
        
        if not result.data:
            raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
        
        return result.data[0]
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la récupération: {str(e)}")


@router.post("", response_model=UtilisateurRead, status_code=201)
async def create_utilisateur(utilisateur: UtilisateurCreate):
    """Créer un nouvel utilisateur"""
    try:
        data = utilisateur.model_dump()
        result = supabase_admin.table("utilisateurs").insert(data).execute()
        
        if not result.data:
            raise HTTPException(status_code=400, detail="Erreur lors de la création")
        
        return result.data[0]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la création: {str(e)}")


@router.put("/{utilisateur_id}", response_model=UtilisateurRead)
async def update_utilisateur(utilisateur_id: UUID, utilisateur: UtilisateurUpdate):
    """Mettre à jour un utilisateur"""
    try:
        data = utilisateur.model_dump(exclude_unset=True)
        
        if not data:
            raise HTTPException(status_code=400, detail="Aucune donnée à mettre à jour")
        
        result = supabase_admin.table("utilisateurs").update(data).eq("id_utilisateur", str(utilisateur_id)).execute()
        
        if not result.data:
            raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
        
        return result.data[0]
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la mise à jour: {str(e)}")


@router.delete("/{utilisateur_id}", status_code=204)
async def delete_utilisateur(utilisateur_id: UUID):
    """Supprimer un utilisateur"""
    try:
        result = supabase_admin.table("utilisateurs").delete().eq("id_utilisateur", str(utilisateur_id)).execute()
        
        if not result.data:
            raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
        
        return None
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la suppression: {str(e)}")

