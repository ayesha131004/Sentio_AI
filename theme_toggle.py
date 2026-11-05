"""
theme_toggle.py
-----------------
Light/dark switch with a "high-tech" light theme.

Usage:
  * app.py:           from theme_toggle import render_theme_toggle
                      render_theme_toggle()   # once, AFTER your theme.py CSS is injected
  * results_page.py:  from theme_toggle import plot_layout
                      PLOT_LAYOUT.update(plot_layout())   # first line in render_results_page
"""

import streamlit as st

LIGHT_CSS = """
<style>
.stApp {
    --bg: #f3f6fc;
    --bg-elevated: rgba(255, 255, 255, 0.82);
    --line: rgba(79, 70, 229, 0.18);
    --text: #0b1220;
    --text-dim: #51607a;
    --neon-cyan: #06b6d4;
    --neon-indigo: #4f46e5;
    --neon-violet: #7c3aed;

    /* blueprint grid + soft glows */
    background:
        radial-gradient(900px 500px at 8% -5%, rgba(6,182,212,.22), transparent 60%),
        radial-gradient(900px 600px at 95% 0%, rgba(124,58,237,.18), transparent 60%),
        radial-gradient(700px 500px at 50% 110%, rgba(79,70,229,.10), transparent 60%),
        linear-gradient(rgba(79,70,229,.07) 1px, transparent 1px),
        linear-gradient(90deg, rgba(79,70,229,.07) 1px, transparent 1px),
        #f3f6fc !important;
    background-size: auto, auto, auto, 38px 38px, 38px 38px, auto !important;
    background-attachment: fixed !important;
}
[data-testid="stHeader"] { background: transparent !important; }

/* glowing animated hairline across the top of the page */
.stApp::before {
    content: "";
    position: fixed; top: 0; left: 0; right: 0; height: 2px; z-index: 999;
    background: linear-gradient(90deg, transparent, #06b6d4, #4f46e5, #7c3aed, transparent);
    background-size: 200% 100%;
    animation: sentio-scan 6s linear infinite;
}
@keyframes sentio-scan { to { background-position: -200% 0; } }
@media (prefers-reduced-motion: reduce) { .stApp::before { animation: none; } }

/* ---------- TEXT: force readable colors, including custom HTML ---------- */
[data-testid="stMarkdownContainer"],
[data-testid="stMarkdownContainer"] p,
[data-testid="stMarkdownContainer"] li,
[data-testid="stMarkdownContainer"] h1,
[data-testid="stMarkdownContainer"] h2,
[data-testid="stMarkdownContainer"] h3,
[data-testid="stMarkdownContainer"] h4,
[data-testid="stMarkdownContainer"] div:not([style*="color"]),
[data-testid="stMarkdownContainer"] span:not([style*="color"]):not([style*="background"]),
[data-testid="stWidgetLabel"] *,
[data-testid="stMetric"] *,
label, .stApp h1, .stApp h2, .stApp h3 {
    color: #0b1220 !important;
    -webkit-text-fill-color: #0b1220 !important;
}
[data-testid="stCaptionContainer"] *,
.input-sub, .comment-meta {
    color: #51607a !important;
    -webkit-text-fill-color: #51607a !important;
}
[data-testid="stMarkdownContainer"] a { color: #4f46e5 !important; }

/* big titles get a subtle tech gradient */
.input-title, .hero-title, [data-testid="stMarkdownContainer"] h1 {
    background: linear-gradient(90deg, #0b1220 0%, #4f46e5 60%, #06b6d4 100%);
    -webkit-background-clip: text; background-clip: text;
    -webkit-text-fill-color: transparent !important;
    color: transparent !important;
}

/* mono "system label" look for widget labels */
[data-testid="stWidgetLabel"] p {
    font-family: 'JetBrains Mono', monospace !important;
    font-size: .72rem !important;
    letter-spacing: .08em; text-transform: uppercase;
    color: #51607a !important; -webkit-text-fill-color: #51607a !important;
}

/* ---------- CARDS / FORMS: glass panel with glowing top edge ---------- */
[data-testid="stVerticalBlockBorderWrapper"],
[data-testid="stForm"], .results-card {
    position: relative;
    background: rgba(255,255,255,.80) !important;
    backdrop-filter: blur(14px); -webkit-backdrop-filter: blur(14px);
    border: 1px solid rgba(79,70,229,.20) !important;
    border-radius: 16px !important;
    box-shadow:
        0 1px 0 rgba(255,255,255,.9) inset,
        0 10px 30px -12px rgba(79,70,229,.30),
        0 0 0 1px rgba(6,182,212,.06);
}
[data-testid="stForm"]::before,
[data-testid="stVerticalBlockBorderWrapper"]::before {
    content: ""; position: absolute; top: -1px; left: 14%; right: 14%; height: 2px;
    border-radius: 2px;
    background: linear-gradient(90deg, transparent, #06b6d4, #7c3aed, transparent);
    opacity: .8; pointer-events: none;
}
/* don't let nested bordered blocks stack glows */
[data-testid="stVerticalBlockBorderWrapper"] [data-testid="stVerticalBlockBorderWrapper"]::before { display: none; }

/* ---------- INPUTS ---------- */
[data-baseweb="input"], [data-baseweb="base-input"], [data-baseweb="select"] > div,
[data-baseweb="textarea"], textarea {
    background: #ffffff !important;
    border: 1px solid rgba(79,70,229,.25) !important;
    border-radius: 10px !important;
    transition: box-shadow .2s, border-color .2s;
}
[data-baseweb="input"] input, [data-baseweb="base-input"] input,
[data-baseweb="select"] input, textarea {
    background: transparent !important;
    color: #0b1220 !important; -webkit-text-fill-color: #0b1220 !important;
}
input::placeholder, textarea::placeholder {
    color: #8a96ad !important; -webkit-text-fill-color: #8a96ad !important;
}
[data-baseweb="input"]:focus-within, [data-baseweb="base-input"]:focus-within,
[data-baseweb="select"] > div:focus-within {
    border-color: #06b6d4 !important;
    box-shadow: 0 0 0 3px rgba(6,182,212,.20), 0 0 18px rgba(6,182,212,.25) !important;
}
[data-baseweb="input"] svg, [data-baseweb="select"] svg { fill: #51607a !important; }
[data-baseweb="popover"] ul, [data-baseweb="menu"], [data-baseweb="popover"] > div {
    background: #ffffff !important; color: #0b1220 !important;
    border: 1px solid rgba(79,70,229,.2) !important; border-radius: 12px !important;
}
[data-baseweb="menu"] li { color: #0b1220 !important; }
[data-baseweb="tag"] { background: rgba(79,70,229,.12) !important; }
[data-baseweb="tag"] span { color: #3730a3 !important; -webkit-text-fill-color: #3730a3 !important; }

/* ---------- BUTTONS ---------- */
.stButton button, .stDownloadButton button,
[data-testid="stFormSubmitButton"] button {
    background: #ffffff !important;
    color: #0b1220 !important; -webkit-text-fill-color: #0b1220 !important;
    border: 1px solid rgba(79,70,229,.30) !important;
    border-radius: 10px !important;
    font-family: 'JetBrains Mono', monospace !important;
    letter-spacing: .02em;
    transition: transform .15s, box-shadow .2s, border-color .2s;
}
.stButton button:hover, .stDownloadButton button:hover {
    border-color: #06b6d4 !important;
    box-shadow: 0 0 0 3px rgba(6,182,212,.15), 0 6px 18px -6px rgba(6,182,212,.5);
    transform: translateY(-1px);
}
/* primary actions (Log in, etc.) */
button[kind="primary"], button[kind="primaryFormSubmit"],
[data-testid="stFormSubmitButton"] button {
    background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 55%, #06b6d4 120%) !important;
    color: #ffffff !important; -webkit-text-fill-color: #ffffff !important;
    border: none !important;
    box-shadow: 0 8px 22px -8px rgba(79,70,229,.7), 0 0 20px rgba(6,182,212,.25);
}
button[kind="primary"]:hover, button[kind="primaryFormSubmit"]:hover,
[data-testid="stFormSubmitButton"] button:hover {
    box-shadow: 0 10px 28px -6px rgba(79,70,229,.85), 0 0 28px rgba(6,182,212,.45);
    transform: translateY(-1px);
}
button[kind="primary"] *, [data-testid="stFormSubmitButton"] button * {
    color: #ffffff !important; -webkit-text-fill-color: #ffffff !important;
}

/* ---------- METRICS, TABS, SLIDER, TABLES ---------- */
[data-testid="stMetricValue"] * {
    font-family: 'JetBrains Mono', monospace !important;
    font-weight: 700 !important;
}
button[data-baseweb="tab"] { color: #51607a !important; }
button[data-baseweb="tab"][aria-selected="true"] { color: #4f46e5 !important; }
[data-baseweb="tab-highlight"] { background: linear-gradient(90deg, #06b6d4, #7c3aed) !important; height: 3px !important; }
[data-baseweb="slider"] [role="slider"] {
    background: #4f46e5 !important;
    box-shadow: 0 0 0 4px rgba(79,70,229,.2), 0 0 14px rgba(6,182,212,.6);
}
[data-testid="stDataFrame"] { border: 1px solid rgba(79,70,229,.2); border-radius: 12px; overflow: hidden; }
[data-testid="stAlert"] { border-radius: 12px !important; }
hr { border-color: rgba(79,70,229,.18) !important; }
</style>
"""


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
