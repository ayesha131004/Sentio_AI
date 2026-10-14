"""
sentiment_engine.py
--------------------
One shared sentiment classifier used by every platform (YouTube, Instagram,
LinkedIn, X). Uses a multilingual model, so comments in different languages
are handled without needing a separate translation step first.

Requires: pip install transformers torch
"""

import streamlit as st


@st.cache_resource(show_spinner="Loading sentiment model (first run only)...")
def load_sentiment_pipeline():
    from transformers import pipeline
    return pipeline(
        "sentiment-analysis",
        model="cardiffnlp/twitter-xlm-roberta-base-sentiment",
        tokenizer="cardiffnlp/twitter-xlm-roberta-base-sentiment",
    )


def _normalize_label(raw_label: str) -> str:
    label = raw_label.lower()
    if "pos" in label or label == "label_2":
        return "positive"
    if "neg" in label or label == "label_0":
        return "negative"
    return "neutral"


def analyze_comments(comments: list[str]) -> dict:
    """Runs sentiment analysis on a list of comment strings (any language).
    Returns counts, percentages, an overall verdict, and per-comment results."""

    comments = [c.strip() for c in comments if c and c.strip()]

    if not comments:
        return {
            "total": 0,
            "positive": 0,
            "negative": 0,
            "neutral": 0,
            "positive_pct": 0.0,
            "negative_pct": 0.0,
            "neutral_pct": 0.0,
            "verdict": "No comments to analyze",
            "per_comment": [],
        }

    clf = load_sentiment_pipeline()

    # Most sentiment models cap input length — truncate defensively.
    truncated = [c[:512] for c in comments]
    raw_results = clf(truncated, truncation=True)

    counts = {"positive": 0, "negative": 0, "neutral": 0}
    per_comment = []

    for comment, res in zip(comments, raw_results):
        label = _normalize_label(res["label"])
        counts[label] += 1
        per_comment.append(
            {"text": comment, "label": label, "score": round(res["score"], 3)}
        )

    total = len(comments)
    positive_pct = round(counts["positive"] / total * 100, 1)
    negative_pct = round(counts["negative"] / total * 100, 1)
    neutral_pct = round(counts["neutral"] / total * 100, 1)

    if positive_pct >= 55:
        verdict = "Overwhelmingly Positive"
    elif negative_pct >= 55:
        verdict = "Overwhelmingly Negative"
    elif positive_pct > negative_pct:
        verdict = "Mostly Positive"
    elif negative_pct > positive_pct:
        verdict = "Mostly Negative"
    else:
        verdict = "Mixed / Neutral"

    return {
        "total": total,
        "positive": counts["positive"],
        "negative": counts["negative"],
        "neutral": counts["neutral"],
        "positive_pct": positive_pct,
        "negative_pct": negative_pct,
        "neutral_pct": neutral_pct,
        "verdict": verdict,
        "per_comment": per_comment,
    }
