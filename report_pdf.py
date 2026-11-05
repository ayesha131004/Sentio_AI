"""
report_pdf.py
--------------
Builds a clean, printable PDF report of the analysis results.

    from report_pdf import build_pdf_report
    pdf_bytes = build_pdf_report(view_df, platform_name=..., url=..., ...)

Uses reportlab (pure Python, no system packages needed).

Fonts: the built-in PDF font only covers Western European characters, so other
characters (emoji, Hindi, Arabic, Chinese...) are replaced with "?". If DejaVu Sans
is available the report also supports Greek, Cyrillic and more Latin letters:
  * add `fonts-dejavu-core` as a line in a file named packages.txt (repo root), or
  * put DejaVuSans.ttf and DejaVuSans-Bold.ttf in a folder named fonts/.
"""

import html
import io
import os
from datetime import datetime, timezone

from reportlab.graphics.charts.piecharts import Pie
from reportlab.graphics.shapes import Circle, Drawing, Rect, String
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

# ---- palette (tuned for white paper) ----
DARK = colors.HexColor("#0b1220")
GRAY = colors.HexColor("#51607a")
LINE = colors.HexColor("#d9def0")
TRACK = colors.HexColor("#e6e9f7")
SOFT = colors.HexColor("#f5f6ff")
INDIGO = colors.HexColor("#4f46e5")
CYAN = colors.HexColor("#0891b2")
POS = colors.HexColor("#0f9f73")
NEU = colors.HexColor("#5b6cf0")
NEG = colors.HexColor("#e0365c")
AMBER = colors.HexColor("#b7791f")

EMOTION_COLORS = {
    "Joy": "#0f9f73", "Neutral": "#5b6cf0", "Sadness": "#d6336c", "Anger": "#e8590c",
    "Fear": "#7c3aed", "Surprise": "#0891b2", "Disgust": "#65a30d", "Optimism": "#ca8a04",
}

_BASE = os.path.dirname(os.path.abspath(__file__))
_FONT_CANDIDATES = [
    (os.path.join(_BASE, "fonts", "DejaVuSans.ttf"), os.path.join(_BASE, "fonts", "DejaVuSans-Bold.ttf")),
    (os.path.join(_BASE, "DejaVuSans.ttf"), os.path.join(_BASE, "DejaVuSans-Bold.ttf")),
    ("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"),
]
_fonts = None


def _setup_fonts():
    """Returns (regular, bold, unicode_ok)."""
    global _fonts
    if _fonts:
        return _fonts
    for reg, bold in _FONT_CANDIDATES:
        if os.path.exists(reg):
            try:
                pdfmetrics.registerFont(TTFont("SentioSans", reg))
                pdfmetrics.registerFont(TTFont("SentioSans-Bold", bold if os.path.exists(bold) else reg))
                _fonts = ("SentioSans", "SentioSans-Bold", True)
                return _fonts
            except Exception:
                continue
    _fonts = ("Helvetica", "Helvetica-Bold", False)
    return _fonts


def _plain(text, uni, limit=None) -> str:
    """Clean text so it can be drawn with the chosen font."""
    t = str(text if text is not None else "").replace("\r", " ").replace("\n", " ")
    t = "".join(ch for ch in t if ch.isprintable())
    if uni:
        t = "".join(ch for ch in t if ord(ch) <= 0xFFFF)  # drop emoji outside the font
    else:
        t = t.encode("latin-1", "replace").decode("latin-1")
    t = " ".join(t.split())
    if limit and len(t) > limit:
        t = t[: limit - 1].rstrip() + "…" if uni else t[: limit - 3].rstrip() + "..."
    return t


def _para(text, uni, limit=None) -> str:
    """Same as _plain, but safe to put inside a Paragraph."""
    return html.escape(_plain(text, uni, limit))


def _verdict(pos: float, neg: float):
    if pos >= 55:
        return "Overwhelmingly Positive", POS
    if neg >= 55:
        return "Overwhelmingly Negative", NEG
    if pos > neg:
        return "Mostly Positive", POS
    if neg > pos:
        return "Mostly Negative", NEG
    return "Mixed / Neutral", INDIGO


