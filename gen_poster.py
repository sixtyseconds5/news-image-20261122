#!/usr/bin/env python3
"""Draw the 22 November 2026 world-news front page as entry.png (1024x1024).

Every picture element is drawn from Pillow shapes in this file.
No network, no photos, no randomness: two runs write identical bytes.
"""
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
OUT_FILE = HERE / "entry.png"
FONT_DIR = Path("/usr/share/fonts/truetype/dejavu")

PAPER = (251, 247, 237)
INK = (26, 26, 26)
MUTED = (92, 88, 80)
RULE = (40, 40, 40)
CRIMSON = (178, 34, 44)
NAVY = (27, 58, 92)
SEA = (127, 179, 200)
SEA_DEEP = (74, 130, 160)
SAND = (232, 217, 176)
SAND_DARK = (201, 178, 124)
SKY = (214, 231, 240)
LEAF = (74, 140, 92)
AMBER = (224, 148, 32)
FLAME = (238, 108, 32)
WHITE = (255, 255, 255)
CREAM_BOX = (255, 253, 247)
GREY_LINE = (196, 190, 176)


def load_font(filename, size):
    return ImageFont.truetype(str(FONT_DIR / filename), size)


def serif_bold(size):
    return load_font("DejaVuSerif-Bold.ttf", size)


def sans_bold(size):
    return load_font("DejaVuSans-Bold.ttf", size)


def sans(size):
    return load_font("DejaVuSans.ttf", size)


def wrap_lines(draw, text, font, max_width):
    """Split text into lines that fit max_width; assert each word fits."""
    words = text.split()
    lines = []
    current = ""
    for word in words:
        trial = word if not current else current + " " + word
        if draw.textlength(trial, font=font) <= max_width:
            current = trial
        else:
            assert draw.textlength(word, font=font) <= max_width, word
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def draw_wrapped(draw, x, y, text, font, fill, max_width, line_gap=4):
    """Draw wrapped text starting at (x, y); return the y after the block."""
    lines = wrap_lines(draw, text, font, max_width)
    _, _, _, line_h = draw.textbbox((0, 0), "Ag", font=font)
    cursor = y
    for line in lines:
        draw.text((x, cursor), line, font=font, fill=fill)
        cursor += line_h + line_gap
    return cursor


def draw_centered(draw, cx, y, text, font, fill):
    width = draw.textlength(text, font=font)
    draw.text((cx - width / 2, y), text, font=font, fill=fill)
    _, _, _, h = draw.textbbox((0, 0), text, font=font)
    return y + h


def burst_star(draw, cx, cy, r_out, r_in, fill, spikes=8):
    """Flat starburst centred on (cx, cy)."""
    pts = []
    for i in range(spikes * 2):
        import math

        ang = math.pi * i / spikes - math.pi / 2
        r = r_out if i % 2 == 0 else r_in
        pts.append((cx + r * math.cos(ang), cy + r * math.sin(ang)))
    draw.polygon(pts, fill=fill)


def dashed_arc(draw, box, start, end, fill, width=3, dash=14):
    """Draw an arc in short dashes so flight paths read as dotted routes."""
    step = 6
    angle = start
    while angle < end:
        draw.arc(box, angle, min(angle + step, end), fill=fill, width=width)
        angle += step + dash


def arrow_head(draw, tip_x, tip_y, dx, dy, size, fill):
    """Small triangle arrowhead pointing along (dx, dy)."""
    import math

    ang = math.atan2(dy, dx)
    left = ang + math.radians(150)
    right = ang - math.radians(150)
    p1 = (tip_x + size * math.cos(left), tip_y + size * math.sin(left))
    p2 = (tip_x + size * math.cos(right), tip_y + size * math.sin(right))
    draw.polygon([(tip_x, tip_y), p1, p2], fill=fill)


