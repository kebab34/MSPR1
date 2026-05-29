"""
ETL - Transform Module
Transform and clean data
"""
import ast         # pour convertir des strings comme "['valeur']" en vraies listes Python
import pandas as pd  # pour manipuler les DataFrames
import logging       # pour écrire des messages de log
from typing import Dict, List, Optional  # pour typer les arguments des fonctions

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Listes de prénoms utilisées pour générer des noms fictifs pour les utilisateurs des datasets Kaggle
_PRENOMS_M = ["Thomas", "Nicolas", "Julien", "Alexandre", "Pierre", "Antoine", "Maxime", "Romain", "Lucas", "Hugo",
              "Mathieu", "Quentin", "Clément", "Adrien", "Baptiste", "Florian", "Guillaume", "Kevin", "Yann", "Sébastien"]
_PRENOMS_F = ["Marie", "Sophie", "Julie", "Camille", "Laura", "Lucie", "Emma", "Léa", "Manon", "Chloé",
              "Pauline", "Élodie", "Clara", "Inès", "Charlotte", "Alice", "Sarah", "Anaïs", "Océane", "Marion"]
_NOMS = ["Martin", "Bernard", "Thomas", "Petit", "Robert", "Richard", "Durand", "Dubois", "Moreau", "Laurent",
         "Simon", "Michel", "Lefebvre", "Leroy", "Roux", "David", "Bertrand", "Morel", "Fournier", "Girard"]


def _get_prenom(sexe: str, index: int) -> str:
    """Retourne un prénom fictif selon le sexe et l'index (pour varier les prénoms)."""
    if sexe == "F":
        return _PRENOMS_F[index % len(_PRENOMS_F)]  # % len(...) pour ne jamais dépasser la liste
    return _PRENOMS_M[index % len(_PRENOMS_M)]


def _get_nom(index: int) -> str:
    """Retourne un nom de famille fictif selon l'index."""
    return _NOMS[index % len(_NOMS)]


