"""
Endpoints d'authentification : register, login, me
"""

from fastapi import APIRouter, HTTPException, Depends, status
from app.core.database import supabase, supabase_admin
from app.schemas.auth import LoginRequest, RegisterRequest, TokenResponse, UserInfo
from app.api.v1.deps import get_current_user

router = APIRouter()


@router.post("/register", status_code=201)
async def register(data: RegisterRequest):
    """
    Crée un compte Supabase Auth et insère l'utilisateur dans la table utilisateurs.
    """
    try:
        auth_response = supabase.auth.sign_up(
            {"email": data.email, "password": data.password}
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Erreur Auth Supabase : {str(e)}")

    if not auth_response.user:
        raise HTTPException(status_code=400, detail="Impossible de créer le compte")

    # Insérer dans la table utilisateurs (sans mot de passe)
    try:
        utilisateur_data = {
            "email": data.email,
            "nom": data.nom,
            "prenom": data.prenom,
            "type_abonnement": "freemium",
        }
        supabase_admin.table("utilisateurs").insert(utilisateur_data).execute()
    except Exception:
        # L'utilisateur Auth est créé, on loggue l'erreur sans bloquer
        pass

    return {
        "message": "Compte créé avec succès. Vérifiez votre email si la confirmation est activée.",
        "email": data.email,
    }


@router.post("/login", response_model=TokenResponse)
async def login(data: LoginRequest):
    """
    Authentifie l'utilisateur et retourne un token JWT Supabase.
    """
    try:
        auth_response = supabase.auth.sign_in_with_password(
            {"email": data.email, "password": data.password}
        )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou mot de passe incorrect",
        )

    if not auth_response.session:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou mot de passe incorrect",
        )

    return TokenResponse(
        access_token=auth_response.session.access_token,
        expires_in=auth_response.session.expires_in,
    )


@router.get("/me", response_model=UserInfo)
async def get_me(current_user: dict = Depends(get_current_user)):
    """
    Retourne les informations de l'utilisateur connecté (extrait du token JWT).
    """
    return UserInfo(id=current_user["id"], email=current_user["email"])
