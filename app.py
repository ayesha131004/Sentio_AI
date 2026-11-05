
"""
Sentio AI - entry point
Page 1: Source selection

Run with:
    streamlit run app.py
"""

import html
import streamlit as st

from theme import (
    inject_theme,
    inject_card_accents,
    find_asset,
    image_to_data_uri,
    md,
    icon,
    donut_svg,
    keyed_container,
    columns,
)

from theme_toggle import render_theme_toggle
from carousel import inject_carousel_css

from pages_instagram import render_instagram_input_page
from pages_youtube import render_youtube_input_page
from pages_linkedin import render_linkedin_input_page
from pages_x import render_x_input_page
from pages_facebook import render_facebook_input_page

from results_page import render_results_page

from auth import require_login, current_user

from credits import (
    render_account_bar,
    show_upgrade_if_requested,
    request_upgrade,
    check_access,
    consume_credit,
    get_account,
    PRO_ONLY,
    FREE_CREDITS,
)


# ==============================================================
# PAGE CONFIGURATION
# ==============================================================

st.set_page_config(
    page_title="Sentio AI - Audience Sentiment Intelligence",
    page_icon=find_asset("favicon") or "📡",
    layout="wide",
    initial_sidebar_state="collapsed",
)


# ==============================================================
# PLATFORM CONFIGURATION
# ==============================================================

PAGE_RENDERERS = {
    "youtube": render_youtube_input_page,
    "instagram": render_instagram_input_page,
    "linkedin": render_linkedin_input_page,
    "x": render_x_input_page,
    "facebook": render_facebook_input_page,
}


PLATFORMS = [
    {
        "key": "youtube",
        "name": "YouTube",
        "icon": "▶",
        "icon_base": "yt",
        "desc": "Video and Shorts comment threads, ranked by relevance.",
        "tag": "video",
        "accent": "#ff4d5e",
    },
    {
        "key": "instagram",
        "name": "Instagram",
        "icon": "◎",
        "icon_base": "ig",
        "desc": "Reel and post comments, including replies.",
        "tag": "reel / post",
        "accent": "#f0589b",
    },
    {
        "key": "linkedin",
        "name": "LinkedIn",
        "icon": "▤",
        "icon_base": "li",
        "desc": "Reactions and comments on a job posting or update.",
        "tag": "job post",
        "accent": "#4d8dff",
    },
    {
        "key": "x",
        "name": "X",
        "icon": "✕",
        "icon_base": "x",
        "desc": "Replies and quote posts under a single tweet.",
        "tag": "tweet",
        "accent": "#c4ccdc",
    },
    {
        "key": "facebook",
        "name": "Facebook",
        "icon": "◉",
        "icon_base": "fb",
        "desc": "Comments on posts, videos, and Reels.",
        "tag": "post / video",
        "accent": "#3b8cff",
    },
]


# ==============================================================
# SESSION STATE
# ==============================================================

if "platform" not in st.session_state:
    st.session_state.platform = None

if "page" not in st.session_state:
    st.session_state.page = "select"


# ==============================================================
# THEME
# ==============================================================

inject_theme()

inject_card_accents(PLATFORMS)

render_theme_toggle()


# ==============================================================
# RESPONSIVE LANDING PAGE CSS
# ==============================================================

