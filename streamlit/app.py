import streamlit as st

st.set_page_config(
    page_title="Santé Connectée",
    page_icon="💪",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS pour un design moderne
st.markdown("""
<style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

    /* Global styles */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }

    /* Hero section */
    .hero-container {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 20px;
        padding: 3rem;
        margin-bottom: 2rem;
        color: white;
        text-align: center;
        box-shadow: 0 10px 40px rgba(102, 126, 234, 0.3);
    }

    .hero-title {
        font-size: 2.8rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
    }

    .hero-subtitle {
        font-size: 1.2rem;
        opacity: 0.9;
        margin-bottom: 0;
    }

    /* Stat cards */
    .stat-card {
        background: white;
        border-radius: 16px;
        padding: 1.5rem;
        text-align: center;
        box-shadow: 0 4px 20px rgba(0,0,0,0.08);
        border: 1px solid #f0f0f0;
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }

    .stat-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 30px rgba(0,0,0,0.12);
    }

    .stat-icon {
        font-size: 2.5rem;
        margin-bottom: 0.5rem;
    }

    .stat-value {
        font-size: 2rem;
        font-weight: 700;
        color: #1a1a2e;
        margin: 0.5rem 0;
    }

    .stat-label {
        color: #6b7280;
        font-size: 0.9rem;
        font-weight: 500;
    }

    /* Feature cards */
    .feature-card {
        background: white;
        border-radius: 16px;
        padding: 1.8rem;
        height: 100%;
        box-shadow: 0 4px 20px rgba(0,0,0,0.06);
        border: 1px solid #f0f0f0;
        transition: all 0.3s ease;
    }

    .feature-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 30px rgba(0,0,0,0.1);
        border-color: #667eea;
    }

    .feature-icon {
        width: 50px;
        height: 50px;
        border-radius: 12px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.5rem;
        margin-bottom: 1rem;
    }

    .feature-title {
        font-size: 1.1rem;
        font-weight: 600;
        color: #1a1a2e;
        margin-bottom: 0.5rem;
    }

    .feature-desc {
        color: #6b7280;
        font-size: 0.9rem;
        line-height: 1.5;
    }

    /* Status badge */
    .status-badge {
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        padding: 0.5rem 1rem;
        border-radius: 50px;
        font-size: 0.85rem;
        font-weight: 500;
    }

    .status-online {
        background: #d1fae5;
        color: #065f46;
    }

    .status-offline {
        background: #fee2e2;
        color: #991b1b;
    }

    /* Section titles */
    .section-title {
        font-size: 1.4rem;
        font-weight: 600;
        color: #1a1a2e;
        margin: 2rem 0 1rem 0;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }

    /* Quick action buttons */
    .quick-action {
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
        border-radius: 12px;
        padding: 1rem 1.5rem;
        text-align: center;
        cursor: pointer;
        transition: all 0.3s ease;
        border: 2px solid transparent;
    }

    .quick-action:hover {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
    }

    /* Sidebar styling */
    .sidebar-section {
        background: #f8f9fa;
        border-radius: 12px;
        padding: 1rem;
        margin-bottom: 1rem;
    }

    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# Import API client
try:
    from utils.api_client import api_client
    api_connected = True
except Exception:
    api_connected = False

# Fonction pour récupérer les statistiques
def get_stats():
    stats = {
        "utilisateurs": 0,
        "aliments": 0,
        "exercices": 0,
        "sessions": 0
    }
    if api_connected:
        try:
            stats["utilisateurs"] = len(api_client.get("/utilisateurs"))
        except:
            pass
        try:
            stats["aliments"] = len(api_client.get("/aliments"))
        except:
            pass
        try:
            stats["exercices"] = len(api_client.get("/exercices"))
        except:
            pass
    return stats

stats = get_stats()

# Hero Section
st.markdown("""
<div class="hero-container">
    <div class="hero-title">🏥 Santé Connectée</div>
    <div class="hero-subtitle">Votre plateforme de coaching personnalisé pour une vie plus saine</div>
</div>
""", unsafe_allow_html=True)

# Status badge
if api_connected:
    st.markdown("""
    <div style="text-align: center; margin-bottom: 2rem;">
        <span class="status-badge status-online">
            <span>●</span> Système opérationnel
        </span>
    </div>
    """, unsafe_allow_html=True)
else:
    st.markdown("""
    <div style="text-align: center; margin-bottom: 2rem;">
        <span class="status-badge status-offline">
            <span>●</span> API non disponible
        </span>
    </div>
    """, unsafe_allow_html=True)

# Statistics Cards
st.markdown('<div class="section-title">📊 Tableau de bord</div>', unsafe_allow_html=True)

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(f"""
    <div class="stat-card">
        <div class="stat-icon">👥</div>
        <div class="stat-value">{stats['utilisateurs']}</div>
        <div class="stat-label">Utilisateurs</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="stat-card">
        <div class="stat-icon">🍎</div>
        <div class="stat-value">{stats['aliments']}</div>
        <div class="stat-label">Aliments</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="stat-card">
        <div class="stat-icon">🏋️</div>
        <div class="stat-value">{stats['exercices']}</div>
        <div class="stat-label">Exercices</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown(f"""
    <div class="stat-card">
        <div class="stat-icon">📈</div>
        <div class="stat-value">∞</div>
        <div class="stat-label">Possibilités</div>
    </div>
    """, unsafe_allow_html=True)

# Features Section
st.markdown('<div class="section-title">🚀 Fonctionnalités</div>', unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    <div class="feature-card">
        <div class="feature-icon" style="background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%);">👤</div>
        <div class="feature-title">Gestion des utilisateurs</div>
        <div class="feature-desc">Créez et gérez les profils utilisateurs avec leurs objectifs personnalisés, données biométriques et préférences.</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="feature-card">
        <div class="feature-icon" style="background: linear-gradient(135deg, #d299c2 0%, #fef9d7 100%);">🍎</div>
        <div class="feature-title">Catalogue nutritionnel</div>
        <div class="feature-desc">Accédez à une base de données complète d'aliments avec leurs valeurs nutritionnelles détaillées.</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class="feature-card">
        <div class="feature-icon" style="background: linear-gradient(135deg, #89f7fe 0%, #66a6ff 100%);">🏋️</div>
        <div class="feature-title">Bibliothèque d'exercices</div>
        <div class="feature-desc">Explorez des centaines d'exercices classés par groupe musculaire, niveau et équipement requis.</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    <div class="feature-card">
        <div class="feature-icon" style="background: linear-gradient(135deg, #a1c4fd 0%, #c2e9fb 100%);">📔</div>
        <div class="feature-title">Journal alimentaire</div>
        <div class="feature-desc">Suivez l'alimentation quotidienne de chaque utilisateur et analysez leurs habitudes nutritionnelles.</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="feature-card">
        <div class="feature-icon" style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);">🏃</div>
        <div class="feature-title">Sessions sportives</div>
        <div class="feature-desc">Planifiez et enregistrez les séances d'entraînement avec suivi des calories brûlées et de l'intensité.</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class="feature-card">
        <div class="feature-icon" style="background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);">📊</div>
        <div class="feature-title">Mesures biométriques</div>
        <div class="feature-desc">Suivez l'évolution du poids, IMC, masse grasse et autres indicateurs de santé dans le temps.</div>
    </div>
    """, unsafe_allow_html=True)

# Quick Start Section
st.markdown('<div class="section-title">⚡ Démarrage rapide</div>', unsafe_allow_html=True)

st.info("👈 **Utilisez le menu latéral** pour naviguer entre les différentes sections de l'application.")

col1, col2, col3 = st.columns(3)

with col1:
    if st.button("👤 Gérer les utilisateurs", use_container_width=True):
        st.switch_page("pages/1_👤_Utilisateurs.py")

with col2:
    if st.button("🍎 Voir les aliments", use_container_width=True):
        st.switch_page("pages/2_🍎_Aliments.py")

with col3:
    if st.button("🏋️ Explorer les exercices", use_container_width=True):
        st.switch_page("pages/3_🏋️_Exercices.py")

# Sidebar
st.sidebar.markdown("""
<div style="text-align: center; padding: 1rem 0;">
    <div style="font-size: 2rem;">💪</div>
    <div style="font-size: 1.2rem; font-weight: 600; color: #1a1a2e;">Santé Connectée</div>
    <div style="font-size: 0.8rem; color: #6b7280;">v1.0.0</div>
</div>
""", unsafe_allow_html=True)

st.sidebar.markdown("---")

# System Status in Sidebar
st.sidebar.markdown("### 🔌 État du système")

if api_connected:
    st.sidebar.success("API FastAPI connectée")
    st.sidebar.caption(f"📊 {stats['utilisateurs']} utilisateurs | {stats['aliments']} aliments | {stats['exercices']} exercices")
else:
    st.sidebar.error("API non disponible")
    st.sidebar.caption("Vérifiez que le service API est démarré")

st.sidebar.markdown("---")

# Links
st.sidebar.markdown("### 🔗 Liens utiles")
st.sidebar.markdown("""
- [📚 Documentation API](http://localhost:8000/docs)
- [🔧 Swagger UI](http://localhost:8000/docs)
- [📊 ReDoc](http://localhost:8000/redoc)
""")

st.sidebar.markdown("---")
st.sidebar.caption("© 2024 MSPR Santé Connectée")
