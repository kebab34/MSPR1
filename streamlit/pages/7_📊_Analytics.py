import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from utils.api_client import api_client

st.set_page_config(page_title="Analytics", page_icon="📊", layout="wide")
st.title("📊 Analytics & Dashboard")
st.markdown("---")


@st.cache_data(ttl=60)
def fetch_all(endpoint: str, total_limit: int = 2000) -> list:
    """Récupère toutes les données en paginant par tranches de 1000."""
    all_data = []
    step = 1000
    for skip in range(0, total_limit, step):
        batch = api_client.get(endpoint, params={"skip": skip, "limit": step})
        if not batch:
            break
        all_data.extend(batch)
        if len(batch) < step:
            break
    return all_data


# ── Chargement des données ──────────────────────────────────────────────────
try:
    with st.spinner("Chargement des données..."):
        utilisateurs = fetch_all("/utilisateurs", total_limit=3000)
        aliments = fetch_all("/aliments", total_limit=1000)
        exercices = fetch_all("/exercices", total_limit=500)
        mesures = fetch_all("/mesures", total_limit=2000)

    df_users = pd.DataFrame(utilisateurs) if utilisateurs else pd.DataFrame()
    df_aliments = pd.DataFrame(aliments) if aliments else pd.DataFrame()
    df_exercices = pd.DataFrame(exercices) if exercices else pd.DataFrame()
    df_mesures = pd.DataFrame(mesures) if mesures else pd.DataFrame()

except Exception as e:
    st.error(f"Impossible de charger les données depuis l'API : {e}")
    st.stop()

# ── KPIs ────────────────────────────────────────────────────────────────────
st.subheader("🔢 Indicateurs clés")
k1, k2, k3, k4 = st.columns(4)
k1.metric("👥 Utilisateurs", len(df_users))
k2.metric("🍎 Aliments", len(df_aliments))
k3.metric("🏋️ Exercices", len(df_exercices))
k4.metric("📏 Mesures biométriques", len(df_mesures))

st.markdown("---")

# ── Section Utilisateurs ────────────────────────────────────────────────────
st.subheader("👥 Utilisateurs")

col_abo, col_sexe, col_age = st.columns(3)

# Répartition abonnements
with col_abo:
    if "type_abonnement" in df_users.columns:
        abo_counts = df_users["type_abonnement"].value_counts().reset_index()
        abo_counts.columns = ["Abonnement", "Nombre"]
        fig_abo = px.pie(
            abo_counts,
            names="Abonnement",
            values="Nombre",
            title="Répartition des abonnements",
            color_discrete_sequence=px.colors.qualitative.Set2,
            hole=0.35,
        )
        fig_abo.update_layout(margin=dict(t=40, b=0, l=0, r=0))
        st.plotly_chart(fig_abo, use_container_width=True)
    else:
        st.info("Colonne type_abonnement absente")

# Répartition sexe
with col_sexe:
    if "sexe" in df_users.columns:
        sexe_counts = df_users["sexe"].value_counts().reset_index()
        sexe_counts.columns = ["Sexe", "Nombre"]
        fig_sexe = px.pie(
            sexe_counts,
            names="Sexe",
            values="Nombre",
            title="Répartition Hommes / Femmes",
            color_discrete_sequence=["#636EFA", "#EF553B", "#00CC96"],
            hole=0.35,
        )
        fig_sexe.update_layout(margin=dict(t=40, b=0, l=0, r=0))
        st.plotly_chart(fig_sexe, use_container_width=True)
    else:
        st.info("Colonne sexe absente")

# Distribution des âges
with col_age:
    if "age" in df_users.columns:
        ages = pd.to_numeric(df_users["age"], errors="coerce").dropna()
        fig_age = px.histogram(
            ages,
            x=ages,
            nbins=20,
            title="Distribution des âges",
            labels={"x": "Âge"},
            color_discrete_sequence=["#00CC96"],
        )
        fig_age.update_layout(showlegend=False, margin=dict(t=40, b=0, l=0, r=0))
        st.plotly_chart(fig_age, use_container_width=True)
    else:
        st.info("Colonne age absente")

