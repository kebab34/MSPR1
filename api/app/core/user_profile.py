"""
Profil application (rôle, abonnement) lié à la table utilisateurs.
"""

import logging
from typing import Any, Optional

from app.core.database import supabase_admin

logger = logging.getLogger(__name__)

_COLS_FULL = (
    "id_utilisateur,email,app_role,type_abonnement,auth_id,"
    "nom,prenom,age,sexe,poids,taille,objectifs"
)
_COLS_MIN = "id_utilisateur,email,app_role,type_abonnement,auth_id"


def _fetch_row(cols: str, field: str, value: str) -> Optional[dict[str, Any]]:
    try:
        r = (
            supabase_admin.table("utilisateurs")
            .select(cols)
            .eq(field, value)
            .limit(1)
            .execute()
        )
        if r.data:
            return r.data[0]
    except Exception as e:
        logger.warning("Lecture profil (%s) échouée : %s", cols[:40], e)
        return None
    return None


def fetch_app_profile(auth_id: str, email: str) -> Optional[dict[str, Any]]:
    """
    Récupère la ligne utilisateurs liée à auth (auth_id) ou, à défaut, à l'email
    (liaison rétroactive de comptes créés avant auth_id).
    """
    row = _fetch_row(_COLS_FULL, "auth_id", auth_id)
    if row is None:
        row = _fetch_row(_COLS_MIN, "auth_id", auth_id)
    if row:
        return row

    if not email:
        return None
    row = _fetch_row(_COLS_FULL, "email", email)
    if row is None:
        row = _fetch_row(_COLS_MIN, "email", email)
    if not row:
        return None
    if not row.get("auth_id"):
        try:
            supabase_admin.table("utilisateurs").update({"auth_id": auth_id}).eq(
                "id_utilisateur", str(row["id_utilisateur"])
            ).execute()
        except Exception:
            pass
    row["auth_id"] = auth_id
    return row


def apply_admin_bootstrap(
    email: str, row: dict, admin_emails: list[str]
) -> dict[str, Any]:
    """Si l'email est listé en ADMIN, assure app_role=admin côté base."""
    em = (email or "").lower().strip()
    admins = {a.lower().strip() for a in admin_emails if a}
    if not admins or em not in admins:
        return row
    if str(row.get("app_role", "user")) == "admin":
        return row
    try:
        supabase_admin.table("utilisateurs").update({"app_role": "admin"}).eq(
            "id_utilisateur", str(row["id_utilisateur"])
        ).execute()
        row["app_role"] = "admin"
    except Exception:
        pass
    return row
