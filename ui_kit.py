
"""
ui_kit.py
----------
Shared responsive input screen for all SentioAI platforms.

Responsive support:
- Mobile phones
- Tablets
- Laptops
- Desktop screens

Keeps existing theme.py helpers and session-state behaviour.
"""

import time
import html

import streamlit as st

from theme import find_asset, image_to_data_uri, icon, keyed_container


# ----------------------------------------------------------------------
# SMALL HELPERS
# ----------------------------------------------------------------------

def _flat(html_content: str) -> str:
    """Convert multiline HTML into one line."""
    return " ".join(
        line.strip()
        for line in html_content.splitlines()
        if line.strip()
    )


def _logo_html(platform: dict) -> str:
    name = html.escape(str(platform.get("name", "")))
    path = find_asset(platform.get("icon_base", "") or "")

    if path:
        try:
            return (
                f'<img src="{image_to_data_uri(path)}" '
                f'alt="{name}">'
            )
        except Exception:
            pass

    fallback = html.escape(str(platform.get("icon", "●")))
    return f"<span>{fallback}</span>"


def _credit_line(platform_key: str) -> str:
    """Return the user's remaining credit information."""
    try:
        from auth import current_user
        from credits import get_account, CREDIT_COLUMN

        acct = get_account(current_user())

        if acct["plan"] == "pro":
            return "Sentio AI Pro · unlimited analyses"

        if platform_key in CREDIT_COLUMN:
            return f"Uses 1 credit · {acct[platform_key]} left"

    except Exception:
        pass

    return ""


def _fill(key: str, value: str):
    st.session_state[key] = value


_SIDE_CARDS = [
    (
        "chart",
        "Sentiment split",
        "The positive, neutral and negative share across every comment."
    ),
    (
        "pulse",
        "Emotion breakdown",
        "Joy, anger, sadness and more, detected comment by comment."
    ),
    (
        "chat",
        "Comment insights",
        "See how individual comments were scored and where the room stands."
    ),
]


# ----------------------------------------------------------------------
# RESPONSIVE CSS
# ----------------------------------------------------------------------

