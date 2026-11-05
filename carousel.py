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
  card_width   kept for backwards compatibility (card size is now responsive:
               4 cards fit the row on wide screens, 3 on medium, 2 on small,
               so the last visible card is never cut in half)
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
    --gap: 1rem;
    --pad: 6px;
    --cards: 4;                         /* cards visible at once */
    container-type: inline-size;        /* lets the cards size themselves to the row */
    overflow-x: auto; overflow-y: hidden;
    padding: 10px var(--pad) 22px;
    cursor: grab;
    overscroll-behavior-x: contain;
    scroll-snap-type: x proximity;
    scroll-padding-left: var(--pad);
    scrollbar-width: thin;
    scrollbar-color: var(--line-strong, rgba(130,150,255,.32)) transparent;
}
.st-key-carousel::-webkit-scrollbar { height: 6px; }
.st-key-carousel::-webkit-scrollbar-button { display: none; width: 0; height: 0; }
.st-key-carousel::-webkit-scrollbar-thumb { background: var(--line-strong, rgba(130,150,255,.32)); border-radius: 6px; }
.st-key-carousel::-webkit-scrollbar-track { background: transparent; margin: 0 var(--pad); }
.st-key-carousel img { -webkit-user-drag: none; }

.st-key-carousel div[data-testid="stHorizontalBlock"] {
    width: max-content !important;
    flex-wrap: nowrap !important;
    gap: var(--gap) !important;
    align-items: stretch !important;
}

/* each card = (row width - side padding - gaps) / cards-per-view */
.st-key-carousel div[data-testid="stColumn"],
.st-key-carousel div[data-testid="column"] {
    --card-w: calc((100cqw - (var(--pad) * 2) - (var(--gap) * (var(--cards) - 1))) / var(--cards));
    flex: 0 0 var(--card-w) !important;
    width: var(--card-w) !important;
    min-width: var(--card-w) !important;
    max-width: var(--card-w) !important;
    scroll-snap-align: start;
}

/* fewer, larger cards on narrower rows so none is ever sliced in half */
@container (max-width: 980px) { .st-key-carousel div[data-testid="stHorizontalBlock"] { --cards: 3; } }
@container (max-width: 680px) { .st-key-carousel div[data-testid="stHorizontalBlock"] { --cards: 2; } }

/* the card-count variable lives on the block, so pass it down to the columns */
.st-key-carousel div[data-testid="stHorizontalBlock"] > div { --cards: inherit; }

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
      el.style.scrollSnapType = "none";
      el.scrollLeft = startScroll - dx;
    });
    function endDrag() {
      if (!dragging) return;
      dragging = false;
      el.style.cursor = ""; el.style.userSelect = ""; el.style.scrollSnapType = "";
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
      el.style.scrollSnapType = "none";          // snapping would fight the animation
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
          el.style.scrollSnapType = "";
        } else {
          var t = Math.min(1, (now - startAt) / (CFG.seconds * 1000));
          el.scrollLeft = ease(t) * max;         // first card -> last card
          expected = el.scrollLeft;
          if (t >= 1) { playing = false; el.style.scrollSnapType = ""; }   // reached the end: stop
        }
      }
    } else if (el && !playing && el.style.scrollSnapType === "none" && !dragging) {
      el.style.scrollSnapType = "";              // auto-scroll was cancelled: give snapping back
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
    st.markdown(_CSS, unsafe_allow_html=True)

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