# ----------------------------------------------------------------------
# CHARTS (drawn with reportlab shapes)
# ----------------------------------------------------------------------
def _donut(counts: dict, width, fonts) -> Drawing:
    regular, bold, _ = fonts
    h = 130
    d = Drawing(width, h)
    total = sum(counts.values())
    order = [("Positive", POS), ("Neutral", NEU), ("Negative", NEG)]
    if total <= 0:
        d.add(String(0, h / 2, "No data", fontName=regular, fontSize=9, fillColor=GRAY))
        return d

    pie = Pie()
    pie.x, pie.y, pie.width, pie.height = 8, 10, 110, 110
    shown = [(name, col) for name, col in order if counts.get(name, 0) > 0]
    pie.data = [counts[name] for name, _ in shown]
    pie.labels = None
    pie.startAngle = 90
    pie.direction = "clockwise"
    pie.slices.strokeWidth = 1.2
    pie.slices.strokeColor = colors.white
    for i, (_, col) in enumerate(shown):
        pie.slices[i].fillColor = col
    d.add(pie)

    cx, cy = pie.x + pie.width / 2, pie.y + pie.height / 2
    d.add(Circle(cx, cy, 33, fillColor=colors.white, strokeColor=None))
    d.add(String(cx, cy + 1, str(total), textAnchor="middle", fontName=bold, fontSize=15, fillColor=DARK))
    d.add(String(cx, cy - 10, "comments", textAnchor="middle", fontName=regular, fontSize=7, fillColor=GRAY))

    for i, (name, col) in enumerate(order):
        y = h - 42 - i * 24
        pct = counts.get(name, 0) / total * 100
        d.add(Rect(140, y, 9, 9, fillColor=col, strokeColor=None, rx=2, ry=2))
        d.add(String(155, y + 1, name, fontName=regular, fontSize=9, fillColor=DARK))
        d.add(String(155, y - 10, f"{pct:.1f}%  ({counts.get(name, 0)})", fontName=regular, fontSize=7.5, fillColor=GRAY))
    return d


def _hbars(items, width, fonts, label_w=62, value_w=34, row_h=19) -> Drawing:
    """items = [(label, value, colour, value_text), ...]"""
    regular, bold, _ = fonts
    h = max(1, len(items)) * row_h + 4
    d = Drawing(width, h)
    if not items:
        return d
    bar_w = width - label_w - value_w
    vmax = max(v for _, v, _, _ in items) or 1
    for i, (label, value, col, text) in enumerate(items):
        y = h - (i + 1) * row_h + 3
        d.add(String(0, y + 1, label, fontName=regular, fontSize=8.5, fillColor=DARK))
        d.add(Rect(label_w, y, bar_w, 9, rx=4, ry=4, fillColor=TRACK, strokeColor=None))
        d.add(Rect(label_w, y, max(3, bar_w * value / vmax), 9, rx=4, ry=4, fillColor=col, strokeColor=None))
        d.add(String(label_w + bar_w + 6, y + 1, text, fontName=bold, fontSize=8, fillColor=GRAY))
    return d


