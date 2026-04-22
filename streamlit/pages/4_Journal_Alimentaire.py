import streamlit as st
import pandas as pd
from datetime import date
from utils.api_client import api_client
from utils.auth_session import ensure_authenticated, render_auth_sidebar, list_utilisateurs_for_pickers
from utils.flash import render_flash, flash_success
from utils.style import inject_css, page_header, section_header

st.set_page_config(page_title="Journal Alimentaire", page_icon="📔", layout="wide")
inject_css()
ensure_authenticated()
render_auth_sidebar()
page_header("📔", "Journal Alimentaire", "Suivi quotidien des repas par utilisateur")
render_flash()

try:
    utilisateurs = list_utilisateurs_for_pickers()
    aliments = api_client.get("/aliments")
except Exception as e:
    st.error(f"Erreur de connexion à l'API: {e}")
    utilisateurs = []
    aliments = []

if not utilisateurs:
    st.warning("Aucun utilisateur trouvé. Veuillez d'abord créer des utilisateurs.")
    st.stop()

def label_user(u):
    full = f"{u.get('prenom') or ''} {u.get('nom') or ''}".strip()
    return full if full else u.get("email", u["id_utilisateur"])

user_options = {label_user(u): u["id_utilisateur"] for u in utilisateurs}
user_selected = st.selectbox("👤 Utilisateur", list(user_options.keys()))
user_id = user_options[user_selected]

tab_consulter, tab_ajouter = st.tabs(["📋 Consulter", "➕ Ajouter une entrée"])

with tab_consulter:
    col1, col2 = st.columns(2)
    with col1:
        date_debut = st.date_input("Date début", value=date.today())
    with col2:
        date_fin = st.date_input("Date fin", value=date.today())

    try:
        params = {"utilisateur_id": user_id, "date_debut": date_debut.isoformat(), "date_fin": date_fin.isoformat()}
        journal = api_client.get("/journal", params=params)

        if journal:
            df = pd.DataFrame(journal)
            st.dataframe(df, use_container_width=True, height=300)

            section_header("📊", "Résumé nutritionnel")
            if "calories_totales" in df.columns:
                total_cal = df["calories_totales"].sum()
                st.metric("🔥 Calories totales", f"{total_cal:.0f} kcal")
        else:
            st.info("Aucune entrée pour cette période")
    except Exception as e:
        st.error(f"Erreur: {e}")

with tab_ajouter:
    if not aliments:
        st.warning("Aucun aliment disponible.")
    else:
        with st.form("form_journal"):
            date_entree = st.date_input("Date", value=date.today())
            aliment_options = {a["nom"]: a["id_aliment"] for a in aliments}
            aliment_selected = st.selectbox("🍎 Aliment", list(aliment_options.keys()))
            aliment_id = aliment_options[aliment_selected]

            col1, col2 = st.columns(2)
            with col1:
                quantite = st.number_input("Quantité", min_value=0.1, value=1.0, step=0.1)
            with col2:
                type_repas = st.selectbox("Repas", ["petit_dejeuner", "dejeuner", "diner", "collation"])

            notes = st.text_area("Notes (optionnel)")
            submitted = st.form_submit_button("✅ Ajouter au journal", use_container_width=True, type="primary")

            if submitted:
                data = {"id_utilisateur": user_id, "id_aliment": aliment_id,
                        "date_consommation": date_entree.isoformat(), "quantite": quantite,
                        "type_repas": type_repas, "notes": notes if notes else None}
                try:
                    res = api_client.post("/journal", data)
                    jid = res.get("id_journal", "—")
                    flash_success(f"**Entrée enregistrée** — {aliment_selected} le {date_entree.isoformat()}. ID : `{jid}`")
                    st.rerun()
                except Exception as e:
                    st.error(f"Erreur: {e}")
