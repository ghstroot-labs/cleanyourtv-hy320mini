#!/usr/bin/env python3
"""VYFLUX v3: minimal, reviewable visual layer over proven Slim Night BR.
No upstream repo changes. Applied exclusively to a detached checkout in GitHub Actions.
"""
from pathlib import Path
import re

ROOT = Path("upstream")
APP = ROOT / "tv-home/web/app.js"
CSS = ROOT / "tv-home/web/app.css"
HTML = ROOT / "tv-home/web/index.html"
RES = ROOT / "tv-home/android/app/src/main/res/drawable"

def replace(path, old, new):
    original = path.read_text(encoding="utf-8")
    count = original.count(old)
    if count != 1:
        raise SystemExit(f"VYFLUX safety check: {path} has {count} matches, wanted 1: {old[:100]!r}")
    path.write_text(original.replace(old, new, 1), encoding="utf-8")

def regex_replace(path, expr, new):
    original = path.read_text(encoding="utf-8")
    out, count = re.subn(expr, lambda _: new, original, count=1, flags=re.S)
    if count != 1:
        raise SystemExit(f"VYFLUX safety check: {path} regex missing: {expr[:90]}")
    path.write_text(out, encoding="utf-8")

# Remove greeting code and markup rather than just covering it.
replace(HTML, '<div id="hy-greeting" class="hy-greeting" aria-label="Saudação"></div>\n', "")
regex_replace(APP, r'  function hyGreeting\(d\) \{\n.*?\n  \}\n(?=  function clock\(\) \{)', "")
replace(APP, '    hyGreeting(d);\n', "")
regex_replace(CSS, r'/\* HY320 Slim Night: static greeting.*?\n(?=/\* Two useful text cards)', "")

# Hide People and its setting WITHOUT destroying their stored entries or settings.
replace(APP, '["apps", "apps"], ["people", "person"], ["quick", "bolt"], ["about", "info"]',
        '["apps", "apps"], ["quick", "bolt"], ["about", "info"]')
replace(APP, '  function peopleOn() { return peopleCount() >= 2; }',
        '  function peopleOn() { return false; } // VYFLUX household: no profile switch')
# Don't list competing experimental home apps among normal media apps on the dock.
replace(APP, '"com.google.android.apps.tv.launcherx", "com.google.android.tvlauncher", "app.couchtv.launcher",',
        '"com.google.android.apps.tv.launcherx", "com.google.android.tvlauncher", "app.couchtv.launcher",\n    "studio.ghstroot.couchtvlite.hy320", "studio.ghstroot.couchtvslimbr.hy320",\n    "studio.ghstroot.slimsamba.br", "studio.ghstroot.vyflux.hy320",')

# Original Couch TV's scene clock, glass photography, rim, typography and date/weather logic
# are NOT replaced. Only its container positioning and scene layering are changed.
clock_code = '''  var VY_CLOCK_CHOICES = ["center", "upper", "lower", "left", "right"];
  var VY_CLOCK_NAMES = {
    center: "Centralizado", upper: "Mais acima", lower: "Mais abaixo",
    left: "Esquerda", right: "Direita"
  };
  function vyClockChoice() {
    var choice = ST.vy_clock_position || HOME.vy_clock_position || "center";
    return VY_CLOCK_CHOICES.indexOf(choice) >= 0 ? choice : "center";
  }
  function vyApplyClockPosition() {
    document.documentElement.setAttribute("data-vy-clock", vyClockChoice());
    glassShown = ""; // realign the ORIGINAL frosted photo inside every digit
  }
'''
replace(APP, '  function readConfig() {\n', clock_code + '  function readConfig() {\n')
replace(APP, '    ST = loadSettings();\n    var savedIdle',
        '    ST = loadSettings();\n    vyApplyClockPosition();\n    var savedIdle')
pos_row = '''    rows.push({ kind: "cycle", key: "vy-clock-position", label: "Posição do relógio",
      value: VY_CLOCK_NAMES[vyClockChoice()],
      act: function () {
        var next = (VY_CLOCK_CHOICES.indexOf(vyClockChoice()) + 1) % VY_CLOCK_CHOICES.length;
        ST.vy_clock_position = VY_CLOCK_CHOICES[next];
        vyApplyClockPosition();
        saveSettings(); clock();
      }
    });
'''
replace(APP, '    rows.push({ kind: "cycle", key: "idle-photo-seconds"',
        pos_row + '    rows.push({ kind: "cycle", key: "idle-photo-seconds"')

# Compact utility pills using the existing native Wi-Fi bridge and TV input selection.
# Third pill opens the app settings; it uses the same focus/navigation as native quick buttons.
replace(APP, '"input", "bluetooth", "network", "screensaver", "wifi"];',
             '"input", "bluetooth", "network", "screensaver", "wifi", "vy-settings"];')