# ----------------------------------------------------------------------
# REPORT
# ----------------------------------------------------------------------
def build_pdf_report(df, platform_name="Platform", url="", emotions=None, keywords=None,
                     used_demo=False, total_all=None) -> bytes:
    """
    df            DataFrame of the comments to include (columns: text, sentiment, score,
                  polarity, likes, emotion). Pass the *filtered* view to mirror the page.
    emotions      {"Joy": 42.9, ...} percentages (optional)
    keywords      [("word", count), ...] (optional)
    total_all     number of comments before filtering (for the scope line)
    """
    fonts = _setup_fonts()
    regular, bold, uni = fonts

    total = len(df)
    total_all = total_all or total
    counts = {k: int((df["sentiment"] == k).sum()) for k in ("Positive", "Neutral", "Negative")} if total else \
             {"Positive": 0, "Neutral": 0, "Negative": 0}
    pos = counts["Positive"] / total * 100 if total else 0.0
    neu = counts["Neutral"] / total * 100 if total else 0.0
    neg = counts["Negative"] / total * 100 if total else 0.0
    net = pos - neg
    likes = int(df["likes"].sum()) if total and "likes" in df else 0
    conf = float(df["score"].mean()) * 100 if total and "score" in df else 0.0
    verdict, verdict_col = _verdict(pos, neg)

    # emotions: use what was passed, else derive from the per-comment labels
    emo = {str(k).capitalize(): float(v) for k, v in (emotions or {}).items()}
    if not emo and total and "emotion" in df:
        known = df[df["emotion"] != "Unknown"]["emotion"]
        if len(known):
            emo = (known.value_counts(normalize=True) * 100).round(1).to_dict()
    top_emotion = max(emo, key=emo.get) if emo else "n/a"

    # ---- styles ----
    S = {
        "h2": ParagraphStyle("h2", fontName=bold, fontSize=12, leading=15, textColor=INDIGO, spaceBefore=14, spaceAfter=6),
        "body": ParagraphStyle("body", fontName=regular, fontSize=9, leading=12.5, textColor=DARK),
        "small": ParagraphStyle("small", fontName=regular, fontSize=8, leading=10.5, textColor=GRAY),
        "cell": ParagraphStyle("cell", fontName=regular, fontSize=8, leading=10.5, textColor=DARK),
        "head": ParagraphStyle("head", fontName=bold, fontSize=8, leading=10, textColor=DARK),
        "kpi": ParagraphStyle("kpi", fontName=regular, fontSize=8, leading=19, textColor=GRAY),
        "meta": ParagraphStyle("meta", fontName=regular, fontSize=9, leading=13, textColor=GRAY),
    }
    page_w = A4[0] - 36 * mm
    story = []

    # ---- header ----
    story.append(Paragraph(
        f'<font name="{bold}" size="22" color="#0b1220">Sentio</font>'
        f'<font name="{bold}" size="22" color="#4f46e5">AI</font>', S["body"]))
    story.append(Paragraph(
        f'<font name="{bold}" size="14" color="#0b1220">Audience sentiment report</font>',
        ParagraphStyle("t", fontName=bold, fontSize=14, leading=22)))
    story.append(Spacer(1, 4))
    scope = (f"All {total_all} comments analysed" if total == total_all
             else f"Showing {total} of {total_all} comments (filters applied)")
    generated = datetime.now(timezone.utc).strftime("%d %b %Y, %H:%M UTC")
    story.append(Paragraph(
        f'<font color="#0b1220">Platform:</font> {_para(platform_name, uni)}<br/>'
        f'<font color="#0b1220">Link:</font> {_para(url, uni, 160)}<br/>'
        f'<font color="#0b1220">Generated:</font> {generated}<br/>'
        f'<font color="#0b1220">Scope:</font> {scope}', S["meta"]))

    if used_demo:
        story.append(Spacer(1, 8))
        warn = Table([[Paragraph(
            "Demo data: live comments could not be fetched for this link, so the figures "
            "below come from sample comments, not from your audience.", S["cell"])]],
            colWidths=[page_w])
        warn.setStyle(TableStyle([
            ("BOX", (0, 0), (-1, -1), 0.8, AMBER), ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#fff7e6")),
            ("LEFTPADDING", (0, 0), (-1, -1), 8), ("TOPPADDING", (0, 0), (-1, -1), 6), ("BOTTOMPADDING", (0, 0), (-1, -1), 6)]))
        story.append(warn)

    # ---- verdict banner ----
    story.append(Spacer(1, 10))
    banner = Table([[Paragraph(
        f'<font name="{regular}" size="8" color="#51607a">OVERALL PERFORMANCE</font><br/>'
        f'<font name="{bold}" size="17" color="{verdict_col.hexval().replace("0x", "#")}">{verdict}</font>',
        ParagraphStyle("vb", fontName=regular, fontSize=8, leading=22))]], colWidths=[page_w])
    banner.setStyle(TableStyle([
        ("BOX", (0, 0), (-1, -1), 0.8, LINE), ("BACKGROUND", (0, 0), (-1, -1), SOFT),
        ("LINEBEFORE", (0, 0), (0, -1), 4, verdict_col),
        ("LEFTPADDING", (0, 0), (-1, -1), 12), ("TOPPADDING", (0, 0), (-1, -1), 8), ("BOTTOMPADDING", (0, 0), (-1, -1), 8)]))
    story.append(banner)

    # ---- KPI grid ----
    def kpi(label, value, col="#0b1220"):
        return Paragraph(f'<font size="8" color="#51607a">{label}</font><br/>'
                         f'<font name="{bold}" size="15" color="{col}">{value}</font>', S["kpi"])

    row1 = [kpi("Comments", f"{total:,}"), kpi("Positive", f"{pos:.1f}%", "#0f9f73"),
            kpi("Neutral", f"{neu:.1f}%", "#5b6cf0"), kpi("Negative", f"{neg:.1f}%", "#e0365c")]
    row2 = [kpi("Net sentiment", f"{net:+.1f}", "#0f9f73" if net >= 0 else "#e0365c"),
            kpi("Total likes", f"{likes:,}"), kpi("Avg. confidence", f"{conf:.0f}%"),
            kpi("Top emotion", _para(top_emotion, uni))]
    kt = Table([row1, row2], colWidths=[page_w / 4] * 4)
    kt.setStyle(TableStyle([
        ("BOX", (0, 0), (-1, -1), 0.6, LINE), ("INNERGRID", (0, 0), (-1, -1), 0.6, LINE),
        ("LEFTPADDING", (0, 0), (-1, -1), 10), ("TOPPADDING", (0, 0), (-1, -1), 7), ("BOTTOMPADDING", (0, 0), (-1, -1), 7)]))
    story.append(Spacer(1, 10))
    story.append(kt)

    # ---- charts: sentiment donut + emotions ----
    half = page_w / 2 - 6
    emo_items = [(_plain(k, uni, 12), v, colors.HexColor(EMOTION_COLORS.get(k, "#64748b")), f"{v:.1f}%")
                 for k, v in sorted(emo.items(), key=lambda kv: -kv[1])[:7]]
    left = _donut(counts, half, fonts)
    right = _hbars(emo_items, half, fonts) if emo_items else Paragraph("No emotion data.", S["small"])
    story.append(Paragraph("Sentiment and emotions", S["h2"]))
    ct = Table([[Paragraph("Sentiment split", S["head"]), Paragraph("Emotions", S["head"])], [left, right]],
               colWidths=[page_w / 2, page_w / 2])
    ct.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP"), ("LEFTPADDING", (0, 0), (-1, -1), 0),
                            ("BOTTOMPADDING", (0, 0), (-1, 0), 6)]))
    story.append(ct)

    # ---- keywords ----
    kw = [(w, c) for w, c in (keywords or []) if str(w).strip()][:10]
    if kw:
        story.append(Paragraph("Top keywords", S["h2"]))
        kw_items = [(_plain(w, uni, 14), float(c), INDIGO, str(int(c))) for w, c in kw]
        story.append(_hbars(kw_items, page_w * 0.7, fonts, label_w=80, row_h=17))

    # ---- comment tables ----
    def comment_table(title, rows):
        story.append(Paragraph(title, S["h2"]))
        if rows is None or len(rows) == 0:
            story.append(Paragraph("No comments in this group.", S["small"]))
            return
        data = [[Paragraph("Comment", S["head"]), Paragraph("Emotion", S["head"]),
                 Paragraph("Conf.", S["head"]), Paragraph("Likes", S["head"])]]
        for _, r in rows.iterrows():
            data.append([
                Paragraph(_para(r.get("text", ""), uni, 260), S["cell"]),
                Paragraph(_para(r.get("emotion", ""), uni), S["cell"]),
                Paragraph(f'{float(r.get("score", 0)) * 100:.0f}%', S["cell"]),
                Paragraph(f'{int(r.get("likes", 0)):,}', S["cell"]),
            ])
        t = Table(data, colWidths=[page_w - 62 * mm, 24 * mm, 18 * mm, 20 * mm], repeatRows=1)
        t.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#eef0ff")),
            ("LINEBELOW", (0, 0), (-1, -1), 0.4, LINE), ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("TOPPADDING", (0, 0), (-1, -1), 4), ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ("LEFTPADDING", (0, 0), (-1, -1), 5), ("RIGHTPADDING", (0, 0), (-1, -1), 5)]))
        story.append(t)

    have = total and "polarity" in df
    comment_table("Most positive comments",
                  df[df["sentiment"] == "Positive"].nlargest(5, "polarity") if have else None)
    comment_table("Most negative comments",
                  df[df["sentiment"] == "Negative"].nsmallest(5, "polarity") if have else None)
    comment_table("Most liked comments",
                  df.nlargest(5, "likes") if total and "likes" in df else None)

    # ---- method note ----
    story.append(Spacer(1, 14))
    story.append(Paragraph(
        "How to read this report: sentiment is scored by a multilingual XLM-RoBERTa model, so comments in "
        "many languages are handled directly. Emotions come from an English-focused DistilRoBERTa model and "
        "are a rougher signal for non-English comments. Percentages are shares of the comments included in "
        "this report, and the model can misread sarcasm or very short comments.", S["small"]))

    # ---- page furniture ----
    def decorate(canvas, doc):
        w, h = A4
        canvas.saveState()
        canvas.setFillColor(INDIGO)
        canvas.rect(0, h - 6, w * 0.6, 6, stroke=0, fill=1)
        canvas.setFillColor(CYAN)
        canvas.rect(w * 0.6, h - 6, w * 0.4, 6, stroke=0, fill=1)
        canvas.setFont(regular, 7.5)
        canvas.setFillColor(GRAY)
        canvas.drawString(18 * mm, 10 * mm, "Sentio AI  |  Audience sentiment report")
        canvas.drawRightString(w - 18 * mm, 10 * mm, f"Page {doc.page}")
        canvas.restoreState()

    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4, leftMargin=18 * mm, rightMargin=18 * mm,
                            topMargin=16 * mm, bottomMargin=18 * mm,
                            title="Sentio AI sentiment report", author="Sentio AI")
    doc.build(story, onFirstPage=decorate, onLaterPages=decorate)
    return buf.getvalue()
