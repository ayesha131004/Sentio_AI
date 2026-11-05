"""
results_page.py
-----------------
Shared results page used by all platforms. Fetches comments, runs
sentiment + emotion analysis, and shows an interactive dashboard:
  - filters (sentiment, confidence, keyword, sort) that drive every chart
  - KPI row, sentiment donut, emotion bars, timeline, keywords
  - a scrollable comment feed and top-comment tabs

Called from app.py once st.session_state.page == "loading".
"""

import html
from collections import Counter

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from comment_fetchers import (
    fetch_instagram_comments_rich,
    fetch_linkedin_comments_rich,
    fetch_x_comments_rich,
    fetch_youtube_comments_rich,
    get_demo_comments_rich,
)

from report_pdf import build_pdf_report
from emotion_engine import analyze_emotions
from sentiment_engine import analyze_comments, results_to_dataframe
from theme_toggle import plot_layout


# Optional: per-comment emotion labels. Works without it.
try:
    from emotion_engine import classify_emotions
except ImportError:
    classify_emotions = None


AVATAR_COLORS = [
    "#8b5cf6", "#3b82f6", "#ec4899",
    "#34d399", "#f59e0b", "#60a5fa"
]

SENT_COLORS = {
    "Positive": "#3ecf8e",
    "Neutral": "#6366f1",
    "Negative": "#ef5b7a",
}

SENT_FACES = {
    "Positive": "😊",
    "Neutral": "😐",
    "Negative": "😞",
}

EMOTION_COLORS = {
    "Joy": "#3ecf8e",
    "Neutral": "#6366f1",
    "Sadness": "#ec4899",
    "Anger": "#f59e0b",
    "Fear": "#a78bfa",
    "Surprise": "#38bdf8",
    "Disgust": "#84cc16",
    "Optimism": "#facc15",
    "Unknown": "#64748b",
}


# ----------------------------------------------------------------------
# STYLE
# ----------------------------------------------------------------------

_CSS = """<style>
.comment-row{
    display:flex;
    align-items:flex-start;
    gap:.8rem;
    padding:.65rem 0;
    border-bottom:1px solid var(--line, rgba(255,255,255,.08));
}
.comment-row:last-child{
    border-bottom:none;
}
.comment-avatar{
    width:32px;
    height:32px;
    border-radius:50%;
    flex-shrink:0;
    margin-top:2px;
    display:flex;
    align-items:center;
    justify-content:center;
    font-size:.8rem;
    font-weight:600;
    color:#fff;
}
.comment-text{
    font-size:.85rem;
    color:var(--text, #e8e8f0);
    line-height:1.4;
    word-break:break-word;
}
.comment-meta{
    font-size:.7rem;
    color:var(--text-dim, #8b8ba0);
    margin-top:3px;
    font-family:'JetBrains Mono',monospace;
}
.comment-badge{
    display:inline-block;
    padding:0 .45rem;
    border-radius:999px;
    font-size:.65rem;
    margin-left:.4rem;
    color:#0b0b14;
    font-weight:600;
}
.comment-heart{
    color:var(--text-dim, #8b8ba0);
    font-size:.85rem;
    margin-left:auto;
    padding-top:2px;
    white-space:nowrap;
}
</style>"""


# ----------------------------------------------------------------------
# PLOT STYLE
# ----------------------------------------------------------------------

def _style(fig, **layout):
    """Applies the current light/dark theme to a Plotly figure."""

    t = plot_layout()

    grid_x = t.pop("xaxis", {})
    grid_y = t.pop("yaxis", {})

    fig.update_layout(
        margin=dict(l=0, r=0, t=40, b=0),
        **t,
        **layout
    )

    fig.update_xaxes(**grid_x)
    fig.update_yaxes(**grid_y)

    return fig


# ----------------------------------------------------------------------
# DATA LOADING
# ----------------------------------------------------------------------

def _fetch(platform_key: str, url: str) -> list[dict]:

    if platform_key == "youtube":
        api_key = st.secrets.get("YOUTUBE_API_KEY", "")

        if not api_key:
            raise ValueError(
                "No YOUTUBE_API_KEY found in .streamlit/secrets.toml"
            )

        return fetch_youtube_comments_rich(url, api_key)

    if platform_key == "instagram":
        return fetch_instagram_comments_rich(url)

    if platform_key == "linkedin":
        return fetch_linkedin_comments_rich(url)

    if platform_key == "x":
        return fetch_x_comments_rich(url)

    raise ValueError(
        f"Comment fetching isn't available for {platform_key} yet."
    )


