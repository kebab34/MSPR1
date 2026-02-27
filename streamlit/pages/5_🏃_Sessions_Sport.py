import streamlit as st
import pandas as pd
from datetime import date, datetime
from utils.api_client import api_client

st.set_page_config(page_title="Sessions Sport", page_icon="🏃", layout="wide")
st.title("🏃 Sessions de Sport")
st.markdown("---")

# Charger les utilisateurs et exercices
try:
    utilisateurs = api_client.get("/utilisateurs")
    exercices = api_client.get("/exercices")
except Exception as e:
    st.error(f"Erreur de connexion à l'API: {e}")
    utilisateurs = []
    exercices = []

if not utilisateurs:
    st.warning("Aucun utilisateur trouvé. Veuillez d'abord créer des utilisateurs.")
    st.stop()

# Sélection de l'utilisateur
def label_user(u):
    full = f"{u.get('prenom') or ''} {u.get('nom') or ''}".strip()
    return full if full else u.get("email", u["id_utilisateur"])

user_options = {label_user(u): u["id_utilisateur"] for u in utilisateurs}
user_selected = st.selectbox("Sélectionner un utilisateur", list(user_options.keys()))
user_id = user_options[user_selected]

tab_consulter, tab_ajouter = st.tabs(["📋 Historique des sessions", "➕ Nouvelle session"])

with tab_consulter:
    col1, col2 = st.columns(2)
    with col1:
        date_debut = st.date_input("Date début", value=date.today(), key="date_debut_sessions")
    with col2:
        date_fin = st.date_input("Date fin", value=date.today(), key="date_fin_sessions")

    try:
        params = {
            "utilisateur_id": user_id,
            "date_debut": date_debut.isoformat(),
            "date_fin": date_fin.isoformat()
        }
        sessions = api_client.get("/sessions", params=params)

        if sessions:
            df = pd.DataFrame(sessions)
            colonnes = ["date_session", "type_session", "duree_minutes", "calories_brulees", "notes"]
            colonnes_presentes = [c for c in colonnes if c in df.columns]
            st.dataframe(df[colonnes_presentes], use_container_width=True)

            # Stats
            st.markdown("### Statistiques")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Sessions", len(df))
            with col2:
                if "duree_minutes" in df.columns:
                    st.metric("Durée totale", f"{df['duree_minutes'].sum():.0f} min")
            with col3:
                if "calories_brulees" in df.columns:
                    st.metric("Calories brûlées", f"{df['calories_brulees'].sum():.0f} kcal")
        else:
            st.info("Aucune session pour cette période")
    except Exception as e:
        st.error(f"Erreur: {e}")

with tab_ajouter:
    with st.form("form_session"):
        date_session = st.date_input("Date de la session", value=date.today())

        col1, col2 = st.columns(2)
        with col1:
            type_session = st.selectbox("Type de session", ["cardio", "musculation", "hiit", "yoga", "natation", "course", "autre"])
            duree = st.number_input("Durée (minutes)", min_value=1, value=30)
        with col2:
            intensite = st.select_slider("Intensité", options=["faible", "modérée", "élevée", "très élevée"])
            calories = st.number_input("Calories brûlées (estimation)", min_value=0, value=200)

        # Sélection des exercices (si disponibles)
        exercices_selectionnes = []
        if exercices:
            df_ex = pd.DataFrame(exercices)
            exercices_selectionnes = st.multiselect(
                "Exercices réalisés",
                options=df_ex["nom"].tolist()
            )

        notes = st.text_area("Notes (optionnel)")

        submitted = st.form_submit_button("Enregistrer la session", use_container_width=True)

        if submitted:
            data = {
                "id_utilisateur": user_id,
                "date_session": date_session.isoformat(),
                "type_session": type_session,
                "duree_minutes": duree,
                "intensite": intensite,
                "calories_brulees": calories,
                "notes": notes if notes else None
            }
            try:
                result = api_client.post("/sessions", data)
                st.success("Session enregistrée!")
                st.rerun()
            except Exception as e:
                st.error(f"Erreur: {e}")
