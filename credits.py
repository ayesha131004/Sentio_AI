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

NOTE: the "Activate" buttons are a DEMO checkout - they flip the account to
Pro without taking any payment. To charge real money, replace
`activate_pro()` with a call made after a successful Razorpay / Stripe payment.
"""

import streamlit as st

from auth import _connect, current_user, logout, AUTH_CSS

# ----------------------------------------------------------------------
# CONFIG - edit these freely
# ----------------------------------------------------------------------
FREE_CREDITS = 3

MONTHLY_PRICE = 499            # rupees per month
ANNUAL_PRICE = 4990            # rupees per year
ANNUAL_SAVING = MONTHLY_PRICE * 12 - ANNUAL_PRICE

# kept for backwards compatibility with older imports
PRO_PRICE_LABEL = f"₹{MONTHLY_PRICE:,}"
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
    ("Unlimited analyses", "No credit limits on YouTube or Instagram."),
    ("Every platform unlocked", "LinkedIn, X and Facebook, in addition to YouTube and Instagram."),
    ("Priority processing", "Your analyses are placed at the front of the queue."),
    ("Deeper insights", "Full per-comment sentiment and emotion breakdowns."),
    ("Priority support", "Faster assistance whenever something looks off."),
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

/* ---------------- account bar: one tidy row, buttons grouped on the right ---------------- */
.st-key-acct_bar { margin-bottom: 0.4rem; }
.st-key-acct_bar div[data-testid="stHorizontalBlock"] {
    align-items: center !important;
    flex-wrap: nowrap !important;
}
.st-key-acct_bar .user-bar {
    display: flex !important;
    align-items: center;
    justify-content: flex-start !important;
    flex-wrap: wrap;
    row-gap: 0.3rem;
    margin: 0 !important;
    min-height: 2.2rem;
    white-space: nowrap;
}
.st-key-acct_bar button {
    height: 2.2rem;
    min-height: 2.2rem;
    padding: 0 0.9rem;
    font-size: 0.85rem;
    line-height: 1;
    white-space: nowrap;
    width: 100%;
}
.st-key-acct_bar div[data-testid="stElementContainer"] { margin: 0 !important; }

/* "go pro" = the one accented button; "log out" = quiet ghost button on the far right */
.st-key-bar_upgrade button {
    background: linear-gradient(90deg, #4f8cff, #8b5cf6) !important;
    border: none !important;
    color: #ffffff !important;
    font-weight: 600;
}
.st-key-bar_upgrade button:hover { filter: brightness(1.1); }
.st-key-logout_btn button {
    background: transparent !important;
    border: 1px solid transparent !important;
    opacity: 0.75;
}
.st-key-logout_btn button:hover {
    border-color: var(--line, rgba(255,255,255,0.2)) !important;
    opacity: 1;
}

/* ---------------- Sentio AI Pro popup (narrow, vertical, formal) ---------------- */
div[data-testid="stDialog"] div[role="dialog"] {
    max-height: 92vh;
    overflow-y: auto;
}

.pro-lead {
    font-size: 1.05rem;
    font-weight: 600;
    line-height: 1.4;
    margin: 0.1rem 0 0.25rem;
}
.pro-sub {
    font-size: 0.85rem;
    opacity: 0.7;
    line-height: 1.5;
    margin-bottom: 0.9rem;
}
.pro-reason {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.76rem;
    color: var(--neutral);
    border: 1px solid rgba(232,178,77,0.4);
    background: rgba(232,178,77,0.08);
    border-radius: 8px;
    padding: 0.6rem 0.9rem;
    margin: 0 0 0.9rem;
    line-height: 1.5;
}

/* what is included */
.pro-section-label {
    font-size: 0.72rem;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    opacity: 0.55;
    margin: 0.2rem 0 0.35rem;
}
.benefit-row {
    display: flex;
    gap: 0.75rem;
    align-items: flex-start;
    padding: 0.5rem 0;
    border-bottom: 1px solid rgba(255,255,255,0.07);
}
.benefit-row:last-child { border-bottom: none; }
.benefit-check {
    flex: 0 0 1.35rem;
    width: 1.35rem;
    height: 1.35rem;
    margin-top: 1px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 0.72rem;
    font-weight: 700;
    color: #8fb4ff;
    background: rgba(99,140,255,0.15);
    border: 1px solid rgba(99,140,255,0.4);
}
.benefit-title { font-weight: 600; font-size: 0.9rem; line-height: 1.3; }
.benefit-desc { font-size: 0.78rem; opacity: 0.65; margin-top: 2px; line-height: 1.4; }

/* the two subscription cards */
.st-key-plan_monthly,
.st-key-plan_annual {
    border-radius: 14px !important;
    padding: 0.35rem 0.4rem 0.2rem !important;
    margin-top: 0.5rem;
}
.st-key-plan_monthly { border: 1px solid rgba(255,255,255,0.14) !important; }
.st-key-plan_annual {
    border: 2px solid transparent !important;
    background:
        linear-gradient(var(--bg-card, #0d1117), var(--bg-card, #0d1117)) padding-box,
        linear-gradient(135deg, #4f8cff, #8b5cf6) border-box !important;
}
.plan-head {
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 0.6rem;
}
.plan-name { font-size: 1rem; font-weight: 600; }
.plan-badge {
    font-size: 0.74rem;
    font-weight: 600;
    padding: 0.18rem 0.65rem;
    border-radius: 999px;
    color: #d9c8ff;
    background: rgba(139,92,246,0.22);
    white-space: nowrap;
}
.plan-price {
    display: flex;
    align-items: baseline;
    gap: 0.35rem;
    margin: 0.55rem 0 0.15rem;
}
.plan-amt { font-size: 2rem; font-weight: 700; line-height: 1; }
.plan-per { font-size: 0.88rem; opacity: 0.65; }
.plan-note { font-size: 0.8rem; opacity: 0.7; line-height: 1.45; margin-bottom: 0.4rem; }

.pro-terms {
    font-size: 0.72rem;
    opacity: 0.6;
    line-height: 1.5;
    text-align: center;
    margin-top: 0.9rem;
}
.demo-note {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.66rem;
    opacity: 0.7;
    text-align: center;
    margin-top: 0.4rem;
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

    with st.container(key="acct_bar"):
        left, mid, right = st.columns([7, 1.25, 1.25], vertical_alignment="center", gap="small")
        with left:
            st.markdown(
                f'<div class="user-bar">signed in as <b>{user}</b>{chips}</div>',
                unsafe_allow_html=True,
            )
        with mid:
            if acct["plan"] != "pro":
                if st.button("✦ go pro", key="bar_upgrade", use_container_width=True):
                    st.session_state.upgrade_reason = "manual"
                    st.rerun()
        with right:
            if st.button("log out", key="logout_btn", use_container_width=True):
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


def _finish_activation(cycle: str):
    activate_pro(current_user())
    st.session_state["pro_cycle"] = cycle
    st.session_state.pop("upgrade_reason_text", None)
    st.session_state.pop("upgrade_open", None)
    st.rerun()


def _upgrade_body():
    reason = st.session_state.get("upgrade_reason_text")

    st.markdown(
        '<div class="pro-lead">Choose your Sentio AI Pro plan</div>'
        '<div class="pro-sub">Understand your audience on every platform, without limits. '
        'Both plans include the full set of features below.</div>',
        unsafe_allow_html=True,
    )
    if reason:
        st.markdown(f'<div class="pro-reason">{reason}</div>', unsafe_allow_html=True)

    # --- what is included ---
    rows = "".join(
        f'<div class="benefit-row"><div class="benefit-check">✓</div>'
        f'<div><div class="benefit-title">{title}</div>'
        f'<div class="benefit-desc">{desc}</div></div></div>'
        for title, desc in PRO_BENEFITS
    )
    st.markdown(
        f'<div class="pro-section-label">What is included</div>{rows}',
        unsafe_allow_html=True,
    )

    # --- plan 1: monthly ---
    with st.container(border=True, key="plan_monthly"):
        st.markdown(
            f"""
            <div class="plan-head"><span class="plan-name">Monthly</span></div>
            <div class="plan-price">
                <span class="plan-amt">₹{MONTHLY_PRICE:,}</span><span class="plan-per">/ month</span>
            </div>
            <div class="plan-note">Billed every month. Cancel at any time.</div>
            """,
            unsafe_allow_html=True,
        )
        if st.button("Choose monthly", key="activate_monthly_btn", use_container_width=True):
            _finish_activation("monthly")

    # --- plan 2: annual (recommended) ---
    with st.container(border=True, key="plan_annual"):
        st.markdown(
            f"""
            <div class="plan-head">
                <span class="plan-name">Annual</span>
                <span class="plan-badge">Save ₹{ANNUAL_SAVING:,}</span>
            </div>
            <div class="plan-price">
                <span class="plan-amt">₹{ANNUAL_PRICE:,}</span><span class="plan-per">/ year</span>
            </div>
            <div class="plan-note">Works out to about ₹{round(ANNUAL_PRICE / 12):,} per month,
            billed once a year. Cancel at any time.</div>
            """,
            unsafe_allow_html=True,
        )
        if st.button("Choose annual", key="activate_annual_btn", type="primary", use_container_width=True):
            _finish_activation("annual")

    st.markdown(
        '<div class="pro-terms">Subscriptions renew automatically until cancelled.</div>'
        '<div class="demo-note">Demo checkout: no real payment is taken.</div>',
        unsafe_allow_html=True,
    )


_HAS_DIALOG = hasattr(st, "dialog")

if _HAS_DIALOG:

    # default width ("small") keeps the popup narrow and tall, like a plan sheet
    @st.dialog("Sentio AI Pro")
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
