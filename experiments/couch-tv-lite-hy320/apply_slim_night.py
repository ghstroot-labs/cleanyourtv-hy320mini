#!/usr/bin/env python3
"""HY320 Slim Night patch, applied only in GitHub Actions to pinned Couch TV source."""
from pathlib import Path
import json

ROOT = Path("upstream")
def patch(path, before, after):
    f = ROOT / path
    s = f.read_text(encoding="utf-8")
    if s.count(before) != 1:
        raise SystemExit(f"Unsafe upstream change: {path} has {s.count(before)} matches, expected one for {before[:80]!r}")
    f.write_text(s.replace(before, after, 1), encoding="utf-8")

app = "tv-home/web/app.js"
html = "tv-home/web/index.html"
css = "tv-home/web/app.css"
native = "tv-home/android/app/src/main/java/app/couchtv/launcher/MainActivity.kt"
manifest = "tv-home/android/app/src/main/AndroidManifest.xml"
i18n = "tv-home/web/i18n.js"

# Non-animated greeting, refreshed by the existing 15-second clock timer (no new timer).
patch(html, "</header>\n\n<!-- Ambient Music Art Screen", '</header>\n<div id="hy-greeting" class="hy-greeting" aria-label="Saudação"></div>\n\n<!-- Ambient Music Art Screen')
patch(app, "  function clock() {\n", '''  function hyGreeting(d) {
    var box = $("hy-greeting");
    if (!box) return;
    var h = d.getHours();
    var hello = h >= 5 && h < 12 ? "BOM DIA" : (h >= 12 && h < 18 ? "BOA TARDE" : "BOA NOITE");
    var message = hello + ", REBECA E NATAN! ❤️‍🔥";
    if (box.textContent !== message) box.textContent = message;
  }
  function clock() {
''')
patch(app, '    var d = new Date(), h = d.getHours(), m = d.getMinutes();\n',
      '    var d = new Date(), h = d.getHours(), m = d.getMinutes();\n    hyGreeting(d);\n')
patch(css, '/* ================= Older WebViews: no gap in flex boxes (#26) =================',
'''/* HY320 Slim Night: static greeting between scenery and dock. Never covers the large clock. */
.hy-greeting { display:none; }
html.theme-night .hy-greeting {
  display:block; position:fixed; left:4.75rem; bottom:19.5rem; z-index:4;
  color:#fff; font-size:1.55rem; font-weight:650; letter-spacing:0.015em;
  white-space:nowrap; text-shadow:0 0.125rem 0.75rem rgba(0,0,0,0.9);
  pointer-events:none;
}
/* Two useful text cards, no blur, video, shadow, or moving transitions. */
html.theme-night #q-wifi, html.theme-night #q-input {
  min-width:12rem; max-width:18rem; height:4.75rem; padding:0.5rem 1rem;
  border-radius:1rem; justify-content:flex-start; gap:0.75rem;
  transition:none; box-shadow:none;
}
html.theme-night #q-wifi span, html.theme-night #q-input span {
  display:block; font-size:1.2rem; font-weight:700; line-height:1.25;
  text-align:left; overflow:hidden; text-overflow:ellipsis; white-space:nowrap;
}
html.theme-night #q-wifi small, html.theme-night #q-input small {
  display:block; font-size:0.95rem; font-weight:450; opacity:0.82;
  overflow:hidden; text-overflow:ellipsis; white-space:nowrap; max-width:12.5rem;
}
html.theme-night #q-wifi.focus, html.theme-night #q-input.focus {
  transform:none; box-shadow:inset 0 0 0 0.1875rem #fff;
  background:rgba(16,16,20,0.93); color:#fff;
}
/* ================= Older WebViews: no gap in flex boxes (#26) =================''')

