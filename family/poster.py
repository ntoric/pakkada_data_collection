"""
poster.py — A4 family poster matching the "Pakkada Family" template design.

Layout:
  - White/light-blue background with soft floral watercolor corners
  - Large title at top
  - Panchayath | Ward | Form No header ribbon
  - Basic family info in 2 columns
  - "Members Details" section: rounded card, 3-column grid of navy mini-cards
  - "Sisters Details" section: rounded card, one horizontal row per sister
"""

import io
import math
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

# ── Font ───────────────────────────────────────────────────────────────────────
FONTS_DIR = Path(__file__).resolve().parent / 'fonts'
FONT_PATH  = FONTS_DIR / 'NotoSansMalayalam.ttf'

# ── Canvas — A4 @ 150 DPI ─────────────────────────────────────────────────────
W, H = 1240, 1754

# ── Palette ────────────────────────────────────────────────────────────────────
BG          = (245, 248, 255)       # near-white
NAVY        = (22,  52, 100)        # dark navy
NAVY_LIGHT  = (40,  80, 150)        # medium navy
CARD_BG     = (210, 225, 248)       # light blue card fill
CARD_BORDER = (160, 185, 230)       # card border
MINI_BG     = (22,  52, 100)        # navy mini-card fill
WHITE       = (255, 255, 255)
GOLD        = (190, 150,  30)       # title underline / accents
LABEL_CLR   = (22,  52, 100)        # navy labels in basic info
FLOWER_A    = (180, 205, 240, 90)   # soft blue floral petal
FLOWER_B    = (160, 190, 235, 60)
FLOWER_C    = (140, 175, 230, 40)


# ── Helpers ────────────────────────────────────────────────────────────────────

def _font(size: int) -> ImageFont.FreeTypeFont:
    try:
        return ImageFont.truetype(str(FONT_PATH), size)
    except Exception:
        return ImageFont.load_default()


def _tw(draw: ImageDraw.Draw, text: str, font) -> int:
    bb = draw.textbbox((0, 0), text, font=font)
    return bb[2] - bb[0]


def _th(draw: ImageDraw.Draw, text: str, font) -> int:
    bb = draw.textbbox((0, 0), text, font=font)
    return bb[3] - bb[1]


