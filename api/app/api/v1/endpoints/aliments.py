"""
Endpoints pour la gestion des aliments
"""

from fastapi import APIRouter, HTTPException, Query, Depends  # outils FastAPI
from typing import List, Optional                              # pour typer les retours et paramètres
from uuid import UUID                                          # pour valider les IDs au format UUID
from app.core.database import supabase_admin                  # client Supabase avec accès total
from app.schemas.aliment import AlimentCreate, AlimentUpdate, AlimentRead  # schémas de validation des données
from app.api.v1.deps import get_current_user                  # dépendance : vérifie que l'utilisateur est connecté

router = APIRouter()  # crée le router pour les routes /aliments


@router.get("", response_model=List[AlimentRead])
async def get_aliments(
    skip: int = Query(0, ge=0),           # nombre d'éléments à sauter (pagination, minimum 0)
    limit: int = Query(100, ge=1, le=1000),  # nombre d'éléments à retourner (entre 1 et 1000)
    search: Optional[str] = None,          # filtre de recherche par nom (optionnel)
    _u: dict = Depends(get_current_user),  # vérifie que l'utilisateur est connecté (token requis)
):
    """Récupère la liste des aliments, avec pagination et recherche optionnelle par nom."""
    try:
        query = supabase_admin.table("aliments").select("*")  # sélectionne toutes les colonnes

        if search:
            query = query.ilike("nom", f"%{search}%")  # filtre insensible à la casse (ILIKE en SQL)

        result = query.range(skip, skip + limit - 1).order("nom").execute()  # pagination + tri alphabétique
        return result.data  # retourne la liste des aliments
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la récupération: {str(e)}")


@router.get("/{aliment_id}", response_model=AlimentRead)
async def get_aliment(aliment_id: UUID, _u: dict = Depends(get_current_user)):
    """Récupère un aliment précis par son UUID."""
    try:
        result = supabase_admin.table("aliments").select("*").eq("id_aliment", str(aliment_id)).execute()
        # .eq = WHERE id_aliment = aliment_id

        if not result.data:
            raise HTTPException(status_code=404, detail="Aliment non trouvé")  # retourne 404 si absent

        return result.data[0]  # retourne le premier (et unique) résultat
    except HTTPException:
        raise  # relance les HTTPException sans les envelopper dans une erreur 500
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la récupération: {str(e)}")


@router.post("", response_model=AlimentRead, status_code=201)
async def create_aliment(aliment: AlimentCreate, _u: dict = Depends(get_current_user)):
    """Crée un nouvel aliment dans la base de données."""
    try:
        data = aliment.model_dump()  # convertit le schéma Pydantic en dictionnaire Python
        result = supabase_admin.table("aliments").insert(data).execute()  # insère en base

        if not result.data:
            raise HTTPException(status_code=400, detail="Erreur lors de la création")

        return result.data[0]  # retourne l'aliment créé avec son UUID généré par Supabase
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la création: {str(e)}")


@router.put("/{aliment_id}", response_model=AlimentRead)
async def update_aliment(
    aliment_id: UUID, aliment: AlimentUpdate, _u: dict = Depends(get_current_user)
):
    """Met à jour un aliment existant (tous les champs ou seulement certains)."""
    try:
        data = aliment.model_dump(exclude_unset=True)  # ne garde que les champs réellement envoyés

        if not data:
            raise HTTPException(status_code=400, detail="Aucune donnée à mettre à jour")

        result = supabase_admin.table("aliments").update(data).eq("id_aliment", str(aliment_id)).execute()
        # UPDATE aliments SET ... WHERE id_aliment = aliment_id

        if not result.data:
            raise HTTPException(status_code=404, detail="Aliment non trouvé")

        return result.data[0]
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la mise à jour: {str(e)}")


@router.delete("/{aliment_id}", status_code=204)
async def delete_aliment(aliment_id: UUID, _u: dict = Depends(get_current_user)):
    """Supprime un aliment par son UUID. Retourne 204 (No Content) si réussi."""
    try:
        result = supabase_admin.table("aliments").delete().eq("id_aliment", str(aliment_id)).execute()
        # DELETE FROM aliments WHERE id_aliment = aliment_id

        if not result.data:
            raise HTTPException(status_code=404, detail="Aliment non trouvé")

        return None  # 204 = succès sans corps de réponse
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la suppression: {str(e)}")
