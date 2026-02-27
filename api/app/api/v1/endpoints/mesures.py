"""
Endpoints pour la gestion des mesures biométriques
"""

from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from uuid import UUID
from datetime import date
from app.core.database import supabase_admin
from app.schemas.mesure import MesureBiometriqueCreate, MesureBiometriqueUpdate, MesureBiometriqueRead

router = APIRouter()


@router.get("", response_model=List[MesureBiometriqueRead])
async def get_mesures(
    utilisateur_id: Optional[UUID] = None,
    date_debut: Optional[date] = None,
    date_fin: Optional[date] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000)
):
    """Récupérer la liste des mesures biométriques"""
    try:
        query = supabase_admin.table("mesures_biometriques").select("*")
        
        if utilisateur_id:
            query = query.eq("id_utilisateur", str(utilisateur_id))
        if date_debut:
            query = query.gte("date_mesure", str(date_debut))
        if date_fin:
            query = query.lte("date_mesure", str(date_fin))

        result = query.range(skip, skip + limit - 1).order("date_mesure", desc=True).execute()
        return result.data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la récupération: {str(e)}")


@router.get("/{mesure_id}", response_model=MesureBiometriqueRead)
async def get_mesure(mesure_id: UUID):
    """Récupérer une mesure biométrique par son ID"""
    try:
        result = supabase_admin.table("mesures_biometriques").select("*").eq("id_mesure", str(mesure_id)).execute()
        
        if not result.data:
            raise HTTPException(status_code=404, detail="Mesure biométrique non trouvée")
        
        return result.data[0]
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la récupération: {str(e)}")


@router.post("", response_model=MesureBiometriqueRead, status_code=201)
async def create_mesure(mesure: MesureBiometriqueCreate):
    """Créer une nouvelle mesure biométrique"""
    try:
        data = mesure.model_dump()
        result = supabase_admin.table("mesures_biometriques").insert(data).execute()
        
        if not result.data:
            raise HTTPException(status_code=400, detail="Erreur lors de la création")
        
        return result.data[0]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la création: {str(e)}")


@router.put("/{mesure_id}", response_model=MesureBiometriqueRead)
async def update_mesure(mesure_id: UUID, mesure: MesureBiometriqueUpdate):
    """Mettre à jour une mesure biométrique"""
    try:
        data = mesure.model_dump(exclude_unset=True)
        
        if not data:
            raise HTTPException(status_code=400, detail="Aucune donnée à mettre à jour")
        
        result = supabase_admin.table("mesures_biometriques").update(data).eq("id_mesure", str(mesure_id)).execute()
        
        if not result.data:
            raise HTTPException(status_code=404, detail="Mesure biométrique non trouvée")
        
        return result.data[0]
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la mise à jour: {str(e)}")


@router.delete("/{mesure_id}", status_code=204)
async def delete_mesure(mesure_id: UUID):
    """Supprimer une mesure biométrique"""
    try:
        result = supabase_admin.table("mesures_biometriques").delete().eq("id_mesure", str(mesure_id)).execute()
        
        if not result.data:
            raise HTTPException(status_code=404, detail="Mesure biométrique non trouvée")
        
        return None
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la suppression: {str(e)}")


