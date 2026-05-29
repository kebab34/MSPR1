"""
Téléchargement automatique des datasets Kaggle nécessaires au pipeline ETL.

Le paquet Python `kaggle` impose un fichier kaggle.json avec "username" et "key"
(ou les variables KAGGLE_USERNAME + KAGGLE_KEY), pas un token seul.

- Linux : si le dossier ~/.kaggle n'existe pas, le fichier attendu est
  ~/.config/kaggle/kaggle.json (voir erreur "Could not find kaggle.json").

Options :
  1) Settings → « Legacy API Credentials » → Create Legacy API Key → placer le JSON
     au bon chemin ci-dessus.

  2) Export avant de lancer le script :
       export KAGGLE_USERNAME='ton_pseudo_kaggle'
       export KAGGLE_KEY='ta_clé_api'   # ou KAGGLE_API_TOKEN si elle joue le rôle de clé

  pip install kaggle
  python3 download_data.py
"""

import json       # pour écrire le fichier kaggle.json (format JSON)
import os         # pour accéder aux variables d'environnement et manipuler les chemins de fichiers
import shutil     # pour renommer/déplacer des fichiers téléchargés
import sys        # pour détecter le système d'exploitation (Linux vs Windows)

# Dossier où seront stockés les fichiers CSV téléchargés (etl/data/)
DATA_DIR = os.path.join(os.path.dirname(__file__), "data")

# Liste des datasets Kaggle à télécharger, avec leur slug (identifiant Kaggle) et nom de fichier attendu
DATASETS = [
    {
        "slug": "adilshamim8/daily-food-and-nutrition-dataset",   # identifiant du dataset sur Kaggle
        "file": "daily_food_nutrition_dataset.csv",               # nom du fichier dans etl/data/
        "kaggle_file": "daily_food_nutrition_dataset.csv",        # nom du fichier tel que Kaggle le télécharge
    },
    {
        "slug": "valakhorasani/gym-members-exercise-dataset",
        "file": "gym_members_exercise_tracking.csv",
        "kaggle_file": "gym_members_exercise_tracking.csv",
    },
    {
        "slug": "ziya07/diet-recommendations-dataset",
        "file": "diet_recommendations_dataset.csv",
        "kaggle_file": "diet_recommendations_dataset.csv",
    },
]


def _kaggle_config_dir() -> str:
    """Retourne le dossier où kaggle.json doit être placé, selon l'OS."""
    override = os.environ.get("KAGGLE_CONFIG_DIR")  # si une variable d'env pointe vers un dossier custom
    if override:
        return override  # on utilise ce dossier custom

    legacy = os.path.expanduser("~/.kaggle")  # chemin classique sur Windows et Mac
    if sys.platform.startswith("linux") and not os.path.exists(legacy):
        # sur Linux, si ~/.kaggle n'existe pas, on cherche dans le dossier XDG standard
        return os.path.join(
            os.environ.get("XDG_CONFIG_HOME") or os.path.expanduser("~/.config"),
            "kaggle",
        )
    return legacy  # retourne ~/.kaggle par défaut


def _ensure_kaggle_json() -> None:
    """Crée automatiquement kaggle.json à partir des variables d'environnement si le fichier n'existe pas."""
    cfg_dir = _kaggle_config_dir()           # récupère le bon dossier selon l'OS
    path = os.path.join(cfg_dir, "kaggle.json")  # chemin complet du fichier kaggle.json
    if os.path.isfile(path):
        return  # le fichier existe déjà, rien à faire

    user = os.environ.get("KAGGLE_USERNAME", "").strip()  # lit le nom d'utilisateur Kaggle depuis .env
    key = (os.environ.get("KAGGLE_KEY") or os.environ.get("KAGGLE_API_TOKEN") or "").strip()  # lit la clé API
    if user and key:
        os.makedirs(cfg_dir, mode=0o700, exist_ok=True)  # crée le dossier avec permissions restreintes
        with open(path, "w", encoding="utf-8") as f:
            json.dump({"username": user, "key": key}, f)  # écrit le fichier JSON avec les credentials
        os.chmod(path, 0o600)  # restreint les permissions du fichier (lecture seule par le propriétaire)
        print(f"ℹ️  kaggle.json écrit : {path}\n")


