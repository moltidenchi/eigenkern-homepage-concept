# EIGENKERN homepage concept

A homepage redesign for [EIGENKERN](https://www.eigenkern.de) (local AI for German small businesses), built as a **working Bootstrap 5.3 static prototype** rather than a flat mockup, so every section can be rebuilt one to one in the Odoo website builder.

- Live prototype: https://moltidenchi.github.io/eigenkern-homepage-concept/
- Style tile: https://moltidenchi.github.io/eigenkern-homepage-concept/styletile.html
- Wächter flow: https://moltidenchi.github.io/eigenkern-homepage-concept/waechter-flow.html
- PNG previews: [`renders/`](renders/)

Freelancer.com contest entry for "Homepage Design Contest for German Local-AI Company (Odoo)". Built with AI assistance.

## Concept: the floor plan

The whole message is *im eigenen Haus*. So the page borrows the visual language of a German technical drawing: a floor plan of the customer's office in the hero, with the walls drawn in ink, data paths inside the house in signal green, and a single dashed line leaving through the Wächter in the outer wall. The same three line styles carry through the "Drei Wege" drawings and the Wächter diagram, so a visitor learns the code once: **solid wall = your house, green = data that stays, dashed = only the shadow goes out.**

Everything else stays quiet: one typeface, cool paper and ink, one signal colour, ruled lists instead of floating cards.

### Tokens

| Name | Hex | Role |
| --- | --- | --- |
| Tinte (ink) | `#16222E` | text, walls, dark sections |
| Stahl (steel) | `#4F5D6B` | secondary text, borders |
| Papier (paper) | `#EEF1F3` | cool section background (not cream) |
| Signalgrün | `#1D6F47` | the one action colour; "stays in the house" |
| Signal auf Tinte | `#7FD1A3` | links, focus and buttons on dark sections |
| Außen (cloud) | `#3D5A78` | everything outside the house, always dashed |

Type: **Fira Sans** (SIL OFL), self-hosted WOFF2, weights 400/500/600. A humanist sans with a DIN-like, engineered feel that stays readable in long German compounds (*Auftragsverarbeitung*, *Rechtsprechungssammlung*). Sentence case throughout, no condensed uppercase.

### What was avoided on purpose

Cream/beige and orange, purple-blue gradients, glowing brains, robots and circuit imagery, emoji icons, pill badges, a chat bubble in the hero, uppercase eyebrow labels on every section, identical shadowed cards. Numbering is used only where the content really is a sequence (the four Wächter steps).

## Brief checklist

| Requirement | Where |
| --- | --- |
| Desktop homepage 1440 px: hero, solutions/industries, three ways, Wächter, costs, FAQ, footer | `index.html`, `renders/homepage-desktop-1440.png` |
| Mobile, at least hero and first two sections | `renders/homepage-mobile-390-top.png` (hero, promise strip, Branchen) and `renders/homepage-mobile-390.png` (full page) |
| Style tile: fonts, palette, buttons, cards, icon style | `styletile.html`, `renders/styletile.png` |
| Wächter flow: original, shadow copy, cloud AI, answer back with real names | `waechter-flow.html`, `assets/img/waechter-flow.svg` (wide) and `waechter-flow-mobile.svg` (stacked), `renders/waechter-flow.png` |
| Odoo theme recommendation | below |
| Self-hostable fonts, no Google Fonts CDN | `assets/fonts/`, checked by `tests/check_assets.py` and `tests/browser_check.py` |
| WCAG AA contrast | `tests/contrast.py` (22 of 22 pairs pass) |

## Odoo approach

**Recommendation:** build it as a custom theme module (extending the existing `theme_eigenkern` module) on top of Odoo's default `website` theme, not on a marketplace theme. The default theme is plain Bootstrap 5.3 with Odoo's SCSS variables, so the palette and Fira Sans go into the theme's `primary_variables.scss` and static folder (no Google Fonts request), and every block of this prototype becomes a custom snippet, while the FAQ and the call to action reuse Odoo's own `s_faq_collapse` and `s_call_to_action`, so the team can keep editing texts in the website builder without touching code.

### Section to snippet mapping

Each top-level `<section>` in `index.html` carries a `data-snippet` attribute, the same convention Odoo uses.

| Section | `data-snippet` | Built from | Notes |
| --- | --- | --- | --- |
| Header | – | custom header template | Bootstrap navbar, sticky; one primary button |
| Hero with floor plan | `s_ek_hero` | `s_text_image` | floor plan is an inline SVG; can also be uploaded as an SVG image |
| Promise strip | `s_ek_facts` | `s_features` | four columns, ruled, icon + text |
| Branchen | `s_ek_branchen` | `s_features_grid` | 9 links in a 3-column ruled grid |
| Drei Wege | `s_ek_wege` | `s_three_columns` | three bordered columns, Hybrid outlined in ink |
| Wächter | `s_ek_waechter` | `s_text_block` + image | wide SVG on desktop, stacked SVG below 768 px, plus a real `<ol>` of the four steps |
| Kosten | `s_ek_kosten` | `s_text_image` | dark section, definition rows |
| FAQ | `s_faq_collapse` | Odoo standard | Bootstrap accordion, restyled through CSS variables only |
| Call to action | `s_call_to_action` | Odoo standard | |
| Footer | – | custom footer template | |

Bootstrap is pinned to **5.3.3**, the version shipped in Odoo 18 and 19, and is overridden only through Bootstrap's CSS custom properties (`--bs-btn-*`, `--bs-accordion-*`, `--bs-navbar-*`), so the same rules carry over to Odoo's SCSS build. No JavaScript beyond Bootstrap's own bundle (navbar collapse and accordion).

## Files

```
index.html               homepage (desktop + responsive)
styletile.html           style tile
waechter-flow.html       Wächter flow on its own page
assets/css/tokens.css    colour tokens (single source for tests and pages)
assets/css/fonts.css     @font-face, self-hosted
assets/css/eigenkern.css theme layer on top of Bootstrap
assets/img/              Wächter diagrams (generated), favicon
assets/icons/            Bootstrap Icons subset + generated sprite
assets/vendor/           Bootstrap 5.3.3 dist files
tools/build_sprite.py    builds the icon sprite
tools/build_flow.py      generates the Wächter SVGs and inlines them into the pages
tools/render.py          PNG renders with headless Chromium
tests/                   validation, asset/link/privacy check, contrast, browser checks
renders/                 PNG previews and overview JPG
```

## Run and test

```bash
python3 -m http.server 8000        # then open http://localhost:8000/
npm ci                             # installs the pinned html-validate
bash tests/run.sh                  # build check, HTML validation, assets, contrast, browser checks
python3 tools/render.py            # re-render PNGs (needs playwright==1.48.0 + Chromium)
```

`tests/run.sh` runs:

1. `tools/build_sprite.py` and `tools/build_flow.py` (generated files are reproducible)
2. `html-validate` 11.21.0 on all three pages (`html-validate:recommended`)
3. `tests/check_assets.py`: every local reference resolves, sprite symbols exist, in-page anchors exist, no external stylesheets/scripts/fonts, no e-mail addresses other than the placeholder, no secret-like strings
4. `tests/contrast.py`: WCAG 2.x contrast for every colour pair the design uses
5. `tests/browser_check.py` (if Playwright is installed): no horizontal overflow at 320/390/768/1440 px, only the self-hosted Fira Sans is loaded, no request leaves the site, mobile menu and FAQ open

## Content and privacy

German copy is taken from the current eigenkern.de pages (marketing text only; long sections shortened). Names, e-mail addresses, phone numbers and postal addresses of people are deliberately left out; contact details are placeholders (`info@beispiel.de`). The example in the Wächter diagram is invented, like the one on the current site.

## Licence

Code: MIT (see `LICENSE`). Third-party assets: see `CREDITS.md`. If this entry wins the contest, the rights to the design transfer to the contest holder under the contest terms.
