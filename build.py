#!/usr/bin/env python3
"""Generador de la web de ARVI.

    python3 build.py

Lee src/content/** (fragmentos HTML de cada página), src/pages.json (títulos) y src/static/**
(CSS, JS, imágenes) y escribe el sitio completo en la raíz del repositorio (lo que sirve GitHub Pages).
Solo necesita Python 3 y beautifulsoup4 + lxml.
"""
import json, re, shutil, pathlib, html as H
from bs4 import BeautifulSoup, NavigableString

ROOT = pathlib.Path(__file__).resolve().parent
SRC = ROOT / "src"
SITE_URL = "https://jesusccl07.github.io/ARVI-Assistant/"
PAGES = json.loads((SRC / "pages.json").read_text(encoding="utf-8"))

# ───────────────────────── Navegación ─────────────────────────
def chapter(n, slug, title):
    return (f"memoria-academica/{slug}", f"{n}. {title}")

MEMORIA = [
    ("memoria-academica", "Resumen de la memoria"),
    chapter(1, "01-introduccion", "Introducción y motivación"),
    chapter(2, "02-objetivos", "Objetivos"),
    chapter(3, "03-requisitos", "Análisis de requisitos"),
    chapter(4, "04-tecnologias", "Estudio de tecnologías"),
    chapter(5, "05-diseno", "Diseño y arquitectura"),
    chapter(6, "06-planificacion", "Planificación del proyecto"),
    chapter(7, "07-entorno", "Preparación del entorno"),
    chapter(8, "08-backend", "Desarrollo del backend"),
    chapter(9, "09-openai", "Integración con OpenAI"),
    chapter(10, "10-voz", "Sistema de voz"),
    chapter(11, "11-memoria", "Memoria persistente con Obsidian"),
    chapter(12, "12-n8n", "Integración con n8n"),
    chapter(13, "13-herramientas-permisos", "Herramientas y permisos"),
    chapter(14, "14-interfaz", "Interfaz gráfica y animaciones"),
    chapter(15, "15-movil", "Escritorio (PWA y Tauri) y móvil"),
    chapter(16, "16-integraciones", "Integraciones externas"),
    chapter(17, "17-seguridad", "Seguridad y privacidad"),
    chapter(18, "18-pruebas", "Pruebas y resultados"),
    chapter(19, "19-incidencias", "Incidencias y soluciones"),
    chapter(20, "20-presupuesto", "Presupuesto"),
    chapter(21, "21-conclusiones", "Conclusiones"),
    chapter(22, "22-mejoras", "Posibles mejoras futuras"),
    chapter(23, "23-bibliografia-anexos", "Bibliografía y anexos"),
    chapter(24, "24-domotica", "Hogar inteligente (Home Assistant)"),
    chapter(25, "25-control-remoto", "Varios ordenadores (ARVI Remote)"),
    chapter(26, "26-aprendizaje-voz", "Aprendizaje de la voz («Mi voz»)"),
    ("memoria-academica/anexo-uso-ia", "Anexo · Uso de herramientas de IA"),
]
SECTIONS = [
    {"id": "memoria", "label": "Memoria", "home": "memoria-academica", "groups": [("Memoria académica", MEMORIA)]},
    {"id": "desarrollo", "label": "Desarrollo", "home": "DIARIO_DESARROLLO", "groups": [("Desarrollo", [
        ("DIARIO_DESARROLLO", "Diario de desarrollo"),
        ("01-analisis-entorno", "Análisis del entorno"),
        ("arquitectura/decisiones-tecnologicas", "Decisiones tecnológicas"),
        ("telefonia", "Telefonía"),
        ("desarrollo/HERRAMIENTAS_CLAUDE", "Herramientas de Claude Code"),
    ])]},
    {"id": "pruebas", "label": "Pruebas", "home": "pruebas/registro-pruebas", "groups": [("Pruebas", [
        ("pruebas/registro-pruebas", "Registro de pruebas"),
        ("pruebas/incidencias", "Incidencias"),
        ("pruebas/evidencias/openai-real-2026-11-12", "Evidencias · OpenAI real"),
        ("pruebas/evidencias/voz-real-2026-11-12", "Evidencias · voz real"),
        ("capturas/figuras", "Capturas"),
    ])]},
    {"id": "gestion", "label": "Gestión", "home": "gestion/presupuesto", "groups": [("Gestión", [
        ("gestion/presupuesto", "Presupuesto y licencias"),
    ])]},
]
ROUTE_SECTION = {r: s for s in SECTIONS for g in s["groups"] for r, _ in g[1]}
ROUTE_LABEL = {r: l for s in SECTIONS for g in s["groups"] for r, l in g[1]}

