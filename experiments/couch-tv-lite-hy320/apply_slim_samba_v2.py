#!/usr/bin/env python3
"""Slim Samba BR v2: visual pass after pinned upstream + Slim Night BR translation/status."""
from pathlib import Path
import re

ROOT = Path("upstream")
APP = ROOT / "tv-home/web/app.js"
CSS = ROOT / "tv-home/web/app.css"
HTML = ROOT / "tv-home/web/index.html"

def replace_one(path, old, new):
    text = path.read_text(encoding="utf-8")
    amount = text.count(old)
    if amount != 1:
        raise SystemExit(f"Expected one anchor in {path}, found {amount}: {old[:100]!r}")
    path.write_text(text.replace(old, new, 1), encoding="utf-8")

def regex_one(path, pattern, replace):
    text = path.read_text(encoding="utf-8")
    text, count = re.subn(pattern, replace, text, count=1, flags=re.S)
    if count != 1:
        raise SystemExit(f"Expected one regex anchor in {path}: {pattern[:90]}")
    path.write_text(text, encoding="utf-8")

# Remove the old greeting *and the update code*, not just its visible style.
replace_one(HTML, '<div id="hy-greeting" class="hy-greeting" aria-label="Saudação"></div>\n', "")
regex_one(APP,
    r'  function hyGreeting\(d\) \{\n.*?\n  \}\n(?=  function clock\(\) \{)',
    "")
replace_one(APP, '    hyGreeting(d);\n', "")
# The old CSS greeting rules can remain inert, but remove them for a smaller style sheet.
regex_one(CSS, r'/\* HY320 Slim Night: static greeting.*?\n(?=/\* Two useful text cards)', "")

# Add persisted clock placement. This is independent of scene/fog/night/own-photo choice.
positions = '''  var SAMBA_CLOCK_POSITIONS = ["center", "upper", "lower", "left", "right"];
  var SAMBA_CLOCK_LABELS = {
    center: "Centralizado", upper: "Superior", lower: "Inferior",
    left: "Esquerda", right: "Direita"
  };
  function sambaClockPosition() {
    var p = ST.samba_clock_position || HOME.samba_clock_position || "center";
    return SAMBA_CLOCK_POSITIONS.indexOf(p) >= 0 ? p : "center";
  }
  function sambaSetClockPosition() {
    document.documentElement.setAttribute("data-samba-clock", sambaClockPosition());
    glassShown = "";
  }
'''
replace_one(APP, '  function readConfig() {\n', positions + '  function readConfig() {\n')
replace_one(APP, '    ST = loadSettings();\n    var savedIdle',
    '    ST = loadSettings();\n    sambaSetClockPosition();\n    var savedIdle')

# Native Home settings list remains intact; add 5-way cycle immediately after the clock controls.
pos_setting = '''    rows.push({ kind: "cycle", key: "samba-clock-position", label: "Posição do relógio",
      value: SAMBA_CLOCK_LABELS[sambaClockPosition()],
      act: function () {
        var pos = sambaClockPosition(), idx = SAMBA_CLOCK_POSITIONS.indexOf(pos);
        ST.samba_clock_position = SAMBA_CLOCK_POSITIONS[(idx + 1) % SAMBA_CLOCK_POSITIONS.length];
        sambaSetClockPosition(); saveSettings(); clock();
      }
    });
'''
replace_one(APP, '    rows.push({ kind: "cycle", key: "idle-photo-seconds"', pos_setting + '    rows.push({ kind: "cycle", key: "idle-photo-seconds"')

# Remove "People" from the settings and keyboard navigation, without deleting saved household data.
replace_one(APP, '["apps", "apps"], ["people", "person"], ["quick", "bolt"], ["about", "info"]',
    '["apps", "apps"], ["quick", "bolt"], ["about", "info"]')
replace_one(APP, '  function peopleOn() { return peopleCount() >= 2; }',
    '  function peopleOn() { return false; } // Slim Samba: no multi-profile switcher')
# Our visible home name is independent of the upstream project.
replace_one(HTML, '<title>Home</title>', '<title>Slim Samba BR</title>')

