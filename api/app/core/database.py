"""
Gestion de la connexion à Supabase
"""

from supabase import create_client, Client
from app.core.config import settings

# Clients Supabase (initialisés au démarrage)
supabase: Client = None
supabase_admin: Client = None

def init_supabase():
    """Initialise les clients Supabase"""
    global supabase, supabase_admin
    try:
        supabase = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
        supabase_admin = create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_KEY)
    except Exception as e:
        print(f"⚠️  Erreur lors de l'initialisation Supabase: {e}")
        print("   L'API fonctionnera mais les endpoints nécessitant Supabase échoueront")

# Initialiser au chargement du module
init_supabase()

