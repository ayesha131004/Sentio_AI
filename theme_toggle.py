"""
theme_toggle.py
-----------------
Light/dark switch + matching Plotly settings.

  * app.py:           render_theme_toggle()  -> AFTER inject_theme()
  * results_page.py:  plot_layout()          -> used by its _style() helper

All CSS lives in theme.py (inject_theme reads st.session_state["theme"]).
"""

import streamlit as st


def current_theme() -> str:
    return st.session_state.get("theme", "dark")


def plot_layout() -> dict:
    """Plotly layout settings that match the current theme."""
    light = current_theme() == "light"
    base = dict(
        template="plotly_white" if light else "plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(
            family="JetBrains Mono, Inter, sans-serif",
            color="#0b1220" if light else "#e8e8f0",
        ),
    )
    if light:
        grid = "rgba(79,70,229,.10)"
        zero = "rgba(79,70,229,.20)"
        base["xaxis"] = dict(gridcolor=grid, zerolinecolor=zero)
        base["yaxis"] = dict(gridcolor=grid, zerolinecolor=zero)
    return base


def render_theme_toggle():
    """Shows a toggle at the top right. Changing it reruns the app, and
    inject_theme() (called earlier in app.py) picks up the new value."""
    st.session_state.setdefault("theme", "dark")

    def _on_change():
        st.session_state.theme = "light" if st.session_state["_theme_light"] else "dark"

    _, right = st.columns([6, 1.4])
    with right:
        st.toggle(
            "☀️ Light mode",
            value=current_theme() == "light",
            key="_theme_light",
            on_change=_on_change,
        )
