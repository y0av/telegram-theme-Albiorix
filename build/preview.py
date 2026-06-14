#!/usr/bin/env python3
"""
Render accurate Albiorix previews from the exact palette (no guess-work):

  assets/preview.png     a phone chat mock-up using the real theme colours
  assets/palette.png     labelled swatches of the key roles

Rendered at 2x and downsampled for crisp anti-aliasing.  Run: python3 build/preview.py
"""
import os, sys
from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from palette import hx

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS = os.path.join(ROOT, "assets")
S = 2  # supersample factor
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FONTB = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

def C(tok, a=255):
    r, g, b = int(hx(tok)[0:2], 16), int(hx(tok)[2:4], 16), int(hx(tok)[4:6], 16)
    return (r, g, b, a)

def f(size, bold=False):
    return ImageFont.truetype(FONTB if bold else FONT, size * S)

def wrap(draw, text, font, max_w):
    words, lines, cur = text.split(), [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if draw.textlength(t, font=font) <= max_w:
            cur = t
        else:
            lines.append(cur); cur = w
    if cur:
        lines.append(cur)
    return lines

def circle_avatar(size):
    """Round crop of the ring-planet icon for the chat avatar."""
    path = os.path.join(ASSETS, "icon.png")
    im = Image.open(path).convert("RGBA").resize((size, size), Image.LANCZOS)
    mask = Image.new("L", (size, size), 0)
    ImageDraw.Draw(mask).ellipse((0, 0, size, size), fill=255)
    im.putalpha(mask)
    return im

def grad_bubble(w, h, top, bot, radius):
    """Vertical gradient rounded bubble (RGBA)."""
    g = Image.new("RGB", (1, h))
    for y in range(h):
        t = y / max(1, h - 1)
        g.putpixel((0, y), tuple(round(top[i] + (bot[i] - top[i]) * t) for i in range(3)))
    g = g.resize((w, h))
    mask = Image.new("L", (w, h), 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, w - 1, h - 1), radius=radius, fill=255)
    out = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    out.paste(g, (0, 0), mask)
    return out


