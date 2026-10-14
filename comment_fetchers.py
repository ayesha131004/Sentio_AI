"""
comment_fetchers.py
---------------------
One fetcher function per platform. YouTube works out of the box with a free
API key. Instagram is best-effort (public posts only — Instagram actively
blocks automated access, so failures here are expected, not a bug).
LinkedIn and X currently have no free public method to read comments on
arbitrary links, so those two intentionally raise a clear error explaining
why — results_page.py catches this and falls back to demo data.

Requires: pip install google-api-python-client instaloader
"""

import re


# ------------------------------------------------------------------
# YOUTUBE — works with a free YouTube Data API v3 key
# ------------------------------------------------------------------
def fetch_youtube_comments(url: str, api_key: str, max_comments: int = 100) -> list[str]:
    from googleapiclient.discovery import build

    video_id = _extract_youtube_id(url)
    if not video_id:
        raise ValueError("Could not extract a video ID from that YouTube URL.")

    youtube = build("youtube", "v3", developerKey=api_key)
    comments = []
    next_page_token = None

    while len(comments) < max_comments:
        request = youtube.commentThreads().list(
            part="snippet",
            videoId=video_id,
            maxResults=min(100, max_comments - len(comments)),
            order="relevance",
            textFormat="plainText",
            pageToken=next_page_token,
        )
        response = request.execute()
        for item in response.get("items", []):
            comments.append(item["snippet"]["topLevelComment"]["snippet"]["textDisplay"])
        next_page_token = response.get("nextPageToken")
        if not next_page_token:
            break

    return comments


def _extract_youtube_id(url: str):
    patterns = [
        r"youtube\.com/watch\?v=([A-Za-z0-9_\-]+)",
        r"youtube\.com/shorts/([A-Za-z0-9_\-]+)",
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
def fetch_instagram_comments(url: str, max_comments: int = 100) -> list[str]:
    import instaloader

    shortcode = _extract_instagram_shortcode(url)
    if not shortcode:
        raise ValueError("Could not extract a shortcode from that Instagram URL.")

    loader = instaloader.Instaloader()
    post = instaloader.Post.from_shortcode(loader.context, shortcode)

    comments = []
    for comment in post.get_comments():
        comments.append(comment.text)
        if len(comments) >= max_comments:
            break
    return comments


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


# ------------------------------------------------------------------
# X — reading replies now requires a paid API tier
# ------------------------------------------------------------------
def fetch_x_comments(url: str, max_comments: int = 100) -> list[str]:
    raise NotImplementedError(
        "X's API requires a paid developer plan to read replies. Add your "
        "own API credentials and call here once you have access."
    )


# ------------------------------------------------------------------
# DEMO DATA — used automatically if a real fetch fails, so the app
# always has something to analyze during a demo or presentation.
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
