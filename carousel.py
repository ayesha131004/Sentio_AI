"""
carousel.py
------------
Makes the real source cards slide automatically (endless loop), and lets the
visitor take over by scrolling by hand.

app.py renders the cards twice inside a container keyed "carousel" and calls

    inject_carousel_css(PLATFORMS, seconds=45, direction="right")

Behaviour:
  * moves on its own (direction="right" = cards drift left -> right)
  * a manual scroll or drag stops it; after `resume_after` seconds it moves
    again in the direction the visitor scrolled
  * pause_on_hover=True also freezes it while the mouse is over the row
  * with "reduce motion" turned on it never moves by itself

Note: card_width should stay >= 230 so one set of cards is wider than the screen.
"""

import json

import streamlit as st

try:
    import streamlit.components.v1 as components
except Exception:  # pragma: no cover
    components = None

_CSS = """
<style>
__ACCENTS__

/* the row is now a real scroll container; JS moves it automatically */
.st-key-carousel {
    overflow-x: auto; overflow-y: hidden;
    padding: 10px 4px 28px;
    cursor: grab;
    overscroll-behavior-x: contain;
    scrollbar-width: thin;
    scrollbar-color: var(--line-strong, rgba(130,150,255,.32)) transparent;
}
.st-key-carousel::-webkit-scrollbar { height: 6px; }
.st-key-carousel::-webkit-scrollbar-thumb { background: var(--line-strong, rgba(130,150,255,.32)); border-radius: 6px; }
.st-key-carousel::-webkit-scrollbar-track { background: transparent; }
.st-key-carousel img { -webkit-user-drag: none; }

.st-key-carousel div[data-testid="stHorizontalBlock"] {
    width: max-content !important;
    flex-wrap: nowrap !important;
    gap: 1rem !important;
    padding-right: 1rem;               /* = gap, so the loop point is seamless */
}
.st-key-carousel div[data-testid="stColumn"],
.st-key-carousel div[data-testid="column"] {
    flex: 0 0 __WIDTH__px !important;
    width: __WIDTH__px !important;
    min-width: __WIDTH__px !important;
    max-width: __WIDTH__px !important;
}

/* keep the invisible script frame from adding a gap */
div[data-testid="stElementContainer"]:has(iframe[height="0"]) {
    position: absolute; width: 0; height: 0; overflow: hidden; margin: 0 !important;
}

/* reduce motion: show a single normal row that the visitor scrolls by hand */
@media (prefers-reduced-motion: reduce) {
    .st-key-carousel div[data-testid="stColumn"]:nth-child(n+__HIDE_FROM__),
    .st-key-carousel div[data-testid="column"]:nth-child(n+__HIDE_FROM__) { display: none !important; }
}
</style>
"""