# IMC moyen par abonnement
if {"poids", "taille", "type_abonnement"}.issubset(df_users.columns):
    df_imc = df_users.copy()
    df_imc["poids"] = pd.to_numeric(df_imc["poids"], errors="coerce")
    df_imc["taille"] = pd.to_numeric(df_imc["taille"], errors="coerce")
    df_imc = df_imc.dropna(subset=["poids", "taille"])
    df_imc = df_imc[df_imc["taille"] > 0]
    df_imc["IMC"] = df_imc["poids"] / (df_imc["taille"] / 100) ** 2
    imc_by_abo = df_imc.groupby("type_abonnement")["IMC"].mean().reset_index()
    imc_by_abo.columns = ["Abonnement", "IMC moyen"]
    fig_imc = px.bar(
        imc_by_abo,
        x="Abonnement",
        y="IMC moyen",
        title="IMC moyen par type d'abonnement",
        color="Abonnement",
        color_discrete_sequence=px.colors.qualitative.Set2,
        text_auto=".1f",
    )
    fig_imc.update_layout(showlegend=False, margin=dict(t=40, b=0, l=0, r=0))
    st.plotly_chart(fig_imc, use_container_width=True)

st.markdown("---")

# ── Section Aliments ────────────────────────────────────────────────────────
st.subheader("🍎 Aliments")

col_top_cal, col_macro = st.columns(2)

with col_top_cal:
    if "calories" in df_aliments.columns and "nom" in df_aliments.columns:
        df_aliments["calories"] = pd.to_numeric(df_aliments["calories"], errors="coerce")
        top_cal = df_aliments.nlargest(15, "calories")[["nom", "calories"]].dropna()
        fig_top = px.bar(
            top_cal,
            y="nom",
            x="calories",
            orientation="h",
            title="Top 15 aliments les plus caloriques",
            labels={"calories": "Calories (kcal)", "nom": "Aliment"},
            color="calories",
            color_continuous_scale="Reds",
        )
        fig_top.update_layout(margin=dict(t=40, b=0, l=0, r=0), yaxis=dict(autorange="reversed"))
        fig_top.update_coloraxes(showscale=False)
        st.plotly_chart(fig_top, use_container_width=True)

with col_macro:
    macro_cols = ["proteines", "glucides", "lipides", "fibres"]
    present = [c for c in macro_cols if c in df_aliments.columns]
    if present:
        moyennes = {col: pd.to_numeric(df_aliments[col], errors="coerce").mean() for col in present}
        fig_macro = go.Figure(go.Bar(
            x=list(moyennes.keys()),
            y=list(moyennes.values()),
            marker_color=["#636EFA", "#EF553B", "#FFA15A", "#00CC96"],
            text=[f"{v:.1f}g" for v in moyennes.values()],
            textposition="outside",
        ))
        fig_macro.update_layout(
            title="Macronutriments moyens (pour 100g)",
            xaxis_title="Macronutriment",
            yaxis_title="Quantité (g)",
            margin=dict(t=40, b=0, l=0, r=0),
        )
        st.plotly_chart(fig_macro, use_container_width=True)

# Distribution calories (histogramme)
if "calories" in df_aliments.columns:
    calories_clean = pd.to_numeric(df_aliments["calories"], errors="coerce").dropna()
    calories_clean = calories_clean[calories_clean < 1000]  # exclure valeurs aberrantes
    fig_dist_cal = px.histogram(
        calories_clean,
        x=calories_clean,
        nbins=30,
        title="Distribution des calories (aliments)",
        labels={"x": "Calories (kcal)"},
        color_discrete_sequence=["#EF553B"],
    )
    fig_dist_cal.update_layout(showlegend=False, margin=dict(t=40, b=0, l=0, r=0))
    st.plotly_chart(fig_dist_cal, use_container_width=True)

st.markdown("---")

