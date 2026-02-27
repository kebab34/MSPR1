import streamlit as st
import pandas as pd
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
    st.warning("Aucun utilisateur trouvé.")
    st.stop()

# Sélecteur : affiche prénom+nom si dispo, sinon email
def label_user(u):
    prenom = u.get("prenom") or ""
    nom = u.get("nom") or ""
    full = f"{prenom} {nom}".strip()
    return full if full else u.get("email", u["id_utilisateur"])

user_options = {label_user(u): u["id_utilisateur"] for u in utilisateurs}
user_selected = st.selectbox("Sélectionner un utilisateur", list(user_options.keys()))
user_id = user_options[user_selected]

tab_historique, tab_ajouter = st.tabs(["📈 Historique", "➕ Nouvelle mesure"])

with tab_historique:
    try:
        mesures = api_client.get("/mesures", params={"utilisateur_id": user_id, "limit": 200})

        if mesures:
            df = pd.DataFrame(mesures)

            # Convertir les colonnes numériques
            for col in ["poids", "frequence_cardiaque", "sommeil", "calories_brulees"]:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors="coerce")

            # Dernière mesure
            st.markdown("### Dernière mesure")
            derniere = df.sort_values("date_mesure", ascending=False).iloc[0] if "date_mesure" in df.columns else df.iloc[0]
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Poids", f"{derniere.get('poids', 'N/A')} kg")
            col2.metric("Fréq. cardiaque", f"{derniere.get('frequence_cardiaque', 'N/A')} bpm")
            col3.metric("Sommeil", f"{derniere.get('sommeil', 'N/A')} h")
            col4.metric("Calories brûlées", f"{derniere.get('calories_brulees', 'N/A')} kcal")

            # Tableau
            st.markdown("### Historique complet")
            cols_display = [c for c in ["date_mesure", "poids", "frequence_cardiaque", "sommeil", "calories_brulees"] if c in df.columns]
            st.dataframe(df[cols_display], use_container_width=True)

            # Graphique évolution du poids (sans NaN)
            if "date_mesure" in df.columns and "poids" in df.columns:
                df_poids = df[["date_mesure", "poids"]].dropna(subset=["poids"]).sort_values("date_mesure")
                if not df_poids.empty:
                    st.markdown("### Évolution du poids")
                    st.line_chart(df_poids.set_index("date_mesure")["poids"])
        else:
            st.info("Aucune mesure enregistrée pour cet utilisateur.")
    except Exception as e:
        st.error(f"Erreur: {e}")

with tab_ajouter:
    with st.form("form_mesure"):
        col1, col2 = st.columns(2)
        with col1:
            poids = st.number_input("Poids (kg)", min_value=0.0, max_value=300.0, value=70.0, step=0.1)
            frequence_cardiaque = st.number_input("Fréquence cardiaque (bpm)", min_value=0, max_value=250, value=70)
        with col2:
            sommeil = st.number_input("Sommeil (heures)", min_value=0.0, max_value=24.0, value=7.0, step=0.5)
            calories_brulees = st.number_input("Calories brûlées", min_value=0.0, max_value=10000.0, value=0.0, step=10.0)

        submitted = st.form_submit_button("Enregistrer", use_container_width=True)

        if submitted:
            data = {
                "id_utilisateur": user_id,
                "poids": poids if poids > 0 else None,
                "frequence_cardiaque": frequence_cardiaque if frequence_cardiaque > 0 else None,
                "sommeil": sommeil if sommeil > 0 else None,
                "calories_brulees": calories_brulees if calories_brulees > 0 else None,
            }
            try:
                api_client.post("/mesures", data)
                st.success("Mesures enregistrées !")
                st.rerun()
            except Exception as e:
                st.error(f"Erreur: {e}")
