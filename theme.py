
"""
theme.py
---------
Single source of truth for SentioAI's visual design.

Features:
- High-tech dark and light themes
- Responsive mobile, tablet, laptop and desktop layouts
- Shared asset and logo helpers
- SVG icon library
- Reusable Streamlit helpers
- Responsive dashboard, forms and platform cards

Call inject_theme() once at the top of every run in app.py.
"""

import base64
import os

import streamlit as st


# ==========================================================
# CONFIGURATION
# ==========================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(BASE_DIR, "assets")

SEARCH_DIRS = [ASSETS_DIR, BASE_DIR]

VALID_EXTENSIONS = [
    "png",
    "jpg",
    "jpeg",
    "webp",
    "svg",
    "avif",
]

MIME_TYPES = {
    "png": "image/png",
    "jpg": "image/jpeg",
    "jpeg": "image/jpeg",
    "webp": "image/webp",
    "svg": "image/svg+xml",
    "avif": "image/avif",
}


# ==========================================================
# ASSET + HTML HELPERS
# ==========================================================

def find_asset(base_name: str):
    """Find an asset inside assets/ or the project directory."""

    for folder in SEARCH_DIRS:
        if not os.path.isdir(folder):
            continue

        for ext in VALID_EXTENSIONS:
            candidate = os.path.join(
                folder,
                f"{base_name}.{ext}"
            )

            if os.path.exists(candidate):
                return candidate

    return None


def image_to_data_uri(path: str) -> str:
    """Convert an image file into a base64 data URI."""

    ext = os.path.splitext(path)[1].lstrip(".").lower()
    mime = MIME_TYPES.get(ext, "image/png")

    with open(path, "rb") as file:
        encoded = base64.b64encode(
            file.read()
        ).decode("utf-8")

    return f"data:{mime};base64,{encoded}"


def md(html: str):
    """
    Render raw HTML through Streamlit Markdown.

    Removes indentation that could otherwise turn HTML into
    a Markdown code block.
    """

    flat = " ".join(
        line.strip()
        for line in html.splitlines()
        if line.strip()
    )

    st.markdown(flat, unsafe_allow_html=True)


def columns(spec, **kwargs):
    """Streamlit columns with compatibility for older versions."""

    try:
        return st.columns(
            spec,
            vertical_alignment="center",
            **kwargs
        )

    except TypeError:
        return st.columns(spec, **kwargs)


def keyed_container(key: str):
    """
    Create a container with a stable CSS key.

    Streamlit 1.39+ supports container keys.
    Older versions fall back to a regular container.
    """

    try:
        return st.container(key=key)

    except TypeError:
        return st.container()


# ==========================================================
# SVG ICONS
# ==========================================================

_ICON_PATHS = {
    "lock": (
        '<rect x="4" y="11" width="16" height="10" rx="2"/>'
        '<path d="M8 11V7a4 4 0 0 1 8 0v4"/>'
    ),

    "infinity": (
        '<path d="M6 8c-2.2 0-4 1.8-4 4s1.8 4 '
        '4 4c4 0 6-8 12-8 2.2 0 4 1.8 4 4s-1.8 4-4 4'
        'c-6 0-8-8-12-8z" transform="translate(-1 0)"/>'
    ),

    "grid": (
        '<rect x="3" y="3" width="7" height="7" rx="1.5"/>'
        '<rect x="14" y="3" width="7" height="7" rx="1.5"/>'
        '<rect x="3" y="14" width="7" height="7" rx="1.5"/>'
        '<rect x="14" y="14" width="7" height="7" rx="1.5"/>'
    ),

    "bolt": '<path d="M13 2 4 14h7l-1 8 9-12h-7z"/>',

    "chart": '<path d="M4 20V10M10 20V4M16 20v-7M22 20H2"/>',

    "chat": (
        '<path d="M21 12a8 8 0 0 1-11.6 7.1L4 20l1-4.6'
        'A8 8 0 1 1 21 12z"/>'
    ),

    "back": '<path d="M19 12H5M11 6l-6 6 6 6"/>',

    "link": (
        '<path d="M10 14a4 4 0 0 0 5.7 0l3-3'
        'a4 4 0 0 0-5.7-5.7l-1 1"/>'
        '<path d="M14 10a4 4 0 0 0-5.7 0l-3 3'
        'a4 4 0 0 0 5.7 5.7l1-1"/>'
    ),

    "shield": (
        '<path d="M12 3 4 6v6c0 5 3.4 8 8 9'
        ' 4.6-1 8-4 8-9V6z"/>'
        '<path d="m9 12 2 2 4-4"/>'
    ),

    "globe": (
        '<circle cx="12" cy="12" r="9"/>'
        '<path d="M3 12h18M12 3c2.5 2.7 3.8 5.7 '
        '3.8 9s-1.3 6.3-3.8 9c-2.5-2.7-3.8-5.7-3.8-9'
        'S9.5 5.7 12 3z"/>'
    ),

    "pulse": '<path d="M3 12h4l2-6 4 12 2-6h6"/>',

    "layers": (
        '<path d="m12 3 9 5-9 5-9-5z"/>'
        '<path d="m3 13 9 5 9-5"/>'
    ),

    "check": '<path d="m5 12 5 5 9-10"/>',

    "x": '<path d="M6 6l12 12M18 6 6 18"/>',

    "download": (
        '<path d="M12 4v11M7 11l5 5 5-5M5 20h14"/>'
    ),

    "star": (
        '<path d="M12 3l2.2 5.8L20 11l-5.8 2.2'
        'L12 19l-2.2-5.8L4 11l5.8-2.2z"/>'
    ),
}


def icon(name: str, size: int = 18) -> str:
    """Return an inline SVG icon."""

    body = _ICON_PATHS.get(name, "")

    return (
        f'<svg class="ico" width="{size}" height="{size}" '
        f'viewBox="0 0 24 24" fill="none" '
        f'stroke="currentColor" stroke-width="1.8" '
        f'stroke-linecap="round" stroke-linejoin="round" '
        f'aria-hidden="true">{body}</svg>'
    )


# ==========================================================
# BRAND MARK
# ==========================================================

def brand_lockup(size: int = 44, show_word: bool = True) -> str:
    """
    Create the SentioAI logo and wordmark.

    Uses sentioai.png if available.
    Otherwise displays a gradient S fallback.
    """

    logo = find_asset("sentioai")

    if logo:
        uri = image_to_data_uri(logo)
        s = size * 1.9

        mark = (
            f'<span class="brand-mark" '
            f'style="width:{size}px;height:{size}px;'
            f'background-image:url({uri});'
            f'background-size:{s:.0f}px {s:.0f}px;'
            f'background-position:'
            f'{-(s * 0.5 - size / 2):.0f}px '
            f'{-(s * 0.40 - size / 2):.0f}px;"></span>'
        )

    else:
        mark = (
            f'<span class="brand-mark fallback" '
            f'style="width:{size}px;height:{size}px;">S</span>'
        )

    word = (
        '<span class="brand-word">Sentio<b>AI</b></span>'
        if show_word
        else ""
    )

    return f'<span class="brand">{mark}{word}</span>'


# ==========================================================
# DARK THEME + BASE CSS
# ==========================================================

