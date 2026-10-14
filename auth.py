"""
auth.py
--------
Login / sign-up for Sentio AI. Users are stored in a local SQLite file
(users.db, created automatically next to this file). Passwords are never
stored in plain text: each one is salted and hashed with PBKDF2-SHA256.

Usage in app.py:
    from auth import require_login, render_user_bar
    require_login()      # shows the login page and stops the script if not logged in
    (the account bar itself lives in credits.render_account_bar)
"""

import hashlib
import hmac
import os
import re
import secrets
import sqlite3
import time

import streamlit as st

from theme import md, icon, brand_lockup, columns, error_box

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "users.db")

PBKDF2_ITERATIONS = 200_000
USERNAME_PATTERN = re.compile(r"^[A-Za-z0-9_.\-]{3,30}$")
MIN_PASSWORD_LENGTH = 8

MAX_FAILED_ATTEMPTS = 5
LOCKOUT_SECONDS = 30


# ----------------------------------------------------------------------
# DATABASE
# ----------------------------------------------------------------------
def _connect() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE COLLATE NOCASE,
            salt TEXT NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    # Lightweight migration: add credit/plan columns to databases created before
    # the credit system existed (existing users get the default free credits).
    existing = {row[1] for row in conn.execute("PRAGMA table_info(users)")}
    migrations = {
        "plan": "TEXT NOT NULL DEFAULT 'free'",
        "yt_credits": "INTEGER NOT NULL DEFAULT 3",
        "ig_credits": "INTEGER NOT NULL DEFAULT 3",
    }
    for col, ddl in migrations.items():
        if col not in existing:
            conn.execute(f"ALTER TABLE users ADD COLUMN {col} {ddl}")
    conn.commit()
    return conn


def _hash_password(password: str, salt: bytes) -> str:
    return hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"), salt, PBKDF2_ITERATIONS
    ).hex()


def register_user(username: str, password: str) -> tuple[bool, str]:
    """Creates a new user. Returns (ok, message)."""
    username = username.strip()

    if not USERNAME_PATTERN.match(username):
        return False, "Username must be 3-30 characters: letters, numbers, . _ - only."
    if len(password) < MIN_PASSWORD_LENGTH:
        return False, f"Password must be at least {MIN_PASSWORD_LENGTH} characters."

    salt = secrets.token_bytes(16)
    pw_hash = _hash_password(password, salt)

    conn = _connect()
    try:
        conn.execute(
            "INSERT INTO users (username, salt, password_hash) VALUES (?, ?, ?)",
            (username, salt.hex(), pw_hash),
        )
        conn.commit()
    except sqlite3.IntegrityError:
        return False, "That username is already taken."
    finally:
        conn.close()

    return True, "Account created."


def user_exists(username: str) -> bool:
    conn = _connect()
    try:
        row = conn.execute(
            "SELECT 1 FROM users WHERE username = ?", (username.strip(),)
        ).fetchone()
    finally:
        conn.close()
    return row is not None


def verify_user(username: str, password: str) -> str | None:
    """Returns the canonical username if credentials are correct, else None."""
    conn = _connect()
    try:
        row = conn.execute(
            "SELECT username, salt, password_hash FROM users WHERE username = ?",
            (username.strip(),),
        ).fetchone()
    finally:
        conn.close()

    if row is None:
        # Hash anyway so a wrong username takes about as long as a wrong password.
        _hash_password(password, b"\x00" * 16)
        return None

    stored_username, salt_hex, stored_hash = row
    candidate = _hash_password(password, bytes.fromhex(salt_hex))
    if hmac.compare_digest(candidate, stored_hash):
        return stored_username
    return None


# ----------------------------------------------------------------------
# SESSION HELPERS
# ----------------------------------------------------------------------
def is_logged_in() -> bool:
    return bool(st.session_state.get("auth_user"))


def current_user() -> str | None:
    return st.session_state.get("auth_user")


def logout():
    # Clear everything so no previous user's data (platform, URL, IG session) leaks over.
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.rerun()


def _lockout_remaining() -> int:
    locked_until = st.session_state.get("auth_locked_until", 0)
    return max(0, int(locked_until - time.time()))


def _register_failed_attempt():
    st.session_state.auth_failed = st.session_state.get("auth_failed", 0) + 1
    if st.session_state.auth_failed >= MAX_FAILED_ATTEMPTS:
        st.session_state.auth_locked_until = time.time() + LOCKOUT_SECONDS
        st.session_state.auth_failed = 0