def _load(platform_key: str, url: str) -> dict:

    cache_key = f"results::{platform_key}::{url}"

    if cache_key in st.session_state:
        return st.session_state[cache_key]

    comments = None
    used_demo = False
    error_message = None

    with st.spinner("Fetching and analyzing comments..."):

        try:
            comments = _fetch(platform_key, url)

        except Exception as e:
            error_message = str(e)

        if not comments:
            comments = get_demo_comments_rich()
            used_demo = True

        results = analyze_comments(comments)

        df = results_to_dataframe(results)

        texts = df["text"].tolist()

        # Per-comment emotions
        if classify_emotions and texts:

            try:
                labels = classify_emotions(texts)

                df["emotion"] = [
                    str(label).capitalize()
                    for label in labels
                ]

            except Exception:
                pass

        # Overall emotion percentages
        try:
            overall_emotions = analyze_emotions(texts) or {}

        except Exception:
            overall_emotions = {}

    data = {
        "df": df,
        "results": results,
        "emotions": overall_emotions,
        "used_demo": used_demo,
        "error": error_message,
    }

    st.session_state[cache_key] = data

    return data


# ----------------------------------------------------------------------
# HELPERS
# ----------------------------------------------------------------------

def _ago(ts) -> str:

    if ts is None or pd.isna(ts):
        return ""

    secs = (
        pd.Timestamp.now(tz="UTC") - ts
    ).total_seconds()

    if secs < 3600:
        return f"{max(1, int(secs // 60))}m"

    if secs < 86400:
        return f"{int(secs // 3600)}h"

    return f"{int(secs // 86400)}d"


def _top_keywords(texts: list[str], n: int = 12) -> pd.DataFrame:

    try:
        from sklearn.feature_extraction.text import CountVectorizer

        vec = CountVectorizer(
            stop_words="english",
            token_pattern=r"(?u)\b[^\W\d_]{3,}\b",
            max_features=200
        )

        counts = vec.fit_transform(texts).sum(axis=0).A1

        words = vec.get_feature_names_out()

        top = Counter(
            dict(zip(words, counts))
        ).most_common(n)

        return pd.DataFrame(
            top,
            columns=["word", "count"]
        )

    except Exception:
        return pd.DataFrame(
            columns=["word", "count"]
        )


def _feed_html(rows: pd.DataFrame) -> str:

    parts = []

    for i, (_, r) in enumerate(rows.iterrows()):

        color = AVATAR_COLORS[
            i % len(AVATAR_COLORS)
        ]

        author = (r.get("author") or "").strip()

        initial = (
            html.escape(author[:1].upper())
            if author else ""
        )

        text = html.escape(
            str(r["text"])[:220]
        )

        badge_color = SENT_COLORS.get(
            r["sentiment"],
            "#64748b"
        )

        meta = " · ".join(
            x for x in [
                html.escape(author),
                _ago(r["published_at"])
            ] if x
        )

        parts.append(
            f'<div class="comment-row">'
            f'<div class="comment-avatar" style="background:{color}">'
            f'{initial}</div>'
            f'<div style="flex:1">'
            f'<div class="comment-text">{text}</div>'
            f'<div class="comment-meta">{meta}'
            f'<span class="comment-badge" '
            f'style="background:{badge_color}">'
            f'{r["sentiment"]}</span>'
            f'</div></div>'
            f'<div class="comment-heart">'
            f'♡ {int(r["likes"])}</div></div>'
        )

    return "".join(parts)


def _back_button():

    if st.button(
        "← analyze another link",
        key="results_back"
    ):

        st.session_state.page = "select"
        st.session_state.platform = None

        st.rerun()


# ----------------------------------------------------------------------
# RESULTS PAGE
# ----------------------------------------------------------------------

