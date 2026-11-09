#!/usr/bin/env python3
"""Generate the Wächter flow diagram (assets/img/waechter-flow.svg) and inline it
into index.html and waechter-flow.html between the waechter-svg markers.

All names in the diagram are invented examples, as on the current site.
"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
C = dict(ink="#16222e", steel="#4f5d6b", line="#d3dae0", paper="#eef1f3", white="#ffffff",
         signal="#1d6f47", tint="#e2f0e7", shadow="#5b6773", cloud="#3d5a78")


def esc(t: str) -> str:
    return t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def rich(line: str) -> str:
    """*real data* -> bold ink; [placeholder] -> bold shadow colour."""
    out = []
    for part in re.split(r"(\*[^*]+\*|\[[^\]]+\])", line):
        if not part:
            continue
        if part.startswith("*"):
            out.append(f'<tspan font-weight="600" fill="{C["ink"]}">{esc(part[1:-1])}</tspan>')
        elif part.startswith("["):
            out.append(f'<tspan font-weight="600" fill="{C["shadow"]}">{esc(part)}</tspan>')
        else:
            out.append(esc(part))
    return "".join(out)


def card(x, y, w, h, title, lines, *, stroke, dash=None, fill=C["white"], title_fill=None, sub=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    s = [f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="4" fill="{fill}" stroke="{stroke}" stroke-width="1.5"{d}/>',
         f'<text x="{x + 20}" y="{y + 32}" font-size="17" font-weight="600" fill="{title_fill or C["ink"]}">{esc(title)}</text>']
    ty = y + 56
    if sub:
        s.append(f'<text x="{x + 20}" y="{ty}" font-size="14" fill="{C["steel"]}">{esc(sub)}</text>')
        ty += 28
    for i, ln in enumerate(lines):
        s.append(f'<text x="{x + 20}" y="{ty + i * 24}" font-size="15.5" fill="{C["steel"]}">{rich(ln)}</text>')
    return "\n    ".join(s)


PREFIX = "ek-arrow"


def make_markers() -> str:
    return "".join(
        f'<marker id="{PREFIX}-{c[1:]}" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">'
        f'<path d="M0,0 L10,5 L0,10 z" fill="{c}"/></marker>' for c in (C["ink"], C["signal"], C["cloud"]))


def arrow(x1, y1, x2, y2, colour, label=None, lx=None, ly=None, dash=None, anchor="middle"):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    s = f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{colour}" stroke-width="2"{d} marker-end="url(#{PREFIX}-{colour[1:]})"/>'
    if label:
        s += f'\n    <rect x="{lx - 62}" y="{ly - 16}" width="124" height="22" fill="{C["white"]}"/>'
        s += f'\n    <text x="{lx}" y="{ly}" font-size="14" font-weight="500" fill="{colour}" text-anchor="{anchor}">{esc(label)}</text>'
    return s


def wide() -> str:
    W, H = 1200, 620
    global PREFIX
    PREFIX = "ek-arrow"
    markers = make_markers()

    # columns
    c1x, c2x, c3x, cw = 30, 400, 860, 310
    r1y, r2y, rh = 110, 360, 190

    parts = [
        f'<svg class="ek-flow ek-flow--wide" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" role="img" aria-labelledby="ek-flow-title ek-flow-desc" font-family="Fira Sans, Segoe UI, system-ui, sans-serif">',
        '  <title id="ek-flow-title">So arbeitet der Wächter</title>',
        '  <desc id="ek-flow-desc">Das Original bleibt im Haus. Der Wächter ersetzt Namen und vertrauliche Angaben durch Platzhalter und schickt nur diese Schattenkopie an die Cloud-KI. '
        'Die Antwort kommt mit Platzhaltern zurück, und erst im Haus setzt der Wächter die echten Angaben wieder ein. Beispiel mit erfundenen Angaben.</desc>',
        f'  <defs>{markers}</defs>',
        # zones
        f'  <rect x="10" y="60" width="770" height="520" rx="4" fill="{C["white"]}" stroke="{C["ink"]}" stroke-width="3"/>',
        f'  <text x="30" y="44" font-size="16" font-weight="600" fill="{C["ink"]}">Ihr Haus</text>',
        f'  <text x="104" y="44" font-size="15" fill="{C["steel"]}">Gerät im Betrieb oder eigener Server in Deutschland. Originale verlassen diesen Bereich nie.</text>',
        f'  <rect x="380" y="76" width="350" height="488" rx="4" fill="{C["tint"]}"/>',
        f'  <text x="400" y="98" font-size="14" font-weight="600" fill="{C["signal"]}">Wächter: ersetzt und setzt wieder ein</text>',
        f'  <rect x="840" y="60" width="350" height="520" rx="4" fill="none" stroke="{C["cloud"]}" stroke-width="2" stroke-dasharray="8 6"/>',
        f'  <text x="860" y="44" font-size="16" font-weight="600" fill="{C["cloud"]}">Cloud-KI, nur wenn Sie es wollen</text>',
        # row 1
        "    " + card(c1x, r1y, cw, rh, "1  Original", ["*Frau Muster Alpha* von der", "*Muster GmbH* bittet um Rückruf", "zur Rechnung *RE-2026-0815*", "über 4.800 €."], stroke=C["ink"], sub="Dokument auf dem Gerät im Haus"),
        "    " + card(c2x + 10, r1y, cw, rh, "2  Schattenkopie", ["[Person 1] von der", "[Firma 1] bittet um Rückruf", "zur Rechnung [Kennung 1]", "über 4.800 €."], stroke=C["signal"], sub="Namen und Kennungen ersetzt"),
        "    " + card(c3x, r1y, cw, rh, "3  Cloud-KI arbeitet", ["Aufgabe: Rückruf vorbereiten,", "Antwortschreiben entwerfen.", "Sie sieht nur [Person 1],", "[Firma 1] und [Kennung 1]."], stroke=C["cloud"], dash="6 5", title_fill=C["cloud"], sub="z. B. ChatGPT oder Claude"),
        # row 2
        "    " + card(c3x, r2y, cw, rh, "Antwort im Schatten", ["Sehr geehrte [Person 1],", "gern rufen wir Sie zur", "Rechnung [Kennung 1] zurück.", "Mit freundlichen Grüßen"], stroke=C["cloud"], dash="6 5", title_fill=C["cloud"], sub="kommt mit Platzhaltern zurück"),
        "    " + card(c2x + 10, r2y, cw, rh, "Zuordnung im Haus", ["[Person 1]  =  *Frau Muster Alpha*", "[Firma 1]  =  *Muster GmbH*", "[Kennung 1]  =  *RE-2026-0815*", "Die Liste verlässt das Haus nie."], stroke=C["signal"], sub="Wächter setzt echte Angaben ein"),
        "    " + card(c1x, r2y, cw, rh, "4  Antwort mit echten Angaben", ["Sehr geehrte *Frau Muster Alpha*,", "gern rufen wir Sie zur", "Rechnung *RE-2026-0815* zurück.", "Mit freundlichen Grüßen"], stroke=C["ink"], sub="fertig zur Freigabe durch Sie"),
        # arrows
        "    " + arrow(c1x + cw + 4, r1y + 95, c2x + 4, r1y + 95, C["signal"]),
        "    " + arrow(c2x + 10 + cw + 4, r1y + 95, c3x - 6, r1y + 95, C["cloud"], "nur der Schatten", 800, r1y + 82, dash="6 5"),
        "    " + arrow(c3x + cw / 2, r1y + rh + 6, c3x + cw / 2, r2y - 8, C["cloud"], dash="6 5"),
        "    " + arrow(c3x - 4, r2y + 95, c2x + 10 + cw + 6, r2y + 95, C["cloud"], "Antwort zurück", 800, r2y + 82, dash="6 5"),
        "    " + arrow(c2x + 6, r2y + 95, c1x + cw + 6, r2y + 95, C["signal"]),
        f'  <text x="{W - 20}" y="608" font-size="13" fill="{C["steel"]}" text-anchor="end">Beispiel mit erfundenen Angaben.</text>',
        "</svg>",
    ]
    return "\n".join(parts) + "\n"


def tall() -> str:
    """Stacked version for narrow screens (shown below the md breakpoint)."""
    global PREFIX
    PREFIX = "ek-arrowt"
    markers = make_markers()
    W, cw, x = 400, 340, 30
    rh, gap = 190, 36
    y = 0
    p = [f'<svg class="ek-flow ek-flow--tall" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} HEIGHT" role="img" aria-labelledby="ek-flowt-title ek-flowt-desc" font-family="Fira Sans, Segoe UI, system-ui, sans-serif">',
         '  <title id="ek-flowt-title">So arbeitet der Wächter</title>',
         '  <desc id="ek-flowt-desc">Das Original bleibt im Haus. Der Wächter ersetzt Namen und vertrauliche Angaben durch Platzhalter und schickt nur diese Schattenkopie an die Cloud-KI. '
         'Die Antwort kommt mit Platzhaltern zurück, und erst im Haus setzt der Wächter die echten Angaben wieder ein. Beispiel mit erfundenen Angaben.</desc>',
         f'  <defs>{markers}</defs>']

    def zone(y0, n, label, colour, dashed):
        h = 50 + n * rh + (n - 1) * gap + 24
        d = ' stroke-dasharray="8 6"' if dashed else ""
        sw = 2 if dashed else 3
        p.append(f'  <rect x="10" y="{y0}" width="{W - 20}" height="{h}" rx="4" fill="{"none" if dashed else C["white"]}" stroke="{colour}" stroke-width="{sw}"{d}/>')
        p.append(f'  <text x="{x}" y="{y0 + 32}" font-size="16" font-weight="600" fill="{colour}">{esc(label)}</text>')
        return y0 + 50, y0 + h

    cy, zend = zone(10, 2, "Ihr Haus: Originale bleiben hier", C["ink"], False)
    p.append("    " + card(x, cy, cw, rh, "1  Original", ["*Frau Muster Alpha* von der", "*Muster GmbH* bittet um Rückruf", "zur Rechnung *RE-2026-0815*", "über 4.800 €."], stroke=C["ink"], sub="Dokument auf dem Gerät im Haus"))
    p.append("    " + arrow(W / 2, cy + rh + 4, W / 2, cy + rh + gap - 6, C["signal"]))
    cy2 = cy + rh + gap
    p.append("    " + card(x, cy2, cw, rh, "2  Schattenkopie", ["[Person 1] von der", "[Firma 1] bittet um Rückruf", "zur Rechnung [Kennung 1]", "über 4.800 €."], stroke=C["signal"], fill=C["tint"], sub="Wächter ersetzt Namen und Kennungen"))
    z2 = zend + 40
    p.append("    " + arrow(W - 50, cy2 + rh + 4, W - 50, z2 + 50 - 6, C["cloud"], "nur der Schatten", W - 130, zend + 26, dash="6 5"))
    cy, zend2 = zone(z2, 2, "Cloud-KI, nur wenn Sie es wollen", C["cloud"], True)
    p.append("    " + card(x, cy, cw, rh, "3  Cloud-KI arbeitet", ["Aufgabe: Rückruf vorbereiten,", "Antwortschreiben entwerfen.", "Sie sieht nur [Person 1],", "[Firma 1] und [Kennung 1]."], stroke=C["cloud"], dash="6 5", title_fill=C["cloud"], sub="z. B. ChatGPT oder Claude"))
    p.append("    " + arrow(W / 2, cy + rh + 4, W / 2, cy + rh + gap - 6, C["cloud"], dash="6 5"))
    cy2 = cy + rh + gap
    p.append("    " + card(x, cy2, cw, rh, "Antwort im Schatten", ["Sehr geehrte [Person 1],", "gern rufen wir Sie zur", "Rechnung [Kennung 1] zurück.", "Mit freundlichen Grüßen"], stroke=C["cloud"], dash="6 5", title_fill=C["cloud"], sub="kommt mit Platzhaltern zurück"))
    z3 = zend2 + 40
    p.append("    " + arrow(W - 50, cy2 + rh + 4, W - 50, z3 + 50 - 6, C["cloud"], "Antwort zurück", W - 130, zend2 + 26, dash="6 5"))
    cy, zend3 = zone(z3, 2, "Wieder im Haus", C["ink"], False)
    p.append("    " + card(x, cy, cw, rh, "Zuordnung im Haus", ["[Person 1]  =  *Frau Muster Alpha*", "[Firma 1]  =  *Muster GmbH*", "[Kennung 1]  =  *RE-2026-0815*", "Die Liste verlässt das Haus nie."], stroke=C["signal"], fill=C["tint"], sub="Wächter setzt echte Angaben ein"))
    p.append("    " + arrow(W / 2, cy + rh + 4, W / 2, cy + rh + gap - 6, C["signal"]))
    cy2 = cy + rh + gap
    p.append("    " + card(x, cy2, cw, rh, "4  Antwort mit echten Angaben", ["Sehr geehrte *Frau Muster Alpha*,", "gern rufen wir Sie zur", "Rechnung *RE-2026-0815* zurück.", "Mit freundlichen Grüßen"], stroke=C["ink"], sub="fertig zur Freigabe durch Sie"))
    H = zend3 + 34
    p.append(f'  <text x="{W - 10}" y="{H - 8}" font-size="13" fill="{C["steel"]}" text-anchor="end">Beispiel mit erfundenen Angaben.</text>')
    p.append("</svg>")
    return "\n".join(p).replace("HEIGHT", str(H)) + "\n"


wide_svg = wide()
(ROOT / "assets/img/waechter-flow.svg").write_text(wide_svg, encoding="utf-8")
tall_svg = tall()
(ROOT / "assets/img/waechter-flow-mobile.svg").write_text(tall_svg, encoding="utf-8")
svg = wide_svg + tall_svg

for page in ("index.html", "waechter-flow.html"):
    path = ROOT / page
    if not path.exists():
        continue
    html = path.read_text(encoding="utf-8")
    new, n = re.subn(r"(<!-- waechter-svg:start -->).*?(<!-- waechter-svg:end -->)",
                     lambda m: m.group(1) + "\n" + svg + m.group(2), html, flags=re.S)
    if n:
        path.write_text(new, encoding="utf-8")
        print(f"inlined flow into {page}")
print("wrote assets/img/waechter-flow.svg and waechter-flow-mobile.svg")