THEME_CSS = r"""
<style>

@import url('https://fonts.googleapis.com/css2?family=Sora:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap');


/* ==========================================================
   DESIGN TOKENS
   ========================================================== */

:root {
    --bg: #050816;
    --bg-elevated: #0b1127;
    --bg-glass: rgba(14, 20, 46, 0.62);

    --line: rgba(130, 150, 255, 0.16);
    --line-strong: rgba(130, 150, 255, 0.32);

    --text: #eaf0ff;
    --text-dim: #8c97bd;
    --text-faint: #5d678a;

    --track: rgba(255, 255, 255, 0.07);
    --logo-bg: #050816;

    --negative: #ff5d7e;
    --neutral: #8b9bff;
    --positive: #2fe0a5;

    --blue: #3b82f6;
    --violet: #8b5cf6;
    --cyan: #22d3ee;

    --brand-grad: linear-gradient(
        135deg,
        #3b82f6 0%,
        #6d5cf6 55%,
        #9b5cf6 100%
    );

    --warn: #f5b94d;

    --radius-lg: 18px;
    --radius-md: 12px;
    --radius-sm: 8px;

    --font: 'Sora', system-ui, -apple-system, 'Segoe UI', sans-serif;
    --mono: 'JetBrains Mono', ui-monospace, 'SFMono-Regular', Menlo, monospace;
}


/* ==========================================================
   BASE
   ========================================================== */

html,
body,
.stApp,
.stApp p,
.stApp label,
.stApp li,
.stApp button,
.stApp input,
.stApp textarea,
.stApp h1,
.stApp h2,
.stApp h3 {
    font-family: var(--font) !important;
}

html,
body,
.stApp,
[data-testid="stAppViewContainer"] {
    width: 100%;
    max-width: 100%;
    overflow-x: hidden;
}

* {
    box-sizing: border-box;
}

.stApp {
    color: var(--text);
    background: var(--bg);
}

#MainMenu,
footer,
header,
[data-testid="stToolbar"],
[data-testid="stDecoration"] {
    display: none !important;
}

.stApp::before {
    content: "";
    position: fixed;
    inset: 0;
    z-index: 0;
    pointer-events: none;

    background:
        radial-gradient(
            ellipse 800px 480px at 82% -6%,
            rgba(139, 92, 246, 0.22),
            transparent 62%
        ),
        radial-gradient(
            ellipse 760px 460px at 8% 2%,
            rgba(34, 211, 238, 0.13),
            transparent 60%
        ),
        linear-gradient(
            rgba(130,150,255,0.055) 1px,
            transparent 1px
        ),
        linear-gradient(
            90deg,
            rgba(130,150,255,0.055) 1px,
            transparent 1px
        );

    background-size:
        auto,
        auto,
        56px 56px,
        56px 56px;

    -webkit-mask-image: radial-gradient(
        ellipse 120% 90% at 50% 0%,
        #000 35%,
        transparent 85%
    );

    mask-image: radial-gradient(
        ellipse 120% 90% at 50% 0%,
        #000 35%,
        transparent 85%
    );
}

.block-container {
    position: relative;
    z-index: 1;
    width: 100%;
    max-width: 1240px;
    padding: 1.2rem 2rem 3rem;
}

div[data-testid="stElementContainer"]:has(style) {
    display: none;
}

.ico {
    flex-shrink: 0;
    vertical-align: middle;
}

div[data-testid="stToggle"] p {
    font-size: 0.8rem;
    color: var(--text-dim);
}


/* ==========================================================
   BRAND
   ========================================================== */

.brand {
    display: inline-flex;
    align-items: center;
    gap: 0.65rem;
}

.brand-mark {
    display: inline-block;
    flex-shrink: 0;
    background-color: var(--logo-bg);
    background-blend-mode: lighten;
    background-repeat: no-repeat;
    border-radius: 12px;
}

.brand-mark.fallback {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    background: var(--brand-grad);
    color: #fff;
    font-weight: 700;
}

.brand-word {
    font-size: 1.28rem;
    font-weight: 600;
    letter-spacing: -0.02em;
    color: #fff;
}

.brand-word b {
    font-weight: 700;
    background: linear-gradient(135deg, #4f9bff, #9b5cf6);
    -webkit-background-clip: text;
    background-clip: text;
    color: transparent;
}


/* ==========================================================
   NAVIGATION
   ========================================================== */

.st-key-topnav {
    border-bottom: 1px solid var(--line);
    padding-bottom: 0.9rem;
    margin-bottom: 2.4rem;
}

.nav-meta {
    display: flex;
    justify-content: flex-end;
    align-items: center;
    gap: 0.5rem;
    flex-wrap: wrap;
}

.nav-user {
    font-size: 0.8rem;
    color: var(--text-dim);
    margin-right: 0.3rem;
}

.nav-user b {
    color: var(--text);
    font-weight: 500;
}


/* ==========================================================
   CHIPS
   ========================================================== */

.chip {
    display: inline-flex;
    align-items: center;
    gap: 0.35rem;

    font-family: var(--mono) !important;
    font-size: 0.7rem;
    font-weight: 500;

    padding: 0.22rem 0.6rem;
    border-radius: 999px;

    white-space: nowrap;

    color: var(--text-dim);
    border: 1px solid var(--line);
    background: rgba(255,255,255,0.03);
}

.chip.accent {
    color: var(--accent, var(--cyan));
    border-color: color-mix(
        in srgb,
        var(--accent, var(--cyan)) 45%,
        transparent
    );
    background: color-mix(
        in srgb,
        var(--accent, var(--cyan)) 10%,
        transparent
    );
}

.chip.pro {
    color: #fff;
    border-color: transparent;
    background: var(--brand-grad);
    font-weight: 600;
}

.chip.low,
.chip.locked {
    color: var(--warn);
    border-color: rgba(245,185,77,0.4);
    background: rgba(245,185,77,0.08);
}

.chip.empty {
    color: var(--negative);
    border-color: rgba(255,93,126,0.4);
    background: rgba(255,93,126,0.08);
}

.chip.ok {
    color: var(--positive);
    border-color: rgba(47,224,165,0.4);
    background: rgba(47,224,165,0.08);
}

.dot {
    width: 6px;
    height: 6px;
    border-radius: 50%;
    background: currentColor;
    box-shadow: 0 0 8px currentColor;
}


/* ==========================================================
   BUTTONS
   ========================================================== */

.stButton > button,
div[data-testid="stFormSubmitButton"] > button {
    width: 100%;
    min-height: 2.7rem;
    padding: 0.55rem 1.1rem;

    white-space: nowrap;
    line-height: 1.2;

    font-family: var(--font) !important;
    font-size: 0.85rem;
    font-weight: 500;

    color: var(--text);
    background: rgba(255,255,255,0.04);

    border: 1px solid var(--line-strong);
    border-radius: var(--radius-md);

    transition:
        border-color .18s ease,
        background .18s ease,
        box-shadow .18s ease,
        transform .18s ease;
}

.stButton > button:hover,
div[data-testid="stFormSubmitButton"] > button:hover {
    color: #fff;
    border-color: var(--cyan);
    background: rgba(34,211,238,0.07);

    box-shadow:
        0 0 0 1px rgba(34,211,238,0.35),
        0 8px 24px -10px rgba(34,211,238,0.5);
}

.stButton > button:focus-visible,
div[data-testid="stFormSubmitButton"] > button:focus-visible {
    outline: 2px solid var(--cyan);
    outline-offset: 2px;
}

.stButton > button:active {
    transform: translateY(1px);
}

.stButton > button[kind="primary"],
div[data-testid="stFormSubmitButton"] > button[kind="primaryFormSubmit"],
.stButton > button[data-testid="stBaseButton-primary"],
div[data-testid="stFormSubmitButton"] > button[data-testid="stBaseButton-primaryFormSubmit"] {
    color: #fff;
    border: none;
    background: var(--brand-grad);
    font-weight: 600;

    box-shadow: 0 10px 28px -12px rgba(99, 102, 241, 0.9);
}

.stButton > button[kind="primary"]:hover,
div[data-testid="stFormSubmitButton"] > button[kind="primaryFormSubmit"]:hover,
.stButton > button[data-testid="stBaseButton-primary"]:hover,
div[data-testid="stFormSubmitButton"] > button[data-testid="stBaseButton-primaryFormSubmit"]:hover {
    color: #fff;
    filter: brightness(1.12);
    background: var(--brand-grad);
    box-shadow: 0 14px 34px -12px rgba(99, 102, 241, 1);
}

div[data-testid="stFormSubmitButton"] {
    width: 100%;
}

.st-key-topnav .stButton > button {
    min-height: 2.3rem;
    font-size: 0.78rem;
    padding: 0.4rem 0.9rem;
}

.st-key-back_to_select .stButton > button,
.st-key-goto_signup .stButton > button,
.st-key-goto_login .stButton > button {
    width: auto;
    min-height: 2.2rem;
    padding: 0.3rem 0.8rem 0.3rem 0.6rem;

    background: transparent;
    border-color: transparent;
    color: var(--text-dim);
}

.st-key-back_to_select .stButton > button:hover,
.st-key-goto_signup .stButton > button:hover,
.st-key-goto_login .stButton > button:hover {
    color: #fff;
    background: rgba(255,255,255,0.05);
    border-color: var(--line);
    box-shadow: none;
}


/* ==========================================================
   INPUTS
   ========================================================== */

div[data-baseweb="input"],
div[data-baseweb="base-input"] {
    background: rgba(5, 8, 22, 0.7) !important;
    border: 1px solid var(--line-strong) !important;
    border-radius: var(--radius-md) !important;

    transition:
        border-color .18s ease,
        box-shadow .18s ease;
}

div[data-baseweb="input"]:focus-within {
    border-color: var(--blue) !important;
    box-shadow: 0 0 0 3px rgba(59,130,246,0.22) !important;
}

div[data-baseweb="input"] input,
div[data-baseweb="base-input"] input {
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;

    color: var(--text) !important;

    font-family: var(--mono) !important;
    font-size: 0.86rem !important;

    padding: 0.8rem 1rem !important;
    height: 2.9rem;
}

div[data-baseweb="input"] input::placeholder {
    color: var(--text-faint) !important;
}

div[data-baseweb="input"] button {
    color: var(--text-dim);
}

div[data-testid="InputInstructions"] {
    display: none;
}

div[data-testid="stTextInput"] label p {
    font-size: 0.8rem;
    color: var(--text-dim);
    font-weight: 500;
}


/* ==========================================================
   FORMS
   ========================================================== */

div[data-testid="stForm"] {
    border: 1px solid var(--line);
    border-radius: var(--radius-lg);

    background: var(--bg-glass);

    -webkit-backdrop-filter: blur(14px);
    backdrop-filter: blur(14px);

    padding: 1.6rem 1.5rem 1.3rem;

    box-shadow: 0 30px 70px -40px rgba(99,102,241,0.55);
}


/* ==========================================================
   ALERTS
   ========================================================== */

.url-error {
    display: flex;
    align-items: flex-start;
    gap: 0.6rem;

    font-size: 0.84rem;
    line-height: 1.5;

    color: #ffb3c2;

    border: 1px solid rgba(255,93,126,0.38);
    background: rgba(255,93,126,0.08);

    border-radius: var(--radius-md);
    padding: 0.75rem 1rem;
    margin-top: 0.9rem;
}

.url-error .ico {
    color: var(--negative);
    margin-top: 2px;
}

div[data-testid="stAlert"] {
    border-radius: var(--radius-md);
}


/* ==========================================================
   LANDING PAGE — HERO
   ========================================================== */

.hero-title {
    font-size: clamp(2.3rem, 4.6vw, 3.6rem);
    font-weight: 700;
    line-height: 1.06;
    letter-spacing: -0.035em;

    color: #fff;

    margin: 0.9rem 0 1.1rem;
}

.hero-sub {
    font-size: 1.02rem;
    line-height: 1.7;
    color: var(--text-dim);

    max-width: 31rem;
    margin: 0 0 1.8rem;
}

.spectrum {
    max-width: 31rem;
}

.spectrum-bar {
    position: relative;
    height: 6px;
    border-radius: 6px;

    background: linear-gradient(
        90deg,
        var(--negative),
        var(--neutral) 50%,
        var(--positive)
    );

    box-shadow: 0 0 22px -4px rgba(139,155,255,0.55);
}

.spectrum-bar::after {
    content: "";
    position: absolute;

    top: 50%;
    left: 68%;

    width: 14px;
    height: 14px;

    transform: translate(-50%, -50%);

    border-radius: 50%;

    background: #fff;
    border: 3px solid var(--bg);

    box-shadow:
        0 0 0 1px var(--line-strong),
        0 0 14px rgba(47,224,165,0.8);
}

.spectrum-labels {
    display: flex;
    justify-content: space-between;

    margin-top: 0.6rem;

    font-family: var(--mono) !important;
    font-size: 0.7rem;
    color: var(--text-dim);
}


/* ==========================================================
   LANDING PAGE — PREVIEW
   ========================================================== */

.preview {
    border: 1px solid var(--line-strong);
    border-radius: 20px;

    padding: 1.3rem 1.4rem 1.4rem;

    background: linear-gradient(
        160deg,
        rgba(20,28,64,0.78),
        rgba(8,12,30,0.78)
    );

    -webkit-backdrop-filter: blur(16px);
    backdrop-filter: blur(16px);

    box-shadow:
        0 40px 90px -40px rgba(99,102,241,0.7),
        inset 0 1px 0 rgba(255,255,255,0.06);
}

.preview-head {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 1.1rem;
}

.preview-title {
    display: flex;
    align-items: center;
    gap: 0.5rem;

    font-size: 0.86rem;
    font-weight: 600;
    color: var(--text);
}

.preview-title .ico {
    color: var(--cyan);
}

.preview-body {
    display: flex;
    align-items: center;
    gap: 1.6rem;
}

.preview-rows {
    flex: 1;
    display: grid;
    gap: 0.85rem;
}

.prow-top {
    display: flex;
    justify-content: space-between;

    font-size: 0.8rem;
    margin-bottom: 0.35rem;

    color: var(--text);
}

.prow-top span:last-child {
    font-family: var(--mono) !important;
    color: var(--text-dim);
}

.track {
    height: 6px;
    border-radius: 4px;
    background: var(--track);
    overflow: hidden;
}

.fill {
    height: 100%;
    border-radius: 4px;
}

.preview-foot {
    margin-top: 1.2rem;
    padding-top: 1rem;

    border-top: 1px solid var(--line);

    display: flex;
    justify-content: space-between;

    font-size: 0.74rem;
    color: var(--text-dim);
}

.preview-foot b {
    color: var(--positive);
    font-weight: 600;
}


/* ==========================================================
   PLATFORM CARDS
   ========================================================== */

.section-head {
    display: flex;
    align-items: baseline;
    justify-content: space-between;

    gap: 1rem;

    margin: 3.2rem 0 1.2rem;
}

.section-title {
    font-size: 1.3rem;
    font-weight: 600;
    letter-spacing: -0.02em;
    color: #fff;
}

.section-note {
    font-size: 0.84rem;
    color: var(--text-dim);
}

[class*="st-key-card_"] {
    --accent: #6d5cf6;

    position: relative;
    overflow: hidden;

    background: linear-gradient(
        180deg,
        rgba(18,26,58,0.72),
        rgba(9,14,34,0.72)
    );

    border: 1px solid var(--line);
    border-radius: var(--radius-lg);

    padding: 1.3rem 1.25rem 1.25rem;

    transition:
        border-color .22s ease,
        box-shadow .22s ease,
        transform .22s ease;
}

[class*="st-key-card_"]::before {
    content: "";

    position: absolute;
    left: 0;
    right: 0;
    top: 0;

    height: 2px;

    background: linear-gradient(
        90deg,
        transparent,
        var(--accent),
        transparent
    );

    opacity: 0.85;
}

[class*="st-key-card_"]:hover {
    transform: translateY(-3px);

    border-color: color-mix(
        in srgb,
        var(--accent) 55%,
        transparent
    );

    box-shadow: 0 22px 44px -26px var(--accent);
}

[class*="st-key-card_"] .stButton > button {
    margin-top: 0.2rem;
}

[class*="st-key-card_"] .stButton > button:hover {
    border-color: var(--accent);

    background: color-mix(
        in srgb,
        var(--accent) 12%,
        transparent
    );

    box-shadow: 0 0 0 1px color-mix(
        in srgb,
        var(--accent) 40%,
        transparent
    );
}

.pc-top {
    display: flex;
    align-items: center;
    justify-content: space-between;

    margin-bottom: 1.1rem;
    min-height: 44px;
}

.pc-icon {
    width: 44px;
    height: 44px;

    border-radius: 12px;

    display: flex;
    align-items: center;
    justify-content: center;

    background: rgba(255,255,255,0.05);
    border: 1px solid var(--line);
}

.pc-icon img {
    width: 24px;
    height: 24px;
    object-fit: contain;
}

.pc-icon span {
    color: var(--accent);
    font-size: 1.2rem;
}

.pc-name {
    font-size: 1.08rem;
    font-weight: 600;
    color: #fff;

    margin-bottom: 0.4rem;
    letter-spacing: -0.01em;
}

.pc-desc {
    font-size: 0.84rem;
    line-height: 1.55;
    color: var(--text-dim);
    min-height: 4.7rem;
}

.pc-tag {
    font-family: var(--mono) !important;
    font-size: 0.72rem;
    color: var(--accent);
    margin-bottom: 0.9rem;
}


/* ==========================================================
   FOOTER
   ========================================================== */

.footer-bar {
    margin-top: 3.4rem;
    padding-top: 1.1rem;

    border-top: 1px solid var(--line);

    display: flex;
    justify-content: space-between;
    align-items: center;

    gap: 1rem;
    flex-wrap: wrap;

    font-size: 0.78rem;
    color: var(--text-dim);
}

.footer-bar .status {
    display: inline-flex;
    align-items: center;
    gap: 0.55rem;
}

.footer-bar .status .dot {
    color: var(--positive);
    animation: pulse 2.4s infinite;
}

.footer-bar .models {
    font-family: var(--mono) !important;
    font-size: 0.72rem;
    color: var(--text-faint);
}

@keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: .45; }
}


/* ==========================================================
   AUTHENTICATION
   ========================================================== */

.auth-side {
    padding: 1.5rem 1rem 0 0;
}

.auth-title {
    font-size: clamp(2rem, 3.6vw, 2.9rem);
    font-weight: 700;
    letter-spacing: -0.035em;
    line-height: 1.08;

    color: #fff;

    margin: 2.6rem 0 1rem;
}

.auth-sub {
    font-size: 1rem;
    line-height: 1.7;
    color: var(--text-dim);

    max-width: 28rem;
    margin-bottom: 2rem;
}

.feat {
    display: flex;
    gap: 0.9rem;
    align-items: flex-start;

    padding: 0.85rem 0;

    border-top: 1px solid var(--line);
    max-width: 28rem;
}

.feat:last-child {
    border-bottom: 1px solid var(--line);
}

.feat-ico {
    width: 34px;
    height: 34px;

    border-radius: 10px;
    flex-shrink: 0;

    display: flex;
    align-items: center;
    justify-content: center;

    color: var(--cyan);

    background: rgba(34,211,238,0.09);
    border: 1px solid rgba(34,211,238,0.22);
}

.feat-title {
    font-size: 0.92rem;
    font-weight: 600;
    color: var(--text);
}

.feat-desc {
    font-size: 0.8rem;
    color: var(--text-dim);
    margin-top: 2px;
    line-height: 1.5;
}

.auth-form-head {
    margin-bottom: 1.1rem;
}

.auth-form-title {
    font-size: 1.4rem;
    font-weight: 600;
    letter-spacing: -0.02em;
    color: #fff;
}

.auth-form-sub {
    font-size: 0.86rem;
    color: var(--text-dim);
    margin-top: 0.3rem;
}

.auth-switch {
    font-size: 0.84rem;
    color: var(--text-dim);
    margin: 1.3rem 0 0.2rem;
}


/* ==========================================================
   LINK INPUT PAGE
   ========================================================== */

.st-key-inputcard {
    width: 100%;
    max-width: 820px;

    margin: 0.6rem auto 0;

    border: 1px solid var(--line-strong);
    border-radius: 22px;

    padding: 2rem 2rem 1.6rem;

    background: linear-gradient(
        160deg,
        rgba(20,28,64,0.72),
        rgba(8,12,30,0.72)
    );

    -webkit-backdrop-filter: blur(16px);
    backdrop-filter: blur(16px);

    box-shadow: 0 40px 90px -45px var(--accent, #6d5cf6);

    position: relative;
    overflow: hidden;
}

.st-key-inputcard::before {
    content: "";

    position: absolute;
    left: 0;
    right: 0;
    top: 0;

    height: 2px;

    background: linear-gradient(
        90deg,
        transparent,
        var(--accent, #6d5cf6),
        transparent
    );
}

.ic-head {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 1.6rem;
}

.ic-platform {
    display: flex;
    align-items: center;
    gap: 0.8rem;

    font-size: 0.95rem;
    font-weight: 600;
    color: var(--text);
}

.ic-title {
    font-size: clamp(1.7rem, 3vw, 2.3rem);
    font-weight: 700;
    letter-spacing: -0.03em;
    color: #fff;
    margin-bottom: 0.6rem;
}

.ic-sub {
    font-size: 0.95rem;
    line-height: 1.65;
    color: var(--text-dim);

    max-width: 36rem;
    margin-bottom: 1.6rem;
}

.ic-formats {
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    gap: 0.5rem;

    margin-top: 1.1rem;

    font-size: 0.78rem;
    color: var(--text-dim);
}

.ic-formats code {
    font-family: var(--mono) !important;
    font-size: 0.72rem;
    color: #b6c2e6;

    background: rgba(255,255,255,0.05);
    border: 1px solid var(--line);

    padding: 0.18rem 0.55rem;
    border-radius: 6px;
}

.loading-line {
    display: flex;
    align-items: center;
    gap: 0.7rem;

    margin-top: 1.2rem;

    font-family: var(--mono) !important;
    font-size: 0.84rem;
    color: var(--text-dim);
}

.mini-spinner {
    width: 14px;
    height: 14px;

    border-radius: 50%;

    border: 2px solid var(--line-strong);
    border-top-color: var(--accent, var(--cyan));

    animation: spin .8s linear infinite;
}

@keyframes spin {
    to { transform: rotate(360deg); }
}


/* ==========================================================
   RESULTS HEADER
   ========================================================== */

.input-eyebrow {
    font-family: var(--mono) !important;
    font-size: 0.74rem;
    letter-spacing: 0.14em;
    text-transform: uppercase;

    color: var(--accent, var(--cyan));
    margin-bottom: 0.3rem;
}

.input-title {
    font-size: clamp(1.8rem, 3.2vw, 2.4rem);
    font-weight: 700;
    letter-spacing: -0.03em;

    color: #fff;

    margin: 0.2rem 0 0.7rem;
}

.input-sub {
    display: inline-block;

    max-width: 100%;

    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;

    font-family: var(--mono) !important;
    font-size: 0.78rem;
    color: var(--text-dim);

    border: 1px solid var(--line);
    border-radius: 999px;

    padding: 0.3rem 0.8rem;

    background: rgba(255,255,255,0.03);
    margin-bottom: 1.2rem;
}


/* ==========================================================
   RESULTS DASHBOARD
   ========================================================== */

.res-head-url {
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;

    max-width: 100%;

    font-family: var(--mono) !important;
    font-size: 0.78rem;
    color: var(--text-dim);

    border: 1px solid var(--line);
    border-radius: 999px;

    padding: 0.3rem 0.8rem;

    background: rgba(255,255,255,0.03);
}

.res-head-url span {
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
}

.res-title {
    font-size: clamp(1.8rem, 3.2vw, 2.4rem);
    font-weight: 700;
    letter-spacing: -0.03em;
    color: #fff;
    margin: 0.9rem 0 0.8rem;
}


/* ---------- KPI cards ---------- */

.kpis {
    display: grid;
    grid-template-columns: repeat(4, minmax(0, 1fr));

    gap: 1rem;
    margin: 1.6rem 0 1.2rem;
}

.kpi {
    min-width: 0;

    border: 1px solid var(--line);
    border-radius: var(--radius-lg);

    padding: 1.05rem 1.2rem;

    background: var(--bg-glass);
}

.kpi-label {
    font-size: 0.78rem;
    color: var(--text-dim);
    margin-bottom: 0.5rem;
}

.kpi-value {
    font-size: 1.55rem;
    font-weight: 700;
    letter-spacing: -0.02em;

    color: #fff;
    line-height: 1.15;

    overflow-wrap: anywhere;
}

.kpi-value.mono {
    font-family: var(--mono) !important;
    font-weight: 600;
}

.kpi-value.pos {
    color: var(--positive);
}

.kpi-value.neg {
    color: var(--negative);
}

.kpi-value.small {
    font-size: 1.15rem;
}


/* ---------- Panels ---------- */

.panel {
    border: 1px solid var(--line);
    border-radius: var(--radius-lg);

    padding: 1.3rem 1.4rem;

    background: var(--bg-glass);
    margin-bottom: 1.1rem;
}

.panel-title {
    display: flex;
    align-items: center;
    justify-content: space-between;

    font-size: 0.98rem;
    font-weight: 600;

    color: #fff;
    margin-bottom: 1.1rem;
}

.panel-title .left {
    display: inline-flex;
    align-items: center;
    gap: 0.55rem;
}

.panel-title .ico {
    color: var(--cyan);
}

.panel-title small {
    font-weight: 400;
    font-size: 0.74rem;
    color: var(--text-dim);
}


/* ---------- Comments ---------- */

.c-row {
    display: flex;
    gap: 0.85rem;
    align-items: flex-start;

    padding: 0.8rem 0;

    border-bottom: 1px solid var(--line);
}

.c-row:first-of-type {
    padding-top: 0;
}

.c-row:last-child {
    border-bottom: none;
    padding-bottom: 0;
}

.c-bar {
    width: 3px;
    align-self: stretch;

    border-radius: 3px;
    flex-shrink: 0;
}

.c-text {
    font-size: 0.86rem;
    line-height: 1.5;

    color: var(--text);
    overflow-wrap: anywhere;
}

.c-meta {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    margin-top: 0.4rem;
}

.c-conf {
    font-family: var(--mono) !important;
    font-size: 0.7rem;
    color: var(--text-faint);
}


/* ---------- Donut and legend ---------- */

.donut-wrap {
    display: flex;
    align-items: center;
    gap: 1.8rem;
}

.donut {
    position: relative;
    width: 150px;
    height: 150px;
    flex-shrink: 0;
}

.donut svg {
    width: 100%;
    height: 100%;
    transform: rotate(-90deg);
}

.donut-center {
    position: absolute;
    inset: 0;

    display: flex;
    flex-direction: column;

    align-items: center;
    justify-content: center;
}

.donut-center b {
    font-size: 1.6rem;
    font-weight: 700;
    color: #fff;
    letter-spacing: -0.02em;
}

.donut-center span {
    font-size: 0.72rem;
    color: var(--text-dim);
}

.legend {
    flex: 1;
    display: grid;
    gap: 0.7rem;
}

.legend-row {
    display: flex;
    align-items: center;
    gap: 0.6rem;

    font-size: 0.86rem;
    color: var(--text);
}

.legend-dot {
    width: 10px;
    height: 10px;

    border-radius: 3px;
    flex-shrink: 0;
}

.legend-pct {
    margin-left: auto;

    font-family: var(--mono) !important;
    font-size: 0.8rem;

    color: var(--text-dim);
}

.emo-row {
    margin-bottom: 1rem;
}

.emo-row:last-child {
    margin-bottom: 0;
}


/* ==========================================================
   STREAMLIT TABLES, EXPANDERS, DOWNLOADS
   ========================================================== */

div[data-testid="stExpander"] {
    border: 1px solid var(--line);
    border-radius: var(--radius-lg);
    background: var(--bg-glass);
}

div[data-testid="stExpander"] summary p {
    font-weight: 500;
}

div[data-testid="stDownloadButton"] button {
    min-height: 2.5rem;

    border: 1px solid var(--line-strong);
    border-radius: var(--radius-md);

    background: rgba(255,255,255,0.04);
    color: var(--text);

    font-size: 0.82rem;
}

div[data-testid="stDownloadButton"] button:hover {
    border-color: var(--cyan);
    color: #fff;
}


/* ==========================================================
   PRO DIALOG
   ========================================================== */

div[data-testid="stDialog"] div[role="dialog"] {
    background: linear-gradient(
        170deg,
        #121a3e,
        #070b1d
    ) !important;

    border: 1px solid var(--line-strong);
    border-radius: 22px;
}

.pro-hero {
    text-align: center;
    margin: 0.2rem 0 0.8rem;
}

.pro-hero-title {
    font-size: 1.8rem;
    font-weight: 700;
    letter-spacing: -0.03em;
    color: #fff;
}

.pro-hero-sub {
    font-size: 0.92rem;
    color: var(--text-dim);
    margin-top: 0.4rem;
    line-height: 1.55;
}

.pro-reason {
    display: flex;
    align-items: center;
    gap: 0.6rem;

    font-size: 0.84rem;
    color: var(--warn);

    border: 1px solid rgba(245,185,77,0.4);
    background: rgba(245,185,77,0.08);

    border-radius: var(--radius-md);
    padding: 0.7rem 1rem;
    margin: 1rem 0;
}

.benefit-row {
    display: flex;
    gap: 0.9rem;
    align-items: flex-start;

    padding: 0.7rem 0;

    border-bottom: 1px solid var(--line);
}

.benefit-row:last-child {
    border-bottom: none;
}

.benefit-icon {
    width: 34px;
    height: 34px;

    border-radius: 10px;
    flex-shrink: 0;

    display: flex;
    align-items: center;
    justify-content: center;

    color: var(--cyan);

    background: rgba(34,211,238,0.09);
    border: 1px solid rgba(34,211,238,0.22);
}

.benefit-title {
    font-weight: 600;
    font-size: 0.92rem;
    color: var(--text);
}

.benefit-desc {
    font-size: 0.8rem;
    color: var(--text-dim);
    margin-top: 2px;
}

.price-box {
    text-align: center;
    margin: 1.2rem 0 0.8rem;
}

.price-big {
    font-size: 2.4rem;
    font-weight: 700;
    letter-spacing: -0.03em;
    color: #fff;
}

.price-per {
    font-size: 0.9rem;
    color: var(--text-dim);
    margin-left: 0.3rem;
}

.demo-note {
    font-size: 0.72rem;
    color: var(--text-faint);
    text-align: center;
    margin-top: 0.7rem;
}


/* ==========================================================
   RESPONSIVE DESIGN
   ========================================================== */


/* ---------- LARGE DESKTOP: 1440px+ ---------- */

@media (min-width: 1440px) {

    .block-container {
        max-width: 1400px;
        padding: 2rem 3rem 4rem;
    }

    .hero-title {
        font-size: clamp(3.4rem, 4vw, 4.4rem);
    }

    .section-head {
        margin-top: 3.8rem;
    }

    .kpis {
        gap: 1.3rem;
    }

    .kpi {
        padding: 1.4rem;
    }

    .panel {
        padding: 1.6rem;
    }
}


/* ---------- LAPTOP: 1025px–1439px ---------- */

@media (min-width: 1025px) and (max-width: 1439px) {

    .block-container {
        max-width: 1240px;
        padding: 1.5rem 2rem 3rem;
    }

    .hero-title {
        font-size: clamp(2.6rem, 4vw, 3.5rem);
    }
}


/* ---------- TABLET: 769px–1024px ---------- */

@media (min-width: 769px) and (max-width: 1024px) {

    .block-container {
        padding: 1.2rem 1.5rem 2.5rem;
    }

    [data-testid="stHorizontalBlock"] {
        flex-wrap: wrap !important;
        gap: 1rem !important;
    }

    [data-testid="stHorizontalBlock"] > [data-testid="column"] {
        min-width: 0 !important;
        flex: 1 1 calc(50% - 1rem) !important;
    }

    .hero-title {
        font-size: clamp(2.2rem, 4.5vw, 3rem);
    }

    .hero-sub {
        font-size: 0.95rem;
    }

    .preview {
        padding: 1.1rem;
    }

    .preview-body {
        gap: 1rem;
    }

    .section-head {
        margin-top: 2.5rem;
    }

    .kpis {
        grid-template-columns: repeat(2, minmax(0, 1fr));
        gap: 0.8rem;
    }

    .panel {
        padding: 1.1rem;
    }

    .st-key-inputcard {
        padding: 1.6rem;
    }

    .auth-title {
        margin-top: 1.5rem;
    }
}


/* ---------- MOBILE: up to 768px ---------- */

@media (max-width: 768px) {

    .block-container {
        padding: 1rem 1rem 2rem !important;
        max-width: 100% !important;
    }

    [data-testid="stHorizontalBlock"] {
        flex-direction: column !important;
        flex-wrap: nowrap !important;
        gap: 0.9rem !important;
    }

    [data-testid="stHorizontalBlock"] > [data-testid="column"] {
        width: 100% !important;
        min-width: 100% !important;
        max-width: 100% !important;
        flex: 1 1 100% !important;
    }

    /* Navigation */

    .st-key-topnav {
        padding-bottom: 0.7rem;
        margin-bottom: 1.5rem;
    }

    .nav-meta {
        justify-content: flex-start;
        gap: 0.4rem;
    }

    .nav-user {
        font-size: 0.74rem;
    }

    .st-key-topnav .stButton > button {
        min-height: 2.2rem;
        padding: 0.4rem 0.65rem;
        font-size: 0.72rem;
    }

    .brand {
        gap: 0.45rem;
    }

    .brand-word {
        font-size: 1.12rem;
    }

    .brand-mark {
        border-radius: 9px;
    }

    /* Hero */

    .hero-title {
        font-size: clamp(2rem, 9vw, 2.8rem);
        line-height: 1.12;
        margin: 0.6rem 0 0.8rem;
    }

    .hero-sub {
        font-size: 0.9rem;
        line-height: 1.65;
        margin-bottom: 1.3rem;
    }

    .spectrum {
        max-width: 100%;
    }

    /* Preview */

    .preview {
        padding: 1rem;
        border-radius: 16px;
    }

    .preview-body {
        flex-direction: column;
        align-items: stretch;
        gap: 1.2rem;
    }

    .preview-foot {
        gap: 0.6rem;
        flex-wrap: wrap;
    }

    /* Section headings */

    .section-head {
        flex-direction: column;
        align-items: flex-start;
        gap: 0.35rem;
        margin: 2.2rem 0 1rem;
    }

    .section-title {
        font-size: 1.15rem;
    }

    .section-note {
        font-size: 0.78rem;
    }

    /* Platform cards */

    [class*="st-key-card_"] {
        padding: 1.1rem;
        border-radius: 15px;
    }

    .pc-desc {
        min-height: auto;
    }

    .pc-top {
        margin-bottom: 0.8rem;
    }

    /* Input page */

    .st-key-inputcard {
        padding: 1.2rem 1rem;
        margin-top: 0.3rem;
        border-radius: 17px;
    }

    .ic-head {
        flex-wrap: wrap;
        gap: 0.7rem;
        margin-bottom: 1.1rem;
    }

    .ic-title {
        font-size: clamp(1.55rem, 7vw, 2rem);
    }

    .ic-sub {
        font-size: 0.87rem;
        margin-bottom: 1.2rem;
    }

    .ic-platform {
        font-size: 0.85rem;
    }

    /* Forms and inputs */

    div[data-testid="stForm"] {
        padding: 1.1rem 0.9rem;
        border-radius: 15px;
    }

    div[data-baseweb="input"] input,
    div[data-baseweb="base-input"] input {
        font-size: 0.82rem !important;
        padding: 0.7rem 0.8rem !important;
    }

    .stButton > button,
    div[data-testid="stFormSubmitButton"] > button {
        width: 100%;
        min-height: 2.8rem;
        white-space: normal;
        font-size: 0.82rem;
    }

    /* Authentication */

    .auth-side {
        padding: 0.5rem 0 0;
    }

    .auth-title {
        font-size: clamp(1.9rem, 8vw, 2.5rem);
        margin: 1rem 0 0.8rem;
    }

    .auth-sub {
        font-size: 0.9rem;
        margin-bottom: 1.2rem;
    }

    /* Results dashboard */

    .res-title {
        font-size: clamp(1.65rem, 7vw, 2.2rem);
    }

    .input-title {
        font-size: clamp(1.6rem, 7vw, 2.1rem);
    }

    .input-sub,
    .res-head-url {
        display: flex;
        width: 100%;
        max-width: 100%;
        overflow-wrap: anywhere;
        white-space: normal;
        border-radius: 10px;
        font-size: 0.7rem;
    }

    /* KPI cards */

    .kpis {
        grid-template-columns: repeat(2, minmax(0, 1fr));
        gap: 0.65rem;
        margin: 1.1rem 0;
    }

    .kpi {
        padding: 0.85rem;
        border-radius: 13px;
        min-width: 0;
    }

    .kpi-label {
        font-size: 0.7rem;
    }

    .kpi-value {
        font-size: 1.25rem;
        overflow-wrap: anywhere;
    }

    .kpi-value.small {
        font-size: 1rem;
    }

    /* Dashboard panels */

    .panel {
        padding: 1rem;
        border-radius: 14px;
        margin-bottom: 0.85rem;
    }

    .panel-title {
        font-size: 0.9rem;
        flex-wrap: wrap;
        gap: 0.5rem;
    }

    /* Sentiment chart */

    .donut-wrap {
        flex-direction: column;
        gap: 1.2rem;
        align-items: center;
    }

    .donut {
        width: 135px;
        height: 135px;
    }

    .legend {
        width: 100%;
    }

    .legend-row {
        font-size: 0.8rem;
    }

    /* Comments */

    .c-row {
        gap: 0.65rem;
    }

    .c-text {
        font-size: 0.8rem;
        overflow-wrap: anywhere;
    }

    .c-meta {
        flex-wrap: wrap;
    }

    /* Tables */

    div[data-testid="stDataFrame"],
    div[data-testid="stTable"] {
        max-width: 100%;
        overflow-x: auto !important;
    }

    /* Footer */

    .footer-bar {
        flex-direction: column;
        align-items: flex-start;
        gap: 0.8rem;
        margin-top: 2rem;
    }

    /* Dialog */

    div[data-testid="stDialog"] div[role="dialog"] {
        width: calc(100vw - 1.5rem) !important;
        max-width: calc(100vw - 1.5rem) !important;
        margin: auto;
        border-radius: 16px;
    }

    .pro-hero-title {
        font-size: 1.5rem;
    }

    .price-big {
        font-size: 2rem;
    }
}


/* ---------- SMALL MOBILE: up to 380px ---------- */

@media (max-width: 380px) {

    .block-container {
        padding-left: 0.75rem !important;
        padding-right: 0.75rem !important;
    }

    .hero-title {
        font-size: 1.9rem;
    }

    .brand-word {
        font-size: 1rem;
    }

    .kpis {
        gap: 0.5rem;
    }

    .kpi {
        padding: 0.7rem;
    }

    .kpi-value {
        font-size: 1.1rem;
    }

    .panel {
        padding: 0.8rem;
    }

    .st-key-inputcard {
        padding: 1rem 0.8rem;
    }
}


/* ---------- ACCESSIBILITY ---------- */

@media (prefers-reduced-motion: reduce) {

    *,
    *::before,
    *::after {
        animation: none !important;
        transition: none !important;
    }

}

</style>
"""


