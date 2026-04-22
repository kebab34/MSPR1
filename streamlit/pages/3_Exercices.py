import streamlit as st
import pandas as pd
from utils.api_client import api_client
from utils.auth_session import ensure_authenticated, render_auth_sidebar
from utils.style import inject_css, page_header, badge, section_header

st.set_page_config(page_title="Exercices", page_icon="🏋️", layout="wide")
inject_css()
ensure_authenticated()
render_auth_sidebar()
page_header("🏋️", "Bibliothèque d'Exercices", "200 exercices classés par groupe musculaire, type et niveau")

try:
    exercices = api_client.get("/exercices")
    if exercices:
        df = pd.DataFrame(exercices)

        # ── Filtres ────────────────────────────────────────────────────────
        col1, col2, col3, col4 = st.columns([3, 2, 2, 2])
        with col1:
            recherche = st.text_input("🔍 Rechercher", "")
        with col2:
            types = ["Tous"] + sorted(df["type"].dropna().unique().tolist()) if "type" in df.columns else ["Tous"]
            type_filtre = st.selectbox("Type", types)
        with col3:
            groupes = ["Tous"] + sorted(df["groupe_musculaire"].dropna().unique().tolist()) if "groupe_musculaire" in df.columns else ["Tous"]
            groupe_filtre = st.selectbox("Groupe musculaire", groupes)
        with col4:
            niveaux = ["Tous"] + sorted(df["niveau"].dropna().unique().tolist()) if "niveau" in df.columns else ["Tous"]
            niveau_filtre = st.selectbox("Niveau", niveaux)

        df_f = df.copy()
        if recherche:
            df_f = df_f[df_f["nom"].str.contains(recherche, case=False, na=False)]
        if type_filtre != "Tous" and "type" in df_f.columns:
            df_f = df_f[df_f["type"] == type_filtre]
        if groupe_filtre != "Tous" and "groupe_musculaire" in df_f.columns:
            df_f = df_f[df_f["groupe_musculaire"] == groupe_filtre]
        if niveau_filtre != "Tous" and "niveau" in df_f.columns:
            df_f = df_f[df_f["niveau"] == niveau_filtre]

        st.caption(f"{len(df_f)} exercice(s) trouvé(s)")

        cols_show = ["nom", "type", "groupe_musculaire", "niveau", "equipement"]
        cols_ok = [c for c in cols_show if c in df_f.columns]
        st.dataframe(df_f[cols_ok], use_container_width=True, height=320)

        # ── Détail exercice ────────────────────────────────────────────────
        if not df_f.empty:
            section_header("🔍", "Détail de l'exercice")
            chosen = st.selectbox("Sélectionner un exercice", df_f["nom"].tolist())
            ex = df_f[df_f["nom"] == chosen].iloc[0]

            col1, col2 = st.columns([1, 2])
            with col1:
                st.markdown(f"""
                <div class="info-card">
                    <div class="info-card-title">🏋️ {ex.get("nom","")}</div>
                    <div class="info-row">
                        <span class="info-row-label">Type</span>
                        <span class="info-row-value">{badge(ex.get("type",""))}</span>
                    </div>
                    <div class="info-row">
                        <span class="info-row-label">Niveau</span>
                        <span class="info-row-value">{badge(ex.get("niveau",""))}</span>
                    </div>
                    <div class="info-row">
                        <span class="info-row-label">Groupe musculaire</span>
                        <span class="info-row-value">{ex.get("groupe_musculaire","—")}</span>
                    </div>
                    <div class="info-row">
                        <span class="info-row-label">Équipement</span>
                        <span class="info-row-value">{ex.get("equipement","—")}</span>
                    </div>
                    <div class="info-row">
                        <span class="info-row-label">Source</span>
                        <span class="info-row-value">{ex.get("source","—")}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)

            with col2:
                if ex.get("description"):
                    st.markdown(f"""
                    <div class="info-card">
                        <div class="info-card-title">📝 Description</div>
                        <p style="font-size:0.9rem;color:#374151;line-height:1.6;margin:0;">{ex["description"]}</p>
                    </div>
                    """, unsafe_allow_html=True)
                if ex.get("instructions"):
                    st.markdown(f"""
                    <div class="info-card">
                        <div class="info-card-title">📋 Instructions</div>
                        <p style="font-size:0.9rem;color:#374151;line-height:1.6;margin:0;">{ex["instructions"]}</p>
                    </div>
                    """, unsafe_allow_html=True)
    else:
        st.info("Aucun exercice trouvé. Lancez l'ETL pour importer les données.")
except Exception as e:
    st.error(f"Erreur lors du chargement: {e}")