# ───────────────────────── Iconos ─────────────────────────
def svg(d, extra=""):
    return f'<svg viewBox="0 0 24 24" aria-hidden="true" {extra}>{d}</svg>'
ICON = {
    "arrow": svg('<path d="M5 12h14M13 6l6 6-6 6"/>'),
    "search": svg('<circle cx="11" cy="11" r="7"/><path d="m20 20-3.5-3.5"/>'),
    "sun": svg('<circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M2 12h2M20 12h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4"/>', 'class="sun"'),
    "moon": svg('<path d="M20 14.5A8.5 8.5 0 0 1 9.5 4a8.5 8.5 0 1 0 10.5 10.5z"/>', 'class="moon"'),
    "menu": svg('<path d="M4 7h16M4 12h16M4 17h16"/>'),
    "clock": svg('<circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/>'),
    "mic": svg('<rect x="9" y="3" width="6" height="12" rx="3"/><path d="M5 11a7 7 0 0 0 14 0M12 18v3"/>'),
    "memory": svg('<ellipse cx="12" cy="6" rx="8" ry="3"/><path d="M4 6v6c0 1.7 3.6 3 8 3s8-1.3 8-3V6M4 12v6c0 1.7 3.6 3 8 3s8-1.3 8-3v-6"/>'),
    "shield": svg('<path d="M12 3l8 3v6c0 4.5-3.2 8-8 9-4.8-1-8-4.5-8-9V6z"/><path d="m9 12 2 2 4-4"/>'),
    "flow": svg('<circle cx="6" cy="6" r="2.5"/><circle cx="18" cy="12" r="2.5"/><circle cx="6" cy="18" r="2.5"/><path d="M8.3 7l7.4 4M8.3 17l7.4-4"/>'),
    "home": svg('<path d="M4 11l8-7 8 7v9a1 1 0 0 1-1 1h-4v-6H9v6H5a1 1 0 0 1-1-1z"/>'),
    "monitor": svg('<rect x="3" y="4" width="18" height="12" rx="2"/><path d="M8 20h8M12 16v4"/>'),
    "github": svg('<path d="M9 19c-4.3 1.4-4.3-2.5-6-3m12 5v-3.5c0-1 .1-1.4-.5-2 2.8-.3 5.5-1.4 5.5-6a4.6 4.6 0 0 0-1.3-3.2 4.2 4.2 0 0 0-.1-3.2s-1.1-.3-3.5 1.3a12 12 0 0 0-6.2 0C6.5 2.8 5.4 3.1 5.4 3.1a4.2 4.2 0 0 0-.1 3.2A4.6 4.6 0 0 0 4 9.5c0 4.6 2.7 5.7 5.5 6-.6.6-.6 1.2-.5 2V21"/>'),
}

LOGO = "assets/img/arvi-logo.svg"

def rel(route):
    return "../" * (len(route.split("/")) if route else 0)

def url(route):
    return route + "/" if route else ""

# ───────────────────────── Plantilla común ─────────────────────────
THEME_BOOT = ("<script>(function(){try{var t=localStorage.getItem('arvi-theme');"
              "document.documentElement.dataset.theme=t||'dark'}catch(e){document.documentElement.dataset.theme='dark'}"
              "})()</script>")
FONTS = ('<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
         '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Geist:wght@300..700&family=JetBrains+Mono:wght@400;500;600&family=Sora:wght@500..700&display=swap">')

