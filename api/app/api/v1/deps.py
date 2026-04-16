"""
Dépendances FastAPI réutilisables (auth, etc.)
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.core.security import verify_token

security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> dict:
    """
    Dépendance qui extrait et valide le token Bearer.
    Retourne les infos de l'utilisateur connecté.
    """
    payload = verify_token(credentials.credentials)
    user_id: str = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token invalide : champ 'sub' manquant",
        )
    return {"id": user_id, "email": payload.get("email", "")}
