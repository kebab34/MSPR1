import streamlit as st
import pandas as pd
from utils.api_client import api_client
from utils.auth_session import ensure_admin, render_auth_sidebar
from utils.flash import render_flash, flash_success
from utils.style import inject_css, page_header, badge, section_header

st.set_page_config(page_title="Utilisateurs", page_icon="👤", layout="wide")
inject_css()
ensure_admin()
render_auth_sidebar()
page_header("👤", "Gestion des Utilisateurs", "Consultez, filtrez et créez des profils utilisateurs (administrateurs)")
render_flash()

tab_liste, tab_ajouter = st.tabs(["📋 Liste", "➕ Ajouter"])

with tab_liste:
    try:
        utilisateurs = api_client.get("/utilisateurs")
        if utilisateurs:
            df = pd.DataFrame(utilisateurs)

            # ── Filtres ──────────────────────────────────────────────────
            col1, col2, col3 = st.columns([3, 2, 2])
            with col1:
                recherche = st.text_input("🔍 Rechercher (nom, prénom, email)", "")
            with col2:
                abos = ["Tous"] + sorted(df["type_abonnement"].dropna().unique().tolist()) if "type_abonnement" in df.columns else ["Tous"]
                abo_filtre = st.selectbox("Abonnement", abos)
            with col3:
                sexes = ["Tous"] + sorted(df["sexe"].dropna().unique().tolist()) if "sexe" in df.columns else ["Tous"]
                sexe_filtre = st.selectbox("Sexe", sexes)

            df_f = df.copy()
            if recherche:
                mask = (
                    df_f.get("nom", pd.Series(dtype=str)).str.contains(recherche, case=False, na=False) |
                    df_f.get("prenom", pd.Series(dtype=str)).str.contains(recherche, case=False, na=False) |
                    df_f.get("email", pd.Series(dtype=str)).str.contains(recherche, case=False, na=False)
                )
                df_f = df_f[mask]
            if abo_filtre != "Tous" and "type_abonnement" in df_f.columns:
                df_f = df_f[df_f["type_abonnement"] == abo_filtre]
            if sexe_filtre != "Tous" and "sexe" in df_f.columns:
                df_f = df_f[df_f["sexe"] == sexe_filtre]

            st.caption(f"{len(df_f)} utilisateur(s) trouvé(s)")

            # ── Tableau ──────────────────────────────────────────────────
            cols_show = ["nom", "prenom", "email", "age", "sexe", "poids", "taille", "type_abonnement", "app_role"]
            cols_ok = [c for c in cols_show if c in df_f.columns]
            st.dataframe(df_f[cols_ok], use_container_width=True, height=320)

            # ── Détail utilisateur ────────────────────────────────────────
            section_header("🔍", "Détail utilisateur")

            def label_user(row):
                full = f"{row.get('prenom') or ''} {row.get('nom') or ''}".strip()
                return full or row.get("email", str(row.get("id_utilisateur", "")))

            if not df_f.empty:
                labels = df_f.apply(label_user, axis=1).tolist()
                chosen = st.selectbox("Sélectionner", labels, key="sel_user")
                user = df_f.iloc[labels.index(chosen)]

                col1, col2 = st.columns([1, 2])
                with col1:
                    abo_val = user.get("type_abonnement", "")
                    sexe_val = user.get("sexe", "")
                    st.markdown(f"""
                    <div class="info-card">
                        <div class="info-card-title">👤 {label_user(user)}</div>
                        <div class="info-row">
                            <span class="info-row-label">Email</span>
                            <span class="info-row-value">{user.get("email","—")}</span>
                        </div>
                        <div class="info-row">
                            <span class="info-row-label">Âge</span>
                            <span class="info-row-value">{user.get("age","—")} ans</span>
                        </div>
                        <div class="info-row">
                            <span class="info-row-label">Sexe</span>
                            <span class="info-row-value">{badge(sexe_val)}</span>
                        </div>
                        <div class="info-row">
                            <span class="info-row-label">Abonnement</span>
                            <span class="info-row-value">{badge(abo_val)}</span>
                        </div>
                        <div class="info-row">
                            <span class="info-row-label">Rôle</span>
                            <span class="info-row-value">{badge(str(user.get("app_role", "user")))}</span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

                with col2:
                    c1, c2, c3 = st.columns(3)
                    c1.metric("⚖️ Poids", f"{user.get('poids', '—')} kg")
                    c2.metric("📏 Taille", f"{user.get('taille', '—')} cm")
                    c3.metric("🎂 Âge", f"{user.get('age', '—')} ans")

                    if user.get("objectifs"):
                        objs = user["objectifs"]
                        tags = " ".join(f'<span class="badge badge-autre" style="margin:2px">{o}</span>' for o in objs)
                        st.markdown(f"**Objectifs :** {tags}", unsafe_allow_html=True)

        else:
            st.info("Aucun utilisateur trouvé.")
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
            sexe = st.selectbox("Sexe", ["M", "F", "Autre"])
            poids = st.number_input("Poids (kg)", min_value=20.0, max_value=300.0, value=70.0)
            taille = st.number_input("Taille (cm)", min_value=100.0, max_value=250.0, value=170.0)
            ABO = ["freemium", "premium", "premium+", "B2B"]
            ABO_LABELS = {
                "freemium": "Gratuit (Free)",
                "premium": "Premium",
                "premium+": "Premium+",
                "B2B": "B2B (entreprise)",
            }
            type_abonnement = st.selectbox(
                "Plan d'abonnement",
                ABO,
                index=0,
                format_func=lambda k: ABO_LABELS.get(k, k),
                help="Le plan est stocké côté API (même valeurs : freemium = gratuit, premium = payant).",
            )
            app_role = st.selectbox(
                "Rôle application",
                ["user", "admin"],
                index=0,
                format_func=lambda r: "Administrateur (back-office)" if r == "admin" else "Utilisateur (application)",
            )

        objectifs = st.multiselect(
            "Objectifs",
            ["perte de poids", "musculation", "forme", "cardio", "flexibilité", "endurance"]
        )

        submitted = st.form_submit_button("✅ Créer l'utilisateur", use_container_width=True, type="primary")
        if submitted:
            if nom and prenom and email:
                data = {"nom": nom, "prenom": prenom, "email": email, "age": age,
                        "sexe": sexe, "poids": poids, "taille": taille,
                        "type_abonnement": type_abonnement, "objectifs": objectifs,
                        "app_role": app_role}
                try:
                    result = api_client.post("/utilisateurs", data)
                    uid = result.get("id_utilisateur", "—")
                    flash_success(f"**Enregistrement réussi** — {prenom} {nom} (`{email}`). ID : `{uid}`")
                    st.rerun()
                except Exception as e:
                    st.error(f"Erreur: {e}")
            else:
                st.warning("Veuillez remplir tous les champs obligatoires (*)")