def check_kaggle_credentials() -> None:
    """Vérifie que les credentials Kaggle sont disponibles, sinon lève une erreur claire."""
    _ensure_kaggle_json()  # tente de créer kaggle.json depuis les variables d'env

    path = os.path.join(_kaggle_config_dir(), "kaggle.json")  # chemin du fichier à vérifier
    if os.path.isfile(path):
        return  # le fichier existe, on peut continuer

    # Si le fichier n'existe toujours pas, on lève une erreur avec un message explicatif
    raise RuntimeError(
        "Credentials Kaggle manquants. "
        "Définissez KAGGLE_USERNAME et KAGGLE_KEY dans le .env "
        "(obtenez-les sur https://www.kaggle.com/settings → API → Legacy API Credentials)."
    )


def _print_kaggle_403_help() -> None:
    """Affiche des conseils quand Kaggle refuse l'accès avec une erreur 403."""
    print()
    print("💡 Erreur 403 (Forbidden) — pistes courantes :")
    print("  • Va sur la page web du dataset (connecté avec le compte lié à ton kaggle.json).")
    print("  • Clique sur « Download » une première fois : une fenêtre peut demander")
    print("    d'accepter les conditions ; valide-les.")
    print("  • Kaggle impose parfois un téléphone vérifié : Account → ton profil → Phone Verification.")
    print("  • Ensuite relance : python3 download_data.py")
    print()
    print("  Plan B : télécharge le .zip depuis le site, dézippe le CSV dans etl/data/,")
    print("  puis renomme-le exactement comme dans la liste DATASETS du script.")
    print()


def download_datasets():
    """Télécharge tous les datasets Kaggle manquants dans etl/data/."""
    check_kaggle_credentials()  # vérifie que les credentials sont présents avant de commencer

    try:
        import kaggle  # importe la librairie Kaggle (doit être installée via pip)
    except ImportError:
        raise RuntimeError("Package 'kaggle' non installé. Ajoutez-le dans requirements.txt.")

    os.makedirs(DATA_DIR, exist_ok=True)  # crée le dossier etl/data/ s'il n'existe pas

    for ds in DATASETS:  # boucle sur chaque dataset à télécharger
        target = os.path.join(DATA_DIR, ds["file"])  # chemin final du fichier CSV

        if os.path.exists(target):
            print(f"⏭️  {ds['file']} déjà présent, on passe.")  # fichier déjà là, on skip
            continue

        print(f"📥 Téléchargement : {ds['slug']} ...")
        try:
            kaggle.api.dataset_download_files(
                ds["slug"],   # identifiant du dataset sur Kaggle (ex: "adilshamim8/daily-food...")
                path=DATA_DIR,  # dossier de destination
                unzip=True,     # dézippe automatiquement le fichier téléchargé
                quiet=False,    # affiche la progression du téléchargement
            )

            # Si Kaggle donne un nom différent de celui attendu, on renomme le fichier
            kaggle_path = os.path.join(DATA_DIR, ds["kaggle_file"])
            if ds["kaggle_file"] != ds["file"] and os.path.exists(kaggle_path):
                shutil.move(kaggle_path, target)  # renomme le fichier au nom attendu

            if os.path.exists(target):
                print(f"✅ {ds['file']} téléchargé avec succès.")
            else:
                # Le fichier n'est pas là malgré le téléchargement — affiche ce qui est présent pour aider
                files = os.listdir(DATA_DIR)
                print(f"⚠️  Fichier attendu '{ds['file']}' introuvable.")
                print(f"   Fichiers présents dans data/ : {files}")
                print(f"   Renomme manuellement le bon fichier en : {ds['file']}")

        except Exception as e:
            print(f"❌ Erreur pour {ds['slug']} : {e}")
            if "403" in str(e):
                _print_kaggle_403_help()  # affiche les conseils si c'est une erreur 403

    print()
    print("Fichiers présents dans etl/data/ :")
    for f in os.listdir(DATA_DIR):
        print(f"  - {f}")  # liste tous les fichiers présents dans le dossier


if __name__ == "__main__":
    download_datasets()  # si on lance ce fichier directement, on télécharge les datasets
