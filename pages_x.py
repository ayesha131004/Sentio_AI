import re

from ui_kit import render_input_page

X_URL_PATTERN = re.compile(
    r"^https?://(www\.|mobile\.)?(x\.com|twitter\.com)/[A-Za-z0-9_]+/status/\d+(\S*)?$",
    re.IGNORECASE,
)


def render_x_input_page(x_platform):
    """Renders the X (Twitter) URL input screen.
    `x_platform` is the X entry from PLATFORMS in app.py."""
    render_input_page(
        platform=x_platform,
        key_prefix="x",
        pattern=X_URL_PATTERN,
        placeholder="https://x.com/username/status/1234567890",
        subtitle=(
            "Works with a single post. "
            "We'll pull the replies and quote posts underneath it and score the sentiment."
        ),
        formats=[
            ("x.com/…/status/", "https://x.com/"),
            ("twitter.com/…/status/", "https://twitter.com/"),
        ],
        empty_msg="Please paste an X link first.",
        invalid_msg=(
            "Invalid URL input — this doesn't look like a link to a single X post."
        ),
    )
