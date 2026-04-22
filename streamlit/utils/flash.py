"""Messages après st.rerun() — st.success seul disparaît avant affichage."""

import streamlit as st

# Liste de (level, message) ; l’ancien nom _mspr_flash (tuple) est encore lu au rendu
FLASH_KEY = "_mspr_flashes"
_LEGACY_KEY = "_mspr_flash"


def _append(level: str, message: str) -> None:
    st.session_state.setdefault(FLASH_KEY, [])
    st.session_state[FLASH_KEY].append((level, message))


def flash_success(message: str) -> None:
    _append("success", message)


def flash_error(message: str) -> None:
    _append("error", message)


def flash_warning(message: str) -> None:
    _append("warning", message)


def render_flash() -> None:
    raw = st.session_state.pop(FLASH_KEY, None)
    if raw is None:
        raw = st.session_state.pop(_LEGACY_KEY, None)
    if not raw:
        return
    if isinstance(raw, list):
        items = raw
    elif isinstance(raw, tuple) and len(raw) == 2:
        items = [raw]
    else:
        return
    for level, message in items:
        if level == "success":
            st.success(message, icon="✅")
        elif level == "warning":
            st.warning(message, icon="⚠️")
        else:
            st.error(message, icon="❌")
