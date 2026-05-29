"""
Microservice de recommandation sportive — HealthAI Coach
Exposé sur le port 8002, séparé de l'API principale.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.core.config import settings
from app.core.database import close_connection
from app.api.endpoints import workout


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    await close_connection()


app = FastAPI(
    title="HealthAI Coach — Recommendation Service",
    description="Microservice de recommandation d'activités physiques personnalisées par IA",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(workout.router, prefix="/recommendations", tags=["Recommandations Sport"])


@app.get("/")
async def root():
    return {
        "service": "recommendation-service",
        "version": "1.0.0",
        "docs": "/docs",
    }


@app.get("/health")
async def health():
    return {"status": "healthy", "service": "recommendation-service"}