APP_RESPONSIVE_CSS = """
<style>

/* ==========================================================
   GLOBAL RESPONSIVE SETTINGS
========================================================== */

.stApp {
    overflow-x: hidden;
}

.block-container {
    width: 100%;
    max-width: 1320px;
    padding-left: 2rem;
    padding-right: 2rem;
    padding-bottom: 3rem;
}

.block-container,
.block-container * {
    box-sizing: border-box;
}

[data-testid="stElementContainer"] {
    min-width: 0;
}

[data-testid="stMarkdownContainer"] {
    min-width: 0;
}

img, svg {
    max-width: 100%;
}

.stApp p {
    overflow-wrap: anywhere;
}


/* ==========================================================
   HERO SECTION
========================================================== */

.hero-title {
    font-size: clamp(2.6rem, 5vw, 4.4rem);
    font-weight: 800;
    line-height: 1.08;
    letter-spacing: -.045em;
    max-width: 650px;
    margin-bottom: 1.3rem;
    color: var(--heading, #ffffff);
}

.hero-sub {
    font-size: 1.08rem;
    line-height: 1.8;
    color: var(--text-dim, #8c97bd);
    max-width: 570px;
    margin-bottom: 2rem;
}

.spectrum {
    max-width: 420px;
    width: 100%;
    margin-top: 2rem;
}

.spectrum-bar {
    width: 100%;
    height: 7px;
    border-radius: 20px;
    background: linear-gradient(
        90deg,
        #ff5d7e 0%,
        #8b9bff 50%,
        #2fe0a5 100%
    );
    box-shadow: 0 0 20px rgba(139,155,255,.15);
}

.spectrum-labels {
    display: flex;
    justify-content: space-between;
    gap: .5rem;
    margin-top: .7rem;
    font-family: var(--mono, monospace);
    font-size: .72rem;
    letter-spacing: .1em;
    text-transform: uppercase;
    color: var(--text-dim, #8c97bd);
}


/* ==========================================================
   SENTIMENT PREVIEW
========================================================== */

.preview {
    width: 100%;
    max-width: 520px;
    min-width: 0;
    margin-left: auto;
    border: 1px solid var(--line-strong, rgba(130,150,255,.32));
    border-radius: 22px;
    padding: 1.5rem;
    background: var(--bg-glass, rgba(14,20,46,.62));
    box-shadow: 0 25px 70px -35px rgba(100,120,255,.3);
    overflow: hidden;
}

.preview-head {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: .8rem;
    flex-wrap: wrap;
    margin-bottom: 1.5rem;
}

.preview-title {
    display: flex;
    align-items: center;
    gap: .55rem;
    font-weight: 650;
    font-size: 1rem;
    color: var(--text, #eaf0ff);
}

.chip {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    gap: .35rem;
    padding: .35rem .75rem;
    border: 1px solid var(--line-strong, rgba(130,150,255,.32));
    border-radius: 999px;
    color: var(--text-dim, #8c97bd);
    font-size: .7rem;
    white-space: nowrap;
}

.preview-body {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 1.5rem;
    min-width: 0;
}

.donut {
    position: relative;
    flex: 0 0 auto;
    display: flex;
    align-items: center;
    justify-content: center;
}

.donut svg {
    display: block;
    width: 100%;
    height: 100%;
}

.donut-center {
    position: absolute;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    text-align: center;
}

.donut-center b {
    font-size: 1.65rem;
    line-height: 1.2;
    color: var(--heading, #fff);
}

.donut-center span {
    font-size: .7rem;
    color: var(--text-dim, #8c97bd);
}

.preview-rows {
    flex: 1;
    min-width: 0;
}

.preview-rows > div {
    margin-bottom: 1rem;
}

.prow-top {
    display: flex;
    justify-content: space-between;
    gap: .6rem;
    margin-bottom: .5rem;
    font-size: .82rem;
    color: var(--text, #eaf0ff);
}

.track {
    width: 100%;
    height: 6px;
    border-radius: 20px;
    overflow: hidden;
    background: var(--track, rgba(255,255,255,.07));
}

.fill {
    height: 100%;
    border-radius: 20px;
}

.preview-foot {
    display: flex;
    justify-content: space-between;
    gap: .7rem;
    flex-wrap: wrap;
    margin-top: 1.3rem;
    padding-top: 1rem;
    border-top: 1px solid var(--line, rgba(130,150,255,.16));
    font-size: .82rem;
}

.preview-foot span {
    color: var(--text-dim, #8c97bd);
}

.preview-foot b {
    color: var(--positive, #2fe0a5);
}


/* ==========================================================
   SOURCE SECTION HEADING
========================================================== */

.section-head {
    display: flex;
    justify-content: space-between;
    align-items: flex-end;
    gap: 1rem;
    flex-wrap: wrap;
    margin: 3.5rem 0 1.5rem;
}

.section-title {
    font-size: clamp(1.55rem, 3vw, 2.1rem);
    font-weight: 750;
    letter-spacing: -.035em;
    color: var(--heading, #ffffff);
}

.section-note {
    font-size: .82rem;
    color: var(--text-dim, #8c97bd);
    line-height: 1.5;
}


/* ==========================================================
   PLATFORM CARDS
========================================================== */

.st-key-carousel {
    width: 100%;
    max-width: 100%;
    min-width: 0;
}

.st-key-carousel [data-testid="stHorizontalBlock"] {
    min-width: 0;
}

.st-key-carousel [data-testid="column"] {
    min-width: 0;
}

.pc-top {
    display: flex;
    justify-content: space-between;
    align-items: center;
    flex-wrap: wrap;
    gap: .6rem;
    margin-bottom: 1.5rem;
}

.pc-icon {
    width: 54px;
    height: 54px;
    flex: 0 0 54px;
    border-radius: 16px;
    display: flex;
    align-items: center;
    justify-content: center;
    background: var(--bg-glass, rgba(14,20,46,.62));
    border: 1px solid var(--line-strong, rgba(130,150,255,.32));
    font-size: 1.5rem;
    overflow: hidden;
}

.pc-icon img {
    width: 34px;
    height: 34px;
    object-fit: contain;
}

.pc-name {
    font-size: 1.2rem;
    font-weight: 700;
    color: var(--heading, #ffffff);
    margin-bottom: .55rem;
}

.pc-desc {
    min-height: 78px;
    font-size: .84rem;
    line-height: 1.6;
    color: var(--text-dim, #8c97bd);
    overflow-wrap: anywhere;
}

.pc-tag {
    display: inline-flex;
    margin-top: .8rem;
    padding: .35rem .7rem;
    border-radius: 999px;
    font-family: var(--mono, monospace);
    font-size: .68rem;
    color: var(--text-dim, #8c97bd);
    background: var(--bg-glass, rgba(14,20,46,.62));
    border: 1px solid var(--line, rgba(130,150,255,.16));
}

/* Card container styling */
.st-key-carousel [class*="st-key-card_"] {
    min-width: 0;
    width: 100%;
    height: 100%;
    padding: 1.25rem;
    border: 1px solid var(--line-strong, rgba(130,150,255,.32));
    border-radius: 19px;
    background: var(--bg-glass, rgba(14,20,46,.62));
    transition: border-color .2s, transform .2s;
    overflow: hidden;
}

.st-key-carousel [class*="st-key-card_"]:hover {
    border-color: var(--accent, var(--line-strong));
    transform: translateY(-3px);
}

/* Platform selection button */
.st-key-carousel .stButton > button {
    width: 100%;
    min-height: 44px;
    margin-top: 1.1rem;
    border-radius: 11px;
    font-size: .85rem;
    font-weight: 650;
}


/* ==========================================================
   CREDIT STATUS CHIPS
========================================================== */

.chip.pro {
    color: #d8c0ff;
    border-color: rgba(168,120,255,.4);
    background: rgba(139,92,246,.12);
}

.chip.locked {
    color: #ffbd77;
    border-color: rgba(245,185,77,.35);
    background: rgba(245,185,77,.08);
}

.chip.ok {
    color: #2fe0a5;
    border-color: rgba(47,224,165,.3);
}

.chip.low {
    color: #f5b94d;
    border-color: rgba(245,185,77,.3);
}

.chip.empty {
    color: #ff7187;
    border-color: rgba(255,93,126,.3);
}


/* ==========================================================
   FOOTER
========================================================== */

.footer-bar {
    display: flex;
    justify-content: space-between;
    align-items: center;
    flex-wrap: wrap;
    gap: .8rem;
    margin-top: 3rem;
    padding: 1rem 0;
    border-top: 1px solid var(--line, rgba(130,150,255,.16));
    font-size: .76rem;
    color: var(--text-dim, #8c97bd);
}

.footer-bar .status {
    display: inline-flex;
    align-items: center;
    gap: .5rem;
}

.footer-bar .dot {
    width: 7px;
    height: 7px;
    border-radius: 50%;
    background: var(--positive, #2fe0a5);
    box-shadow: 0 0 8px var(--positive, #2fe0a5);
}

.footer-bar .models {
    text-align: right;
}


/* ==========================================================
   TABLET
========================================================== */

@media screen and (max-width: 960px) {

    .block-container {
        max-width: 100%;
        padding-left: 1.5rem;
        padding-right: 1.5rem;
    }

    .hero-title {
        font-size: clamp(2.3rem, 4.5vw, 3.3rem);
    }

    .hero-sub {
        font-size: .98rem;
    }

    .preview {
        padding: 1.2rem;
    }

    .preview-body {
        gap: 1rem;
    }

    .section-head {
        margin-top: 2.7rem;
    }

    .pc-desc {
        min-height: 90px;
    }
}


/* ==========================================================
   MOBILE
========================================================== */

@media screen and (max-width: 640px) {

    .block-container {
        width: 100%;
        max-width: 100%;
        padding: .8rem .9rem 2rem;
    }

    /* Hero */
    .hero-title {
        font-size: clamp(2rem, 8vw, 2.8rem);
        line-height: 1.1;
        letter-spacing: -.04em;
        margin-bottom: .9rem;
    }

    .hero-sub {
        font-size: .9rem;
        line-height: 1.65;
        margin-bottom: 1.2rem;
    }

    .spectrum {
        margin-top: 1.3rem;
    }

    .spectrum-labels {
        font-size: .62rem;
    }

    /* Sentiment preview */
    .preview {
        max-width: 100%;
        margin: .8rem 0 0;
        padding: 1rem;
        border-radius: 17px;
    }

    .preview-head {
        margin-bottom: 1.1rem;
    }

    .preview-title {
        font-size: .9rem;
    }

    .preview-body {
        gap: .8rem;
    }

    .donut-center b {
        font-size: 1.35rem;
    }

    .donut-center span {
        font-size: .62rem;
    }

    .preview-rows > div {
        margin-bottom: .8rem;
    }

    .prow-top {
        font-size: .72rem;
    }

    .preview-foot {
        font-size: .75rem;
    }

    /* Source heading */
    .section-head {
        align-items: flex-start;
        flex-direction: column;
        gap: .45rem;
        margin: 2.5rem 0 1.2rem;
    }

    .section-title {
        font-size: 1.6rem;
    }

    .section-note {
        font-size: .75rem;
    }

    /* Platform cards */
    .st-key-carousel [class*="st-key-card_"] {
        padding: 1.1rem;
        border-radius: 15px;
    }

    .pc-top {
        margin-bottom: 1rem;
    }

    .pc-icon {
        width: 46px;
        height: 46px;
        flex-basis: 46px;
        border-radius: 13px;
    }

    .pc-icon img {
        width: 29px;
        height: 29px;
    }

    .pc-name {
        font-size: 1.1rem;
    }

    .pc-desc {
        min-height: 0;
        font-size: .83rem;
    }

    .pc-tag {
        font-size: .65rem;
    }

    .st-key-carousel .stButton > button {
        margin-top: .8rem;
        min-height: 44px;
        font-size: .82rem;
    }

    /* Footer */
    .footer-bar {
        align-items: flex-start;
        flex-direction: column;
        margin-top: 2rem;
        font-size: .7rem;
    }

    .footer-bar .models {
        text-align: left;
    }
}


/* ==========================================================
   EXTRA SMALL PHONES
========================================================== */

@media screen and (max-width: 390px) {

    .block-container {
        padding-left: .65rem;
        padding-right: .65rem;
    }

    .hero-title {
        font-size: 1.95rem;
    }

    .preview {
        padding: .85rem;
    }

    .preview-body {
        gap: .5rem;
    }

    .prow-top {
        font-size: .67rem;
    }

    .section-title {
        font-size: 1.45rem;
    }

    .chip {
        font-size: .62rem;
        padding: .3rem .55rem;
    }
}


/* ==========================================================
   LARGE DESKTOP
========================================================== */

@media screen and (min-width: 1600px) {

    .block-container {
        max-width: 1450px;
    }

    .hero-title {
        font-size: 4.5rem;
    }
}


/* ==========================================================
   ACCESSIBILITY
========================================================== */

@media (prefers-reduced-motion: reduce) {

    *,
    *::before,
    *::after {
        scroll-behavior: auto !important;
        animation-duration: .01ms !important;
        animation-iteration-count: 1 !important;
        transition-duration: .01ms !important;
    }
}

</style>
"""