_CSS = """
<style>

/* ==============================================================
   BASE
============================================================== */

.st-key-hx_page {
    --hx: #6d8bff;
    --hx2: #8b5cf6;
    width: 100%;
    max-width: 100%;
    min-width: 0;
    margin-top: 1.6rem;
}

.st-key-hx_page,
.st-key-hx_page * {
    box-sizing: border-box;
}

.st-key-hx_page div[data-testid="stElementContainer"] {
    margin: 0;
}

.block-container:has(.st-key-hx_page) {
    max-width: 1320px;
    width: 100%;
    padding-left: 2rem;
    padding-right: 2rem;
    padding-bottom: 5rem;
}

.st-key-hx_page div[data-testid="stHorizontalBlock"]:not(.st-key-hx_chips *) {
    gap: 3rem;
}

.st-key-hx_chips div[data-testid="stHorizontalBlock"] {
    gap: .8rem;
}

/* Prevent long URLs and text from overflowing */
.st-key-hx_page,
.hx-card,
.hx-card-desc,
.hx-model,
.hx-sub {
    overflow-wrap: anywhere;
    word-break: normal;
}


/* ==============================================================
   PROGRESS STEPS
============================================================== */

.hx-steps {
    display: flex;
    align-items: center;
    gap: .9rem;
    flex-wrap: wrap;
    font-family: var(--mono, ui-monospace, monospace);
    font-size: .76rem;
    letter-spacing: .1em;
    text-transform: uppercase;
    margin: 1.6rem 0 2.6rem;
}

.hx-step {
    display: flex;
    align-items: center;
    gap: .7rem;
    color: var(--text-dim, #8c97bd);
    opacity: .6;
}

.hx-step.done,
.hx-step.now {
    opacity: 1;
}

.hx-step.now {
    color: var(--text, #eaf0ff);
}

.hx-dot {
    width: 1.9rem;
    height: 1.9rem;
    flex-shrink: 0;
    border-radius: 50%;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    border: 1px solid var(--line-strong, rgba(130,150,255,.32));
    font-size: .74rem;
}

.hx-step.done .hx-dot {
    color: var(--positive, #2fe0a5);
    border-color: var(--positive, #2fe0a5);
    background: color-mix(in srgb, var(--positive, #2fe0a5) 14%, transparent);
}

.hx-step.now .hx-dot {
    color: var(--hx);
    border-color: var(--hx);
    box-shadow: 0 0 14px color-mix(in srgb, var(--hx) 55%, transparent);
}

.hx-bar {
    flex: 0 0 3rem;
    height: 1px;
    background: linear-gradient(
        90deg,
        var(--line-strong, rgba(130,150,255,.32)),
        transparent
    );
}


/* ==============================================================
   HERO
============================================================== */

.hx-hero {
    display: flex;
    gap: 1.6rem;
    align-items: center;
    margin: 0 0 1.5rem;
    min-width: 0;
}

.hx-logo {
    position: relative;
    flex: 0 0 84px;
    width: 84px;
    height: 84px;
    border-radius: 24px;
    display: flex;
    align-items: center;
    justify-content: center;
    background: var(--bg-glass, rgba(14,20,46,.62));
    font-size: 1.6rem;
    color: var(--hx);
}

.hx-logo::before {
    content: "";
    position: absolute;
    inset: -2px;
    border-radius: 22px;
    padding: 2px;
    background: conic-gradient(
        var(--hx),
        transparent 35%,
        var(--hx) 70%,
        transparent
    );
    -webkit-mask: linear-gradient(#000 0 0) content-box,
                  linear-gradient(#000 0 0);
    -webkit-mask-composite: xor;
    mask-composite: exclude;
    animation: hx-spin 7s linear infinite;
}

.hx-logo img {
    width: 46px;
    height: 46px;
    object-fit: contain;
    border-radius: 11px;
}

@keyframes hx-spin {
    to {
        transform: rotate(360deg);
    }
}

.hx-eyebrow {
    display: inline-flex;
    align-items: center;
    gap: .5rem;
    font-family: var(--mono, ui-monospace, monospace);
    font-size: .74rem;
    letter-spacing: .14em;
    text-transform: uppercase;
    color: var(--hx);
    padding: .4rem 1rem;
    border-radius: 999px;
    border: 1px solid color-mix(in srgb, var(--hx) 42%, transparent);
    background: color-mix(in srgb, var(--hx) 10%, transparent);
}

.hx-pulse {
    width: 7px;
    height: 7px;
    flex-shrink: 0;
    border-radius: 50%;
    background: var(--hx);
    animation: hx-pulse 1.8s infinite;
}

@keyframes hx-pulse {
    0% {
        box-shadow: 0 0 0 0 color-mix(in srgb, var(--hx) 70%, transparent);
    }

    100% {
        box-shadow: 0 0 0 10px transparent;
    }
}

.hx-title {
    font-size: clamp(2.2rem, 4vw, 3.3rem);
    font-weight: 700;
    letter-spacing: -.03em;
    line-height: 1.12;
    margin: .9rem 0 0;
    color: var(--heading, #fff);
}

.hx-title em {
    font-style: normal;
    background: linear-gradient(90deg, var(--hx), var(--hx2));
    -webkit-background-clip: text;
    background-clip: text;
    color: transparent;
}

.hx-sub {
    font-size: 1.05rem;
    color: var(--text-dim, #8c97bd);
    line-height: 1.7;
    max-width: 44rem;
    margin: 0 0 2.4rem;
}


/* ==============================================================
   INPUT PANEL
============================================================== */

.st-key-hx_panel {
    position: relative;
    overflow: hidden;
    min-width: 0;
    width: 100%;
    border: 1px solid var(--line-strong, rgba(130,150,255,.32));
    border-radius: 20px;
    background: var(--bg-glass, rgba(14,20,46,.62));
    -webkit-backdrop-filter: blur(12px);
    backdrop-filter: blur(12px);
    padding: 2.2rem 2.2rem 2rem;
    box-shadow: 0 28px 64px -36px color-mix(in srgb, var(--hx) 75%, transparent);
}

.st-key-hx_panel::before {
    content: "";
    position: absolute;
    left: 0;
    right: 0;
    top: 0;
    height: 2px;
    background: linear-gradient(90deg, transparent, var(--hx), transparent);
}

.hx-label {
    font-family: var(--mono, ui-monospace, monospace);
    font-size: .76rem;
    letter-spacing: .14em;
    text-transform: uppercase;
    color: var(--text-dim, #8c97bd);
    margin: 0 0 .9rem;
}

.hx-chips-label {
    margin: 1.8rem 0 .9rem;
}


/* ==============================================================
   URL INPUT
============================================================== */

.st-key-hx_page .st-key-hx_input_wrap div[data-baseweb="input"] {
    width: 100%;
    min-width: 0;
    border: 1px solid var(--line-strong, rgba(130,150,255,.32)) !important;
    border-radius: 14px !important;
}

.st-key-hx_page .st-key-hx_input_wrap div[data-baseweb="input"]:focus-within {
    border-color: var(--hx) !important;
    box-shadow:
        0 0 0 3px color-mix(in srgb, var(--hx) 22%, transparent),
        0 0 28px color-mix(in srgb, var(--hx) 30%, transparent) !important;
}

.st-key-hx_page .st-key-hx_input_wrap div[data-baseweb="input"] input {
    height: 3.7rem;
    min-width: 0;
    padding: 0 1.3rem !important;
    font-size: 1rem !important;
}


/* ==============================================================
   INPUT STATUS
============================================================== */

.hx-status {
    display: flex;
    align-items: center;
    gap: .6rem;
    min-height: 1.6rem;
    font-family: var(--mono, ui-monospace, monospace);
    font-size: .82rem;
    margin: .9rem 0 0;
}

.hx-status.ok {
    color: var(--positive, #2fe0a5);
}

.hx-status.warn {
    color: var(--warn, #f5b94d);
}

.hx-status i {
    width: 7px;
    height: 7px;
    flex-shrink: 0;
    border-radius: 50%;
    background: currentColor;
    display: inline-block;
    box-shadow: 0 0 8px currentColor;
}


/* ==============================================================
   QUICK-FILL CHIPS
============================================================== */

.st-key-hx_page .st-key-hx_chips .stButton > button {
    width: 100%;
    min-width: 0;
    height: 2.7rem;
    min-height: 2.7rem;
    padding: 0 .8rem;
    font-family: var(--mono, ui-monospace, monospace);
    font-size: .82rem;
    white-space: normal;
    overflow-wrap: anywhere;
    border-radius: 999px;
    background: color-mix(in srgb, var(--hx) 8%, transparent) !important;
    border: 1px dashed color-mix(in srgb, var(--hx) 55%, transparent) !important;
    box-shadow: none;
}

.st-key-hx_page .st-key-hx_chips .stButton > button:hover {
    border-style: solid !important;
    background: color-mix(in srgb, var(--hx) 18%, transparent) !important;
    box-shadow: none;
}


/* ==============================================================
   ANALYZE BUTTON
============================================================== */

.st-key-hx_page .st-key-hx_submit_wrap {
    margin-top: 2.2rem;
}

.st-key-hx_page .st-key-hx_submit_wrap .stButton > button {
    position: relative;
    overflow: hidden;
    width: 100%;
    height: 3.8rem;
    min-height: 3.8rem;
    border: none !important;
    border-radius: 14px !important;
    background: linear-gradient(90deg, var(--hx), var(--hx2)) !important;
    box-shadow: 0 16px 36px -16px color-mix(in srgb, var(--hx) 85%, transparent) !important;
    transition: transform .15s, filter .15s;
}

.st-key-hx_page .st-key-hx_submit_wrap .stButton > button p {
    color: #fff !important;
    font-weight: 700;
    letter-spacing: .02em;
    font-size: 1.1rem;
}

.st-key-hx_page .st-key-hx_submit_wrap .stButton > button:hover {
    transform: translateY(-1px);
    filter: brightness(1.08);
}

.st-key-hx_page .st-key-hx_submit_wrap .stButton > button::after {
    content: "";
    position: absolute;
    top: 0;
    bottom: 0;
    width: 40%;
    left: -60%;
    background: linear-gradient(
        100deg,
        transparent,
        rgba(255,255,255,.3),
        transparent
    );
    animation: hx-shine 3.4s ease-in-out infinite;
}

@keyframes hx-shine {
    0% {
        left: -60%;
    }

    55%, 100% {
        left: 130%;
    }
}

.hx-meta {
    font-family: var(--mono, ui-monospace, monospace);
    font-size: .8rem;
    color: var(--text-dim, #8c97bd);
    margin-top: 1.1rem;
    min-height: 1.2rem;
}


/* ==============================================================
   LOADING
============================================================== */

.hx-load {
    margin-top: 1.4rem;
    padding: 1.2rem 1.4rem;
    border-radius: 14px;
    border: 1px solid color-mix(in srgb, var(--hx) 40%, transparent);
    background: color-mix(in srgb, var(--hx) 8%, transparent);
}

.hx-load-row {
    display: flex;
    align-items: center;
    gap: .7rem;
    font-family: var(--mono, ui-monospace, monospace);
    font-size: .82rem;
    color: var(--text, #eaf0ff);
}

.hx-ring {
    width: 16px;
    height: 16px;
    flex-shrink: 0;
    border-radius: 50%;
    border: 2px solid color-mix(in srgb, var(--hx) 30%, transparent);
    border-top-color: var(--hx);
    animation: hx-spin .8s linear infinite;
}

.hx-track {
    height: 4px;
    border-radius: 4px;
    background: var(--track, rgba(255,255,255,.07));
    margin-top: .75rem;
    overflow: hidden;
}

.hx-fill {
    height: 100%;
    border-radius: 4px;
    background: linear-gradient(90deg, var(--hx), var(--hx2));
    transition: width .6s ease;
}


/* ==============================================================
   SIDE COLUMN
============================================================== */

.hx-side-title {
    font-family: var(--mono, ui-monospace, monospace);
    font-size: .76rem;
    letter-spacing: .14em;
    text-transform: uppercase;
    color: var(--text-dim, #8c97bd);
    margin: .4rem 0 1.1rem;
}

.hx-side-title.hx-gap-top {
    margin-top: 2.2rem;
}

.hx-card {
    display: flex;
    gap: 1.2rem;
    align-items: flex-start;
    min-width: 0;
    padding: 1.5rem 1.6rem;
    margin-bottom: 1.1rem;
    border-radius: 18px;
    border: 1px solid var(--line, rgba(130,150,255,.16));
    background: var(--bg-glass, rgba(14,20,46,.62));
    transition: transform .2s, border-color .2s;
}

.hx-card:hover {
    transform: translateX(3px);
    border-color: var(--hx);
}

.hx-ico {
    flex: 0 0 3rem;
    width: 3rem;
    height: 3rem;
    border-radius: 14px;
    display: flex;
    align-items: center;
    justify-content: center;
    color: var(--hx);
    background: color-mix(in srgb, var(--hx) 14%, transparent);
    border: 1px solid color-mix(in srgb, var(--hx) 32%, transparent);
}

.hx-card-title {
    font-weight: 600;
    font-size: 1.02rem;
    line-height: 1.3;
    color: var(--text, #eaf0ff);
}

.hx-card-desc {
    font-size: .9rem;
    color: var(--text-dim, #8c97bd);
    line-height: 1.6;
    margin-top: .35rem;
}

.hx-models {
    display: flex;
    flex-wrap: wrap;
    gap: .7rem;
}

.hx-model {
    font-family: var(--mono, ui-monospace, monospace);
    font-size: .74rem;
    padding: .4rem .9rem;
    border-radius: 999px;
    color: var(--text-dim, #8c97bd);
    border: 1px solid var(--line-strong, rgba(130,150,255,.32));
}


/* ==============================================================
   TABLET RESPONSIVENESS
============================================================== */

@media screen and (max-width: 960px) {

    .block-container:has(.st-key-hx_page) {
        max-width: 100%;
        padding-left: 1.5rem;
        padding-right: 1.5rem;
    }

    .st-key-hx_page {
        margin-top: 1rem;
    }

    .st-key-hx_page div[data-testid="stHorizontalBlock"]:not(.st-key-hx_chips *) {
        gap: 1.8rem;
    }

    .hx-hero {
        gap: 1.1rem;
    }

    .hx-logo {
        flex-basis: 72px;
        width: 72px;
        height: 72px;
        border-radius: 20px;
    }

    .hx-logo img {
        width: 40px;
        height: 40px;
    }

    .hx-title {
        font-size: clamp(2rem, 4vw, 2.7rem);
    }

    .st-key-hx_panel {
        padding: 1.8rem;
    }

    .hx-card {
        padding: 1.2rem;
        gap: .9rem;
    }
}


/* ==============================================================
   MOBILE RESPONSIVENESS
============================================================== */

@media screen and (max-width: 640px) {

    .block-container:has(.st-key-hx_page) {
        width: 100%;
        max-width: 100%;
        padding: .8rem .9rem 2.5rem;
    }

    .st-key-hx_page {
        margin-top: .4rem;
    }

    /* Stack the main input and information columns */
    .st-key-hx_page div[data-testid="stHorizontalBlock"]:not(.st-key-hx_chips *) {
        gap: 1.2rem;
    }

    /* Progress steps */
    .hx-steps {
        gap: .45rem;
        margin: 1rem 0 1.6rem;
        font-size: .62rem;
        letter-spacing: .06em;
    }

    .hx-step {
        gap: .35rem;
    }

    .hx-dot {
        width: 1.55rem;
        height: 1.55rem;
        font-size: .68rem;
    }

    .hx-bar {
        flex-basis: .9rem;
    }

    /* Hero */
    .hx-hero {
        align-items: flex-start;
        gap: .85rem;
        margin-bottom: 1rem;
    }

    .hx-logo {
        flex: 0 0 58px;
        width: 58px;
        height: 58px;
        border-radius: 17px;
        font-size: 1.2rem;
    }

    .hx-logo::before {
        border-radius: 17px;
    }

    .hx-logo img {
        width: 32px;
        height: 32px;
    }

    .hx-eyebrow {
        font-size: .61rem;
        letter-spacing: .08em;
        padding: .35rem .65rem;
    }

    .hx-title {
        font-size: clamp(1.65rem, 7vw, 2.25rem);
        line-height: 1.15;
        margin-top: .6rem;
    }

    .hx-sub {
        font-size: .91rem;
        line-height: 1.6;
        margin-bottom: 1.5rem;
    }

    /* Input panel */
    .st-key-hx_panel {
        padding: 1.25rem 1rem 1.2rem;
        border-radius: 16px;
    }

    .hx-label {
        font-size: .68rem;
        letter-spacing: .1em;
        margin-bottom: .7rem;
    }

    .hx-chips-label {
        margin-top: 1.3rem;
    }

    /* URL field */
    .st-key-hx_page .st-key-hx_input_wrap div[data-baseweb="input"] input {
        height: 3.25rem;
        padding: 0 .85rem !important;
        font-size: .88rem !important;
    }

    /* Chips */
    .st-key-hx_chips div[data-testid="stHorizontalBlock"] {
        gap: .45rem;
    }

    .st-key-hx_page .st-key-hx_chips .stButton > button {
        min-height: 2.6rem;
        height: auto;
        padding: .55rem .4rem;
        font-size: .7rem;
        line-height: 1.25;
    }

    /* Analyze button */
    .st-key-hx_page .st-key-hx_submit_wrap {
        margin-top: 1.5rem;
    }

    .st-key-hx_page .st-key-hx_submit_wrap .stButton > button {
        height: 3.35rem;
        min-height: 3.35rem;
    }

    .st-key-hx_page .st-key-hx_submit_wrap .stButton > button p {
        font-size: .98rem;
    }

    .hx-meta {
        font-size: .72rem;
    }

    /* Side cards */
    .hx-side-title {
        margin-top: .8rem;
        font-size: .7rem;
    }

    .hx-side-title.hx-gap-top {
        margin-top: 1.5rem;
    }

    .hx-card {
        padding: 1rem;
        gap: .85rem;
        margin-bottom: .75rem;
        border-radius: 14px;
    }

    .hx-ico {
        flex: 0 0 2.5rem;
        width: 2.5rem;
        height: 2.5rem;
        border-radius: 11px;
    }

    .hx-card-title {
        font-size: .94rem;
    }

    .hx-card-desc {
        font-size: .82rem;
        line-height: 1.5;
    }

    .hx-models {
        gap: .45rem;
    }

    .hx-model {
        font-size: .66rem;
        padding: .4rem .65rem;
    }

    .hx-load {
        padding: 1rem;
    }

    .hx-load-row {
        font-size: .73rem;
    }

    /* Touch-friendly controls */
    .st-key-hx_page .stButton > button {
        min-height: 44px;
    }
}


/* ==============================================================
   EXTRA SMALL PHONES
============================================================== */

@media screen and (max-width: 390px) {

    .block-container:has(.st-key-hx_page) {
        padding-left: .65rem;
        padding-right: .65rem;
    }

    .hx-hero {
        gap: .65rem;
    }

    .hx-logo {
        flex-basis: 50px;
        width: 50px;
        height: 50px;
    }

    .hx-logo img {
        width: 28px;
        height: 28px;
    }

    .hx-eyebrow {
        font-size: .55rem;
        padding: .3rem .5rem;
    }

    .hx-title {
        font-size: 1.55rem;
    }

    .hx-sub {
        font-size: .85rem;
    }

    .st-key-hx_panel {
        padding: 1rem .8rem;
    }

    .hx-steps {
        font-size: .57rem;
    }

    .hx-bar {
        flex-basis: .5rem;
    }

    .st-key-hx_page .st-key-hx_chips .stButton > button {
        font-size: .65rem;
    }
}


/* ==============================================================
   LARGE DESKTOP
============================================================== */

@media screen and (min-width: 1600px) {

    .block-container:has(.st-key-hx_page) {
        max-width: 1450px;
    }

    .st-key-hx_page div[data-testid="stHorizontalBlock"]:not(.st-key-hx_chips *) {
        gap: 4rem;
    }
}


/* ==============================================================
   ACCESSIBILITY
============================================================== */

@media (prefers-reduced-motion: reduce) {

    .hx-logo::before,
    .hx-pulse,
    .hx-ring,
    .st-key-hx_page .st-key-hx_submit_wrap .stButton > button::after {
        animation: none !important;
    }

    .hx-card,
    .st-key-hx_page .st-key-hx_submit_wrap .stButton > button {
        transition: none !important;
    }
}

</style>
"""


