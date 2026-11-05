"""
carousel.py
------------
Makes the real source cards slide automatically (left -> right, endless loop).

app.py renders the cards twice inside a container keyed "carousel";
this file only injects the CSS that turns that row into a moving carousel.

  inject_carousel_css(PLATFORMS)                      # left -> right
  inject_carousel_css(PLATFORMS, direction="left")    # right -> left
  inject_carousel_css(PLATFORMS, seconds=60)          # slower (bigger = slower)

Pauses on hover or keyboard focus. With "reduce motion" turned on, the
carousel stops moving and becomes a normal scrollable row.
"""

import streamlit as st

_CSS = """
<style>
__ACCENTS__

.st-key-carousel { overflow: hidden; padding: 10px 4px 28px; }

.st-key-carousel div[data-testid="stHorizontalBlock"] {
    width: max-content !important;
    flex-wrap: nowrap !important;
    gap: 1rem !important;
    padding-right: 1rem;               /* = gap, so the loop point is seamless */
    animation: sentio-cards __SECONDS__s linear infinite;
    animation-direction: __DIRECTION__;
}
.st-key-carousel div[data-testid="stColumn"],
.st-key-carousel div[data-testid="column"] {
    flex: 0 0 __WIDTH__px !important;
    width: __WIDTH__px !important;
    min-width: __WIDTH__px !important;
    max-width: __WIDTH__px !important;
}

/* pause so cards are easy to click */
.st-key-carousel:hover div[data-testid="stHorizontalBlock"],
.st-key-carousel:focus-within div[data-testid="stHorizontalBlock"] {
    animation-play-state: paused;
}

/* two identical sets, so shifting by half the row loops without a jump */
@keyframes sentio-cards { from { transform: translateX(0); } to { transform: translateX(-50%); } }

@media (prefers-reduced-motion: reduce) {
    .st-key-carousel { overflow-x: auto; }
    .st-key-carousel div[data-testid="stHorizontalBlock"] { animation: none !important; }
    .st-key-carousel div[data-testid="stColumn"]:nth-child(n+__HIDE_FROM__),
    .st-key-carousel div[data-testid="column"]:nth-child(n+__HIDE_FROM__) { display: none !important; }
}
</style>
"""


def inject_carousel_css(platforms: list, seconds: int = 45, direction: str = "right",
                        card_width: int = 250):
    # The second (duplicate) set of cards uses keys like "card_youtube_dup",
    # so give them the same per-platform accent colours as the first set.
    accents = "".join(
        f'.st-key-card_{p["key"]}_dup {{ --accent: {p["accent"]}; }}' for p in platforms
    )
    css = (
        _CSS.replace("__ACCENTS__", accents)
        .replace("__SECONDS__", str(int(seconds)))
        # "reverse" plays the keyframes backwards, which moves the row left -> right.
        .replace("__DIRECTION__", "reverse" if direction == "right" else "normal")
        .replace("__WIDTH__", str(int(card_width)))
        .replace("__HIDE_FROM__", str(len(platforms) + 1))
    )
    st.markdown(css, unsafe_allow_html=True)
