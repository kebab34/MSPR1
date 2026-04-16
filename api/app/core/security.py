"""
Utilitaires de sécurité : vérification JWT Supabase
"""

from jose import JWTError, jwt
from fastapi import HTTPException, status
from app.core.config import settings


def verify_token(token: str) -> dict:
    """Vérifie et décode un token JWT Supabase"""
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET,
            algorithms=[settings.JWT_ALGORITHM],
            options={"verify_aud": False},
        )
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token invalide ou expiré",
            headers={"WWW-Authenticate": "Bearer"},
        )
