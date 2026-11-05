"""
Sentio AI - entry point (page 1: source selection).

Run with: streamlit run app.py
"""

import streamlit as st

from theme import (
    inject_theme, inject_card_accents, find_asset, image_to_data_uri,
    md, icon, donut_svg, keyed_container, columns,
)
from theme_toggle import render_theme_toggle
from marquee import render_platform_marquee
from pages_instagram import render_instagram_input_page
from pages_youtube import render_youtube_input_page
from pages_linkedin import render_linkedin_input_page
from pages_x import render_x_input_page
from pages_facebook import render_facebook_input_page
from results_page import render_results_page
from auth import require_login, current_user
from credits import (
    render_account_bar, show_upgrade_if_requested, request_upgrade,
    check_access, consume_credit, get_account, PRO_ONLY, FREE_CREDITS,
)

PAGE_RENDERERS = {
    "youtube": render_youtube_input_page,
    "instagram": render_instagram_input_page,
    "linkedin": render_linkedin_input_page,
    "x": render_x_input_page,
    "facebook": render_facebook_input_page,
}

PLATFORMS = [
    {"key": "youtube", "name": "YouTube", "icon": "▶", "icon_base": "yt",
     "desc": "Video and Shorts comment threads, ranked by relevance.",
     "tag": "video", "accent": "#ff4d5e"},
    {"key": "instagram", "name": "Instagram", "icon": "◎", "icon_base": "ig",
     "desc": "Reel and post comments, including replies.",
     "tag": "reel / post", "accent": "#f0589b"},
    {"key": "linkedin", "name": "LinkedIn", "icon": "▤", "icon_base": "li",
     "desc": "Reactions and comments on a job posting or update.",
     "tag": "job post", "accent": "#4d8dff"},
    {"key": "x", "name": "X", "icon": "✕", "icon_base": "x",
     "desc": "Replies and quote posts under a single tweet.",
     "tag": "tweet", "accent": "#c4ccdc"},
    {"key": "facebook", "name": "Facebook", "icon": "◉", "icon_base": "fb",
     "desc": "Comments on posts, videos, and Reels.",
     "tag": "post / video", "accent": "#3b8cff"},
]

# Must be the first Streamlit call in the script.
st.set_page_config(
    page_title="Sentio AI - Audience Sentiment Intelligence",
    page_icon=find_asset("favicon") or "📡",
    layout="wide",
    initial_sidebar_state="collapsed",
)

if "platform" not in st.session_state:
    st.session_state.platform = None
if "page" not in st.session_state:
    st.session_state.page = "select"

# Theme is injected on every run, before anything is drawn.
inject_theme()
inject_card_accents(PLATFORMS)

# Light/dark toggle: AFTER inject_theme() so its overrides win, and BEFORE
# the login gate so it also shows on the login page.
render_theme_toggle()

# ----------------------------------------------------------------------
# LOGIN GATE + TOP NAV
# ----------------------------------------------------------------------
require_login()
render_account_bar()
show_upgrade_if_requested()

# ----------------------------------------------------------------------
# PAGE 2 / PAGE 3 ROUTING (must run before the landing page is drawn)
# ----------------------------------------------------------------------
if st.session_state.page != "loading":
    st.session_state.analysis_charged = False

if st.session_state.page == "input" and st.session_state.platform in PAGE_RENDERERS:
    chosen = next(p for p in PLATFORMS if p["key"] == st.session_state.platform)
    PAGE_RENDERERS[st.session_state.platform](chosen)
    st.stop()

elif st.session_state.page == "loading":
    platform_key = st.session_state.platform

    # Spend one credit exactly once per analysis (the results page reruns on every click).
    if not st.session_state.get("analysis_charged"):
        allowed, reason = check_access(current_user(), platform_key)
        if not allowed or not consume_credit(current_user(), platform_key):
            st.session_state.page = "select"
            st.session_state.platform = None
            request_upgrade(reason or "no_credits", platform_key)
            st.rerun()
        st.session_state.analysis_charged = True

    url = st.session_state.get("analysis_url", "")
    chosen = next((p for p in PLATFORMS if p["key"] == platform_key), None)
    render_results_page(platform_key, url, chosen)
    st.stop()

# ----------------------------------------------------------------------
# HERO
# ----------------------------------------------------------------------
hero_left, hero_right = columns([1.05, 1], gap="large")

