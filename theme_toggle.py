"""
theme_toggle.py
-----------------
Light/dark switch. Call render_theme_toggle() once near the top of app.py,
AFTER your existing theme CSS is injected, so these overrides apply on top.
"""

import streamlit as st

LIGHT_CSS = """
<style>
.stApp {
    --bg: #f6f7fb;
    --bg-elevated: #ffffff;
    --line: rgba(20, 20, 40, 0.12);
    --text: #14141f;
    --text-dim: #5f5f75;
    background: #f6f7fb !important;
}
[data-testid="stHeader"] { background: transparent !important; }

/* text */
[data-testid="stMarkdownContainer"] p,
[data-testid="stMarkdownContainer"] li,
[data-testid="stMarkdownContainer"] h1,
[data-testid="stMarkdownContainer"] h2,
[data-testid="stMarkdownContainer"] h3,
[data-testid="stMarkdownContainer"] h4,
[data-testid="stWidgetLabel"] *,
[data-testid="stMetric"] *,
[data-testid="stCaptionContainer"] * { color: #14141f !important; }
[data-testid="stCaptionContainer"] * { color: #5f5f75 !important; }

/* cards (st.container(border=True)) */
[data-testid="stVerticalBlockBorderWrapper"] {
    background: #ffffff !important;
    border-color: rgba(20, 20, 40, 0.12) !important;
}

/* inputs, selects, multiselect */
[data-baseweb="input"], [data-baseweb="base-input"],
[data-baseweb="select"] > div, textarea {
    background: #ffffff !important;
    color: #14141f !important;
}
[data-baseweb="input"] input, [data-baseweb="select"] input { color: #14141f !important; }
[data-baseweb="popover"] ul, [data-baseweb="menu"] {
    background: #ffffff !important;
    color: #14141f !important;
}

/* buttons */
.stButton button, .stDownloadButton button {
    background: #ffffff !important;
    color: #14141f !important;
    border: 1px solid rgba(20, 20, 40, 0.18) !important;
}

/* tabs */
button[data-baseweb="tab"] { color: #5f5f75 !important; }
button[data-baseweb="tab"][aria-selected="true"] { color: #14141f !important; }
</style>
"""


def current_theme() -> str:
    return st.session_state.get("theme", "dark")


def plot_layout() -> dict:
    """Plotly layout settings that match the current theme."""
    light = current_theme() == "light"
    return dict(
        template="plotly_white" if light else "plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, sans-serif", color="#14141f" if light else "#e8e8f0"),
    )


def render_theme_toggle():
    """Shows a toggle at the top right and applies the chosen theme."""
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

    if current_theme() == "light":
        st.markdown(LIGHT_CSS, unsafe_allow_html=True)
