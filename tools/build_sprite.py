#!/usr/bin/env python3
"""Build assets/icons/sprite.svg from the vendored Bootstrap Icons in assets/icons/src.

Usage in HTML: <svg class="ek-icon" aria-hidden="true"><use href="assets/icons/sprite.svg#bank"></use></svg>
"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "assets/icons/src"
symbols = []
for svg in sorted(SRC.glob("*.svg")):
    text = svg.read_text(encoding="utf-8")
    view_box = re.search(r'viewBox="([^"]+)"', text).group(1)
    inner = re.search(r"<svg[^>]*>(.*)</svg>", text, re.S).group(1).strip()
    symbols.append(f'  <symbol id="{svg.stem}" viewBox="{view_box}" fill="currentColor">{inner}</symbol>')
out = ('<svg xmlns="http://www.w3.org/2000/svg">\n'
       '  <!-- Bootstrap Icons v1.13.1, MIT License, (c) The Bootstrap Authors. See assets/icons/LICENSE-bootstrap-icons -->\n'
       + "\n".join(symbols) + "\n</svg>\n")
(ROOT / "assets/icons/sprite.svg").write_text(out, encoding="utf-8")
print(f"sprite.svg: {len(symbols)} symbols")
