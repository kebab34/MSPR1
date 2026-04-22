import streamlit as st
import pandas as pd
from datetime import date
from utils.api_client import api_client
from utils.auth_session import ensure_authenticated, render_auth_sidebar, list_utilisateurs_for_pickers
from utils.flash import render_flash, flash_success
from utils.style import inject_css, page_header, badge, section_header

st.set_page_config(page_title="Sessions Sport", page_icon="🏃", layout="wide")
inject_css()
ensure_authenticated()
render_auth_sidebar()
page_header("🏃", "Sessions de Sport", "Historique et planification des entraînements")
render_flash()

try:
    utilisateurs = list_utilisateurs_for_pickers()
    exercices = api_client.get("/exercices")
except Exception as e:
    st.error(f"Erreur de connexion à l'API: {e}")
    utilisateurs = []
    exercices = []

if not utilisateurs:
    st.warning("Aucun utilisateur trouvé. Veuillez d'abord créer des utilisateurs.")
    st.stop()

def label_user(u):
    full = f"{u.get('prenom') or ''} {u.get('nom') or ''}".strip()
    return full if full else u.get("email", u["id_utilisateur"])

user_options = {label_user(u): u["id_utilisateur"] for u in utilisateurs}
user_selected = st.selectbox("👤 Utilisateur", list(user_options.keys()))
user_id = user_options[user_selected]

tab_consulter, tab_ajouter = st.tabs(["📋 Historique", "➕ Nouvelle session"])

with tab_consulter:
    col1, col2 = st.columns(2)
    with col1:
        date_debut = st.date_input("Date début", value=date.today(), key="date_debut_sessions")
    with col2:
        date_fin = st.date_input("Date fin", value=date.today(), key="date_fin_sessions")

    try:
        params = {"utilisateur_id": user_id, "date_debut": date_debut.isoformat(), "date_fin": date_fin.isoformat()}
        sessions = api_client.get("/sessions", params=params)

        if sessions:
            df = pd.DataFrame(sessions)
            colonnes = ["date_session", "type_session", "duree_minutes", "calories_brulees", "notes"]
            cols_ok = [c for c in colonnes if c in df.columns]
            st.dataframe(df[cols_ok], use_container_width=True, height=280)

            section_header("📊", "Statistiques de la période")
            c1, c2, c3 = st.columns(3)
            c1.metric("🏋️ Sessions", len(df))
            c2.metric("⏱️ Durée totale", f"{df['duree_minutes'].sum():.0f} min" if "duree_minutes" in df.columns else "—")
            c3.metric("🔥 Calories brûlées", f"{df['calories_brulees'].sum():.0f} kcal" if "calories_brulees" in df.columns else "—")
        else:
            st.info("Aucune session pour cette période")
    except Exception as e:
        st.error(f"Erreur: {e}")

with tab_ajouter:
    with st.form("form_session"):
        date_session = st.date_input("Date de la session", value=date.today())
        col1, col2 = st.columns(2)
        with col1:
            type_session = st.selectbox("Type", ["cardio", "musculation", "hiit", "yoga", "natation", "course", "autre"])
            duree = st.number_input("Durée (minutes)", min_value=1, value=30)
        with col2:
            intensite = st.select_slider("Intensité", options=["faible", "moderee", "elevee"])
            calories = st.number_input("Calories brûlées (estimation)", min_value=0, value=200)

        exercices_selectionnes = []
        if exercices:
            df_ex = pd.DataFrame(exercices)
            exercices_selectionnes = st.multiselect("Exercices réalisés", options=df_ex["nom"].tolist())

        notes = st.text_area("Notes (optionnel)")
        submitted = st.form_submit_button("✅ Enregistrer la session", use_container_width=True, type="primary")

        if submitted:
            data = {"id_utilisateur": user_id, "date_session": date_session.isoformat(),
                    "type_session": type_session, "duree_minutes": duree,
                    "intensite": intensite, "calories_brulees": calories,
                    "notes": notes if notes else None}
            try:
                result = api_client.post("/sessions", data)
                sid = result.get("id_session", "—")
                flash_success(f"**Session enregistrée** — {date_session} · {type_session} · {duree} min. ID : `{sid}`")
                st.rerun()
            except Exception as e:
                st.error(f"Erreur: {e}")
