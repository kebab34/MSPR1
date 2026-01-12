"""
Endpoints pour la gestion des exercices
"""

from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from uuid import UUID
from app.core.database import supabase_admin
from app.schemas.exercice import ExerciceCreate, ExerciceUpdate, ExerciceRead

router = APIRouter()


@router.get("", response_model=List[ExerciceRead])
async def get_exercices(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    type: Optional[str] = None,
    groupe_musculaire: Optional[str] = None,
    niveau: Optional[str] = None,
    search: Optional[str] = None
):
    """Récupérer la liste des exercices"""
    try:
        query = supabase_admin.table("exercices").select("*")
        
        if type:
            query = query.eq("type", type)
        if groupe_musculaire:
            query = query.eq("groupe_musculaire", groupe_musculaire)
        if niveau:
            query = query.eq("niveau", niveau)
        if search:
            query = query.ilike("nom", f"%{search}%")
        
        result = query.range(skip, skip + limit - 1).order("nom").execute()
        return result.data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la récupération: {str(e)}")


@router.get("/{exercice_id}", response_model=ExerciceRead)
async def get_exercice(exercice_id: UUID):
    """Récupérer un exercice par son ID"""
    try:
        result = supabase_admin.table("exercices").select("*").eq("id_exercice", str(exercice_id)).execute()
        
        if not result.data:
            raise HTTPException(status_code=404, detail="Exercice non trouvé")
        
        return result.data[0]
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la récupération: {str(e)}")


@router.post("", response_model=ExerciceRead, status_code=201)
async def create_exercice(exercice: ExerciceCreate):
    """Créer un nouvel exercice"""
    try:
        data = exercice.model_dump()
        result = supabase_admin.table("exercices").insert(data).execute()
        
        if not result.data:
            raise HTTPException(status_code=400, detail="Erreur lors de la création")
        
        return result.data[0]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la création: {str(e)}")


@router.put("/{exercice_id}", response_model=ExerciceRead)
async def update_exercice(exercice_id: UUID, exercice: ExerciceUpdate):
    """Mettre à jour un exercice"""
    try:
        data = exercice.model_dump(exclude_unset=True)
        
        if not data:
            raise HTTPException(status_code=400, detail="Aucune donnée à mettre à jour")
        
        result = supabase_admin.table("exercices").update(data).eq("id_exercice", str(exercice_id)).execute()
        
        if not result.data:
            raise HTTPException(status_code=404, detail="Exercice non trouvé")
        
        return result.data[0]
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la mise à jour: {str(e)}")


@router.delete("/{exercice_id}", status_code=204)
async def delete_exercice(exercice_id: UUID):
    """Supprimer un exercice"""
    try:
        result = supabase_admin.table("exercices").delete().eq("id_exercice", str(exercice_id)).execute()
        
        if not result.data:
            raise HTTPException(status_code=404, detail="Exercice non trouvé")
        
        return None
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la suppression: {str(e)}")

