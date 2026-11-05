"""
marquee.py
-----------
Auto-scrolling strip of platform logos for the landing page.

  from marquee import render_platform_marquee
  render_platform_marquee(PLATFORMS)                    # moves left -> right
  render_platform_marquee(PLATFORMS, direction="left")  # moves right -> left
  render_platform_marquee(PLATFORMS, seconds=45)        # slower (bigger = slower)

Pure CSS animation: pauses on hover, and stops if the visitor has
"reduce motion" turned on. Colors come from theme.py variables, so it works
in both dark and light mode.
"""

import streamlit as st

from theme import find_asset, image_to_data_uri, md

_BASE_CSS = """
.mq {
    position: relative; overflow: hidden; margin: 0 0 1.6rem; padding: 0.35rem 0;
    -webkit-mask-image: linear-gradient(90deg, transparent, #000 8%, #000 92%, transparent);
            mask-image: linear-gradient(90deg, transparent, #000 8%, #000 92%, transparent);
}
.mq-track {
    display: flex; width: max-content;
    animation-name: sentio-mq; animation-timing-function: linear;
    animation-iteration-count: infinite;
}
.mq:hover .mq-track { animation-play-state: paused; }
.mq-group { display: flex; gap: 0.9rem; padding-right: 0.9rem; flex-shrink: 0; }
.mq-item {
    display: flex; align-items: center; gap: 0.7rem;
    padding: 0.55rem 1.1rem 0.55rem 0.6rem; white-space: nowrap;
    border: 1px solid var(--line); border-radius: 999px; background: var(--bg-glass);
    transition: border-color .2s ease, box-shadow .2s ease;
}
.mq-item:hover {
    border-color: var(--mq-accent);
    box-shadow: 0 8px 22px -12px var(--mq-accent);
}
.mq-ico {
    width: 34px; height: 34px; border-radius: 10px; flex-shrink: 0;
    display: flex; align-items: center; justify-content: center;
    background-color: var(--track); border: 1px solid var(--line);
    background-repeat: no-repeat; background-position: center; background-size: 20px 20px;
}
.mq-ico span { color: var(--mq-accent); font-size: 1rem; }
.mq-name { font-size: 0.9rem; font-weight: 600; color: var(--text); line-height: 1.2; }
.mq-tag { font-family: var(--mono) !important; font-size: 0.7rem; color: var(--mq-accent); }
/* 4 identical groups, so shifting by one group (25%) loops without a jump */
@keyframes sentio-mq { from { transform: translateX(0); } to { transform: translateX(-25%); } }
"""


def render_platform_marquee(platforms: list, seconds: int = 30, direction: str = "right"):
    # Each logo is embedded once in CSS (not once per repeated item) to keep the page light.
    icon_css = []
    items = []
    for p in platforms:
        path = find_asset(p["icon_base"])
        if path:
            icon_css.append(
                f'.mq-ico-{p["key"]} {{ background-image: url({image_to_data_uri(path)}); }}'
            )
            ico = f'<div class="mq-ico mq-ico-{p["key"]}"></div>'
        else:
            ico = f'<div class="mq-ico"><span>{p["icon"]}</span></div>'
        items.append(
            f'<div class="mq-item" style="--mq-accent:{p["accent"]}">{ico}'
            f'<div><div class="mq-name">{p["name"]}</div>'
            f'<div class="mq-tag">{p["tag"]}</div></div></div>'
        )

    group = f'<div class="mq-group">{"".join(items)}</div>'
    # "reverse" plays the keyframes backwards, which moves the strip left -> right.
    play = "reverse" if direction == "right" else "normal"

    st.markdown(f"<style>{_BASE_CSS}{''.join(icon_css)}</style>", unsafe_allow_html=True)
    md(
        f'<div class="mq" aria-hidden="true">'
        f'<div class="mq-track" style="animation-duration:{int(seconds)}s;'
        f'animation-direction:{play}">{group * 4}</div></div>'
    )
