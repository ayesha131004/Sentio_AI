import re
import time
import streamlit as st

YOUTUBE_URL_PATTERN = re.compile(
    r"^https?://(www\.)?(youtube\.com/(watch\?v=|shorts/)[A-Za-z0-9_\-]+|youtu\.be/[A-Za-z0-9_\-]+)(\S*)?$",
    re.IGNORECASE,
)


def render_youtube_input_page(yt_platform):
    """Renders the YouTube URL input screen.
    `yt_platform` is the YouTube entry from PLATFORMS in app.py (for its accent color)."""

    if st.button("← back to platforms", key="back_to_select"):
        st.session_state.page = "select"
        st.rerun()

    st.markdown(
        f"""
        <div class="input-eyebrow" style="--accent:{yt_platform['accent']}; color:{yt_platform['accent']};">
            ● youtube connected
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown('<div class="input-title">Paste your YouTube link</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="input-sub">Works with videos and Shorts only. '
        'We\'ll pull every comment underneath it and score the sentiment.</div>',
        unsafe_allow_html=True,
    )

    url = st.text_input(
        "YouTube URL",
        placeholder="https://www.youtube.com/watch?v=xxxxxxxxxxx",
        label_visibility="collapsed",
        key="yt_url_input",
    )

    st.markdown(
        """
        <div class="example-links">
            valid formats:<br>
            <code>youtube.com/watch?v=&lt;id&gt;</code><br>
            <code>youtube.com/shorts/&lt;id&gt;</code><br>
            <code>youtu.be/&lt;id&gt;</code>
        </div>
        """,
        unsafe_allow_html=True,
    )

    submit = st.button("Analyze this link", key="yt_submit")

    if submit:
        if not url.strip():
            st.markdown(
                '<div class="url-error">⚠ Please paste a YouTube link first.</div>',
                unsafe_allow_html=True,
            )
        elif not YOUTUBE_URL_PATTERN.match(url.strip()):
            st.markdown(
                '<div class="url-error">⚠ Invalid URL input — this doesn\'t look like a '
                'YouTube video or Shorts link.</div>',
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
