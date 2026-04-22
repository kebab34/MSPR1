"""
Session Streamlit : JWT Supabase / API, profil (rôle, plan) et garde d'accès.
"""

from __future__ import annotations

import streamlit as st
from typing import Optional, Dict, Any

from utils.api_client import api_client, get_api_token, set_api_token
from utils.flash import flash_error, flash_success, flash_warning, render_flash


def list_utilisateurs_for_pickers() -> list:
    """
    Admins : liste complète. Utilisateurs : uniquement leur fiche (id issu de /auth/me).
    """
    p = st.session_state.get("user_profile") or {}
    if p.get("app_role") == "admin":
        try:
            return api_client.get("/utilisateurs")
        except Exception:
            return []
    iu = p.get("id_utilisateur")
    if not iu:
        return []
    return [
        {
            "id_utilisateur": iu,
            "prenom": (p.get("email") or "?").split("@")[0],
            "nom": "",
            "email": p.get("email", ""),
        }
    ]


def _profile() -> dict:
    return st.session_state.get("user_profile") or {}


def refresh_profile() -> Optional[Dict[str, Any]]:
    """Recharge le profil via GET /auth/me (ou None si non connecté / erreur)."""
    if not get_api_token():
        st.session_state.pop("user_profile", None)
        return None
    try:
        p = api_client.me()
        st.session_state["user_profile"] = p
        st.session_state.pop("auth_profile_error", None)
        return p
    except Exception as e:
        set_api_token(None)
        st.session_state.pop("user_profile", None)
        err_s = str(e)
        if "401" in err_s or "403" in err_s or "invalide" in err_s.lower() or "expir" in err_s.lower():
            st.session_state["auth_profile_error"] = (
                "**Session rejetée par l’API** — le secret JWT ne correspond souvent pas à Supabase. "
                "Dans le fichier `.env` de l’API, `JWT_SECRET` doit être **exactement** le "
                "« JWT Secret » (Settings → API) du projet Supabase, ou la valeur de "
                "`npx supabase status` (JWT secret) en local. Puis redémarre le conteneur `api`."
            )
        else:
            st.session_state["auth_profile_error"] = f"Impossible de charger le profil : {err_s}"
        return None