def head(title, desc, r, route, body_class=""):
    full = "ARVI · Asistente de Respuesta por Voz e Integraciones" if not route else f"{title} · ARVI"
    canon = SITE_URL + url(route)
    return f'''<!doctype html>
<html lang="es" data-root="{r}" data-theme="dark">
<head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{H.escape(full)}</title>
<meta name="description" content="{H.escape(desc, quote=True)}">
<meta name="theme-color" content="#060914">
<meta property="og:title" content="{H.escape(full, quote=True)}"><meta property="og:description" content="{H.escape(desc, quote=True)}"><meta property="og:type" content="website"><meta property="og:url" content="{canon}">
<link rel="canonical" href="{canon}">
<link rel="icon" href="{r}{LOGO}" type="image/svg+xml">
{THEME_BOOT}
{FONTS}
<link rel="stylesheet" href="{r}assets/css/arvi.css">
</head>
<body class="{body_class}">
<a class="skip" href="#contenido">Saltar al contenido</a>
<div id="progress" aria-hidden="true"></div>
'''

def header(r, active_id):
    links = "".join(
        f'<a href="{r}{url(s["home"])}"{" aria-current=\"page\"" if s["id"] == active_id else ""}>{s["label"]}</a>' for s in SECTIONS)
    return f'''<header class="hdr"><div class="hdr-in">
<button class="ico-btn burger" type="button" aria-label="Abrir menú" aria-expanded="false">{ICON["menu"]}</button>
<a class="brand" href="{r or "./"}" aria-label="ARVI, inicio"><img src="{r}{LOGO}" alt="" width="30" height="30">ARVI</a>
<nav class="topnav" aria-label="Secciones">{links}</nav>
<span class="hdr-sp"></span>
<button class="btn-search" type="button" data-search aria-label="Buscar">{ICON["search"].replace("<svg", '<svg width="18" height="18" style="stroke:currentColor;fill:none;stroke-width:1.8"')}<span class="t">Buscar</span><kbd>Ctrl K</kbd></button>
<button class="ico-btn theme-t" type="button" aria-label="Cambiar entre tema claro y oscuro">{ICON["moon"]}{ICON["sun"]}</button>
<a class="ico-btn" href="https://github.com/Jesusccl07/ARVI-Assistant" aria-label="Repositorio en GitHub" rel="noopener">{ICON["github"]}</a>
</div></header>
'''

def footer(r):
    return f'''<footer class="ftr"><div class="ftr-in">
<a class="brand" href="{r or "./"}"><img src="{r}{LOGO}" alt="" width="24" height="24">ARVI</a>
<span>Asistente de Respuesta por Voz e Integraciones · Proyecto Final de Ciclo Formativo de Grado Superior</span>
<nav aria-label="Pie">{"".join(f'<a href="{r}{url(s["home"])}">{s["label"]}</a>' for s in SECTIONS)}</nav>
</div></footer>
<script src="{r}assets/js/app.js" defer></script>
'''

# ───────────────────────── Procesado del contenido ─────────────────────────
OK = ("completo", "completa", "completada", "cumplido", "aceptada", "superada", "superado", "ok", "hecho", "hecha", "resuelta", "resuelto", "pasa", "real")
WARN = ("pendiente", "[pendiente]", "parcial", "propuesta", "en curso", "abierta", "abierto")
BAD = ("sustituida", "falla", "fallida", "no cumplido", "bloqueada")

def slug_text(s):
    return re.sub(r"\s+", " ", s).strip()