replace(APP, '      if (q === "wifi") return !!(TV && TV.wifiStatus);',
             '      if (q === "wifi") return !!(TV && TV.wifiStatus);\n      if (q === "vy-settings") return true;')
replace(APP, 'el.innerHTML = ICONS.network + "<span>Wi-Fi<small>" + esc(label) + "</small></span>";',
             'el.innerHTML = ICONS.network + "<span>" + esc(wifi.ssid || "Wi-Fi") + "</span>";')
replace(APP, 'el.innerHTML = ICONS.input + "<span>Entradas<small>" + esc(summary) + "</small></span>";',
             'el.innerHTML = ICONS.input + "<span>Entradas</span>";')
replace(APP, '      } else if (q === "screensaver") {\n',
             '      } else if (q === "vy-settings") {\n        el.innerHTML = ICONS.gear + "<span>Configurações</span>";\n      } else if (q === "screensaver") {\n')
replace(APP, '    else if (q === "input") openInputs();',
             '    else if (q === "input") openInputs();\n    else if (q === "vy-settings") openSettings();')

# VYFLUX brand in the application UI. Not clickable; keyboard focus stays on functional controls.
replace(HTML, '<title>Home</title>', '<title>VYFLUX</title>')
brand = '''  <div class="vy-brand" aria-hidden="true">
    <svg class="vy-symbol" viewBox="0 0 48 48">
      <path fill="#D8E7F1" d="M6 13 Q10 9 14 13 L22 30 Q24 34 27 29 L34 14 Q37 9 42 13 L31 36 Q25 46 18 36Z"/>
      <path fill="#1ACBED" d="M23 30 Q25 33 27 29 L34 14 Q38 9 42 13 Q44 16 42 19 L31 37 Q25 43 20 37Z"/>
      <path fill="#EEF8FF" d="M22 15 Q22 14 23 15 L30 20 Q31 21 30 22 L23 26 Q22 27 22 25Z"/>
    </svg><span>VY<span class="vy-flux">FLUX</span></span>
  </div>
'''
replace(HTML, '<header class="top">\n', '<header class="top">\n' + brand)

# Native Android launcher icon and TV banner — not upstream HTE imagery.
# Vector graphics render at all icon sizes, require no runtime blur, and are
# inspired by the approved silver/cyan V ribbon and play motif.
(RES / "icon.xml").write_text('''<?xml version="1.0" encoding="utf-8"?>
<vector xmlns:android="http://schemas.android.com/apk/res/android"
    android:width="48dp" android:height="48dp"
    android:viewportWidth="48" android:viewportHeight="48">
    <path android:fillColor="#0C1726"
        android:pathData="M11,1 L37,1 Q47,1 47,11 L47,37 Q47,47 37,47 L11,47 Q1,47 1,37 L1,11 Q1,1 11,1Z"/>
    <path android:strokeColor="#536C87" android:strokeWidth="0.7" android:fillColor="@android:color/transparent"
        android:pathData="M11,2 L37,2 Q46,2 46,11 L46,37 Q46,46 37,46 L11,46 Q2,46 2,37 L2,11 Q2,2 11,2Z"/>
    <path android:fillColor="#CADCE9"
        android:pathData="M6,14 Q10,10 14,13 L22,30 Q24,34 27,29 L34,14 Q38,10 42,13 L31,36 Q25,44 19,36Z"/>
    <path android:fillColor="#24D5ED"
        android:pathData="M22,30 Q24,34 27,29 L34,14 Q38,10 42,13 Q44,16 42,19 L31,37 Q25,43 20,37Z"/>
    <path android:fillColor="#F1FAFF"
        android:pathData="M22,15 Q22,14 23,15 L30,20 Q31,21 30,22 L23,26 Q22,27 22,25Z"/>
    <path android:strokeColor="#39D6F0" android:strokeWidth="1.1" android:strokeLineCap="round"
        android:fillColor="@android:color/transparent"
        android:pathData="M11,11 Q24,4 39,11"/>
    <path android:strokeColor="#92B6C7" android:strokeWidth="0.8" android:strokeLineCap="round"
        android:fillColor="@android:color/transparent"
        android:pathData="M10,39 Q24,47 39,38"/>
</vector>
''', encoding="utf-8")
(RES / "banner.xml").write_text('''<?xml version="1.0" encoding="utf-8"?>
<vector xmlns:android="http://schemas.android.com/apk/res/android"
    android:width="320dp" android:height="180dp"
    android:viewportWidth="320" android:viewportHeight="180">
    <path android:fillColor="#0C1726" android:pathData="M0,0h320v180h-320z"/>
    <path android:fillColor="#132B41" android:pathData="M0,115 Q140,65 320,110 L320,180 L0,180Z"/>
    <path android:strokeColor="#22C8ED" android:strokeWidth="2" android:fillColor="@android:color/transparent"
        android:pathData="M40,56 Q160,-12 280,58"/>
    <path android:fillColor="#D8E7F1"
        android:pathData="M90,55 Q108,40 123,55 L151,113 Q159,130 169,112 L199,57 Q216,39 230,55 L181,143 Q156,173 131,143Z"/>
    <path android:fillColor="#21D2EF"
        android:pathData="M150,113 Q159,130 169,112 L199,57 Q216,39 230,55 Q242,68 229,83 L181,143 Q156,173 132,144Z"/>
    <path android:fillColor="#F4FAFF"
        android:pathData="M151,53 L151,103 L187,79Z"/>
</vector>
''', encoding="utf-8")

