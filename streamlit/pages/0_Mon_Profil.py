import streamlit as st
from utils.api_client import api_client
from utils.auth_session import ensure_authenticated, refresh_profile, render_auth_sidebar
from utils.flash import flash_error, flash_success, render_flash
from utils.style import inject_css, page_header

st.set_page_config(page_title="Mon profil", page_icon="🙋", layout="wide")
inject_css()
ensure_authenticated()
render_auth_sidebar()
page_header("🙋", "Mon profil", "Complétez votre fiche (table `utilisateurs`) et gérez le passage Premium")
render_flash()

OBJECTIFS_CHOIX = [
    "perte de poids",
    "musculation",
    "forme",
    "cardio",
    "flexibilité",
    "endurance",
]

try:
    p = api_client.me()
    st.session_state["user_profile"] = p
except Exception as e:
    st.error(f"Impossible de charger le profil : {e}")
    st.stop()

with st.form("form_mon_profil", clear_on_submit=False):
    st.subheader("Informations personnelles")
    c1, c2 = st.columns(2)
    with c1:
        st.text_input("Email (lecture seule)", value=p.get("email") or "", disabled=True)
        prenom = st.text_input("Prénom", value=p.get("prenom") or "", key="mp_prenom")
        nom = st.text_input("Nom", value=p.get("nom") or "", key="mp_nom")
    with c2:
        age_val = p.get("age")
        age = st.number_input(
            "Âge",
            min_value=0,
            max_value=150,
            value=int(age_val) if age_val is not None else 0,
            help="0 = non renseigné",
        )
        sexe_cur = p.get("sexe") or ""
        sexe_opt = ["", "M", "F", "Autre"]
        si = sexe_opt.index(sexe_cur) if sexe_cur in sexe_opt else 0
        sexe = st.selectbox("Sexe", sexe_opt, index=si, format_func=lambda x: "(non indiqué)" if x == "" else x)
        c_p, c_t = st.columns(2)
        with c_p:
            pv = p.get("poids")
            poids = st.number_input(
                "Poids (kg)", min_value=0.0, max_value=300.0, value=float(pv) if pv is not None else 0.0, step=0.1, format="%.1f", help="0 = non renseigné"
            )
        with c_t:
            tv = p.get("taille")
            taille = st.number_input(
                "Taille (cm)", min_value=0.0, max_value=300.0, value=float(tv) if tv is not None else 0.0, step=0.1, format="%.1f", help="0 = non renseigné"
            )

    obj_cur = p.get("objectifs") or []
    if not isinstance(obj_cur, list):
        obj_cur = []
    objectifs = st.multiselect("Objectifs", OBJECTIFS_CHOIX, default=obj_cur)

    st.divider()
    st.subheader("Formule")
    is_prem = (p.get("type_abonnement") or "freemium").lower() == "premium"
    premium_on = st.checkbox(
        "Passer en Premium (démo : activer / désactiver)",
        value=is_prem,
        help="Décoché = Gratuit (freemium), coché = Premium. Pas de paiement pour l’instant.",
    )

    submitted = st.form_submit_button("Enregistrer", type="primary", use_container_width=True)

    if submitted:
        payload: dict = {
            "prenom": prenom.strip() or None,
            "nom": nom.strip() or None,
            "objectifs": objectifs,
            "type_abonnement": "premium" if premium_on else "freemium",
        }
        if age and age > 0:
            payload["age"] = int(age)
        else:
            payload["age"] = None
        if sexe:
            payload["sexe"] = sexe
        else:
            payload["sexe"] = None
        if poids and poids > 0:
            payload["poids"] = float(poids)
        else:
            payload["poids"] = None
        if taille and taille > 0:
            payload["taille"] = float(taille)
        else:
            payload["taille"] = None

        try:
            api_client.update_me(payload)
            refresh_profile()
            flash_success("Profil enregistré.")
            st.rerun()
        except Exception as e:
            flash_error(f"Enregistrement impossible : {e}")
            st.rerun()

st.caption(
    "Rôle **admin** et plan **Gratuit** sont appliqués à l’inscription. "
    "Cette page met à jour votre ligne via `PATCH /api/v1/auth/me`."
)
