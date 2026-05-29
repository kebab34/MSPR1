"""
Dépendances FastAPI — authentification et contrôle des rôles.
Ces fonctions sont injectées dans les routes via Depends() pour protéger les endpoints.
"""

from fastapi import Depends, HTTPException, status             # outils FastAPI pour les dépendances et erreurs HTTP
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer  # pour lire le header Authorization
from app.core.security import verify_token                     # fonction de vérification du token JWT
from app.core.config import get_admin_email_set                # retourne la liste des emails admin
from app.core.user_profile import apply_admin_bootstrap, fetch_app_profile  # fonctions de profil utilisateur

security = HTTPBearer()  # lit automatiquement le header "Authorization: Bearer <token>" sur chaque requête


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),  # FastAPI injecte le token automatiquement
) -> dict:
    """
    Dépendance de base : vérifie que le token JWT est valide.
    Retourne un dict avec l'id (sub) et l'email de l'utilisateur connecté.
    Utilisée sur toutes les routes qui nécessitent une connexion.
    """
    payload = verify_token(credentials.credentials)  # décode et valide le token JWT
    user_id: str = payload.get("sub")                # "sub" = subject = identifiant unique de l'utilisateur
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token invalide : champ 'sub' manquant",
        )
    return {"id": user_id, "email": payload.get("email", "")}  # retourne l'identité de base


async def require_admin(user: dict = Depends(get_current_user)) -> dict:
    """
    Dépendance stricte : vérifie que l'utilisateur connecté a le rôle 'admin'.
    Lève une erreur 403 si ce n'est pas le cas.
    Utilisée sur les routes réservées aux admins (ex: liste des utilisateurs, analytics).
    """
    prof = fetch_app_profile(user["id"], user.get("email", ""))  # récupère le profil depuis la base
    if not prof:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Aucun profil métier lié à ce compte. Contactez un administrateur.",
        )
    prof = apply_admin_bootstrap(
        user.get("email", ""), prof, get_admin_email_set()  # promouvoit automatiquement si email admin
    )
    if str(prof.get("app_role", "user")) != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Réservé aux administrateurs",
        )
    return {**user, "profile": prof}  # retourne l'utilisateur enrichi avec son profil


async def get_current_profile(user: dict = Depends(get_current_user)) -> dict:
    """
    Dépendance enrichie : retourne l'utilisateur connecté avec son id_utilisateur (UUID en base)
    et son app_role (user ou admin).
    Utilisée sur les routes qui ont besoin de l'id_utilisateur pour filtrer les données.
    """
    prof = fetch_app_profile(user["id"], user.get("email", ""))  # récupère le profil depuis la base
    if not prof:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Aucun profil métier lié à ce compte.",
        )
    prof = apply_admin_bootstrap(user.get("email", ""), prof, get_admin_email_set())
    id_utilisateur = str(prof.get("id_utilisateur") or "")  # récupère l'UUID de la table utilisateurs
    if not id_utilisateur:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Profil incomplet (id_utilisateur manquant).",
        )
    return {
        **user,                                          # reprend id et email de base
        "id_utilisateur": id_utilisateur,               # ajoute l'UUID de la table utilisateurs
        "app_role": str(prof.get("app_role", "user")),  # ajoute le rôle (user ou admin)
    }


async def require_user(user: dict = Depends(get_current_user)) -> dict:
    """
    Dépendance simple : accepte tout utilisateur connecté (user ou admin).
    Utilisée sur les routes accessibles à tous les utilisateurs authentifiés.
    """
    return user  # retourne l'utilisateur tel quel, juste vérifié qu'il est connecté