def process(route, body):
    soup = BeautifulSoup(f"<div id='root'>{body}</div>", "lxml")
    root = soup.select_one("#root")
    # tablas: contenedor con scroll + estados como etiquetas
    for t in root.find_all("table"):
        if route == "memoria-academica":
            ths = [th.get_text(strip=True) for th in t.find_all("th")]
            if "Archivo" in ths:
                i = ths.index("Archivo")
                for tr in t.find_all("tr"):
                    cells = tr.find_all(["th", "td"])
                    if len(cells) > i: cells[i].decompose()
            for td in t.select("tbody tr td:first-child"):
                m = re.match(r"(\d+)\.", td.get_text(strip=True))
                if m:
                    ch = next((r for r, l in MEMORIA if l.startswith(m.group(1) + ". ")), None)
                    if ch:
                        a = soup.new_tag("a", href="../" + ch.split("/")[-1] + "/")
                        a["class"] = "row-link"; a.string = td.get_text(strip=True)
                        td.clear(); td.append(a)
        for td in t.find_all("td"):
            txt = slug_text(td.get_text())
            low = txt.lower().rstrip(".")
            if 0 < len(txt) <= 26 and not td.find("a"):
                kind = "ok" if low.startswith(OK) else "warn" if low.startswith(WARN) else "bad" if low.startswith(BAD) else None
                if kind:
                    sp = soup.new_tag("span"); sp["class"] = f"pill {kind}"; sp.string = txt
                    td.clear(); td.append(sp)
        wrap = soup.new_tag("div"); wrap["class"] = "table-wrap"
        t.wrap(wrap)
    # diagramas Mermaid
    for pre in root.select("pre.mermaid"):
        code = pre.get_text()
        m = re.search(r"%%\s*figura:\s*(.+)", code)
        cap = m.group(1).strip() if m else "Diagrama"
        fig = soup.new_tag("figure"); fig["class"] = "diagram rv"
        body_div = soup.new_tag("div"); body_div["class"] = "diagram-body"
        body_div["title"] = "Pulsa para ampliar"
        load = soup.new_tag("div"); load["class"] = "load"
        pre.wrap(fig); pre.wrap(body_div)
        body_div.insert(0, load)
        fc = soup.new_tag("figcaption"); fc.string = cap
        fig.append(fc)
    # imágenes con carga diferida
    for img in root.find_all("img"):
        img["loading"] = "lazy"; img["decoding"] = "async"
    # [PENDIENTE]
    for node in list(root.find_all(string=re.compile(r"\[PENDIENTE\]"))):
        if node.find_parent(["code", "pre", "a", "h1", "h2", "h3"]): continue
        parts = re.split(r"(\[PENDIENTE\])", str(node))
        frag = []
        for p in parts:
            if p == "[PENDIENTE]":
                mk = soup.new_tag("mark"); mk["class"] = "pend"; mk.string = "PENDIENTE"; frag.append(mk)
            elif p: frag.append(NavigableString(p))
        for f in frag: node.insert_before(f)
        node.extract()
    # enlaces de ancla en títulos + índice
    toc = []
    for h in root.find_all(["h2", "h3", "h4"]):
        if not h.get("id"): continue
        a = soup.new_tag("a", href="#" + h["id"]); a["class"] = "anchor"; a["aria-label"] = "Enlace a esta sección"; a.string = "#"
        h.insert(0, a)
        if h.name in ("h2", "h3"):
            toc.append((h.name, h["id"], h.get_text(" ", strip=True).lstrip("# ").strip()))
    # enlaces externos
    for a in root.find_all("a", href=re.compile(r"^https?://")):
        a["rel"] = "noopener"
    if len(toc) > 40:
        toc = [t for t in toc if t[0] == "h2"]
    words = len(root.get_text(" ").split())
    return root.decode_contents(), toc, words, root

def plain(el):
    return re.sub(r"\s+", " ", el.get_text(" ", strip=True))

