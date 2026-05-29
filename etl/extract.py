"""
ETL - Extract Module
Extract data from various sources
"""
import pandas as pd          # librairie pour manipuler les tableaux de données
import os                    # pour lire les variables d'environnement (clé API RapidAPI)
from typing import Optional, List  # pour typer les arguments des fonctions
import logging               # pour écrire des messages de log

logging.basicConfig(level=logging.INFO)  # configure le niveau de log minimum à INFO
logger = logging.getLogger(__name__)     # crée un logger avec le nom du fichier courant


def extract_from_csv(file_path: str) -> pd.DataFrame:
    """
    Lit un fichier CSV et retourne un DataFrame pandas.
    """
    try:
        df = pd.read_csv(file_path, on_bad_lines='skip')  # lit le CSV, ignore les lignes malformées
        logger.info(f"Extracted {len(df)} rows from {file_path}")  # log du nombre de lignes lues
        return df  # retourne le tableau de données
    except Exception as e:
        logger.error(f"Error extracting from CSV: {str(e)}")  # log de l'erreur si ça plante
        raise  # relance l'exception pour que le pipeline la capture


def extract_from_excel(file_path: str, sheet_name: Optional[str] = None) -> pd.DataFrame:
    """
    Lit un fichier Excel et retourne un DataFrame pandas.
    sheet_name est optionnel : si non fourni, lit la première feuille.
    """
    try:
        df = pd.read_excel(file_path, sheet_name=sheet_name)  # lit le fichier Excel
        logger.info(f"Extracted {len(df)} rows from {file_path}")
        return df
    except Exception as e:
        logger.error(f"Error extracting from Excel: {str(e)}")
        raise


def extract_from_api(api_url: str, params: Optional[dict] = None) -> pd.DataFrame:
    """
    Appelle une API REST et convertit la réponse JSON en DataFrame pandas.
    params permet de passer des paramètres de requête (ex: limit, offset).
    """
    try:
        import requests  # librairie pour faire des requêtes HTTP
        response = requests.get(api_url, params=params)  # envoie une requête GET à l'URL
        response.raise_for_status()  # lève une erreur si le code HTTP est 4xx ou 5xx
        data = response.json()       # convertit la réponse en dictionnaire Python
        df = pd.DataFrame(data)      # convertit le dictionnaire en DataFrame
        logger.info(f"Extracted {len(df)} rows from API: {api_url}")
        return df
    except Exception as e:
        logger.error(f"Error extracting from API: {str(e)}")
        raise


def extract_exercises_from_exercisedb(limit: int = 100) -> pd.DataFrame:
    """
    Récupère les exercices depuis ExerciseDB.
    Essaie d'abord la source publique GitHub (sans clé API),
    puis bascule sur RapidAPI si la clé RAPIDAPI_KEY est définie.
    """
    try:
        import requests

        # URL de l'API ExerciseDB payante (RapidAPI)
        base_url = "https://exercisedb.p.rapidapi.com/exercises"

        # Headers pour RapidAPI (la clé est optionnelle, vide par défaut)
        headers = {
            "X-RapidAPI-Key": os.getenv("RAPIDAPI_KEY", ""),  # lit la clé depuis le .env
            "X-RapidAPI-Host": "exercisedb.p.rapidapi.com"
        }

        try:
            # Source publique gratuite : fichier JSON sur GitHub, pas besoin de clé
            public_url = "https://raw.githubusercontent.com/yuhonas/free-exercise-db/main/dist/exercises.json"
            response = requests.get(public_url, timeout=30)  # timeout de 30 secondes max
            response.raise_for_status()  # vérifie que la requête a réussi
            exercises = response.json()  # convertit la réponse en liste Python

            # On limite au nombre demandé pour ne pas charger trop de données
            if limit and len(exercises) > limit:
                exercises = exercises[:limit]

            df = pd.DataFrame(exercises)  # convertit la liste en DataFrame
            logger.info(f"Extracted {len(df)} exercises from ExerciseDB (public source)")
            return df

        except Exception as e:
            logger.warning(f"Public source failed, trying RapidAPI: {str(e)}")
            # Si la source publique échoue, on essaie RapidAPI si une clé est disponible
            if os.getenv("RAPIDAPI_KEY"):
                response = requests.get(base_url, headers=headers, params={"limit": limit}, timeout=30)
                response.raise_for_status()
                exercises = response.json()
                df = pd.DataFrame(exercises)
                logger.info(f"Extracted {len(df)} exercises from ExerciseDB (RapidAPI)")
                return df
            else:
                raise ValueError("No API key provided and public source unavailable")  # aucune source dispo

    except Exception as e:
        logger.error(f"Error extracting exercises from ExerciseDB: {str(e)}")
        raise
