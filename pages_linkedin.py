import re
import time
import streamlit as st

LINKEDIN_URL_PATTERN = re.compile(
    r"^https?://(www\.)?linkedin\.com/(jobs/view/[A-Za-z0-9_\-]+|posts/[A-Za-z0-9_\-]+|feed/update/[A-Za-z0-9:_\-]+)/?(\?.*)?$",
    re.IGNORECASE,
)


def render_linkedin_input_page(li_platform):
    """Renders the LinkedIn URL input screen.
    `li_platform` is the LinkedIn entry from PLATFORMS in app.py (for its accent color)."""

    if st.button("← back to platforms", key="back_to_select"):
        st.session_state.page = "select"
        st.rerun()

    st.markdown(
        f"""
        <div class="input-eyebrow" style="--accent:{li_platform['accent']}; color:{li_platform['accent']};">
            ● linkedin connected
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown('<div class="input-title">Paste your LinkedIn link</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="input-sub">Works with job postings and post updates only. '
        'We\'ll pull every comment underneath it and score the sentiment.</div>',
        unsafe_allow_html=True,
    )

    url = st.text_input(
        "LinkedIn URL",
        placeholder="https://www.linkedin.com/jobs/view/xxxxxxxxxx",
        label_visibility="collapsed",
        key="li_url_input",
    )

    st.markdown(
        """
        <div class="example-links">
            valid formats:<br>
            <code>linkedin.com/jobs/view/&lt;id&gt;</code><br>
            <code>linkedin.com/posts/&lt;id&gt;</code><br>
            <code>linkedin.com/feed/update/&lt;id&gt;</code>
        </div>
        """,
        unsafe_allow_html=True,
    )

    submit = st.button("Analyze this link", key="li_submit")

    if submit:
        if not url.strip():
            st.markdown(
                '<div class="url-error">⚠ Please paste a LinkedIn link first.</div>',
                unsafe_allow_html=True,
            )
        elif not LINKEDIN_URL_PATTERN.match(url.strip()):
            st.markdown(
                '<div class="url-error">⚠ Invalid URL input — this doesn\'t look like a '
                'LinkedIn job posting or update link.</div>',
                unsafe_allow_html=True,
            )
        else:
            status = st.empty()
            for msg in ["analyzing....", "1 sec....", "almost ready...."]:
                status.markdown(
                    f'<div class="loading-line"><span class="mini-spinner"></span> {msg}</div>',
                    unsafe_allow_html=True,
                )
                time.sleep(1)
            st.session_state.analysis_url = url.strip()
            st.session_state.page = "loading"
            st.rerun()