# ───────────────────────── Páginas de documento ─────────────────────────
def render_doc(route, meta, content):
    r = rel(route)
    inner, toc, words, root = process(route, content)
    sec = ROUTE_SECTION.get(route)
    seq = [x for g in sec["groups"] for x in g[1]] if sec else []
    side = ""
    if sec:
        items = ""
        for gname, glist in sec["groups"]:
            items += f'<div class="grp"><ul>' + "".join(
                f'<li><a href="{r}{url(rt)}"{" aria-current=\"page\"" if rt == route else ""}>{H.escape(lb)}</a></li>' for rt, lb in glist) + "</ul></div>"
        side = f'<h2>{sec["groups"][0][0]}</h2>{items}'
    else:
        side = ""
    crumbs = f'<a href="{r or "./"}">Inicio</a>'
    if sec:
        crumbs += f'<i>/</i><a href="{r}{url(sec["home"])}">{sec["label"]}</a>'
    crumbs += f'<i>/</i><span>{H.escape(ROUTE_LABEL.get(route, meta["title"]))}</span>'
    mins = max(1, round(words / 220))
    chip = f'<span class="chip">{ICON["clock"].replace("<svg", "<svg")} {mins} min de lectura</span>'
    toc_html = ""
    if len(toc) >= 2:
        toc_html = '<nav class="toc" aria-label="En esta página"><h2>En esta página</h2><ul>' + "".join(
            f'<li><a class="{"l3" if lv == "h3" else ""}" href="#{i}">{H.escape(t)}</a></li>' for lv, i, t in toc) + "</ul></nav>"
    pager = ""
    ids = [rt for rt, _ in seq]
    if route in ids:
        k = ids.index(route)
        if k > 0: pager += f'<a class="prev" href="{r}{url(ids[k-1])}"><small>Anterior</small><span>{H.escape(seq[k-1][1])}</span></a>'
        if k < len(ids) - 1: pager += f'<a class="next" href="{r}{url(ids[k+1])}"><small>Siguiente</small><span>{H.escape(seq[k+1][1])}</span></a>'
        pager = f'<div class="pager">{pager}</div>'
    out = head(meta["title"], meta["description"] or "Documentación de ARVI", r, route)
    out += header(r, sec["id"] if sec else "")
    out += '<div class="scrim"></div>'
    out += f'''<div class="shell">
<aside class="side" aria-label="Capítulos">{side}</aside>
<main id="contenido">
<div class="crumbs">{crumbs}</div>
<h1 class="page-h">{H.escape(meta["title"])}</h1>
<div class="page-meta">{chip}</div>
<article class="prose">{inner}</article>
{pager}
</main>
{toc_html}
</div>
'''
    out += footer(r) + "</body></html>\n"
    return out, root

