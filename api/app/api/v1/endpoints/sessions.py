"""
Endpoints pour la gestion des sessions sport
"""

from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from uuid import UUID
from datetime import date
from app.core.database import supabase_admin
from app.schemas.session import SessionSportCreate, SessionSportUpdate, SessionSportRead

router = APIRouter()


@router.get("", response_model=List[SessionSportRead])
async def get_sessions(
    utilisateur_id: Optional[UUID] = None,
    date_debut: Optional[date] = None,
    date_fin: Optional[date] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000)
):
    """Récupérer la liste des sessions sport"""
    try:
        query = supabase_admin.table("sessions_sport").select("*")
        
        if utilisateur_id:
            query = query.eq("id_utilisateur", str(utilisateur_id))
        if date_debut:
            query = query.gte("date", str(date_debut))
        if date_fin:
            query = query.lte("date", str(date_fin))
        
        result = query.range(skip, skip + limit - 1).order("date", desc=True).execute()
        return result.data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la récupération: {str(e)}")


@router.get("/{session_id}", response_model=SessionSportRead)
async def get_session(session_id: UUID):
    """Récupérer une session par son ID"""
    try:
        result = supabase_admin.table("sessions_sport").select("*").eq("id_session", str(session_id)).execute()
        
        if not result.data:
            raise HTTPException(status_code=404, detail="Session non trouvée")
        
        return result.data[0]
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la récupération: {str(e)}")


@router.post("", response_model=SessionSportRead, status_code=201)
async def create_session(session: SessionSportCreate):
    """Créer une nouvelle session sport"""
    try:
        # Extraire les exercices si présents
        exercices = session.exercices if hasattr(session, 'exercices') else []
        session_data = session.model_dump(exclude={'exercices'})
        
        # Créer la session
        result = supabase_admin.table("sessions_sport").insert(session_data).execute()
        
        if not result.data:
            raise HTTPException(status_code=400, detail="Erreur lors de la création de la session")
        
        session_id = result.data[0]["id_session"]
        
        # Ajouter les exercices si présents
        if exercices:
            for exercice in exercices:
                exercice_data = exercice.model_dump()
                exercice_data["id_session"] = session_id
                supabase_admin.table("session_exercices").insert(exercice_data).execute()
        
        # Récupérer la session complète
        result = supabase_admin.table("sessions_sport").select("*").eq("id_session", session_id).execute()
        return result.data[0]
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la création: {str(e)}")


@router.put("/{session_id}", response_model=SessionSportRead)
async def update_session(session_id: UUID, session: SessionSportUpdate):
    """Mettre à jour une session sport"""
    try:
        data = session.model_dump(exclude_unset=True)
        
        if not data:
            raise HTTPException(status_code=400, detail="Aucune donnée à mettre à jour")
        
        result = supabase_admin.table("sessions_sport").update(data).eq("id_session", str(session_id)).execute()
        
        if not result.data:
            raise HTTPException(status_code=404, detail="Session non trouvée")
        
        return result.data[0]
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la mise à jour: {str(e)}")


@router.delete("/{session_id}", status_code=204)
async def delete_session(session_id: UUID):
    """Supprimer une session sport"""
    try:
        result = supabase_admin.table("sessions_sport").delete().eq("id_session", str(session_id)).execute()
        
        if not result.data:
            raise HTTPException(status_code=404, detail="Session non trouvée")
        
        return None
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la suppression: {str(e)}")

