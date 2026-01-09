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
        # Remove duplicates
        df = df.drop_duplicates()
        
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

