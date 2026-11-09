#!/usr/bin/env python3
"""Combine the PNG renders into one overview JPG (renders/overview.jpg).
Needs Pillow and fontTools (to read the self-hosted WOFF2 Fira Sans)."""
import tempfile
import textwrap
from pathlib import Path

from fontTools.ttLib import TTFont
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
R = ROOT / "renders"
tmp = Path(tempfile.mkdtemp())
for w in ("400-normal", "600-normal"):
    f = TTFont(ROOT / f"assets/fonts/fira-sans/fira-sans-latin-{w}.woff2")
    f.flavor = None
    f.save(tmp / f"fira-{w}.ttf")


def sc(im, w):
    return im.resize((w, round(im.size[1] * w / im.size[0])), Image.LANCZOS)


D = sc(Image.open(R / "homepage-desktop-1440.png").convert("RGB"), 900)
M = sc(Image.open(R / "homepage-mobile-390-top.png").convert("RGB"), 390)
S = sc(Image.open(R / "styletile.png").convert("RGB"), 900)
F = sc(Image.open(R / "waechter-flow.png").convert("RGB"), 900)
pad, top = 60, 190
W = pad + 900 + pad + 390 + pad + 900 + pad
H = top + max(D.size[1], M.size[1], S.size[1] + F.size[1] + pad * 2 + 560) + pad
cv = Image.new("RGB", (W, H), "#eef1f3")
dr = ImageDraw.Draw(cv)
title = ImageFont.truetype(str(tmp / "fira-600-normal.ttf"), 54)
body = ImageFont.truetype(str(tmp / "fira-400-normal.ttf"), 26)
bold = ImageFont.truetype(str(tmp / "fira-600-normal.ttf"), 26)
dr.text((pad, 48), "EIGENKERN: Ihre eigene KI. Im eigenen Haus.", font=title, fill="#16222e")
dr.text((pad, 122), "Homepage concept, working Bootstrap 5.3 prototype for the Odoo website builder  |  "
        "moltidenchi.github.io/eigenkern-homepage-concept", font=body, fill="#4f5d6b")
x1 = pad
x2 = x1 + 900 + pad
x3 = x2 + 390 + pad


def place(im, x, y, label):
    dr.text((x, y - 40), label, font=bold, fill="#16222e")
    cv.paste(im, (x, y))
    dr.rectangle([x - 1, y - 1, x + im.size[0], y + im.size[1]], outline="#d3dae0")


place(D, x1, top + 40, "1  Desktop 1440 px, full page")
place(M, x2, top + 40, "2  Mobile 390 px")
place(S, x3, top + 40, "3  Style tile")
fy = top + 40 + S.size[1] + pad + 40
place(F, x3, fy, "4  Wächter flow")
ny = fy + F.size[1] + pad + 40
dr.text((x3, ny - 40), "5  Odoo approach", font=bold, fill="#16222e")
text = ("Custom theme module (extending theme_eigenkern) on Odoo's default website theme: plain Bootstrap 5.3, "
        "palette and self-hosted Fira Sans in primary_variables.scss and the module's static folder, every block a "
        "custom snippet; FAQ and call to action reuse s_faq_collapse and s_call_to_action, so texts stay editable "
        "in the website builder.")
y = ny
for line in textwrap.wrap(text, 62):
    dr.text((x3, y), line, font=body, fill="#16222e")
    y += 38
y += 20
for line in ("Fonts self-hosted (SIL OFL), no Google Fonts request.", "WCAG AA: 22 of 22 colour pairs pass.",
             "Built with AI assistance."):
    dr.text((x3, y), line, font=body, fill="#4f5d6b")
    y += 38
cv = cv.crop((0, 0, W, max(y + pad, top + 40 + D.size[1] + pad)))
out = R / "overview.jpg"
cv.save(out, quality=86, optimize=True, progressive=True)
print(f"{out.relative_to(ROOT)}  {cv.size[0]}x{cv.size[1]}  {out.stat().st_size // 1024} KB")