# ───────────────────────── Portada ─────────────────────────
STEPS = [
    ("Hablas", "Grabas desde la interfaz: ventana de escritorio, PWA instalable o el móvil por red privada. El audio viaja solo hasta tu propio ordenador.",
     ["PWA", "Tauri", "Móvil"], "memoria-academica/15-movil/", 15),
    ("Se transcribe", "VoiceStudio convierte tu voz en texto en local con faster-whisper. Si no responde, ARVI usa OpenAI como respaldo y te lo avisa.",
     ["VoiceStudio", "faster-whisper-base", "gpt-transcribe"], "memoria-academica/10-voz/", 10),
    ("Piensa", "El agente razona con el modelo de OpenAI y consulta tu memoria en Obsidian: notas, proyectos y preferencias que ya conoce.",
     ["Agente", "OpenAI", "Obsidian · FTS5"], "memoria-academica/11-memoria/", 11),
    ("Pide permiso", "Cada herramienta tiene un nivel de permiso de los cuatro posibles. Las acciones sensibles esperan tu aprobación y quedan registradas.",
     ["4 niveles", "Confirmación", "Auditoría"], "memoria-academica/13-herramientas-permisos/", 13),
    ("Actúa", "Ejecuta herramientas locales y automatizaciones: flujos de n8n, consultas a GitHub, luces con Home Assistant u otros ordenadores con ARVI Remote.",
     ["n8n", "GitHub", "Home Assistant", "ARVI Remote"], "memoria-academica/12-n8n/", 12),
    ("Responde", "Contesta con voz. OmniVoice la genera en local y, si falla, entra la voz de OpenAI con un aviso de que es una voz de IA.",
     ["OmniVoice", "gpt-4o-mini-tts", "Aviso de voz IA"], "memoria-academica/10-voz/", 10),
]
PILLARS = [
    ("mic", "Voz local, con respaldo", "Reconocimiento y síntesis en tu ordenador con VoiceStudio. Si falla, la nube toma el relevo sin que pierdas la conversación.", "memoria-academica/10-voz/", "w3"),
    ("memory", "Memoria que no se olvida", "Una bóveda de Obsidian con búsqueda de texto completo. Tu memoria y tu voz se quedan en este PC.", "memoria-academica/11-memoria/", "w3"),
    ("shield", "Cuatro niveles de permisos", "El servidor decide qué puede hacer cada herramienta. Lo delicado exige tu confirmación.", "memoria-academica/13-herramientas-permisos/", ""),
    ("flow", "Automatizaciones con n8n", "Flujos externos que ARVI lanza por ti: el tiempo, avisos, tareas repetitivas.", "memoria-academica/12-n8n/", ""),
    ("home", "Hogar inteligente", "Luces y dispositivos a través de Home Assistant, con las mismas reglas de permisos.", "memoria-academica/24-domotica/", ""),
    ("monitor", "Varios ordenadores", "ARVI Remote te deja dar órdenes a otros equipos de tu red desde una sola esfera.", "memoria-academica/25-control-remoto/", ""),
    ("shield", "Seguridad por defecto", "El servidor solo escucha en este equipo salvo que lo permitas, y las pruebas OWASP automáticas vigilan cada ruta.", "memoria-academica/17-seguridad/", "w3"),
    ("mic", "«Mi voz»", "ARVI puede aprender a hablar con tu voz, siempre después de que des tu consentimiento.", "memoria-academica/26-aprendizaje-voz/", "w3"),
]
GALLERY = [
    ("Panel principal", "La esfera, las métricas y los permisos a la vista.", "capturas/fase-13/2026-11-12_interfaz-cristal-escritorio.png", 0, "Panel principal de ARVI con tema de cristal, esfera en espera y resumen de estado."),
    ("En el móvil", "La misma interfaz, adaptada a pantalla estrecha.", "capturas/fase-13/2026-11-12_interfaz-cristal-movil.png", 1, "Interfaz de ARVI en el móvil."),
    ("Permisos", "ARVI espera tu aprobación antes de una acción sensible.", "capturas/fase-4/2026-11-12_permiso-pendiente.png", 0, "Una acción pendiente de aprobación en ARVI."),
    ("Memoria", "Las notas de Obsidian que ARVI consulta y escribe.", "capturas/fase-4/2026-11-12_panel-memoria.png", 0, "Panel de memoria de ARVI con notas de Obsidian."),
    ("Mi casa", "Dispositivos del hogar (simulados en las pruebas).", "capturas/fase-11/2026-11-12_mi-casa-escritorio.png", 0, "Pantalla Mi casa con luces y dispositivos."),
    ("Ordenadores", "Los equipos conectados con ARVI Remote.", "capturas/fase-11/2026-11-12_mis-ordenadores.png", 0, "Pantalla de ordenadores conectados."),
    ("Mi voz", "El consentimiento previo para aprender tu voz.", "capturas/fase-12/2026-11-12_mi-voz-consentimiento.png", 0, "Pantalla Mi voz con el consentimiento para el aprendizaje de la voz."),
]

