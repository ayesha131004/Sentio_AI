import re

from ui_kit import render_input_page

LINKEDIN_URL_PATTERN = re.compile(
    r"^https?://([a-z]{2,3}\.)?linkedin\.com/(posts/|feed/update/|jobs/view/|pulse/)\S+$",
    re.IGNORECASE,
)


def render_linkedin_input_page(li_platform):
    """Renders the LinkedIn URL input screen.
    `li_platform` is the LinkedIn entry from PLATFORMS in app.py."""
    render_input_page(
        platform=li_platform,
        key_prefix="li",
        pattern=LINKEDIN_URL_PATTERN,
        placeholder="https://www.linkedin.com/posts/your-post-link",
        subtitle=(
            "Works with a job posting or an update. "
            "We'll pull the reactions and comments and score the sentiment."
        ),
        formats=[
            ("posts/", "https://www.linkedin.com/posts/"),
            ("feed/update/", "https://www.linkedin.com/feed/update/"),
            ("jobs/view/", "https://www.linkedin.com/jobs/view/"),
        ],
        empty_msg="Please paste a LinkedIn link first.",
        invalid_msg=(
            "Invalid URL input — this doesn't look like a LinkedIn post or job link."
        ),
    )
