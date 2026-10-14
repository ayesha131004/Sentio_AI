import re
import time
import streamlit as st

FACEBOOK_URL_PATTERN = re.compile(
    r"^https?://(www\.)?(facebook\.com/([\w.\-]+/(posts|videos)/[A-Za-z0-9]+|watch/?\?v=[0-9]+|reel/[0-9]+)|fb\.watch/[A-Za-z0-9_\-]+)/?(\?.*)?$",
    re.IGNORECASE,
)


def render_facebook_input_page(fb_platform):
    """Renders the Facebook URL input screen.
    `fb_platform` is the Facebook entry from PLATFORMS in app.py (for its accent color)."""

    if st.button("← back to platforms", key="back_to_select"):
        st.session_state.page = "select"
        st.rerun()

    st.markdown(
        f"""
        <div class="input-eyebrow" style="--accent:{fb_platform['accent']}; color:{fb_platform['accent']};">
            ● facebook connected
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown('<div class="input-title">Paste your Facebook link</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="input-sub">Works with posts, videos, and Reels only. '
        'We\'ll pull every comment underneath it and score the sentiment.</div>',
        unsafe_allow_html=True,
    )

    url = st.text_input(
        "Facebook URL",
        placeholder="Paste your facebook link here ",
        label_visibility="collapsed",
        key="fb_url_input",
    )

    st.markdown(
        """
        <div class="example-links">
         only facebook post, video and reel links are valid!
           
        </div>
        """,
        unsafe_allow_html=True,
    )

    submit = st.button("Analyze this link", key="fb_submit")

    if submit:
        if not url.strip():
            st.markdown(
                '<div class="url-error">⚠ Please paste a Facebook link first.</div>',
                unsafe_allow_html=True,
            )
        elif not FACEBOOK_URL_PATTERN.match(url.strip()):
            st.markdown(
                '<div class="url-error">⚠ Invalid URL input — this doesn\'t look like a '
                'Facebook post, video, or Reel link.</div>',
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
