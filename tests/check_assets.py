#!/usr/bin/env python3
"""Static checks for the prototype pages.

1. Every local href/src/<use href> in the HTML and every url() in our CSS resolves to a file.
2. Every sprite reference (sprite.svg#id) exists as a <symbol id> in the sprite.
3. No stylesheet, script, font or image is loaded from another host (GDPR: no CDN, no Google Fonts).
4. In-page anchors (#id) point to an element that exists.
5. No e-mail addresses other than the neutral placeholder, and no secrets-looking strings.
"""
import re
import sys
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PAGES = ["index.html", "styletile.html", "waechter-flow.html"]
CSS = sorted((ROOT / "assets/css").glob("*.css"))
SPRITE = (ROOT / "assets/icons/sprite.svg").read_text(encoding="utf-8")
SYMBOLS = set(re.findall(r'<symbol id="([^"]+)"', SPRITE))
ALLOWED_EMAIL = {"info@beispiel.de"}
SECRET_PATTERNS = [r"gh[pousr]_[A-Za-z0-9]{20,}", r"AKIA[0-9A-Z]{16}", r"-----BEGIN [A-Z ]*PRIVATE KEY-----", r"sk-[A-Za-z0-9]{20,}"]

errors: list[str] = []


class Collector(HTMLParser):
    def __init__(self):
        super().__init__()
        self.refs: list[tuple[str, str, str]] = []  # (tag, attr, value)
        self.ids: set[str] = set()

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if "id" in a:
            self.ids.add(a["id"])
        for attr in ("href", "src"):
            if a.get(attr):
                self.refs.append((tag, attr, a[attr]))
        if tag == "link" and a.get("rel") in ("stylesheet", "preload", "icon") and a.get("href", "").startswith(("http:", "https:", "//")):
            errors.append(f"external asset via <link rel={a.get('rel')}>: {a['href']}")
        if tag in ("script", "img", "source", "iframe") and a.get("src", "").startswith(("http:", "https:", "//")):
            errors.append(f"external asset via <{tag}>: {a['src']}")

    handle_startendtag = handle_starttag


def check_local(base: Path, ref: str, where: str) -> None:
    path = ref.split("#")[0].split("?")[0]
    if not path:
        return
    target = (base / path).resolve()
    if not target.exists():
        errors.append(f"{where}: missing file {ref}")
    if "sprite.svg#" in ref and ref.split("#", 1)[1] not in SYMBOLS:
        errors.append(f"{where}: sprite symbol not found: {ref}")


checked = 0
for page in PAGES:
    html = (ROOT / page).read_text(encoding="utf-8")
    c = Collector()
    c.feed(html)
    for tag, attr, value in c.refs:
        checked += 1
        if value.startswith(("http:", "https:", "mailto:", "tel:")):
            continue
        if value.startswith("#"):
            if value != "#" and value[1:] not in c.ids:
                errors.append(f"{page}: anchor {value} has no target")
            continue
        check_local(ROOT, value, page)
    for m in re.finditer(r"[\w.+-]+@[\w-]+\.[\w.]+", html):
        if m.group(0) not in ALLOWED_EMAIL:
            errors.append(f"{page}: unexpected e-mail address {m.group(0)}")
    for pat in SECRET_PATTERNS:
        if re.search(pat, html):
            errors.append(f"{page}: secret-like string matching {pat}")

for css in CSS:
    text = css.read_text(encoding="utf-8")
    for url in re.findall(r"url\(\s*['\"]?([^'\")]+)['\"]?\s*\)", text):
        checked += 1
        if url.startswith(("http:", "https:", "//")):
            errors.append(f"{css.name}: external url() {url}")
        elif not url.startswith("data:"):
            check_local(css.parent, url, css.name)
    if "@import" in text:
        errors.append(f"{css.name}: @import found (avoid chained requests)")

if errors:
    print("\n".join(f"FAIL {e}" for e in errors))
    sys.exit(1)
print(f"assets ok: {checked} references in {len(PAGES)} pages and {len(CSS)} stylesheets, {len(SYMBOLS)} sprite symbols, no external assets")