# ----------------------------------------------------------------------
# UI  (all styling lives in theme.py)
# ----------------------------------------------------------------------
AUTH_CSS = ""  # kept so older imports (credits.py) don't break


def _error(msg: str):
    error_box(msg)


def _render_login_form():
    with st.form("login_form", clear_on_submit=False):
        username = st.text_input("Username", key="login_username", placeholder="your_username")
        password = st.text_input(
            "Password", key="login_password", type="password", placeholder="Your password"
        )
        submitted = st.form_submit_button("Log in", type="primary")

    if not submitted:
        return

    remaining = _lockout_remaining()
    if remaining > 0:
        _error(f"Too many failed attempts. Try again in {remaining}s.")
        return

    if not username.strip() or not password:
        _error("Enter both a username and password.")
        return

    user = verify_user(username, password)
    if user is None:
        _register_failed_attempt()
        if not user_exists(username):
            _error("No account found with that username. Create one with the link below.")
        else:
            _error("Incorrect username or password.")
        return

    st.session_state.auth_failed = 0
    st.session_state.auth_user = user
    st.rerun()


def _render_signup_form():
    with st.form("signup_form", clear_on_submit=False):
        username = st.text_input("Choose a username", key="signup_username", placeholder="your_username")
        password = st.text_input(
            f"Choose a password (min {MIN_PASSWORD_LENGTH} characters)",
            key="signup_password", type="password", placeholder="At least 8 characters",
        )
        confirm = st.text_input(
            "Confirm password", key="signup_confirm", type="password", placeholder="Repeat your password"
        )
        submitted = st.form_submit_button("Create account", type="primary")

    if not submitted:
        return

    if not username.strip() or not password:
        _error("Fill in all the fields.")
        return
    if password != confirm:
        _error("Passwords don't match.")
        return

    ok, message = register_user(username, password)
    if not ok:
        _error(message)
        return

    # Log them straight in after signing up.
    st.session_state.auth_user = username.strip()
    st.rerun()


def _set_mode(mode: str):
    st.session_state.auth_mode = mode


FEATURES = [
    ("globe", "Multilingual sentiment", "Comments in any language are scored without a translation step."),
    ("pulse", "Emotion breakdown", "Joy, neutral, sadness and anger, alongside the positive / negative split."),
    ("layers", "Five platforms", "YouTube, Instagram, LinkedIn, X and Facebook from one place."),
]


def render_auth_page():
    mode = st.session_state.get("auth_mode", "login")

    md(f'<div style="padding-bottom:0.9rem;border-bottom:1px solid var(--line);">{brand_lockup(42)}</div>')

    side, form_col = columns([1.1, 1], gap="large")

    with side:
        feats = "".join(
            f'<div class="feat"><div class="feat-ico">{icon(i, 17)}</div>'
            f'<div><div class="feat-title">{t}</div><div class="feat-desc">{d}</div></div></div>'
            for i, t, d in FEATURES
        )
        md(
            f"""
            <div class="auth-side">
                <div class="auth-title">Read the room before you reply.</div>
                <div class="auth-sub">Sentio AI turns a comment section into a clear picture of
                sentiment and emotion.</div>
                {feats}
            </div>
            """
        )

    with form_col:
        if mode == "login":
            title, sub = "Welcome back", "Log in to keep analyzing what your audience feels."
        else:
            title, sub = "Create your account", "Pick a username and password. It takes a few seconds."
        md(
            f"""
            <div class="auth-form-head">
                <div class="auth-form-title">{title}</div>
                <div class="auth-form-sub">{sub}</div>
            </div>
            """
        )

        if mode == "login":
            _render_login_form()
            md('<div class="auth-switch">New to Sentio AI?</div>')
            st.button("Create an account", key="goto_signup", on_click=_set_mode, args=("signup",))
        else:
            _render_signup_form()
            md('<div class="auth-switch">Already have an account?</div>')
            st.button("Back to log in", key="goto_login", on_click=_set_mode, args=("login",))


def require_login():
    """Call near the top of app.py (after inject_theme()). If nobody is
    logged in, shows the login page and halts the rest of the script."""
    if not is_logged_in():
        render_auth_page()
        st.stop()
