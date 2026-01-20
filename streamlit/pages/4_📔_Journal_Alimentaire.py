import streamlit as st
import pandas as pd
from datetime import date, datetime
from utils.api_client import api_client

st.set_page_config(page_title="Journal Alimentaire", page_icon="📔", layout="wide")
st.title("📔 Journal Alimentaire")
st.markdown("---")

# Charger les utilisateurs et aliments pour les sélecteurs
try:
    utilisateurs = api_client.get("/utilisateurs")
    aliments = api_client.get("/aliments")
except Exception as e:
    st.error(f"Erreur de connexion à l'API: {e}")
    utilisateurs = []
    aliments = []

if not utilisateurs:
    st.warning("Aucun utilisateur trouvé. Veuillez d'abord créer des utilisateurs.")
    st.stop()

# Sélection de l'utilisateur
df_users = pd.DataFrame(utilisateurs)
user_options = {f"{u['prenom']} {u['nom']}": u["id_utilisateur"] for u in utilisateurs}
user_selected = st.selectbox("Sélectionner un utilisateur", list(user_options.keys()))
user_id = user_options[user_selected]

tab_consulter, tab_ajouter = st.tabs(["📋 Consulter le journal", "➕ Ajouter une entrée"])

with tab_consulter:
    col1, col2 = st.columns(2)
    with col1:
        date_debut = st.date_input("Date début", value=date.today())
    with col2:
        date_fin = st.date_input("Date fin", value=date.today())

    try:
        params = {
            "utilisateur_id": user_id,
            "date_debut": date_debut.isoformat(),
            "date_fin": date_fin.isoformat()
        }
        journal = api_client.get("/journal", params=params)

        if journal:
            df = pd.DataFrame(journal)
            st.dataframe(df, use_container_width=True)

            # Résumé nutritionnel
            st.markdown("### Résumé nutritionnel")
            if "calories_totales" in df.columns:
                total_cal = df["calories_totales"].sum()
                st.metric("Calories totales", f"{total_cal:.0f} kcal")
        else:
            st.info("Aucune entrée pour cette période")
    except Exception as e:
        st.error(f"Erreur: {e}")

with tab_ajouter:
    if not aliments:
        st.warning("Aucun aliment disponible. Veuillez d'abord ajouter des aliments.")
    else:
        with st.form("form_journal"):
            date_entree = st.date_input("Date", value=date.today())

            df_aliments = pd.DataFrame(aliments)
            aliment_options = {a["nom"]: a["id_aliment"] for a in aliments}
            aliment_selected = st.selectbox("Aliment", list(aliment_options.keys()))
            aliment_id = aliment_options[aliment_selected]

            col1, col2 = st.columns(2)
            with col1:
                quantite = st.number_input("Quantité", min_value=0.1, value=1.0, step=0.1)
            with col2:
                type_repas = st.selectbox("Type de repas", ["petit_dejeuner", "dejeuner", "diner", "collation"])

            notes = st.text_area("Notes (optionnel)")

            submitted = st.form_submit_button("Ajouter au journal", use_container_width=True)

            if submitted:
                data = {
                    "id_utilisateur": user_id,
                    "id_aliment": aliment_id,
                    "date_consommation": date_entree.isoformat(),
                    "quantite": quantite,
                    "type_repas": type_repas,
                    "notes": notes if notes else None
                }
                try:
                    api_client.post("/journal", data)
                    st.success("Entrée ajoutée au journal!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Erreur: {e}")
