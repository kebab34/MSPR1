"""
Endpoints pour la gestion du journal alimentaire
"""

from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from uuid import UUID
from datetime import date
from app.core.database import supabase_admin
from app.schemas.journal import JournalAlimentaireCreate, JournalAlimentaireUpdate, JournalAlimentaireRead

router = APIRouter()


@router.get("", response_model=List[JournalAlimentaireRead])
async def get_journal_entries(
    utilisateur_id: Optional[UUID] = None,
    date_debut: Optional[date] = None,
    date_fin: Optional[date] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000)
):
    """Récupérer les entrées du journal alimentaire"""
    try:
        query = supabase_admin.table("journal_alimentaire").select("*")
        
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


@router.get("/{journal_id}", response_model=JournalAlimentaireRead)
async def get_journal_entry(journal_id: UUID):
    """Récupérer une entrée du journal par son ID"""
    try:
        result = supabase_admin.table("journal_alimentaire").select("*").eq("id_journal", str(journal_id)).execute()
        
        if not result.data:
            raise HTTPException(status_code=404, detail="Entrée du journal non trouvée")
        
        return result.data[0]
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la récupération: {str(e)}")


@router.post("", response_model=JournalAlimentaireRead, status_code=201)
async def create_journal_entry(entry: JournalAlimentaireCreate):
    """Créer une nouvelle entrée dans le journal alimentaire"""
    try:
        # Vérifier qu'on a soit un aliment soit une recette
        if not entry.id_aliment and not entry.id_recette:
            raise HTTPException(status_code=400, detail="Il faut spécifier soit un aliment soit une recette")
        if entry.id_aliment and entry.id_recette:
            raise HTTPException(status_code=400, detail="Il faut spécifier soit un aliment soit une recette, pas les deux")
        
        data = entry.model_dump()
        result = supabase_admin.table("journal_alimentaire").insert(data).execute()
        
        if not result.data:
            raise HTTPException(status_code=400, detail="Erreur lors de la création")
        
        return result.data[0]
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la création: {str(e)}")


@router.put("/{journal_id}", response_model=JournalAlimentaireRead)
async def update_journal_entry(journal_id: UUID, entry: JournalAlimentaireUpdate):
    """Mettre à jour une entrée du journal"""
    try:
        data = entry.model_dump(exclude_unset=True)
        
        if not data:
            raise HTTPException(status_code=400, detail="Aucune donnée à mettre à jour")
        
        result = supabase_admin.table("journal_alimentaire").update(data).eq("id_journal", str(journal_id)).execute()
        
        if not result.data:
            raise HTTPException(status_code=404, detail="Entrée du journal non trouvée")
        
        return result.data[0]
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la mise à jour: {str(e)}")


@router.delete("/{journal_id}", status_code=204)
async def delete_journal_entry(journal_id: UUID):
    """Supprimer une entrée du journal"""
    try:
        result = supabase_admin.table("journal_alimentaire").delete().eq("id_journal", str(journal_id)).execute()
        
        if not result.data:
            raise HTTPException(status_code=404, detail="Entrée du journal non trouvée")
        
        return None
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la suppression: {str(e)}")


