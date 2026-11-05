import re

from ui_kit import render_input_page

YOUTUBE_URL_PATTERN = re.compile(
    r"^https?://(www\.)?(youtube\.com/(watch\?v=|shorts/)[A-Za-z0-9_\-]+|youtu\.be/[A-Za-z0-9_\-]+)(\S*)?$",
    re.IGNORECASE,
)


def render_youtube_input_page(yt_platform):
    """Renders the YouTube URL input screen.
    `yt_platform` is the YouTube entry from PLATFORMS in app.py (for its accent color)."""
    render_input_page(
        platform=yt_platform,
        key_prefix="yt",
        pattern=YOUTUBE_URL_PATTERN,
        placeholder="https://www.youtube.com/watch?v=xxxxxxxxxxx",
        subtitle=(
            "Works with videos and Shorts only. "
            "We'll pull every comment underneath it and score the sentiment."
        ),
        formats=[
            ("watch?v=", "https://www.youtube.com/watch?v="),
            ("shorts/", "https://www.youtube.com/shorts/"),
            ("youtu.be/", "https://youtu.be/"),
        ],
        empty_msg="Please paste a YouTube link first.",
        invalid_msg=(
            "Invalid URL input — this doesn't look like a YouTube video or Shorts link."
        ),
    )
