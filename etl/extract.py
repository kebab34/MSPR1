"""
ETL - Extract Module
Extract data from various sources
"""
import pandas as pd
import os
from typing import Optional, List
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def extract_from_csv(file_path: str) -> pd.DataFrame:
    """
    Extract data from CSV file
    
    Args:
        file_path: Path to CSV file
        
    Returns:
        DataFrame with extracted data
    """
    try:
        df = pd.read_csv(file_path)
        logger.info(f"Extracted {len(df)} rows from {file_path}")
        return df
    except Exception as e:
        logger.error(f"Error extracting from CSV: {str(e)}")
        raise


def extract_from_excel(file_path: str, sheet_name: Optional[str] = None) -> pd.DataFrame:
    """
    Extract data from Excel file
    
    Args:
        file_path: Path to Excel file
        sheet_name: Name of the sheet to extract (optional)
        
    Returns:
        DataFrame with extracted data
    """
    try:
        df = pd.read_excel(file_path, sheet_name=sheet_name)
        logger.info(f"Extracted {len(df)} rows from {file_path}")
        return df
    except Exception as e:
        logger.error(f"Error extracting from Excel: {str(e)}")
        raise


def extract_from_api(api_url: str, params: Optional[dict] = None) -> pd.DataFrame:
    """
    Extract data from API endpoint
    
    Args:
        api_url: URL of the API endpoint
        params: Query parameters (optional)
        
    Returns:
        DataFrame with extracted data
    """
    try:
        import requests
        response = requests.get(api_url, params=params)
        response.raise_for_status()
        data = response.json()
        df = pd.DataFrame(data)
        logger.info(f"Extracted {len(df)} rows from API: {api_url}")
        return df
    except Exception as e:
        logger.error(f"Error extracting from API: {str(e)}")
        raise

