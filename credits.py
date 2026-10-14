"""
credits.py
-----------
Credit system + "Sentio AI Pro" upgrade popup.

Rules
  * YouTube   -> 3 free trial credits per account (1 credit = 1 analysis)
  * Instagram -> 3 free credits per account
  * Facebook, LinkedIn, X -> Sentio AI Pro only
  * Pro plan  -> unlimited analyses on every platform

Credits and plan live in the same users.db as the login (see auth.py).

NOTE: the "Activate Pro" button is a DEMO checkout - it flips the account to
Pro without taking any payment. To charge real money, replace
`activate_pro()` with a call made after a successful Razorpay / Stripe payment.
"""

import streamlit as st

from auth import _connect, current_user, logout, AUTH_CSS

# ----------------------------------------------------------------------
# CONFIG - edit these freely
# ----------------------------------------------------------------------
FREE_CREDITS = 3
PRO_PRICE_LABEL = "₹499"       # shown on the popup
PRO_PRICE_PERIOD = "/ month"

CREDIT_COLUMN = {"youtube": "yt_credits", "instagram": "ig_credits"}
PRO_ONLY = {"facebook", "linkedin", "x"}
PLATFORM_NAMES = {
    "youtube": "YouTube",
    "instagram": "Instagram",
    "facebook": "Facebook",
    "linkedin": "LinkedIn",
    "x": "X",
}

PRO_BENEFITS = [
    ("∞", "Unlimited analyses", "No credit limits on YouTube or Instagram."),
    ("🔓", "Every platform unlocked", "LinkedIn, X and Facebook, on top of YouTube and Instagram."),
    ("⚡", "Priority processing", "Your analyses go to the front of the queue."),
    ("📊", "Deeper insights", "Full per-comment sentiment and emotion breakdowns."),
    ("💬", "Priority support", "Get help faster when something looks off."),
]


# ----------------------------------------------------------------------
# DATABASE HELPERS
# ----------------------------------------------------------------------
def get_account(username: str) -> dict:
    conn = _connect()
    try:
        row = conn.execute(
            "SELECT plan, yt_credits, ig_credits FROM users WHERE username = ?",
            (username,),
        ).fetchone()
    finally:
        conn.close()
    if row is None:
        return {"plan": "free", "youtube": 0, "instagram": 0}
    return {"plan": row[0], "youtube": row[1], "instagram": row[2]}


def is_pro(username: str) -> bool:
    return get_account(username)["plan"] == "pro"


def check_access(username: str, platform: str) -> tuple[bool, str | None]:
    """Returns (allowed, reason). reason is 'pro_only' or 'no_credits' when blocked."""
    acct = get_account(username)
    if acct["plan"] == "pro":
        return True, None
    if platform in PRO_ONLY:
        return False, "pro_only"
    if platform in CREDIT_COLUMN:
        if acct[platform] > 0:
            return True, None
        return False, "no_credits"
    return False, "pro_only"


def consume_credit(username: str, platform: str) -> bool:
    """Spends one credit atomically. Pro users are never charged.
    Returns True if the analysis may go ahead."""
    acct = get_account(username)
    if acct["plan"] == "pro":
        return True
    col = CREDIT_COLUMN.get(platform)
    if col is None:
        return False  # pro-only platform
    conn = _connect()
    try:
        cur = conn.execute(
            f"UPDATE users SET {col} = {col} - 1 WHERE username = ? AND {col} > 0",
            (username,),
        )
        conn.commit()
        return cur.rowcount == 1
    finally:
        conn.close()


def activate_pro(username: str):
    conn = _connect()
    try:
        conn.execute("UPDATE users SET plan = 'pro' WHERE username = ?", (username,))
        conn.commit()
    finally:
        conn.close()


# ----------------------------------------------------------------------
# UI: account bar (signed in as / plan / credits / upgrade / log out)
# ----------------------------------------------------------------------
BAR_CSS = """
<style>
.acct-chip {
    display: inline-block;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.68rem;
    padding: 0.12rem 0.55rem;
    border-radius: 20px;
    border: 1px solid var(--line);
    color: var(--text-dim);
    margin-left: 0.4rem;
}
.acct-chip.pro {
    color: #07110d;
    background: var(--positive);
    border-color: var(--positive);
    font-weight: 600;
}
.acct-chip.low { color: var(--neutral); border-color: var(--neutral); }
.acct-chip.empty { color: var(--negative); border-color: var(--negative); }
.pro-badge {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.66rem;
    margin-left: 0.4rem;
    color: var(--neutral);
    border: 1px solid var(--neutral);
    border-radius: 20px;
    padding: 0.15rem 0.55rem;
    display: inline-block;
}
.pro-hero { text-align: center; margin-bottom: 0.4rem; }
.pro-hero-title { font-size: 1.7rem; font-weight: 700; letter-spacing: -0.02em; }
.pro-hero-sub { font-size: 0.9rem; opacity: 0.7; margin-top: 0.3rem; line-height: 1.5; }
.pro-reason {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.78rem;
    color: var(--neutral);
    border: 1px solid rgba(232,178,77,0.4);
    background: rgba(232,178,77,0.08);
    border-radius: 8px;
    padding: 0.6rem 0.9rem;
    margin: 0.8rem 0;
}
.benefit-row {
    display: flex;
    gap: 0.8rem;
    align-items: flex-start;
    padding: 0.6rem 0;
    border-bottom: 1px solid rgba(255,255,255,0.08);
}
.benefit-row:last-child { border-bottom: none; }
.benefit-icon { font-size: 1.2rem; width: 1.8rem; text-align: center; flex-shrink: 0; }
.benefit-title { font-weight: 600; font-size: 0.92rem; }
.benefit-desc { font-size: 0.8rem; opacity: 0.65; margin-top: 1px; }
.price-box { text-align: center; margin: 1rem 0 0.4rem; }
.price-big { font-size: 2.2rem; font-weight: 700; }
.price-per { font-size: 0.9rem; opacity: 0.6; margin-left: 0.2rem; }
.demo-note {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.68rem;
    opacity: 0.55;
    text-align: center;
    margin-top: 0.5rem;
}
</style>
"""