# Render-only matte acrylic for slow Android WebView 101: zero backdrop-filter or
# continuous motion. Keep original Antonio photographic glass clock implementation.
style = """
/* === VYFLUX v3 / projectors and TVs / Matte Acrylic Lite === */
html.theme-night .people-wrap,
html.theme-night #people,
html.theme-night #people-pop,
html.theme-night #hy-greeting { display:none !important; }

html.theme-night .vy-brand {
  position:fixed; z-index:12; top:2.45rem; left:3.85rem;
  display:flex; align-items:center; gap:.65rem;
  color:rgba(244,250,255,.96); font-size:2.3rem;
  line-height:1; letter-spacing:-.055em; font-weight:830;
  text-shadow:0 .11rem .25rem rgba(0,0,0,.55);
  pointer-events:none;
}
html.theme-night .vy-brand .vy-flux { color:#47D5ED; }
html.theme-night .vy-brand .vy-symbol {
  width:4.25rem; height:4.25rem; flex:none;
}
.vy-brand { display:none; }

/* EXACT Couch TV original scene digits: their photograph-based frosted fill,
   Antonio thin condensed font, glass rim and sheen are deliberately untouched.
   Force their layer above foreground hills so they are never partially hidden. */
html.theme-night .scene .sbg { z-index:0; }
html.theme-night .scene .shade { z-index:1; }
html.theme-night .scene .fg { z-index:2; }
html.theme-night .scene .gclock:not(.under) {
  z-index:4 !important;
  position:absolute !important;
  top:20vh !important; left:0 !important; right:0 !important;
  text-align:center !important;
  font-family:"Antonio","Arial Narrow",sans-serif !important;
  font-weight:300 !important; font-size:28rem !important;
  line-height:.82 !important; letter-spacing:-.02em !important;
  transform:none !important; filter:none !important;
}
html.theme-night[data-vy-clock="upper"] .scene .gclock:not(.under) {
  top:14.5vh !important;
}
html.theme-night[data-vy-clock="lower"] .scene .gclock:not(.under) {
  top:31.5vh !important;
}
html.theme-night[data-vy-clock="left"] .scene .gclock:not(.under) {
  top:21vh !important; left:5rem !important;
  right:0 !important; text-align:left !important;
  font-size:25rem !important;
}
html.theme-night[data-vy-clock="right"] .scene .gclock:not(.under) {
  top:21vh !important; left:0 !important;
  right:5rem !important; text-align:right !important;
  font-size:25rem !important;
}
/* No scene-specific date movement; keep it between pills and clock. */
html.theme-night .date,
html.theme-night.scene-fog .date,
html.theme-night.scene-night .date,
html.theme-night.scene-golden .date,
html.theme-night.scene-water .date,
html.theme-night.scene-dawn .date {
  position:fixed !important;
  top:11.75vh !important; left:0 !important; right:0 !important;
  text-align:center !important; color:#ECF2F7 !important;
  font-size:1.85rem !important; line-height:2.2rem !important;
  font-weight:500 !important;
  text-shadow:0 .1rem .35rem rgba(0,0,0,.62) !important;
}
html.theme-night .date .wx { color:rgba(230,243,255,.88) !important; }

/* Three discreet CleanYourTV-inspired pills in the upper control row.
   No big blocks over the scenery, no blur and no animations. */
html.theme-night .top .quick {
  position:fixed !important; z-index:13 !important;
  top:2.65rem !important; bottom:auto !important;
  left:57% !important; right:auto !important;
  transform:translateX(-50%) !important;
  margin:0 !important; padding:0 !important;
}
html.theme-night .top .qbtns {
  display:flex !important; justify-content:center !important;
  align-items:center !important; gap:1.1rem !important;
}
html.theme-night .qbtn#q-input,
html.theme-night .qbtn#q-wifi,
html.theme-night .qbtn#q-vy-settings {
  flex:none !important;
  min-width:0 !important; max-width:28rem !important;
  height:4.15rem !important; min-height:4.15rem !important;
  padding:.45rem 1.2rem !important;
  border-radius:2.3rem !important;
  display:flex !important; align-items:center !important;
  justify-content:center !important; gap:.65rem !important;
  background:linear-gradient(180deg,
    rgba(82,111,130,.52), rgba(13,29,45,.72)) !important;
  color:rgba(240,249,255,.96) !important;
  border:.07rem solid rgba(222,239,248,.27) !important;
  box-shadow:inset 0 .08rem 0 rgba(255,255,255,.13) !important;
  -webkit-backdrop-filter:none !important; backdrop-filter:none !important;
  transform:none !important; transition:none !important;
}
html.theme-night .qbtn#q-input svg,
html.theme-night .qbtn#q-wifi svg,
html.theme-night .qbtn#q-vy-settings svg {
  width:2.1rem !important; height:2.1rem !important;
  flex:none !important;
}
html.theme-night .qbtn#q-input span,
html.theme-night .qbtn#q-wifi span,
html.theme-night .qbtn#q-vy-settings span {
  display:inline !important; font-size:1.35rem !important;
  line-height:1.4 !important; font-weight:650 !important;
  white-space:nowrap !important; max-width:19rem !important;
  overflow:hidden !important; text-overflow:ellipsis !important;
}
html.theme-night .qbtn#q-input.focus,
html.theme-night .qbtn#q-wifi.focus,
html.theme-night .qbtn#q-vy-settings.focus {
  border-color:#BDECF8 !important;
  box-shadow:inset 0 0 0 .12rem #D4F9FF !important;
}

/* Compact dock: solid pseudo-frosted acrylic with restrained cyan accent.
   Keep the upstream grid sizing/focus-navigation and each real app icon. */
html.theme-night .apps { bottom:4.1rem !important; }
html.theme-night .grid {
  background:linear-gradient(170deg, rgba(60,84,99,.86),
    rgba(13,29,41,.88) 38%, rgba(10,25,37,.94)) !important;
  -webkit-backdrop-filter:none !important; backdrop-filter:none !important;
  border:.075rem solid rgba(177,221,236,.44) !important;
  border-radius:2.7rem !important;
  padding:1.1rem 1.45rem !important;
  column-gap:1.32rem !important; grid-column-gap:1.32rem !important;
  box-shadow:inset 0 .09rem 0 rgba(218,242,252,.23),
    0 .55rem 1.35rem rgba(0,0,0,.24) !important;
}
html.theme-night .app, html.theme-night .tile {
  transition:none !important;
}
html.theme-night .app .face { box-shadow:none !important; }
html.theme-night .app.focus { transform:translateY(-.24rem) !important; }
html.theme-night .app.focus .face {
  box-shadow:0 0 0 .20rem #6BE4FA !important;
  border-radius:22.5% !important;
}
html.theme-night .app:not(.focus) .face img { filter:none !important; }

/* Popup and full-screen controls must stay reachable with the remote. */
html.theme-night.setting .vy-brand, html.theme-night.setting .quick,
html.theme-night.expanded .vy-brand, html.theme-night.expanded .quick,
html.theme-night.gearing .quick, html.theme-night.apping .quick {
  visibility:hidden !important;
}
html.lighter.theme-night .grid, html.lighter.theme-night .qbtn {
  -webkit-backdrop-filter:none !important; backdrop-filter:none !important;
}
"""
with CSS.open("a", encoding="utf-8") as file:
    file.write("\n" + style + "\n")

# Static guardrails: no greeting, no profile selector, clock retains photo-glass implementation.
app_text = APP.read_text(encoding="utf-8")
css_text = CSS.read_text(encoding="utf-8")
html_text = HTML.read_text(encoding="utf-8")
assert "function hyGreeting(" not in app_text
assert "id=\"hy-greeting\"" not in html_text
assert '["people", "person"]' not in app_text
assert "vy-clock-position" in app_text
assert 'font-family:"Antonio"' in css_text
assert 'ICONS.gear + "<span>Configurações</span>"' in app_text
assert "VYFLUX" in html_text
assert "backdrop-filter:none !important" in css_text
assert "studio.ghstroot.vyflux.hy320" in app_text
print("VYFLUX_V3_PATCH_OK original_Couch_glass_clock=1 icon_replaced=1 banner_replaced=1 " +
      "pills=3 clock_positions=5 greeting_removed=1 people_hidden=1 low_cost_acrylic=1")
