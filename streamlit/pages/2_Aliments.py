import streamlit as st
import pandas as pd
from utils.api_client import api_client
from utils.auth_session import ensure_authenticated, render_auth_sidebar
from utils.flash import render_flash, flash_success
from utils.style import inject_css, page_header, macro_bar, section_header

st.set_page_config(page_title="Aliments", page_icon="🍎", layout="wide")
inject_css()
ensure_authenticated()
render_auth_sidebar()
page_header("🍎", "Catalogue d'Aliments", "500 aliments avec valeurs nutritionnelles complètes")
render_flash()

tab_liste, tab_ajouter = st.tabs(["📋 Catalogue", "➕ Ajouter"])

with tab_liste:
    try:
        aliments = api_client.get("/aliments")
        if aliments:
            df = pd.DataFrame(aliments)

            col1, col2 = st.columns([3, 2])
            with col1:
                recherche = st.text_input("🔍 Rechercher un aliment", "")
            with col2:
                if "source" in df.columns:
                    sources = ["Toutes"] + sorted(df["source"].dropna().unique().tolist())
                    source_filtre = st.selectbox("Source", sources)
                else:
                    source_filtre = "Toutes"

            df_f = df.copy()
            if recherche:
                df_f = df_f[df_f["nom"].str.contains(recherche, case=False, na=False)]
            if source_filtre != "Toutes" and "source" in df.columns:
                df_f = df_f[df_f["source"] == source_filtre]

            st.caption(f"{len(df_f)} aliment(s) trouvé(s)")

            cols_show = ["nom", "calories", "proteines", "glucides", "lipides", "fibres", "unite"]
            cols_ok = [c for c in cols_show if c in df_f.columns]
            st.dataframe(df_f[cols_ok], use_container_width=True, height=320)

            # ── Détail nutritionnel ───────────────────────────────────────
            if not df_f.empty:
                section_header("🔬", "Détail nutritionnel")
                chosen = st.selectbox("Sélectionner un aliment", df_f["nom"].tolist())
                aliment = df_f[df_f["nom"] == chosen].iloc[0]

                col1, col2 = st.columns([1, 1])
                with col1:
                    c1, c2 = st.columns(2)
                    c1.metric("🔥 Calories", f"{aliment.get('calories', '—')} kcal")
                    c2.metric("📦 Unité", str(aliment.get("unite", "100g")))

                with col2:
                    # Barres macronutriments
                    macros_html = ""
                    ref = 100.0
                    macros = [
                        ("Protéines", "proteines", "#3b82f6"),
                        ("Glucides",  "glucides",  "#f59e0b"),
                        ("Lipides",   "lipides",   "#ef4444"),
                        ("Fibres",    "fibres",    "#10b981"),
                    ]
                    for label, col, color in macros:
                        val = aliment.get(col, 0) or 0
                        macros_html += macro_bar(label, float(val), ref, color)

                    st.markdown(f"""
                    <div class="info-card">
                        <div class="info-card-title">📊 Macronutriments (pour {aliment.get("unite","100g")})</div>
                        {macros_html}
                    </div>
                    """, unsafe_allow_html=True)
        else:
            st.info("Aucun aliment trouvé. Lancez l'ETL pour importer les données.")
    except Exception as e:
        st.error(f"Erreur lors du chargement: {e}")

with tab_ajouter:
    with st.form("form_aliment"):
        nom = st.text_input("Nom de l'aliment *")
        col1, col2, col3 = st.columns(3)
        with col1:
            calories  = st.number_input("Calories (kcal)", min_value=0.0, value=0.0)
            proteines = st.number_input("Protéines (g)",   min_value=0.0, value=0.0)
        with col2:
            glucides = st.number_input("Glucides (g)", min_value=0.0, value=0.0)
            lipides  = st.number_input("Lipides (g)",  min_value=0.0, value=0.0)
        with col3:
            fibres = st.number_input("Fibres (g)", min_value=0.0, value=0.0)
            unite  = st.text_input("Unité", value="100g")
        source = st.text_input("Source", value="manuel")

        submitted = st.form_submit_button("✅ Ajouter l'aliment", use_container_width=True, type="primary")
        if submitted:
            if nom:
                data = {"nom": nom, "calories": calories, "proteines": proteines,
                        "glucides": glucides, "lipides": lipides, "fibres": fibres,
                        "unite": unite, "source": source}
                try:
                    res = api_client.post("/aliments", data)
                    uid = res.get("id_aliment", "—")
                    flash_success(f"**Aliment ajouté** — « {nom} » (ID : `{uid}`).")
                    st.rerun()
                except Exception as e:
                    st.error(f"Erreur: {e}")
            else:
                st.warning("Veuillez entrer un nom d'aliment")
