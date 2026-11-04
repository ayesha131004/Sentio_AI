"""
sentiment_engine.py
--------------------
One shared sentiment classifier used by every platform (YouTube, Instagram,
LinkedIn, X). Uses a multilingual model, so comments in different languages
are handled without a separate translation step.

Input can be either:
  * list[str]   (old behaviour)
  * list[dict]  (text, likes, published_at, author) from the *_rich fetchers

Output keeps the same keys as before, plus richer per_comment entries.
Use results_to_dataframe(results) to get a DataFrame for charts.

Requires: pip install transformers torch sentencepiece protobuf pandas
"""

import pandas as pd
import streamlit as st

MODEL_NAME = "cardiffnlp/twitter-xlm-roberta-base-sentiment"


@st.cache_resource(show_spinner="Loading sentiment model (first run only)...")
def load_sentiment_pipeline():
    from transformers import AutoModelForSequenceClassification, AutoTokenizer, pipeline

    # Try the fast tokenizer first; fall back to the slow one if conversion fails.
    try:
        tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    except Exception:
        tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME, use_fast=False)

    model = AutoModelForSequenceClassification.from_pretrained(MODEL_NAME)
    return pipeline(
        "sentiment-analysis",
        model=model,
        tokenizer=tokenizer,
        top_k=None,  # return the probability of every class, not just the top one
    )


def _normalize_label(raw_label: str) -> str:
    label = raw_label.lower()
    if "pos" in label or label == "label_2":
        return "positive"
    if "neg" in label or label == "label_0":
        return "negative"
    return "neutral"


@st.cache_data(show_spinner=False, ttl=3600)
def _classify(texts: tuple) -> list[dict]:
    """Returns one {positive, neutral, negative} probability dict per text.
    Cached, so re-running the app on the same comments is instant."""
    clf = load_sentiment_pipeline()
    raw = clf(list(texts), truncation=True, max_length=512, batch_size=16)

    out = []
    for item in raw:
        probs = {"positive": 0.0, "neutral": 0.0, "negative": 0.0}
        for entry in item:
            probs[_normalize_label(entry["label"])] += float(entry["score"])
        out.append(probs)
    return out


def _to_records(comments) -> list[dict]:
    """Accepts list[str] or list[dict] and returns clean list[dict]."""
    records = []
    for c in comments or []:
        if isinstance(c, dict):
            text = (c.get("text") or "").strip()
            if text:
                records.append({
                    "text": text,
                    "likes": int(c.get("likes", 0) or 0),
                    "published_at": c.get("published_at"),
                    "author": c.get("author", ""),
                })
        elif isinstance(c, str) and c.strip():
            records.append({"text": c.strip(), "likes": 0,
                            "published_at": None, "author": ""})
    return records


def _empty_result() -> dict:
    return {
        "total": 0, "positive": 0, "negative": 0, "neutral": 0,
        "positive_pct": 0.0, "negative_pct": 0.0, "neutral_pct": 0.0,
        "net_sentiment": 0.0, "avg_polarity": 0.0,
        "verdict": "No comments to analyze", "per_comment": [],
    }


def analyze_comments(comments) -> dict:
    """Runs sentiment analysis on comments (any language).
    Returns counts, percentages, an overall verdict, and per-comment results."""

    records = _to_records(comments)
    if not records:
        return _empty_result()

    texts = tuple(r["text"][:512] for r in records)
    probs_list = _classify(texts)

    counts = {"positive": 0, "negative": 0, "neutral": 0}
    per_comment = []

    for rec, probs in zip(records, probs_list):
        label = max(probs, key=probs.get)
        counts[label] += 1
        per_comment.append({
            **rec,
            "label": label,
            "score": round(probs[label], 3),  # confidence in the chosen label
            "polarity": round(probs["positive"] - probs["negative"], 3),  # -1 to +1
            "p_positive": round(probs["positive"], 3),
            "p_neutral": round(probs["neutral"], 3),
            "p_negative": round(probs["negative"], 3),
        })

    total = len(records)
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
        "net_sentiment": round(positive_pct - negative_pct, 1),
        "avg_polarity": round(sum(p["polarity"] for p in per_comment) / total, 3),
        "verdict": verdict,
        "per_comment": per_comment,
    }


def results_to_dataframe(results: dict) -> pd.DataFrame:
    """One row per comment, ready for the Plotly dashboard.
    Columns: text, sentiment, score, polarity, likes, published_at, author
    (plus emotion, if emotion_engine has added it to per_comment)."""
    rows = results.get("per_comment", [])
    cols = ["text", "sentiment", "score", "polarity", "likes", "published_at", "author"]
    if not rows:
        return pd.DataFrame(columns=cols + ["emotion"])

    df = pd.DataFrame(rows)
    df["sentiment"] = df["label"].str.capitalize()
    df["published_at"] = pd.to_datetime(df["published_at"], errors="coerce", utc=True)
    if "emotion" not in df:
        df["emotion"] = "Unknown"
    extra = [c for c in ("p_positive", "p_neutral", "p_negative") if c in df]
    return df[cols + ["emotion"] + extra]
