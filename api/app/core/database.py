"""
Gestion de la connexion à Supabase
"""

from supabase import create_client, Client  # client officiel Supabase pour Python
from app.core.config import settings        # importe la configuration (URL, clés...)

# Deux clients Supabase sont créés :
# - supabase : clé publique (accès limité, respecte les politiques RLS)
# - supabase_admin : clé de service (accès total, contourne les politiques RLS)
supabase: Client = None        # sera initialisé par init_supabase()
supabase_admin: Client = None  # sera initialisé par init_supabase()

def init_supabase():
    """Crée les deux connexions Supabase au démarrage de l'API."""
    global supabase, supabase_admin  # modifie les variables globales définies au-dessus
    try:
        supabase = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)               # client public
        supabase_admin = create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_KEY) # client admin
    except Exception as e:
        # Si Supabase n'est pas disponible au démarrage, on affiche un avertissement sans planter
        print(f"⚠️  Erreur lors de l'initialisation Supabase: {e}")
        print("   L'API fonctionnera mais les endpoints nécessitant Supabase échoueront")

# Appel immédiat à l'initialisation dès que ce fichier est importé (au démarrage de l'API)
init_supabase()