def _credit_chip(label: str, n: int) -> str:
    cls = "empty" if n == 0 else ("low" if n == 1 else "")
    return f'<span class="acct-chip {cls}">{label} credits: {n}</span>'


def render_account_bar():
    """Replaces auth.render_user_bar(): signed-in user, plan, credits, upgrade + log out."""
    st.markdown(AUTH_CSS + BAR_CSS, unsafe_allow_html=True)
    user = current_user()
    acct = get_account(user)

    if acct["plan"] == "pro":
        chips = '<span class="acct-chip pro">SENTIO AI PRO</span>'
    else:
        chips = (
            '<span class="acct-chip">FREE</span>'
            + _credit_chip("YouTube", acct["youtube"])
            + _credit_chip("Instagram", acct["instagram"])
        )

    left, mid, right = st.columns([5, 1.3, 1])
    with left:
        st.markdown(
            f'<div class="user-bar" style="justify-content:flex-start;">'
            f'signed in as <b>{user}</b>{chips}</div>',
            unsafe_allow_html=True,
        )
    with mid:
        if acct["plan"] != "pro":
            if st.button("✦ go pro", key="bar_upgrade"):
                st.session_state.upgrade_reason = "manual"
                st.rerun()
    with right:
        if st.button("log out", key="logout_btn"):
            logout()


# ----------------------------------------------------------------------
# UI: Sentio AI Pro popup
# ----------------------------------------------------------------------
def _reason_text(reason: str | None, platform: str | None) -> str | None:
    name = PLATFORM_NAMES.get(platform or "", "")
    if reason == "pro_only":
        return f"🔒 {name} analysis is available on Sentio AI Pro only."
    if reason == "no_credits":
        return (
            f"You've used all {FREE_CREDITS} free {name} credits. "
            f"Upgrade to keep analyzing."
        )
    return None


def _upgrade_body():
    reason = st.session_state.get("upgrade_reason_text")

    st.markdown(
        """
        <div class="pro-hero">
            <div class="pro-hero-title">✦ Sentio AI Pro</div>
            <div class="pro-hero-sub">Understand your audience on every platform, without limits.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    if reason:
        st.markdown(f'<div class="pro-reason">{reason}</div>', unsafe_allow_html=True)

    rows = "".join(
        f'<div class="benefit-row"><div class="benefit-icon">{icon}</div>'
        f'<div><div class="benefit-title">{title}</div>'
        f'<div class="benefit-desc">{desc}</div></div></div>'
        for icon, title, desc in PRO_BENEFITS
    )
    st.markdown(rows, unsafe_allow_html=True)

    st.markdown(
        f'<div class="price-box"><span class="price-big">{PRO_PRICE_LABEL}</span>'
        f'<span class="price-per">{PRO_PRICE_PERIOD}</span></div>',
        unsafe_allow_html=True,
    )

    if st.button("Activate Sentio AI Pro", key="activate_pro_btn", type="primary", use_container_width=True):
        activate_pro(current_user())
        st.session_state.pop("upgrade_reason_text", None)
        st.session_state.pop("upgrade_open", None)
        st.rerun()

    st.markdown(
        '<div class="demo-note">Demo checkout: no real payment is taken.</div>',
        unsafe_allow_html=True,
    )


_HAS_DIALOG = hasattr(st, "dialog")

if _HAS_DIALOG:

    @st.dialog("Sentio AI Pro", width="large")
    def _upgrade_dialog():
        _upgrade_body()


def request_upgrade(reason: str | None = None, platform: str | None = None):
    """Call from anywhere, then st.rerun(): the popup opens on the next run."""
    st.session_state.upgrade_open = True
    st.session_state.upgrade_reason_text = _reason_text(reason, platform)


def show_upgrade_if_requested():
    """Call once per run from app.py, before the platform cards.
    Opens the Sentio AI Pro popup if one was requested."""
    # The "go pro" button in the account bar only sets upgrade_reason.
    if st.session_state.pop("upgrade_reason", None):
        request_upgrade()

    if not st.session_state.get("upgrade_open"):
        return

    if _HAS_DIALOG:
        st.session_state.upgrade_open = False  # one-shot: closing the popup keeps it closed
        _upgrade_dialog()
    else:
        # Older Streamlit without st.dialog: show the same content inline instead.
        with st.container(border=True):
            _upgrade_body()
            if st.button("Maybe later", key="upgrade_close"):
                st.session_state.upgrade_open = False
                st.rerun()
        st.stop()
