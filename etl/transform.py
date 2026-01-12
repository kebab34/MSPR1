"""
ETL - Transform Module
Transform and clean data
"""
import pandas as pd
import logging
from typing import Dict, List, Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean data: remove duplicates, handle missing values
    
    Args:
        df: Input DataFrame
        
    Returns:
        Cleaned DataFrame
    """
    try:
        # Convertir les listes en strings pour permettre drop_duplicates
        for col in df.columns:
            if df[col].dtype == 'object':
                # Vérifier si la colonne contient des listes
                if df[col].apply(lambda x: isinstance(x, list)).any():
                    df[col] = df[col].apply(lambda x: str(x) if isinstance(x, list) else x)
        
        # Remove duplicates (seulement sur les colonnes qui ne sont pas des listes)
        # Identifier les colonnes avec des types hashables
        hashable_cols = [col for col in df.columns if df[col].dtype != 'object' or not df[col].apply(lambda x: isinstance(x, (list, dict))).any()]
        
        if hashable_cols:
            df = df.drop_duplicates(subset=hashable_cols)
        else:
            # Si toutes les colonnes contiennent des listes, on ne fait pas de drop_duplicates
            logger.warning("All columns contain unhashable types, skipping drop_duplicates")
        
        # Remove rows with all NaN
        df = df.dropna(how='all')
        
        logger.info(f"Cleaned data: {len(df)} rows remaining")
        return df
    except Exception as e:
        logger.error(f"Error cleaning data: {str(e)}")
        raise


def normalize_columns(df: pd.DataFrame, column_mapping: Dict[str, str]) -> pd.DataFrame:
    """
    Normalize column names
    
    Args:
        df: Input DataFrame
        column_mapping: Dictionary mapping old names to new names
        
    Returns:
        DataFrame with normalized columns
    """
    try:
        df = df.rename(columns=column_mapping)
        logger.info(f"Normalized columns: {list(column_mapping.values())}")
        return df
    except Exception as e:
        logger.error(f"Error normalizing columns: {str(e)}")
        raise


def validate_data(df: pd.DataFrame, required_columns: List[str]) -> bool:
    """
    Validate that required columns exist
    
    Args:
        df: Input DataFrame
        required_columns: List of required column names
        
    Returns:
        True if validation passes, False otherwise
    """
    try:
        missing_columns = set(required_columns) - set(df.columns)
        if missing_columns:
            logger.error(f"Missing required columns: {missing_columns}")
            return False
        logger.info("Data validation passed")
        return True
    except Exception as e:
        logger.error(f"Error validating data: {str(e)}")
        return False


def transform_data(df: pd.DataFrame, transformations: Optional[Dict] = None) -> pd.DataFrame:
    """
    Apply transformations to data
    
    Args:
        df: Input DataFrame
        transformations: Dictionary of transformations to apply
        
    Returns:
        Transformed DataFrame
    """
    try:
        # Apply custom transformations here
        # Example: df['new_column'] = df['old_column'].apply(some_function)
        
        if transformations:
            for transformation in transformations:
                # Apply transformation logic
                pass
        
        logger.info(f"Transformed data: {len(df)} rows")
        return df
    except Exception as e:
        logger.error(f"Error transforming data: {str(e)}")
        raise


def transform_exercises_from_exercisedb(df: pd.DataFrame) -> pd.DataFrame:
    """
    Transform ExerciseDB API data to match our schema
    
    Args:
        df: DataFrame from ExerciseDB API
        
    Returns:
        Transformed DataFrame matching our exercices table schema
    """
    try:
        # Créer un nouveau DataFrame avec les colonnes mappées
        result = pd.DataFrame()
        
        # Mapper les colonnes existantes
        if 'name' in df.columns:
            result['nom'] = df['name']
        
        if 'type' in df.columns:
            result['type'] = df['type']
        elif 'bodyPart' in df.columns:
            # Utiliser bodyPart comme type si type n'existe pas
            result['type'] = df['bodyPart']
        
        if 'target' in df.columns:
            result['groupe_musculaire'] = df['target']
        elif 'muscle' in df.columns:
            result['groupe_musculaire'] = df['muscle']
        
        if 'difficulty' in df.columns:
            result['niveau'] = df['difficulty']
        
        if 'equipment' in df.columns:
            result['equipement'] = df['equipment']
        
        if 'instructions' in df.columns:
            # Instructions peut être une liste, on la convertit en string
            result['instructions'] = df['instructions'].apply(
                lambda x: ', '.join(x) if isinstance(x, list) else str(x) if x else None
            )
        
        # Ajouter la description
        if 'name' in df.columns:
            result['description'] = df['name'].apply(lambda x: f"Exercice: {x}")
        
        # Normaliser le type d'exercice (si la colonne existe)
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
            # Valeur par défaut si type n'existe pas
            result['type'] = 'autre'
        
        # Normaliser le niveau (si la colonne existe)
        if 'niveau' in result.columns:
            result['niveau'] = result['niveau'].astype(str).str.lower().replace({
                'beginner': 'debutant',
                'intermediate': 'intermediaire',
                'expert': 'avance',
                'advanced': 'avance'
            })
        else:
            # Valeur par défaut si niveau n'existe pas
            result['niveau'] = 'debutant'
        
        # Normaliser l'équipement (si la colonne existe)
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
            # Valeur par défaut si equipement n'existe pas
            result['equipement'] = 'aucun'
        
        # S'assurer que groupe_musculaire existe
        if 'groupe_musculaire' not in result.columns:
            result['groupe_musculaire'] = None
        
        # Ajouter la source
        result['source'] = 'ExerciseDB API'
        
        # Remplacer les valeurs NaN par None
        result = result.where(pd.notna(result), None)
        
        logger.info(f"Transformed {len(result)} exercises")
        return result
        
    except Exception as e:
        logger.error(f"Error transforming exercises: {str(e)}")
        raise


def transform_foods_from_csv(df: pd.DataFrame) -> pd.DataFrame:
    """
    Transform food/nutrition CSV data to match our schema
    
    Args:
        df: DataFrame from CSV file
        
    Returns:
        Transformed DataFrame matching our aliments table schema
    """
    try:
        # Mapping possible des colonnes CSV vers notre schéma
        # (à adapter selon le format du CSV)
        result = pd.DataFrame()
        
        # Colonnes possibles dans les datasets nutritionnels
        column_mapping = {
            'name': 'nom',
            'food_name': 'nom',
            'Food': 'nom',
            'calories': 'calories',
            'Calories': 'calories',
            'protein': 'proteines',
            'Protein': 'proteines',
            'proteins': 'proteines',
            'carbohydrate': 'glucides',
            'Carbohydrate': 'glucides',
            'carbs': 'glucides',
            'fat': 'lipides',
            'Fat': 'lipides',
            'fats': 'lipides',
            'fiber': 'fibres',
            'Fiber': 'fibres',
            'fibers': 'fibres',
            'unit': 'unite',
            'Unit': 'unite'
        }
        
        # Mapper les colonnes
        for old_col, new_col in column_mapping.items():
            if old_col in df.columns:
                result[new_col] = df[old_col]
        
        # Valeurs par défaut si manquantes
        if 'calories' not in result.columns:
            result['calories'] = 0.0
        if 'proteines' not in result.columns:
            result['proteines'] = 0.0
        if 'glucides' not in result.columns:
            result['glucides'] = 0.0
        if 'lipides' not in result.columns:
            result['lipides'] = 0.0
        if 'fibres' not in result.columns:
            result['fibres'] = 0.0
        if 'unite' not in result.columns:
            result['unite'] = '100g'
        
        # Ajouter la source
        result['source'] = 'Kaggle Dataset'
        
        # Remplacer les valeurs NaN
        result = result.where(pd.notna(result), None)
        
        # S'assurer que les valeurs numériques sont des floats
        numeric_cols = ['calories', 'proteines', 'glucides', 'lipides', 'fibres']
        for col in numeric_cols:
            if col in result.columns:
                result[col] = pd.to_numeric(result[col], errors='coerce').fillna(0.0)
        
        logger.info(f"Transformed {len(result)} foods")
        return result
        
    except Exception as e:
        logger.error(f"Error transforming foods: {str(e)}")
        raise

