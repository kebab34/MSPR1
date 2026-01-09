"""
Streamlit Application - Interface d'administration
"""
import streamlit as st
import os
from dotenv import load_dotenv
import requests

# Load environment variables
load_dotenv()

# Configuration
API_URL = os.getenv("API_URL", "http://api:8000")
SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")


def check_api_health():
    """Check if API is healthy"""
    try:
        response = requests.get(f"{API_URL}/health", timeout=5)
        return response.status_code == 200
    except:
        return False


# Page configuration
st.set_page_config(
    page_title="MSPR - Interface d'administration",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Sidebar
st.sidebar.title("📊 MSPR Admin")
st.sidebar.markdown("---")

# Navigation
page = st.sidebar.selectbox(
    "Navigation",
    ["🏠 Accueil", "📈 Dashboard", "⚙️ Configuration"]
)

# Main content
if page == "🏠 Accueil":
    st.title("Bienvenue sur l'interface d'administration MSPR")
    st.markdown("---")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("API Status", "🟢 En ligne" if check_api_health() else "🔴 Hors ligne")
    
    with col2:
        st.metric("Base de données", "🟢 Connectée")
    
    with col3:
        st.metric("ETL", "🟢 Actif")
    
    st.markdown("---")
    st.info("👈 Utilisez le menu de gauche pour naviguer dans l'application")

elif page == "📈 Dashboard":
    st.title("📈 Dashboard")
    st.markdown("---")
    st.info("Dashboard à implémenter selon vos besoins")

elif page == "⚙️ Configuration":
    st.title("⚙️ Configuration")
    st.markdown("---")
    
    with st.expander("Configuration API"):
        st.text_input("URL API", value=API_URL, disabled=True)
        st.text_input("URL Supabase", value=SUPABASE_URL, disabled=True)

