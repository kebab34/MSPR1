"""
Application FastAPI principale pour le projet MSPR
Domaine : Santé connectée et coaching personnalisé
"""

from fastapi import FastAPI                        # le framework web qui crée l'application
from fastapi.middleware.cors import CORSMiddleware # middleware qui gère les autorisations cross-origin (CORS)
from app.core.config import settings               # importe la configuration (URL, clés, préfixes...)
from app.api.v1.api import api_router              # importe toutes les routes de l'API v1

# Crée l'application FastAPI avec ses métadonnées (titre, description, version)
app = FastAPI(
    title="MSPR API - Santé Connectée",
    description="API pour la gestion de la santé connectée et du coaching personnalisé",
    version="1.0.0",
    docs_url="/docs",    # URL de la documentation Swagger (interface interactive)
    redoc_url="/redoc"   # URL de la documentation ReDoc (interface alternative)
)

# Ajoute le middleware CORS : autorise le frontend Next.js (localhost:3000/8000) à appeler l'API
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,  # liste des origines autorisées (définie dans config.py)
    allow_credentials=True,               # autorise l'envoi de cookies et headers d'authentification
    allow_methods=["*"],                  # autorise toutes les méthodes HTTP (GET, POST, PUT, DELETE...)
    allow_headers=["*"],                  # autorise tous les headers HTTP (Authorization, Content-Type...)
)

# Enregistre toutes les routes de l'API sous le préfixe /api/v1
app.include_router(api_router, prefix=settings.API_V1_PREFIX)

@app.get("/")
async def root():
    """Route racine : affiche un message de bienvenue et le lien vers la doc."""
    return {
        "message": "Bienvenue sur l'API MSPR - Santé Connectée",
        "version": "1.0.0",
        "docs": "/docs"   # renvoie vers la doc Swagger
    }

@app.get("/health")
async def health_check():
    """Route de health check : permet de vérifier que l'API est bien démarrée (utilisée par le dashboard)."""
    return {"status": "healthy"}
