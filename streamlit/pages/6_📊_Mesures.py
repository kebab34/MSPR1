import streamlit as st
import pandas as pd
from datetime import date
from utils.api_client import api_client

st.set_page_config(page_title="Mesures Biométriques", page_icon="📊", layout="wide")
st.title("📊 Mesures Biométriques")
st.markdown("---")

# Charger les utilisateurs
try:
    utilisateurs = api_client.get("/utilisateurs")
except Exception as e:
    st.error(f"Erreur de connexion à l'API: {e}")
    utilisateurs = []

if not utilisateurs:
    st.warning("Aucun utilisateur trouvé. Veuillez d'abord créer des utilisateurs.")
    st.stop()

# Sélection de l'utilisateur
user_options = {f"{u['prenom']} {u['nom']}": u["id_utilisateur"] for u in utilisateurs}
user_selected = st.selectbox("Sélectionner un utilisateur", list(user_options.keys()))
user_id = user_options[user_selected]

tab_historique, tab_ajouter = st.tabs(["📈 Historique", "➕ Nouvelle mesure"])

with tab_historique:
    try:
        params = {"utilisateur_id": user_id}
        mesures = api_client.get("/mesures", params=params)

        if mesures:
            df = pd.DataFrame(mesures)

            # Dernières mesures
            st.markdown("### Dernières mesures")
            if not df.empty:
                derniere = df.iloc[0] if "date_mesure" not in df.columns else df.sort_values("date_mesure", ascending=False).iloc[0]

                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Poids", f"{derniere.get('poids', 'N/A')} kg")
                with col2:
                    st.metric("IMC", f"{derniere.get('imc', 'N/A')}")
                with col3:
                    st.metric("Masse grasse", f"{derniere.get('masse_grasse', 'N/A')} %")
                with col4:
                    st.metric("Masse musculaire", f"{derniere.get('masse_musculaire', 'N/A')} %")

            # Tableau historique
            st.markdown("### Historique complet")
            colonnes = ["date_mesure", "poids", "imc", "masse_grasse", "masse_musculaire", "tour_taille", "tour_hanches"]
            colonnes_presentes = [c for c in colonnes if c in df.columns]
            st.dataframe(df[colonnes_presentes], use_container_width=True)

            # Graphique d'évolution
            if "date_mesure" in df.columns and "poids" in df.columns:
                st.markdown("### Évolution du poids")
                df_sorted = df.sort_values("date_mesure")
                st.line_chart(df_sorted.set_index("date_mesure")["poids"])
        else:
            st.info("Aucune mesure enregistrée")
    except Exception as e:
        st.error(f"Erreur: {e}")

with tab_ajouter:
    with st.form("form_mesure"):
        date_mesure = st.date_input("Date de la mesure", value=date.today())

        st.markdown("#### Mesures corporelles")
        col1, col2 = st.columns(2)
        with col1:
            poids = st.number_input("Poids (kg)", min_value=20.0, max_value=300.0, value=70.0, step=0.1)
            masse_grasse = st.number_input("Masse grasse (%)", min_value=0.0, max_value=100.0, value=20.0, step=0.1)
            tour_taille = st.number_input("Tour de taille (cm)", min_value=0.0, max_value=200.0, value=80.0, step=0.5)
        with col2:
            imc = st.number_input("IMC", min_value=10.0, max_value=50.0, value=22.0, step=0.1)
            masse_musculaire = st.number_input("Masse musculaire (%)", min_value=0.0, max_value=100.0, value=40.0, step=0.1)
            tour_hanches = st.number_input("Tour de hanches (cm)", min_value=0.0, max_value=200.0, value=90.0, step=0.5)

        st.markdown("#### Mesures vitales (optionnel)")
        col1, col2, col3 = st.columns(3)
        with col1:
            frequence_cardiaque = st.number_input("Fréquence cardiaque (bpm)", min_value=0, max_value=250, value=70)
        with col2:
            tension_systolique = st.number_input("Tension systolique", min_value=0, max_value=300, value=120)
        with col3:
            tension_diastolique = st.number_input("Tension diastolique", min_value=0, max_value=200, value=80)

        notes = st.text_area("Notes (optionnel)")

        submitted = st.form_submit_button("Enregistrer les mesures", use_container_width=True)

        if submitted:
            data = {
                "id_utilisateur": user_id,
                "date_mesure": date_mesure.isoformat(),
                "poids": poids,
                "imc": imc,
                "masse_grasse": masse_grasse,
                "masse_musculaire": masse_musculaire,
                "tour_taille": tour_taille,
                "tour_hanches": tour_hanches,
                "frequence_cardiaque": frequence_cardiaque if frequence_cardiaque > 0 else None,
                "tension_systolique": tension_systolique if tension_systolique > 0 else None,
                "tension_diastolique": tension_diastolique if tension_diastolique > 0 else None,
                "notes": notes if notes else None
            }
            try:
                api_client.post("/mesures", data)
                st.success("Mesures enregistrées!")
                st.rerun()
            except Exception as e:
                st.error(f"Erreur: {e}")
