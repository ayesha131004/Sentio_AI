import re

from ui_kit import render_input_page

FACEBOOK_URL_PATTERN = re.compile(
    r"^https?://((www|m|web)\.)?(facebook\.com/\S+|fb\.watch/\S+)$",
    re.IGNORECASE,
)


def render_facebook_input_page(fb_platform):
    """Renders the Facebook URL input screen.
    `fb_platform` is the Facebook entry from PLATFORMS in app.py."""
    render_input_page(
        platform=fb_platform,
        key_prefix="fb",
        pattern=FACEBOOK_URL_PATTERN,
        placeholder="https://www.facebook.com/username/posts/xxxxxxxx",
        subtitle=(
            "Works with public posts, videos and Reels. "
            "We'll pull the comments underneath and score the sentiment."
        ),
        formats=[
            ("facebook.com/", "https://www.facebook.com/"),
            ("fb.watch/", "https://fb.watch/"),
        ],
        empty_msg="Please paste a Facebook link first.",
        invalid_msg=(
            "Invalid URL input — this doesn't look like a Facebook post, video or Reel link."
        ),
    )
