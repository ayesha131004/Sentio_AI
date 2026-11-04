"""
comment_fetchers.py
---------------------
One fetcher function per platform.

Two flavours of each fetcher:
  * fetch_xxx_comments(...)       -> list[str]   (old behaviour, unchanged)
  * fetch_xxx_comments_rich(...)  -> list[dict]  (text, likes, published_at, author)

YouTube works with a free API key. Instagram is best-effort (public posts
only). LinkedIn and X have no free public method, so they raise a clear error
and results_page.py falls back to demo data.

Requires: pip install google-api-python-client instaloader
"""

import random
import re
from datetime import datetime, timedelta, timezone


# ------------------------------------------------------------------
# YOUTUBE
# ------------------------------------------------------------------
def fetch_youtube_comments_rich(url: str, api_key: str, max_comments: int = 100) -> list[dict]:
    from googleapiclient.discovery import build

    video_id = _extract_youtube_id(url)
    if not video_id:
        raise ValueError("Could not extract a video ID from that YouTube URL.")

    youtube = build("youtube", "v3", developerKey=api_key)
    comments: list[dict] = []
    next_page_token = None

    while len(comments) < max_comments:
        response = youtube.commentThreads().list(
            part="snippet",
            videoId=video_id,
            maxResults=max(1, min(100, max_comments - len(comments))),
            order="relevance",
            textFormat="plainText",
            pageToken=next_page_token,
        ).execute()

        for item in response.get("items", []):
            s = item["snippet"]["topLevelComment"]["snippet"]
            comments.append({
                "text": s.get("textDisplay", ""),
                "likes": int(s.get("likeCount", 0) or 0),
                "published_at": s.get("publishedAt"),
                "author": s.get("authorDisplayName", ""),
            })

        next_page_token = response.get("nextPageToken")
        if not next_page_token:
            break

    return comments


def fetch_youtube_comments(url: str, api_key: str, max_comments: int = 100) -> list[str]:
    return [c["text"] for c in fetch_youtube_comments_rich(url, api_key, max_comments)]


def _extract_youtube_id(url: str):
    patterns = [
        r"youtube\.com/watch\?(?:.*&)?v=([A-Za-z0-9_\-]+)",
        r"youtube\.com/shorts/([A-Za-z0-9_\-]+)",
        r"youtube\.com/live/([A-Za-z0-9_\-]+)",
        r"youtube\.com/embed/([A-Za-z0-9_\-]+)",
        r"youtu\.be/([A-Za-z0-9_\-]+)",
    ]
    for pat in patterns:
        m = re.search(pat, url)
        if m:
            return m.group(1)
    return None


# ------------------------------------------------------------------
# INSTAGRAM — best-effort, public posts only, no login
# ------------------------------------------------------------------
def fetch_instagram_comments_rich(url: str, max_comments: int = 100) -> list[dict]:
    import instaloader

    shortcode = _extract_instagram_shortcode(url)
    if not shortcode:
        raise ValueError("Could not extract a shortcode from that Instagram URL.")

    loader = instaloader.Instaloader()
    post = instaloader.Post.from_shortcode(loader.context, shortcode)

    comments: list[dict] = []
    for c in post.get_comments():
        created = getattr(c, "created_at_utc", None)
        owner = getattr(c, "owner", None)
        comments.append({
            "text": c.text,
            "likes": int(getattr(c, "likes_count", 0) or 0),
            "published_at": created.replace(tzinfo=timezone.utc).isoformat() if created else None,
            "author": getattr(owner, "username", "") if owner else "",
        })
        if len(comments) >= max_comments:
            break
    return comments


def fetch_instagram_comments(url: str, max_comments: int = 100) -> list[str]:
    return [c["text"] for c in fetch_instagram_comments_rich(url, max_comments)]


def _extract_instagram_shortcode(url: str):
    m = re.search(r"instagram\.com/(?:reel|reels|p)/([A-Za-z0-9_\-]+)", url)
    return m.group(1) if m else None


# ------------------------------------------------------------------
# LINKEDIN — no free public API for reading comments on arbitrary posts
# ------------------------------------------------------------------
def fetch_linkedin_comments(url: str, max_comments: int = 100) -> list[str]:
    raise NotImplementedError(
        "LinkedIn does not provide public API access to comments on job "
        "posts or updates for third-party apps. This is a platform "
        "restriction, not a bug in this code."
    )


def fetch_linkedin_comments_rich(url: str, max_comments: int = 100) -> list[dict]:
    return fetch_linkedin_comments(url, max_comments)


# ------------------------------------------------------------------
# X — reading replies now requires a paid API tier
# ------------------------------------------------------------------
def fetch_x_comments(url: str, max_comments: int = 100) -> list[str]:
    raise NotImplementedError(
        "X's API requires a paid developer plan to read replies. Add your "
        "own API credentials and call here once you have access."
    )


def fetch_x_comments_rich(url: str, max_comments: int = 100) -> list[dict]:
    return fetch_x_comments(url, max_comments)


# ------------------------------------------------------------------
# DEMO DATA — used automatically if a real fetch fails.
# ------------------------------------------------------------------
DEMO_COMMENTS = [
    "This is amazing, I loved every second of it!",
    "Not what I expected, kind of disappointing.",
    "It's okay I guess, nothing special.",
    "Best content I've seen all week!",
    "Waste of time honestly.",
    "Pretty good, would watch again.",
    "Meh, could be better.",
    "This changed my perspective completely, thank you!",
    "I don't really have an opinion on this.",
    "Terrible quality, expected way better.",
    "Absolutely loved this, sharing with everyone!",
    "Underwhelming to say the least.",
    "Solid effort, a few rough edges though.",
    "Ce contenu est incroyable, bravo !",
    "No me gustó para nada, muy aburrido.",
]


def get_demo_comments_rich(seed: int = 7) -> list[dict]:
    """Demo comments with fake likes/dates so every chart still renders."""
    rng = random.Random(seed)
    now = datetime.now(timezone.utc)
    return [
        {
            "text": text,
            "likes": rng.randint(0, 250),
            "published_at": (now - timedelta(hours=rng.randint(1, 24 * 14))).isoformat(),
            "author": f"demo_user_{i + 1}",
        }
        for i, text in enumerate(DEMO_COMMENTS)
    ]
