#!/usr/bin/env python3
"""Headless browser checks (needs Playwright + Chromium): no horizontal overflow at
320/390/768/1440 px, all fonts are the self-hosted Fira Sans, no requests leave the
local server, the FAQ accordion and the mobile menu open."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))
from playwright.sync_api import sync_playwright  # noqa: E402
from render import serve  # noqa: E402

fails = []
httpd, base = serve()
with sync_playwright() as p:
    b = p.chromium.launch()
    for page_name in ("index.html", "styletile.html", "waechter-flow.html"):
        for w in (320, 390, 768, 1440):
            ctx = b.new_context(viewport={"width": w, "height": 800})
            pg = ctx.new_page()
            external = []
            pg.on("request", lambda r: external.append(r.url) if not r.url.startswith(base) else None)
            pg.goto(base + page_name, wait_until="networkidle")
            pg.evaluate("document.fonts.ready")
            over = pg.evaluate("document.documentElement.scrollWidth - document.documentElement.clientWidth")
            if over > 0:
                fails.append(f"{page_name}@{w}: horizontal overflow {over}px")
            if external:
                fails.append(f"{page_name}@{w}: external requests {external}")
            fonts = pg.evaluate("[...document.fonts].filter(f => f.status === 'loaded').map(f => f.family)")
            if not fonts or any("Fira Sans" not in f for f in fonts):
                fails.append(f"{page_name}@{w}: unexpected fonts {fonts}")
            if page_name == "index.html" and w == 390:
                pg.click("button.navbar-toggler")
                pg.wait_for_selector("#ek-nav.show", timeout=3000)
                pg.click("button.navbar-toggler")
            if page_name == "index.html" and w == 1440:
                pg.click("button[data-bs-target='#faq-3']")
                pg.wait_for_selector("#faq-3.show", timeout=3000)
                pg.keyboard.press("Tab")
            ctx.close()
    b.close()
httpd.shutdown()
if fails:
    print("\n".join("FAIL " + f for f in fails))
    sys.exit(1)
print("browser ok: 3 pages x 4 widths, no overflow, only self-hosted Fira Sans, no external requests, menu and FAQ open")
