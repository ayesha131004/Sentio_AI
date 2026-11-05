
"""
carousel.py
------------
Responsive SentioAI horizontal platform carousel.

Mobile:
    One full card visible, automatic horizontal movement,
    manual swipe and drag supported.

Tablet:
    Two cards visible, automatic horizontal movement.

Laptop/Desktop:
    Four cards visible, automatic horizontal movement.

All devices:
    Moves left -> right -> left continuously.
    Pauses during user interaction.
    Resumes after the user becomes idle.
    Never vertically stacks platform cards.
"""

import json
import streamlit as st

try:
    import streamlit.components.v1 as components
except Exception:
    components = None


_CSS = """
<style>

/* =========================================================
   CAROUSEL CONTAINER
   ========================================================= */

.st-key-carousel {
    --gap: 16px;
    --pad: 6px;
    --cards: 4;

    container-type: inline-size;
    box-sizing: border-box;

    width: 100% !important;
    max-width: 100% !important;
    min-width: 0 !important;

    overflow-x: auto !important;
    overflow-y: hidden !important;

    padding: 12px var(--pad) 22px !important;

    cursor: grab;
    overscroll-behavior-x: contain;
    overscroll-behavior-y: auto;

    scroll-snap-type: x proximity;
    scroll-padding-left: var(--pad);

    scrollbar-width: thin;
    scrollbar-color:
        var(--line-strong, rgba(130,150,255,.32))
        transparent;

    -webkit-overflow-scrolling: touch;
}

.st-key-carousel:active {
    cursor: grabbing;
}

.st-key-carousel::-webkit-scrollbar {
    height: 5px;
}

.st-key-carousel::-webkit-scrollbar-button {
    display: none;
}

.st-key-carousel::-webkit-scrollbar-thumb {
    background: var(--line-strong, rgba(130,150,255,.32));
    border-radius: 10px;
}

.st-key-carousel::-webkit-scrollbar-track {
    background: transparent;
}

.st-key-carousel img {
    -webkit-user-drag: none;
    user-select: none;
    max-width: 100%;
}


/* =========================================================
   HORIZONTAL CARD ROW
   ========================================================= */

.st-key-carousel div[data-testid="stHorizontalBlock"] {
    display: flex !important;

    width: max-content !important;
    min-width: 100% !important;
    max-width: none !important;

    flex-wrap: nowrap !important;
    flex-direction: row !important;

    gap: var(--gap) !important;
    align-items: stretch !important;

    box-sizing: border-box;
}


/* =========================================================
   CARD WIDTH
   ========================================================= */

.st-key-carousel div[data-testid="stColumn"],
.st-key-carousel div[data-testid="column"] {

    --card-w: calc(
        (100cqw - (var(--pad) * 2) -
        (var(--gap) * (var(--cards) - 1))) / var(--cards)
    );

    flex: 0 0 var(--card-w) !important;

    width: var(--card-w) !important;
    min-width: var(--card-w) !important;
    max-width: var(--card-w) !important;

    box-sizing: border-box;
    scroll-snap-align: start;
}


/* =========================================================
   CONTENT PROTECTION
   ========================================================= */

.st-key-carousel [data-testid="stColumn"] *,
.st-key-carousel [data-testid="column"] * {
    box-sizing: border-box;
}

.st-key-carousel [data-testid="stMarkdownContainer"],
.st-key-carousel [data-testid="stMarkdownContainer"] p {
    max-width: 100%;
    overflow-wrap: anywhere;
}

.st-key-carousel button {
    max-width: 100% !important;
    white-space: normal !important;
    overflow-wrap: anywhere;
}

.st-key-carousel [data-testid="stColumn"] > div,
.st-key-carousel [data-testid="column"] > div {
    min-width: 0;
    max-width: 100%;
}


/* =========================================================
   TABLET: TWO CARDS
   ========================================================= */

@container (max-width: 1100px) {

    .st-key-carousel div[data-testid="stHorizontalBlock"] {
        --cards: 2;
    }
}


/* =========================================================
   MOBILE: ONE FULL CARD
   ========================================================= */

@container (max-width: 680px) {

    .st-key-carousel {
        --gap: 12px;
        --pad: 4px;

        scroll-snap-type: x mandatory;
        scroll-padding-left: var(--pad);
    }

    .st-key-carousel div[data-testid="stHorizontalBlock"] {
        --cards: 1;
    }

    .st-key-carousel div[data-testid="stColumn"],
    .st-key-carousel div[data-testid="column"] {
        scroll-snap-align: start;
    }

}


/* =========================================================
   HIDE INVISIBLE SCRIPT FRAME
   ========================================================= */

div[data-testid="stElementContainer"]:has(iframe[height="0"]) {
    position: absolute !important;
    width: 0 !important;
    height: 0 !important;
    overflow: hidden !important;
    margin: 0 !important;
    padding: 0 !important;
}


/* =========================================================
   ACCESSIBILITY
   ========================================================= */

@media (prefers-reduced-motion: reduce) {

    .st-key-carousel {
        scroll-behavior: auto !important;
    }

}

</style>
"""


