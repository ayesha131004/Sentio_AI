"""
ui_kit.py
----------
Shared "high-tech" input screen used by every platform page
(YouTube, Instagram, LinkedIn, X, Facebook).

Built on top of theme.py: it reuses its colour variables (so dark AND light mode
both work), its asset finder (assets/ folder or project root), its icons, its
md() helper and its .url-error / .chip styles. Everything new is prefixed hx-.

Each pages_<platform>.py only has to describe itself (URL pattern, placeholder,
example prefixes, messages) and call render_input_page(...).

Session-state behaviour is unchanged from the old pages:
  * "← back to platforms"  -> st.session_state.page = "select"
  * valid link + Analyze   -> st.session_state.analysis_url = <url>
                              st.session_state.page = "loading"
"""

import time

import streamlit as st

from theme import find_asset, image_to_data_uri, icon, keyed_container


# ----------------------------------------------------------------------
# small helpers
# ----------------------------------------------------------------------
def _flat(html: str) -> str:
    """Same trick as theme.md(): one line, so Markdown never sees a code block."""
    return " ".join(line.strip() for line in html.splitlines() if line.strip())


def _logo_html(platform: dict) -> str:
    name = platform.get("name", "")
    path = find_asset(platform.get("icon_base", "") or "")
    if path:
        try:
            return f'<img src="{image_to_data_uri(path)}" alt="{name}">'
        except Exception:
            pass
    return f'<span>{platform.get("icon", "●")}</span>'


def _credit_line(platform_key: str) -> str:
    """'Uses 1 credit · 2 left' for free users, 'unlimited' for Pro. Empty if unknown."""
    try:
        from auth import current_user
        from credits import get_account, CREDIT_COLUMN

        acct = get_account(current_user())
        if acct["plan"] == "pro":
            return "Sentio AI Pro · unlimited analyses"
        if platform_key in CREDIT_COLUMN:
            return f"Uses 1 credit · {acct[platform_key]} left"
    except Exception:
        pass
    return ""


def _fill(key: str, value: str):
    st.session_state[key] = value


_SIDE_CARDS = [
    ("chart", "Sentiment split", "The positive, neutral and negative share across every comment."),
    ("pulse", "Emotion breakdown", "Joy, anger, sadness and more, detected comment by comment."),
    ("chat", "Comment insights", "See how individual comments were scored and where the room stands."),
]

