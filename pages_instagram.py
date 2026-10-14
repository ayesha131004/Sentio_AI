import os
import re
import time
import base64
import streamlit as st

# ----------------------------------------------------------------------
# Self-contained asset helpers (kept local to this file so app.py doesn't
# need to pass anything extra in — same assets/ folder as your main app)
# ----------------------------------------------------------------------
ASSETS_DIR = os.path.join(os.path.dirname(__file__), "assets")
VALID_EXTENSIONS = ["png", "jpg", "jpeg", "webp", "svg", "avif"]


def _find_asset(base_name: str):
    if not os.path.isdir(ASSETS_DIR):
        return None
    for ext in VALID_EXTENSIONS:
        candidate = os.path.join(ASSETS_DIR, f"{base_name}.{ext}")
        if os.path.exists(candidate):
            return candidate
    return None


def _image_to_data_uri(path: str) -> str:
    ext = os.path.splitext(path)[1].lstrip(".").lower()
    mime = "svg+xml" if ext == "svg" else ext
    with open(path, "rb") as f:
        encoded = base64.b64encode(f.read()).decode()
    return f"data:image/{mime};base64,{encoded}"


INSTAGRAM_URL_PATTERN = re.compile(
    r"^https?://(www\.)?instagram\.com/(reel|reels|p)/[A-Za-z0-9_\-]+/?(\?.*)?$",
    re.IGNORECASE,
)

# ----------------------------------------------------------------------
# STYLE — scoped to this page only
# ----------------------------------------------------------------------
st.markdown(
    """
    <style>
    .ig-card {
        position: relative;
        background: linear-gradient(135deg, #ff6fa5 0%, #f72585 45%, #c026a3 100%);
        border-radius: 22px;
        padding: 2.4rem 2.4rem 3.4rem;
        max-width: 640px;
        margin: 2rem auto 0;
        box-shadow: 0 25px 60px -20px rgba(247, 37, 133, 0.45);
    }

    .ig-card-logo {
        position: absolute;
        top: 1.6rem;
        left: 1.8rem;
        width: 38px;
        height: 38px;
        border-radius: 10px;
        object-fit: contain;
        background: rgba(255,255,255,0.15);
        padding: 5px;
    }

    .ig-card-title {
        text-align: center;
        color: white;
        font-family: 'Space Grotesk', sans-serif;
        font-size: 1.5rem;
        font-weight: 700;
        margin: 0.5rem 0 1.8rem;
    }

    .ig-sentio-logo {
        position: absolute;
        bottom: 1.2rem;
        right: 1.6rem;
        height: 26px;
        width: auto;
        opacity: 0.9;
    }

    /* Text input styled to sit on the pink card */
    .ig-card div[data-testid="stTextInput"] input {
        background: rgba(255,255,255,0.92) !important;
        border: none !important;
        border-radius: 10px !important;
        color: #2a0d1f !important;
        font-family: 'JetBrains Mono', monospace !important;
        font-size: 0.85rem !important;
        padding: 0.8rem 1rem !important;
    }

    .ig-card div[data-testid="stButton"] button {
        border-radius: 10px !important;
        font-family: 'JetBrains Mono', monospace !important;
        font-weight: 600 !important;
        border: none !important;
    }

    .ig-clear-btn button {
        background: rgba(255,255,255,0.25) !important;
        color: white !important;
    }

    .ig-analyze-btn button {
        background: #1a0a13 !important;
        color: white !important;
    }

    .ig-card .url-error {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.8rem;
        color: #fff3f6;
        background: rgba(0,0,0,0.22);
        border: 1px solid rgba(255,255,255,0.35);
        border-radius: 8px;
        padding: 0.7rem 1rem;
        margin-top: 0.9rem;
    }

    .ig-card .loading-line {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.85rem;
        color: white;
        margin-top: 1rem;
        display: flex;
        align-items: center;
        gap: 0.6rem;
    }

    .ig-mini-spinner {
        width: 13px;
        height: 13px;
        border-radius: 50%;
        border: 2px solid rgba(255,255,255,0.35);
        border-top-color: white;
        animation: ig-spin 0.8s linear infinite;
    }

    @keyframes ig-spin {
        to { transform: rotate(360deg); }
    }
    </style>
    """,
    unsafe_allow_html=True,
)


def render_instagram_input_page(ig_platform):
    """Renders the pink-gradient Instagram URL input card, per the sketch:
    Instagram logo top-left, URL field + clear (X) + Analyze inline,
    SentioAI logo bottom-right."""

    if st.button("← back to platforms", key="back_to_select"):
        st.session_state.page = "select"
        st.rerun()

    ig_logo = _find_asset("ig")
    sentio_logo = _find_asset("sentioai")

    st.markdown('<div class="ig-card">', unsafe_allow_html=True)

    if ig_logo:
        st.markdown(
            f'<img src="{_image_to_data_uri(ig_logo)}" class="ig-card-logo">',
            unsafe_allow_html=True,
        )

    st.markdown('<div class="ig-card-title">Analyze an Instagram Reel or Post</div>', unsafe_allow_html=True)

    if "ig_url_input" not in st.session_state:
        st.session_state.ig_url_input = ""

    col_input, col_clear, col_analyze = st.columns([3, 0.6, 1], gap="small")

    with col_input:
        url = st.text_input(
            "Instagram URL",
            placeholder="Fetch URL only of Insta",
            label_visibility="collapsed",
            key="ig_url_input",
        )

    with col_clear:
        st.markdown('<div class="ig-clear-btn">', unsafe_allow_html=True)
        if st.button("✕", key="ig_clear"):
            st.session_state.ig_url_input = ""
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    with col_analyze:
        st.markdown('<div class="ig-analyze-btn">', unsafe_allow_html=True)
        submit = st.button("Analyze", key="ig_submit")
        st.markdown('</div>', unsafe_allow_html=True)

    if submit:
        if not url.strip():
            st.markdown(
                '<div class="url-error">⚠ Please paste an Instagram link first.</div>',
                unsafe_allow_html=True,
            )
        elif not INSTAGRAM_URL_PATTERN.match(url.strip()):
            st.markdown(
                '<div class="url-error">⚠ Invalid URL input — this doesn\'t look like an '
                'Instagram Reel or Post link.</div>',
                unsafe_allow_html=True,
            )
        else:
            status = st.empty()
            for msg in ["analyzing....", "1 sec....", "almost ready...."]:
                status.markdown(
                    f'<div class="loading-line"><span class="ig-mini-spinner"></span> {msg}</div>',
                    unsafe_allow_html=True,
                )
                time.sleep(1)
            st.session_state.analysis_url = url.strip()
            st.session_state.page = "loading"
            st.rerun()

    if sentio_logo:
        st.markdown(
            f'<img src="{_image_to_data_uri(sentio_logo)}" class="ig-sentio-logo">',
            unsafe_allow_html=True,
        )

    st.markdown('</div>', unsafe_allow_html=True)
