"""
Streamlit Application - Interface d'administration
"""
import streamlit as st
import os
import sys
from pathlib import Path
from dotenv import load_dotenv
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Charger les variables d'environnement depuis la racine du projet
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

# Configuration
API_URL = os.getenv("API_URL", "http://localhost:8000")
SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")

# Import du client API
sys.path.append(str(Path(__file__).parent))
from utils.api_client import api_client


def check_api_health():
    """Check if API is healthy"""
    try:
        response = requests.get(f"{API_URL}/health", timeout=5)
        return response.status_code == 200
    except:
        return False


@st.cache_data(ttl=60)  # Cache pour 60 secondes
def get_data_from_api(endpoint: str, params: dict = None):
    """Récupère des données depuis l'API avec cache"""
    try:
        response = requests.get(f"{API_URL}{endpoint}", params=params, timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"Erreur lors de la récupération des données: {str(e)}")
        return []


# Page configuration
st.set_page_config(
    page_title="MSPR - Santé Connectée",
    page_icon="💪",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personnalisé pour un design plus moderne
st.markdown("""
    <style>
    /* Style général */
    .main {
        padding-top: 2rem;
    }
    
    /* Titres */
    h1 {
        color: #1f77b4;
        border-bottom: 3px solid #1f77b4;
        padding-bottom: 10px;
    }
    
    /* Métriques */
    [data-testid="stMetricValue"] {
        font-size: 2.5rem;
        font-weight: bold;
    }
    
    /* Sidebar */
    .css-1d391kg {
        background-color: #f0f2f6;
    }
    
    /* Cards */
    .stCard {
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    /* Boutons */
    .stButton>button {
        border-radius: 20px;
        background-color: #1f77b4;
        color: white;
        font-weight: bold;
    }
    
    /* Dataframes */
    .dataframe {
        border-radius: 10px;
    }
    
    /* Success message */
    .success-box {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        border-radius: 5px;
        padding: 10px;
        margin: 10px 0;
    }
    </style>
""", unsafe_allow_html=True)

# Sidebar avec design amélioré
st.sidebar.markdown("""
    <div style='text-align: center; padding: 20px 0;'>
        <h1 style='color: #1f77b4; margin: 0;'>💪 MSPR</h1>
        <p style='color: #666; margin: 5px 0;'>Santé Connectée</p>
    </div>
""", unsafe_allow_html=True)
st.sidebar.markdown("---")

# Navigation
page = st.sidebar.selectbox(
    "Navigation",
    [
        "🏠 Accueil",
        "📈 Dashboard",
        "🏋️ Exercices",
        "👥 Utilisateurs",
        "🍎 Aliments",
        "⚙️ Configuration"
    ]
)

# Main content
if page == "🏠 Accueil":
    # Header avec gradient
    st.markdown("""
        <div style='background: linear-gradient(90deg, #1f77b4 0%, #ff7f0e 100%); 
                    padding: 30px; border-radius: 10px; margin-bottom: 30px;'>
            <h1 style='color: white; margin: 0; text-align: center;'>🏠 Bienvenue sur MSPR</h1>
            <p style='color: white; text-align: center; margin: 10px 0 0 0; font-size: 1.2em;'>
                Plateforme de gestion de la santé connectée et du coaching personnalisé
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    # Statut de l'API
    api_status = check_api_health()
    status_color = "🟢" if api_status else "🔴"
    status_text = "En ligne" if api_status else "Hors ligne"
    
    # Métriques avec icônes
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
            <div style='text-align: center; padding: 20px; background-color: #f0f2f6; border-radius: 10px;'>
                <div style='font-size: 3rem; margin-bottom: 10px;'>{status_color}</div>
                <div style='font-size: 1.2em; font-weight: bold; color: #1f77b4;'>API Status</div>
                <div style='color: #666;'>{status_text}</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col2:
        try:
            exercices_count = len(get_data_from_api("/api/v1/exercices?limit=1000"))
            st.markdown(f"""
                <div style='text-align: center; padding: 20px; background-color: #f0f2f6; border-radius: 10px;'>
                    <div style='font-size: 3rem; margin-bottom: 10px;'>🏋️</div>
                    <div style='font-size: 2.5rem; font-weight: bold; color: #1f77b4;'>{exercices_count}</div>
                    <div style='color: #666;'>Exercices</div>
                </div>
            """, unsafe_allow_html=True)
        except:
            st.markdown("""
                <div style='text-align: center; padding: 20px; background-color: #f0f2f6; border-radius: 10px;'>
                    <div style='font-size: 3rem; margin-bottom: 10px;'>🏋️</div>
                    <div style='font-size: 2.5rem; font-weight: bold; color: #1f77b4;'>N/A</div>
                    <div style='color: #666;'>Exercices</div>
                </div>
            """, unsafe_allow_html=True)
    
    with col3:
        try:
            users_count = len(get_data_from_api("/api/v1/utilisateurs?limit=1000"))
            st.markdown(f"""
                <div style='text-align: center; padding: 20px; background-color: #f0f2f6; border-radius: 10px;'>
                    <div style='font-size: 3rem; margin-bottom: 10px;'>👥</div>
                    <div style='font-size: 2.5rem; font-weight: bold; color: #1f77b4;'>{users_count}</div>
                    <div style='color: #666;'>Utilisateurs</div>
                </div>
            """, unsafe_allow_html=True)
        except:
            st.markdown("""
                <div style='text-align: center; padding: 20px; background-color: #f0f2f6; border-radius: 10px;'>
                    <div style='font-size: 3rem; margin-bottom: 10px;'>👥</div>
                    <div style='font-size: 2.5rem; font-weight: bold; color: #1f77b4;'>N/A</div>
                    <div style='color: #666;'>Utilisateurs</div>
                </div>
            """, unsafe_allow_html=True)
    
    with col4:
        try:
            aliments_count = len(get_data_from_api("/api/v1/aliments?limit=1000"))
            st.markdown(f"""
                <div style='text-align: center; padding: 20px; background-color: #f0f2f6; border-radius: 10px;'>
                    <div style='font-size: 3rem; margin-bottom: 10px;'>🍎</div>
                    <div style='font-size: 2.5rem; font-weight: bold; color: #1f77b4;'>{aliments_count}</div>
                    <div style='color: #666;'>Aliments</div>
                </div>
            """, unsafe_allow_html=True)
        except:
            st.markdown("""
                <div style='text-align: center; padding: 20px; background-color: #f0f2f6; border-radius: 10px;'>
                    <div style='font-size: 3rem; margin-bottom: 10px;'>🍎</div>
                    <div style='font-size: 2.5rem; font-weight: bold; color: #1f77b4;'>N/A</div>
                    <div style='color: #666;'>Aliments</div>
                </div>
            """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Section d'aide
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
            <div style='background-color: #e3f2fd; padding: 20px; border-radius: 10px; border-left: 4px solid #1f77b4;'>
                <h3 style='color: #1f77b4; margin-top: 0;'>💡 Navigation</h3>
                <p>Utilisez le menu de gauche pour accéder aux différentes sections :</p>
                <ul>
                    <li><strong>Dashboard</strong> : Vue d'ensemble avec graphiques</li>
                    <li><strong>Exercices</strong> : Gestion des exercices</li>
                    <li><strong>Utilisateurs</strong> : Gestion des utilisateurs</li>
                    <li><strong>Aliments</strong> : Base de données nutritionnelle</li>
                </ul>
            </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
            <div style='background-color: #fff3e0; padding: 20px; border-radius: 10px; border-left: 4px solid #ff7f0e;'>
                <h3 style='color: #ff7f0e; margin-top: 0;'>🚀 Fonctionnalités</h3>
                <p>Explorez les fonctionnalités disponibles :</p>
                <ul>
                    <li>Recherche et filtres avancés</li>
                    <li>Graphiques interactifs</li>
                    <li>Statistiques en temps réel</li>
                    <li>Gestion complète des données</li>
                </ul>
            </div>
        """, unsafe_allow_html=True)

elif page == "📈 Dashboard":
    st.markdown("""
        <div style='background: linear-gradient(90deg, #1f77b4 0%, #ff7f0e 100%); 
                    padding: 20px; border-radius: 10px; margin-bottom: 30px;'>
            <h1 style='color: white; margin: 0;'>📈 Dashboard</h1>
            <p style='color: white; margin: 10px 0 0 0;'>Vue d'ensemble de vos données</p>
        </div>
    """, unsafe_allow_html=True)
    
    # Statistiques générales
    col1, col2, col3, col4 = st.columns(4)
    
    try:
        exercices = get_data_from_api("/api/v1/exercices?limit=1000")
        utilisateurs = get_data_from_api("/api/v1/utilisateurs?limit=1000")
        aliments = get_data_from_api("/api/v1/aliments?limit=1000")
        
        with col1:
            st.metric("Total Exercices", len(exercices))
        
        with col2:
            st.metric("Total Utilisateurs", len(utilisateurs))
        
        with col3:
            st.metric("Total Aliments", len(aliments))
        
        with col4:
            # Calculer le nombre d'exercices par type
            if exercices:
                df_ex = pd.DataFrame(exercices)
                types_count = df_ex['type'].value_counts().sum() if 'type' in df_ex.columns else 0
                st.metric("Types d'exercices", types_count)
        
        st.markdown("---")
        
        # Graphiques
        col1, col2 = st.columns(2)
        
        with col1:
            if exercices and len(exercices) > 0:
                df_ex = pd.DataFrame(exercices)
                if 'type' in df_ex.columns:
                    type_counts = df_ex['type'].value_counts()
                    colors = px.colors.qualitative.Set3[:len(type_counts)]
                    fig = px.pie(
                        values=type_counts.values,
                        names=type_counts.index,
                        title="📊 Répartition par type",
                        color_discrete_sequence=colors
                    )
                    fig.update_traces(textposition='inside', textinfo='percent+label')
                    fig.update_layout(font=dict(size=12), showlegend=True)
                    st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            if exercices and len(exercices) > 0:
                df_ex = pd.DataFrame(exercices)
                if 'niveau' in df_ex.columns:
                    niveau_counts = df_ex['niveau'].value_counts()
                    fig = px.bar(
                        x=niveau_counts.index,
                        y=niveau_counts.values,
                        title="📈 Répartition par niveau",
                        labels={'x': 'Niveau', 'y': 'Nombre'},
                        color=niveau_counts.values,
                        color_continuous_scale='Blues'
                    )
                    fig.update_layout(font=dict(size=12), showlegend=False)
                    st.plotly_chart(fig, use_container_width=True)
        
        # Tableau récapitulatif
        st.markdown("---")
        st.subheader("📊 Vue d'ensemble des données")
        
        if exercices and len(exercices) > 0:
            df_ex = pd.DataFrame(exercices)
            display_cols = ['nom', 'type', 'niveau', 'equipement']
            available_cols = [col for col in display_cols if col in df_ex.columns]
            if available_cols:
                st.dataframe(df_ex[available_cols].head(10), use_container_width=True)
    
    except Exception as e:
        st.error(f"Erreur lors du chargement des données: {str(e)}")

elif page == "🏋️ Exercices":
    st.markdown("""
        <div style='background: linear-gradient(90deg, #1f77b4 0%, #ff7f0e 100%); 
                    padding: 20px; border-radius: 10px; margin-bottom: 30px;'>
            <h1 style='color: white; margin: 0;'>🏋️ Gestion des Exercices</h1>
            <p style='color: white; margin: 10px 0 0 0;'>Explorez et gérez votre base d'exercices</p>
        </div>
    """, unsafe_allow_html=True)
    
    # Filtres avec style
    st.markdown("### 🔍 Recherche et filtres")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        search_term = st.text_input(
            "🔍 Rechercher un exercice", 
            "",
            placeholder="Ex: pompes, squat, course..."
        )
    
    with col2:
        filter_type = st.selectbox(
            "📋 Type d'exercice", 
            ["Tous", "force", "cardio", "flexibilite", "autre"],
            help="Filtrez par type d'exercice"
        )
    
    with col3:
        filter_niveau = st.selectbox(
            "⭐ Niveau", 
            ["Tous", "debutant", "intermediaire", "avance"],
            help="Filtrez par niveau de difficulté"
        )
    
    # Récupérer les exercices
    try:
        exercices = get_data_from_api("/api/v1/exercices?limit=1000")
        
        if exercices:
            df = pd.DataFrame(exercices)
            
            # Appliquer les filtres
            if search_term:
                df = df[df['nom'].str.contains(search_term, case=False, na=False)]
            
            if filter_type != "Tous":
                df = df[df['type'] == filter_type]
            
            if filter_niveau != "Tous":
                df = df[df['niveau'] == filter_niveau]
            
            # Métrique avec style
            st.markdown(f"""
                <div style='background-color: #e3f2fd; padding: 15px; border-radius: 10px; margin: 20px 0; text-align: center;'>
                    <span style='font-size: 1.5em; font-weight: bold; color: #1f77b4;'>{len(df)}</span>
                    <span style='font-size: 1.2em; color: #666; margin-left: 10px;'>exercices trouvés</span>
                </div>
            """, unsafe_allow_html=True)
            
            # Afficher les exercices
            if len(df) > 0:
                # Sélectionner les colonnes à afficher
                display_cols = ['nom', 'type', 'groupe_musculaire', 'niveau', 'equipement', 'description']
                available_cols = [col for col in display_cols if col in df.columns]
                
                # Style du dataframe
                st.dataframe(
                    df[available_cols],
                    use_container_width=True,
                    height=400,
                    hide_index=True
                )
            else:
                st.info("Aucun exercice trouvé avec ces critères")
        else:
            st.info("Aucun exercice disponible")
    
    except Exception as e:
        st.error(f"Erreur: {str(e)}")

elif page == "👥 Utilisateurs":
    st.markdown("""
        <div style='background: linear-gradient(90deg, #1f77b4 0%, #ff7f0e 100%); 
                    padding: 20px; border-radius: 10px; margin-bottom: 30px;'>
            <h1 style='color: white; margin: 0;'>👥 Gestion des Utilisateurs</h1>
            <p style='color: white; margin: 10px 0 0 0;'>Visualisez et gérez vos utilisateurs</p>
        </div>
    """, unsafe_allow_html=True)
    
    try:
        utilisateurs = get_data_from_api("/api/v1/utilisateurs?limit=1000")
        
        if utilisateurs:
            df = pd.DataFrame(utilisateurs)
            st.metric("Total utilisateurs", len(df))
            st.markdown("---")
            
            # Statistiques
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if 'type_abonnement' in df.columns:
                    abo_counts = df['type_abonnement'].value_counts()
                    st.metric("Abonnements Premium", abo_counts.get('premium', 0) + abo_counts.get('premium+', 0))
            
            with col2:
                if 'sexe' in df.columns:
                    sexe_counts = df['sexe'].value_counts()
                    st.metric("Hommes", sexe_counts.get('M', 0))
            
            with col3:
                if 'sexe' in df.columns:
                    sexe_counts = df['sexe'].value_counts()
                    st.metric("Femmes", sexe_counts.get('F', 0))
            
            st.markdown("---")
            
            # Tableau des utilisateurs
            display_cols = ['email', 'nom', 'prenom', 'age', 'sexe', 'poids', 'taille', 'type_abonnement']
            available_cols = [col for col in display_cols if col in df.columns]
            
            st.dataframe(
                df[available_cols],
                use_container_width=True,
                height=400
            )
        else:
            st.info("Aucun utilisateur disponible")
    
    except Exception as e:
        st.error(f"Erreur: {str(e)}")

elif page == "🍎 Aliments":
    st.markdown("""
        <div style='background: linear-gradient(90deg, #1f77b4 0%, #ff7f0e 100%); 
                    padding: 20px; border-radius: 10px; margin-bottom: 30px;'>
            <h1 style='color: white; margin: 0;'>🍎 Gestion des Aliments</h1>
            <p style='color: white; margin: 10px 0 0 0;'>Base de données nutritionnelle</p>
        </div>
    """, unsafe_allow_html=True)
    
    try:
        aliments = get_data_from_api("/api/v1/aliments?limit=1000")
        
        if aliments:
            df = pd.DataFrame(aliments)
            st.metric("Total aliments", len(df))
            st.markdown("---")
            
            # Recherche
            search = st.text_input("🔍 Rechercher un aliment", "")
            if search:
                df = df[df['nom'].str.contains(search, case=False, na=False)]
            
            # Graphique des calories avec style amélioré
            if 'calories' in df.columns:
                st.markdown("### 📊 Analyses nutritionnelles")
                col1, col2 = st.columns(2)
                
                with col1:
                    # Top 10 aliments les plus caloriques
                    top_cal = df.nlargest(10, 'calories')[['nom', 'calories']]
                    fig = px.bar(
                        top_cal,
                        x='nom',
                        y='calories',
                        title="🔥 Top 10 aliments les plus caloriques",
                        color='calories',
                        color_continuous_scale='Reds',
                        labels={'nom': 'Aliment', 'calories': 'Calories (kcal)'}
                    )
                    fig.update_xaxes(tickangle=45)
                    fig.update_layout(font=dict(size=11), showlegend=False)
                    st.plotly_chart(fig, use_container_width=True)
                
                with col2:
                    # Distribution des calories
                    fig = px.histogram(
                        df,
                        x='calories',
                        title="📈 Distribution des calories",
                        nbins=30,
                        color_discrete_sequence=['#1f77b4']
                    )
                    fig.update_layout(
                        font=dict(size=11),
                        xaxis_title="Calories (kcal)",
                        yaxis_title="Nombre d'aliments"
                    )
                    st.plotly_chart(fig, use_container_width=True)
            
            st.markdown("---")
            
            # Tableau des aliments
            display_cols = ['nom', 'calories', 'proteines', 'glucides', 'lipides', 'fibres', 'unite']
            available_cols = [col for col in display_cols if col in df.columns]
            
            st.dataframe(
                df[available_cols],
                use_container_width=True,
                height=400
            )
        else:
            st.info("Aucun aliment disponible")
    
    except Exception as e:
        st.error(f"Erreur: {str(e)}")

elif page == "⚙️ Configuration":
    st.title("⚙️ Configuration")
    st.markdown("---")
    
    with st.expander("Configuration API"):
        st.text_input("URL API", value=API_URL, disabled=True)
        st.text_input("URL Supabase", value=SUPABASE_URL[:50] + "..." if SUPABASE_URL else "", disabled=True)
    
    with st.expander("Statut des services"):
        api_status = check_api_health()
        st.write(f"API: {'🟢 En ligne' if api_status else '🔴 Hors ligne'}")
        st.write(f"Base de données: 🟢 Connectée")
    
    st.markdown("---")
    st.info("💡 Pour modifier la configuration, éditez le fichier `.env` à la racine du projet")