st.markdown(
    APP_RESPONSIVE_CSS,
    unsafe_allow_html=True,
)


# ==============================================================
# LOGIN GATE + TOP NAVIGATION
# ==============================================================

require_login()

render_account_bar()

show_upgrade_if_requested()


# ==============================================================
# PAGE ROUTING
# ==============================================================

if st.session_state.page != "loading":
    st.session_state.analysis_charged = False


# --------------------------------------------------------------
# INPUT PAGE
# --------------------------------------------------------------

if (
    st.session_state.page == "input"
    and st.session_state.platform in PAGE_RENDERERS
):

    chosen = next(
        p for p in PLATFORMS
        if p["key"] == st.session_state.platform
    )

    PAGE_RENDERERS[st.session_state.platform](chosen)

    st.stop()


# --------------------------------------------------------------
# RESULTS PAGE
# --------------------------------------------------------------

elif st.session_state.page == "loading":

    platform_key = st.session_state.platform

    # Spend one credit exactly once per analysis.
    if not st.session_state.get("analysis_charged"):

        allowed, reason = check_access(
            current_user(),
            platform_key
        )

        if not allowed or not consume_credit(
            current_user(),
            platform_key
        ):

            st.session_state.page = "select"
            st.session_state.platform = None

            request_upgrade(
                reason or "no_credits",
                platform_key
            )

            st.rerun()

        st.session_state.analysis_charged = True

    url = st.session_state.get("analysis_url", "")

    chosen = next(
        (
            p for p in PLATFORMS
            if p["key"] == platform_key
        ),
        None
    )

    render_results_page(
        platform_key,
        url,
        chosen
    )

    st.stop()