def ensure_authenticated() -> None:
    """Bloque la page si l'utilisateur n'est pas connecté (JWT valide + profil)."""
    # Affiche d’abord les messages retenus (inscription, etc.) : survivent au rerun
    render_flash()

    t = get_api_token()
    if t and not st.session_state.get("user_profile"):
        if refresh_profile():
            return
    if get_api_token() and st.session_state.get("user_profile"):
        return

    if err_b := st.session_state.pop("auth_profile_error", None):
        st.error(err_b)

    st.markdown("### Connexion à l'application")
    st.caption(
        "Créez un compte : rôle **admin** + plan **Gratuit (freemium)** sont enregistrés à l’inscription."
    )

    tab_login, tab_register = st.tabs(["Se connecter", "Créer un compte"])

    with tab_login:
        with st.form("streamlit_auth_login", clear_on_submit=False):
            email = st.text_input("Email", placeholder="vous@exemple.com", key="login_email")
            password = st.text_input("Mot de passe", type="password", key="login_password")
            sub = st.form_submit_button("Se connecter", type="primary", use_container_width=True)
            if sub:
                if not email or not password:
                    st.warning("Saisissez l'email et le mot de passe.")
                else:
                    try:
                        r = api_client.login(email.strip(), password)
                        set_api_token(r["access_token"])
                        if refresh_profile():
                            flash_success("Connexion réussie. Bienvenue !")
                            st.rerun()
                        flash_error("Connexion : la session n’a pas pu être validée. Vérifiez la configuration (JWT, API).")
                        st.rerun()
                    except Exception as e:
                        flash_error(f"Connexion refusée : {e}")
                        st.rerun()

    with tab_register:
        with st.form("streamlit_auth_register", clear_on_submit=False):
            st.caption(
                "Compte **admin** + plan **Gratuit (freemium)** enregistrés à la création. "
                "Vous compléterez le détail sur la page **Mon profil**."
            )
            r_email = st.text_input("Email *", placeholder="vous@exemple.com", key="reg_email")
            r_prenom = st.text_input("Prénom", key="reg_prenom")
            r_nom = st.text_input("Nom", key="reg_nom")
            r_pw = st.text_input("Mot de passe *", type="password", key="reg_pw", help="Au moins 6 caractères selon la config Supabase.")
            r_pw2 = st.text_input("Confirmer le mot de passe *", type="password", key="reg_pw2")
            reg_sub = st.form_submit_button("Créer mon compte", type="primary", use_container_width=True)
            if reg_sub:
                if not r_email or not r_pw:
                    st.warning("Email et mot de passe obligatoires.")
                elif r_pw != r_pw2:
                    st.error("Les mots de passe ne correspondent pas.")
                else:
                    try:
                        res = api_client.register(
                            email=r_email.strip(),
                            password=r_pw,
                            prenom=r_prenom.strip() or None,
                            nom=r_nom.strip() or None,
                        )
                        api_msg = (res.get("message") or "").strip() or "Compte enregistré (plan Gratuit)."
                        if res.get("access_token"):
                            set_api_token(res["access_token"])
                            if refresh_profile():
                                flash_success(f"{api_msg} Vous êtes connecté.")
                                st.rerun()
                            flash_success(
                                f"{api_msg} La connexion automatique a échoué — "
                                "voir l’alerte de session ci-dessus (souvent JWT_SECRET ≠ Supabase)."
                            )
                            st.rerun()
                        else:
                            try:
                                r = api_client.login(r_email.strip(), r_pw)
                                set_api_token(r["access_token"])
                                if refresh_profile():
                                    flash_success(f"{api_msg} Vous êtes connecté.")
                                    st.rerun()
                                flash_error(
                                    "Inscription enregistrée, mais le profil n’a pas pu être chargé. "
                                    "Vérifiez la config API (JWT, Supabase)."
                                )
                                st.rerun()
                            except Exception as le:
                                le_s = str(le)
                                flash_success(f"{api_msg} Utilisez l’onglet « Se connecter ».")
                                if le_s and le_s not in (api_msg, "None"):
                                    flash_warning(f"Connexion immédiate impossible : {le_s}")
                                st.rerun()
                    except Exception as e:
                        flash_error(f"Inscription refusée ou erreur : {e}")
                        st.rerun()

    st.info(
        "Le backend et Supabase doivent être accessibles. Après connexion, "
        "votre rôle et votre plan s’affichent dans la barre latérale."
    )
    st.stop()


def ensure_admin() -> None:
    """Accès réservé au rôle `admin` (défini en base + option ADMIN_EMAILS côté API)."""
    ensure_authenticated()
    p = _profile()
    if p.get("app_role") != "admin":
        st.error("Cette page est réservée aux **administrateurs**.")
        st.caption("Connectez-vous avec un compte disposant du rôle admin (voir variable `ADMIN_EMAILS` côté API si besoin).")
        st.stop()


def is_premium() -> bool:
    """True si l'abonnement n'est pas freemium (plan payant côté métier)."""
    plan = ( _profile().get("type_abonnement") or "freemium").lower()
    return plan and plan not in ("freemium", "")


def render_auth_sidebar() -> None:
    """Bouton déconnexion + résumé du profil (sidebar). Appeler après `ensure_authenticated`."""
    p = _profile()
    st.sidebar.caption("Compte")
    st.sidebar.write(f"**{p.get('email', '—')}**")
    role = p.get("app_role", "user")
    st.sidebar.caption("Rôle : " + ("🛡️ Admin" if role == "admin" else "👤 Utilisateur"))
    plan = p.get("type_abonnement", "freemium")
    st.sidebar.caption("Plan : " + ("Gratuit" if plan == "freemium" else plan))
    try:
        st.sidebar.page_link("pages/0_Mon_Profil.py", label="🙋 Mon profil", use_container_width=True)
    except Exception:
        st.sidebar.caption("Page **Mon profil** : menu latéral → `0_Mon_Profil`")
    if st.sidebar.button("Déconnexion", use_container_width=True):
        set_api_token(None)
        st.rerun()