_JS = """
<script>
(function () {
  var P = window.parent, doc, KEY = "__sentioCarousel";
  try { doc = P.document; } catch (e) { return; }
  if (P[KEY] && P[KEY].stop) { try { P[KEY].stop(); } catch (e) {} }

  var CFG = __CONFIG__;
  var reduced = !!(P.matchMedia && P.matchMedia("(prefers-reduced-motion: reduce)").matches);
  var alive = true, el = null, track = null, half = 0;
  var pos = 0, lastRead = 0, dir = CFG.dir;
  var resumeAt = 0, dragging = false, moved = false, hovering = false, touching = false;
  var suppressClick = false, startX = 0, lastX = 0, startScroll = 0;
  var last = Date.now(), tickCount = 0, listeners = [];

  function add(t, type, fn, opts) { t.addEventListener(type, fn, opts); listeners.push([t, type, fn, opts]); }
  function stop() {
    alive = false;
    listeners.forEach(function (l) { try { l[0].removeEventListener(l[1], l[2], l[3]); } catch (e) {} });
    listeners = [];
  }
  P[KEY] = { stop: stop };

  function measure() { half = track ? track.offsetWidth / 2 : 0; }
  // Two identical sets: position p looks exactly like p + half, so wrap inside [8, half + 8].
  function norm(v) {
    if (half <= 0) return v;
    while (v < 8) v += half;
    while (v > half + 8) v -= half;
    return v;
  }
  function setScroll(v) { el.scrollLeft = v; lastRead = el.scrollLeft; }
  function resumeLater() { resumeAt = Date.now() + CFG.resumeMs; }

  function bind(n) {
    el = n;
    track = el.querySelector('div[data-testid="stHorizontalBlock"]');
    half = 0;

    // Manual scroll (touch swipe, trackpad, Shift+wheel, scrollbar, keyboard)
    add(el, "scroll", function () {
      if (dragging || !half) return;
      var cur = el.scrollLeft;
      if (Math.abs(cur - lastRead) > 0.5) {
        dir = cur > lastRead ? 1 : -1;          // keep going the way the visitor pushed
        var n2 = norm(cur);
        if (n2 !== cur) el.scrollLeft = n2;
        pos = n2; lastRead = el.scrollLeft;
        resumeLater();
      }
    }, { passive: true });

    // Mouse drag
    add(el, "pointerdown", function (e) {
      if (e.pointerType !== "mouse" || e.button !== 0) return;
      dragging = true; moved = false;
      startX = lastX = e.clientX; startScroll = el.scrollLeft;
    });
    add(doc, "pointermove", function (e) {
      if (!dragging) return;
      var dx = e.clientX - startX;
      if (!moved && Math.abs(dx) < 5) return;
      moved = true;
      el.style.cursor = "grabbing"; el.style.userSelect = "none";
      var step = e.clientX - lastX;
      if (step) dir = step > 0 ? -1 : 1;        // dragging right = cards move right
      lastX = e.clientX;
      var v = startScroll - dx, n3 = norm(v);
      if (n3 !== v) startScroll += n3 - v;
      setScroll(n3); pos = lastRead;
    });
    function endDrag() {
      if (!dragging) return;
      dragging = false;
      el.style.cursor = ""; el.style.userSelect = "";
      if (moved) { suppressClick = true; setTimeout(function () { suppressClick = false; }, 60); }
      pos = el.scrollLeft; lastRead = pos;
      resumeLater();
    }
    add(doc, "pointerup", endDrag);
    add(doc, "pointercancel", endDrag);
    // A drag must not "click" the button under the cursor
    add(el, "click", function (e) {
      if (suppressClick) { e.stopPropagation(); e.preventDefault(); }
    }, true);
    add(el, "dragstart", function (e) { e.preventDefault(); });

    // Touch: hold still while a finger is down
    add(el, "touchstart", function () { touching = true; }, { passive: true });
    add(el, "touchend", function () { touching = false; resumeLater(); }, { passive: true });
    add(el, "touchcancel", function () { touching = false; resumeLater(); }, { passive: true });

    add(el, "mouseenter", function () { hovering = true; });
    add(el, "mouseleave", function () { hovering = false; });
  }

  function frame() {
    if (!alive) return;
    if (window.frameElement && !window.frameElement.isConnected) { stop(); return; }

    var now = Date.now();
    var dt = Math.min(0.05, (now - last) / 1000);
    last = now;

    if (!el || !el.isConnected) {
      var found = doc.querySelector(".st-key-carousel");
      if (found) bind(found); else el = null;
    }
    if (el) {
      if (!half || (++tickCount % 45 === 0)) {
        var before = half;
        measure();
        if (half && !before) { pos = half * 0.5; setScroll(pos); }
      }
      var paused = reduced || dragging || touching || doc.hidden ||
                   (CFG.hover && hovering) || now < resumeAt;
      if (half && !paused) {
        pos = norm(pos + dir * (half / CFG.seconds) * dt);
        setScroll(pos);
      }
    }
    P.requestAnimationFrame(frame);
  }
  P.requestAnimationFrame(frame);
})();
</script>
"""


def inject_carousel_css(platforms: list, seconds: int = 45, direction: str = "right",
                        card_width: int = 250, pause_on_hover: bool = False,
                        resume_after: float = 1.5):
    """
    seconds         time for one full pass of the cards (bigger = slower)
    direction       "right": cards drift left -> right, "left": right -> left
    card_width      width of each card in px (keep >= 230)
    pause_on_hover  also freeze the row while the mouse is over it
    resume_after    seconds of calm after a manual scroll before it moves again
    """
    # The duplicate set of cards uses keys like "card_youtube_dup",
    # so give them the same per-platform accent colours as the first set.
    accents = "".join(
        f'.st-key-card_{p["key"]}_dup {{ --accent: {p["accent"]}; }}' for p in platforms
    )
    css = (
        _CSS.replace("__ACCENTS__", accents)
        .replace("__WIDTH__", str(int(card_width)))
        .replace("__HIDE_FROM__", str(len(platforms) + 1))
    )
    st.markdown(css, unsafe_allow_html=True)

    if components is None:
        return  # manual scrolling still works; only the auto-movement is skipped
    cfg = {
        "seconds": max(5, int(seconds)),
        # dir -1 = scrollLeft decreases = cards move to the right
        "dir": -1 if direction == "right" else 1,
        "resumeMs": int(resume_after * 1000),
        "hover": bool(pause_on_hover),
    }
    try:
        components.html(_JS.replace("__CONFIG__", json.dumps(cfg)), height=0)
    except Exception:
        pass  # never break the page over a decorative effect