def render_home():
    r = ""
    out = head("ARVI", "ARVI es un asistente personal de IA por voz que se ejecuta en tu ordenador: voz local, memoria en Obsidian, automatizaciones con n8n y permisos de cuatro niveles.", r, "", "home")
    out += header(r, "")
    steps_json = json.dumps([{"t": s[0], "d": s[1], "tags": s[2], "u": s[3], "n": s[4]} for s in STEPS], ensure_ascii=False)
    step_btns = "".join(
        f'<li><button type="button" role="tab" aria-selected="false"><i>{k+1}</i>{s[0]}</button></li>' for k, s in enumerate(STEPS))
    cards = "".join(
        f'<a class="card {w} rv" href="{u}"><span class="ic">{ICON[ic]}</span><h3>{t}</h3><p>{d}</p><span class="go">Leer el capítulo {ICON["arrow"]}</span></a>'
        for ic, t, d, u, w in PILLARS)
    tabs = "".join(
        f'<button type="button" role="tab" aria-selected="false" data-cap="{H.escape(c, quote=True)}"><b>{t}</b><small>{d}</small></button>' for t, d, _, _, c in GALLERY)
    imgs = "".join(
        f'<img alt="{H.escape(c, quote=True)}" {"src" if k == 0 else "data-src"}="{p}" data-phone="{ph}" width="{412 if ph else 1440}" height="{915 if ph else 900}" decoding="async">'
        for k, (t, d, p, ph, c) in enumerate(GALLERY))
    out += f'''<main id="contenido">
<section class="hero"><div class="wrap hero-grid">
  <div>
    <h1>Un asistente de voz que vive en tu ordenador</h1>
    <p class="lead">ARVI escucha, recuerda lo que le importa a tu trabajo y actúa sobre tu equipo, pero solo con los permisos que tú le das. Esta es su documentación completa: desde la idea hasta las pruebas.</p>
    <div class="cta">
      <a class="btn main" href="memoria-academica/">Leer la memoria {ICON["arrow"]}</a>
      <a class="btn" href="DIARIO_DESARROLLO/">Ver el diario de desarrollo</a>
    </div>
    <p class="note-hero">Versión de entrega · 12 de noviembre de 2026. Lo que aún depende del alumno aparece marcado como <mark class="pend" style="background:rgba(251,191,36,.14);color:var(--warn);border:1px solid rgba(251,191,36,.3);border-radius:.4rem;padding:.05em .4em;font:600 .82em var(--font-m)">PENDIENTE</mark> en la memoria.</p>
  </div>
  <div class="stage">
    <div class="orb-wrap" role="button" tabindex="0" aria-label="Esfera de ARVI. Pulsa para cambiar de estado"><canvas id="orb" aria-hidden="true"></canvas></div>
    <div class="say" aria-live="polite"><div class="say-state" id="say-state">En espera</div><p class="say-line" id="say-line"></p></div>
    <div class="states" role="group" aria-label="Estado de la esfera">
      <button type="button" data-s="idle" aria-pressed="true">En espera</button><button type="button" data-s="listening" aria-pressed="false">Escuchando</button><button type="button" data-s="thinking" aria-pressed="false">Pensando</button><button type="button" data-s="speaking" aria-pressed="false">Hablando</button>
    </div>
    <p class="demo-tag">Demostración con los cuatro estados de la interfaz real</p>
  </div>
</div></section>

<div class="wrap"><div class="stats rv">
  <div class="stat"><b data-count="26">26</b><span>capítulos y un anexo en la memoria académica</span></div>
  <div class="stat"><b data-count="4">4</b><span>niveles de permisos aplicados en el servidor</span></div>
  <div class="stat"><b data-count="40" data-suf="+">40+</b><span>pruebas registradas, automáticas y reales</span></div>
  <div class="stat"><b data-count="2">2</b><span>motores de voz: uno local y otro de respaldo</span></div>
</div></div>

<section class="sec"><div class="wrap">
  <div class="sec-h"><h2>Qué pasa cuando le hablas</h2><p>Seis pasos entre tu voz y su respuesta. Pulsa uno para ver qué hace y dónde está explicado.</p></div>
  <div class="flow">
    <ol class="steps" role="tablist" aria-label="Pasos de una orden">{step_btns}</ol>
    <div class="step-card" id="step-card" data-root="{r}"></div>
  </div>
  <script type="application/json" id="steps-data">{steps_json}</script>
</div></section>

<section class="sec"><div class="wrap">
  <div class="sec-h"><h2>Lo que hace posible</h2><p>Cada pieza tiene su capítulo, con el diseño, el código y las pruebas que lo respaldan.</p></div>
  <div class="bento">{cards}</div>
</div></section>

<section class="sec"><div class="wrap">
  <div class="sec-h"><h2>La interfaz, tal como es</h2><p>Capturas reales de la aplicación, tomadas durante el desarrollo.</p></div>
  <div class="gal">
    <div class="gal-tabs" role="tablist" aria-label="Pantallas">{tabs}</div>
    <div><div class="frame"><div class="frame-bar"><span></span><span></span><span></span></div>{imgs}</div><p class="cap"></p></div>
  </div>
</div></section>

<div class="wrap"><div class="band">
  <a class="card rv" href="memoria-academica/"><span class="ic">{ICON["memory"]}</span><h3>Memoria académica</h3><p>Los capítulos del proyecto, de la introducción a las conclusiones.</p><span class="go">Abrir {ICON["arrow"]}</span></a>
  <a class="card rv" href="pruebas/registro-pruebas/"><span class="ic">{ICON["shield"]}</span><h3>Pruebas e incidencias</h3><p>Qué se probó, cómo salió y qué hubo que arreglar.</p><span class="go">Abrir {ICON["arrow"]}</span></a>
  <a class="card rv" href="memoria-academica/05-diseno/"><span class="ic">{ICON["flow"]}</span><h3>Arquitectura</h3><p>Diagramas de componentes, de secuencia y de datos.</p><span class="go">Abrir {ICON["arrow"]}</span></a>
</div></div>
<div style="height:clamp(56px,8vw,110px)"></div>
</main>
'''
    out += footer(r).replace('<script src="assets/js/app.js" defer></script>', '<script src="assets/js/orb.js" defer></script><script src="assets/js/app.js" defer></script><script src="assets/js/home.js" defer></script>')
    out += "</body></html>\n"
    return out

