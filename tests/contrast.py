#!/usr/bin/env python3
"""WCAG 2.x contrast check for the EIGENKERN concept palette.

Reads the colour tokens from assets/css/tokens.css (:root custom properties)
and checks every foreground/background pair the design actually uses.
Exit code 1 if any pair falls below its WCAG AA threshold.
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CSS = (ROOT / "assets/css/tokens.css").read_text(encoding="utf-8")
TOKENS = dict(re.findall(r"--(ek-[a-z0-9-]+):\s*(#[0-9a-fA-F]{6})\s*;", CSS))

# (foreground, background, minimum ratio, where it is used)
PAIRS = [
    ("ek-ink", "ek-white", 4.5, "body text and headings on white"),
    ("ek-ink", "ek-paper", 4.5, "body text on paper sections"),
    ("ek-steel", "ek-white", 4.5, "secondary text on white"),
    ("ek-steel", "ek-paper", 4.5, "secondary text on paper"),
    ("ek-white", "ek-signal", 4.5, "primary button label"),
    ("ek-white", "ek-signal-dark", 4.5, "primary button hover"),
    ("ek-signal", "ek-white", 4.5, "links and signal text on white"),
    ("ek-signal", "ek-paper", 4.5, "links on paper"),
    ("ek-signal-dark", "ek-signal-tint", 4.5, "signal label on tint"),
    ("ek-white", "ek-ink", 4.5, "text on ink sections"),
    ("ek-mist", "ek-ink", 4.5, "secondary text on ink"),
    ("ek-signal-light", "ek-ink", 4.5, "signal text and links on ink"),
    ("ek-ink", "ek-signal-light", 4.5, "button label on ink sections"),
    ("ek-shadow", "ek-white", 4.5, "placeholder token text"),
    ("ek-cloud", "ek-white", 4.5, "cloud zone labels"),
    ("ek-signal", "ek-signal-tint", 4.5, "Wächter label on the tint band (diagram)"),
    ("ek-steel", "ek-signal-tint", 4.5, "diagram card text on tint (mobile flow)"),
    ("ek-shadow", "ek-signal-tint", 4.5, "placeholders on tint (mobile flow)"),
    ("ek-ink", "ek-signal-tint", 4.5, "real names on tint (mobile flow)"),
    ("ek-steel", "ek-white", 3.0, "UI borders of inputs/tokens (non-text, 1.4.11)"),
    ("ek-signal", "ek-white", 3.0, "focus ring on white (non-text, 1.4.11)"),
    ("ek-signal-light", "ek-ink", 3.0, "focus ring on ink (non-text, 1.4.11)"),
]


def lum(hex_colour: str) -> float:
    rgb = [int(hex_colour[i:i + 2], 16) / 255 for i in (1, 3, 5)]
    lin = [c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4 for c in rgb]
    return 0.2126 * lin[0] + 0.7152 * lin[1] + 0.0722 * lin[2]


def ratio(a: str, b: str) -> float:
    la, lb = sorted((lum(a), lum(b)), reverse=True)
    return (la + 0.05) / (lb + 0.05)


def main() -> int:
    failed = 0
    print(f"{'foreground':<16} {'background':<16} {'ratio':>6}  {'min':>4}  result  use")
    for fg, bg, minimum, use in PAIRS:
        if fg not in TOKENS or bg not in TOKENS:
            print(f"missing token: {fg} or {bg}")
            failed += 1
            continue
        r = ratio(TOKENS[fg], TOKENS[bg])
        ok = r >= minimum
        failed += not ok
        print(f"{fg:<16} {bg:<16} {r:6.2f}  {minimum:4.1f}  {'pass' if ok else 'FAIL':<6}  {use}")
    print(f"\n{len(PAIRS) - failed}/{len(PAIRS)} pairs pass WCAG AA")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
