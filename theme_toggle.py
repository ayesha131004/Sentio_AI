
"""
theme_toggle.py
----------------
Responsive light/dark theme toggle.

Landing page:
    Compact toggle at the top-right.

Mobile:
    Remains right-aligned without unnecessary spacing.

Results:
    Plotly charts follow the selected theme.
"""

import streamlit as st


def current_theme() -> str:
    return st.session_state.get("theme", "dark")


def plot_layout() -> dict:
    """Plotly layout settings matching the current theme."""

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

        base["xaxis"] = dict(
            gridcolor=grid,
            zerolinecolor=zero,
        )

        base["yaxis"] = dict(
            gridcolor=grid,
            zerolinecolor=zero,
        )

    return base


_TOGGLE_CSS = """
<style>

/* =====================================================
   THEME TOGGLE POSITION
   ===================================================== */

.st-key-theme_toggle_wrap {
    display: flex !important;
    justify-content: flex-end !important;
    align-items: center !important;

    width: 100% !important;

    margin-top: 0 !important;
    margin-bottom: 0 !important;
    padding: 0 !important;
}

/* Keep the toggle label on one line */

.st-key-theme_toggle_wrap label {
    white-space: nowrap !important;
    margin: 0 !important;
    line-height: 1.2 !important;
}

/* Prevent toggle from stretching */

.st-key-theme_toggle_wrap div[data-testid="stToggle"] {
    width: auto !important;
    max-width: 100% !important;
}

/* Remove unnecessary vertical spacing */

.st-key-theme_toggle_wrap [data-testid="stWidgetLabel"] {
    margin-bottom: 0 !important;
}

/* Mobile */

@media screen and (max-width: 640px) {

    .st-key-theme_toggle_wrap {
        margin-top: 0 !important;
        margin-bottom: .2rem !important;
    }

    .st-key-theme_toggle_wrap label {
        font-size: .84rem !important;
    }

}

</style>
"""


def render_theme_toggle():
    """
    Render a compact right-aligned theme switch.

    Theme changes trigger a Streamlit rerun.
    inject_theme() then applies the selected theme.
    """

    st.session_state.setdefault("theme", "dark")

    def _on_change():

        st.session_state.theme = (
            "light"
            if st.session_state["_theme_light"]
            else "dark"
        )

    st.markdown(
        _TOGGLE_CSS,
        unsafe_allow_html=True,
    )

    # Equal columns provide sufficient room on mobile.
    left, right = st.columns(
        [1, 1],
        gap="small",
    )

    with right:

        with st.container(key="theme_toggle_wrap"):

            st.toggle(
                "☀️ Light mode",
                value=current_theme() == "light",
                key="_theme_light",
                on_change=_on_change,
            )
