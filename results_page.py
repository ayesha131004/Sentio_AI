"""
results_page.py
-----------------
Shared page-3 renderer used by all four platforms. Fetches comments,
runs them through sentiment_engine + emotion_engine, and displays:
  - a comments feed card (colored avatar, text, meta, heart icon)
  - a sentiment donut chart with a face in the center + legend
  - an emotion breakdown (joy / neutral / sadness / anger bars)

Called from app.py once st.session_state.page == "loading".
"""

import streamlit as st
import pandas as pd

from sentiment_engine import analyze_comments
from emotion_engine import analyze_emotions
from comment_fetchers import (
    fetch_youtube_comments,
    fetch_instagram_comments,
    fetch_linkedin_comments,
    fetch_x_comments,
    DEMO_COMMENTS,
)

AVATAR_COLORS = ["#8b5cf6", "#3b82f6", "#ec4899", "#34d399", "#f59e0b", "#60a5fa"]

EMOTION_COLORS = {
    "joy": "#3ecf8e",
    "neutral": "#6366f1",
    "sadness": "#ec4899",
    "anger": "#f59e0b",
}
EMOTION_LABELS = {"joy": "Joy", "neutral": "Neutral", "sadness": "Sadness", "anger": "Anger"}

# ----------------------------------------------------------------------
# STYLE — scoped to this page
# ----------------------------------------------------------------------
st.markdown(
    """
    <style>
    .results-card {
        background: var(--bg-elevated);
        border: 1px solid var(--line);
        border-radius: 16px;
        padding: 1.4rem 1.3rem;
        margin-bottom: 1.2rem;
    }

    .results-card-title {
        display: flex;
        align-items: center;
        gap: 0.55rem;
        font-weight: 600;
        font-size: 1rem;
        color: var(--text);
        margin-bottom: 1rem;
    }

    .comment-row {
        display: flex;
        align-items: flex-start;
        gap: 0.8rem;
        padding: 0.65rem 0;
        border-bottom: 1px solid var(--line);
    }

    .comment-row:last-child {
        border-bottom: none;
    }

    .comment-avatar {
        width: 32px;
        height: 32px;
        border-radius: 50%;
        flex-shrink: 0;
        margin-top: 2px;
    }

    .comment-text {
        font-size: 0.85rem;
        color: var(--text);
        line-height: 1.4;
    }

    .comment-meta {
        font-size: 0.7rem;
        color: var(--text-dim);
        margin-top: 3px;
        font-family: 'JetBrains Mono', monospace;
    }

    .comment-heart {
        color: var(--text-dim);
        font-size: 0.95rem;
        margin-left: auto;
        padding-top: 2px;
    }

    .donut-wrap {
        display: flex;
        align-items: center;
        gap: 1.5rem;
    }

    .donut {
        width: 110px;
        height: 110px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        flex-shrink: 0;
    }

    .donut-inner {
        width: 72px;
        height: 72px;
        border-radius: 50%;
        background: var(--bg-elevated);
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.9rem;
    }

    .legend-row {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        font-size: 0.85rem;
        color: var(--text);
        margin-bottom: 0.55rem;
    }

    .legend-dot {
        width: 10px;
        height: 10px;
        border-radius: 50%;
        flex-shrink: 0;
    }

    .legend-pct {
        margin-left: auto;
        color: var(--text-dim);
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.8rem;
    }

    .emotion-row {
        margin-bottom: 0.9rem;
    }

    .emotion-row:last-child {
        margin-bottom: 0;
    }

    .emotion-label {
        display: flex;
        justify-content: space-between;
        font-size: 0.82rem;
        color: var(--text);
        margin-bottom: 0.35rem;
    }

    .emotion-track {
        height: 7px;
        border-radius: 4px;
        background: rgba(255,255,255,0.08);
        overflow: hidden;
    }

    .emotion-fill {
        height: 100%;
        border-radius: 4px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


def render_results_page(platform_key: str, url: str, platform_info: dict):
    accent = platform_info["accent"] if platform_info else "#3ecf8e"
    platform_name = platform_info["name"] if platform_info else "Platform"

    st.markdown(
        f"""
        <div class="input-eyebrow" style="--accent:{accent}; color:{accent};">
            ● analysis complete
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown('<div class="input-title">Results</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="input-sub">{url}</div>', unsafe_allow_html=True)

    comments = None
    used_demo = False
    error_message = None

    with st.spinner("Fetching and analyzing comments..."):
        try:
            if platform_key == "youtube":
                api_key = st.secrets.get("YOUTUBE_API_KEY", "")
                if not api_key:
                    raise ValueError("No YOUTUBE_API_KEY found in .streamlit/secrets.toml")
                comments = fetch_youtube_comments(url, api_key)
            elif platform_key == "instagram":
                comments = fetch_instagram_comments(url)
            elif platform_key == "linkedin":
                comments = fetch_linkedin_comments(url)
            elif platform_key == "x":
                comments = fetch_x_comments(url)
        except Exception as e:
            error_message = str(e)

        if not comments:
            comments = DEMO_COMMENTS
            used_demo = True

        results = analyze_comments(comments)
        emotions = analyze_emotions(comments)

    if used_demo:
        st.warning(
            f"⚠ Live comment fetching wasn't available for this link "
            f"({error_message or 'no comments returned'}). "
            f"Showing demo data so you can still see how the analysis works."
        )

    col_left, col_right = st.columns([1, 1], gap="large")

    # ---------------- LEFT: comments feed ----------------
    with col_left:
        st.markdown('<div class="results-card">', unsafe_allow_html=True)
        st.markdown(
            f'<div class="results-card-title">💬 {platform_name} Comments</div>',
            unsafe_allow_html=True,
        )
        for i, c in enumerate(results["per_comment"][:8]):
            color = AVATAR_COLORS[i % len(AVATAR_COLORS)]
            hours_ago = (i + 1) * 2
            st.markdown(
                f"""
                <div class="comment-row">
                    <div class="comment-avatar" style="background:{color}"></div>
                    <div style="flex:1">
                        <div class="comment-text">{c['text'][:140]}</div>
                        <div class="comment-meta">{hours_ago}h · Reply</div>
                    </div>
                    <div class="comment-heart">♡</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        st.markdown('</div>', unsafe_allow_html=True)

    # ---------------- RIGHT: sentiment donut + emotions ----------------
    with col_right:
        pos, neu, neg = results["positive_pct"], results["neutral_pct"], results["negative_pct"]
        stop1 = pos
        stop2 = pos + neu

        if pos >= neu and pos >= neg:
            face = "😊"
        elif neg >= pos and neg >= neu:
            face = "😞"
        else:
            face = "😐"

        st.markdown('<div class="results-card">', unsafe_allow_html=True)
        st.markdown('<div class="results-card-title">📊 Sentiment</div>', unsafe_allow_html=True)
        st.markdown(
            f"""
            <div class="donut-wrap">
                <div class="donut" style="background: conic-gradient(#3ecf8e 0% {stop1}%, #6366f1 {stop1}% {stop2}%, #ef5b7a {stop2}% 100%);">
                    <div class="donut-inner">{face}</div>
                </div>
                <div style="flex:1">
                    <div class="legend-row">
                        <span class="legend-dot" style="background:#3ecf8e"></span>
                        Positive<span class="legend-pct">{pos}%</span>
                    </div>
                    <div class="legend-row">
                        <span class="legend-dot" style="background:#6366f1"></span>
                        Neutral<span class="legend-pct">{neu}%</span>
                    </div>
                    <div class="legend-row">
                        <span class="legend-dot" style="background:#ef5b7a"></span>
                        Negative<span class="legend-pct">{neg}%</span>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="results-card">', unsafe_allow_html=True)
        st.markdown('<div class="results-card-title">❤️ Emotions</div>', unsafe_allow_html=True)
        for key in ["joy", "neutral", "sadness", "anger"]:
            pct = emotions.get(key, 0)
            color = EMOTION_COLORS[key]
            st.markdown(
                f"""
                <div class="emotion-row">
                    <div class="emotion-label"><span>{EMOTION_LABELS[key]}</span><span>{pct}%</span></div>
                    <div class="emotion-track"><div class="emotion-fill" style="width:{pct}%; background:{color}"></div></div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown(f"### Overall performance: **{results['verdict']}**")
    st.caption(f"Based on {results['total']} comments analyzed (any language).")

    with st.expander("See every comment's sentiment"):
        for c in results["per_comment"]:
            st.write(f"**[{c['label'].upper()}]** ({c['score']}) — {c['text']}")

    if st.button("← analyze another link", key="results_back"):
        st.session_state.page = "select"
        st.session_state.platform = None
        st.rerun()
