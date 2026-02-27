import streamlit as st
import pandas as pd
from utils.api_client import api_client

st.set_page_config(page_title="Utilisateurs", page_icon="👤", layout="wide")
st.title("👤 Gestion des Utilisateurs")
st.markdown("---")

# Tabs pour organiser les actions
tab_liste, tab_ajouter = st.tabs(["📋 Liste des utilisateurs", "➕ Ajouter un utilisateur"])

with tab_liste:
    try:
        utilisateurs = api_client.get("/utilisateurs")
        if utilisateurs:
            df = pd.DataFrame(utilisateurs)
            colonnes_affichage = ["nom", "prenom", "email", "age", "sexe", "poids", "taille", "type_abonnement"]
            colonnes_presentes = [c for c in colonnes_affichage if c in df.columns]
            st.dataframe(df[colonnes_presentes], use_container_width=True)

            # Détails d'un utilisateur
            st.markdown("### Détails utilisateur")
            def label_user(row):
                full = f"{row.get('prenom') or ''} {row.get('nom') or ''}".strip()
                return full if full else row.get("email", str(row.get("id_utilisateur", "")))
            labels = df.apply(label_user, axis=1).tolist()
            label_selectionne = st.selectbox("Sélectionner un utilisateur", labels)

            if label_selectionne:
                user = df.iloc[labels.index(label_selectionne)]
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Poids", f"{user.get('poids', 'N/A')} kg")
                with col2:
                    st.metric("Taille", f"{user.get('taille', 'N/A')} cm")
                with col3:
                    st.metric("Âge", f"{user.get('age', 'N/A')} ans")

                if user.get("objectifs"):
                    st.markdown("**Objectifs:** " + ", ".join(user["objectifs"]))
        else:
            st.info("Aucun utilisateur trouvé")
    except Exception as e:
        st.error(f"Erreur lors du chargement: {e}")

with tab_ajouter:
    with st.form("form_utilisateur"):
        col1, col2 = st.columns(2)
        with col1:
            nom = st.text_input("Nom *")
            prenom = st.text_input("Prénom *")
            email = st.text_input("Email *")
            age = st.number_input("Âge", min_value=1, max_value=120, value=30)
        with col2:
            sexe = st.selectbox("Sexe", ["M", "F"])
            poids = st.number_input("Poids (kg)", min_value=20.0, max_value=300.0, value=70.0)
            taille = st.number_input("Taille (cm)", min_value=100.0, max_value=250.0, value=170.0)
            type_abonnement = st.selectbox("Type d'abonnement", ["freemium", "premium"])

        objectifs = st.multiselect(
            "Objectifs",
            ["perte de poids", "musculation", "forme", "cardio", "flexibilité", "endurance"]
        )

        submitted = st.form_submit_button("Créer l'utilisateur", use_container_width=True)

        if submitted:
            if nom and prenom and email:
                data = {
                    "nom": nom,
                    "prenom": prenom,
                    "email": email,
                    "age": age,
                    "sexe": sexe,
                    "poids": poids,
                    "taille": taille,
                    "type_abonnement": type_abonnement,
                    "objectifs": objectifs
                }
                try:
                    result = api_client.post("/utilisateurs", data)
                    st.success(f"Utilisateur {prenom} {nom} créé avec succès!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Erreur: {e}")
            else:
                st.warning("Veuillez remplir tous les champs obligatoires (*)")