# ----------------------------------------------------------------------
# PROGRESS STEPS
# ----------------------------------------------------------------------

def _steps_html() -> str:
    items = [
        ("done", icon("check", 12), "Source"),
        ("now", "2", "Paste link"),
        ("", "3", "Analysis"),
    ]

    parts = []

    for i, (cls, sym, label) in enumerate(items):

        parts.append(
            f'<div class="hx-step {cls}">'
            f'<span class="hx-dot">{sym}</span>'
            f'{label}</div>'
        )

        if i < len(items) - 1:
            parts.append('<span class="hx-bar"></span>')

    return '<div class="hx-steps">' + "".join(parts) + "</div>"


# ----------------------------------------------------------------------
# LOADING HTML
# ----------------------------------------------------------------------

def _loading_html(msg: str, pct: int) -> str:

    safe_msg = html.escape(str(msg))
    safe_pct = max(0, min(100, int(pct)))

    return (
        f'<div class="hx-load">'
        f'<div class="hx-load-row">'
        f'<span class="hx-ring"></span>{safe_msg}'
        f'</div>'
        f'<div class="hx-track">'
        f'<div class="hx-fill" style="width:{safe_pct}%"></div>'
        f'</div>'
        f'</div>'
    )


# ----------------------------------------------------------------------
# ERROR HTML
# ----------------------------------------------------------------------

