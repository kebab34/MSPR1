import os
import threading
import requests
from typing import Any, Optional

_local = threading.local()


def set_api_token(token: Optional[str]) -> None:
    """Synchronise le JWT (Streamlit session + fallback thread-local)."""
    _local.token = token
    try:
        import streamlit as st
        if token:
            st.session_state["access_token"] = token
        else:
            for k in ("access_token", "user_profile"):
                st.session_state.pop(k, None)
    except Exception:
        pass


def get_api_token() -> Optional[str]:
    try:
        import streamlit as st
        t = st.session_state.get("access_token")
        if t:
            return t
    except Exception:
        pass
    return getattr(_local, "token", None)


def _auth_headers() -> dict[str, str]:
    t = get_api_token()
    if t:
        return {"Authorization": f"Bearer {t}"}
    return {}


class APIClient:
    """Client pour communiquer avec l'API FastAPI (JWT optionnel)."""

    @staticmethod
    def _raise_for_status(response: requests.Response) -> None:
        if response.ok:
            return
        try:
            body = response.json()
            detail = body.get("detail", response.text)
            if isinstance(detail, list):
                detail = "; ".join(str(x) for x in detail)
        except Exception:
            detail = response.text or response.reason
        raise requests.HTTPError(f"{response.status_code} — {detail}")

    def __init__(self):
        self.base_url = os.getenv("API_URL", "http://localhost:8000")
        self.api_prefix = "/api/v1"

    def _url(self, endpoint: str) -> str:
        return f"{self.base_url}{self.api_prefix}{endpoint}"

    def _merge_headers(self, extra: Optional[dict]) -> dict[str, str]:
        h: dict[str, str] = {}
        h.update(_auth_headers())
        if extra:
            h.update({k: v for k, v in extra.items() if v is not None})
        return h

    def get(
        self, endpoint: str, params: Optional[dict] = None, headers: Optional[dict] = None
    ) -> list | dict:
        response = requests.get(
            self._url(endpoint), params=params, timeout=10, headers=self._merge_headers(headers)
        )
        self._raise_for_status(response)
        return response.json()

    def post(
        self,
        endpoint: str,
        data: dict,
        headers: Optional[dict] = None,
        *,
        skip_auth: bool = False,
    ) -> dict:
        if skip_auth:
            h = {"Content-Type": "application/json"}
            if headers:
                h.update(headers)
        else:
            h = self._merge_headers(headers)
            h.setdefault("Content-Type", "application/json")
        response = requests.post(
            self._url(endpoint), json=data, timeout=10, headers=h
        )
        self._raise_for_status(response)
        return response.json()

    def put(
        self, endpoint: str, data: dict, headers: Optional[dict] = None
    ) -> dict:
        h = self._merge_headers(headers)
        h.setdefault("Content-Type", "application/json")
        response = requests.put(
            self._url(endpoint), json=data, timeout=10, headers=h
        )
        self._raise_for_status(response)
        return response.json()

    def patch(
        self, endpoint: str, data: dict, headers: Optional[dict] = None
    ) -> dict:
        h = self._merge_headers(headers)
        h.setdefault("Content-Type", "application/json")
        response = requests.patch(
            self._url(endpoint), json=data, timeout=10, headers=h
        )
        self._raise_for_status(response)
        return response.json()

    def delete(
        self, endpoint: str, headers: Optional[dict] = None
    ) -> Any:
        response = requests.delete(
            self._url(endpoint), timeout=10, headers=self._merge_headers(headers)
        )
        self._raise_for_status(response)
        if response.text:
            try:
                return response.json()
            except Exception:
                return response.text
        return None

    def login(self, email: str, password: str) -> dict:
        return self.post(
            "/auth/login",
            {"email": email, "password": password},
            skip_auth=True,
        )

    def register(
        self,
        email: str,
        password: str,
        nom: Optional[str] = None,
        prenom: Optional[str] = None,
    ) -> dict:
        """Crée un compte Supabase + ligne utilisateur (plan gratuit / freemium par défaut)."""
        payload: dict = {"email": email, "password": password}
        if nom:
            payload["nom"] = nom
        if prenom:
            payload["prenom"] = prenom
        return self.post("/auth/register", payload, skip_auth=True)

    def me(self) -> dict:
        return self.get("/auth/me")

    def update_me(self, data: dict) -> dict:
        """Met à jour le profil connecté (champs + freemium/premium)."""
        return self.patch("/auth/me", data)


api_client = APIClient()
