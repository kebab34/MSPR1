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
        padding-top: 1rem;
        padding-left: 2rem;
        padding-right: 2rem;
    }
    
    /* Sidebar améliorée style v0 */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1f77b4 0%, #0d5a8a 100%);
    }
    
    [data-testid="stSidebar"] .css-1d391kg {
        background: transparent;
    }
    
    /* Radio buttons dans sidebar style v0 */
    [data-testid="stSidebar"] [data-baseweb="radio"] {
        background: transparent;
    }
    
    [data-testid="stSidebar"] [data-baseweb="radio"] label {
        color: rgba(255, 255, 255, 0.8) !important;
        font-weight: 500;
        padding: 10px 12px !important;
        border-radius: 8px;
        transition: all 0.2s;
        cursor: pointer !important;
        display: block !important;
        width: 100% !important;
        margin: 4px 0 !important;
    }
    
    [data-testid="stSidebar"] [data-baseweb="radio"] label:hover {
        background: rgba(255, 255, 255, 0.1) !important;
        color: white !important;
    }
    
    [data-testid="stSidebar"] [data-baseweb="radio"] input[checked="true"] + label,
    [data-testid="stSidebar"] [data-baseweb="radio"] [checked="true"] + label {
        background: rgba(255, 255, 255, 0.15) !important;
        color: white !important;
    }
    
    /* Assurer que les radio buttons sont cliquables */
    [data-testid="stSidebar"] [data-baseweb="radio"] input {
        cursor: pointer !important;
        z-index: 1;
    }
    
    [data-testid="stSidebar"] [data-baseweb="radio"] > div {
        margin-bottom: 4px;
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
    
    /* Cards avec ombre et effet style v0 */
    .metric-card {
        background: white;
        border-radius: 12px;
        padding: 24px;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
        transition: transform 0.2s, box-shadow 0.2s;
        border: 1px solid #e5e7eb;
    }
    
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.15);
    }
    
    /* Info cards */
    .info-card {
        background: white;
        border-radius: 12px;
        padding: 20px;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
        border-left: 5px solid;
        transition: box-shadow 0.2s;
    }
    
    .info-card:hover {
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.12);
    }
    
    /* Boutons */
    .stButton>button {
        border-radius: 25px;
        background: linear-gradient(90deg, #1f77b4 0%, #0d5a8a 100%);
        color: white;
        font-weight: 600;
        border: none;
        padding: 0.5rem 1.5rem;
        transition: all 0.3s;
    }
    
    .stButton>button:hover {
        background: linear-gradient(90deg, #0d5a8a 0%, #1f77b4 100%);
        transform: scale(1.05);
        box-shadow: 0 4px 8px rgba(31, 119, 180, 0.3);
    }
    
    /* Dataframes */
    .dataframe {
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    /* Success message */
    .success-box {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        border-radius: 8px;
        padding: 15px;
        margin: 10px 0;
    }
    
    /* Hide Streamlit default elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Amélioration des selectbox */
    .stSelectbox > div > div {
        background-color: white;
        border-radius: 8px;
    }
    
    /* Amélioration des inputs */
    .stTextInput > div > div > input {
        border-radius: 8px;
        border: 2px solid #e5e7eb;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #1f77b4;
        box-shadow: 0 0 0 3px rgba(31, 119, 180, 0.1);
    }
    </style>
""", unsafe_allow_html=True)

# Sidebar avec design v0
st.sidebar.markdown("""
    <div style='padding: 20px 0 25px 0; border-bottom: 1px solid rgba(255, 255, 255, 0.2);'>
        <div style='display: flex; align-items: center; gap: 12px; padding: 0 20px;'>
            <div style='display: flex; align-items: center; justify-content: center; width: 40px; height: 40px; background: rgba(255, 255, 255, 0.15); border-radius: 8px;'>
                <span style='font-size: 1.5rem;'>💪</span>
            </div>
            <div>
                <h1 style='color: white; margin: 0; font-size: 1.25rem; font-weight: 700;'>HealthAI</h1>
                <p style='color: rgba(255, 255, 255, 0.7); margin: 2px 0 0 0; font-size: 0.75rem;'>Coach Personnel</p>
            </div>
        </div>
    </div>
""", unsafe_allow_html=True)

# Navigation avec style v0
st.sidebar.markdown("<div style='padding: 8px 0;'></div>", unsafe_allow_html=True)

# Navigation
nav_options = [
    "🏠 Dashboard",
    "🏋️ Exercices",
    "👥 Utilisateurs",
    "🍎 Aliments",
    "⚙️ Configuration"
]

page = st.sidebar.radio(
    "Navigation",
    nav_options,
    label_visibility="collapsed"
)

# Footer sidebar (enlevé pour éviter de bloquer les boutons)
# st.sidebar.markdown("""
#     <div style='padding: 15px 20px; border-top: 1px solid rgba(255, 255, 255, 0.2); margin-top: 20px;'>
#         <p style='color: rgba(255, 255, 255, 0.6); font-size: 0.75rem; margin: 0; text-align: center;'>
#             Plateforme de santé connectée
#         </p>
#     </div>
# """, unsafe_allow_html=True)

# Main content
if page == "🏠 Dashboard":
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
    
    # Métriques avec style v0
    col1, col2, col3, col4 = st.columns(4)
    
    try:
        exercices = get_data_from_api("/api/v1/exercices?limit=1000")
        utilisateurs = get_data_from_api("/api/v1/utilisateurs?limit=1000")
        aliments = get_data_from_api("/api/v1/aliments?limit=1000")
        
        with col1:
            status_bg = "from-emerald-50" if api_status else "from-red-50"
            status_border = "border-t-emerald-500" if api_status else "border-t-red-500"
            status_icon = "✅" if api_status else "❌"
            status_text = "En ligne" if api_status else "Hors ligne"
            status_desc = "Tous les services fonctionnent" if api_status else "Services indisponibles"
            st.markdown(f"""
                <div class='metric-card' style='background: linear-gradient(135deg, #d4edda 0%, white 100%); border-top: 4px solid #28a745;'>
                    <div style='display: flex; align-items: start; justify-content: space-between;'>
                        <div>
                            <p style='font-size: 0.875rem; font-weight: 500; color: #666; margin: 0 0 8px 0;'>API Status</p>
                            <p style='font-size: 1.875rem; font-weight: 700; color: #1f77b4; margin: 0 0 4px 0;'>{status_text}</p>
                            <p style='font-size: 0.75rem; color: #999; margin: 0;'>{status_desc}</p>
                        </div>
                        <div style='background: white; border-radius: 8px; padding: 12px; box-shadow: 0 1px 3px rgba(0,0,0,0.1);'>
                            <span style='font-size: 1.5rem;'>{status_icon}</span>
                        </div>
                    </div>
                </div>
            """, unsafe_allow_html=True)
    
        with col2:
            exercices_count = len(exercices) if exercices else 0
            st.markdown(f"""
                <div class='metric-card' style='background: linear-gradient(135deg, #fff3cd 0%, white 100%); border-top: 4px solid #ffc107;'>
                    <div style='display: flex; align-items: start; justify-content: space-between;'>
                        <div>
                            <p style='font-size: 0.875rem; font-weight: 500; color: #666; margin: 0 0 8px 0;'>Exercices</p>
                            <p style='font-size: 1.875rem; font-weight: 700; color: #1f77b4; margin: 0 0 4px 0;'>{exercices_count}</p>
                            <p style='font-size: 0.75rem; color: #999; margin: 0;'>Base d'exercices</p>
                        </div>
                        <div style='background: white; border-radius: 8px; padding: 12px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); color: #ffc107;'>
                            <span style='font-size: 1.5rem;'>🏋️</span>
                        </div>
                    </div>
                </div>
            """, unsafe_allow_html=True)
        
        with col3:
            users_count = len(utilisateurs) if utilisateurs else 0
            st.markdown(f"""
                <div class='metric-card' style='background: linear-gradient(135deg, #cfe2ff 0%, white 100%); border-top: 4px solid #1f77b4;'>
                    <div style='display: flex; align-items: start; justify-content: space-between;'>
                        <div>
                            <p style='font-size: 0.875rem; font-weight: 500; color: #666; margin: 0 0 8px 0;'>Utilisateurs</p>
                            <p style='font-size: 1.875rem; font-weight: 700; color: #1f77b4; margin: 0 0 4px 0;'>{users_count}</p>
                            <p style='font-size: 0.75rem; color: #999; margin: 0;'>Utilisateurs inscrits</p>
                        </div>
                        <div style='background: white; border-radius: 8px; padding: 12px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); color: #1f77b4;'>
                            <span style='font-size: 1.5rem;'>👥</span>
                        </div>
                    </div>
                </div>
            """, unsafe_allow_html=True)
        
        with col4:
            aliments_count = len(aliments) if aliments else 0
            st.markdown(f"""
                <div class='metric-card' style='background: linear-gradient(135deg, #f8d7da 0%, white 100%); border-top: 4px solid #dc3545;'>
                    <div style='display: flex; align-items: start; justify-content: space-between;'>
                        <div>
                            <p style='font-size: 0.875rem; font-weight: 500; color: #666; margin: 0 0 8px 0;'>Aliments</p>
                            <p style='font-size: 1.875rem; font-weight: 700; color: #1f77b4; margin: 0 0 4px 0;'>{aliments_count}</p>
                            <p style='font-size: 0.75rem; color: #999; margin: 0;'>Base nutritionnelle</p>
                        </div>
                        <div style='background: white; border-radius: 8px; padding: 12px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); color: #dc3545;'>
                            <span style='font-size: 1.5rem;'>🍎</span>
                        </div>
                    </div>
                </div>
            """, unsafe_allow_html=True)
    except:
        st.error("Erreur lors du chargement des données")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # KPIs Business style v0
    st.markdown("### 💼 KPIs Business")
    col1, col2, col3, col4 = st.columns(4)
    
    try:
        if utilisateurs:
            df_usr = pd.DataFrame(utilisateurs)
            total_users = len(df_usr)
            premium_users = len(df_usr[df_usr['type_abonnement'].isin(['premium', 'premium+', 'B2B'])]) if 'type_abonnement' in df_usr.columns else 0
            conversion_rate = (premium_users / total_users * 100) if total_users > 0 else 0
            
            with col1:
                st.markdown(f"""
                    <div style='background: white; border-radius: 12px; padding: 24px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); border: 1px solid #e5e7eb;'>
                        <div style='display: flex; align-items: center; gap: 16px;'>
                            <div style='background: rgba(31, 119, 180, 0.1); border-radius: 8px; padding: 12px;'>
                                <span style='font-size: 1.5rem; color: #1f77b4;'>📈</span>
                            </div>
                            <div>
                                <p style='font-size: 0.875rem; color: #666; margin: 0 0 4px 0;'>Taux Conversion Premium</p>
                                <p style='font-size: 1.5rem; font-weight: 700; color: #1f77b4; margin: 0;'>{conversion_rate:.1f}%</p>
                            </div>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown(f"""
                    <div style='background: white; border-radius: 12px; padding: 24px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); border: 1px solid #e5e7eb;'>
                        <div style='display: flex; align-items: center; gap: 16px;'>
                            <div style='background: rgba(255, 127, 14, 0.1); border-radius: 8px; padding: 12px;'>
                                <span style='font-size: 1.5rem; color: #ff7f0e;'>🎯</span>
                            </div>
                            <div>
                                <p style='font-size: 0.875rem; color: #666; margin: 0 0 4px 0;'>Utilisateurs Premium</p>
                                <p style='font-size: 1.5rem; font-weight: 700; color: #1f77b4; margin: 0;'>{premium_users}</p>
                            </div>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
            
            with col3:
                st.markdown(f"""
                    <div style='background: white; border-radius: 12px; padding: 24px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); border: 1px solid #e5e7eb;'>
                        <div style='display: flex; align-items: center; gap: 16px;'>
                            <div style='background: rgba(16, 185, 129, 0.1); border-radius: 8px; padding: 12px;'>
                                <span style='font-size: 1.5rem; color: #10b981;'>👥</span>
                            </div>
                            <div>
                                <p style='font-size: 0.875rem; color: #666; margin: 0 0 4px 0;'>Utilisateurs Actifs</p>
                                <p style='font-size: 1.5rem; font-weight: 700; color: #1f77b4; margin: 0;'>{total_users}</p>
                            </div>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
            
            with col4:
                if exercices:
                    df_ex = pd.DataFrame(exercices)
                    types_count = len(df_ex['type'].unique()) if 'type' in df_ex.columns else 0
                    st.markdown(f"""
                        <div style='background: white; border-radius: 12px; padding: 24px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); border: 1px solid #e5e7eb;'>
                            <div style='display: flex; align-items: center; gap: 16px;'>
                                <div style='background: rgba(245, 158, 11, 0.1); border-radius: 8px; padding: 12px;'>
                                    <span style='font-size: 1.5rem; color: #f59e0b;'>💪</span>
                                </div>
                                <div>
                                    <p style='font-size: 0.875rem; color: #666; margin: 0 0 4px 0;'>Types d'exercices</p>
                                    <p style='font-size: 1.5rem; font-weight: 700; color: #1f77b4; margin: 0;'>{types_count}</p>
                                </div>
                            </div>
                        </div>
                    """, unsafe_allow_html=True)
    except:
        pass

elif page == "📈 Dashboard":
    st.markdown("""
        <div style='background: linear-gradient(90deg, #1f77b4 0%, #ff7f0e 100%); 
                    padding: 32px; border-radius: 12px; margin-bottom: 32px; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);'>
            <h1 style='color: white; margin: 0; font-size: 1.875rem; font-weight: 700;'>📈 Dashboard</h1>
            <p style='color: rgba(255, 255, 255, 0.8); margin: 8px 0 0 0; font-size: 1rem;'>Vue d'ensemble de vos données</p>
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
        
        # KPIs Business
        st.markdown("### 💼 KPIs Business")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            # Taux de conversion Premium
            if utilisateurs:
                df_usr = pd.DataFrame(utilisateurs)
                total_users = len(df_usr)
                premium_users = len(df_usr[df_usr['type_abonnement'].isin(['premium', 'premium+', 'B2B'])]) if 'type_abonnement' in df_usr.columns else 0
                conversion_rate = (premium_users / total_users * 100) if total_users > 0 else 0
                st.metric("📈 Taux Conversion Premium", f"{conversion_rate:.1f}%", delta=f"{premium_users}/{total_users}")
        
        with col2:
            # Répartition par objectif
            if utilisateurs:
                df_usr = pd.DataFrame(utilisateurs)
                if 'objectifs' in df_usr.columns:
                    # Compter les objectifs (peut être une liste)
                    all_objectifs = []
                    for obj in df_usr['objectifs']:
                        if isinstance(obj, list):
                            all_objectifs.extend(obj)
                        elif isinstance(obj, str):
                            # Essayer de parser si c'est une string représentant une liste
                            try:
                                import ast
                                parsed = ast.literal_eval(obj)
                                if isinstance(parsed, list):
                                    all_objectifs.extend(parsed)
                            except:
                                all_objectifs.append(obj)
                    unique_objectifs = len(set(all_objectifs)) if all_objectifs else 0
                    st.metric("🎯 Objectifs uniques", unique_objectifs)
                else:
                    st.metric("🎯 Objectifs uniques", "N/A")
        
        with col3:
            # Engagement (utilisateurs actifs)
            if utilisateurs:
                df_usr = pd.DataFrame(utilisateurs)
                # Simuler l'engagement (utilisateurs avec données)
                active_users = len(df_usr)  # Simplification
                st.metric("👥 Utilisateurs actifs", active_users)
        
        with col4:
            # Satisfaction (moyenne basée sur progression)
            # Simulation : basée sur le nombre d'utilisateurs premium
            if utilisateurs:
                df_usr = pd.DataFrame(utilisateurs)
                premium_count = len(df_usr[df_usr['type_abonnement'].isin(['premium', 'premium+'])]) if 'type_abonnement' in df_usr.columns else 0
                total = len(df_usr)
                satisfaction = (premium_count / total * 100) if total > 0 else 0
                st.metric("⭐ Satisfaction estimée", f"{satisfaction:.0f}%")
        
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
                    padding: 32px; border-radius: 12px; margin-bottom: 32px; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);'>
            <div style='display: flex; align-items: center; gap: 12px;'>
                <span style='font-size: 2rem;'>🏋️</span>
                <div>
                    <h1 style='color: white; margin: 0; font-size: 1.875rem; font-weight: 700;'>Gestion des Exercices</h1>
                    <p style='color: rgba(255, 255, 255, 0.8); margin: 4px 0 0 0; font-size: 1rem;'>Explorez et gérez votre base d'exercices</p>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    # Onglets pour CRUD
    tab1, tab2, tab3 = st.tabs(["📋 Liste", "➕ Créer", "✏️ Modifier/Supprimer"])
    
    with tab1:
        # Filtres avec style
        st.markdown("### 🔍 Recherche et filtres")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            search_term = st.text_input(
                "🔍 Rechercher un exercice", 
                "",
                placeholder="Ex: pompes, squat, course...",
                key="search_ex"
            )
        
        with col2:
            filter_type = st.selectbox(
                "📋 Type d'exercice", 
                ["Tous", "force", "cardio", "flexibilite", "autre"],
                help="Filtrez par type d'exercice",
                key="filter_type"
            )
        
        with col3:
            filter_niveau = st.selectbox(
                "⭐ Niveau", 
                ["Tous", "debutant", "intermediaire", "avance"],
                help="Filtrez par niveau de difficulté",
                key="filter_niveau"
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
                    display_cols = ['nom', 'type', 'groupe_musculaire', 'niveau', 'equipement', 'description']
                    available_cols = [col for col in display_cols if col in df.columns]
                    
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
    
    with tab2:
        st.markdown("### ➕ Créer un nouvel exercice")
        
        with st.form("create_exercice", clear_on_submit=True):
            col1, col2 = st.columns(2)
            
            with col1:
                nom = st.text_input("Nom de l'exercice *", placeholder="Ex: Pompes")
                type_ex = st.selectbox("Type *", ["force", "cardio", "flexibilite", "autre"])
                groupe_musculaire = st.text_input("Groupe musculaire", placeholder="Ex: pectoraux")
                niveau = st.selectbox("Niveau *", ["debutant", "intermediaire", "avance"])
            
            with col2:
                equipement = st.text_input("Équipement", placeholder="Ex: aucun, haltères...")
                description = st.text_area("Description", placeholder="Description de l'exercice...")
                instructions = st.text_area("Instructions", placeholder="Instructions détaillées...")
                source = st.text_input("Source", value="Manuel", placeholder="Source des données")
            
            submitted = st.form_submit_button("✅ Créer l'exercice", use_container_width=True)
            
            if submitted:
                if not nom:
                    st.error("Le nom est obligatoire")
                else:
                    try:
                        data = {
                            "nom": nom,
                            "type": type_ex,
                            "groupe_musculaire": groupe_musculaire if groupe_musculaire else None,
                            "niveau": niveau,
                            "equipement": equipement if equipement else "aucun",
                            "description": description if description else None,
                            "instructions": instructions if instructions else None,
                            "source": source if source else "Manuel"
                        }
                        
                        response = requests.post(
                            f"{API_URL}/api/v1/exercices",
                            json=data,
                            timeout=10
                        )
                        response.raise_for_status()
                        
                        st.success(f"✅ Exercice '{nom}' créé avec succès !")
                        st.balloons()
                    except Exception as e:
                        st.error(f"❌ Erreur lors de la création: {str(e)}")
    
    with tab3:
        st.markdown("### ✏️ Modifier ou Supprimer un exercice")
        
        try:
            exercices = get_data_from_api("/api/v1/exercices?limit=1000")
            
            if exercices and len(exercices) > 0:
                df = pd.DataFrame(exercices)
                
                # Sélectionner un exercice
                exercice_names = df['nom'].tolist()
                selected_name = st.selectbox("Sélectionner un exercice", exercice_names)
                
                if selected_name:
                    selected_ex = df[df['nom'] == selected_name].iloc[0]
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown("#### 📝 Modifier")
                        with st.form("update_exercice"):
                            nom_upd = st.text_input("Nom", value=selected_ex.get('nom', ''))
                            type_upd = st.selectbox("Type", ["force", "cardio", "flexibilite", "autre"], 
                                                   index=["force", "cardio", "flexibilite", "autre"].index(selected_ex.get('type', 'force')) if selected_ex.get('type') in ["force", "cardio", "flexibilite", "autre"] else 0)
                            niveau_upd = st.selectbox("Niveau", ["debutant", "intermediaire", "avance"],
                                                    index=["debutant", "intermediaire", "avance"].index(selected_ex.get('niveau', 'debutant')) if selected_ex.get('niveau') in ["debutant", "intermediaire", "avance"] else 0)
                            equipement_upd = st.text_input("Équipement", value=selected_ex.get('equipement', ''))
                            description_upd = st.text_area("Description", value=selected_ex.get('description', ''))
                            
                            if st.form_submit_button("💾 Mettre à jour"):
                                try:
                                    data = {
                                        "nom": nom_upd,
                                        "type": type_upd,
                                        "niveau": niveau_upd,
                                        "equipement": equipement_upd,
                                        "description": description_upd
                                    }
                                    
                                    response = requests.put(
                                        f"{API_URL}/api/v1/exercices/{selected_ex['id_exercice']}",
                                        json=data,
                                        timeout=10
                                    )
                                    response.raise_for_status()
                                    
                                    st.success("✅ Exercice mis à jour avec succès !")
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"❌ Erreur: {str(e)}")
                    
                    with col2:
                        st.markdown("#### 🗑️ Supprimer")
                        st.warning(f"⚠️ Vous êtes sur le point de supprimer l'exercice '{selected_name}'")
                        
                        if st.button("🗑️ Supprimer définitivement", type="primary"):
                            try:
                                response = requests.delete(
                                    f"{API_URL}/api/v1/exercices/{selected_ex['id_exercice']}",
                                    timeout=10
                                )
                                response.raise_for_status()
                                
                                st.success("✅ Exercice supprimé avec succès !")
                                st.rerun()
                            except Exception as e:
                                st.error(f"❌ Erreur: {str(e)}")
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
    
    tab1, tab2, tab3 = st.tabs(["📋 Liste", "➕ Créer", "✏️ Modifier/Supprimer"])
    
    with tab1:
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
                    height=400,
                    hide_index=True
                )
            else:
                st.info("Aucun utilisateur disponible")
        
        except Exception as e:
            st.error(f"Erreur: {str(e)}")
    
    with tab2:
        st.markdown("### ➕ Créer un nouvel utilisateur")
        
        with st.form("create_utilisateur", clear_on_submit=True):
            col1, col2 = st.columns(2)
            
            with col1:
                email = st.text_input("Email *", placeholder="exemple@email.com")
                nom = st.text_input("Nom", placeholder="Dupont")
                prenom = st.text_input("Prénom", placeholder="Jean")
                age = st.number_input("Âge", min_value=1, max_value=150, value=25)
            
            with col2:
                sexe = st.selectbox("Sexe", ["M", "F", "Autre"])
                poids = st.number_input("Poids (kg)", min_value=0.0, value=70.0, step=0.1)
                taille = st.number_input("Taille (cm)", min_value=0.0, value=175.0, step=0.1)
                type_abonnement = st.selectbox("Type d'abonnement", ["freemium", "premium", "premium+", "B2B"])
            
            objectifs = st.multiselect("Objectifs", ["perte de poids", "prise de masse", "forme", "cardio", "musculation", "sommeil"])
            
            submitted = st.form_submit_button("✅ Créer l'utilisateur", use_container_width=True)
            
            if submitted:
                if not email:
                    st.error("L'email est obligatoire")
                else:
                    try:
                        data = {
                            "email": email,
                            "nom": nom if nom else None,
                            "prenom": prenom if prenom else None,
                            "age": age if age else None,
                            "sexe": sexe,
                            "poids": poids if poids else None,
                            "taille": taille if taille else None,
                            "type_abonnement": type_abonnement,
                            "objectifs": objectifs if objectifs else []
                        }
                        
                        response = requests.post(
                            f"{API_URL}/api/v1/utilisateurs",
                            json=data,
                            timeout=10
                        )
                        response.raise_for_status()
                        
                        st.success(f"✅ Utilisateur '{email}' créé avec succès !")
                        st.balloons()
                    except Exception as e:
                        st.error(f"❌ Erreur lors de la création: {str(e)}")
    
    with tab3:
        st.markdown("### ✏️ Modifier ou Supprimer un utilisateur")
        
        try:
            utilisateurs = get_data_from_api("/api/v1/utilisateurs?limit=1000")
            
            if utilisateurs and len(utilisateurs) > 0:
                df = pd.DataFrame(utilisateurs)
                
                # Sélectionner un utilisateur
                user_emails = df['email'].tolist()
                selected_email = st.selectbox("Sélectionner un utilisateur", user_emails)
                
                if selected_email:
                    selected_user = df[df['email'] == selected_email].iloc[0]
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown("#### 📝 Modifier")
                        with st.form("update_utilisateur"):
                            email_upd = st.text_input("Email", value=selected_user.get('email', ''))
                            nom_upd = st.text_input("Nom", value=selected_user.get('nom', ''))
                            prenom_upd = st.text_input("Prénom", value=selected_user.get('prenom', ''))
                            age_upd = st.number_input("Âge", min_value=1, max_value=150, value=int(selected_user.get('age', 25)))
                            sexe_upd = st.selectbox("Sexe", ["M", "F", "Autre"], 
                                                  index=["M", "F", "Autre"].index(selected_user.get('sexe', 'M')) if selected_user.get('sexe') in ["M", "F", "Autre"] else 0)
                            poids_upd = st.number_input("Poids (kg)", min_value=0.0, value=float(selected_user.get('poids', 70.0)), step=0.1)
                            taille_upd = st.number_input("Taille (cm)", min_value=0.0, value=float(selected_user.get('taille', 175.0)), step=0.1)
                            type_abonnement_upd = st.selectbox("Type d'abonnement", ["freemium", "premium", "premium+", "B2B"],
                                                             index=["freemium", "premium", "premium+", "B2B"].index(selected_user.get('type_abonnement', 'freemium')) if selected_user.get('type_abonnement') in ["freemium", "premium", "premium+", "B2B"] else 0)
                            
                            if st.form_submit_button("💾 Mettre à jour"):
                                try:
                                    data = {
                                        "email": email_upd,
                                        "nom": nom_upd if nom_upd else None,
                                        "prenom": prenom_upd if prenom_upd else None,
                                        "age": age_upd,
                                        "sexe": sexe_upd,
                                        "poids": poids_upd,
                                        "taille": taille_upd,
                                        "type_abonnement": type_abonnement_upd
                                    }
                                    
                                    response = requests.put(
                                        f"{API_URL}/api/v1/utilisateurs/{selected_user['id_utilisateur']}",
                                        json=data,
                                        timeout=10
                                    )
                                    response.raise_for_status()
                                    
                                    st.success("✅ Utilisateur mis à jour avec succès !")
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"❌ Erreur: {str(e)}")
                    
                    with col2:
                        st.markdown("#### 🗑️ Supprimer")
                        st.warning(f"⚠️ Vous êtes sur le point de supprimer l'utilisateur '{selected_email}'")
                        
                        if st.button("🗑️ Supprimer définitivement", type="primary"):
                            try:
                                response = requests.delete(
                                    f"{API_URL}/api/v1/utilisateurs/{selected_user['id_utilisateur']}",
                                    timeout=10
                                )
                                response.raise_for_status()
                                
                                st.success("✅ Utilisateur supprimé avec succès !")
                                st.rerun()
                            except Exception as e:
                                st.error(f"❌ Erreur: {str(e)}")
            else:
                st.info("Aucun utilisateur disponible")
        except Exception as e:
            st.error(f"Erreur: {str(e)}")

elif page == "🍎 Aliments":
    st.markdown("""
        <div style='background: linear-gradient(90deg, #1f77b4 0%, #ff7f0e 100%); 
                    padding: 32px; border-radius: 12px; margin-bottom: 32px; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);'>
            <div style='display: flex; align-items: center; gap: 12px;'>
                <span style='font-size: 2rem;'>🍎</span>
                <div>
                    <h1 style='color: white; margin: 0; font-size: 1.875rem; font-weight: 700;'>Gestion des Aliments</h1>
                    <p style='color: rgba(255, 255, 255, 0.8); margin: 4px 0 0 0; font-size: 1rem;'>Base de données nutritionnelle complète</p>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["📋 Liste", "➕ Créer", "✏️ Modifier/Supprimer"])
    
    with tab1:
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
                if 'calories' in df.columns and len(df) > 0:
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
                if len(df) > 0:
                    display_cols = ['nom', 'calories', 'proteines', 'glucides', 'lipides', 'fibres', 'unite']
                    available_cols = [col for col in display_cols if col in df.columns]
                    
                    st.dataframe(
                        df[available_cols],
                        use_container_width=True,
                        height=400,
                        hide_index=True
                    )
                else:
                    st.info("Aucun aliment trouvé avec ces critères")
            else:
                st.info("Aucun aliment disponible")
        
        except Exception as e:
            st.error(f"Erreur: {str(e)}")
    
    with tab2:
        st.markdown("### ➕ Créer un nouvel aliment")
        
        with st.form("create_aliment", clear_on_submit=True):
            col1, col2 = st.columns(2)
            
            with col1:
                nom = st.text_input("Nom de l'aliment *", placeholder="Ex: Pomme")
                calories = st.number_input("Calories (kcal) *", min_value=0.0, value=0.0, step=0.1)
                proteines = st.number_input("Protéines (g)", min_value=0.0, value=0.0, step=0.1)
                glucides = st.number_input("Glucides (g)", min_value=0.0, value=0.0, step=0.1)
            
            with col2:
                lipides = st.number_input("Lipides (g)", min_value=0.0, value=0.0, step=0.1)
                fibres = st.number_input("Fibres (g)", min_value=0.0, value=0.0, step=0.1)
                unite = st.text_input("Unité", value="100g", placeholder="Ex: 100g, 1 portion...")
                source = st.text_input("Source", placeholder="Ex: Kaggle, Manuel...")
            
            submitted = st.form_submit_button("✅ Créer l'aliment", use_container_width=True)
            
            if submitted:
                if not nom or calories < 0:
                    st.error("Le nom et les calories sont obligatoires")
                else:
                    try:
                        data = {
                            "nom": nom,
                            "calories": calories,
                            "proteines": proteines,
                            "glucides": glucides,
                            "lipides": lipides,
                            "fibres": fibres,
                            "unite": unite if unite else "100g",
                            "source": source if source else None
                        }
                        
                        response = requests.post(
                            f"{API_URL}/api/v1/aliments",
                            json=data,
                            timeout=10
                        )
                        response.raise_for_status()
                        
                        st.success(f"✅ Aliment '{nom}' créé avec succès !")
                        st.balloons()
                    except Exception as e:
                        st.error(f"❌ Erreur lors de la création: {str(e)}")
    
    with tab3:
        st.markdown("### ✏️ Modifier ou Supprimer un aliment")
        
        try:
            aliments = get_data_from_api("/api/v1/aliments?limit=1000")
            
            if aliments and len(aliments) > 0:
                df = pd.DataFrame(aliments)
                
                # Sélectionner un aliment
                aliment_names = df['nom'].tolist()
                selected_name = st.selectbox("Sélectionner un aliment", aliment_names)
                
                if selected_name:
                    selected_al = df[df['nom'] == selected_name].iloc[0]
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown("#### 📝 Modifier")
                        with st.form("update_aliment"):
                            nom_upd = st.text_input("Nom", value=selected_al.get('nom', ''))
                            calories_upd = st.number_input("Calories (kcal)", min_value=0.0, value=float(selected_al.get('calories', 0.0)), step=0.1)
                            proteines_upd = st.number_input("Protéines (g)", min_value=0.0, value=float(selected_al.get('proteines', 0.0)), step=0.1)
                            glucides_upd = st.number_input("Glucides (g)", min_value=0.0, value=float(selected_al.get('glucides', 0.0)), step=0.1)
                            lipides_upd = st.number_input("Lipides (g)", min_value=0.0, value=float(selected_al.get('lipides', 0.0)), step=0.1)
                            fibres_upd = st.number_input("Fibres (g)", min_value=0.0, value=float(selected_al.get('fibres', 0.0)), step=0.1)
                            unite_upd = st.text_input("Unité", value=selected_al.get('unite', '100g'))
                            
                            if st.form_submit_button("💾 Mettre à jour"):
                                try:
                                    data = {
                                        "nom": nom_upd,
                                        "calories": calories_upd,
                                        "proteines": proteines_upd,
                                        "glucides": glucides_upd,
                                        "lipides": lipides_upd,
                                        "fibres": fibres_upd,
                                        "unite": unite_upd
                                    }
                                    
                                    response = requests.put(
                                        f"{API_URL}/api/v1/aliments/{selected_al['id_aliment']}",
                                        json=data,
                                        timeout=10
                                    )
                                    response.raise_for_status()
                                    
                                    st.success("✅ Aliment mis à jour avec succès !")
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"❌ Erreur: {str(e)}")
                    
                    with col2:
                        st.markdown("#### 🗑️ Supprimer")
                        st.warning(f"⚠️ Vous êtes sur le point de supprimer l'aliment '{selected_name}'")
                        
                        if st.button("🗑️ Supprimer définitivement", type="primary"):
                            try:
                                response = requests.delete(
                                    f"{API_URL}/api/v1/aliments/{selected_al['id_aliment']}",
                                    timeout=10
                                )
                                response.raise_for_status()
                                
                                st.success("✅ Aliment supprimé avec succès !")
                                st.rerun()
                            except Exception as e:
                                st.error(f"❌ Erreur: {str(e)}")
            else:
                st.info("Aucun aliment disponible")
        except Exception as e:
            st.error(f"Erreur: {str(e)}")

elif page == "⚙️ Configuration":
    st.markdown("""
        <div style='background: linear-gradient(90deg, #1f77b4 0%, #ff7f0e 100%); 
                    padding: 20px; border-radius: 10px; margin-bottom: 30px;'>
            <h1 style='color: white; margin: 0;'>⚙️ Configuration & Outils</h1>
            <p style='color: white; margin: 10px 0 0 0;'>Gestion de la qualité des données et export</p>
        </div>
    """, unsafe_allow_html=True)
    
    # Onglets
    tab1, tab2, tab3, tab4 = st.tabs(["🔧 Configuration", "🧹 Nettoyage", "📊 Qualité", "💾 Export"])
    
    with tab1:
        st.markdown("### 🔧 Configuration du système")
        
        with st.expander("Configuration API"):
            st.text_input("URL API", value=API_URL, disabled=True, key="api_url")
            st.text_input("URL Supabase", value=SUPABASE_URL[:50] + "..." if SUPABASE_URL else "", disabled=True, key="supabase_url")
        
        with st.expander("Statut des services"):
            api_status = check_api_health()
            st.write(f"API: {'🟢 En ligne' if api_status else '🔴 Hors ligne'}")
            st.write(f"Base de données: 🟢 Connectée")
        
        st.markdown("---")
        st.info("💡 Pour modifier la configuration, éditez le fichier `.env` à la racine du projet")
    
    with tab2:
        st.markdown("### 🧹 Outils de Nettoyage Interactifs")
        st.markdown("Corrigez manuellement les anomalies détectées dans vos données.")
        
        # Sélection de la table
        table_choice = st.selectbox(
            "Sélectionner une table à nettoyer",
            ["exercices", "aliments", "utilisateurs", "journal_alimentaire", "sessions_sport", "mesures_biometriques"]
        )
        
        try:
            data = get_data_from_api(f"/api/v1/{table_choice}?limit=1000")
            
            if data and len(data) > 0:
                df = pd.DataFrame(data)
                
                st.markdown(f"#### 📋 Données de la table `{table_choice}` ({len(df)} enregistrements)")
                
                # Afficher les anomalies détectées
                st.markdown("##### 🔍 Anomalies détectées")
                
                anomalies = []
                
                # Détecter les doublons
                if 'nom' in df.columns:
                    duplicates = df[df.duplicated(subset=['nom'], keep=False)]
                    if len(duplicates) > 0:
                        anomalies.append(f"⚠️ {len(duplicates)} doublons détectés (basés sur 'nom')")
                
                # Détecter les valeurs manquantes
                missing = df.isnull().sum()
                missing_cols = missing[missing > 0]
                if len(missing_cols) > 0:
                    anomalies.append(f"⚠️ Valeurs manquantes: {dict(missing_cols)}")
                
                # Détecter les valeurs négatives pour les champs numériques
                numeric_cols = df.select_dtypes(include=['float64', 'int64']).columns
                negative_values = {}
                for col in numeric_cols:
                    if col in ['calories', 'proteines', 'glucides', 'lipides', 'poids', 'taille', 'age']:
                        neg_count = (df[col] < 0).sum()
                        if neg_count > 0:
                            negative_values[col] = neg_count
                if negative_values:
                    anomalies.append(f"⚠️ Valeurs négatives détectées: {negative_values}")
                
                if anomalies:
                    for anomaly in anomalies:
                        st.warning(anomaly)
                else:
                    st.success("✅ Aucune anomalie détectée")
                
                st.markdown("---")
                
                # Afficher les données avec possibilité de modification
                st.markdown("##### ✏️ Modifier les données")
                
                # Sélectionner un enregistrement
                if 'nom' in df.columns:
                    record_names = df['nom'].tolist()
                elif 'id' in df.columns:
                    record_names = [f"ID: {id}" for id in df['id'].tolist()]
                else:
                    record_names = [f"Ligne {i+1}" for i in range(len(df))]
                
                selected_record = st.selectbox("Sélectionner un enregistrement à modifier", record_names)
                
                if selected_record:
                    if 'nom' in df.columns:
                        selected_idx = df[df['nom'] == selected_record].index[0]
                    else:
                        selected_idx = record_names.index(selected_record)
                    
                    record = df.iloc[selected_idx].to_dict()
                    
                    st.markdown("**Données actuelles:**")
                    st.json(record)
                    
                    st.info("💡 Pour modifier cet enregistrement, utilisez la page de gestion correspondante (Exercices, Utilisateurs, Aliments)")
                
            else:
                st.info(f"Aucune donnée disponible dans la table `{table_choice}`")
        
        except Exception as e:
            st.error(f"Erreur lors du chargement des données: {str(e)}")
    
    with tab3:
        st.markdown("### 📊 Métriques de Qualité des Données")
        
        try:
            # Récupérer les données de toutes les tables
            exercices = get_data_from_api("/api/v1/exercices?limit=1000")
            aliments = get_data_from_api("/api/v1/aliments?limit=1000")
            utilisateurs = get_data_from_api("/api/v1/utilisateurs?limit=1000")
            
            # Calculer les métriques
            metrics = {}
            
            if exercices:
                df_ex = pd.DataFrame(exercices)
                metrics['exercices'] = {
                    'total': len(df_ex),
                    'doublons': df_ex.duplicated(subset=['nom']).sum() if 'nom' in df_ex.columns else 0,
                    'valeurs_manquantes': df_ex.isnull().sum().sum(),
                    'taux_qualite': ((len(df_ex) - df_ex.duplicated(subset=['nom']).sum() - df_ex.isnull().sum().sum()) / len(df_ex) * 100) if len(df_ex) > 0 else 0
                }
            
            if aliments:
                df_al = pd.DataFrame(aliments)
                metrics['aliments'] = {
                    'total': len(df_al),
                    'doublons': df_al.duplicated(subset=['nom']).sum() if 'nom' in df_al.columns else 0,
                    'valeurs_manquantes': df_al.isnull().sum().sum(),
                    'taux_qualite': ((len(df_al) - df_al.duplicated(subset=['nom']).sum() - df_al.isnull().sum().sum()) / len(df_al) * 100) if len(df_al) > 0 else 0
                }
            
            if utilisateurs:
                df_usr = pd.DataFrame(utilisateurs)
                metrics['utilisateurs'] = {
                    'total': len(df_usr),
                    'doublons': df_usr.duplicated(subset=['email']).sum() if 'email' in df_usr.columns else 0,
                    'valeurs_manquantes': df_usr.isnull().sum().sum(),
                    'taux_qualite': ((len(df_usr) - df_usr.duplicated(subset=['email']).sum() - df_usr.isnull().sum().sum()) / len(df_usr) * 100) if len(df_usr) > 0 else 0
                }
            
            # Afficher les métriques
            for table, data in metrics.items():
                st.markdown(f"#### 📊 {table.capitalize()}")
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("Total", data['total'])
                
                with col2:
                    st.metric("Doublons", data['doublons'], delta="à corriger" if data['doublons'] > 0 else None)
                
                with col3:
                    st.metric("Valeurs manquantes", data['valeurs_manquantes'], delta="à compléter" if data['valeurs_manquantes'] > 0 else None)
                
                with col4:
                    st.metric("Taux de qualité", f"{data['taux_qualite']:.1f}%", 
                             delta="✅ Excellent" if data['taux_qualite'] >= 95 else "⚠️ À améliorer" if data['taux_qualite'] >= 80 else "❌ Critique")
                
                st.markdown("---")
        
        except Exception as e:
            st.error(f"Erreur lors du calcul des métriques: {str(e)}")
    
    with tab4:
        st.markdown("### 💾 Export des Données Nettoyées")
        st.markdown("Exportez vos données dans différents formats pour analyse ou sauvegarde.")
        
        # Sélection de la table
        export_table = st.selectbox(
            "Sélectionner une table à exporter",
            ["exercices", "aliments", "utilisateurs", "journal_alimentaire", "sessions_sport", "mesures_biometriques"]
        )
        
        # Format d'export
        export_format = st.radio(
            "Format d'export",
            ["CSV", "JSON"],
            horizontal=True
        )
        
        try:
            data = get_data_from_api(f"/api/v1/{export_table}?limit=10000")
            
            if data and len(data) > 0:
                df = pd.DataFrame(data)
                
                st.markdown(f"#### 📋 Données à exporter: `{export_table}`")
                st.info(f"📊 {len(df)} enregistrements disponibles")
                
                # Aperçu
                st.markdown("##### 👁️ Aperçu des données")
                st.dataframe(df.head(10), use_container_width=True)
                
                # Boutons d'export
                col1, col2 = st.columns(2)
                
                with col1:
                    if export_format == "CSV":
                        csv = df.to_csv(index=False).encode('utf-8')
                        st.download_button(
                            label="📥 Télécharger en CSV",
                            data=csv,
                            file_name=f"{export_table}_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.csv",
                            mime="text/csv",
                            use_container_width=True
                        )
                    else:
                        json_str = df.to_json(orient='records', indent=2)
                        st.download_button(
                            label="📥 Télécharger en JSON",
                            data=json_str,
                            file_name=f"{export_table}_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.json",
                            mime="application/json",
                            use_container_width=True
                        )
                
                with col2:
                    st.info("💡 Les données exportées sont les données actuellement stockées dans la base de données.")
                
            else:
                st.info(f"Aucune donnée disponible dans la table `{export_table}`")
        
        except Exception as e:
            st.error(f"Erreur lors de l'export: {str(e)}")

