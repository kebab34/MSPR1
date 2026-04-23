"""
Endpoints d'authentification : register, login, me
"""

import logging
from typing import Any, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from app.core.database import supabase, supabase_admin
from app.core.config import get_admin_email_set
from app.core.user_profile import apply_admin_bootstrap, fetch_app_profile
from app.schemas.auth import (
    LoginRequest,
    ProfileMeUpdate,
    RegisterRequest,
    RegisterResponse,
    TokenResponse,
    UserInfo,
)
from app.api.v1.deps import get_current_user

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/register", response_model=RegisterResponse, status_code=201)
async def register(data: RegisterRequest):
    """
    Crée un compte Supabase Auth et insère l'utilisateur dans la table utilisateurs.
    Si Supabase renvoie une session (souvent sans confirmation d'email), les tokens
    sont inclus pour que le client n'ait pas à rappeler /login.
    """
    payload: dict = {"email": data.email, "password": data.password}
    meta = {}
    if data.nom:
        meta["nom"] = data.nom
    if data.prenom:
        meta["prenom"] = data.prenom
    if meta:
        payload["options"] = {"data": meta}

    try:
        auth_response = supabase.auth.sign_up(payload)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Erreur Auth Supabase : {str(e)}")

    if not auth_response.user:
        raise HTTPException(status_code=400, detail="Impossible de créer le compte")

    # La ligne public.utilisateurs est créée par le trigger SQL (migration
    # utilisateurs_on_auth_user_insert). Insert API en secours si la migration
    # n’est pas encore appliquée.
    auth_uid = str(auth_response.user.id)
    utilisateur_data: dict = {
        "email": data.email,
        "type_abonnement": "freemium",
        "app_role": "user",
        "auth_id": auth_uid,
    }
    if data.nom is not None:
        utilisateur_data["nom"] = data.nom
    if data.prenom is not None:
        utilisateur_data["prenom"] = data.prenom
    try:
        supabase_admin.table("utilisateurs").upsert(
            utilisateur_data, on_conflict="email"
        ).execute()
    except Exception as e:
        logger.warning(
            "Upsert utilisateurs après inscription ignoré ou en échec (trigger DB peut avoir déjà créé la ligne) : %s",
            e,
            exc_info=True,
        )

    msg = "Compte créé avec succès. Vérifiez votre email si la confirmation est activée."
    out: dict = {"message": msg, "email": data.email}
    if auth_response.session:
        out["access_token"] = auth_response.session.access_token
        out["expires_in"] = auth_response.session.expires_in
    return out


def _format_auth_login_error(exc: Exception) -> str:
    """Message lisible pour l'utilisateur (Supabase / GoTrue)."""
    raw = (
        getattr(exc, "message", None)
        or getattr(exc, "msg", None)
        or str(exc)
    )
    low = raw.lower()
    if "email not confirmed" in low or "email_not_confirmed" in low:
        return (
            "E-mail non confirmé : ouvrez le lien reçu par e-mail, "
            "ou désactivez la confirmation dans le tableau Supabase (Auth > Providers > Email)."
        )
    if "invalid login" in low or "invalid credentials" in low:
        return "E-mail ou mot de passe incorrect."
    if raw and len(raw) < 200:
        return raw
    return "E-mail ou mot de passe incorrect."


@router.post("/login", response_model=TokenResponse)
async def login(data: LoginRequest):
    """
    Authentifie l'utilisateur et retourne un token JWT Supabase.
    """
    try:
        auth_response = supabase.auth.sign_in_with_password(
            {"email": data.email, "password": data.password}
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=_format_auth_login_error(e),
        ) from e

    if not auth_response.session:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Connexion refusée (aucune session). Vérifiez la configuration Supabase Auth.",
        )

    return TokenResponse(
        access_token=auth_response.session.access_token,
        expires_in=auth_response.session.expires_in,
    )


