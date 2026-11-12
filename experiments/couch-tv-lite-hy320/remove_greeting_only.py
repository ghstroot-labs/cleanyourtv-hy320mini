#!/usr/bin/env python3
"""Only remove the greeting from the verified Slim Night BR recipe, leaving all else untouched."""
from pathlib import Path
import re

ROOT = Path("upstream/tv-home/web")
html = ROOT / "index.html"
app = ROOT / "app.js"
css = ROOT / "app.css"

def remove_once(path, old):
    content = path.read_text(encoding="utf-8")
    if content.count(old) != 1:
        raise SystemExit(f"Unexpected baseline: {path} has {content.count(old)} matches for greeting")
    path.write_text(content.replace(old, "", 1), encoding="utf-8")

remove_once(html, '<div id="hy-greeting" class="hy-greeting" aria-label="Saudação"></div>\n')
remove_once(app, '    hyGreeting(d);\n')

text = app.read_text(encoding="utf-8")
text, count = re.subn(
    r'  function hyGreeting\(d\) \{\n.*?\n  \}\n(?=  function clock\(\) \{)',
    "", text, count=1, flags=re.S,
)
if count != 1:
    raise SystemExit("Greeting function did not match the verified baseline")
app.write_text(text, encoding="utf-8")

text = css.read_text(encoding="utf-8")
text, count = re.subn(
    r'/\* HY320 Slim Night: static greeting.*?\n(?=/\* Two useful text cards)',
    "", text, count=1, flags=re.S,
)
if count != 1:
    raise SystemExit("Greeting CSS did not match the verified baseline")
css.write_text(text, encoding="utf-8")

# Verify ONLY the greeting was removed: original cards, clock and language are intact.
js = app.read_text(encoding="utf-8")
markup = html.read_text(encoding="utf-8")
style = css.read_text(encoding="utf-8")
assert "hyGreeting" not in js and "REBECA E NATAN" not in js
assert 'id="hy-greeting"' not in markup
assert ".hy-greeting" not in style
assert "hyWifiRefresh" in js and 'id="q-' in js
assert "function glassClock(hm)" in js and "function drawClocks(el, s, hm)" in js
assert "html.theme-night #q-wifi, html.theme-night #q-input" in style
print("GREETING_ONLY_REMOVAL_OK previous_clock=1 previous_cards=1 previous_dock=1 greeting=0")