def render_404():
    r = "/ARVI-Assistant/"  # GitHub Pages sirve el 404 desde cualquier ruta
    out = head("Página no encontrada", "Esta página no existe.", r, "404")
    out = out.replace('data-root="/ARVI-Assistant/"', 'data-root="/ARVI-Assistant/"')
    out += header(r, "")
    out += f'''<main id="contenido" class="nf"><div>
<div class="orb-wrap"><canvas id="orb" aria-hidden="true"></canvas></div>
<h1>Esta página no existe</h1><p>Puede que el enlace haya cambiado. Busca lo que necesitas o vuelve al inicio.</p>
<div class="cta" style="justify-content:center"><button class="btn main" type="button" data-search>Buscar en la documentación</button><a class="btn" href="{r}">Ir al inicio</a></div>
</div></main>
<script src="{r}assets/js/orb.js"></script><script>addEventListener('DOMContentLoaded',function(){{var o=ARVIOrb(document.getElementById('orb'),{{state:'thinking'}})}})</script>
'''
    out += footer(r) + "</body></html>\n"
    return out

# ───────────────────────── Construcción ─────────────────────────
def main():
    # estáticos
    dst = ROOT / "assets"
    if dst.exists(): shutil.rmtree(dst)
    shutil.copytree(SRC / "static", dst)
    search = []
    sitemap = []
    for route, meta in PAGES.items():
        if route == "": continue
        f = SRC / "content" / route / "index.html"
        content = f.read_text(encoding="utf-8")
        page, root = render_doc(route, meta, content)
        out = ROOT / route / "index.html"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(page, encoding="utf-8")
        sitemap.append(url(route))
        # índice de búsqueda: una entrada por página y una por sección
        label = ROUTE_LABEL.get(route, meta["title"])
        search.append({"t": label, "h": "", "u": url(route), "x": plain(root)[:300], "s": meta["description"][:140], "p": 1})
        cur = None; buf = []
        def flush():
            if cur and buf:
                search.append({"t": label, "h": cur[1], "u": url(route) + "#" + cur[0], "x": " ".join(buf)[:700]})
        for el in root.find_all(["h2", "h3", "p", "li", "td"]):
            if el.name in ("h2", "h3"):
                flush(); buf = []
                cur = (el.get("id"), plain(el).lstrip("# ").strip()) if el.get("id") else None
            elif cur:
                buf.append(plain(el))
        flush()
    (ROOT / "index.html").write_text(render_home(), encoding="utf-8")
    (ROOT / "404.html").write_text(render_404(), encoding="utf-8")
    (ROOT / "search-index.json").write_text(json.dumps(search, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    sm = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + "".join(
        f"<url><loc>{SITE_URL}{u}</loc></url>\n" for u in [""] + sorted(sitemap)) + "</urlset>\n"
    (ROOT / "sitemap.xml").write_text(sm, encoding="utf-8")
    gz = ROOT / "sitemap.xml.gz"
    if gz.exists(): gz.unlink()
    print(f"{len(PAGES) - 1} páginas + portada + 404; índice de búsqueda: {len(search)} entradas")

if __name__ == "__main__":
    main()