def render_results_page(
    platform_key: str,
    url: str,
    platform_info: dict
):

    st.markdown(
        _CSS,
        unsafe_allow_html=True
    )

    accent = (
        platform_info["accent"]
        if platform_info else "#3ecf8e"
    )

    platform_name = (
        platform_info["name"]
        if platform_info else "Platform"
    )

    st.markdown(
        f'<div class="input-eyebrow" '
        f'style="--accent:{accent}; color:{accent};">'
        f'● analysis complete</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="input-title">Results</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        f'<div class="input-sub">{html.escape(url)}</div>',
        unsafe_allow_html=True
    )

    data = _load(platform_key, url)

    df = data["df"]
    results = data["results"]

    # Demo data warning
    if data["used_demo"]:

        st.warning(
            f"⚠ Live comment fetching wasn't available for this link "
            f"({data['error'] or 'no comments returned'}). "
            f"Showing demo data so you can still see how the analysis works."
        )

    # Empty data check
    if df.empty:

        st.info("No comments to analyze.")

        _back_button()

        return

    # ------------------------------------------------------------------
    # FILTERS
    # ------------------------------------------------------------------

    with st.container(border=True):

        f1, f2, f3, f4 = st.columns(
            [2.2, 1.6, 2.2, 1.6]
        )

        picked = f1.multiselect(
            "Sentiment",
            list(SENT_COLORS),
            default=list(SENT_COLORS)
        )

        min_conf = f2.slider(
            "Min confidence",
            0.0,
            1.0,
            0.0,
            0.05
        )

        query = f3.text_input(
            "Search comments",
            placeholder="e.g. audio, editing, ending"
        )

        sort_by = f4.selectbox(
            "Sort feed",
            [
                "Most liked",
                "Newest",
                "Most positive",
                "Most negative"
            ]
        )

    view = df[
        df["sentiment"].isin(picked)
        & (df["score"] >= min_conf)
    ]

    if query:

        view = view[
            view["text"].str.contains(
                query,
                case=False,
                na=False,
                regex=False
            )
        ]

    if view.empty:

        st.info("No comments match these filters.")

        _back_button()

        return

    # ------------------------------------------------------------------
    # KPI ROW
    # ------------------------------------------------------------------

    pos = (
        view["sentiment"] == "Positive"
    ).mean() * 100

    neg = (
        view["sentiment"] == "Negative"
    ).mean() * 100

    k1, k2, k3, k4, k5 = st.columns(5)

    k1.metric(
        "Comments",
        len(view),
        delta=f"of {len(df)}" if len(view) != len(df) else None,
        delta_color="off"
    )

    k2.metric(
        "Positive",
        f"{pos:.1f}%"
    )

    k3.metric(
        "Negative",
        f"{neg:.1f}%"
    )

    k4.metric(
        "Net sentiment",
        f"{pos - neg:+.1f}"
    )

    k5.metric(
        "Total likes",
        f"{int(view['likes'].sum()):,}"
    )

    # ------------------------------------------------------------------
    # SENTIMENT DONUT + EMOTIONS
    # ------------------------------------------------------------------

    c_left, c_right = st.columns(
        2,
        gap="large"
    )

    with c_left:

        with st.container(border=True):

            counts = (
                view["sentiment"]
                .value_counts()
                .reindex(
                    list(SENT_COLORS),
                    fill_value=0
                )
            )

            dominant = counts.idxmax()

            donut = go.Figure(
                go.Pie(
                    labels=counts.index,
                    values=counts.values,
                    hole=0.65,
                    sort=False,
                    marker=dict(
                        colors=[
                            SENT_COLORS[k]
                            for k in counts.index
                        ],
                        line=dict(
                            color="rgba(0,0,0,0)",
                            width=0
                        )
                    ),
                    textinfo="percent",
                    hovertemplate=(
                        "%{label}: %{value} comments "
                        "(%{percent})<extra></extra>"
                    )
                )
            )

            donut.add_annotation(
                text=SENT_FACES[dominant],
                showarrow=False,
                font=dict(size=40)
            )

            _style(
                donut,
                title="📊 Sentiment",
                height=320
            )

            st.plotly_chart(
                donut,
                width="stretch"
            )

    with c_right:

        with st.container(border=True):

            has_per_comment = (
                "emotion" in view.columns
                and view["emotion"].ne("Unknown").any()
            )

            if has_per_comment:

                emo = (
                    view["emotion"]
                    .value_counts(normalize=True)
                    .mul(100)
                    .round(1)
                    .rename_axis("emotion")
                    .reset_index(name="pct")
                    .sort_values("pct")
                )

                note = ""

            else:

                raw = data["emotions"]

                emo = pd.DataFrame(
                    [
                        (k.capitalize(), float(v))
                        for k, v in raw.items()
                    ],
                    columns=["emotion", "pct"]
                ).sort_values("pct")

                note = " (all comments)"

            bars = px.bar(
                emo,
                x="pct",
                y="emotion",
                orientation="h",
                text="pct",
                color="emotion",
                color_discrete_map=EMOTION_COLORS,
                title=f"❤️ Emotions{note}"
            )

            bars.update_traces(
                texttemplate="%{text}%",
                textposition="outside",
                cliponaxis=False
            )

            _style(
                bars,
                showlegend=False,
                xaxis_title=None,
                yaxis_title=None,
                height=320
            )

            bars.update_xaxes(
                range=[0, 110],
                showgrid=False,
                visible=False
            )

            st.plotly_chart(
                bars,
                width="stretch"
            )

    # ------------------------------------------------------------------
    # TIMELINE + KEYWORDS
    # ------------------------------------------------------------------

    t_left, t_right = st.columns(
        [3, 2],
        gap="large"
    )

    with t_left:

        with st.container(border=True):

            timed = view.dropna(
                subset=["published_at"]
            )

            if len(timed) >= 2:

                span = (
                    timed["published_at"].max()
                    - timed["published_at"].min()
                )

                freq = (
                    "h"
                    if span < pd.Timedelta(days=3)
                    else "D"
                )

                tl = timed.assign(
                    bucket=timed["published_at"].dt.floor(freq)
                )

                tl = (
                    tl.groupby(["bucket", "sentiment"])
                    .size()
                    .reset_index(name="comments")
                )

                fig = px.bar(
                    tl,
                    x="bucket",
                    y="comments",
                    color="sentiment",
                    color_discrete_map=SENT_COLORS,
                    title="📈 Sentiment over time"
                )

                _style(
                    fig,
                    xaxis_title=None,
                    yaxis_title=None,
                    legend_title=None,
                    height=320
                )

                st.plotly_chart(
                    fig,
                    width="stretch"
                )

            else:

                st.caption(
                    "Not enough dated comments for a timeline."
                )

    with t_right:

        with st.container(border=True):

            kw = _top_keywords(
                view["text"].tolist()
            )

            if not kw.empty:

                fig = px.bar(
                    kw.sort_values("count"),
                    x="count",
                    y="word",
                    orientation="h",
                    title="🔑 Top keywords"
                )

                fig.update_traces(
                    marker_color=accent
                )

                _style(
                    fig,
                    xaxis_title=None,
                    yaxis_title=None,
                    height=320
                )

                st.plotly_chart(
                    fig,
                    width="stretch"
                )

            else:

                st.caption(
                    "Not enough text for keywords."
                )

    # ------------------------------------------------------------------
    # COMMENT FEED
    # ------------------------------------------------------------------

    sorters = {
        "Most liked": ("likes", False),
        "Newest": ("published_at", False),
        "Most positive": ("polarity", False),
        "Most negative": ("polarity", True),
    }

    col, asc = sorters[sort_by]

    feed = (
        view.sort_values(
            col,
            ascending=asc,
            na_position="last"
        )
        .head(50)
    )

    with st.container(border=True):

        st.markdown(
            f"#### 💬 {platform_name} Comments"
        )

        with st.container(
            height=420,
            border=False
        ):

            st.markdown(
                _feed_html(feed),
                unsafe_allow_html=True
            )

    # ------------------------------------------------------------------
    # TOP COMMENT TABS
    # ------------------------------------------------------------------

    cols = [
        "text",
        "sentiment",
        "emotion",
        "score",
        "likes"
    ]

    tab1, tab2, tab3 = st.tabs(
        [
            "Most positive",
            "Most negative",
            "Most liked"
        ]
    )

    tab1.dataframe(
        view[
            view["sentiment"] == "Positive"
        ].nlargest(10, "polarity")[cols],
        hide_index=True,
        width="stretch"
    )

    tab2.dataframe(
        view[
            view["sentiment"] == "Negative"
        ].nsmallest(10, "polarity")[cols],
        hide_index=True,
        width="stretch"
    )

    tab3.dataframe(
        view.nlargest(10, "likes")[cols],
        hide_index=True,
        width="stretch"
    )

    # ------------------------------------------------------------------
    # OVERALL PERFORMANCE
    # ------------------------------------------------------------------

    st.markdown(
        f"### Overall performance: **{results['verdict']}**"
    )

    st.caption(
        f"Based on {results['total']} comments analyzed (any language)."
    )

    # ------------------------------------------------------------------
    # DOWNLOAD REPORTS - CSV + PDF
    # ------------------------------------------------------------------

    col_csv, col_pdf = st.columns(2)

    # CSV DOWNLOAD
    with col_csv:

        st.download_button(
            label="⬇ Download results (CSV)",
            data=view.to_csv(index=False).encode("utf-8"),
            file_name="sentio_results.csv",
            mime="text/csv",
            use_container_width=True,
        )

    # PDF DOWNLOAD
    with col_pdf:

        pdf_bytes = build_pdf_report(
            view,
            platform_name=platform_name,
            url=url,
            emotions=data["emotions"],
            keywords=list(
                kw.itertuples(
                    index=False,
                    name=None
                )
            ),
            used_demo=data["used_demo"],
            total_all=len(df),
        )

        st.download_button(
            label="📄 Download PDF Report",
            data=pdf_bytes,
            file_name="SentioAI_Report.pdf",
            mime="application/pdf",
            use_container_width=True,
        )

    # ------------------------------------------------------------------
    # BACK BUTTON
    # ------------------------------------------------------------------

    _back_button()