def location_pin(draw, x, y, label, font, fill=CRIMSON, label_fill=INK, above=True):
    """Dot marker with a short place label beside it."""
    draw.ellipse([x - 6, y - 6, x + 6, y + 6], fill=fill, outline=WHITE, width=2)
    ty = y - 24 if above else y + 10
    tw = draw.textlength(label, font=font)
    tx = min(max(x - tw / 2, 34), 990 - tw)
    draw.rectangle([tx - 4, ty - 2, tx + tw + 4, ty + 16], fill=WHITE)
    draw.text((tx, ty), label, font=font, fill=label_fill)


def tanker_ship(draw, x, y, scale=1.0):
    """Side-view tanker hull with deck tanks; (x, y) is the waterline centre."""
    w = int(150 * scale)
    h = int(26 * scale)
    draw.polygon(
        [(x - w // 2, y), (x + w // 2, y), (x + w // 2 - 16, y + h), (x - w // 2 + 16, y + h)],
        fill=(52, 64, 78),
        outline=INK,
    )
    draw.rectangle([x - w // 2 + 8, y - int(14 * scale), x + w // 2 - 8, y], fill=(120, 52, 44), outline=INK)
    for i in range(4):
        tx = x - w // 2 + 18 + i * int(30 * scale)
        draw.ellipse([tx, y - int(22 * scale), tx + int(22 * scale), y - int(12 * scale)], fill=(200, 200, 205), outline=INK)
    draw.rectangle([x + w // 2 - 26, y - int(30 * scale), x + w // 2 - 8, y - int(12 * scale)], fill=WHITE, outline=INK)


def draw_masthead(draw):
    draw.rectangle([14, 14, 1010, 1010], outline=RULE, width=3)
    draw.line([28, 30, 996, 30], fill=RULE, width=2)
    y = draw_centered(draw, 512, 38, "THE WORLD IN ONE DAY", serif_bold(46), INK)
    draw_centered(draw, 512, y + 8, "SUNDAY, 22 NOVEMBER 2026  \u2022  WORLD NEWS IN ONE IMAGE", sans_bold(21), CRIMSON)
    draw.line([28, 112, 996, 112], fill=RULE, width=2)
    draw.line([28, 117, 996, 117], fill=RULE, width=1)


def draw_lead_map(draw, box):
    """Gulf scene: land, sea, markers, flight arcs and a struck tanker."""
    x0, y0, x1, y1 = box
    draw.rectangle(box, fill=SEA, outline=RULE, width=2)
    # Iran landmass across the top-right
    draw.polygon(
        [(x0 + 250, y0), (x1, y0), (x1, y0 + 78), (x0 + 430, y0 + 96), (x0 + 300, y0 + 60)],
        fill=SAND, outline=SAND_DARK,
    )
    # Arabian side landmass on the left and bottom-left
    draw.polygon(
        [(x0, y0), (x0 + 250, y0), (x0 + 300, y0 + 60), (x0 + 210, y0 + 130),
         (x0 + 170, y0 + 190), (x0, y1)],
        fill=SAND, outline=SAND_DARK,
    )
    # Oman land at bottom-right
    draw.polygon(
        [(x0 + 430, y1), (x1, y1), (x1, y0 + 150), (x0 + 470, y0 + 165)],
        fill=SAND, outline=SAND_DARK,
    )
    small = sans_bold(13)
    draw.text((x0 + 452, y0 + 16), "IRAN", font=sans_bold(16), fill=(120, 90, 40))
    draw.text((x0 + 330, y0 + 96), "PERSIAN GULF", font=sans_bold(14), fill=(30, 80, 110))
    # Kuwait + US air base on the north-west shore
    kx, ky = x0 + 238, y0 + 52
    draw.rectangle([kx - 26, ky - 8, kx + 26, ky + 8], fill=(90, 90, 90), outline=INK)
    draw.line([kx - 22, ky, kx + 22, ky], fill=WHITE, width=2)
    location_pin(draw, kx, ky - 16, "KUWAIT \u00b7 US AIR BASE", small, above=True)
    burst_star(draw, kx + 30, ky - 4, 15, 7, FLAME)
    # Bahrain island dot mid-gulf, label above the dot to stay clear of the sea name
    bx, by = x0 + 258, y0 + 116
    draw.ellipse([bx - 12, by - 7, bx + 12, by + 7], fill=SAND, outline=SAND_DARK)
    location_pin(draw, bx, by, "BAHRAIN", small, above=True)
    # Flight arcs from Iran toward Kuwait and Bahrain
    dashed_arc(draw, [x0 + 180, y0 - 30, x0 + 560, y0 + 150], 150, 235, CRIMSON, width=4, dash=8)
    arrow_head(draw, kx + 18, ky - 18, -1, 0.4, 13, CRIMSON)
    dashed_arc(draw, [x0 + 250, y0 + 10, x0 + 520, y0 + 170], 140, 215, CRIMSON, width=4, dash=8)
    arrow_head(draw, bx + 14, by - 12, -1, 0.5, 12, CRIMSON)
    # Drone glyph near the arcs: body with four rotor dots
    dx, dy = x0 + 400, y0 + 44
    draw.line([dx - 11, dy - 8, dx + 11, dy + 8], fill=INK, width=3)
    draw.line([dx - 11, dy + 8, dx + 11, dy - 8], fill=INK, width=3)
    for rx, ry in [(-13, -10), (13, -10), (-13, 10), (13, 10)]:
        draw.ellipse([dx + rx - 4, dy + ry - 3, dx + rx + 4, dy + ry + 3], outline=INK, width=2)
    draw.ellipse([dx - 4, dy - 4, dx + 4, dy + 4], fill=INK)
    # Tanker off Oman with hit burst and smoke, label to its right
    tx, ty = x0 + 352, y1 - 46
    tanker_ship(draw, tx, ty, scale=1.0)
    burst_star(draw, tx - 30, ty - 26, 20, 9, FLAME)
    draw.ellipse([tx - 50, ty - 54, tx - 26, ty - 36], fill=(110, 110, 110))
    draw.ellipse([tx - 38, ty - 64, tx - 16, ty - 48], fill=(140, 140, 140))
    location_pin(draw, tx + 84, ty - 4, "TANKERS HIT OFF OMAN", small, above=True)
    draw.text((x0 + 170, y1 - 26), "GULF OF OMAN", font=sans_bold(13), fill=(30, 80, 110))
    for wx in range(x0 + 30, x1 - 30, 46):
        draw.arc([wx, y1 - 22, wx + 30, y1 - 8], 0, 180, fill=SEA_DEEP, width=2)


def draw_lead(draw):
    draw.text((28, 126), "LEAD  \u2022  MIDDLE EAST \u2014 GULF ESCALATION", font=sans_bold(17), fill=CRIMSON)
    headline = serif_bold(30)
    draw.text((28, 150), "Iran strikes US air base in Kuwait,", font=headline, fill=INK)
    draw.text((28, 186), "targets Bahrain; tankers hit off Oman", font=headline, fill=INK)
    draw_lead_map(draw, [28, 228, 648, 448])
    body = sans(15)
    bold15 = sans_bold(15)
    tx = 664
    ty = 232
    ty = draw_wrapped(draw, tx, ty, "Missiles and drones hit a US air base in Kuwait; Bahrain also targeted in wider Gulf attacks.", body, INK, 332)
    ty += 8
    ty = draw_wrapped(draw, tx, ty, "Multiple tankers struck off the Oman coast as Iran\u2013US naval tensions escalate.", body, INK, 332)
    ty += 8
    draw.rectangle([tx, ty, tx + 332, ty + 52], fill=(253, 238, 230), outline=CRIMSON, width=2)
    draw_wrapped(draw, tx + 10, ty + 6, "Why it leads: Gulf shipping and US bases in the firing line.", bold15, CRIMSON, 312)


def illo_europe_war(draw, box):
    x0, y0, x1, y1 = box
    draw.rectangle(box, fill=SKY, outline=GREY_LINE)
    ground = y1 - 18
    for i, (bw, bh) in enumerate([(34, 44), (28, 32), (38, 50), (26, 28)]):
        bx = x0 + 14 + i * 46
        draw.rectangle([bx, ground - bh, bx + bw, ground], fill=(96, 104, 116), outline=INK)
        for wy in range(ground - bh + 7, ground - 8, 12):
            draw.rectangle([bx + 6, wy, bx + 13, wy + 6], fill=(240, 220, 130))
    dashed_arc(draw, [x0 + 120, y0 - 26, x1 + 10, y0 + 70], 95, 175, CRIMSON, width=3)
    burst_star(draw, x0 + 128, ground - 48, 15, 7, FLAME)
    sea_y = y1 - 16
    draw.rectangle([x1 - 108, sea_y - 6, x1 - 6, y1 - 2], fill=SEA)
    draw.polygon([(x1 - 96, sea_y - 4), (x1 - 22, sea_y - 4), (x1 - 30, sea_y + 6), (x1 - 88, sea_y + 6)], fill=(70, 76, 86), outline=INK)
    draw.rectangle([x1 - 78, sea_y - 16, x1 - 38, sea_y - 4], fill=(150, 60, 50), outline=INK)
    burst_star(draw, x1 - 58, sea_y - 20, 11, 5, FLAME)


def illo_trade_deal(draw, box):
    x0, y0, x1, y1 = box
    draw.rectangle(box, fill=(238, 244, 238), outline=GREY_LINE)
    # EU flag: blue field with ring of gold dots
    draw.rectangle([x0 + 16, y0 + 12, x0 + 92, y0 + 46], fill=(0, 51, 153), outline=INK)
    import math

    for i in range(8):
        ang = math.pi * 2 * i / 8
        cx = x0 + 54 + 16 * math.cos(ang)
        cy = y0 + 29 + 9 * math.sin(ang)
        draw.ellipse([cx - 3, cy - 3, cx + 3, cy + 3], fill=(255, 204, 0))
    # Indonesia flag: red over white
    draw.rectangle([x1 - 92, y0 + 12, x1 - 16, y0 + 29], fill=(206, 17, 38), outline=INK)
    draw.rectangle([x1 - 92, y0 + 29, x1 - 16, y0 + 46], fill=WHITE, outline=INK)
    # Signed document in the middle, kept clear of both flags
    dx0, dy0 = x0 + 112, y0 + 10
    draw.rectangle([dx0, dy0, dx0 + 72, dy0 + 46], fill=WHITE, outline=INK, width=2)
    for ly in range(dy0 + 8, dy0 + 26, 8):
        draw.line([dx0 + 8, ly, dx0 + 64, ly], fill=MUTED, width=2)
    draw.line([dx0 + 8, dy0 + 38, dx0 + 32, dy0 + 33], fill=NAVY, width=2)
    draw.line([dx0 + 40, dy0 + 38, dx0 + 64, dy0 + 33], fill=CRIMSON, width=2)
    # Falling tariff bars along the bottom-left, label bottom-right
    base = y1 - 8
    heights = [22, 17, 11, 6]
    for i, hh in enumerate(heights):
        bx = x0 + 20 + i * 24
        draw.rectangle([bx, base - hh, bx + 16, base], fill=AMBER, outline=INK)
    draw.line([x0 + 16, base - 26, x0 + 108, base - 10], fill=LEAF, width=4)
    arrow_head(draw, x0 + 108, base - 10, 1, 0.3, 11, LEAF)
    label = "98.5% tariffs gone"
    lw = draw.textlength(label, font=sans_bold(14))
    draw.rectangle([x1 - 16 - lw - 8, base - 24, x1 - 8, base - 4], fill=WHITE)
    draw.text((x1 - 12 - lw, base - 22), label, font=sans_bold(14), fill=LEAF)


def illo_climate_deadlock(draw, box):
    x0, y0, x1, y1 = box
    draw.rectangle(box, fill=(240, 244, 250), outline=GREY_LINE)
    gx, gy, gr = x0 + 56, y0 + 48, 34
    draw.ellipse([gx - gr, gy - gr, gx + gr, gy + gr], fill=SEA, outline=NAVY, width=2)
    draw.polygon([(gx - 22, gy - 14), (gx - 4, gy - 22), (gx + 2, gy - 4), (gx - 12, gy + 6)], fill=LEAF)
    draw.polygon([(gx + 8, gy + 8), (gx + 24, gy + 14), (gx + 14, gy + 24)], fill=LEAF)
    draw.line([gx - gr, gy, gx + gr, gy], fill=NAVY, width=1)
    # Thermometer
    tx = x0 + 112
    draw.rectangle([tx, y0 + 14, tx + 12, y0 + 66], fill=WHITE, outline=INK)
    draw.rectangle([tx + 3, y0 + 30, tx + 9, y0 + 66], fill=CRIMSON)
    draw.ellipse([tx - 4, y0 + 62, tx + 16, y0 + 82], fill=CRIMSON, outline=INK)
    # Factory stacks with smoke
    for sx in (x0 + 150, x0 + 178):
        draw.rectangle([sx, y0 + 44, sx + 16, y1 - 14], fill=(110, 110, 110), outline=INK)
        draw.ellipse([sx - 2, y0 + 26, sx + 18, y0 + 44], fill=(160, 160, 160))
        draw.ellipse([sx + 2, y0 + 14, sx + 20, y0 + 30], fill=(185, 185, 185))
    # Deadlock: cross at top-right, opposing arrows along the bottom
    cx, cy = x1 - 40, y0 + 26
    draw.line([cx - 11, cy - 11, cx + 11, cy + 11], fill=CRIMSON, width=5)
    draw.line([cx - 11, cy + 11, cx + 11, cy - 11], fill=CRIMSON, width=5)
    ay = y1 - 18
    draw.line([x1 - 104, ay, x1 - 58, ay], fill=NAVY, width=4)
    arrow_head(draw, x1 - 58, ay, 1, 0, 11, NAVY)
    draw.line([x1 - 58, ay + 11, x1 - 104, ay + 11], fill=CRIMSON, width=4)
    arrow_head(draw, x1 - 104, ay + 11, -1, 0, 11, CRIMSON)
    draw.rectangle([x1 - 104, y0 + 40, x1 - 52, y0 + 58], fill=WHITE)
    draw.text((x1 - 98, y0 + 42), "COP31", font=sans_bold(16), fill=NAVY)


def illo_peru_quake(draw, box):
    x0, y0, x1, y1 = box
    draw.rectangle(box, fill=(250, 243, 230), outline=GREY_LINE)
    base = y1 - 22
    draw.polygon([(x0 + 16, base), (x0 + 84, y0 + 22), (x0 + 150, base)], fill=(150, 118, 84), outline=INK)
    draw.polygon([(x0 + 104, base), (x0 + 168, y0 + 34), (x0 + 228, base)], fill=(176, 140, 98), outline=INK)
    draw.polygon([(x0 + 72, y0 + 36), (x0 + 84, y0 + 22), (x0 + 96, y0 + 36), (x0 + 88, y0 + 42), (x0 + 80, y0 + 42)], fill=WHITE)
    draw.polygon([(x0 + 158, y0 + 46), (x0 + 168, y0 + 34), (x0 + 178, y0 + 46)], fill=WHITE)
    # Ground crack zigzag
    crack = [(x0 + 20, base + 8), (x0 + 70, base + 2), (x0 + 110, base + 10), (x0 + 150, base + 3), (x0 + 205, base + 9), (x0 + 250, base + 4)]
    draw.line(crack, fill=INK, width=3)
    # Seismograph trace
    pts = []
    for i in range(9):
        px = x1 - 92 + i * 10
        py = y0 + 30 + (14 if i % 2 == 0 else -12)
        pts.append((px, py))
    draw.line(pts, fill=CRIMSON, width=3)
    draw.ellipse([x1 - 84, y0 + 42, x1 - 14, y0 + 70], fill=CRIMSON, outline=WHITE, width=2)
    draw.text((x1 - 77, y0 + 47), "M 6.9", font=sans_bold(17), fill=WHITE)
    draw.text((x0 + 18, y0 + 8), "ANDES, PERU", font=sans_bold(13), fill=(110, 80, 40))


def illo_hongkong_vote(draw, box):
    x0, y0, x1, y1 = box
    draw.rectangle(box, fill=(244, 240, 250), outline=GREY_LINE)
    # Skyline silhouettes, kept below the place label
    for i, hh in enumerate([36, 50, 30, 44]):
        bx = x0 + 14 + i * 30
        draw.rectangle([bx, y1 - 10 - hh, bx + 22, y1 - 10], fill=(80, 88, 120), outline=INK)
    # Ballot box with paper and tick, clear of the voters label
    bx0, by0 = x0 + 186, y0 + 42
    draw.rectangle([bx0, by0, bx0 + 92, by0 + 34], fill=NAVY, outline=INK, width=2)
    draw.rectangle([bx0 + 26, by0 - 4, bx0 + 66, by0 + 4], fill=INK)
    draw.rectangle([bx0 + 34, by0 - 26, bx0 + 60, by0 - 2], fill=WHITE, outline=INK)
    draw.line([bx0 + 40, by0 - 14, bx0 + 46, by0 - 7], fill=LEAF, width=3)
    draw.line([bx0 + 46, by0 - 7, bx0 + 56, by0 - 21], fill=LEAF, width=3)
    draw.text((bx0 + 14, by0 + 9), "VOTE", font=sans_bold(16), fill=WHITE)
    draw.rectangle([x0 + 10, y0 + 5, x0 + 104, y0 + 23], fill=WHITE)
    draw.text((x0 + 14, y0 + 7), "HONG KONG", font=sans_bold(13), fill=NAVY)
    voters = "~5,700 voters"
    vw = draw.textlength(voters, font=sans_bold(14))
    draw.rectangle([x0 + 110, y0 + 5, x0 + 116 + vw, y0 + 25], fill=WHITE)
    draw.text((x0 + 113, y0 + 7), voters, font=sans_bold(14), fill=CRIMSON)


def illo_cricket_captain(draw, box):
    x0, y0, x1, y1 = box
    draw.rectangle(box, fill=(232, 244, 226), outline=GREY_LINE)
    draw.rectangle([x0 + 4, y1 - 30, x1 - 4, y1 - 4], fill=(110, 170, 90))
    # Stumps
    for i in range(3):
        sx = x0 + 120 + i * 14
        draw.rectangle([sx, y0 + 40, sx + 7, y1 - 28], fill=(240, 200, 90), outline=INK)
    draw.rectangle([x0 + 122, y0 + 36, x0 + 132, y0 + 41], fill=(240, 200, 90), outline=INK)
    draw.rectangle([x0 + 138, y0 + 36, x0 + 148, y0 + 41], fill=(240, 200, 90), outline=INK)
    # Bat leaning
    draw.polygon([(x0 + 66, y1 - 28), (x0 + 82, y1 - 28), (x0 + 96, y0 + 30), (x0 + 84, y0 + 26)], fill=(222, 184, 120), outline=INK)
    draw.line([x0 + 90, y0 + 28, x0 + 102, y0 + 12], fill=INK, width=4)
    # Ball
    draw.ellipse([x0 + 196, y0 + 52, x0 + 222, y0 + 78], fill=(190, 40, 50), outline=INK, width=2)
    draw.arc([x0 + 200, y0 + 54, x0 + 218, y0 + 76], 60, 300, fill=WHITE, width=2)
    # Captain cap + unanimous tick badge
    draw.polygon([(x1 - 84, y0 + 30), (x1 - 30, y0 + 30), (x1 - 38, y0 + 14), (x1 - 76, y0 + 14)], fill=(0, 110, 60), outline=INK)
    draw.rectangle([x1 - 88, y0 + 30, x1 - 24, y0 + 36], fill=(0, 110, 60), outline=INK)
    draw.ellipse([x1 - 62, y0 + 44, x1 - 28, y0 + 78], fill=LEAF, outline=WHITE, width=2)
    draw.line([x1 - 54, y0 + 61, x1 - 47, y0 + 69], fill=WHITE, width=4)
    draw.line([x1 - 47, y0 + 69, x1 - 35, y0 + 52], fill=WHITE, width=4)
    draw.rectangle([x0 + 10, y0 + 5, x0 + 108, y0 + 23], fill=WHITE)
    draw.text((x0 + 14, y0 + 7), "TEST CRICKET", font=sans_bold(13), fill=(0, 90, 50))


GRID_STORIES = [
    ("WAR / EUROPE", CRIMSON, illo_europe_war,
     "Russian missile hits Lviv, two killed",
     "Drones hit Russian cargo ship in Baltic; Finland tightens security."),
    ("TRADE", (0, 110, 60), illo_trade_deal,
     "EU\u2013Indonesia trade deal signed",
     "After ten years: 98.5% of tariffs eliminated."),
    ("CLIMATE", NAVY, illo_climate_deadlock,
     "COP31 talks deadlocked",
     "Standoff over fossil fuels and climate finance."),
    ("AMERICAS", (160, 90, 20), illo_peru_quake,
     "M6.9 quake shakes Peru\u2019s Andes",
     "No damage or casualties immediately reported."),
    ("ASIA", (90, 60, 140), illo_hongkong_vote,
     "Hong Kong voting begins",
     "Election Committee poll, ~5,700 voters; Trump\u2013Xi Shenzhen fallout."),
    ("SPORT", (0, 110, 60), illo_cricket_captain,
     "Cummins stays Australia captain",
     "Unanimous support to remain Test cricket captain."),
]


def draw_grid_cell(draw, x, y, w, h, story):
    kicker, colour, painter, headline, detail = story
    draw.rectangle([x, y, x + w, y + h], fill=CREAM_BOX, outline=RULE, width=2)
    draw.rectangle([x, y, x + w, y + 26], fill=colour)
    draw.text((x + 10, y + 4), kicker, font=sans_bold(15), fill=WHITE)
    painter(draw, [x + 8, y + 32, x + w - 8, y + 112])
    hy = draw_wrapped(draw, x + 10, y + 118, headline, sans_bold(15), INK, w - 20, line_gap=1)
    draw_wrapped(draw, x + 10, hy + 1, detail, sans(13), MUTED, w - 20, line_gap=1)


def draw_grid(draw):
    cell_w, cell_h, gap = 316, 202, 10
    xs = [28, 28 + cell_w + gap, 28 + 2 * (cell_w + gap)]
    ys = [460, 460 + cell_h + gap]
    for idx, story in enumerate(GRID_STORIES):
        draw_grid_cell(draw, xs[idx % 3], ys[idx // 3], cell_w, cell_h, story)


def draw_also_today(draw):
    y0 = 884
    draw.rectangle([28, y0, 996, 996], fill=NAVY, outline=RULE, width=2)
    draw.text((42, y0 + 8), "ALSO TODAY", font=sans_bold(17), fill=(255, 204, 0))
    items = [
        "Estonia to close border with Russia; Moscow decries \u2018new Iron Curtain\u2019",
        "Cyclone Akvan cancels 14 flights at Ranchi",
        "Air Niugini emergency landing in Philippines \u2014 all 146 survive",
        "Bolsonaro in ICU with bowel obstruction",
    ]
    col_w = 464
    positions = [(42, y0 + 36), (518, y0 + 36), (42, y0 + 72), (518, y0 + 72)]
    for (px, py), text in zip(positions, items):
        draw.ellipse([px, py + 5, px + 8, py + 13], fill=(255, 204, 0))
        draw_wrapped(draw, px + 14, py, text, sans(13), WHITE, col_w - 14, line_gap=1)


def build_poster():
    img = Image.new("RGB", (1024, 1024), PAPER)
    draw = ImageDraw.Draw(img)
    draw_masthead(draw)
    draw_lead(draw)
    draw_grid(draw)
    draw_also_today(draw)
    img.save(OUT_FILE, format="PNG")
    print(f"wrote {OUT_FILE} ({OUT_FILE.stat().st_size} bytes)")


if __name__ == "__main__":
    build_poster()
