import requests
import os
from typing import Optional

class APIClient:
    """Client pour communiquer avec l'API FastAPI."""

    def __init__(self):
        # Utiliser localhost par défaut (pour lancement direct)
        # Pour Docker, définir API_URL=http://api:8000 dans .env
        self.base_url = os.getenv("API_URL", "http://localhost:8000")
        self.api_prefix = "/api/v1"

    def _url(self, endpoint: str) -> str:
        """Construit l'URL complète."""
        return f"{self.base_url}{self.api_prefix}{endpoint}"

    def get(self, endpoint: str, params: Optional[dict] = None) -> list | dict:
        """Requête GET."""
        response = requests.get(self._url(endpoint), params=params, timeout=10)
        response.raise_for_status()
        return response.json()

    def post(self, endpoint: str, data: dict) -> dict:
        """Requête POST."""
        response = requests.post(self._url(endpoint), json=data, timeout=10)
        response.raise_for_status()
        return response.json()

    def put(self, endpoint: str, data: dict) -> dict:
        """Requête PUT."""
        response = requests.put(self._url(endpoint), json=data, timeout=10)
        response.raise_for_status()
        return response.json()

    def delete(self, endpoint: str) -> dict:
        """Requête DELETE."""
        response = requests.delete(self._url(endpoint), timeout=10)
        response.raise_for_status()
        return response.json()


api_client = APIClient()