# ==============================================================
# HERO SECTION
# ==============================================================

hero_left, hero_right = columns(
    [1.05, 1],
    gap="large"
)


# --------------------------------------------------------------
# HERO LEFT
# --------------------------------------------------------------

with hero_left:

    md(
        """
        <div class="hero-title">
            Understand what your audience feels.
        </div>

        <div class="hero-sub">
            Paste a link. Sentio AI reads every comment underneath it
            and shows where the room stands: positive, negative,
            or somewhere in between.
        </div>

        <div class="spectrum">
            <div class="spectrum-bar"></div>

            <div class="spectrum-labels">
                <span>negative</span>
                <span>neutral</span>
                <span>positive</span>
            </div>
        </div>
        """
    )


# --------------------------------------------------------------
# HERO RIGHT
# --------------------------------------------------------------

with hero_right:

    ring = donut_svg(
        [
            (62, "#2fe0a5"),
            (24, "#8b9bff"),
            (14, "#ff5d7e"),
        ],
        size=132,
        stroke=13,
    )

    md(
        f"""
        <div class="preview">

            <div class="preview-head">

                <div class="preview-title">
                    {icon("pulse", 17)}
                    Audience sentiment
                </div>

                <span class="chip">
                    example output
                </span>

            </div>

            <div class="preview-body">

                <div
                    class="donut"
                    style="width:132px;height:132px;"
                >

                    {ring}

                    <div class="donut-center">
                        <b>62%</b>
                        <span>positive</span>
                    </div>

                </div>

                <div class="preview-rows">

                    <div>
                        <div class="prow-top">
                            <span>Positive</span>
                            <span>62%</span>
                        </div>

                        <div class="track">
                            <div
                                class="fill"
                                style="width:62%;background:#2fe0a5"
                            ></div>
                        </div>
                    </div>

                    <div>
                        <div class="prow-top">
                            <span>Neutral</span>
                            <span>24%</span>
                        </div>

                        <div class="track">
                            <div
                                class="fill"
                                style="width:24%;background:#8b9bff"
                            ></div>
                        </div>
                    </div>

                    <div>
                        <div class="prow-top">
                            <span>Negative</span>
                            <span>14%</span>
                        </div>

                        <div class="track">
                            <div
                                class="fill"
                                style="width:14%;background:#ff5d7e"
                            ></div>
                        </div>
                    </div>

                </div>

            </div>

            <div class="preview-foot">
                <span>Overall verdict</span>
                <b>Mostly positive</b>
            </div>

        </div>
        """
    )


