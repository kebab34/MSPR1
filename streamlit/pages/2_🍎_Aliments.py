import streamlit as st
import pandas as pd
from utils.api_client import api_client

st.set_page_config(page_title="Aliments", page_icon="🍎", layout="wide")
st.title("🍎 Catalogue d'Aliments")
st.markdown("---")

tab_liste, tab_ajouter = st.tabs(["📋 Liste des aliments", "➕ Ajouter un aliment"])

with tab_liste:
    try:
        aliments = api_client.get("/aliments")
        if aliments:
            df = pd.DataFrame(aliments)

            # Filtres
            col1, col2 = st.columns(2)
            with col1:
                recherche = st.text_input("🔍 Rechercher un aliment", "")
            with col2:
                if "source" in df.columns:
                    sources = ["Toutes"] + df["source"].dropna().unique().tolist()
                    source_filtre = st.selectbox("Filtrer par source", sources)
                else:
                    source_filtre = "Toutes"

            # Appliquer les filtres
            df_filtre = df.copy()
            if recherche:
                df_filtre = df_filtre[df_filtre["nom"].str.contains(recherche, case=False, na=False)]
            if source_filtre != "Toutes" and "source" in df.columns:
                df_filtre = df_filtre[df_filtre["source"] == source_filtre]

            st.markdown(f"**{len(df_filtre)} aliments trouvés**")

            colonnes_affichage = ["nom", "calories", "proteines", "glucides", "lipides", "fibres", "unite"]
            colonnes_presentes = [c for c in colonnes_affichage if c in df_filtre.columns]
            st.dataframe(df_filtre[colonnes_presentes], use_container_width=True)

            # Détails nutritionnels
            if not df_filtre.empty:
                st.markdown("### Détails nutritionnels")
                aliment_selectionne = st.selectbox("Sélectionner un aliment", df_filtre["nom"].tolist())
                if aliment_selectionne:
                    aliment = df_filtre[df_filtre["nom"] == aliment_selectionne].iloc[0]
                    col1, col2, col3, col4, col5 = st.columns(5)
                    with col1:
                        st.metric("Calories", f"{aliment.get('calories', 'N/A')} kcal")
                    with col2:
                        st.metric("Protéines", f"{aliment.get('proteines', 'N/A')} g")
                    with col3:
                        st.metric("Glucides", f"{aliment.get('glucides', 'N/A')} g")
                    with col4:
                        st.metric("Lipides", f"{aliment.get('lipides', 'N/A')} g")
                    with col5:
                        st.metric("Fibres", f"{aliment.get('fibres', 'N/A')} g")
        else:
            st.info("Aucun aliment trouvé. Lancez l'ETL pour importer les données.")
    except Exception as e:
        st.error(f"Erreur lors du chargement: {e}")

with tab_ajouter:
    with st.form("form_aliment"):
        nom = st.text_input("Nom de l'aliment *")
        col1, col2, col3 = st.columns(3)
        with col1:
            calories = st.number_input("Calories (kcal)", min_value=0.0, value=0.0)
            proteines = st.number_input("Protéines (g)", min_value=0.0, value=0.0)
        with col2:
            glucides = st.number_input("Glucides (g)", min_value=0.0, value=0.0)
            lipides = st.number_input("Lipides (g)", min_value=0.0, value=0.0)
        with col3:
            fibres = st.number_input("Fibres (g)", min_value=0.0, value=0.0)
            unite = st.text_input("Unité", value="100g")

        source = st.text_input("Source", value="manuel")

        submitted = st.form_submit_button("Ajouter l'aliment", use_container_width=True)

        if submitted:
            if nom:
                data = {
                    "nom": nom,
                    "calories": calories,
                    "proteines": proteines,
                    "glucides": glucides,
                    "lipides": lipides,
                    "fibres": fibres,
                    "unite": unite,
                    "source": source
                }
                try:
                    api_client.post("/aliments", data)
                    st.success(f"Aliment '{nom}' ajouté avec succès!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Erreur: {e}")
            else:
                st.warning("Veuillez entrer un nom d'aliment")
