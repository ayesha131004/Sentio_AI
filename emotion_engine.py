"""
emotion_engine.py
-------------------
Second, separate model from sentiment_engine.py — sentiment (positive/
negative/neutral) and emotion (joy/sadness/anger/etc.) are different
classification tasks, so they use different models.

Note: this emotion model is English-focused. If most of your comments are
in other languages, the emotion breakdown will be less reliable than the
sentiment breakdown (which uses a multilingual model). Sentiment stays the
primary, trustworthy number; treat emotions as a secondary, rougher signal.

Requires: pip install transformers torch
"""

import streamlit as st

EMOTION_MODEL = "j-hartmann/emotion-english-distilroberta-base"

# The model outputs 7 emotions; we group them down to the 4 shown in the UI.
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


def analyze_emotions(comments: list[str]) -> dict:
    """Returns percentages for joy / neutral / sadness / anger across all comments."""

    comments = [c.strip() for c in comments if c and c.strip()]
    if not comments:
        return {"joy": 0.0, "neutral": 0.0, "sadness": 0.0, "anger": 0.0}

    clf = load_emotion_pipeline()
    truncated = [c[:512] for c in comments]
    raw_results = clf(truncated, truncation=True)

    totals = {"joy": 0, "neutral": 0, "sadness": 0, "anger": 0}
    for scores in raw_results:
        best = max(scores, key=lambda x: x["score"])
        group = GROUP_MAP.get(best["label"].lower(), "neutral")
        totals[group] += 1

    total_count = len(comments)
    return {k: round(v / total_count * 100, 1) for k, v in totals.items()}
