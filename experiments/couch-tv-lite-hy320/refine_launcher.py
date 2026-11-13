#!/usr/bin/env python3
"""Safe refinements for the isolated HY320 Couch TV build."""
from pathlib import Path
import json
import re

ROOT = Path("upstream")
WEB = ROOT / "tv-home/web"
APP = WEB / "app.js"
CSS = WEB / "app.css"
HTML = WEB / "index.html"
I18N = WEB / "i18n.js"


def patch(path: Path, before: str, after: str) -> None:
    source = path.read_text(encoding="utf-8")
    count = source.count(before)
    if count != 1:
        raise SystemExit(f"Unsafe baseline: {path} has {count} matches; expected exactly one for {before[:100]!r}")
    path.write_text(source.replace(before, after, 1), encoding="utf-8")


# Keep the location fixed to the municipal centre of Palhoça, SC.
config_path = ROOT / "config.json"
config = json.loads(config_path.read_text(encoding="utf-8"))
config["people"] = []
config["weather"] = {
    "lat": -27.64500046,
    "lon": -48.66799927,
    "place": "Palhoça, SC",
    "timezone": "America/Sao_Paulo",
}
config.setdefault("home", {})["people_enabled"] = False
config_path.write_text(json.dumps(config, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

# Fully disable profile UI while retaining the app's internal shared-household fallback.
patch(APP,
      'var PEOPLE = [], NOBODY = false, who = null, pi = 0;',
      'var PEOPLE_DISABLED = true, PEOPLE = [], NOBODY = false, who = null, pi = 0;')
patch(APP,
      'PEOPLE = (list || []).filter(function (p) { return p && p.id && p.name; });',
      'PEOPLE = PEOPLE_DISABLED ? [] : (list || []).filter(function (p) { return p && p.id && p.name; });')
patch(APP,
      'var SECS = [["language", "globe"], ["location", "pin"], ["weather", "cloud"], ["look", "look"],\n    ["apps", "apps"], ["people", "person"], ["quick", "bolt"], ["about", "info"]];',
      'var SECS = [["language", "globe"], ["weather", "cloud"], ["look", "look"],\n    ["apps", "apps"], ["quick", "bolt"], ["about", "info"]];')
patch(APP,
      '  var WX_DEFAULT = { lat: -33.8688, lon: 151.2093, place: "Sydney", timezone: "Australia/Sydney" };',
      '  var WX_DEFAULT = { lat: -27.64500046, lon: -48.66799927, place: "Palhoça, SC", timezone: "America/Sao_Paulo" };')
patch(APP,
      '    if (CFG.weather) WXCFG = CFG.weather;\n    var pl = ST.place;\n    if (pl && isFinite(pl.lat) && isFinite(pl.lon)) WXCFG = { lat: pl.lat, lon: pl.lon, place: pl.name || "", timezone: pl.timezone || "auto" };',
      '    WXCFG = CFG.weather || WX_DEFAULT;\n    delete ST.place; // This HY320 build uses Palhoça as its fixed weather location.')
patch(APP,
      '    WX_EVERY = [15, 30, 60].indexOf(ST.wx_every) >= 0 ? ST.wx_every : 30;',
      '    WX_EVERY = [15, 30, 60].indexOf(ST.wx_every) >= 0 ? ST.wx_every : 15;')

# Use Open-Meteo's current model output at the land grid cell and validate responses.
patch(APP,
      '    var url = "https://api.open-meteo.com/v1/forecast?latitude=" + WXCFG.lat + "&longitude=" + WXCFG.lon +\n      "&current=temperature_2m,weather_code,is_day&timezone=" + encodeURIComponent(WXCFG.timezone || "auto") + "&forecast_days=1";\n    return fetch(url).then(function (r) { return r.json(); }).then(function (j) {\n      var c = j.current, code = Math.round(c.weather_code);\n      return { temp: Math.round(c.temperature_2m), code: code, text: "", is_day: !!c.is_day };\n    });',
      '    var url = "https://api.open-meteo.com/v1/forecast?latitude=" + WXCFG.lat + "&longitude=" + WXCFG.lon +\n      "&current=temperature_2m,weather_code,is_day,apparent_temperature,relative_humidity_2m,precipitation,wind_speed_10m" +\n      "&timezone=" + encodeURIComponent(WXCFG.timezone || "America/Sao_Paulo") + "&forecast_days=1&cell_selection=land";\n    return fetch(url, { cache: "no-store" }).then(function (r) {\n      if (!r.ok) throw new Error("weather " + r.status);\n      return r.json();\n    }).then(function (j) {\n      var c = j && j.current;\n      if (!c || !isFinite(c.temperature_2m) || !isFinite(c.weather_code)) throw new Error("weather data unavailable");\n      return { temp: Math.round(c.temperature_2m), code: Math.round(c.weather_code), text: "", is_day: !!c.is_day,\n        apparent: isFinite(c.apparent_temperature) ? Math.round(c.apparent_temperature) : null,\n        humidity: isFinite(c.relative_humidity_2m) ? Math.round(c.relative_humidity_2m) : null,\n        precipitation: isFinite(c.precipitation) ? c.precipitation : null,\n        wind: isFinite(c.wind_speed_10m) ? c.wind_speed_10m : null };\n    });')

# Let the first frame render before starting network weather work.
patch(APP,
      '      refreshWeather();\n      setInterval(refreshWeather, WX_EVERY * 60000);',
      '      // Render the home screen first; weather is non-critical to the initial frame.\n      setTimeout(function () {\n        refreshWeather();\n        setInterval(refreshWeather, WX_EVERY * 60000);\n      }, 1200);')
# With profiles removed, there is no reason to poll the bridge for profile changes.
patch(APP,
      '    if (!OFFLINE) setInterval(followWho, 3000);',
      '    if (!OFFLINE && !PEOPLE_DISABLED) setInterval(followWho, 3000);')

# The hidden DOM nodes remain because the upstream renderer references them; they no longer occupy UI space.
patch(CSS,
      '/* Two useful text cards, no blur, video, shadow, or moving transitions. */',
      '/* Couch TV Slim Night: profiles are intentionally disabled on this two-person projector. */\n.top-left .people-wrap { display: none !important; }\n\n/* Two useful text cards, no blur, video, shadow, or moving transitions. */')
patch(CSS,
      'html.theme-night #q-wifi, html.theme-night #q-input {\n  min-width:12rem; max-width:18rem; height:4.75rem; padding:0.5rem 1rem;\n  border-radius:1rem; justify-content:flex-start; gap:0.75rem;\n  transition:none; box-shadow:none;\n}',
      'html.theme-night #q-wifi, html.theme-night #q-input {\n  min-width:16.5rem; max-width:22.5rem; height:6.25rem; padding:0.75rem 1.4rem;\n  border-radius:999px; justify-content:flex-start; gap:1rem;\n  background:rgba(12,14,18,0.48); border:1px solid rgba(255,255,255,0.18);\n  backdrop-filter:blur(8px); -webkit-backdrop-filter:blur(8px);\n  transition:none; box-shadow:none;\n}\nhtml.theme-night #q-wifi span, html.theme-night #q-input span {\n  display:block; font-size:1.75rem; font-weight:700; line-height:1.3;\n  text-align:left; overflow:hidden; text-overflow:ellipsis; white-space:nowrap;\n}\nhtml.theme-night #q-wifi small, html.theme-night #q-input small {\n  display:block; font-size:1.25rem; font-weight:500; line-height:1.3; opacity:0.9;\n  overflow:hidden; text-overflow:ellipsis; white-space:nowrap; max-width:17rem;\n}\nhtml.theme-night #q-wifi svg, html.theme-night #q-input svg {\n  width:2.5rem; height:2.5rem; flex:none;\n}')

patch(HTML, '<html lang="en-AU">', '<html lang="pt-BR">')
patch(HTML, '<title>Home</title>', '<title>Couch TV Slim Night BR</title>')

# A small copy review for wording that remains visible in this configuration.
i18n = I18N.read_text(encoding="utf-8")
match = re.search(r"S\['pt-BR'\] = (\{.*?\});", i18n, re.S)
if not match:
    raise SystemExit("Could not locate the pt-BR dictionary safely")
pt = json.loads(match.group(1))
pt.update({
    "wx_mostly_clear": "Predominantemente ensolarado",
    "gear_home_sub": "Idioma, clima, aparência e aplicativos",
    "idle_photo_sub": "Após um período sem comandos, oculta os aplicativos e a seção Continuar assistindo. O relógio, o clima e as paisagens permanecem visíveis. Qualquer tecla restaura a tela sem abrir um aplicativo.",
    "about_reset_sub": "O idioma, o clima, a aparência, as fotos e os acessos rápidos voltam às configurações do config.json. Os aplicativos instalados são preservados.",
})
pt.update({
    "wx_mostly_clear": "Predomínio de sol",
    "wx_provider_note": "Serviço gratuito, sem conta nem chave de API. É o único provedor disponível no momento.",
    "sun_sync_sub": "Escolhe a paisagem de acordo com o amanhecer, o dia, o entardecer e a noite da sua região.",
    "glass_note": "Aplica um efeito de vidro fosco atrás do relógio, de {keep} e dos aplicativos, permitindo que a paisagem continue visível. Em aparelhos mais lentos, escolha Ativado, sem desfoque.",
    "glass_amount_note": "Controla quanto da paisagem aparece através do vidro, do relógio e dos ícones, variando entre fosco e muito transparente.",
    "np_note": "Mostra a música reproduzida no Spotify ou em outro aplicativo e oferece os controles Anterior, Reproduzir/Pausar e Próximo. Na seção Continuar assistindo, pressione a seta para cima.",
    "np_note_offline": "Para acessar a reprodução em andamento, é necessário ter um computador na rede ou o aplicativo instalado na TV.",
    "quick_note": "Pressione OK para mostrar ou ocultar um botão. Mantenha OK pressionado para alterar a ordem.",
    "hint_slider": "Use as setas esquerda e direita para ajustar. Pressione Voltar para retornar.",
    "photos_pick": "Adicionar fotos de um dispositivo USB ou do projetor",
    "video_note": "Um vídeo curto, sem som e em repetição substitui a foto. Informe um link MP4 ou MOV da internet ou da rede local. Se a reprodução falhar, a foto continuará sendo exibida. Em aparelhos mais lentos, deixe esse recurso desativado.",
    "upd_err_allow": "Primeiro, permita que este aplicativo instale outros aplicativos. Nas configurações do Android, abra Segurança e restrições e habilite Fontes desconhecidas. Em seguida, tente novamente.",
    "run_alone": "Diretamente no projetor, sem computador",
    "run_quiet": "O computador não está respondendo",
    "home_ask_sub": "Assim, o botão Início abrirá este aplicativo. O Android exibirá um seletor: escolha este aplicativo e selecione Sempre. A tela inicial original continuará instalada."
})
i18n = i18n[:match.start(1)] + json.dumps(pt, ensure_ascii=False, separators=(",", ":")) + i18n[match.end(1):]
I18N.write_text(i18n, encoding="utf-8")

# Verify the intended configuration and guard against accidental feature regressions.
check = json.loads(config_path.read_text(encoding="utf-8"))
assert check["people"] == []
assert check["weather"]["place"] == "Palhoça, SC"
js = APP.read_text(encoding="utf-8")
css = CSS.read_text(encoding="utf-8")
assert "PEOPLE_DISABLED = true" in js
assert '["people", "person"]' not in js
assert 'border-radius:999px' in css
assert "cell_selection=land" in js
assert "weather data unavailable" in js
assert "setTimeout(function () {\n        refreshWeather();" in js
print("HY320_REFINEMENTS_OK people=hidden pills=rounded weather=Palhoca refresh=15m boot=deferred")
