"""
carousel.py
------------
Source cards slide once from the first card (YouTube) to the last (Facebook),
then stop. Any manual scroll, swipe, drag or key press cancels the
auto-scroll, and it does not restart.

app.py renders the cards once inside a container keyed "carousel" and calls

    inject_carousel_css(PLATFORMS, seconds=9)

Options:
  seconds      how long the slide from first to last card takes
  card_width   width of each card in px (wider = more distance to travel)
  start_delay  seconds to wait after the page loads before sliding

With "reduce motion" turned on there is no auto-scroll, only manual scrolling.
"""

import json

import streamlit as st

try:
    import streamlit.components.v1 as components
except Exception:  # pragma: no cover
    components = None

_CSS = """
<style>
/* the row is a normal horizontal scroll container; JS slides it once */
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
  var alive = true, el = null, listeners = [];
  var playing = false, startAt = 0, expected = 0;
  var dragging = false, moved = false, suppressClick = false, startX = 0, startScroll = 0;

  function add(t, type, fn, opts) { t.addEventListener(type, fn, opts); listeners.push([t, type, fn, opts]); }
  function stop() {
    alive = false;
    listeners.forEach(function (l) { try { l[0].removeEventListener(l[1], l[2], l[3]); } catch (e) {} });
    listeners = [];
  }
  P[KEY] = { stop: stop };

  function cancel() { playing = false; }
  function ease(t) { return t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2; }

  function bind(n) {
    el = n;

    // Any manual interaction cancels the auto-scroll for good.
    add(el, "wheel", cancel, { passive: true });
    add(el, "touchstart", cancel, { passive: true });
    add(el, "keydown", cancel);
    add(el, "scroll", function () {
      if (playing && Math.abs(el.scrollLeft - expected) > 3) cancel();
    }, { passive: true });

    // Mouse drag-to-scroll
    add(el, "pointerdown", function (e) {
      cancel();
      if (e.pointerType !== "mouse" || e.button !== 0) return;
      dragging = true; moved = false; startX = e.clientX; startScroll = el.scrollLeft;
    });
    add(doc, "pointermove", function (e) {
      if (!dragging) return;
      var dx = e.clientX - startX;
      if (!moved && Math.abs(dx) < 5) return;
      moved = true;
      el.style.cursor = "grabbing"; el.style.userSelect = "none";
      el.scrollLeft = startScroll - dx;
    });
    function endDrag() {
      if (!dragging) return;
      dragging = false;
      el.style.cursor = ""; el.style.userSelect = "";
      if (moved) { suppressClick = true; setTimeout(function () { suppressClick = false; }, 60); }
    }
    add(doc, "pointerup", endDrag);
    add(doc, "pointercancel", endDrag);
    // A drag must not "click" the button under the cursor
    add(el, "click", function (e) {
      if (suppressClick) { e.stopPropagation(); e.preventDefault(); }
    }, true);
    add(el, "dragstart", function (e) { e.preventDefault(); });

    // Play once per page load (the flag lives on the element itself).
    if (!reduced && el.dataset.sentioAuto !== "1") {
      el.dataset.sentioAuto = "1";
      el.scrollLeft = 0; expected = 0;
      playing = true;
      startAt = Date.now() + CFG.delayMs;
    }
  }

  function frame() {
    if (!alive) return;
    if (window.frameElement && !window.frameElement.isConnected) { stop(); return; }

    if (!el || !el.isConnected) {
      var found = doc.querySelector(".st-key-carousel");
      if (found) bind(found); else el = null;
    }
    if (el && playing && !doc.hidden) {
      var now = Date.now();
      if (now >= startAt) {
        var max = el.scrollWidth - el.clientWidth;
        if (max <= 0) {
          playing = false;                       // everything already fits
        } else {
          var t = Math.min(1, (now - startAt) / (CFG.seconds * 1000));
          el.scrollLeft = ease(t) * max;         // YouTube -> Facebook
          expected = el.scrollLeft;
          if (t >= 1) playing = false;           // reached the end: stop
        }
      }
    }
    P.requestAnimationFrame(frame);
  }
  P.requestAnimationFrame(frame);
})();
</script>
"""


def inject_carousel_css(platforms: list = None, seconds: float = 9, card_width: int = 300,
                        start_delay: float = 1.0, **_ignored):
    """Styles the card row as a scroller and slides it once, first card -> last card.
    Extra keyword arguments from older versions (direction, pause_on_hover, ...) are ignored."""
    css = _CSS.replace("__WIDTH__", str(int(card_width)))
    st.markdown(css, unsafe_allow_html=True)

    if components is None:
        return  # manual scrolling still works; only the auto-slide is skipped
    cfg = {
        "seconds": max(1.0, float(seconds)),
        "delayMs": int(max(0.0, float(start_delay)) * 1000),
    }
    try:
        components.html(_JS.replace("__CONFIG__", json.dumps(cfg)), height=0)
    except Exception:
        pass  # never break the page over a decorative effect