def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Nettoie un DataFrame :
    - Convertit les colonnes contenant des listes en strings (pour pouvoir détecter les doublons)
    - Supprime les doublons
    - Supprime les lignes entièrement vides
    """
    try:
        for col in df.columns:  # parcourt toutes les colonnes
            if df[col].dtype == 'object':  # ne traite que les colonnes de type texte/objet
                # Vérifie si au moins une cellule de cette colonne contient une liste Python
                if df[col].apply(lambda x: isinstance(x, list)).any():
                    # Convertit les listes en strings pour permettre la comparaison de doublons
                    df[col] = df[col].apply(lambda x: str(x) if isinstance(x, list) else x)

        # Identifie les colonnes dont les valeurs sont comparables (pas des listes ni des dicts)
        hashable_cols = [col for col in df.columns if df[col].dtype != 'object' or not df[col].apply(lambda x: isinstance(x, (list, dict))).any()]

        if hashable_cols:
            df = df.drop_duplicates(subset=hashable_cols)  # supprime les lignes en double sur ces colonnes
        else:
            logger.warning("All columns contain unhashable types, skipping drop_duplicates")

        df = df.dropna(how='all')  # supprime les lignes où TOUTES les colonnes sont vides (NaN)

        logger.info(f"Cleaned data: {len(df)} rows remaining")
        return df
    except Exception as e:
        logger.error(f"Error cleaning data: {str(e)}")
        raise


def normalize_columns(df: pd.DataFrame, column_mapping: Dict[str, str]) -> pd.DataFrame:
    """
    Renomme les colonnes d'un DataFrame selon un dictionnaire de mapping.
    Ex: {"Food_Item": "nom"} renomme la colonne "Food_Item" en "nom".
    """
    try:
        df = df.rename(columns=column_mapping)  # renomme les colonnes selon le dictionnaire
        logger.info(f"Normalized columns: {list(column_mapping.values())}")
        return df
    except Exception as e:
        logger.error(f"Error normalizing columns: {str(e)}")
        raise


def validate_data(df: pd.DataFrame, required_columns: List[str]) -> bool:
    """
    Vérifie que toutes les colonnes obligatoires sont présentes dans le DataFrame.
    Retourne True si tout est ok, False si une colonne manque.
    """
    try:
        missing_columns = set(required_columns) - set(df.columns)  # colonnes attendues mais absentes
        if missing_columns:
            logger.error(f"Missing required columns: {missing_columns}")  # log les colonnes manquantes
            return False  # validation échouée
        logger.info("Data validation passed")
        return True  # toutes les colonnes sont présentes
    except Exception as e:
        logger.error(f"Error validating data: {str(e)}")
        return False


def transform_data(df: pd.DataFrame, transformations: Optional[Dict] = None) -> pd.DataFrame:
    """
    Fonction générique de transformation (réservée pour des transformations custom futures).
    """
    try:
        if transformations:
            for transformation in transformations:
                pass  # logique de transformation à implémenter si besoin

        logger.info(f"Transformed data: {len(df)} rows")
        return df
    except Exception as e:
        logger.error(f"Error transforming data: {str(e)}")
        raise


def transform_exercises_from_exercisedb(df: pd.DataFrame) -> pd.DataFrame:
    """
    Transforme les données brutes de l'API ExerciseDB pour les adapter
    au schéma de la table 'exercices' en base de données.
    """
    try:
        result = pd.DataFrame()  # crée un DataFrame vide qui recevra les colonnes transformées

        # Mappe la colonne 'name' de l'API vers 'nom' dans notre base
        if 'name' in df.columns:
            result['nom'] = df['name']

        # Mappe le type d'exercice (priorité à 'type', sinon utilise 'bodyPart')
        if 'type' in df.columns:
            result['type'] = df['type']
        elif 'bodyPart' in df.columns:
            result['type'] = df['bodyPart']

        # Mappe le groupe musculaire ciblé (priorité à 'target', sinon 'muscle')
        if 'target' in df.columns:
            result['groupe_musculaire'] = df['target']
        elif 'muscle' in df.columns:
            result['groupe_musculaire'] = df['muscle']

        if 'difficulty' in df.columns:
            result['niveau'] = df['difficulty']  # niveau de difficulté

        if 'equipment' in df.columns:
            result['equipement'] = df['equipment']  # équipement nécessaire

        if 'instructions' in df.columns:
            # Les instructions peuvent être une liste de strings → on les joint en une seule string
            result['instructions'] = df['instructions'].apply(
                lambda x: ', '.join(x) if isinstance(x, list) else str(x) if x else None
            )

        # Génère une description basique à partir du nom
        if 'name' in df.columns:
            result['description'] = df['name'].apply(lambda x: f"Exercice: {x}")

        # Normalise les types d'exercices vers les valeurs attendues en base (français)
        if 'type' in result.columns:
            result['type'] = result['type'].astype(str).str.lower().replace({
                'strength': 'force',
                'cardio': 'cardio',
                'stretching': 'flexibilite',
                'powerlifting': 'force',
                'strongman': 'force',
                'olympic_weightlifting': 'force',
                'chest': 'force',
                'back': 'force',
                'shoulders': 'force',
                'arms': 'force',
                'legs': 'force'
            })
        else:
            result['type'] = 'autre'  # valeur par défaut si la colonne est absente

        # Normalise les niveaux vers les valeurs attendues en base (français)
        if 'niveau' in result.columns:
            result['niveau'] = result['niveau'].astype(str).str.lower().replace({
                'beginner': 'debutant',
                'intermediate': 'intermediaire',
                'expert': 'avance',
                'advanced': 'avance'
            })
        else:
            result['niveau'] = 'debutant'  # valeur par défaut

        # Normalise l'équipement vers les valeurs attendues en base (français)
        if 'equipement' in result.columns:
            result['equipement'] = result['equipement'].astype(str).str.lower().replace({
                'body weight': 'aucun',
                'none': 'aucun',
                '': 'aucun',
                'dumbbell': 'haltères',
                'barbell': 'barre',
                'cable': 'câble',
                'machine': 'machine'
            })
        else:
            result['equipement'] = 'aucun'  # valeur par défaut

        if 'groupe_musculaire' not in result.columns:
            result['groupe_musculaire'] = None  # None si absent (valeur nulle en base)

        result['source'] = 'ExerciseDB API'  # trace l'origine des données

        result = result.where(pd.notna(result), None)  # remplace tous les NaN par None (compatible JSON)

        logger.info(f"Transformed {len(result)} exercises")
        return result

    except Exception as e:
        logger.error(f"Error transforming exercises: {str(e)}")
        raise


def restore_list_columns(df: pd.DataFrame, list_columns: List[str]) -> pd.DataFrame:
    """
    Reconvertit les colonnes qui ont été transformées en strings par clean_data
    en vraies listes Python, nécessaires pour les colonnes PostgreSQL de type TEXT[].
    Ex: "['fitness']" redevient ['fitness'].
    """
    for col in list_columns:  # parcourt les colonnes à reconvertir
        if col in df.columns:
            df[col] = df[col].apply(
                lambda x: ast.literal_eval(x)          # convertit la string "['x']" en liste ['x']
                if isinstance(x, str) and x.startswith('[')  # seulement si c'est une string qui ressemble à une liste
                else x  # sinon on laisse la valeur telle quelle
            )
    return df


def transform_nutrition_dataset(df: pd.DataFrame) -> pd.DataFrame:
    """
    Transforme le dataset 'Daily Food & Nutrition' (Kaggle) vers le schéma de la table 'aliments'.
    Colonnes source : Food_Item, Calories (kcal), Protein (g), Carbohydrates (g), Fat (g), Fiber (g)
    """
    try:
        result = pd.DataFrame()  # DataFrame vide qui recevra les colonnes transformées
        result['nom'] = df['Food_Item'].astype(str).str.strip()  # nom de l'aliment, sans espaces superflus
        result['calories'] = pd.to_numeric(df['Calories (kcal)'], errors='coerce').fillna(0.0)  # calories, 0 si invalide
        result['proteines'] = pd.to_numeric(df['Protein (g)'], errors='coerce').fillna(0.0)
        result['glucides'] = pd.to_numeric(df['Carbohydrates (g)'], errors='coerce').fillna(0.0)
        result['lipides'] = pd.to_numeric(df['Fat (g)'], errors='coerce').fillna(0.0)
        result['fibres'] = pd.to_numeric(df['Fiber (g)'], errors='coerce').fillna(0.0)
        result['unite'] = '100g'  # toutes les valeurs nutritionnelles sont pour 100g
        result['source'] = 'Kaggle - Daily Food & Nutrition Dataset'  # traçabilité de l'origine
        result = result.dropna(subset=['nom'])   # supprime les lignes sans nom
        result = result[result['nom'] != '']     # supprime les lignes avec un nom vide
        result = result.where(pd.notna(result), None)  # remplace les NaN par None
        logger.info(f"Transformed {len(result)} foods from nutrition dataset")
        return result
    except Exception as e:
        logger.error(f"Error transforming nutrition dataset: {str(e)}")
        raise


def transform_gym_members_to_utilisateurs(df: pd.DataFrame) -> pd.DataFrame:
    """
    Transforme le dataset 'Gym Members Exercise' (Kaggle) vers le schéma de la table 'utilisateurs'.
    Génère des emails fictifs uniques et des prénoms/noms aléatoires car le dataset n'en contient pas.
    """
    try:
        result = pd.DataFrame()
        # Génère des emails uniques et reproductibles (même email pour le même index à chaque run)
        result['email'] = [f"gym.member.{i:04d}@healthai.com" for i in range(len(df))]
        result['age'] = pd.to_numeric(df['Age'], errors='coerce').astype('Int64')  # Int64 supporte les valeurs manquantes
        result['sexe'] = df['Gender'].map({'Male': 'M', 'Female': 'F'}).fillna('Autre')  # traduit en M/F
        result['prenom'] = [_get_prenom(s, i) for i, s in enumerate(result['sexe'])]  # prénom fictif selon le sexe
        result['nom'] = [_get_nom(i) for i in range(len(df))]  # nom de famille fictif
        result['poids'] = pd.to_numeric(df['Weight (kg)'], errors='coerce').round(2)
        result['taille'] = (pd.to_numeric(df['Height (m)'], errors='coerce') * 100).round(2)  # converti m → cm
        # Mappe le niveau d'expérience vers le type d'abonnement (1-2 = freemium, 3 = premium)
        result['type_abonnement'] = df['Experience_Level'].map({
            1: 'freemium',
            2: 'freemium',
            3: 'premium',
        }).fillna('freemium')
        # Génère un objectif basé sur le type d'entraînement du dataset
        result['objectifs'] = df['Workout_Type'].apply(
            lambda x: [f"Entraînement: {x}"] if pd.notna(x) else ['fitness']
        )
        result = result.where(pd.notna(result), None)  # remplace les NaN par None
        logger.info(f"Transformed {len(result)} utilisateurs from gym members dataset")
        return result
    except Exception as e:
        logger.error(f"Error transforming gym members to utilisateurs: {str(e)}")
        raise


def transform_gym_members_to_mesures(df: pd.DataFrame, email_to_id: dict) -> pd.DataFrame:
    """
    Transforme le dataset 'Gym Members Exercise' vers le schéma de la table 'mesures_biometriques'.
    email_to_id est un dictionnaire {email: uuid} construit depuis la base après insertion des utilisateurs,
    nécessaire pour lier chaque mesure à son utilisateur.
    """
    try:
        result = pd.DataFrame()
        emails = [f"gym.member.{i:04d}@healthai.com" for i in range(len(df))]  # reconstruit les emails fictifs
        result['id_utilisateur'] = [email_to_id.get(e) for e in emails]  # résout l'UUID via le dictionnaire
        result['poids'] = pd.to_numeric(df['Weight (kg)'], errors='coerce').round(2)
        result['frequence_cardiaque'] = pd.to_numeric(df['Avg_BPM'], errors='coerce').astype('Int64')  # fréquence cardiaque moyenne
        result['calories_brulees'] = pd.to_numeric(df['Calories_Burned'], errors='coerce').round(2)
        result['sommeil'] = None  # donnée non disponible dans ce dataset
        result = result.dropna(subset=['id_utilisateur'])  # supprime les lignes sans utilisateur associé
        result = result.where(pd.notna(result), None)
        logger.info(f"Transformed {len(result)} mesures from gym members dataset")
        return result
    except Exception as e:
        logger.error(f"Error transforming gym members to mesures: {str(e)}")
        raise


def transform_diet_reco_to_utilisateurs(df: pd.DataFrame) -> pd.DataFrame:
    """
    Transforme le dataset 'Diet Recommendations' (Kaggle) vers le schéma de la table 'utilisateurs'.
    Colonnes source : Patient_ID, Age, Gender, Weight_kg, Height_cm, Severity, Diet_Recommendation
    """
    try:
        result = pd.DataFrame()
        # Génère un email à partir du Patient_ID (ex: "patient001" → "patient001@healthai.com")
        result['email'] = df['Patient_ID'].astype(str).str.lower().apply(
            lambda x: f"{x}@healthai.com"
        )
        result['age'] = pd.to_numeric(df['Age'], errors='coerce').astype('Int64')
        result['sexe'] = df['Gender'].map({'Male': 'M', 'Female': 'F'}).fillna('Autre')
        result['prenom'] = [_get_prenom(s, i) for i, s in enumerate(result['sexe'])]
        result['nom'] = [_get_nom(i) for i in range(len(df))]
        result['poids'] = pd.to_numeric(df['Weight_kg'], errors='coerce').round(2)
        result['taille'] = pd.to_numeric(df['Height_cm'], errors='coerce').round(2)
        # Mappe la sévérité médicale vers le type d'abonnement
        result['type_abonnement'] = df['Severity'].map({
            'Mild': 'freemium',
            'Moderate': 'premium',
            'Severe': 'premium+',
        }).fillna('freemium')
        # Utilise la recommandation diététique comme objectif utilisateur
        result['objectifs'] = df.apply(
            lambda row: [str(row['Diet_Recommendation'])] if pd.notna(row.get('Diet_Recommendation')) else ['santé'],
            axis=1  # axis=1 = applique la fonction sur chaque ligne (pas chaque colonne)
        )
        result = result.dropna(subset=['email'])  # supprime les lignes sans email
        result = result.where(pd.notna(result), None)
        logger.info(f"Transformed {len(result)} utilisateurs from diet recommendations dataset")
        return result
    except Exception as e:
        logger.error(f"Error transforming diet recommendations to utilisateurs: {str(e)}")
        raise


def transform_foods_from_csv(df: pd.DataFrame) -> pd.DataFrame:
    """
    Fonction générique de transformation pour tout CSV alimentaire.
    Essaie de mapper les colonnes courantes vers le schéma 'aliments'.
    """
    try:
        result = pd.DataFrame()

        # Dictionnaire de mapping : noms de colonnes courants → noms attendus en base
        column_mapping = {
            'name': 'nom', 'food_name': 'nom', 'Food': 'nom',
            'calories': 'calories', 'Calories': 'calories',
            'protein': 'proteines', 'Protein': 'proteines', 'proteins': 'proteines',
            'carbohydrate': 'glucides', 'Carbohydrate': 'glucides', 'carbs': 'glucides',
            'fat': 'lipides', 'Fat': 'lipides', 'fats': 'lipides',
            'fiber': 'fibres', 'Fiber': 'fibres', 'fibers': 'fibres',
            'unit': 'unite', 'Unit': 'unite'
        }

        for old_col, new_col in column_mapping.items():  # essaie chaque correspondance possible
            if old_col in df.columns:
                result[new_col] = df[old_col]  # copie la colonne si elle existe dans le CSV

        # Valeurs par défaut pour les colonnes numériques absentes
        if 'calories' not in result.columns: result['calories'] = 0.0
        if 'proteines' not in result.columns: result['proteines'] = 0.0
        if 'glucides' not in result.columns: result['glucides'] = 0.0
        if 'lipides' not in result.columns: result['lipides'] = 0.0
        if 'fibres' not in result.columns: result['fibres'] = 0.0
        if 'unite' not in result.columns: result['unite'] = '100g'

        result['source'] = 'Kaggle Dataset'  # traçabilité

        result = result.where(pd.notna(result), None)  # remplace les NaN par None

        # Convertit les colonnes numériques en float et remplace les valeurs invalides par 0
        numeric_cols = ['calories', 'proteines', 'glucides', 'lipides', 'fibres']
        for col in numeric_cols:
            if col in result.columns:
                result[col] = pd.to_numeric(result[col], errors='coerce').fillna(0.0)

        logger.info(f"Transformed {len(result)} foods")
        return result

    except Exception as e:
        logger.error(f"Error transforming foods: {str(e)}")
        raise
