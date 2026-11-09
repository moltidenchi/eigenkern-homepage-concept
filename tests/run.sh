#!/usr/bin/env bash
# Run all checks. Requires Node (for the pinned html-validate in package.json) and Python 3.
set -euo pipefail
cd "$(dirname "$0")/.."

echo "== Build steps are reproducible (sprite + Wächter diagram) =="
python3 tools/build_sprite.py
python3 tools/build_flow.py
git diff --quiet -- assets/icons/sprite.svg assets/img index.html waechter-flow.html 2>/dev/null \
  || echo "note: generated files changed; commit them"

echo "== HTML validation (html-validate 11.21.0, pinned) =="
[ -d node_modules/html-validate ] || npm ci --no-audit --no-fund
npx --no-install html-validate index.html styletile.html waechter-flow.html
echo "html-validate: 0 errors"

echo "== Assets, links, anchors, privacy =="
python3 tests/check_assets.py

echo "== WCAG AA contrast =="
python3 tests/contrast.py

echo "== Headless browser checks (optional, needs Playwright) =="
if python3 -c "import playwright" 2>/dev/null; then
  python3 tests/browser_check.py
else
  echo "skipped: Playwright not installed (pip install playwright==1.48.0 && python -m playwright install chromium)"
fi