def _centered_text(draw, y, text, font, color, width=W):
    tw = _tw(draw, text, font)
    draw.text(((width - tw) // 2, y), text, font=font, fill=color)
    return _th(draw, text, font)


def _draw_rounded_rect(draw: ImageDraw.Draw, x, y, w, h, r, fill, outline=None, lw=2):
    draw.rounded_rectangle([x, y, x + w, y + h], radius=r, fill=fill,
                            outline=outline, width=lw)


# ── Floral watercolor background ───────────────────────────────────────────────

def _draw_background(img: Image.Image):
    img.paste(BG, [0, 0, W, H])
    overlay = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(overlay)

    # Helper: draw multi-layer petal cluster
    def petal_cluster(cx, cy, scale=1.0):
        sizes  = [(260, 360), (200, 280), (150, 210), (100, 145), (70, 100)]
        colors = [FLOWER_A, FLOWER_A, FLOWER_B, FLOWER_B, FLOWER_C]
        offsets = [(0, 0), (30, -20), (-25, 30), (50, 40), (-40, -30)]
        for (rw, rh), col, (ox, oy) in zip(sizes, colors, offsets):
            rw2 = int(rw * scale)
            rh2 = int(rh * scale)
            ex = cx + ox - rw2 // 2
            ey = cy + oy - rh2 // 2
            d.ellipse([ex, ey, ex + rw2, ey + rh2], fill=col)

    # Four corner clusters
    petal_cluster(-60, -60, 1.0)           # top-left
    petal_cluster(W + 60, -60, 1.0)        # top-right
    petal_cluster(-60, H + 60, 0.9)        # bottom-left
    petal_cluster(W + 60, H + 60, 0.9)     # bottom-right
    # Subtle mid accents
    petal_cluster(W // 2 + 200, H // 2, 0.45)
    petal_cluster(W // 2 - 300, H // 2 - 100, 0.35)

    comp = Image.alpha_composite(img.convert('RGBA'), overlay)
    img.paste(comp.convert('RGB'))


# ── Mini card for a child ──────────────────────────────────────────────────────

def _draw_child_card(img: Image.Image, x: int, y: int, w: int, h: int,
                      lines: list[str], font):
    """Dark navy mini-card with white text lines."""
    draw = ImageDraw.Draw(img)
    _draw_rounded_rect(draw, x, y, w, h, r=12, fill=MINI_BG, outline=None)
    ty = y + 10
    for line in lines:
        draw.text((x + 12, ty), line, font=font, fill=WHITE)
        ty += _th(draw, line, font) + 5


# ── Sister row card ───────────────────────────────────────────────────────────

def _draw_sister_card(img: Image.Image, x: int, y: int, w: int, h: int,
                       cols: list[str], font):
    """Horizontal navy card with columns of text separated evenly."""
    draw = ImageDraw.Draw(img)
    _draw_rounded_rect(draw, x, y, w, h, r=10, fill=MINI_BG, outline=None)
    col_w = w // len(cols)
    for i, text in enumerate(cols):
        cx = x + i * col_w + 14
        th = _th(draw, text, font)
        draw.text((cx, y + (h - th) // 2), text, font=font, fill=WHITE)


# ── Main renderer ──────────────────────────────────────────────────────────────

def render_family_poster(family_data: dict) -> bytes:
    img = Image.new('RGB', (W, H), BG)
    _draw_background(img)
    draw = ImageDraw.Draw(img)

    # ── Fonts ──
    F_TITLE  = _font(72)
    F_HEADER = _font(30)
    F_LABEL  = _font(26)
    F_VALUE  = _font(26)
    F_SEC    = _font(32)
    F_MINI   = _font(21)
    F_SIS    = _font(22)

    PAD  = 62
    CW   = W - PAD * 2
    y    = 52

    # ════════════════════════════════════════
    # TITLE
    # ════════════════════════════════════════
    title = "Pakkada Family"
    th_px = _centered_text(draw, y, title, F_TITLE, NAVY)
    y += th_px + 10
    # Underline
    tw = _tw(draw, title, F_TITLE)
    ux = (W - tw) // 2
    draw.line([(ux, y), (ux + tw, y)], fill=GOLD, width=3)
    y += 18

    # ════════════════════════════════════════
    # HEADER RIBBON: Panchayath | Ward | Form No
    # ════════════════════════════════════════
    panch = family_data.get('പഞ്ചായത്ത്', '')
    ward  = family_data.get('വാർഡ്', '')
    formn = family_data.get('ഫോം നമ്പർ', '')

    ribbon_h = 52
    draw.rectangle([PAD - 10, y, W - PAD + 10, y + ribbon_h], fill=(0, 0, 0, 0))

    parts = [
        (f"Panchanyath : {panch}", 'left'),
        (f"Ward : {ward}",         'center'),
        (f"Form No : {formn}",     'right'),
    ]
    for text, align in parts:
        tw2 = _tw(draw, text, F_HEADER)
        if align == 'left':
            tx = PAD
        elif align == 'center':
            tx = (W - tw2) // 2
        else:
            tx = W - PAD - tw2
        ty2 = y + (ribbon_h - _th(draw, text, F_HEADER)) // 2
        draw.text((tx, ty2), text, font=F_HEADER, fill=NAVY)

    y += ribbon_h + 8
    # Divider
    draw.line([(PAD, y), (W - PAD, y)], fill=NAVY_LIGHT, width=2)
    y += 18

    # ════════════════════════════════════════
    # BASIC INFO — 2 columns
    # ════════════════════════════════════════
    head   = family_data.get('ഗൃഹനാഥന്റെ പേര്', '')
    mobile = family_data.get('മൊബൈൽ നമ്പർ',     '')
    father = family_data.get('ഉപ്പയുടെ പേര്',    '')
    wife   = family_data.get('ഭാര്യയുടെ പേര്',   '')
    mother = family_data.get('ഉമ്മയുടെ പേര്',    '')

    left_fields  = [("Name",          head),
                    ("Father's Name", father),
                    ("Mother's Name", mother)]
    right_fields = [("Mobile",        mobile),
                    ("Wife's Name",   wife)]

    row_h = _th(draw, "A", F_LABEL) + 10
    info_y = y
    for lbl, val in left_fields:
        if lbl or val:
            draw.text((PAD, info_y), lbl, font=F_LABEL, fill=NAVY)
            colon_x = PAD + 180
            draw.text((colon_x, info_y), f": {val}", font=F_VALUE, fill=NAVY)
            info_y += row_h

    info_y2 = y
    rx = W // 2 + 20
    for lbl, val in right_fields:
        if lbl or val:
            draw.text((rx, info_y2), lbl, font=F_LABEL, fill=NAVY)
            draw.text((rx + 165, info_y2), f": {val}", font=F_VALUE, fill=NAVY)
            info_y2 += row_h

    y = max(info_y, info_y2) + 22

    # ════════════════════════════════════════
    # MEMBERS DETAILS
    # ════════════════════════════════════════
    children = family_data.get('മക്കളുടെ വിവരം', [])
    if children:
        # Section heading
        _centered_text(draw, y, "Members Details", F_SEC, NAVY)
        # Underline heading
        hw = _tw(draw, "Members Details", F_SEC)
        hx = (W - hw) // 2
        draw.line([(hx, y + _th(draw, "Members Details", F_SEC) + 2),
                   (hx + hw, y + _th(draw, "Members Details", F_SEC) + 2)],
                  fill=NAVY, width=2)
        y += _th(draw, "Members Details", F_SEC) + 18

        # Build mini-card lines for each child
        COLS = 3
        mcol_gap = 14
        mcol_w = (CW - (COLS - 1) * mcol_gap) // COLS

        def child_lines(c):
            ls = []
            relation = c.get('ബന്ധം', '')
            name     = c.get('പേര്', '')
            mob      = c.get('മൊബൈൽ നമ്പർ', '')
            w2       = c.get('ഭാര്യയുടെ പേര്', '')
            kids     = c.get('കുട്ടികൾ', {})
            ab5      = kids.get('5 വയസിനു മുകളിൽ', 0)
            bl5      = kids.get('5 വയസിനു താഴെ', 0)
            ls.append(f"Name    : {name}")
            if mob: ls.append(f"Mobile  : {mob}")
            if w2:  ls.append(f"Wife    : {w2}")
            ls.append(f"Children (5+) : {ab5}")
            ls.append(f"Children (5-) : {bl5}")
            return ls

        line_h   = _th(draw, "A", F_MINI) + 5
        max_lines = max(len(child_lines(c)) for c in children)
        mini_h   = 12 + max_lines * line_h + 10

        rows     = math.ceil(len(children) / COLS)
        grid_h   = rows * (mini_h + 10) - 10
        outer_h  = grid_h + 28
        outer_pad = 14

        # Outer card
        _draw_rounded_rect(draw, PAD - 10, y, CW + 20, outer_h + outer_pad * 2,
                            r=20, fill=CARD_BG, outline=CARD_BORDER, lw=2)
        gy = y + outer_pad

        for i, child in enumerate(children):
            col_i = i % COLS
            row_i = i // COLS
            mx = PAD - 10 + outer_pad + col_i * (mcol_w + mcol_gap)
            my = gy + row_i * (mini_h + 10)
            lines = child_lines(child)
            _draw_child_card(img, mx, my, mcol_w, mini_h, lines, F_MINI)
            draw = ImageDraw.Draw(img)

        y += outer_h + outer_pad * 2 + 20

    # ════════════════════════════════════════
    # SISTERS DETAILS
    # ════════════════════════════════════════
    sisters = family_data.get('സഹോദരിമാരുടെ വിവരങ്ങൾ', [])
    if sisters:
        _centered_text(draw, y, "Sisters Details", F_SEC, NAVY)
        sw = _tw(draw, "Sisters Details", F_SEC)
        sx = (W - sw) // 2
        draw.line([(sx, y + _th(draw, "Sisters Details", F_SEC) + 2),
                   (sx + sw, y + _th(draw, "Sisters Details", F_SEC) + 2)],
                  fill=NAVY, width=2)
        y += _th(draw, "Sisters Details", F_SEC) + 18

        sis_h    = 46
        sis_gap  = 10
        sis_pad  = 14
        sis_rows_h = len(sisters) * (sis_h + sis_gap) - sis_gap
        outer_h  = sis_rows_h + sis_pad * 2

        _draw_rounded_rect(draw, PAD - 10, y, CW + 20, outer_h,
                            r=20, fill=CARD_BG, outline=CARD_BORDER, lw=2)
        sy2 = y + sis_pad

        for sister in sisters:
            name = sister.get('സഹോദരിയുടെ പേര്', '')
            mob  = sister.get('മൊബൈൽ നമ്പർ', '')
            kids = sister.get('കുട്ടികൾ', {})
            ab5  = kids.get('5 വയസിനു മുകളിൽ', 0)
            bl5  = kids.get('5 വയസിനു താഴെ', 0)
            cols = [f"Name : {name}", f"Mobile: {mob}",
                    f"Children (5+) : {ab5}", f"Children (5-) : {bl5}"]
            _draw_sister_card(img, PAD - 10 + sis_pad, sy2,
                               CW + 20 - sis_pad * 2, sis_h, cols, F_SIS)
            draw = ImageDraw.Draw(img)
            sy2 += sis_h + sis_gap

        y += outer_h + 20

    # ════════════════════════════════════════
    # FOOTER
    # ════════════════════════════════════════
    footer = "ntoric.com  |  Pakkada Data Collection"
    fw = _tw(draw, footer, _font(20))
    draw.text(((W - fw) // 2, H - 50), footer, font=_font(20), fill=NAVY_LIGHT)

    buf = io.BytesIO()
    img.save(buf, format='JPEG', quality=93, optimize=True)
    buf.seek(0)
    return buf.read()