def _error_html(message: str) -> str:

    safe_message = html.escape(str(message))

    return (
        f'<div class="url-error">'
        f'{icon("shield", 16)}'
        f'<span>{safe_message}</span>'
        f'</div>'
    )


# ----------------------------------------------------------------------
# SHARED INPUT PAGE
# ----------------------------------------------------------------------

def render_input_page(
    *,
    platform: dict,
    key_prefix: str,
    pattern,
    placeholder: str,
    subtitle: str,
    formats: list,
    empty_msg: str,
    invalid_msg: str,
):
    """
    platform:
        Entry from PLATFORMS in app.py.

    key_prefix:
        Unique prefix for widget keys.

    pattern:
        Compiled regex used to validate the URL.

    formats:
        List of (chip label, example URL) pairs.
    """

    accent = platform.get("accent", "#6d8bff")
    name = platform.get("name", "")
    pkey = platform.get("key", "")

    input_key = f"{key_prefix}_url_input"
    submit_key = f"{key_prefix}_submit"

    safe_accent = html.escape(str(accent), quote=True)

    st.markdown(
        _CSS + f"<style>.st-key-hx_page{{--hx:{safe_accent};}}</style>",
        unsafe_allow_html=True,
    )

    with keyed_container("hx_page"):

        # ----------------------------------------------------------
        # BACK BUTTON
        # ----------------------------------------------------------

        if st.button(
            "← back to platforms",
            key="back_to_select"
        ):
            st.session_state.page = "select"
            st.rerun()

        # ----------------------------------------------------------
        # PROGRESS STEPS
        # ----------------------------------------------------------

        st.markdown(
            _steps_html(),
            unsafe_allow_html=True
        )

        # ----------------------------------------------------------
        # RESPONSIVE MAIN LAYOUT
        # ----------------------------------------------------------

        left, right = st.columns(
            [1.6, 1],
            gap="large"
        )

        # ==========================================================
        # LEFT COLUMN: HERO + INPUT
        # ==========================================================

        with left:

            safe_name = html.escape(str(name))
            safe_subtitle = html.escape(str(subtitle))

            st.markdown(
                _flat(
                    f"""
                    <div class="hx-hero">

                        <div class="hx-logo">
                            {_logo_html(platform)}
                        </div>

                        <div>

                            <span class="hx-eyebrow">
                                <span class="hx-pulse"></span>
                                {safe_name} connected
                            </span>

                            <div class="hx-title">
                                Paste your <em>{safe_name}</em> link
                            </div>

                        </div>

                    </div>

                    <div class="hx-sub">
                        {safe_subtitle}
                    </div>
                    """
                ),
                unsafe_allow_html=True,
            )

            # ------------------------------------------------------
            # INPUT PANEL
            # ------------------------------------------------------

            with keyed_container("hx_panel"):

                st.markdown(
                    '<div class="hx-label">Source link</div>',
                    unsafe_allow_html=True,
                )

                with keyed_container("hx_input_wrap"):

                    url = st.text_input(
                        f"{name} URL",
                        placeholder=placeholder,
                        label_visibility="collapsed",
                        key=input_key,
                    )

                clean = (url or "").strip()

                # --------------------------------------------------
                # URL VALIDATION STATUS
                # --------------------------------------------------

                if clean and pattern.match(clean):

                    st.markdown(
                        f"""
                        <div class="hx-status ok">
                            <i></i>
                            Valid {safe_name} link detected
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

                elif clean:

                    st.markdown(
                        f"""
                        <div class="hx-status warn">
                            <i></i>
                            This does not look like a {safe_name} link yet
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

                else:

                    st.markdown(
                        '<div class="hx-status"></div>',
                        unsafe_allow_html=True,
                    )

                # --------------------------------------------------
                # QUICK-FILL FORMATS
                # --------------------------------------------------

                st.markdown(
                    """
                    <div class="hx-label hx-chips-label">
                        Accepted formats · tap to start
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

                with keyed_container("hx_chips"):

                    cols = st.columns(len(formats))

                    for i, (label, example) in enumerate(formats):

                        with cols[i]:

                            st.button(
                                label,
                                key=f"{key_prefix}_fmt_{i}",
                                on_click=_fill,
                                args=(input_key, example),
                                use_container_width=True,
                            )

                # --------------------------------------------------
                # ANALYZE BUTTON
                # --------------------------------------------------

                with keyed_container("hx_submit_wrap"):

                    submit = st.button(
                        "Analyze this link",
                        key=submit_key,
                        type="primary",
                        use_container_width=True,
                    )

                # --------------------------------------------------
                # CREDIT INFORMATION
                # --------------------------------------------------

                credit_text = html.escape(
                    str(_credit_line(pkey))
                )

                st.markdown(
                    f'<div class="hx-meta">{credit_text}</div>',
                    unsafe_allow_html=True,
                )

                feedback = st.empty()

                # --------------------------------------------------
                # SUBMISSION HANDLING
                # --------------------------------------------------

                if submit:

                    if not clean:

                        feedback.markdown(
                            _error_html(empty_msg),
                            unsafe_allow_html=True,
                        )

                    elif not pattern.match(clean):

                        feedback.markdown(
                            _error_html(invalid_msg),
                            unsafe_allow_html=True,
                        )

                    else:

                        for msg, pct in [
                            ("analyzing....", 33),
                            ("1 sec....", 66),
                            ("almost ready....", 100),
                        ]:

                            feedback.markdown(
                                _loading_html(msg, pct),
                                unsafe_allow_html=True,
                            )

                            time.sleep(1)

                        st.session_state.analysis_url = clean
                        st.session_state.page = "loading"

                        st.rerun()

        # ==========================================================
        # RIGHT COLUMN: FEATURES
        # ==========================================================

        with right:

            cards = "".join(
                (
                    f'<div class="hx-card">'
                    f'<div class="hx-ico">{icon(ico, 18)}</div>'
                    f'<div>'
                    f'<div class="hx-card-title">{html.escape(title)}</div>'
                    f'<div class="hx-card-desc">{html.escape(desc)}</div>'
                    f'</div>'
                    f'</div>'
                )
                for ico, title, desc in _SIDE_CARDS
            )

            st.markdown(
                _flat(
                    f"""
                    <div class="hx-side-title">
                        What you'll get
                    </div>

                    {cards}

                    <div class="hx-side-title hx-gap-top">
                        Powered by
                    </div>

                    <div class="hx-models">

                        <span class="hx-model">
                            XLM-RoBERTa sentiment
                        </span>

                        <span class="hx-model">
                            DistilRoBERTa emotion
                        </span>

                    </div>
                    """
                ),
                unsafe_allow_html=True,
            )
