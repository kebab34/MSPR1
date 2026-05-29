"""
Endpoints du moteur de recommandation sportive.
"""

from fastapi import APIRouter, HTTPException, Query
from app.models.recommendation import WorkoutRequest, WorkoutResponse, FeedbackRequest, FeedbackResponse
from app.services import engine

router = APIRouter()


@router.post("/generate", response_model=WorkoutResponse, status_code=201)
async def generer_programme(req: WorkoutRequest):
    """
    Génère un programme d'entraînement hebdomadaire personnalisé via IA.
    Le programme est stocké en MongoDB pour consultation ultérieure.
    """
    try:
        return await engine.generer_programme(req)
    except ValueError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur interne : {str(e)}")


@router.get("/history/{utilisateur_id}")
async def historique_recommandations(
    utilisateur_id: str,
    limit: int = Query(10, ge=1, le=50),
):
    """Retourne l'historique des programmes générés pour un utilisateur."""
    try:
        return await engine.get_historique(utilisateur_id, limit)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la récupération : {str(e)}")


@router.post("/feedback", response_model=FeedbackResponse, status_code=201)
async def soumettre_feedback(req: FeedbackRequest):
    """
    Enregistre le retour de l'utilisateur sur une recommandation.
    Ces feedbacks permettront l'amélioration future du moteur.
    """
    try:
        feedback_id = await engine.enregistrer_feedback(req.model_dump())
        return FeedbackResponse(
            message="Feedback enregistré avec succès.",
            recommendation_id=req.recommendation_id,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de l'enregistrement : {str(e)}")
