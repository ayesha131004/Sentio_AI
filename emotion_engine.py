"""
emotion_engine.py
-------------------
Second, separate model from sentiment_engine.py. Sentiment (positive/
negative/neutral) and emotion (joy/sadness/anger/etc.) are different
classification tasks, so they use different models.

Functions:
  * classify_emotions(texts) -> list[str]   one of 7 emotion labels per text,
                                            same length and order as the input
  * analyze_emotions(texts)  -> dict        grouped percentages (joy / neutral /
                                            sadness / anger), unchanged API

Note: this emotion model is English-focused. For comments in other languages
the emotion result is a rougher signal than the multilingual sentiment result.

Requires: pip install transformers torch
"""

import streamlit as st

EMOTION_MODEL = "j-hartmann/emotion-english-distilroberta-base"

# The model's 7 labels, used as-is for per-comment results.
EMOTIONS = ["joy", "surprise", "neutral", "sadness", "fear", "anger", "disgust"]

# Grouping used only by analyze_emotions (the 4-bar summary).
GROUP_MAP = {
    "joy": "joy",
    "surprise": "joy",
    "neutral": "neutral",
    "sadness": "sadness",
    "fear": "sadness",
    "anger": "anger",
    "disgust": "anger",
}


@st.cache_resource(show_spinner="Loading emotion model (first run only)...")
def load_emotion_pipeline():
    from transformers import pipeline
    return pipeline("text-classification", model=EMOTION_MODEL, top_k=None)


@st.cache_data(show_spinner=False, ttl=3600)
def _classify_cached(texts: tuple) -> list[str]:
    """One emotion label per text. Cached, so filter changes and repeated
    calls on the same comments never re-run the model."""
    labels = ["neutral"] * len(texts)

    # Only send non-empty texts to the model, but keep original positions.
    idx = [i for i, t in enumerate(texts) if t and t.strip()]
    if not idx:
        return labels

    clf = load_emotion_pipeline()
    batch = [texts[i][:512] for i in idx]
    raw = clf(batch, truncation=True, max_length=512, batch_size=16)

    for i, scores in zip(idx, raw):
        best = max(scores, key=lambda x: x["score"])
        label = best["label"].lower()
        labels[i] = label if label in EMOTIONS else "neutral"
    return labels


def classify_emotions(comments) -> list[str]:
    """Returns one emotion label per comment, same length and order as the
    input (empty comments get 'neutral'). Accepts list[str] or list[dict]."""
    texts = tuple(
        (c.get("text", "") if isinstance(c, dict) else str(c or "")) for c in (comments or [])
    )
    if not texts:
        return []
    return _classify_cached(texts)


def analyze_emotions(comments) -> dict:
    """Returns percentages for joy / neutral / sadness / anger across all comments."""
    labels = classify_emotions(comments)
    if not labels:
        return {"joy": 0.0, "neutral": 0.0, "sadness": 0.0, "anger": 0.0}

    totals = {"joy": 0, "neutral": 0, "sadness": 0, "anger": 0}
    for label in labels:
        totals[GROUP_MAP.get(label, "neutral")] += 1

    n = len(labels)
    return {k: round(v / n * 100, 1) for k, v in totals.items()}