# Expose a read-only Wi-Fi status and an explicitly user-initiated permission request.
# No password, BSSID, MAC or scan data is retrieved or stored.
patch(manifest, '    <uses-permission android:name="android.permission.ACCESS_NETWORK_STATE" />',
'''    <uses-permission android:name="android.permission.ACCESS_NETWORK_STATE" />
    <uses-permission android:name="android.permission.ACCESS_WIFI_STATE" />
    <uses-permission android:name="android.permission.ACCESS_FINE_LOCATION" />''')
patch(native, 'import android.app.Activity\n', 'import android.app.Activity\nimport android.Manifest\nimport android.net.NetworkCapabilities\nimport android.net.wifi.WifiManager\n')
patch(native, '    override fun onNewIntent(intent: Intent) {\n',
'''    override fun onRequestPermissionsResult(
        requestCode: Int, permissions: Array<out String>, grantResults: IntArray
    ) {
        super.onRequestPermissionsResult(requestCode, permissions, grantResults)
        if (requestCode == 9081) js("window.hyWifiRefresh && window.hyWifiRefresh()")
    }

    override fun onNewIntent(intent: Intent) {
''')
patch(native, '    inner class Native {\n',
'''    inner class Native {
        /** The name of the connected network only, if the person granted Android location access. */
        @JavascriptInterface
        fun wifiStatus(): String {
            val cm = getSystemService(android.net.ConnectivityManager::class.java)
            val caps = cm?.activeNetwork?.let { cm.getNetworkCapabilities(it) }
            val connected = caps?.hasTransport(NetworkCapabilities.TRANSPORT_WIFI) == true
            val permitted = Build.VERSION.SDK_INT < 23 ||
                checkSelfPermission(Manifest.permission.ACCESS_FINE_LOCATION) == PackageManager.PERMISSION_GRANTED
            val ssid = if (connected && permitted) {
                try {
                    val wm = applicationContext.getSystemService(WIFI_SERVICE) as? WifiManager
                    val raw = wm?.connectionInfo?.ssid.orEmpty().trim('"')
                    if (raw.equals("<unknown ssid>", true) || raw == "0x" || raw.isBlank()) "" else raw
                } catch (_: Exception) { "" }
            } else ""
            return JSONObject().put("connected", connected).put("ssid", ssid)
                .put("permission", permitted).toString()
        }

        /** Only after pressing the Wi-Fi card. Does not change Wi-Fi settings. */
        @JavascriptInterface
        fun wifiCardAction(): Boolean {
            main.post {
                val cm = getSystemService(android.net.ConnectivityManager::class.java)
                val caps = cm?.activeNetwork?.let { cm.getNetworkCapabilities(it) }
                val connected = caps?.hasTransport(NetworkCapabilities.TRANSPORT_WIFI) == true
                if (connected && Build.VERSION.SDK_INT >= 23 &&
                    checkSelfPermission(Manifest.permission.ACCESS_FINE_LOCATION) != PackageManager.PERMISSION_GRANTED) {
                    requestPermissions(arrayOf(Manifest.permission.ACCESS_FINE_LOCATION), 9081)
                } else {
                    start(Intent(Settings.ACTION_WIFI_SETTINGS))
                }
            }
            return true
        }

''')

# Reuse the existing TV input menu and focus navigation, rather than a second key handler.
patch(app, 'var QUICK_ALL = ["sleep", "picture", "look", "soundscape", "screen_off", "headphones", "input", "bluetooth", "network", "screensaver"];',
'var QUICK_ALL = ["sleep", "picture", "look", "soundscape", "screen_off", "headphones", "input", "bluetooth", "network", "screensaver", "wifi"];')
patch(app, '      if (q === "input") return !OFFLINE || nativeInputs();',
'      if (q === "input") return !OFFLINE || nativeInputs() || !!(TV && TV.tvInputs);\n      if (q === "wifi") return !!(TV && TV.wifiStatus);')
patch(app, '  function renderQuick() {\n',
'''  function hyReadWifi() {
    try { return JSON.parse(TV.wifiStatus()); } catch (e) {}
    return { connected: false, permission: false, ssid: "" };
  }
  window.hyWifiRefresh = function () { if (quickReady) renderQuick(); };
  function renderQuick() {
''')
patch(app, '      } else if (q === "input") {\n        el.innerHTML = ICONS.input + "<span>" + esc(t("input")) + "</span>";',
'''      } else if (q === "wifi") {
        var wifi = hyReadWifi();
        var label = !wifi.connected ? "Desconectado" :
          wifi.ssid ? wifi.ssid : wifi.permission ? "Conectado" : "Toque para identificar";
        el.innerHTML = ICONS.network + "<span>Wi-Fi<small>" + esc(label) + "</small></span>";
      } else if (q === "input") {
        var ports = inputList();
        var names = ports.map(function (p) { return p.label || "HDMI"; }).slice(0, 2);
        var summary = names.length ? names.join(" · ") : "Ver entradas";
        el.innerHTML = ICONS.input + "<span>Entradas<small>" + esc(summary) + "</small></span>";''')
