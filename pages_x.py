import re
import time
import streamlit as st

X_URL_PATTERN = re.compile(
    r"^https?://(www\.)?(twitter\.com|x\.com)/[A-Za-z0-9_]+/status/[0-9]+(\S*)?$",
    re.IGNORECASE,
)


def render_x_input_page(x_platform):
    """Renders the X (Twitter) URL input screen.
    `x_platform` is the X entry from PLATFORMS in app.py (for its accent color)."""

    if st.button("← back to platforms", key="back_to_select"):
        st.session_state.page = "select"
        st.rerun()

    st.markdown(
        f"""
        <div class="input-eyebrow" style="--accent:{x_platform['accent']}; color:{x_platform['accent']};">
            ● x connected
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown('<div class="input-title">Paste your X link</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="input-sub">Works with a single tweet\'s replies and quote posts. '
        'We\'ll pull every reply underneath it and score the sentiment.</div>',
        unsafe_allow_html=True,
    )

    url = st.text_input(
        "X URL",
        placeholder="https://x.com/username/status/xxxxxxxxxxx",
        label_visibility="collapsed",
        key="x_url_input",
    )

    st.markdown(
        """
        <div class="example-links">
            valid formats:<br>
            <code>x.com/&lt;user&gt;/status/&lt;id&gt;</code><br>
            <code>twitter.com/&lt;user&gt;/status/&lt;id&gt;</code>
        </div>
        """,
        unsafe_allow_html=True,
    )

    submit = st.button("Analyze this link", key="x_submit")

    if submit:
        if not url.strip():
            st.markdown(
                '<div class="url-error">⚠ Please paste an X link first.</div>',
                unsafe_allow_html=True,
            )
        elif not X_URL_PATTERN.match(url.strip()):
            st.markdown(
                '<div class="url-error">⚠ Invalid URL input — this doesn\'t look like an '
                'X (Twitter) post link.</div>',
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