with hero_left:
    md(
        """
        <div class="hero-title">Understand what your audience feels.</div>
        <div class="hero-sub">Paste a link. Sentio AI reads every comment underneath it and shows
        where the room stands: positive, negative, or somewhere in between.</div>
        <div class="spectrum">
            <div class="spectrum-bar"></div>
            <div class="spectrum-labels"><span>negative</span><span>neutral</span><span>positive</span></div>
        </div>
        """
    )

with hero_right:
    ring = donut_svg([(62, "#2fe0a5"), (24, "#8b9bff"), (14, "#ff5d7e")], size=132, stroke=13)
    md(
        f"""
        <div class="preview">
            <div class="preview-head">
                <div class="preview-title">{icon("pulse", 17)} Audience sentiment</div>
                <span class="chip">example output</span>
            </div>
            <div class="preview-body">
                <div class="donut" style="width:132px;height:132px;">{ring}
                    <div class="donut-center"><b>62%</b><span>positive</span></div>
                </div>
                <div class="preview-rows">
                    <div><div class="prow-top"><span>Positive</span><span>62%</span></div>
                        <div class="track"><div class="fill" style="width:62%;background:#2fe0a5"></div></div></div>
                    <div><div class="prow-top"><span>Neutral</span><span>24%</span></div>
                        <div class="track"><div class="fill" style="width:24%;background:#8b9bff"></div></div></div>
                    <div><div class="prow-top"><span>Negative</span><span>14%</span></div>
                        <div class="track"><div class="fill" style="width:14%;background:#ff5d7e"></div></div></div>
                </div>
            </div>
            <div class="preview-foot"><span>Overall verdict</span><b>Mostly positive</b></div>
        </div>
        """
    )

# ----------------------------------------------------------------------
# SOURCE CARDS
# ----------------------------------------------------------------------
acct = get_account(current_user())
is_pro_user = acct["plan"] == "pro"
note = (
    "Unlimited analyses on every platform."
    if is_pro_user
    else f"Free accounts get {FREE_CREDITS} analyses each on YouTube and Instagram."
)
md(
    f"""
    <div class="section-head">
        <div class="section-title">Choose a source</div>
        <div class="section-note">{note}</div>
    </div>
    """
)

# Auto-scrolling platform strip (left -> right). Decorative; the cards below stay clickable.
# Options: seconds=30 (bigger = slower), direction="left" to reverse.
render_platform_marquee(PLATFORMS)

cols = st.columns(5, gap="medium")
for col, p in zip(cols, PLATFORMS):
    with col:
        with keyed_container(f"card_{p['key']}"):
            icon_file = find_asset(p["icon_base"])
            icon_html = (
                f'<img src="{image_to_data_uri(icon_file)}" alt="{p["name"]} logo">'
                if icon_file else f'<span>{p["icon"]}</span>'
            )

            if is_pro_user:
                status = f'<span class="chip pro">{icon("star", 12)} Pro</span>'
                cta = f"Select {p['name']}"
            elif p["key"] in PRO_ONLY:
                status = f'<span class="chip locked">{icon("lock", 12)} Pro only</span>'
                cta = "Unlock with Pro"
            else:
                left = acct.get(p["key"], 0)
                cls = "empty" if left == 0 else ("low" if left == 1 else "ok")
                status = f'<span class="chip {cls}">{left} of {FREE_CREDITS} free</span>'
                cta = f"Select {p['name']}" if left > 0 else "Upgrade to continue"

            md(
                f"""
                <div class="pc-top"><div class="pc-icon">{icon_html}</div>{status}</div>
                <div class="pc-name">{p['name']}</div>
                <div class="pc-desc">{p['desc']}</div>
                <div class="pc-tag">{p['tag']}</div>
                """
            )
            if st.button(cta, key=f"select_{p['key']}"):
                ok, reason = check_access(current_user(), p["key"])
                if not ok:
                    request_upgrade(reason, p["key"])
                    st.rerun()
                st.session_state.platform = p["key"]
                st.session_state.page = "input"
                st.rerun()

# ----------------------------------------------------------------------
# FOOTER
# ----------------------------------------------------------------------
md(
    """
    <div class="footer-bar">
        <span class="status"><span class="dot"></span>Ready. Pick a source to begin.</span>
        <span class="models">XLM-RoBERTa sentiment &nbsp;/&nbsp; DistilRoBERTa emotion</span>
    </div>
    """
)
