import streamlit as st
import pandas as pd
from utils.api_client import api_client
from utils.auth_session import ensure_authenticated, render_auth_sidebar, list_utilisateurs_for_pickers
from utils.flash import render_flash, flash_success
from utils.style import inject_css, page_header, section_header

st.set_page_config(page_title="Mesures Biométriques", page_icon="📊", layout="wide")
inject_css()
ensure_authenticated()
render_auth_sidebar()
page_header("📏", "Mesures Biométriques", "Suivi du poids, fréquence cardiaque, sommeil et calories brûlées")
render_flash()

try:
    utilisateurs = list_utilisateurs_for_pickers()
except Exception as e:
    st.error(f"Erreur de connexion à l'API: {e}")
    utilisateurs = []

if not utilisateurs:
    st.warning("Aucun utilisateur trouvé.")
    st.stop()

def label_user(u):
    full = f"{u.get('prenom') or ''} {u.get('nom') or ''}".strip()
    return full if full else u.get("email", u["id_utilisateur"])

user_options = {label_user(u): u["id_utilisateur"] for u in utilisateurs}
user_selected = st.selectbox("👤 Utilisateur", list(user_options.keys()))
user_id = user_options[user_selected]

tab_historique, tab_ajouter = st.tabs(["📈 Historique", "➕ Nouvelle mesure"])

with tab_historique:
    try:
        mesures = api_client.get("/mesures", params={"utilisateur_id": user_id, "limit": 200})
        if mesures:
            df = pd.DataFrame(mesures)
            for col in ["poids", "frequence_cardiaque", "sommeil", "calories_brulees"]:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors="coerce")

            section_header("📊", "Dernière mesure")
            derniere = df.sort_values("date_mesure", ascending=False).iloc[0] if "date_mesure" in df.columns else df.iloc[0]
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("⚖️ Poids", f"{derniere.get('poids', '—')} kg")
            c2.metric("❤️ Fréq. cardiaque", f"{derniere.get('frequence_cardiaque', '—')} bpm")
            c3.metric("😴 Sommeil", f"{derniere.get('sommeil', '—')} h")
            c4.metric("🔥 Calories brûlées", f"{derniere.get('calories_brulees', '—')} kcal")

            section_header("📋", "Historique complet")
            cols_display = [c for c in ["date_mesure", "poids", "frequence_cardiaque", "sommeil", "calories_brulees"] if c in df.columns]
            st.dataframe(df[cols_display], use_container_width=True, height=280)

            if "date_mesure" in df.columns and "poids" in df.columns:
                df_poids = df[["date_mesure", "poids"]].dropna(subset=["poids"]).sort_values("date_mesure")
                if not df_poids.empty:
                    section_header("📈", "Évolution du poids")
                    st.line_chart(df_poids.set_index("date_mesure")["poids"])
        else:
            st.info("Aucune mesure enregistrée pour cet utilisateur.")
    except Exception as e:
        st.error(f"Erreur: {e}")

with tab_ajouter:
    with st.form("form_mesure"):
        col1, col2 = st.columns(2)
        with col1:
            poids = st.number_input("⚖️ Poids (kg)", min_value=0.0, max_value=300.0, value=70.0, step=0.1)
            frequence_cardiaque = st.number_input("❤️ Fréquence cardiaque (bpm)", min_value=0, max_value=250, value=70)
        with col2:
            sommeil = st.number_input("😴 Sommeil (heures)", min_value=0.0, max_value=24.0, value=7.0, step=0.5)
            calories_brulees = st.number_input("🔥 Calories brûlées", min_value=0.0, max_value=10000.0, value=0.0, step=10.0)

        submitted = st.form_submit_button("✅ Enregistrer", use_container_width=True, type="primary")
        if submitted:
            data = {"id_utilisateur": user_id,
                    "poids": poids if poids > 0 else None,
                    "frequence_cardiaque": frequence_cardiaque if frequence_cardiaque > 0 else None,
                    "sommeil": sommeil if sommeil > 0 else None,
                    "calories_brulees": calories_brulees if calories_brulees > 0 else None}
            try:
                res = api_client.post("/mesures", data)
                mid = res.get("id_mesure", "—")
                flash_success(f"**Mesure enregistrée** — poids {poids} kg. ID : `{mid}`")
                st.rerun()
            except Exception as e:
                st.error(f"Erreur: {e}")