_JS = """
<script>
(function () {

    var P = window.parent;
    var doc;

    var KEY = "__sentioCarousel";

    try {
        doc = P.document;
    } catch (e) {
        return;
    }

    /* Clean up the previous animation */

    if (P[KEY] && P[KEY].stop) {
        try {
            P[KEY].stop();
        } catch (e) {}
    }

    var CFG = __CONFIG__;

    var reducedMotion = !!(
        P.matchMedia &&
        P.matchMedia("(prefers-reduced-motion: reduce)").matches
    );

    var alive = true;
    var el = null;
    var listeners = [];

    var pos = 0;
    var dir = 1;

    var running = false;
    var finished = false;

    var startAt = Date.now() + CFG.delayMs;
    var pausedUntil = 0;
    var holdUntil = 0;

    var last = Date.now();

    var hovering = false;
    var focused = false;
    var dragging = false;

    var moved = false;
    var suppressClick = false;

    var startX = 0;
    var startScroll = 0;


    /* =====================================================
       EVENT MANAGEMENT
       ===================================================== */

    function add(target, type, fn, opts) {

        target.addEventListener(type, fn, opts);

        listeners.push([
            target,
            type,
            fn,
            opts
        ]);
    }


    function stop() {

        alive = false;

        listeners.forEach(function (item) {

            try {
                item[0].removeEventListener(
                    item[1],
                    item[2],
                    item[3]
                );
            } catch (e) {}

        });

        listeners = [];
    }


    P[KEY] = {
        stop: stop
    };


    /* =====================================================
       PAUSE ON USER INTERACTION
       ===================================================== */

    function touch() {

        pausedUntil = Date.now() + CFG.idleMs;

    }


    /* =====================================================
       BIND CAROUSEL
       ===================================================== */

    function bind(node) {

        el = node;

        pos = el.scrollLeft;

        dir = parseInt(
            el.dataset.sentioDir || "1",
            10
        ) || 1;


        /* Mouse wheel */

        add(el, "wheel", touch, {
            passive: true
        });


        /* Touch swipe */

        add(el, "touchstart", touch, {
            passive: true
        });

        add(el, "touchmove", touch, {
            passive: true
        });

        add(el, "touchend", touch, {
            passive: true
        });


        /* Keyboard */

        add(el, "keydown", touch);


        /* Hover */

        add(el, "mouseenter", function () {

            hovering = true;

        });

        add(el, "mouseleave", function () {

            hovering = false;
            touch();

        });


        /* Keyboard focus */

        add(el, "focusin", function () {

            focused = true;

        });

        add(el, "focusout", function (e) {

            if (
                !e.relatedTarget ||
                !el.contains(e.relatedTarget)
            ) {

                focused = false;
                touch();

            }

        });


        /* Manual scrollbar / swipe movement */

        add(el, "scroll", function () {

            if (!running) {
                touch();
            }

        }, {
            passive: true
        });


        /* =================================================
           MOUSE DRAG
           ================================================= */

        add(el, "pointerdown", function (e) {

            touch();

            if (
                e.pointerType !== "mouse" ||
                e.button !== 0
            ) {
                return;
            }

            dragging = true;
            moved = false;

            startX = e.clientX;
            startScroll = el.scrollLeft;

        });


        add(doc, "pointermove", function (e) {

            if (!dragging) return;

            var dx = e.clientX - startX;

            if (!moved && Math.abs(dx) < 5) {
                return;
            }

            moved = true;

            touch();

            el.style.cursor = "grabbing";
            el.style.userSelect = "none";
            el.style.scrollSnapType = "none";

            el.scrollLeft = startScroll - dx;

        });


        function endDrag() {

            if (!dragging) return;

            dragging = false;

            el.style.cursor = "";
            el.style.userSelect = "";
            el.style.scrollSnapType = "";

            touch();

            if (moved) {

                suppressClick = true;

                P.setTimeout(function () {

                    suppressClick = false;

                }, 120);

            }

        }


        add(doc, "pointerup", endDrag);
        add(doc, "pointercancel", endDrag);


        /* Prevent accidental card selection after dragging */

        add(el, "click", function (e) {

            if (suppressClick) {

                e.stopPropagation();
                e.preventDefault();

            }

        }, true);


        add(el, "dragstart", function (e) {

            e.preventDefault();

        });

    }


    /* =====================================================
       AUTO-SCROLL STATE
       ===================================================== */

    function setRunning(on) {

        if (on === running) return;

        running = on;

        if (!el) return;

        if (on) {

            pos = el.scrollLeft;

            el.style.scrollSnapType = "none";

        } else if (!dragging) {

            el.style.scrollSnapType = "";

        }

    }


    /* =====================================================
       MAIN ANIMATION LOOP
       ===================================================== */

    function frame() {

        if (!alive) return;


        /* Stop when Streamlit removes the iframe */

        if (
            window.frameElement &&
            !window.frameElement.isConnected
        ) {

            stop();
            return;

        }


        var now = Date.now();

        var dt = Math.min(
            0.05,
            (now - last) / 1000
        );

        last = now;


        /* Find the carousel after Streamlit renders */

        if (!el || !el.isConnected) {

            var found = doc.querySelector(
                ".st-key-carousel"
            );

            if (found) {

                bind(found);

            } else {

                el = null;

            }

        }


        if (el) {

            var max = Math.max(
                0,
                el.scrollWidth - el.clientWidth
            );


            /* Keep position valid after resizing */

            pos = Math.max(
                0,
                Math.min(pos, max)
            );


            /* Auto-scroll is enabled on ALL screen sizes */

            var canRun =
                !reducedMotion &&
                !finished &&
                max > 2 &&
                !doc.hidden &&
                !dragging &&
                !hovering &&
                !focused &&
                now >= startAt &&
                now >= pausedUntil;


            if (!canRun) {

                setRunning(false);

            } else {

                setRunning(true);


                if (now >= holdUntil) {

                    var speed = max / CFG.seconds;

                    pos += dir * speed * dt;


                    /* RIGHT END: reverse direction */

                    if (pos >= max) {

                        pos = max;

                        dir = -1;

                        holdUntil = now + CFG.endHoldMs;

                        if (!CFG.loop) {
                            finished = true;
                        }

                    }


                    /* LEFT END: reverse direction */

                    else if (pos <= 0) {

                        pos = 0;

                        dir = 1;

                        holdUntil = now + CFG.endHoldMs;

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


def inject_carousel_css(
    platforms: list = None,
    seconds: float = 9,
    card_width: int = 300,
    start_delay: float = 1.0,
    loop: bool = True,
    idle_resume: float = 2.5,
    end_pause: float = 1.2,
    **_ignored
):
    """
    Responsive SentioAI carousel.

    Mobile:
        One card visible, automatic horizontal movement.

    Tablet:
        Two cards visible.

    Desktop:
        Four cards visible.

    All devices:
        Automatic left-right movement.
        Manual swipe and drag.
        Pause on interaction.
        Resume after inactivity.
    """

    st.markdown(
        _CSS,
        unsafe_allow_html=True
    )

    if components is None:
        return


    cfg = {

        "seconds": max(
            1.0,
            float(seconds)
        ),

        "delayMs": int(
            max(0.0, float(start_delay)) * 1000
        ),

        "idleMs": int(
            max(0.0, float(idle_resume)) * 1000
        ),

        "endHoldMs": int(
            max(0.0, float(end_pause)) * 1000
        ),

        "loop": bool(loop),

    }


    try:

        components.html(

            _JS.replace(
                "__CONFIG__",
                json.dumps(cfg)
            ),

            height=0

        )

    except Exception:

        pass
