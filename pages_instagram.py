import re

from ui_kit import render_input_page

INSTAGRAM_URL_PATTERN = re.compile(
    r"^https?://(www\.)?instagram\.com/(p|reel|reels|tv)/[A-Za-z0-9_\-]+(\S*)?$",
    re.IGNORECASE,
)


def render_instagram_input_page(ig_platform):
    """Renders the Instagram URL input screen.
    `ig_platform` is the Instagram entry from PLATFORMS in app.py."""
    render_input_page(
        platform=ig_platform,
        key_prefix="ig",
        pattern=INSTAGRAM_URL_PATTERN,
        placeholder="https://www.instagram.com/reel/xxxxxxxxxxx/",
        subtitle=(
            "Works with public Reels and posts. "
            "We'll pull the comments, including replies, and score the sentiment."
        ),
        formats=[
            ("reel/", "https://www.instagram.com/reel/"),
            ("p/", "https://www.instagram.com/p/"),
            ("tv/", "https://www.instagram.com/tv/"),
        ],
        empty_msg="Please paste an Instagram link first.",
        invalid_msg=(
            "Invalid URL input — this doesn't look like an Instagram Reel or post link."
        ),
    )