# ----------------------------------------------------------------------
# CSS. Selectors are deliberately specific so theme.py's global
# `.stButton > button` / `div[data-baseweb="input"]` rules cannot override them.
# ----------------------------------------------------------------------
_CSS = """
<style>
.st-key-hx_page {
    --hx: #6d8bff;
    --hx2: #8b5cf6;
    margin-top: 1.6rem;
}
.st-key-hx_page div[data-testid="stElementContainer"] { margin: 0; }

/* ---- roomier page: wider cap on this screen only, more air between the two columns ---- */
.block-container:has(.st-key-hx_page) { max-width: 1320px; padding-bottom: 5rem; }
.st-key-hx_page div[data-testid="stHorizontalBlock"]:not(.st-key-hx_chips *) { gap: 4rem; }
.st-key-hx_chips div[data-testid="stHorizontalBlock"] { gap: .8rem; }
@media (max-width: 960px) {
    .st-key-hx_page div[data-testid="stHorizontalBlock"]:not(.st-key-hx_chips *) { gap: 2.5rem; }
}

/* ---- progress steps ---- */
.hx-steps {
    display: flex; align-items: center; gap: .9rem; flex-wrap: wrap;
    font-family: var(--mono, ui-monospace, monospace);
    font-size: .76rem; letter-spacing: .1em; text-transform: uppercase;
    margin: 1.6rem 0 2.6rem;
}
.hx-step { display: flex; align-items: center; gap: .7rem; color: var(--text-dim, #8c97bd); opacity: .6; }
.hx-step.done, .hx-step.now { opacity: 1; }
.hx-step.now { color: var(--text, #eaf0ff); }
.hx-dot {
    width: 1.9rem; height: 1.9rem; border-radius: 50%;
    display: inline-flex; align-items: center; justify-content: center;
    border: 1px solid var(--line-strong, rgba(130,150,255,.32)); font-size: .74rem;
}
.hx-step.done .hx-dot { color: var(--positive, #2fe0a5); border-color: var(--positive, #2fe0a5); background: color-mix(in srgb, var(--positive, #2fe0a5) 14%, transparent); }
.hx-step.now .hx-dot {
    color: var(--hx); border-color: var(--hx);
    box-shadow: 0 0 14px color-mix(in srgb, var(--hx) 55%, transparent);
}
.hx-bar { flex: 0 0 3rem; height: 1px; background: linear-gradient(90deg, var(--line-strong, rgba(130,150,255,.32)), transparent); }

/* ---- hero ---- */
.hx-hero { display: flex; gap: 1.6rem; align-items: center; margin: 0 0 1.5rem; }
.hx-logo {
    position: relative; flex: 0 0 84px; width: 84px; height: 84px;
    border-radius: 24px; display: flex; align-items: center; justify-content: center;
    background: var(--bg-glass, rgba(14,20,46,.62));
    font-size: 1.6rem; color: var(--hx);
}
.hx-logo::before {
    content: ""; position: absolute; inset: -2px; border-radius: 22px; padding: 2px;
    background: conic-gradient(var(--hx), transparent 35%, var(--hx) 70%, transparent);
    -webkit-mask: linear-gradient(#000 0 0) content-box, linear-gradient(#000 0 0);
    -webkit-mask-composite: xor; mask-composite: exclude;
    animation: hx-spin 7s linear infinite;
}
.hx-logo img { width: 46px; height: 46px; object-fit: contain; border-radius: 11px; }
@keyframes hx-spin { to { transform: rotate(360deg); } }

.hx-eyebrow {
    display: inline-flex; align-items: center; gap: .5rem;
    font-family: var(--mono, ui-monospace, monospace);
    font-size: .74rem; letter-spacing: .14em; text-transform: uppercase;
    color: var(--hx); padding: .4rem 1rem; border-radius: 999px;
    border: 1px solid color-mix(in srgb, var(--hx) 42%, transparent);
    background: color-mix(in srgb, var(--hx) 10%, transparent);
}
.hx-pulse { width: 7px; height: 7px; border-radius: 50%; background: var(--hx); animation: hx-pulse 1.8s infinite; }
@keyframes hx-pulse {
    0%   { box-shadow: 0 0 0 0 color-mix(in srgb, var(--hx) 70%, transparent); }
    100% { box-shadow: 0 0 0 10px transparent; }
}
.hx-title {
    font-size: clamp(2.2rem, 4vw, 3.3rem); font-weight: 700;
    letter-spacing: -.03em; line-height: 1.12; margin: .9rem 0 0;
    color: var(--heading, #fff);
}
.hx-title em {
    font-style: normal;
    background: linear-gradient(90deg, var(--hx), var(--hx2));
    -webkit-background-clip: text; background-clip: text; color: transparent;
}
.hx-sub { font-size: 1.05rem; color: var(--text-dim, #8c97bd); line-height: 1.7; max-width: 44rem; margin: 0 0 2.4rem; }

/* ---- glass panel ---- */
.st-key-hx_panel {
    position: relative; overflow: hidden;
    border: 1px solid var(--line-strong, rgba(130,150,255,.32)); border-radius: 20px;
    background: var(--bg-glass, rgba(14,20,46,.62));
    -webkit-backdrop-filter: blur(12px); backdrop-filter: blur(12px);
    padding: 2.2rem 2.2rem 2rem;
    box-shadow: 0 28px 64px -36px color-mix(in srgb, var(--hx) 75%, transparent);
}
@media (max-width: 640px) { .st-key-hx_panel { padding: 1.4rem 1.2rem 1.3rem; } }
.st-key-hx_panel::before {
    content: ""; position: absolute; left: 0; right: 0; top: 0; height: 2px;
    background: linear-gradient(90deg, transparent, var(--hx), transparent);
}
.hx-label {
    font-family: var(--mono, ui-monospace, monospace);
    font-size: .76rem; letter-spacing: .14em; text-transform: uppercase;
    color: var(--text-dim, #8c97bd); margin: 0 0 .9rem;
}
.hx-chips-label { margin: 1.8rem 0 .9rem; }

/* ---- link input (beats theme.py's global input rules by specificity) ---- */
.st-key-hx_page .st-key-hx_input_wrap div[data-baseweb="input"] {
    border: 1px solid var(--line-strong, rgba(130,150,255,.32)) !important;
    border-radius: 14px !important;
}
.st-key-hx_page .st-key-hx_input_wrap div[data-baseweb="input"]:focus-within {
    border-color: var(--hx) !important;
    box-shadow: 0 0 0 3px color-mix(in srgb, var(--hx) 22%, transparent),
                0 0 28px color-mix(in srgb, var(--hx) 30%, transparent) !important;
}
.st-key-hx_page .st-key-hx_input_wrap div[data-baseweb="input"] input {
    height: 3.7rem; padding: 0 1.3rem !important; font-size: 1rem !important;
}

.hx-status {
    display: flex; align-items: center; gap: .6rem; min-height: 1.6rem;
    font-family: var(--mono, ui-monospace, monospace); font-size: .82rem; margin: .9rem 0 0;
}
.hx-status.ok   { color: var(--positive, #2fe0a5); }
.hx-status.warn { color: var(--warn, #f5b94d); }
.hx-status i { width: 7px; height: 7px; border-radius: 50%; background: currentColor; display: inline-block; box-shadow: 0 0 8px currentColor; }

/* ---- quick-fill chips ---- */
.st-key-hx_page .st-key-hx_chips .stButton > button {
    width: 100%; height: 2.7rem; min-height: 2.7rem; padding: 0 1rem;
    font-family: var(--mono, ui-monospace, monospace); font-size: .82rem;
    white-space: nowrap; border-radius: 999px;
    background: color-mix(in srgb, var(--hx) 8%, transparent) !important;
    border: 1px dashed color-mix(in srgb, var(--hx) 55%, transparent) !important;
    box-shadow: none;
}
.st-key-hx_page .st-key-hx_chips .stButton > button:hover {
    border-style: solid !important;
    background: color-mix(in srgb, var(--hx) 18%, transparent) !important;
    box-shadow: none;
}

/* ---- analyze button ---- */
.st-key-hx_page .st-key-hx_submit_wrap { margin-top: 2.2rem; }
.st-key-hx_page .st-key-hx_submit_wrap .stButton > button {
    position: relative; overflow: hidden; width: 100%;
    height: 3.8rem; min-height: 3.8rem; border: none !important; border-radius: 14px !important;
    background: linear-gradient(90deg, var(--hx), var(--hx2)) !important;
    box-shadow: 0 16px 36px -16px color-mix(in srgb, var(--hx) 85%, transparent) !important;
    transition: transform .15s, filter .15s;
}
.st-key-hx_page .st-key-hx_submit_wrap .stButton > button p {
    color: #fff !important; font-weight: 700; letter-spacing: .02em; font-size: 1.1rem;
}
.st-key-hx_page .st-key-hx_submit_wrap .stButton > button:hover { transform: translateY(-1px); filter: brightness(1.08); }
.st-key-hx_page .st-key-hx_submit_wrap .stButton > button::after {
    content: ""; position: absolute; top: 0; bottom: 0; width: 40%; left: -60%;
    background: linear-gradient(100deg, transparent, rgba(255,255,255,.3), transparent);
    animation: hx-shine 3.4s ease-in-out infinite;
}
@keyframes hx-shine { 0% { left: -60%; } 55%, 100% { left: 130%; } }

.hx-meta {
    font-family: var(--mono, ui-monospace, monospace); font-size: .8rem;
    color: var(--text-dim, #8c97bd); margin-top: 1.1rem; min-height: 1.2rem;
}

/* ---- loading ---- */
.hx-load {
    margin-top: 1.4rem; padding: 1.2rem 1.4rem; border-radius: 14px;
    border: 1px solid color-mix(in srgb, var(--hx) 40%, transparent);
    background: color-mix(in srgb, var(--hx) 8%, transparent);
}
.hx-load-row {
    display: flex; align-items: center; gap: .7rem;
    font-family: var(--mono, ui-monospace, monospace); font-size: .82rem; color: var(--text, #eaf0ff);
}
.hx-ring {
    width: 16px; height: 16px; border-radius: 50%;
    border: 2px solid color-mix(in srgb, var(--hx) 30%, transparent);
    border-top-color: var(--hx); animation: hx-spin .8s linear infinite;
}
.hx-track { height: 4px; border-radius: 4px; background: var(--track, rgba(255,255,255,.07)); margin-top: .75rem; overflow: hidden; }
.hx-fill { height: 100%; border-radius: 4px; background: linear-gradient(90deg, var(--hx), var(--hx2)); transition: width .6s ease; }

/* ---- side column ---- */
.hx-side-title {
    font-family: var(--mono, ui-monospace, monospace);
    font-size: .76rem; letter-spacing: .14em; text-transform: uppercase;
    color: var(--text-dim, #8c97bd); margin: .4rem 0 1.1rem;
}
.hx-side-title.hx-gap-top { margin-top: 2.2rem; }
.hx-card {
    display: flex; gap: 1.2rem; align-items: flex-start;
    padding: 1.5rem 1.6rem; margin-bottom: 1.1rem; border-radius: 18px;
    border: 1px solid var(--line, rgba(130,150,255,.16)); background: var(--bg-glass, rgba(14,20,46,.62));
    transition: transform .2s, border-color .2s;
}
.hx-card:hover { transform: translateX(3px); border-color: var(--hx); }
.hx-ico {
    flex: 0 0 3rem; width: 3rem; height: 3rem; border-radius: 14px;
    display: flex; align-items: center; justify-content: center; color: var(--hx);
    background: color-mix(in srgb, var(--hx) 14%, transparent);
    border: 1px solid color-mix(in srgb, var(--hx) 32%, transparent);
}
.hx-card-title { font-weight: 600; font-size: 1.02rem; line-height: 1.3; color: var(--text, #eaf0ff); }
.hx-card-desc { font-size: .9rem; color: var(--text-dim, #8c97bd); line-height: 1.6; margin-top: .35rem; }
.hx-models { display: flex; flex-wrap: wrap; gap: .7rem; }
.hx-model {
    font-family: var(--mono, ui-monospace, monospace); font-size: .74rem;
    padding: .4rem .9rem; border-radius: 999px; color: var(--text-dim, #8c97bd);
    border: 1px solid var(--line-strong, rgba(130,150,255,.32));
}
</style>
"""


