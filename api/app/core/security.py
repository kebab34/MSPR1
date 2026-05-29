"""
Utilitaires de sécurité : vérification JWT Supabase
(Supabase récent : JWT ES256 + JWKS ; anciens projets / config : HS256 + JWT_SECRET)
"""

from __future__ import annotations  # permet d'utiliser les annotations de type avant leur déclaration

import json           # pour décoder la réponse JWKS (format JSON)
import time           # pour gérer l'expiration du cache JWKS
import urllib.error   # pour capturer les erreurs réseau
import urllib.request # pour faire des requêtes HTTP sans dépendance externe
from typing import Any, Optional  # pour typer les variables

from fastapi import HTTPException, status  # pour retourner des erreurs HTTP propres
from jose import JWTError, jwk, jwt        # librairie de décodage JWT (python-jose)

from app.core.config import settings  # importe la configuration (JWT_SECRET, SUPABASE_URL...)

# Cache en mémoire pour les clés JWKS (évite de les retélécharger à chaque requête)
# Contient un tuple (timestamp, données) ou None si pas encore chargé
_jwks_cache: Optional[tuple[float, dict[str, Any]]] = None
JWKS_TTL_SEC = 300  # durée de validité du cache : 5 minutes


def _invalidate_jwks_cache() -> None:
    """Vide le cache JWKS (appelé quand une clé kid est introuvable → rotation de clé)."""
    global _jwks_cache
    _jwks_cache = None


def _jwks_url() -> str:
    """Retourne l'URL de l'endpoint JWKS de Supabase (liste des clés publiques)."""
    return f"{settings.SUPABASE_URL.rstrip('/')}/auth/v1/.well-known/jwks.json"


def _fetch_jwks() -> dict[str, Any]:
    """
    Télécharge les clés publiques JWKS depuis Supabase.
    Utilise un cache de 5 minutes pour ne pas appeler Supabase à chaque requête.
    """
    global _jwks_cache
    now = time.time()  # heure actuelle en secondes
    if _jwks_cache is not None and now - _jwks_cache[0] < JWKS_TTL_SEC:
        return _jwks_cache[1]  # retourne le cache s'il est encore valide
    try:
        req = urllib.request.Request(_jwks_url(), method="GET")  # prépare la requête HTTP
        with urllib.request.urlopen(req, timeout=8) as resp:      # envoie la requête (timeout 8s)
            data = json.loads(resp.read().decode())               # décode la réponse JSON
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Impossible de charger les clés JWT Supabase (JWKS) : {e}",
        ) from e
    _jwks_cache = (now, data)  # met en cache avec le timestamp actuel
    return data


def _decode_es256(token: str) -> dict:
    """
    Décode un token JWT signé avec l'algorithme ES256 (Supabase récent).
    Cherche la clé publique correspondante dans le JWKS grâce au 'kid' (key ID) du header.
    """
    header = jwt.get_unverified_header(token)  # lit le header du token sans le vérifier
    kid = header.get("kid")                    # récupère l'identifiant de la clé utilisée
    if not kid:
        raise JWTError("JWT ES256 sans kid")   # un token ES256 doit toujours avoir un kid

    def _try_with(jwks_data: dict[str, Any]) -> Optional[dict]:
        """Cherche la clé correspondante dans le JWKS et décode le token."""
        raw = next((k for k in jwks_data.get("keys", []) if k.get("kid") == kid), None)  # cherche la clé par kid
        if not raw:
            return None  # clé introuvable dans ce JWKS
        pub = jwk.construct(raw)             # construit la clé publique depuis le JSON
        return jwt.decode(
            token,
            pub,
            algorithms=["ES256"],            # algorithme de décodage
            options={"verify_aud": False},   # ne vérifie pas l'audience (optionnel dans notre cas)
        )

    jwks_data = _fetch_jwks()               # récupère les clés (depuis le cache ou Supabase)
    payload = _try_with(jwks_data)
    if payload is None:
        _invalidate_jwks_cache()            # la clé n'est pas dans le cache → on le vide
        payload = _try_with(_fetch_jwks())  # retente avec les clés fraîchement téléchargées
    if payload is None:
        raise JWTError(f"Aucune clé JWKS pour kid={kid}")  # aucune clé trouvée même après refresh
    return payload


def verify_token(token: str) -> dict:
    """
    Vérifie et décode un token JWT Supabase.
    Supporte deux algorithmes selon la version de Supabase :
    - ES256 : Supabase récent (clés JWKS, asymétrique)
    - HS256 : anciens projets (clé secrète symétrique JWT_SECRET)
    Retourne le payload décodé (contient 'sub' = user_id, 'email', etc.)
    Lève une HTTPException 401 si le token est invalide ou expiré.
    """
    try:
        header = jwt.get_unverified_header(token)   # lit le header sans vérification
        alg = header.get("alg") or "HS256"          # récupère l'algorithme, HS256 par défaut
        if alg == "ES256":
            return _decode_es256(token)              # décodage via JWKS pour ES256
        return jwt.decode(
            token,
            settings.JWT_SECRET,                    # clé secrète symétrique pour HS256
            algorithms=[settings.JWT_ALGORITHM],
            options={"verify_aud": False},
        )
    except HTTPException:
        raise  # re-propage les HTTPException (ex: 503 si JWKS injoignable)
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token invalide ou expiré",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token invalide ou expiré",
            headers={"WWW-Authenticate": "Bearer"},
        )
