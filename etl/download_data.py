"""
Téléchargement automatique des datasets Kaggle nécessaires au pipeline ETL.

Prérequis :
  1. Avoir un compte Kaggle (gratuit) sur kaggle.com
  2. Générer un token API : kaggle.com/settings → API → "Create New Token"
     → télécharge kaggle.json
  3. Placer kaggle.json dans C:/Users/<ton_user>/.kaggle/kaggle.json
  4. pip install kaggle

Ensuite : python download_data.py
"""

import os
import shutil
import sys

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")

DATASETS = [
    {
        "slug": "utsavdesai26/daily-food-and-nutrition-dataset",
        "file": "daily_food_nutrition_dataset.csv",
        "kaggle_file": "daily_food_nutrition_dataset.csv",
    },
    {
        "slug": "valakhorasani/gym-members-exercise-dataset",
        "file": "gym_members_exercise_tracking.csv",
        "kaggle_file": "gym_members_exercise_tracking.csv",
    },
    {
        "slug": "waqi786/diet-recommendation-dataset",
        "file": "diet_recommendations_dataset.csv",
        "kaggle_file": "diet_recommendations_dataset.csv",
    },
]


def check_kaggle_credentials():
    kaggle_json = os.path.expanduser("~/.kaggle/kaggle.json")
    if not os.path.exists(kaggle_json):
        print("❌ Fichier kaggle.json introuvable.")
        print()
        print("Pour le créer :")
        print("  1. Va sur https://www.kaggle.com/settings")
        print("  2. Section 'API' → clique sur 'Create New Token'")
        print("  3. Déplace le fichier téléchargé vers :", kaggle_json)
        sys.exit(1)


def download_datasets():
    check_kaggle_credentials()

    try:
        import kaggle
    except ImportError:
        print("❌ Package 'kaggle' non installé. Lance : pip install kaggle")
        sys.exit(1)

    os.makedirs(DATA_DIR, exist_ok=True)

    for ds in DATASETS:
        target = os.path.join(DATA_DIR, ds["file"])

        if os.path.exists(target):
            print(f"⏭️  {ds['file']} déjà présent, on passe.")
            continue

        print(f"📥 Téléchargement : {ds['slug']} ...")
        try:
            kaggle.api.dataset_download_files(
                ds["slug"],
                path=DATA_DIR,
                unzip=True,
                quiet=False,
            )

            # Renommer si le nom du fichier Kaggle diffère
            kaggle_path = os.path.join(DATA_DIR, ds["kaggle_file"])
            if ds["kaggle_file"] != ds["file"] and os.path.exists(kaggle_path):
                shutil.move(kaggle_path, target)

            if os.path.exists(target):
                print(f"✅ {ds['file']} téléchargé avec succès.")
            else:
                # Lister les fichiers téléchargés pour aider au debug
                files = os.listdir(DATA_DIR)
                print(f"⚠️  Fichier attendu '{ds['file']}' introuvable.")
                print(f"   Fichiers présents dans data/ : {files}")
                print(f"   Renomme manuellement le bon fichier en : {ds['file']}")

        except Exception as e:
            print(f"❌ Erreur pour {ds['slug']} : {e}")

    print()
    print("Fichiers présents dans etl/data/ :")
    for f in os.listdir(DATA_DIR):
        print(f"  - {f}")


if __name__ == "__main__":
    download_datasets()
