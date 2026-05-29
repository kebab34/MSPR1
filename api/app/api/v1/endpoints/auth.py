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

router = APIRouter()  # router pour les routes /auth
logger = logging.getLogger(__name__)


@router.post("/register", response_model=RegisterResponse, status_code=201)
async def register(data: RegisterRequest):
    """
    Crée un compte utilisateur :
    1. Crée le compte dans Supabase Auth (email + mot de passe)
    2. Insère la ligne dans la table utilisateurs (via upsert de secours si le trigger SQL ne l'a pas fait)
    3. Retourne un token directement si Supabase fournit une session (pas besoin de rappeler /login)
    """
    payload: dict = {"email": data.email, "password": data.password}  # données pour Supabase Auth
    meta = {}
    if data.nom:
        meta["nom"] = data.nom       # ajoute le nom dans les métadonnées Auth si fourni
    if data.prenom:
        meta["prenom"] = data.prenom # ajoute le prénom dans les métadonnées Auth si fourni
    if meta:
        payload["options"] = {"data": meta}  # passe les métadonnées à Supabase

    try:
        auth_response = supabase.auth.sign_up(payload)  # crée le compte dans Supabase Auth
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Erreur Auth Supabase : {str(e)}")

    if not auth_response.user:
        raise HTTPException(status_code=400, detail="Impossible de créer le compte")

    # Récupère l'UUID généré par Supabase Auth pour cet utilisateur
    auth_uid = str(auth_response.user.id)
    utilisateur_data: dict = {
        "email": data.email,
        "type_abonnement": "freemium",  # abonnement par défaut à l'inscription
        "app_role": "user",             # rôle par défaut
        "auth_id": auth_uid,            # lien avec Supabase Auth
    }
    if data.nom is not None:
        utilisateur_data["nom"] = data.nom
    if data.prenom is not None:
        utilisateur_data["prenom"] = data.prenom
    try:
        # Upsert de secours : si le trigger SQL a déjà créé la ligne, on la met juste à jour
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
        # Si Supabase retourne déjà une session, on inclut le token pour éviter un double appel /login
        out["access_token"] = auth_response.session.access_token
        out["expires_in"] = auth_response.session.expires_in
    return out


def _format_auth_login_error(exc: Exception) -> str:
    """Traduit les erreurs Supabase en messages lisibles pour l'utilisateur."""
    raw = (
        getattr(exc, "message", None)  # essaie d'abord l'attribut "message"
        or getattr(exc, "msg", None)   # puis "msg"
        or str(exc)                    # sinon convertit en string
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
        return raw  # retourne le message brut s'il est court et lisible
    return "E-mail ou mot de passe incorrect."  # message générique par défaut


@router.post("/login", response_model=TokenResponse)
async def login(data: LoginRequest):
    """
    Authentifie l'utilisateur avec email + mot de passe.
    Retourne un token JWT Supabase à utiliser dans le header Authorization de toutes les requêtes suivantes.
    """
    logger.info("LOGIN TENTATIVE email=%s", data.email)
    try:
        auth_response = supabase.auth.sign_in_with_password(
            {"email": data.email, "password": data.password}  # envoie les credentials à Supabase Auth
        )
    except Exception as e:
        logger.error("LOGIN ERREUR email=%s erreur=%s", data.email, str(e)[:300])
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=_format_auth_login_error(e),  # message d'erreur traduit
        ) from e

    if not auth_response.session:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Connexion refusée (aucune session). Vérifiez la configuration Supabase Auth.",
        )

    return TokenResponse(
        access_token=auth_response.session.access_token,  # le token JWT à utiliser
        expires_in=auth_response.session.expires_in,       # durée de validité en secondes
    )


def _safe_int_profil(v: Any) -> Optional[int]:
    """Convertit une valeur en int sans planter si la valeur est None ou invalide."""
    if v is None or v == "":
        return None
    try:
        return int(float(v))  # float() d'abord pour gérer "75.0" → 75
    except (TypeError, ValueError):
        return None


def _safe_float_profil(v: Any) -> Optional[float]:
    """Convertit une valeur en float sans planter si la valeur est None ou invalide."""
    if v is None or v == "":
        return None
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def _safe_objectifs_profil(v: Any) -> Optional[list[str]]:
    """Convertit les objectifs en liste de strings, retourne None si la valeur est absente."""
    if v is None:
        return None
    if isinstance(v, list):
        return [str(x) for x in v]  # s'assure que tous les éléments sont des strings
    return None


def _prof_to_userinfo(user_id: str, email: str, prof: Optional[dict[str, Any]]) -> UserInfo:
    """
    Construit l'objet UserInfo retourné par /me à partir du profil BDD.
    Ne plante jamais : si les données sont corrompues, retourne un profil minimal.
    """
    if not prof:
        # Profil absent → retourne uniquement les infos Auth
        return UserInfo(
            id=user_id,
            email=email,
            id_utilisateur=None,
            app_role="user",
            type_abonnement="freemium",
        )
    try:
        obj_list = _safe_objectifs_profil(prof.get("objectifs"))  # convertit les objectifs en liste
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
        # Si le profil est partiellement illisible, retourne un profil minimal sans planter
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
    Retourne le profil complet de l'utilisateur connecté :
    infos Auth (id, email) + infos BDD (rôle, abonnement, poids, taille, objectifs...).
    """
    user_id = current_user["id"]
    email = current_user.get("email", "")
    prof = fetch_app_profile(user_id, email)  # récupère le profil depuis la table utilisateurs
    if not prof:
        return _prof_to_userinfo(user_id, email, None)  # retourne un profil minimal si absent
    prof = apply_admin_bootstrap(email, prof, get_admin_email_set())  # promouvoit si email admin
    return _prof_to_userinfo(user_id, email, prof)


@router.patch("/me", response_model=UserInfo)
async def patch_me(
    body: ProfileMeUpdate,
    current_user: dict = Depends(get_current_user),
):
    """
    Met à jour les informations de profil de l'utilisateur connecté
    (poids, taille, objectifs, type_abonnement...).
    Seuls les champs envoyés dans le body sont modifiés.
    """
    user_id = current_user["id"]
    email = current_user.get("email", "")
    prof = fetch_app_profile(user_id, email)  # récupère le profil actuel
    if not prof:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Aucun profil métier lié à ce compte.",
        )
    prof = apply_admin_bootstrap(email, prof, get_admin_email_set())
    uid = str(prof.get("id_utilisateur", ""))  # récupère l'UUID de la table utilisateurs
    if not uid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Profil invalide (id_utilisateur manquant).",
        )
    data = body.model_dump(exclude_unset=True)  # ne garde que les champs réellement envoyés
    if not data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Aucun champ à mettre à jour.",
        )
    try:
        supabase_admin.table("utilisateurs").update(data).eq(
            "id_utilisateur", uid  # UPDATE utilisateurs SET ... WHERE id_utilisateur = uid
        ).execute()
    except Exception as e:
        logger.exception("patch_me update")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la mise à jour : {e!s}",
        ) from e
    prof2 = fetch_app_profile(user_id, email)  # relit le profil après mise à jour pour retourner les nouvelles valeurs
    if prof2:
        prof2 = apply_admin_bootstrap(email, prof2, get_admin_email_set())
    return _prof_to_userinfo(user_id, email, prof2)