# Consistent true center alignment for any wallpaper. Avoid transform(-50%) on the
# glass clock because upstream uses element offsets to align the photo inside digits.
# Layout units are upstream's 120rem wide TV screen; 25rem clock has ~20.5rem line height.
style = """
/* =====================================================================
   SLIM SAMBA BR v2 — Frosted Acrylic Lite (static, zero backdrop blur)
   ===================================================================== */
html.theme-night .people-wrap, html.theme-night #people, html.theme-night #people-pop {
  display: none !important;
}
html.theme-night .scene .gclock {
  left: 0 !important; right: 0 !important;
  top: calc(42% - 10.25rem) !important;
  text-align: center !important;
  font-size: 25rem !important;
  transform: none !important;
  filter: none !important;
  white-space: nowrap;
}
html.theme-night[data-samba-clock="upper"] .scene .gclock {
  top: calc(27% - 10.25rem) !important;
}
html.theme-night[data-samba-clock="lower"] .scene .gclock {
  top: calc(52% - 10.25rem) !important;
}
html.theme-night[data-samba-clock="left"] .scene .gclock {
  top: calc(42% - 10.25rem) !important;
  left: 4rem !important; right: auto !important; text-align: left !important;
  font-size: 22rem !important;
}
html.theme-night[data-samba-clock="right"] .scene .gclock {
  top: calc(42% - 10.25rem) !important;
  left: auto !important; right: 4rem !important; text-align: right !important;
  font-size: 22rem !important;
}
/* Date and weather keep their own stable position; they no longer follow scene-specific clocks. */
html.theme-night .date, html.theme-night.scene-fog .date,
html.theme-night.scene-night .date, html.theme-night.scene-water .date,
html.theme-night.scene-golden .date, html.theme-night.scene-dawn .date {
  left: 0 !important; right: 0 !important;
  top: 5.25rem !important; text-align: center !important;
  color: #eff4fa !important;
  text-shadow: 0 0.125rem 0.5rem rgba(0,0,0,.68) !important;
}
html.theme-night .date .wx { color: rgba(239,244,250,.88) !important; }

/* Unified macOS-inspired dock: fine bright acrylic edge, matte semi-opaque
   graphite and one static specular gradient — no expensive blur shader. */
html.theme-night .grid {
  background: linear-gradient(165deg, rgba(164,183,198,.56) 0%, rgba(68,83,99,.81) 8%,
    rgba(26,35,47,.88) 50%, rgba(31,42,53,.93) 100%) !important;
  -webkit-backdrop-filter: none !important; backdrop-filter: none !important;
  border: .08rem solid rgba(226,238,250,.46) !important;
  box-shadow: inset 0 .12rem 0 rgba(255,255,255,.31),
    inset 0 -.07rem 0 rgba(255,255,255,.08),
    0 .75rem 2rem rgba(3,8,13,.36) !important;
  border-radius: 2.7rem !important;
  padding: 1.2rem 1.65rem !important;
  column-gap: 1.5rem !important; grid-column-gap: 1.5rem !important;
}
html.theme-night .app, html.theme-night .tile {
  transition: none !important;
}
html.theme-night .app .face {
  border: .065rem solid rgba(244,249,255,.18);
  box-shadow: none !important;
  transition: none !important;
}
html.theme-night .app.focus {
  transform: translateY(-.35rem) !important;
}
html.theme-night .app.focus .face {
  border-color: rgba(255,255,255,.9) !important;
  box-shadow: 0 0 0 .22rem rgba(255,255,255,.95) !important;
}
html.theme-night .app:not(.focus) .face img { filter: none !important; }

/* Wi-Fi + Input: large frosted-acrylic cards ABOVE the dock, central and easy
   to read from a sofa. Existing TV remote focus and action handlers are reused. */
html.theme-night .top .quick {
  position: fixed !important;
  top: auto !important; right: auto !important;
  left: 50% !important; bottom: 15.25rem !important;
  transform: translateX(-50%) !important;
  margin: 0 !important; z-index: 8 !important;
  align-items: stretch !important;
}
html.theme-night .quick .qbtns { gap: 1.5rem !important; }
html.theme-night #q-wifi, html.theme-night #q-input {
  width: 26rem !important; min-width: 26rem !important; max-width: 26rem !important;
  height: 6.75rem !important; min-height: 6.75rem !important;
  padding: .8rem 1.5rem !important; border-radius: 1.65rem !important;
  display: flex !important; align-items: center !important;
  justify-content: flex-start !important; gap: 1.05rem !important;
  color: #f7faff !important;
  background: linear-gradient(155deg, rgba(163,185,201,.68) 0%,
    rgba(55,73,89,.87) 12%, rgba(27,38,52,.91) 100%) !important;
  border: .08rem solid rgba(228,239,251,.5) !important;
  box-shadow: inset 0 .12rem 0 rgba(255,255,255,.24),
    0 .45rem 1.1rem rgba(4,10,19,.24) !important;
  -webkit-backdrop-filter: none !important; backdrop-filter: none !important;
  transition: none !important; transform: none !important;
}
html.theme-night #q-wifi > svg, html.theme-night #q-input > svg {
  width: 3rem !important; height: 3rem !important; flex: none !important;
}
html.theme-night #q-wifi span, html.theme-night #q-input span {
  display: block !important; flex: 1 !important; min-width: 0 !important;
  font-size: 1.8rem !important; line-height: 1.25 !important;
  font-weight: 700 !important; color: #f7faff !important;
}
html.theme-night #q-wifi small, html.theme-night #q-input small {
  display: block !important; max-width: 19rem !important;
  margin-top: .22rem !important; font-size: 1.22rem !important;
  font-weight: 500 !important; line-height: 1.25 !important;
  opacity: .92 !important; color: #e2eaf3 !important;
}
html.theme-night #q-wifi.focus, html.theme-night #q-input.focus {
  border-color: #fff !important;
  box-shadow: inset 0 0 0 .18rem rgba(255,255,255,.95),
    0 .4rem 1.1rem rgba(0,0,0,.3) !important;
}
/* When the user opens full-screen settings or the expanded app grid, avoid
   laying the status cards over the controls. */
html.theme-night.setting .quick,
html.theme-night.expanded .quick,
html.theme-night.gearing .quick { display: none !important; }
"""
with CSS.open("a", encoding="utf-8") as f:
    f.write("\n" + style + "\n")

# Assert no visible old greeting and no People section in navigation.
final_app = APP.read_text(encoding="utf-8")
final_html = HTML.read_text(encoding="utf-8")
final_css = CSS.read_text(encoding="utf-8")
assert "hyGreeting(" not in final_app
assert "id=\"hy-greeting\"" not in final_html
assert '["people", "person"]' not in final_app
assert 'samba-clock-position' in final_app and 'data-samba-clock' in final_app
assert "backdrop-filter: none !important" in final_css
print("SLIM_SAMBA_V2_PATCH_OK greeting_removed=1 people_section_removed=1 clock_positions=5 frosted_acrylic=1 cards=2")