# ==========================================================
# LIGHT THEME
# ==========================================================

LIGHT_CSS = r"""
<style>

:root,
.stApp {
    color-scheme: light;

    --bg: #f3f6fc;
    --bg-elevated: #ffffff;
    --bg-glass: rgba(255, 255, 255, 0.82);

    --line: rgba(79, 70, 229, 0.16);
    --line-strong: rgba(79, 70, 229, 0.30);

    --text: #0b1220;
    --text-dim: #51607a;
    --text-faint: #8a96ad;

    --track: rgba(79, 70, 229, 0.12);
    --heading: #0b1220;

    --cyan: #0891b2;

    --negative: #e0365c;
    --neutral: #5b6cf0;
    --positive: #0f9f73;
    --warn: #b7791f;
}


/* ---------- Backdrop ---------- */

.stApp {
    background: var(--bg) !important;
}

.stApp::before {
    background:
        radial-gradient(
            ellipse 800px 480px at 82% -6%,
            rgba(124, 58, 237, 0.18),
            transparent 62%
        ),
        radial-gradient(
            ellipse 760px 460px at 8% 2%,
            rgba(6, 182, 212, 0.20),
            transparent 60%
        ),
        linear-gradient(
            rgba(79,70,229,0.08) 1px,
            transparent 1px
        ),
        linear-gradient(
            90deg,
            rgba(79,70,229,0.08) 1px,
            transparent 1px
        );

    background-size:
        auto,
        auto,
        56px 56px,
        56px 56px;
}


/* ---------- Animated scan line ---------- */

.stApp::after {
    content: "";

    position: fixed;
    top: 0;
    left: 0;
    right: 0;

    height: 2px;
    z-index: 999;
    pointer-events: none;

    background: linear-gradient(
        90deg,
        transparent,
        #06b6d4,
        #4f46e5,
        #7c3aed,
        transparent
    );

    background-size: 200% 100%;

    animation: sentio-scan 6s linear infinite;
}

@keyframes sentio-scan {
    to {
        background-position: -200% 0;
    }
}


/* ---------- Headings ---------- */

.brand-word,
.section-title,
.pc-name,
.auth-form-title,
.ic-title,
.kpi-value,
.panel-title,
.donut-center b,
.pro-hero-title,
.price-big {
    color: var(--heading);
}

.kpi-value.pos {
    color: var(--positive);
}

.kpi-value.neg {
    color: var(--negative);
}

.hero-title,
.auth-title,
.res-title,
.input-title {
    background: linear-gradient(
        95deg,
        #0b1220 0%,
        #312e81 45%,
        #4f46e5 75%,
        #0891b2 100%
    );

    -webkit-background-clip: text;
    background-clip: text;

    color: transparent;
    -webkit-text-fill-color: transparent;
}


/* ---------- Cards ---------- */

[class*="st-key-card_"] {
    background: linear-gradient(
        180deg,
        rgba(255,255,255,0.96),
        rgba(244,247,255,0.92)
    );

    box-shadow: 0 12px 30px -18px rgba(79,70,229,0.45);
}

.preview,
.st-key-inputcard {
    background: linear-gradient(
        160deg,
        rgba(255,255,255,0.96),
        rgba(238,243,255,0.92)
    );

    box-shadow:
        0 30px 70px -40px rgba(79,70,229,0.55),
        inset 0 1px 0 #ffffff;
}

div[data-testid="stForm"] {
    background: rgba(255,255,255,0.86);

    box-shadow:
        0 30px 70px -40px rgba(79,70,229,0.5),
        inset 0 1px 0 #ffffff;

    position: relative;
}

div[data-testid="stForm"]::before {
    content: "";

    position: absolute;
    top: -1px;
    left: 14%;
    right: 14%;

    height: 2px;
    border-radius: 2px;

    background: linear-gradient(
        90deg,
        transparent,
        #06b6d4,
        #7c3aed,
        transparent
    );

    pointer-events: none;
}

.pc-icon {
    background: rgba(79,70,229,0.06);
}

.chip {
    background: rgba(255,255,255,0.75);
}

.res-head-url,
.input-sub {
    background: rgba(255,255,255,0.75);
}

.ic-formats code {
    color: #3730a3;
    background: rgba(79,70,229,0.08);
}

.url-error {
    color: #9f1239;
}

div[data-testid="stDialog"] div[role="dialog"] {
    background: #ffffff !important;
}

.spectrum-bar::after {
    box-shadow:
        0 0 0 1px var(--line-strong),
        0 0 14px rgba(15,159,115,0.7);
}


/* ---------- Buttons ---------- */

.stButton > button,
div[data-testid="stFormSubmitButton"] > button {
    background: #ffffff;
    color: var(--text);
    border-color: var(--line-strong);
}

.stButton > button:hover,
div[data-testid="stFormSubmitButton"] > button:hover {
    color: var(--text);
    background: #ffffff;
    border-color: #06b6d4;

    box-shadow:
        0 0 0 3px rgba(6,182,212,0.15),
        0 8px 20px -8px rgba(6,182,212,0.5);
}

.st-key-back_to_select .stButton > button:hover,
.st-key-goto_signup .stButton > button:hover,
.st-key-goto_login .stButton > button:hover {
    color: var(--text);
    background: rgba(79,70,229,0.07);
    border-color: var(--line);
}

div[data-testid="stDownloadButton"] button {
    background: #ffffff;
    color: var(--text);
}

div[data-testid="stDownloadButton"] button:hover {
    color: var(--text);
    border-color: #06b6d4;
}


/* ---------- Primary buttons ---------- */

.stButton > button[kind="primary"],
div[data-testid="stFormSubmitButton"] > button[kind="primaryFormSubmit"],
.stButton > button[data-testid="stBaseButton-primary"],
div[data-testid="stFormSubmitButton"] > button[data-testid="stBaseButton-primaryFormSubmit"] {
    color: #ffffff;
    border: none;
    background: var(--brand-grad);

    box-shadow:
        0 10px 26px -10px rgba(79,70,229,0.75),
        0 0 18px rgba(6,182,212,0.22);
}

.stButton > button[kind="primary"]:hover,
div[data-testid="stFormSubmitButton"] > button[kind="primaryFormSubmit"]:hover,
.stButton > button[data-testid="stBaseButton-primary"]:hover,
div[data-testid="stFormSubmitButton"] > button[data-testid="stBaseButton-primaryFormSubmit"]:hover {
    color: #ffffff;
    background: var(--brand-grad);
    filter: brightness(1.08);

    box-shadow:
        0 14px 32px -10px rgba(79,70,229,0.9),
        0 0 26px rgba(6,182,212,0.4);
}

.stApp .stButton button p,
.stApp div[data-testid="stFormSubmitButton"] button p,
.stApp div[data-testid="stDownloadButton"] button p {
    color: inherit !important;
}

.stApp .stButton button[kind="primary"] p,
.stApp .stButton button[data-testid="stBaseButton-primary"] p,
.stApp div[data-testid="stFormSubmitButton"] button p {
    color: #ffffff !important;
}


/* ---------- Native Streamlit text ---------- */

.stApp [data-testid="stMarkdownContainer"] p,
.stApp [data-testid="stMarkdownContainer"] li,
.stApp [data-testid="stMarkdownContainer"] h1,
.stApp [data-testid="stMarkdownContainer"] h2,
.stApp [data-testid="stMarkdownContainer"] h3,
.stApp [data-testid="stMarkdownContainer"] h4 {
    color: var(--text) !important;
}

.stApp [data-testid="stMarkdownContainer"] a {
    color: #4f46e5 !important;
}

.stApp [data-testid="stWidgetLabel"] p,
.stApp label p {
    color: var(--text-dim) !important;

    font-family: var(--mono) !important;
    font-size: 0.72rem !important;

    letter-spacing: 0.08em;
    text-transform: uppercase;
}

.stApp [data-testid="stCaptionContainer"] * {
    color: var(--text-dim) !important;
}

.stApp [data-testid="stMetricLabel"] * {
    color: var(--text-dim) !important;
}

.stApp [data-testid="stMetricValue"] * {
    color: var(--text) !important;
    font-family: var(--mono) !important;
    font-weight: 700 !important;
}

div[data-testid="stExpander"] summary p {
    color: var(--text) !important;
}

div[data-testid="stToggle"] p {
    color: var(--text-dim) !important;
    text-transform: none;
    letter-spacing: 0;

    font-family: var(--font) !important;
    font-size: 0.8rem !important;
}


/* ---------- Inputs and selects ---------- */

.stApp div[data-baseweb="input"],
.stApp div[data-baseweb="base-input"] {
    background: #ffffff !important;
    border: 1px solid var(--line-strong) !important;
}

.stApp div[data-baseweb="input"]:focus-within {
    border-color: #06b6d4 !important;

    box-shadow:
        0 0 0 3px rgba(6,182,212,0.20),
        0 0 18px rgba(6,182,212,0.25) !important;
}

.stApp div[data-baseweb="input"] input::placeholder {
    color: var(--text-faint) !important;
}

.stApp div[data-baseweb="select"] > div {
    background: #ffffff !important;
    color: var(--text) !important;

    border: 1px solid var(--line-strong) !important;
    border-radius: var(--radius-md) !important;
}

.stApp div[data-baseweb="select"] svg {
    fill: var(--text-dim) !important;
}

.stApp [data-baseweb="tag"] {
    background: rgba(79,70,229,0.12) !important;
}

.stApp [data-baseweb="tag"] span {
    color: #3730a3 !important;
}

div[data-baseweb="popover"] ul,
div[data-baseweb="popover"] > div,
div[data-baseweb="menu"] {
    background: #ffffff !important;
    color: var(--text) !important;

    border: 1px solid var(--line) !important;
    border-radius: 12px !important;
}

div[data-baseweb="menu"] li,
div[data-baseweb="popover"] li {
    color: var(--text) !important;
}


/* ---------- Containers, tabs, sliders, tables ---------- */

[data-testid="stVerticalBlockBorderWrapper"] {
    background: var(--bg-glass);
    border-color: var(--line) !important;
    border-radius: 14px;
}

.stApp button[data-baseweb="tab"] p {
    color: var(--text-dim) !important;
}

.stApp button[data-baseweb="tab"][aria-selected="true"] p {
    color: #4f46e5 !important;
}

.stApp [data-baseweb="tab-highlight"] {
    background: linear-gradient(
        90deg,
        #06b6d4,
        #7c3aed
    ) !important;
}

.stApp [data-testid="stSliderThumbValue"],
.stApp [data-testid="stTickBarMin"],
.stApp [data-testid="stTickBarMax"] {
    color: var(--text) !important;
}

.stApp [data-baseweb="slider"] [role="slider"] {
    background: #4f46e5 !important;

    box-shadow:
        0 0 0 4px rgba(79,70,229,0.2),
        0 0 14px rgba(6,182,212,0.6);
}

.stApp [data-testid="stDataFrame"] {
    border: 1px solid var(--line);
    border-radius: 12px;
    overflow: hidden;
}

.stApp hr {
    border-color: var(--line) !important;
}

</style>
"""