def render_chat():
    W, H = 760 * S, 1480 * S
    img = Image.new("RGBA", (W, H), C("bgDeep"))
    d = ImageDraw.Draw(img)

    pad = 22 * S
    statusH = 38 * S
    barH = 92 * S

    # ── chat wallpaper behind messages ──
    wp = Image.open(os.path.join(ASSETS, "wallpaper.png")).convert("RGB")
    area_top = statusH + barH
    area = (W, H - area_top - 100 * S)
    # cover-crop
    sc = max(area[0] / wp.width, area[1] / wp.height)
    wp2 = wp.resize((int(wp.width * sc), int(wp.height * sc)), Image.LANCZOS)
    cx, cy = (wp2.width - area[0]) // 2, (wp2.height - area[1]) // 2
    wp2 = wp2.crop((cx, cy, cx + area[0], cy + area[1]))
    img.paste(wp2, (0, area_top))

    # ── status bar ──
    d.rectangle((0, 0, W, statusH), fill=C("bgDeep"))
    d.text((pad, statusH // 2), "9:41", font=f(15, True), fill=C("text"), anchor="lm")
    for i, r in enumerate((26, 18, 10)):  # faux signal/wifi/batt dots
        x = W - pad - i * 22 * S
        d.ellipse((x - 5 * S, statusH//2 - 5*S, x + 5*S, statusH//2 + 5*S), fill=C("textSub"))

    # ── action bar ──
    d.rectangle((0, statusH, W, statusH + barH), fill=C("surface"))
    by = statusH + barH // 2
    d.text((pad, by), "‹", font=f(34, True), fill=C("accent"), anchor="lm")
    av = circle_avatar(56 * S)
    img.paste(av, (pad + 30 * S, statusH + (barH - 56 * S)//2), av)
    tx = pad + 30 * S + 56 * S + 16 * S
    d.text((tx, by - 13 * S), "Albiorix", font=f(21, True), fill=C("text"), anchor="lm")
    d.text((tx, by + 13 * S), "moon of Saturn · online",
           font=f(14), fill=C("accent"), anchor="lm")
    d.text((W - pad, by), "⋮", font=f(28, True), fill=C("textSub"), anchor="rm")
    # vector phone glyph
    px, pyy = W - pad - 30 * S, by
    d.arc((px-9*S, pyy-9*S, px+9*S, pyy+9*S), 100, 200, fill=C("textSub"), width=max(2, S*2))

    # ── messages ──
    y = area_top + 22 * S
    rad = 22 * S
    maxw = int(W * 0.72)

    def service(text):
        nonlocal y
        fnt = f(13, True)
        tw = d.textlength(text, font=fnt)
        bw = tw + 28 * S
        x0 = (W - bw)//2
        d.rounded_rectangle((x0, y, x0 + bw, y + 30 * S), radius=15 * S,
                            fill=C("serviceBg", 0xcc))
        d.text((W//2, y + 15 * S), text, font=fnt, fill=C("text"), anchor="mm")
        y += 30 * S + 18 * S

    def bubble(text, out=False, time="", reply=None, link=False):
        nonlocal y
        fnt = f(16)
        tfnt = f(11)
        inner = maxw - 28 * S
        lines = wrap(d, text, fnt, inner)
        lh = fnt.getbbox("Ay")[3] + 6 * S
        rep_h = 40 * S if reply else 0
        bh = 16 * S + rep_h + len(lines) * lh + 14 * S
        # measure width
        tw = max([d.textlength(l, font=fnt) for l in lines] + ([d.textlength(reply[1], font=tfnt)] if reply else [0]))
        bw = int(min(maxw, max(tw + 28 * S, 90 * S)))
        x0 = (W - pad - bw) if out else pad
        if out:
            b = grad_bubble(bw, bh, C("outBubble")[:3], C("outBubbleGrad")[:3], rad)
            img.paste(b, (x0, y), b)
        else:
            d.rounded_rectangle((x0, y, x0 + bw, y + bh), radius=rad, fill=C("inBubble"))
        ty = y + 12 * S
        tcol = C("text") if out else C("text")
        if reply:
            d.rounded_rectangle((x0 + 12*S, ty, x0 + 15*S, ty + 32*S), radius=2*S,
                                fill=C("accent") if not out else C("cfeae3"))
            d.text((x0 + 24*S, ty), reply[0], font=f(12, True),
                   fill=C("accent") if not out else C("cfeae3"), anchor="lt")
            d.text((x0 + 24*S, ty + 16*S), reply[1], font=tfnt,
                   fill=C("textSub") if not out else C("cfeae3"), anchor="lt")
            ty += rep_h
        for i, l in enumerate(lines):
            col = tcol
            d.text((x0 + 14 * S, ty), l, font=fnt, fill=col)
            if link and i == len(lines) - 1:  # underline last line as a link demo
                lw = d.textlength(l, font=fnt)
                lc = C("accentText") if out else C("accent")
                d.text((x0 + 14 * S, ty), l, font=fnt, fill=lc)
                d.line((x0+14*S, ty+lh-4*S, x0+14*S+lw, ty+lh-4*S), fill=lc, width=max(1,S))
            ty += lh
        # time + checks
        tcol2 = C("outTimeText" if False else "b9ddd5") if out else C("textSub")
        ttxt = time
        d.text((x0 + bw - (24*S if out else 14*S), y + bh - 8*S), ttxt,
               font=tfnt, fill=tcol2, anchor="rs")
        if out:  # double check
            cx = x0 + bw - 16 * S
            cyy = y + bh - 12 * S
            for dx in (0, 5 * S):
                d.line((cx+dx, cyy, cx+dx+3*S, cyy+4*S), fill=C("cfeae3"), width=max(1,S))
                d.line((cx+dx+3*S, cyy+4*S, cx+dx+9*S, cyy-4*S), fill=C("cfeae3"), width=max(1,S))
        y += bh + 12 * S

    service("TODAY")
    bubble("Found a new moon orbiting Saturn tonight.", out=False, time="21:04")
    bubble("They're calling it Albiorix.", out=False, time="21:04")
    bubble("Perfect name for a dark theme.", out=True, time="21:06")
    bubble("Deep space indigo, one aurora-teal accent. Docs here: yoav.xyz",
           out=True, time="21:06", link=True)
    bubble("Looks incredible — installing it now.", out=False, time="21:07",
           reply=("Albiorix", "Deep space indigo, one aurora-teal accent…"))

    # ── input bar ──
    iy0 = H - 96 * S
    d.rectangle((0, iy0, W, H), fill=C("surface"))
    # vector smiley
    sx, sy = pad + 16 * S, iy0 + 48 * S
    d.ellipse((sx-12*S, sy-12*S, sx+12*S, sy+12*S), outline=C("textSub"), width=max(2, S*2))
    d.ellipse((sx-6*S, sy-5*S, sx-2*S, sy-1*S), fill=C("textSub"))
    d.ellipse((sx+2*S, sy-5*S, sx+6*S, sy-1*S), fill=C("textSub"))
    d.arc((sx-7*S, sy-4*S, sx+7*S, sy+7*S), 20, 160, fill=C("textSub"), width=max(2, S*2))
    pill = (pad + 40 * S, iy0 + 22 * S, W - 90 * S, iy0 + 74 * S)
    d.rounded_rectangle(pill, radius=26 * S, fill=C("bgDeep"))
    d.text((pill[0] + 20 * S, iy0 + 48 * S), "Message", font=f(16),
           fill=C("textDim"), anchor="lm")
    # vector paperclip-ish attach (diagonal rounded line)
    ax, ay = pill[2] - 20 * S, iy0 + 48 * S
    d.line((ax-2*S, ay-10*S, ax-2*S, ay+8*S), fill=C("textSub"), width=max(2, S*2))
    d.arc((ax-12*S, ay-10*S, ax+8*S, ay+6*S), 200, 360, fill=C("textSub"), width=max(2, S*2))
    # send button
    sb = (W - 74 * S, iy0 + 22 * S, W - 22 * S, iy0 + 74 * S)
    d.ellipse(sb, fill=C("accentFill"))
    scx, scy = (sb[0]+sb[2])//2, (sb[1]+sb[3])//2
    d.polygon([(scx-9*S, scy-9*S), (scx+11*S, scy), (scx-9*S, scy+9*S),
               (scx-4*S, scy)], fill=C("onAccent"))

    out = img.convert("RGB").resize((W // S, H // S), Image.LANCZOS)
    out.save(os.path.join(ASSETS, "preview.png"), "PNG")
    print("  wrote assets/preview.png")


def render_palette():
    rows = [
        ("Base", ["bgDeep", "bg", "surface", "surface2", "border"]),
        ("Bubbles", ["inBubble", "outBubble", "outBubbleGrad", "serviceBg"]),
        ("Accent", ["accent", "accentText", "accentFill", "accentDeep"]),
        ("Text", ["text", "textSub", "textDim"]),
        ("Semantic", ["red", "green", "gold", "orange"]),
    ]
    cellw, cellh, gap, lblw, top = 150*S, 76*S, 14*S, 150*S, 30*S
    cols = max(len(r[1]) for r in rows)
    W = lblw + cols*(cellw+gap) + gap
    H = top*2 + len(rows)*(cellh+gap)
    img = Image.new("RGB", (W, H), C("bgDeep")[:3])
    d = ImageDraw.Draw(img)
    for ri, (label, toks) in enumerate(rows):
        y = top + ri*(cellh+gap)
        d.text((gap*2, y + cellh//2), label, font=f(17, True), fill=C("text"), anchor="lm")
        for ci, tok in enumerate(toks):
            x = lblw + ci*(cellw+gap)
            col = C(tok)
            d.rounded_rectangle((x, y, x+cellw, y+cellh), radius=14*S, fill=col)
            lum = 0.2126*col[0]+0.7152*col[1]+0.0722*col[2]
            tc = C("bgDeep") if lum > 140 else C("text")
            d.text((x+14*S, y+16*S), tok, font=f(12, True), fill=tc)
            d.text((x+14*S, y+cellh-22*S), "#"+hx(tok), font=f(11), fill=tc)
    img.resize((W//S, H//S), Image.LANCZOS).save(os.path.join(ASSETS, "palette.png"), "PNG")
    print("  wrote assets/palette.png")


if __name__ == "__main__":
    print("Albiorix preview")
    render_chat()
    render_palette()
    print("done.")
