import streamlit as st
import pandas as pd
from utils.api_client import api_client

st.set_page_config(page_title="Exercices", page_icon="🏋️", layout="wide")
st.title("🏋️ Bibliothèque d'Exercices")
st.markdown("---")

try:
    exercices = api_client.get("/exercices")
    if exercices:
        df = pd.DataFrame(exercices)

        # Filtres
        col1, col2, col3 = st.columns(3)
        with col1:
            recherche = st.text_input("🔍 Rechercher", "")
        with col2:
            if "groupe_musculaire" in df.columns:
                groupes = ["Tous"] + sorted(df["groupe_musculaire"].dropna().unique().tolist())
                groupe_filtre = st.selectbox("Groupe musculaire", groupes)
            else:
                groupe_filtre = "Tous"
        with col3:
            if "niveau" in df.columns:
                niveaux = ["Tous"] + sorted(df["niveau"].dropna().unique().tolist())
                niveau_filtre = st.selectbox("Niveau", niveaux)
            else:
                niveau_filtre = "Tous"

        # Appliquer les filtres
        df_filtre = df.copy()
        if recherche:
            df_filtre = df_filtre[df_filtre["nom"].str.contains(recherche, case=False, na=False)]
        if groupe_filtre != "Tous" and "groupe_musculaire" in df.columns:
            df_filtre = df_filtre[df_filtre["groupe_musculaire"] == groupe_filtre]
        if niveau_filtre != "Tous" and "niveau" in df.columns:
            df_filtre = df_filtre[df_filtre["niveau"] == niveau_filtre]

        st.markdown(f"**{len(df_filtre)} exercices trouvés**")

        # Affichage en grille
        colonnes_affichage = ["nom", "type", "groupe_musculaire", "niveau", "equipement"]
        colonnes_presentes = [c for c in colonnes_affichage if c in df_filtre.columns]
        st.dataframe(df_filtre[colonnes_presentes], use_container_width=True)

        # Détails d'un exercice
        if not df_filtre.empty:
            st.markdown("### Détails de l'exercice")
            exercice_selectionne = st.selectbox("Sélectionner un exercice", df_filtre["nom"].tolist())
            if exercice_selectionne:
                exercice = df_filtre[df_filtre["nom"] == exercice_selectionne].iloc[0]
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown(f"**Type:** {exercice.get('type', 'N/A')}")
                    st.markdown(f"**Groupe musculaire:** {exercice.get('groupe_musculaire', 'N/A')}")
                    st.markdown(f"**Niveau:** {exercice.get('niveau', 'N/A')}")
                with col2:
                    st.markdown(f"**Équipement:** {exercice.get('equipement', 'N/A')}")
                    st.markdown(f"**Source:** {exercice.get('source', 'N/A')}")

                if exercice.get("description"):
                    st.markdown("**Description:**")
                    st.write(exercice["description"])
    else:
        st.info("Aucun exercice trouvé. Lancez l'ETL pour importer les données.")
except Exception as e:
    st.error(f"Erreur lors du chargement: {e}")