# ==========================================================
# THEME INJECTION
# ==========================================================

def inject_theme():
    """
    Inject the base dark theme on every Streamlit run.

    When session_state['theme'] == 'light',
    inject the light theme overrides as well.
    """

    st.markdown(
        THEME_CSS,
        unsafe_allow_html=True
    )

    if st.session_state.get("theme", "dark") == "light":
        st.markdown(
            LIGHT_CSS,
            unsafe_allow_html=True
        )


# ==========================================================
# PLATFORM CARD ACCENTS
# ==========================================================

def inject_card_accents(platforms: list):
    """Apply individual accent colours to platform cards."""

    rules = "".join(
        (
            f'.st-key-card_{p["key"]} '
            f'{{ --accent: {p["accent"]}; }}'
        )
        for p in platforms
    )

    st.markdown(
        f"<style>{rules}</style>",
        unsafe_allow_html=True
    )


# ==========================================================
# SHARED DONUT CHART
# ==========================================================

def donut_svg(segments, size: int = 150, stroke: int = 14) -> str:
    """
    Generate an SVG donut chart.

    segments:
        [(percentage, colour), ...]

    Percentages should sum to approximately 100.
    """

    radius = (size - stroke) / 2
    circumference = 2 * 3.14159265 * radius

    cumulative = 0.0

    parts = [
        (
            f'<circle cx="{size/2}" cy="{size/2}" '
            f'r="{radius}" fill="none" '
            f'style="stroke:var(--track)" '
            f'stroke-width="{stroke}"/>'
        )
    ]

    for pct, colour in segments:

        if pct <= 0:
            continue

        dash = circumference * pct / 100

        parts.append(
            (
                f'<circle cx="{size/2}" cy="{size/2}" '
                f'r="{radius}" fill="none" '
                f'stroke="{colour}" '
                f'stroke-width="{stroke}" '
                f'stroke-dasharray="{dash:.2f} '
                f'{circumference - dash:.2f}" '
                f'stroke-dashoffset="'
                f'{-circumference * cumulative / 100:.2f}"/>'
            )
        )

        cumulative += pct

    return (
        f'<svg viewBox="0 0 {size} {size}" '
        f'aria-hidden="true">'
        f'{"".join(parts)}'
        f'</svg>'
    )


# ==========================================================
# SHARED ERROR BOX
# ==========================================================

def error_box(message: str):
    """Display a styled error message."""

    md(
        f'<div class="url-error">'
        f'{icon("shield", 16)}'
        f'<span>{message}</span>'
        f'</div>'
    )