# ==============================================================
# SOURCE SELECTION HEADING
# ==============================================================

acct = get_account(current_user())

is_pro_user = acct["plan"] == "pro"

note = (
    "Unlimited analyses on every platform."
    if is_pro_user
    else (
        f"Free accounts get {FREE_CREDITS} analyses each "
        "on YouTube and Instagram."
    )
)

md(
    f"""
    <div class="section-head">

        <div class="section-title">
            Choose a source
        </div>

        <div class="section-note">
            {html.escape(note)}
        </div>

    </div>
    """
)


# ==============================================================
# PLATFORM CAROUSEL
# ==============================================================

inject_carousel_css(
    PLATFORMS,
    seconds=9,
    card_width=300,
    start_delay=1.0,
)


# --------------------------------------------------------------
# PLATFORM CARD
# --------------------------------------------------------------

def render_source_card(p: dict):
    """Render one platform selection card."""

    with keyed_container(f"card_{p['key']}"):

        icon_file = find_asset(p["icon_base"])

        if icon_file:

            icon_html = (
                f'<img src="{image_to_data_uri(icon_file)}" '
                f'alt="{html.escape(p["name"])} logo">'
            )

        else:

            icon_html = (
                f'<span>{html.escape(p["icon"])}</span>'
            )

        # ------------------------------------------------------
        # ACCOUNT STATUS
        # ------------------------------------------------------

        if is_pro_user:

            status = (
                f'<span class="chip pro">'
                f'{icon("star", 12)} Pro'
                f'</span>'
            )

            cta = f"Select {p['name']}"

        elif p["key"] in PRO_ONLY:

            status = (
                f'<span class="chip locked">'
                f'{icon("lock", 12)} Pro only'
                f'</span>'
            )

            cta = "Unlock with Pro"

        else:

            left = acct.get(p["key"], 0)

            cls = (
                "empty" if left == 0
                else "low" if left == 1
                else "ok"
            )

            status = (
                f'<span class="chip {cls}">'
                f'{left} of {FREE_CREDITS} free'
                f'</span>'
            )

            cta = (
                f"Select {p['name']}"
                if left > 0
                else "Upgrade to continue"
            )

        # ------------------------------------------------------
        # CARD CONTENT
        # ------------------------------------------------------

        md(
            f"""
            <div class="pc-top">

                <div class="pc-icon">
                    {icon_html}
                </div>

                {status}

            </div>

            <div class="pc-name">
                {html.escape(p['name'])}
            </div>

            <div class="pc-desc">
                {html.escape(p['desc'])}
            </div>

            <div class="pc-tag">
                {html.escape(p['tag'])}
            </div>
            """
        )

        # ------------------------------------------------------
        # SELECTION BUTTON
        # ------------------------------------------------------

        if st.button(
            cta,
            key=f"select_{p['key']}",
            use_container_width=True,
        ):

            ok, reason = check_access(
                current_user(),
                p["key"]
            )

            if not ok:

                request_upgrade(
                    reason,
                    p["key"]
                )

                st.rerun()

            st.session_state.platform = p["key"]
            st.session_state.page = "input"

            st.rerun()


# --------------------------------------------------------------
# RENDER ALL PLATFORM CARDS
# --------------------------------------------------------------

with keyed_container("carousel"):

    cols = st.columns(
        len(PLATFORMS),
        gap="medium"
    )

    for col, platform in zip(cols, PLATFORMS):

        with col:
            render_source_card(platform)


# ==============================================================
# FOOTER
# ==============================================================

md(
    """
    <div class="footer-bar">

        <span class="status">
            <span class="dot"></span>
            Ready. Pick a source to begin.
        </span>

        <span class="models">
            XLM-RoBERTa sentiment
            &nbsp;/&nbsp;
            DistilRoBERTa emotion
        </span>

    </div>
    """
)
