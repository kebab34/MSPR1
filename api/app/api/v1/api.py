"""
Router principal pour l'API v1 — regroupe tous les sous-routers en un seul.
"""

from fastapi import APIRouter  # classe qui regroupe des routes FastAPI
from app.api.v1.endpoints import health, utilisateurs, aliments, exercices, journal, sessions, mesures, auth, nutrition_ai
# importe les routers de chaque ressource métier

api_router = APIRouter()  # crée le router principal qui contiendra tous les autres

# Routes d'authentification (publiques — pas besoin de token pour s'inscrire ou se connecter)
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
# → /api/v1/auth/login, /api/v1/auth/register, /api/v1/auth/me

# Routes de health check
api_router.include_router(health.router, prefix="/health", tags=["health"])
# → /api/v1/health

# Routes des ressources métier (toutes protégées par JWT)
api_router.include_router(utilisateurs.router, prefix="/utilisateurs", tags=["utilisateurs"])
api_router.include_router(aliments.router, prefix="/aliments", tags=["aliments"])
api_router.include_router(exercices.router, prefix="/exercices", tags=["exercices"])
api_router.include_router(journal.router, prefix="/journal", tags=["journal"])
api_router.include_router(sessions.router, prefix="/sessions", tags=["sessions"])
api_router.include_router(mesures.router, prefix="/mesures", tags=["mesures"])

# Routes IA — nutrition (analyse photo + plan de repas)
api_router.include_router(nutrition_ai.router, prefix="/ai/nutrition", tags=["IA - Nutrition"])
# → /api/v1/ai/nutrition/analyze-photo
# → /api/v1/ai/nutrition/meal-plan