# ── Section Exercices ───────────────────────────────────────────────────────
st.subheader("🏋️ Exercices")

col_type, col_niveau, col_muscle = st.columns(3)

with col_type:
    if "type" in df_exercices.columns:
        type_counts = df_exercices["type"].value_counts().reset_index()
        type_counts.columns = ["Type", "Nombre"]
        fig_type = px.pie(
            type_counts,
            names="Type",
            values="Nombre",
            title="Répartition par type",
            color_discrete_sequence=px.colors.qualitative.Pastel,
            hole=0.35,
        )
        fig_type.update_layout(margin=dict(t=40, b=0, l=0, r=0))
        st.plotly_chart(fig_type, use_container_width=True)

with col_niveau:
    if "niveau" in df_exercices.columns:
        niveau_counts = df_exercices["niveau"].value_counts().reset_index()
        niveau_counts.columns = ["Niveau", "Nombre"]
        fig_niv = px.bar(
            niveau_counts,
            x="Niveau",
            y="Nombre",
            title="Répartition par niveau",
            color="Niveau",
            color_discrete_sequence=px.colors.qualitative.Set3,
            text_auto=True,
        )
        fig_niv.update_layout(showlegend=False, margin=dict(t=40, b=0, l=0, r=0))
        st.plotly_chart(fig_niv, use_container_width=True)

with col_muscle:
    if "groupe_musculaire" in df_exercices.columns:
        muscle_counts = (
            df_exercices["groupe_musculaire"]
            .dropna()
            .value_counts()
            .head(10)
            .reset_index()
        )
        muscle_counts.columns = ["Groupe musculaire", "Nombre"]
        fig_muscle = px.bar(
            muscle_counts,
            y="Groupe musculaire",
            x="Nombre",
            orientation="h",
            title="Top 10 groupes musculaires",
            color="Nombre",
            color_continuous_scale="Blues",
        )
        fig_muscle.update_layout(
            margin=dict(t=40, b=0, l=0, r=0),
            yaxis=dict(autorange="reversed"),
        )
        fig_muscle.update_coloraxes(showscale=False)
        st.plotly_chart(fig_muscle, use_container_width=True)

st.markdown("---")

# ── Section Mesures biométriques ────────────────────────────────────────────
st.subheader("📏 Mesures biométriques")

if df_mesures.empty:
    st.info("Aucune mesure biométrique disponible.")
else:
    col_bpm, col_cal_br = st.columns(2)

    with col_bpm:
        if "frequence_cardiaque" in df_mesures.columns:
            bpm = pd.to_numeric(df_mesures["frequence_cardiaque"], errors="coerce").dropna()
            fig_bpm = px.histogram(
                bpm,
                x=bpm,
                nbins=30,
                title="Distribution fréquence cardiaque (BPM)",
                labels={"x": "BPM"},
                color_discrete_sequence=["#FF6692"],
            )
            fig_bpm.update_layout(showlegend=False, margin=dict(t=40, b=0, l=0, r=0))
            st.plotly_chart(fig_bpm, use_container_width=True)

    with col_cal_br:
        if "calories_brulees" in df_mesures.columns:
            cal_br = pd.to_numeric(df_mesures["calories_brulees"], errors="coerce").dropna()
            fig_cal_br = px.histogram(
                cal_br,
                x=cal_br,
                nbins=30,
                title="Distribution calories brûlées",
                labels={"x": "Calories"},
                color_discrete_sequence=["#FFA15A"],
            )
            fig_cal_br.update_layout(showlegend=False, margin=dict(t=40, b=0, l=0, r=0))
            st.plotly_chart(fig_cal_br, use_container_width=True)

    # Stats résumées
    st.markdown("#### Statistiques descriptives")
    numeric_mesures = df_mesures.select_dtypes(include="number")
    if not numeric_mesures.empty:
        st.dataframe(numeric_mesures.describe().round(2), use_container_width=True)

st.markdown("---")
st.caption("Données actualisées toutes les 60 secondes · Source : API HealthAI Coach")
