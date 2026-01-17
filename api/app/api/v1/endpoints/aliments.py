"""
Endpoints pour la gestion des aliments
"""

from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from uuid import UUID
from app.core.database import supabase_admin
from app.schemas.aliment import AlimentCreate, AlimentUpdate, AlimentRead

router = APIRouter()


@router.get("", response_model=List[AlimentRead])
async def get_aliments(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    search: Optional[str] = None
):
    """Récupérer la liste des aliments"""
    try:
        query = supabase_admin.table("aliments").select("*")
        
        if search:
            query = query.ilike("nom", f"%{search}%")
        
        result = query.range(skip, skip + limit - 1).order("nom").execute()
        return result.data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la récupération: {str(e)}")


@router.get("/{aliment_id}", response_model=AlimentRead)
async def get_aliment(aliment_id: UUID):
    """Récupérer un aliment par son ID"""
    try:
        result = supabase_admin.table("aliments").select("*").eq("id_aliment", str(aliment_id)).execute()
        
        if not result.data:
            raise HTTPException(status_code=404, detail="Aliment non trouvé")
        
        return result.data[0]
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la récupération: {str(e)}")


@router.post("", response_model=AlimentRead, status_code=201)
async def create_aliment(aliment: AlimentCreate):
    """Créer un nouvel aliment"""
    try:
        data = aliment.model_dump()
        result = supabase_admin.table("aliments").insert(data).execute()
        
        if not result.data:
            raise HTTPException(status_code=400, detail="Erreur lors de la création")
        
        return result.data[0]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la création: {str(e)}")


@router.put("/{aliment_id}", response_model=AlimentRead)
async def update_aliment(aliment_id: UUID, aliment: AlimentUpdate):
    """Mettre à jour un aliment"""
    try:
        data = aliment.model_dump(exclude_unset=True)
        
        if not data:
            raise HTTPException(status_code=400, detail="Aucune donnée à mettre à jour")
        
        result = supabase_admin.table("aliments").update(data).eq("id_aliment", str(aliment_id)).execute()
        
        if not result.data:
            raise HTTPException(status_code=404, detail="Aliment non trouvé")
        
        return result.data[0]
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la mise à jour: {str(e)}")


@router.delete("/{aliment_id}", status_code=204)
async def delete_aliment(aliment_id: UUID):
    """Supprimer un aliment"""
    try:
        result = supabase_admin.table("aliments").delete().eq("id_aliment", str(aliment_id)).execute()
        
        if not result.data:
            raise HTTPException(status_code=404, detail="Aliment non trouvé")
        
        return None
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la suppression: {str(e)}")


