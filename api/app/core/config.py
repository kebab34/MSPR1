"""
Configuration de l'application utilisant Pydantic Settings
"""

import os                                    # pour accéder aux variables d'environnement si besoin
from pathlib import Path                     # pour construire les chemins de fichiers
from pydantic_settings import BaseSettings   # classe de base Pydantic qui lit automatiquement les variables d'env
from typing import List                      # pour typer les listes

# Remonte 4 niveaux depuis ce fichier pour trouver la racine du projet (là où se trouve le .env)
BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
ENV_FILE = BASE_DIR / ".env"  # chemin complet vers le fichier .env


class Settings(BaseSettings):
    """Classe de configuration : chaque attribut est lu automatiquement depuis le fichier .env."""

    # Connexion à Supabase
    SUPABASE_URL: str          # URL de l'instance Supabase (ex: http://localhost:54321)
    SUPABASE_KEY: str          # clé publique Supabase (accès limité, utilisée par les clients)
    SUPABASE_SERVICE_KEY: str  # clé de service Supabase (accès total, utilisée côté serveur uniquement)

    # Connexion PostgreSQL directe (pour les opérations SQL avancées)
    DATABASE_URL: str  # ex: postgresql://postgres:postgres@host.docker.internal:54322/postgres

    # Authentification JWT
    JWT_SECRET: str              # clé secrète pour signer et vérifier les tokens JWT
    JWT_ALGORITHM: str = "HS256" # algorithme de signature (HS256 par défaut, ES256 si Supabase moderne)
    JWT_EXPIRATION: int = 3600   # durée de validité d'un token en secondes (1 heure)

    # Emails des administrateurs : ces comptes reçoivent automatiquement le rôle admin à la connexion
    ADMIN_EMAILS: str = ""  # liste séparée par des virgules, ex: "admin@test.com,autre@test.com"

    # Clé API Google Gemini pour l'IA (nutrition + recommandations) — gratuit sur aistudio.google.com
    GEMINI_API_KEY: str = ""
    # Mode démo : retourne des données fictives si True (utile sans quota Gemini)
    MOCK_AI: bool = False

    # Origines autorisées pour le CORS (frontends qui peuvent appeler l'API)
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",    # Next.js en dev
        "http://127.0.0.1:3000",
        "http://localhost:8000",    # Next.js en Docker
        "http://127.0.0.1:8000",
        "http://localhost:8003",
        "http://127.0.0.1:8003",
    ]

    # Préfixe de toutes les routes de l'API
    API_V1_PREFIX: str = "/api/v1"  # toutes les routes commencent par /api/v1/...

    class Config:
        env_file = str(ENV_FILE) if ENV_FILE.exists() else None  # lit le .env s'il existe
        env_file_encoding = "utf-8"   # encodage du fichier .env
        case_sensitive = True          # les noms de variables sont sensibles à la casse
        extra = "ignore"               # ignore les variables du .env qui ne sont pas déclarées ici


settings = Settings()  # crée une instance unique de la config, utilisée dans tout le projet


def get_admin_email_set() -> List[str]:
    """Retourne la liste des emails admin en minuscules, nettoyée des espaces."""
    if not (settings.ADMIN_EMAILS and settings.ADMIN_EMAILS.strip()):
        return []  # pas d'admins configurés
    return [e.strip().lower() for e in settings.ADMIN_EMAILS.split(",") if e.strip()]  # split sur la virgule