patch(app, '    else if (q === "input") openInputs();',
'''    else if (q === "input") openInputs();
    else if (q === "wifi") {
      try { if (TV && TV.wifiCardAction) TV.wifiCardAction(); } catch (e) {}
    }''')

# Brazilian Portuguese becomes a selectable language, automatically picked when TV locale is pt-*.
patch(i18n, '    { id: "en", name: "English", locale: "en-AU" },',
'''    { id: "en", name: "English", locale: "en-AU" },
    { id: "pt-BR", name: "Português (Brasil)", locale: "pt-BR", clock: "24h", country: "BR" },''')
patch(i18n, '    if (/^es-MX/i.test(n)) return "es-MX";',
'''    if (/^pt(?:-|$)/i.test(n)) return "pt-BR";
    if (/^es-MX/i.test(n)) return "es-MX";''')

# First batch: the home, navigation, visual settings, permissions and all on-screen primary controls.
# Untranslated rare advanced settings currently fall back to upstream English, never broken strings.
pt = {
"keep_watching":"Continuar assistindo","who_watching":"Quem está assistindo","apps":"Aplicativos","more_apps":"Mais aplicativos","app_store":"Loja de aplicativos","settings":"Configurações","new_app":"Novo","nothing_yet":"Nada em andamento por enquanto.","nothing_for":"Nada em andamento para {name}.",
"kids_mode":"Modo infantil","kids_shows_for":"Programas de {name}","kids_grown_ups":"Adultos","kids_ep":"Temporada {s}, episódio {e}","kids_season":"Temporada {s}","kids_pin_title":"Só para adultos","kids_pin_sub":"Digite o PIN dos responsáveis para sair do modo infantil.","kids_pin_typed":"{n} dígitos digitados","kids_pin_wait":"Muitas tentativas. Aguarde {n} segundos.","kids_pin_wrong":"PIN incorreto.","kids_pin_hint":"Use as setas e OK, ou os números. Voltar fecha.",
"everyone":"todos","off_in":"Desliga em {m} min","off_in_night":"Desliga em {m} min","sleep_timer":"Temporizador","switching":"Alterando…","picture_mode":"Modo de imagem","classic_look":"Visual clássico","oled_look":"Visual OLED Cinema","night_look":"Visual Noturno","input":"Entradas","bluetooth":"Bluetooth","network":"Rede","n_min":"{n} min","timer_off":"Desligado","soundscape":"Sons ambientes","screen_off":"Desligar tela","screen_off_wake_hint":"Pressione qualquer botão para reativar","sound_off":"Desligado","sound_rain":"Chuva suave","sound_fire":"Lareira","sound_waves":"Ondas do mar","sound_brown":"Ruído marrom","sound_volume":"Volume ambiente",
"no_inputs":"Nenhuma entrada foi encontrada pelo Android.","inputs_hint":"Acima e abaixo para escolher, OK para trocar, Voltar para fechar","bt_sub":"Caixas de som, fones e controles","net_sub":"Wi-Fi e rede","opening":"Abrindo {title}…","opening_in":"Abrindo {title} em {app}…","screen_not_set":"Esta tela ainda não foi configurada.","people_lift_hint":"Acima e abaixo para mover, OK para soltar","people_hold_hint":"Segure OK sobre um nome para mover","app_lift_hint":"Esquerda e direita para mover, abaixo para Mais aplicativos, OK para soltar","app_add_hint":"Segure OK em um aplicativo para adicioná-lo à tela inicial","saved":"Salvo.","that_app":"Esse aplicativo","ctx_move":"Mover","ctx_hide":"Ocultar da tela inicial","ctx_remove_shelf":"Remover de Continuar assistindo","ctx_uninstall":"Desinstalar","ctx_info":"Informações do aplicativo","cancel":"Cancelar","removed":"Removido",
"wx_clear":"Céu limpo","wx_mostly_clear":"Predomínio de sol","wx_partly":"Parcialmente nublado","wx_cloudy":"Nublado","wx_fog":"Neblina","wx_drizzle":"Garoa","wx_light_rain":"Chuva fraca","wx_rain":"Chuva","wx_heavy_rain":"Chuva forte","wx_showers":"Pancadas de chuva","wx_heavy_showers":"Pancadas fortes","wx_storms":"Tempestades",
"gear_home":"Configurações da tela inicial","gear_home_sub":"Idioma, clima, cenas, aplicativos e perfis","gear_tv":"Configurações do projetor","gear_tv_sub":"Wi-Fi, imagem, som e sistema","tv_settings_none":"Não foi possível abrir as configurações do projetor.","set_title":"Configurações da tela inicial","sec_language":"Idioma","sec_location":"Localização","sec_weather":"Clima","sec_look":"Aparência e paisagens","sec_apps":"Aplicativos","sec_people":"Pessoas","sec_quick":"Acessos rápidos","sec_about":"Sobre","hint_secs":"Acima e abaixo para escolher, OK para abrir, Voltar para fechar","hint_rows":"OK para alterar, Voltar para retornar","hint_rows_move":"OK para alterar, segure OK para mover, Voltar para retornar","hint_lift":"Acima e abaixo para mover, OK para soltar","hint_typing":"Digite com o controle ou teclado virtual e confirme em OK. Voltar cancela.","on":"Ativado","off":"Desativado","confirm_remove":"Pressione OK novamente para remover","confirm_reset":"Pressione OK novamente para redefinir","lang_note":"O controle pelo celular possui seu próprio idioma.",
"loc_now":"Cidade do clima","loc_unset":"Não definido","loc_search":"Buscar uma cidade","loc_type":"Digite uma cidade e confirme em OK","loc_searching":"Pesquisando…","loc_none":"Nada encontrado para “{q}”.","loc_error":"Não foi possível buscar a cidade. Confira o Wi-Fi.","loc_set":"Agora o clima é de {place}.","loc_reset":"Restaurar local do config.json","loc_results":"Locais encontrados","wx_show":"Mostrar clima","wx_units":"Unidades","wx_every":"Atualizar a cada","wx_provider":"Provedor","wx_night_only":"O clima aparece junto à data no visual Noturno.","every_min":"{n} minutos",
"look_head":"Aparência","look_night":"Paisagens noturnas","look_night_sub":"Relógio grande sobre a paisagem","look_oled":"OLED Cinema","look_oled_sub":"Fundo preto e foco luminoso","look_classic":"Clássico","look_classic_sub":"Uma foto e uma grade de aplicativos","scenes_head":"Paisagens","scene_night":"Noite","scene_golden":"Hora dourada","scene_water":"Reflexo na água","scene_fog":"Neblina","scene_dawn":"Amanhecer na floresta","scene_photo":"Sua foto {n}","scene_mine":"Sua paisagem {n}","sun_sync":"Acompanhar o sol","scene_secs":"Duração de cada paisagem","n_secs":"{n} segundos","clock":"Relógio","clock_12":"12 horas","clock_24":"24 horas","idle_photo":"Ocultar ícones quando inativo","one_scene":"É preciso manter ao menos uma paisagem.","photos_head":"Suas fotos","photos_pick":"Adicionar fotos do USB ou projetor","photos_pick_sub":"Abre o seletor de arquivos do Android","photos_no_pick":"Não há seletor de arquivos neste aparelho","photos_url":"Adicionar foto por link","photos_url_type":"Digite o endereço de uma imagem JPEG ou PNG e confirme em OK","photos_checking":"Abrindo foto…","photos_bad":"O endereço não abriu uma foto.","photos_added":"Foto adicionada à paisagem.","photos_added_n":"{n} fotos adicionadas.","photos_full":"O limite é de 50 fotos.","photos_count":"{n} de {max} fotos","photo_remove":"Remover foto {n}",
"glass_head":"Vidro","glass":"Painéis translúcidos","glass_lite":"Ativado, sem desfoque","moving_tiles":"Ícones em movimento","keep_show":"Mostrar Continuar assistindo","lighter":"Modo leve","lighter_note":"Reduz desfoque, sombras e animações para aparelhos lentos.","glass_icons":"Ícones translúcidos","glass_focus":"Aplicativo selecionado","glass_focus_colour":"Cores originais","glass_focus_glass":"Manter translúcido","hint_slider":"Esquerda e direita para alterar, Voltar para retornar","clock_liquid":"Vidro líquido","clock_frosted":"Fosco","clock_style":"Estilo do relógio","glass_amt_5":"Muito transparente","glass_amt_4":"Transparente","glass_amt_3":"Equilibrado","glass_amt_2":"Suave","glass_amt_1":"Fosco","glass_amount":"Transparência","video_head":"Fundo animado","video":"Vídeo de fundo","video_url":"Link do vídeo","video_none":"Nenhum","video_checking":"Abrindo vídeo…","video_bad":"O link não abriu um vídeo.","video_added":"Vídeo aplicado como fundo.","video_remove":"Remover vídeo","np_head":"Reproduzindo agora","np_show":"Cartão de reprodução","np_prev":"Anterior","np_play":"Reproduzir","np_pause":"Pausar","np_next":"Próximo","ambient_down_hint":"Pressione Baixo ou Voltar para os aplicativos","ambient_music":"Tela de música ambiente","ambient_open_app":"Abrir aplicativo","np_expand":"Tela cheia","sound_head":"Som","nav_sound":"Som da navegação","nav_sound_system":"Som do projetor","nav_sound_soft":"Suave","nav_sound_off":"Desligado",
"apps_home":"Na tela inicial ({n} de {max})","apps_more":"Em Mais aplicativos","apps_hidden":"Ocultos","app_on_home":"Na tela inicial","app_in_more":"Mais aplicativos","app_hidden":"Oculto","apps_none":"Nenhum aplicativo encontrado.","people_add":"Adicionar pessoa","people_type":"Digite um nome e confirme em OK","people_full":"O limite é de 12 pessoas.","person_name":"Nome","person_rename_type":"Digite o novo nome e confirme em OK","person_remove":"Remover {name}","person_on":"Assistindo agora",
"quick_sleep":"Temporizador","quick_picture":"Modo de imagem","quick_look":"Alternar aparência","quick_soundscape":"Sons ambientes","quick_headphones":"Fones Bluetooth","headphones":"Fones de ouvido","quick_screen_off":"Desligar tela","quick_input":"Lista de entradas","quick_screensaver":"Protetor de tela","no_screensaver":"Este aparelho não tem protetor de tela.","ambient_head":"Protetor de tela","ambient_settings":"Álbuns do Google Fotos","quick_bluetooth":"Dispositivos Bluetooth","quick_network":"Rede","quick_needs_bridge":"Exige computador","quick_note":"OK mostra ou oculta um botão. Segure OK para mudar a ordem.",
"about_version":"Versão","about_web":"Prévia web","about_code":"Couch TV no GitHub","about_running":"Executando","run_alone":"Direto no projetor, sem computador","run_bridge":"Com computador","run_off":"Computador desligado","run_quiet":"Computador não responde","about_kept":"Configurações salvas","kept_tv":"Neste aparelho","kept_both":"Neste aparelho e no computador","about_reset":"Redefinir configurações da tela inicial","reset_done":"Configurações restauradas.",
"sec_updates":"Atualizações","upd_auto":"Avisar sobre novas versões","upd_check":"Buscar atualizações","upd_checking":"Verificando…","upd_last":"Última verificação: {when}","upd_never":"Ainda não verificado","upd_latest":"Esta é a versão mais recente.","upd_install":"Atualizar para {v}","upd_downloading":"Baixando… {p}%","upd_confirm":"Confirme na tela que abrir","upd_gear":"Versão {v} pronta para instalar","upd_err_net":"Não foi possível acessar o GitHub. Confira o Wi-Fi.","upd_err_bad":"O arquivo baixado não passou na verificação. Nada foi instalado.","upd_err_other_key":"Esta edição foi compilada com outra assinatura e não pode receber essa atualização.","upd_err_cancelled":"Atualização cancelada. Nada mudou.","upd_err_failed":"O Android não instalou a atualização.","upd_ask_yes":"Sim, avisar","upd_ask_no":"Não, verificarei depois",
"home_ask":"Definir o Couch TV como tela inicial?","home_ask_yes":"Sim, mostrar","home_ask_no":"Agora não","home_row":"Definir o Couch TV como tela inicial","home_now":"O Couch TV já é sua tela inicial.","home_not_yet":"Ainda não foi alterado.",
"smart_home":"Casa inteligente","sh_climate":"Ar-condicionado","sh_scenes":"Cenas","sh_checking":"Verificando","sh_down":"O Home Assistant não respondeu.","sh_room_quiet":"Sem resposta","sh_set_to":"Definir para","sh_range":"Entre","sh_now":"Agora {t}","sh_off":"Desligado","sh_mode":"Modo","sh_mode_heat":"Aquecer","sh_mode_cool":"Resfriar","sh_mode_heat_cool":"Aquecer e resfriar","sh_mode_auto":"Automático","sh_mode_dry":"Desumidificar","sh_mode_fan_only":"Somente ventilador","sh_act_heating":"Aquecendo","sh_act_cooling":"Resfriando","sh_act_drying":"Desumidificando","sh_act_fan":"Ventilador ligado","sh_act_idle":"Em espera","sh_cooler":"Mais frio","sh_warmer":"Mais quente","sh_turn_on":"Ligar","sh_turn_off":"Desligar","sh_turned_on":"Ligando {name}","sh_turned_off":"Desligando {name}","sh_mode_now":"{name}: {mode}","sh_no_setpoint":"Configure isso no Home Assistant.","sh_no_modes":"Não há modos disponíveis.","sh_starting":"Iniciando {name}","sh_started":"{name}: concluído.","sh_failed":"Não foi possível concluir.","sh_refused":"Esta alteração não é permitida.","sh_hint":"Esquerda/direita para mover, cima/baixo entre linhas, OK para confirmar e Voltar para fechar."
}
pt.update({
    "devmode_gone": "O Couch TV não está mais instalado na TV. O Modo de Desenvolvedor pode ter expirado. Ative-o novamente e reinstale o Couch TV.",
    "devmode_runs_out": "O Modo de Desenvolvedor expira em {days} dias e a LG removerá o Couch TV. Ligue a TV por um minuto para renovar ou toque em Prorrogar no aplicativo do Modo de Desenvolvedor.",
    "devmode_not_renewed_left": "O Modo de Desenvolvedor não foi renovado há {days} dias (restam {left} dias). Será renovado quando a TV for ligada.",
    "devmode_not_renewed": "O Modo de Desenvolvedor não é renovado há {days} dias. Será renovado quando a TV for ligada.",
    "kids_empty": "Ainda não há programas aqui. Um responsável pode adicioná-los pelo controle no celular ou no config.json.",
    "kids_cant_open": "Não foi possível abrir {title}. Peça ajuda a um responsável.",
    "pic_not_ready": "A troca de modo de imagem ainda não está disponível aqui.",
    "computer_off": "O computador está desligado, então os programas ficam ocultos. Os aplicativos continuam funcionando.",
    "computer_quiet": "O computador não respondeu. Os aplicativos continuam funcionando.",
    "bridge_no": "O computador recusou a solicitação ({status}).",
    "bridge_down": "O computador não está respondendo.",
    "bridge_slow": "O computador demorou demais para responder.",
    "stays_put": "{name} permanece sempre nesta posição.",
    "already_home": "{name} já está na tela inicial.",
    "now_home": "{name} está na tela inicial.",
    "moved_more": "{name} foi movido para Mais aplicativos.",
    "ctx_hint": "Acima e abaixo para escolher, OK para executar, Voltar para fechar",
    "ctx_hidden": "Ocultado. Para mostrar novamente, vá a Configurações, Aplicativos.",
    "photo_by": "Foto: {by}",
    "photo_albury": "Tempestade ao pôr do sol, Albury",
    "photo_aresquiers": "Praia de Aresquiers, França",
    "am": "a.m.",
    "pm": "p.m.",
    "loc_note": "Define a cidade e o fuso horário do clima. Uma cidade ou bairro basta; não informe seu endereço. Busca pelo Open-Meteo.",
    "wx_provider_note": "Gratuito, sem conta nem chave. Único provedor por enquanto.",
    "wx_ambient": "Efeitos de clima na paisagem",
    "wx_ambient_sub": "Chuva, neve e neblina suaves sobre as paisagens",
    "wx_sun_grade": "Tonalidade conforme a luz do sol",
    "wx_sun_grade_sub": "Tons quentes ao amanhecer e ao pôr do sol",
    "sun_sync_sub": "Escolhe a paisagem conforme amanhecer, dia, entardecer e noite da sua região",
    "idle_photo_sub": "Após um período sem comandos, oculta aplicativos, Continuar assistindo e perfis. Relógio, clima e fotos permanecem. Qualquer tecla restaura as linhas sem abrir um aplicativo.",
    "photos_no_pick_sub": "Use um link para adicionar uma foto.",
    "photos_storage": "Suas fotos ficam neste aparelho. Cada imagem consome armazenamento e memória; muitas fotos podem deixar aparelhos antigos lentos.",
    "photos_note": "Suas fotos se alternam com as paisagens. No visual Clássico, elas substituem as imagens originais.",
    "glass_note": "Vidro fosco atrás do relógio, {keep} e dos aplicativos, deixando a paisagem aparecer. Em aparelhos lentos, escolha Ativado, sem desfoque.",
    "moving_tiles_note": "O ícone selecionado balança suavemente. Desative se houver tremulação ou lentidão.",
    "glass_icons_note": "Os símbolos dos aplicativos aparecem sobre vidro claro, sem fundo próprio, e recuperam as cores ao serem selecionados.",
    "glass_amount_note": "Controla quanto da paisagem aparece através do vidro, relógio e ícones, de fosco a muito transparente.",
    "video_url_type": "Digite o link para um vídeo MP4 ou MOV e confirme em OK",
    "video_apple": "O endereço usa um servidor de vídeo da Apple que o Android TV não reconhece como confiável. Use outro link ou uma cópia armazenada em um computador da rede.",
    "video_note": "Um vídeo curto, sem som e em repetição, substitui a foto. Informe um link MP4 ou MOV na internet ou na rede local. Se não reproduzir, a foto permanece. Desative em aparelhos lentos.",
    "np_note": "Mostra a música reproduzida no Spotify ou em outro aplicativo, com botões Anterior, Reproduzir/Pausar e Próximo. Pressione Acima a partir de Continuar assistindo.",
    "np_note_offline": "Exige um computador na rede ou o aplicativo instalado na TV: sem eles, o Android não permite acessar a reprodução em andamento.",
    "apps_note": "OK move um aplicativo entre a tela inicial, Mais aplicativos e Ocultos. Segure OK para reorganizar.",
    "apps_classic": "O visual Clássico mantém sua própria ordem. Ocultar funciona nos dois modos.",
    "people_none": "Nenhuma pessoa cadastrada. Nesse caso, Continuar assistindo mostra tudo.",
    "people_note": "Uma pessoa: sem seletor. Duas: alternador. Três ou mais: ícone redondo com lista.",
    "headphones_not_found": "Não foi possível acessar os fones",
    "no_dream": "O protetor de tela não iniciou as fotos. Tente de novo ou reinicie o aparelho se o problema persistir.",
    "ambient_settings_sub": "Escolha os álbuns exibidos quando o aparelho estiver inativo.",
    "quick_needs_tv_app": "Exige o aplicativo instalado no aparelho",
    "quick_needs_picture": "Exige o computador e uma configuração de imagem",
    "quick_needs_inputs": "Exige o computador ou um aparelho com lista de entradas",
    "about_reset_sub": "Idioma, local, clima, aparência, fotos e acessos rápidos voltam ao config.json. Pessoas e aplicativos são preservados.",
    "upd_told": "Couch TV {v} disponível: Configurações, Tela inicial, Atualizações.",
    "upd_note": "As atualizações vêm dos lançamentos do Couch TV no GitHub. Com os avisos ativados, o aparelho verifica uma vez por semana e sempre pede confirmação antes de instalar. Suas configurações permanecem.",
    "upd_err_allow": "Primeiro permita que o aplicativo instale outros apps: em Configurações do Android, Fontes desconhecidas (Segurança e restrições). Depois tente Atualizar.",
    "upd_ask": "Quer ser avisado quando houver uma nova versão do Couch TV?",
    "upd_ask_sub": "O aparelho verifica uma vez por semana e mostra um indicador em Configurações. Nunca instala sem perguntar.",
    "upd_ask_yes_sub": "Verificação semanal",
    "upd_ask_no_sub": "Configurações da tela inicial, Atualizações, a qualquer momento",
    "upd_ask_done": "Salvo. Você pode alterar em Configurações da tela inicial, Atualizações.",
    "home_ask_sub": "Assim, o botão Início abre este aplicativo. O Android mostrará um seletor: escolha este app e toque em Sempre. A tela inicial original permanece instalada.",
    "home_ask_yes_sub": "Abre o seletor de tela inicial do Android",
    "home_ask_no_sub": "Configurações da tela inicial, Sobre, a qualquer momento",
    "home_row_sub": "Pede ao Android para abrir este aplicativo ao pressionar Início",
    "home_google_tv": "Este é um Google TV, que pode manter sua tela original no botão Início. A função de monitorar o botão Início pode trazer o Couch TV de volta; consulte o README.",
})

# Protect against typos in localization keys, and verify placeholders remain unchanged.
import re
src = (ROOT / i18n).read_text(encoding="utf-8")
begin = src.index("  S.en = {")
end = src.index("\n  S.es = {", begin)
english = src[begin:end]
all_keys = dict(re.findall(r'^\s{4}([a-z][a-z0-9_]*):\s*"((?:[^"\\]|\\.)*)"', english, re.M))
for key, value in pt.items():
    if key not in all_keys:
        raise SystemExit(f"Unknown pt-BR key: {key}")
    slots = lambda s: sorted(re.findall(r'\{[a-zA-Z0-9_]+\}', s))
    if slots(value) != slots(all_keys[key]):
        raise SystemExit(f"pt-BR placeholder mismatch for {key}")
# Full coverage is enforced by a separate audit below; until then, English remains as safe fallback.
js = json.dumps(pt, ensure_ascii=False, separators=(',', ':'))
patch(i18n, "\n  S.es = {", "\n  S['pt-BR'] = " + js + ";\n\n  S.es = {")
print(f"SLIM_NIGHT_PATCH_APPLIED pt_br_keys={len(pt)} upstream_english_keys={len(all_keys)}")