def _safe_int_profil(v: Any) -> Optional[int]:
    if v is None or v == "":
        return None
    try:
        return int(float(v))
    except (TypeError, ValueError):
        return None


def _safe_float_profil(v: Any) -> Optional[float]:
    if v is None or v == "":
        return None
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def _safe_objectifs_profil(v: Any) -> Optional[list[str]]:
    if v is None:
        return None
    if isinstance(v, list):
        return [str(x) for x in v]
    return None


def _prof_to_userinfo(user_id: str, email: str, prof: Optional[dict[str, Any]]) -> UserInfo:
    if not prof:
        return UserInfo(
            id=user_id,
            email=email,
            id_utilisateur=None,
            app_role="user",
            type_abonnement="freemium",
        )
    # Données BDD parfois incohérentes (import ETL, saisies libres) : ne jamais faire
    # échouer GET /me, sinon le client perd la session après un login réussi.
    try:
        obj_list = _safe_objectifs_profil(prof.get("objectifs"))
        return UserInfo(
            id=user_id,
            email=email,
            id_utilisateur=str(prof.get("id_utilisateur", "")) or None,
            app_role=str(prof.get("app_role", "user")),
            type_abonnement=str(prof.get("type_abonnement", "freemium") or "freemium"),
            nom=prof.get("nom") if prof.get("nom") is not None else None,
            prenom=prof.get("prenom") if prof.get("prenom") is not None else None,
            age=_safe_int_profil(prof.get("age")),
            sexe=prof.get("sexe") if prof.get("sexe") is not None else None,
            poids=_safe_float_profil(prof.get("poids")),
            taille=_safe_float_profil(prof.get("taille")),
            objectifs=obj_list,
        )
    except Exception:
        logger.warning(
            "Profil utilisateur partiellement illisible, réponse /me minimale (id=%s)",
            user_id,
            exc_info=True,
        )
        return UserInfo(
            id=user_id,
            email=email,
            id_utilisateur=str(prof.get("id_utilisateur", "")) or None,
            app_role=str(prof.get("app_role", "user")),
            type_abonnement=str(prof.get("type_abonnement", "freemium") or "freemium"),
        )


@router.get("/me", response_model=UserInfo)
async def get_me(current_user: dict = Depends(get_current_user)):
    """
    Profil Auth + rôle (admin/user) et plan (type_abonnement) depuis la table utilisateurs.
    """
    user_id = current_user["id"]
    email = current_user.get("email", "")
    prof = fetch_app_profile(user_id, email)
    if not prof:
        return _prof_to_userinfo(user_id, email, None)
    prof = apply_admin_bootstrap(email, prof, get_admin_email_set())
    return _prof_to_userinfo(user_id, email, prof)


@router.patch("/me", response_model=UserInfo)
async def patch_me(
    body: ProfileMeUpdate,
    current_user: dict = Depends(get_current_user),
):
    """
    Met à jour la fiche métier de l'utilisateur connecté (champs profil + freemium/premium).
    """
    user_id = current_user["id"]
    email = current_user.get("email", "")
    prof = fetch_app_profile(user_id, email)
    if not prof:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Aucun profil métier lié à ce compte.",
        )
    prof = apply_admin_bootstrap(email, prof, get_admin_email_set())
    uid = str(prof.get("id_utilisateur", ""))
    if not uid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Profil invalide (id_utilisateur manquant).",
        )
    data = body.model_dump(exclude_unset=True)
    if not data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Aucun champ à mettre à jour.",
        )
    try:
        supabase_admin.table("utilisateurs").update(data).eq(
            "id_utilisateur", uid
        ).execute()
    except Exception as e:
        logger.exception("patch_me update")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la mise à jour : {e!s}",
        ) from e
    prof2 = fetch_app_profile(user_id, email)
    if prof2:
        prof2 = apply_admin_bootstrap(email, prof2, get_admin_email_set())
    return _prof_to_userinfo(user_id, email, prof2)