def _steps_html() -> str:
    items = [("done", icon("check", 12), "Source"), ("now", "2", "Paste link"), ("", "3", "Analysis")]
    parts = []
    for i, (cls, sym, label) in enumerate(items):
        parts.append(f'<div class="hx-step {cls}"><span class="hx-dot">{sym}</span>{label}</div>')
        if i < len(items) - 1:
            parts.append('<span class="hx-bar"></span>')
    return '<div class="hx-steps">' + "".join(parts) + "</div>"


def _loading_html(msg: str, pct: int) -> str:
    return (
        f'<div class="hx-load"><div class="hx-load-row"><span class="hx-ring"></span>{msg}</div>'
        f'<div class="hx-track"><div class="hx-fill" style="width:{pct}%"></div></div></div>'
    )


def _error_html(message: str) -> str:
    return f'<div class="url-error">{icon("shield", 16)}<span>{message}</span></div>'


# ----------------------------------------------------------------------
# the shared page
# ----------------------------------------------------------------------
def render_input_page(
    *,
    platform: dict,
    key_prefix: str,
    pattern,
    placeholder: str,
    subtitle: str,
    formats: list,
    empty_msg: str,
    invalid_msg: str,
):
    """platform    the entry from PLATFORMS in app.py (name, accent, icon_base, key ...)
    key_prefix  short unique prefix for widget keys, e.g. "yt"
    pattern     compiled regex a valid link must match
    formats     [(chip label, text that the chip puts in the box), ...]"""
    accent = platform.get("accent", "#6d8bff")
    name = platform.get("name", "")
    pkey = platform.get("key", "")
    input_key = f"{key_prefix}_url_input"
    submit_key = f"{key_prefix}_submit"

    st.markdown(
        _CSS + f"<style>.st-key-hx_page{{--hx:{accent};}}</style>",
        unsafe_allow_html=True,
    )

    with keyed_container("hx_page"):
        if st.button("← back to platforms", key="back_to_select"):
            st.session_state.page = "select"
            st.rerun()

        st.markdown(_steps_html(), unsafe_allow_html=True)

        left, right = st.columns([1.6, 1], gap="large")

        # ------------------------------ left: hero + input ------------------------------
        with left:
            st.markdown(
                _flat(
                    f"""
                    <div class="hx-hero">
                        <div class="hx-logo">{_logo_html(platform)}</div>
                        <div>
                            <span class="hx-eyebrow"><span class="hx-pulse"></span>{name} connected</span>
                            <div class="hx-title">Paste your <em>{name}</em> link</div>
                        </div>
                    </div>
                    <div class="hx-sub">{subtitle}</div>
                    """
                ),
                unsafe_allow_html=True,
            )

            with keyed_container("hx_panel"):
                st.markdown('<div class="hx-label">Source link</div>', unsafe_allow_html=True)

                with keyed_container("hx_input_wrap"):
                    url = st.text_input(
                        f"{name} URL",
                        placeholder=placeholder,
                        label_visibility="collapsed",
                        key=input_key,
                    )

                clean = (url or "").strip()
                if clean and pattern.match(clean):
                    st.markdown(
                        f'<div class="hx-status ok"><i></i>Valid {name} link detected</div>',
                        unsafe_allow_html=True,
                    )
                elif clean:
                    st.markdown(
                        f'<div class="hx-status warn"><i></i>This does not look like a {name} link yet</div>',
                        unsafe_allow_html=True,
                    )
                else:
                    st.markdown('<div class="hx-status"></div>', unsafe_allow_html=True)

                st.markdown(
                    '<div class="hx-label hx-chips-label">Accepted formats · tap to start</div>',
                    unsafe_allow_html=True,
                )
                with keyed_container("hx_chips"):
                    cols = st.columns(len(formats))
                    for i, (label, example) in enumerate(formats):
                        with cols[i]:
                            st.button(
                                label,
                                key=f"{key_prefix}_fmt_{i}",
                                on_click=_fill,
                                args=(input_key, example),
                                use_container_width=True,
                            )

                with keyed_container("hx_submit_wrap"):
                    submit = st.button(
                        "Analyze this link",
                        key=submit_key,
                        type="primary",
                        use_container_width=True,
                    )

                st.markdown(
                    f'<div class="hx-meta">{_credit_line(pkey)}</div>',
                    unsafe_allow_html=True,
                )

                feedback = st.empty()

                if submit:
                    if not clean:
                        feedback.markdown(_error_html(empty_msg), unsafe_allow_html=True)
                    elif not pattern.match(clean):
                        feedback.markdown(_error_html(invalid_msg), unsafe_allow_html=True)
                    else:
                        for msg, pct in [("analyzing....", 33), ("1 sec....", 66), ("almost ready....", 100)]:
                            feedback.markdown(_loading_html(msg, pct), unsafe_allow_html=True)
                            time.sleep(1)
                        st.session_state.analysis_url = clean
                        st.session_state.page = "loading"
                        st.rerun()

        # ------------------------------ right: what you get ------------------------------
        with right:
            cards = "".join(
                f'<div class="hx-card"><div class="hx-ico">{icon(ico, 18)}</div>'
                f'<div><div class="hx-card-title">{title}</div>'
                f'<div class="hx-card-desc">{desc}</div></div></div>'
                for ico, title, desc in _SIDE_CARDS
            )
            st.markdown(
                _flat(
                    f"""
                    <div class="hx-side-title">What you'll get</div>
                    {cards}
                    <div class="hx-side-title hx-gap-top">Powered by</div>
                    <div class="hx-models">
                        <span class="hx-model">XLM-RoBERTa sentiment</span>
                        <span class="hx-model">DistilRoBERTa emotion</span>
                    </div>
                    """
                ),
                unsafe_allow_html=True,
            )
