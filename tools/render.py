#!/usr/bin/env python3
"""Render PNG previews of the static pages with headless Chromium (Playwright).

Serves the repo on a local port so <use href> sprites and fonts load like on Pages.
Usage: python tools/render.py [--base URL]   (default: local server)
"""
import argparse
import functools
import http.server
import threading
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "renders"

SHOTS = [
    # name, page, viewport width, height, full page, device scale
    ("homepage-desktop-1440", "index.html", 1440, 900, True, 1),
    ("homepage-mobile-390", "index.html", 390, 844, True, 2),
    ("styletile", "styletile.html", 1440, 900, True, 1),
    ("waechter-flow", "waechter-flow.html", 1440, 900, True, 1),
]


def serve() -> tuple[http.server.ThreadingHTTPServer, str]:
    class Quiet(http.server.SimpleHTTPRequestHandler):
        def log_message(self, *args):  # keep render output readable
            pass

    handler = functools.partial(Quiet, directory=str(ROOT))
    httpd = http.server.ThreadingHTTPServer(("127.0.0.1", 0), handler)
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    return httpd, f"http://127.0.0.1:{httpd.server_address[1]}/"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--base")
    args = ap.parse_args()
    httpd, base = (None, args.base) if args.base else serve()
    OUT.mkdir(exist_ok=True)
    with sync_playwright() as p:
        browser = p.chromium.launch()
        for name, page_path, w, h, full, scale in SHOTS:
            ctx = browser.new_context(viewport={"width": w, "height": h}, device_scale_factor=scale,
                                      reduced_motion="reduce", locale="de-DE")
            page = ctx.new_page()
            page.goto(base + page_path, wait_until="networkidle")
            page.evaluate("document.fonts.ready")
            # static preview: header should not repeat in a full-page capture
            page.add_style_tag(content=".sticky-top{position:static!important}")
            page.wait_for_timeout(300)
            out = OUT / f"{name}.png"
            page.screenshot(path=str(out), full_page=full)
            print(f"{out.relative_to(ROOT)}  {out.stat().st_size // 1024} KB")
            if name == "homepage-mobile-390":
                # hero + promise strip + Branchen, as a separate shorter preview
                bottom = page.evaluate("document.querySelector('#branchen').getBoundingClientRect().bottom + window.scrollY")
                top_out = OUT / "homepage-mobile-390-top.png"
                page.screenshot(path=str(top_out), clip={"x": 0, "y": 0, "width": w, "height": bottom}, full_page=True)
                print(f"{top_out.relative_to(ROOT)}  {top_out.stat().st_size // 1024} KB")
            ctx.close()
        browser.close()
    if httpd:
        httpd.shutdown()


if __name__ == "__main__":
    main()
