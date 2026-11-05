"""
carousel.py
------------
Source cards glide back and forth on their own: left -> right, a short rest at
the end, then right -> left, and so on.

The user is always in control:
  * hovering a card, focusing a button, dragging, scrolling (wheel, touchpad,
    swipe, scrollbar) or pressing a key PAUSES the motion immediately;
  * a moment after the user stops interacting (idle_resume seconds, and not
    hovering any more) it continues from exactly where they left it.

app.py renders the cards once inside a container keyed "carousel" and calls

    inject_carousel_css(PLATFORMS, seconds=9)

Options:
  seconds       time for one full pass, first card -> last card
  start_delay   seconds to wait after the page loads before moving
  loop          True  = keep going back and forth (default)
                False = slide once to the end and stop
  idle_resume   seconds of no interaction before the motion resumes
  end_pause     seconds to rest at either end before turning around
  card_width    kept for backwards compatibility (card size is responsive)

With "reduce motion" turned on there is no auto-motion, only manual scrolling.
"""

import json

import streamlit as st

try:
    import streamlit.components.v1 as components
except Exception:  # pragma: no cover
    components = None

_CSS = """
<style>
/* the row is a normal horizontal scroll container; JS glides it */
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

  var pos = 0, dir = 1, running = false, finished = false;
  var startAt = Date.now() + CFG.delayMs;
  var pausedUntil = 0, holdUntil = 0, last = Date.now();
  var hovering = false, focused = false;
  var dragging = false, moved = false, suppressClick = false, startX = 0, startScroll = 0;

  function add(t, type, fn, opts) { t.addEventListener(type, fn, opts); listeners.push([t, type, fn, opts]); }
  function stop() {
    alive = false;
    listeners.forEach(function (l) { try { l[0].removeEventListener(l[1], l[2], l[3]); } catch (e) {} });
    listeners = [];
  }
  P[KEY] = { stop: stop };

  // any user activity: pause now, resume only after a quiet moment
  function touch() { pausedUntil = Date.now() + CFG.idleMs; }

  function bind(n) {
    el = n;
    pos = el.scrollLeft;
    dir = parseInt(el.dataset.sentioDir || "1", 10) || 1;

    add(el, "wheel", touch, { passive: true });
    add(el, "touchstart", touch, { passive: true });
    add(el, "touchmove", touch, { passive: true });
    add(el, "keydown", touch);

    add(el, "mouseenter", function () { hovering = true; });
    add(el, "mouseleave", function () { hovering = false; touch(); });
    add(el, "focusin", function () { focused = true; });
    add(el, "focusout", function (e) {
      if (!e.relatedTarget || !el.contains(e.relatedTarget)) { focused = false; touch(); }
    });

    // a scroll we did not cause (scrollbar drag, touch, keys...) counts as the user
    add(el, "scroll", function () {
      if (running && Math.abs(el.scrollLeft - Math.round(pos)) <= 3) return;
      touch();
    }, { passive: true });

    // Mouse drag-to-scroll
    add(el, "pointerdown", function (e) {
      touch();
      if (e.pointerType !== "mouse" || e.button !== 0) return;
      dragging = true; moved = false; startX = e.clientX; startScroll = el.scrollLeft;
    });
    add(doc, "pointermove", function (e) {
      if (!dragging) return;
      var dx = e.clientX - startX;
      if (!moved && Math.abs(dx) < 5) return;
      moved = true;
      touch();
      el.style.cursor = "grabbing"; el.style.userSelect = "none";
      el.style.scrollSnapType = "none";
      el.scrollLeft = startScroll - dx;
    });
    function endDrag() {
      if (!dragging) return;
      dragging = false;
      el.style.cursor = ""; el.style.userSelect = ""; el.style.scrollSnapType = "";
      touch();
      if (moved) { suppressClick = true; setTimeout(function () { suppressClick = false; }, 60); }
    }
    add(doc, "pointerup", endDrag);
    add(doc, "pointercancel", endDrag);
    // A drag must not "click" the button under the cursor
    add(el, "click", function (e) {
      if (suppressClick) { e.stopPropagation(); e.preventDefault(); }
    }, true);
    add(el, "dragstart", function (e) { e.preventDefault(); });
  }

  function setRunning(on) {
    if (on === running) return;
    running = on;
    if (!el) return;
    if (on) { pos = el.scrollLeft; el.style.scrollSnapType = "none"; }   // snapping would fight the glide
    else if (!dragging) { el.style.scrollSnapType = ""; }
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

    if (el && !reduced) {
      var max = el.scrollWidth - el.clientWidth;
      var canRun = !finished && max > 2 && !doc.hidden && !dragging && !hovering && !focused &&
                   now >= startAt && now >= pausedUntil;

      if (!canRun) {
        setRunning(false);
      } else {
        setRunning(true);
        if (now >= holdUntil) {
          pos += dir * (max / CFG.seconds) * dt;
          if (pos >= max) {
            pos = max; dir = -1; holdUntil = now + CFG.endHoldMs;
            if (!CFG.loop) finished = true;
          } else if (pos <= 0) {
            pos = 0; dir = 1; holdUntil = now + CFG.endHoldMs;
          }
          el.dataset.sentioDir = String(dir);
          el.scrollLeft = pos;
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
                        start_delay: float = 1.0, loop: bool = True,
                        idle_resume: float = 2.5, end_pause: float = 1.2, **_ignored):
    """Styles the card row as a scroller and glides it back and forth.
    The motion pauses whenever the user hovers, drags, scrolls or focuses a card,
    and resumes from the same spot after `idle_resume` quiet seconds.
    Extra keyword arguments from older versions (direction, pause_on_hover, ...) are ignored."""
    st.markdown(_CSS, unsafe_allow_html=True)

    if components is None:
        return  # manual scrolling still works; only the auto-motion is skipped
    cfg = {
        "seconds": max(1.0, float(seconds)),
        "delayMs": int(max(0.0, float(start_delay)) * 1000),
        "idleMs": int(max(0.0, float(idle_resume)) * 1000),
        "endHoldMs": int(max(0.0, float(end_pause)) * 1000),
        "loop": bool(loop),
    }
    try:
        components.html(_JS.replace("__CONFIG__", json.dumps(cfg)), height=0)
    except Exception:
        pass  # never break the page over a decorative effect
