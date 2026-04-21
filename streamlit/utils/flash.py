"""Messages après st.rerun() — st.success seul disparaît avant affichage."""

import streamlit as st

FLASH_KEY = "_mspr_flash"


def flash_success(message: str) -> None:
    st.session_state[FLASH_KEY] = ("success", message)


def flash_error(message: str) -> None:
    st.session_state[FLASH_KEY] = ("error", message)


def render_flash() -> None:
    if FLASH_KEY not in st.session_state:
        return
    level, message = st.session_state.pop(FLASH_KEY)
    if level == "success":
        st.success(message, icon="✅")
    else:
        st.error(message, icon="❌")
