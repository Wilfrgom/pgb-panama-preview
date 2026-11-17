#!/usr/bin/env python3
"""Generates every page of the PGB replica with a shared header and footer.

Run from anywhere:  python3 pgb-replica/build/build.py
Edit page content here (static pages) or in courses.json (course pages).
"""
import html
import json
import re
from urllib.parse import quote
from pathlib import Path

BUILD = Path(__file__).resolve().parent
ROOT = BUILD.parent
WA = "https://wa.link/46inih"
COURSES = json.loads((BUILD / "courses.json").read_text())
BY_SLUG = {c["slug"]: c for c in COURSES}
IATA_ORDER = [  # order used on the original "Cursos IATA" list
    "curso-cadena-de-suministro", "curso-seguridad-basica-lado-aire",
    "curso-seguridad-operacional-aviacion", "curso-operaciones-en-tierra-ahm",
    "curso-seguridad-de-la-carga", "curso-introduccion-a-la-carga",
    "curso-gestion-de-calidad-qms", "curso-sms-operaciones-en-tierra",
    "curso-servicios-de-rampa-igom", "curso-atencion-al-pasajero",
    "curso-respuesta-a-emergencias",
]
FIRST_AID = ["curso-primeros-auxilios-rcp-dea", "curso-brigada-de-emergencias"]

esc = html.escape


def meta_value(course, key):
    for k, v in course["meta"] + course["info"]:
        if k == key:
            return v
    return ""


# ---------------------------------------------------------------- partials
def nav_html(active):
    def top(href, label, key, sub=""):
        cls = ' class="active"' if key == active else ""
        li_cls = ' class="has-sub"' if sub else ""
        return f'<li{li_cls}><a href="{href}"{cls}>{label}</a>{sub}</li>'

    iata = "".join(
        f'<li><a href="{s}.html">{esc(short_title(BY_SLUG[s]))}</a></li>'
        for s in sorted(IATA_ORDER, key=lambda s: short_title(BY_SLUG[s]))
    )
    training = (
        '<ul class="sub">'
        f'<li class="has-sub"><a href="cursos-iata.html">Cursos IATA</a><ul class="sub">{iata}</ul></li>'
        '<li class="has-sub"><a href="cursos-pgb.html">Cursos PGB</a><ul class="sub">'
        '<li><a href="curso-montacargas.html">Curso de montacargas</a></li>'
        '<li class="has-sub"><a href="primeros-auxilios.html">Cursos – Primeros Auxilios</a><ul class="sub">'
        '<li><a href="curso-brigada-de-emergencias.html">Brigada de Emergencias</a></li>'
        '<li><a href="curso-primeros-auxilios-rcp-dea.html">Primeros Auxilios Básicos con RCP y DEA</a></li>'
        "</ul></li>"
        "</ul></li>"
        "</ul>"
    )
    return (
        "<ul>"
        + top("index.html", "Inicio", "inicio")
        + top("nosotros.html", "Nosotros", "nosotros",
              '<ul class="sub"><li><a href="instalaciones.html">Instalaciones</a></li></ul>')
        + top("servicios.html", "Servicios", "servicios")
        + top("centro-de-entrenamiento.html", "Centro de Entrenamiento", "entrenamiento", training)
        + top("contacto.html", "Contacto", "contacto")
        + "</ul>"
    )


def short_title(c):
    return re.sub(r"^Curso de ", "", c["title"])


ICONS = {
    "ig": '<svg viewBox="0 0 24 24"><rect x="3" y="3" width="18" height="18" rx="5" fill="none" stroke="currentColor" stroke-width="2"/><circle cx="12" cy="12" r="4" fill="none" stroke="currentColor" stroke-width="2"/><circle cx="17.5" cy="6.5" r="1.2" fill="currentColor"/></svg>',
    "fb": '<svg viewBox="0 0 24 24"><path fill="currentColor" d="M14 8h3V4h-3c-2.8 0-4 1.7-4 4.2V10H7v4h3v8h4v-8h3l1-4h-4V8.5c0-.3.2-.5.5-.5Z"/></svg>',
    "wa": '<svg viewBox="0 0 24 24"><path fill="currentColor" d="M12 2a10 10 0 0 0-8.6 15.1L2 22l5-1.3A10 10 0 1 0 12 2Zm0 18a8 8 0 0 1-4.1-1.1l-.3-.2-3 .8.8-2.9-.2-.3A8 8 0 1 1 12 20Zm4.4-6c-.2-.1-1.4-.7-1.7-.8-.2-.1-.4-.1-.5.1l-.8 1c-.1.2-.3.2-.5.1a6.6 6.6 0 0 1-3.3-2.9c-.2-.4.2-.4.7-1.3.1-.2 0-.3 0-.4l-.8-1.8c-.2-.5-.4-.4-.5-.4h-.5a1 1 0 0 0-.7.3 3 3 0 0 0-.9 2.2c0 1.3.9 2.5 1 2.7.1.2 1.8 2.8 4.4 3.9 1.6.7 2.3.8 3.1.6.5-.1 1.4-.6 1.6-1.1.2-.6.2-1 .1-1.1l-.5-.1Z"/></svg>',
    "map": '<svg viewBox="0 0 24 24"><path fill="currentColor" d="M12 2a7 7 0 0 0-7 7c0 5.2 7 13 7 13s7-7.8 7-13a7 7 0 0 0-7-7Zm0 9.5A2.5 2.5 0 1 1 12 6.5a2.5 2.5 0 0 1 0 5Z"/></svg>',
    "arrow": '<svg viewBox="0 0 24 24" width="18" height="18"><path d="M5 12h14m-6-6 6 6-6 6" fill="none" stroke="currentColor" stroke-width="1.8"/></svg>',
    "check": '<svg viewBox="0 0 24 24" width="18" height="18"><path d="m5 12 4.5 4.5L19 7" fill="none" stroke="currentColor" stroke-width="2.2"/></svg>',
    "pin": '<svg viewBox="0 0 24 24" width="20" height="20"><path fill="currentColor" d="M12 2a7 7 0 0 0-7 7c0 5.2 7 13 7 13s7-7.8 7-13a7 7 0 0 0-7-7Zm0 9.5A2.5 2.5 0 1 1 12 6.5a2.5 2.5 0 0 1 0 5Z"/></svg>',
    "phone": '<svg viewBox="0 0 24 24" width="20" height="20"><path fill="currentColor" d="M6.6 10.8a15.1 15.1 0 0 0 6.6 6.6l2.2-2.2c.3-.3.7-.4 1-.2 1.1.4 2.3.6 3.6.6.6 0 1 .4 1 1V20c0 .6-.4 1-1 1A17 17 0 0 1 3 4c0-.6.4-1 1-1h3.5c.6 0 1 .4 1 1 0 1.3.2 2.5.6 3.6.1.3 0 .7-.2 1Z"/></svg>',
    "mail": '<svg viewBox="0 0 24 24" width="20" height="20"><path fill="currentColor" d="M20 4H4a2 2 0 0 0-2 2v12a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2V6a2 2 0 0 0-2-2Zm0 4-8 5-8-5V6l8 5 8-5Z"/></svg>',
}


SOCIAL = {
    "ig": ("Instagram", "https://www.instagram.com/pgb_latam/"),
    "fb": ("Facebook", "https://www.facebook.com/p/Premium-Ground-Business-Cargo-61575569991376/"),
    "wa": ("Whatsapp", WA),
    "map": ("Ubicación en Google Maps", "https://maps.app.goo.gl/i47zJh3EpSM7D1Xx8"),
}


def socials():
    return (
        '<div class="socials">'
        + "".join(
            f'<a href="{url}" target="_blank" rel="noopener" aria-label="{label}">{ICONS[key]}</a>'
            for key, (label, url) in SOCIAL.items()
        )
        + "</div>"
    )


SITE_URL = "https://www.pgbpanama.com"   # used for absolute Open Graph URLs
# Preview deployments must not be indexed (they would compete with pgbpanama.com).
# Set to False when this goes live on the real domain.
PREVIEW = True


def layout(title, body, active, solid=True, description="Servicio Logístico y Manejo de Carga", extra_head=""):
    full_title = "PGB – Premium Ground Business – Servicio Logístico y Manejo de Carga" if title is None \
        else f"{title} – PGB – Premium Ground Business"
    header_cls = "header header--solid" if solid else "header"
    return f"""<!DOCTYPE html>
<html lang="es" class="no-js">
<head>
<meta charset="UTF-8">
<script>document.documentElement.className = "js";</script>
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(full_title)}</title>
<meta name="description" content="{esc(description)}">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;700&family=Inter+Tight:wght@400;500;600;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="https://use.typekit.net/krv6wwr.css">
<link rel="stylesheet" href="styles.css">
<link rel="icon" href="assets/favicon.svg" type="image/svg+xml">
<link rel="icon" href="assets/favicon-32.png" sizes="32x32" type="image/png">
<link rel="apple-touch-icon" href="assets/apple-touch-icon.png">
<meta name="theme-color" content="#091836">
{'<meta name="robots" content="noindex, nofollow">' if PREVIEW else ""}
<meta property="og:type" content="website">
<meta property="og:site_name" content="PGB – Premium Ground Business">
<meta property="og:title" content="{esc(full_title)}">
<meta property="og:description" content="{esc(description)}">
<meta property="og:image" content="{SITE_URL}/assets/og-image.jpg">
<meta name="twitter:card" content="summary_large_image">
{extra_head}
</head>
<body>
<!-- Generated by build/build.py — edit there, not here. -->

<header class="{header_cls}" id="header">
  <div class="header__inner">
    <a href="index.html" class="logo"><img src="assets/LOGO-EDIABLTE-HORIZONTAL-PRINCIPAL.png" alt="PGB – Premium Ground Business"></a>
    <nav class="nav" id="nav">{nav_html(active)}</nav>
    <button class="panel-btn" id="panelBtn" aria-label="Abrir menú" aria-expanded="false" aria-controls="panel">
      <span class="panel-btn__burger" aria-hidden="true"><i></i><i></i><i></i></span><span class="panel-btn__label">Menú</span>
      <svg class="panel-btn__grid" aria-hidden="true" viewBox="0 0 16 16" width="16" height="16" fill="currentColor"><circle cx="2" cy="2" r="1.6"/><circle cx="8" cy="2" r="1.6"/><circle cx="14" cy="2" r="1.6"/><circle cx="2" cy="8" r="1.6"/><circle cx="8" cy="8" r="1.6"/><circle cx="14" cy="8" r="1.6"/><circle cx="2" cy="14" r="1.6"/><circle cx="8" cy="14" r="1.6"/><circle cx="14" cy="14" r="1.6"/></svg>
    </button>
  </div>
</header>

<aside class="panel" id="panel" role="dialog" aria-modal="true" aria-label="Menú" aria-hidden="true">
  <button class="panel__close" id="panelClose" aria-label="Cerrar menú">&times;</button>
  <img src="assets/LOGO-EDIABLTE-HORIZONTAL-PRINCIPAL.png" alt="PGB" class="panel__logo">
  <nav class="panel__nav">
    <a href="index.html">Inicio</a><a href="nosotros.html">Nosotros</a><a href="instalaciones.html" class="panel__sub">Instalaciones</a><a href="servicios.html">Servicios</a><a href="centro-de-entrenamiento.html">Centro de Entrenamiento</a><a href="cursos-iata.html" class="panel__sub">Cursos IATA</a><a href="cursos-pgb.html" class="panel__sub">Cursos PGB</a><a href="contacto.html">Contacto</a>
  </nav>
  <div class="panel__info">
    <h6>Contacto</h6>
    <a href="mailto:info@pgbpanama.com">info@pgbpanama.com</a>
    <a href="{WA}">Whatsapp: 507 6462-6739</a>
  </div>
</aside>
<div class="overlay" id="overlay"></div>

<main>
{body}
</main>

<footer class="footer sticky-footer" id="contacto">
  <div class="sticky-footer__fixed">
    <div class="sticky-footer__inner">
      <div class="sticky-footer__glow" aria-hidden="true"><span></span><span></span><span></span></div>
  <div class="container footer__grid">
    <h2 class="footer__tag fade-blur">Moviendo el Mundo<br>Juntos.</h2>
    <div class="fade-blur" style="--d:.1s">
      <h6>Dirección</h6>
      <p>Av. Domingo Díaz, Edificio Global Business Terminal, Piso 5, Oficina 1.</p>
      {socials()}
    </div>
    <nav class="footer__links fade-blur" style="--d:.2s" aria-label="Enlaces del sitio">
      <h6>Enlaces</h6>
      <ul>
        <li><a href="index.html">Inicio</a></li>
        <li><a href="nosotros.html">Nosotros</a></li>
        <li><a href="instalaciones.html">Instalaciones</a></li>
        <li><a href="servicios.html">Servicios</a></li>
        <li><a href="cursos-iata.html">Cursos IATA</a></li>
        <li><a href="cursos-pgb.html">Cursos PGB</a></li>
        <li><a href="contacto.html">Contacto</a></li>
      </ul>
    </nav>
    <div class="footer__contact fade-blur" style="--d:.3s">
      <h6>Contacto</h6>
      <p><span>Servicios:</span> <a href="mailto:info@pgbpanama.com">info@pgbpanama.com</a></p>
      <p><span>Centro de entrenamiento:</span> <a href="mailto:certificaciones@pgbpanama.com">certificaciones@pgbpanama.com</a></p>
      <p><span>Recursos humanos:</span> <a href="mailto:recursoshumanos@pgbpanama.com">recursoshumanos@pgbpanama.com</a></p>
      <p class="mt"><a href="{WA}">Whatsapp: 507 6462-6739</a></p>
      <p class="phone"><a href="tel:+5073756602">+ 507 375-6602 / 375-6601</a></p>
    </div>
  </div>
  <div class="container footer__bottom">
    <a href="contacto.html">Contacto</a>
    <span><a href="index.html">www.pgbpanama.com</a> © 2026. Todos los derechos reservados.</span>
  </div>
    </div>
  </div>
</footer>

<a class="wa-float" href="{WA}" aria-label="WhatsApp">
  {ICONS["wa"].replace("<svg", '<svg width="26" height="26" style="color:#fff"')}
</a>

<script src="main.js"></script>
</body>
</html>
"""


# ---------------------------------------------------------------- helpers
def course_row(c):
    hours = meta_value(c, "Duración")
    mode = meta_value(c, "Modalidad")
    return (
        f'<a class="course-row reveal" href="{c["slug"]}.html">'
        f'<h6>{esc(short_title(c) if c["slug"] != "curso-cadena-de-suministro" else c["title"])}</h6>'
        f'<span>Modalidad: {esc(mode)}</span><span class="course-row__hours">{esc(hours)}</span>'
        f'<i>{ICONS["arrow"]}</i></a>'
    )


def render_lines(lines):
    """Turn parsed text lines into paragraphs, bulleted and numbered lists."""
    out, ul, ol = [], [], []

    def flush():
        if ul:
            out.append("<ul>" + "".join(f"<li>{x}</li>" for x in ul) + "</ul>")
            ul.clear()
        if ol:
            out.append("<ol>" + "".join(f"<li>{x}</li>" for x in ol) + "</ol>")
            ol.clear()

    for line in lines:
        if line.startswith("- "):
            if ol:
                flush()
            ul.append(label(line[2:]))
        elif re.match(r"^\d+\.\s", line):
            if ul:
                flush()
            ol.append(esc(re.sub(r"^\d+\.\s*", "", line)))
        else:
            flush()
            cls = ' class="lead"' if line.endswith(":") else ""
            out.append(f"<p{cls}>{label(line)}</p>")
    flush()
    return "\n".join(out)


def label(text):
    """Bold a short 'Label:' prefix, as the original pages do."""
    m = re.match(r"^([^:.]{2,60}):\s*(.+)$", text)
    if m:
        return f"<strong>{esc(m.group(1))}:</strong> {esc(m.group(2))}"
    return esc(text)


def cta_block(c):
    return (
        '<div class="enroll reveal">'
        f'<a class="btn btn--blue" href="{esc(c["enroll"])}" target="_blank" rel="noopener">Inscribirme ahora</a>'
        f'<p>Por sólo <strong>{esc(c["price"])}</strong> dólares</p>'
        "</div>"
    )


# ---------------------------------------------------------------- pages
def course_page(c):
    meta_bar = "".join(f"<div><span>{esc(k)}:</span> {esc(v)}</div>" for k, v in c["meta"])
    info = "".join(f"<li><span>{esc(k)}:</span> {esc(v)}</li>" for k, v in c["info"])
    photo = f'<img class="course-side__photo" src="assets/{c["photo"]}" alt="">' if c["photo"] else ""
    wa_btn = ""
    if c["slug"] in IATA_ORDER:
        msg = f'Hola, me interesa el curso IATA "{c["title"]}". Los contacto desde el sitio web de PGB.'
        wa_btn = (f'<a class="btn btn--wa" href="https://wa.me/50764626739?text={quote(msg)}" target="_blank" rel="noopener">'
                  + ICONS["wa"].replace("<svg", '<svg width="20" height="20"') + " Consultar por WhatsApp</a>")

    # Sections before the first CTA: content + "¿Qué aprenderás?". After: audience.
    sec_html = []
    for i, s in enumerate(c["sections"]):
        sec_html.append(
            f'<section class="course-sec reveal"><h4>{esc(s["title"])}</h4>{render_lines(s["lines"])}</section>'
        )
        if s["title"].startswith("¿Qué aprenderás") and len(c["sections"]) > i + 1:
            sec_html.append(cta_block(c))

    badge = f'<img src="assets/{c["badge"]}" alt="">' if c["badge"] else \
        '<img src="assets/002.png" alt="">'
    cert_title, *cert_body = c["cert"] or ["Certificado otorgado"]
    cert = (
        f'<div class="cert reveal">{badge}<div><h5>{esc(cert_title)}</h5>'
        + "".join(f"<p>{label(x)}</p>" for x in cert_body)
        + "</div></div>"
    )
    exam = ""
    if c["exam"]:
        exam = f'<div class="exam reveal"><h5>Información del examen</h5>{render_lines(c["exam"])}</div>'

    if c["slug"] in IATA_ORDER:
        trail = [("centro-de-entrenamiento.html", "Centro de Entrenamiento"), ("cursos-iata.html", "Cursos IATA")]
    elif c["slug"] in FIRST_AID:
        trail = [("centro-de-entrenamiento.html", "Centro de Entrenamiento"), ("cursos-pgb.html", "Cursos PGB"),
                 ("primeros-auxilios.html", "Primeros Auxilios")]
    else:
        trail = [("centro-de-entrenamiento.html", "Centro de Entrenamiento"), ("cursos-pgb.html", "Cursos PGB")]
    crumbs = "".join(f'<li><a href="{h}">{esc(t)}</a></li>' for h, t in trail)
    crumbs = f'<nav class="breadcrumbs" aria-label="Ruta de navegación"><ol>{crumbs}<li aria-current="page">{esc(short_title(c))}</li></ol></nav>'
    wa_msg = quote(f'Hola, me interesa el curso "{c["title"]}". Los contacto desde el sitio web de PGB.')
    bar = f"""<div class="course-bar" role="region" aria-label="Inscripción">
  <div class="course-bar__price"><span>Precio</span><strong>{esc(c["price"])}</strong></div>
  <a class="course-bar__wa" href="https://wa.me/50764626739?text={wa_msg}" target="_blank" rel="noopener" aria-label="Consultar por WhatsApp">{ICONS["wa"]}</a>
  <a class="btn btn--blue course-bar__btn" href="{esc(c["enroll"])}" target="_blank" rel="noopener">Inscribirme</a>
</div>"""
    schema = {
        "@context": "https://schema.org", "@type": "Course", "name": c["title"],
        "description": (c["intro"][0] if c["intro"] else c["title"]),
        "provider": {"@type": "Organization", "name": "PGB – Premium Ground Business", "sameAs": SITE_URL},
        "offers": {"@type": "Offer", "price": f'{num(c["price"]):.2f}', "priceCurrency": "USD", "category": "Paid"},
        "hasCourseInstance": {"@type": "CourseInstance",
                              "courseMode": "Online" if "learning" in meta_value(c, "Modalidad").lower() else "Onsite",
                              "inLanguage": "en" if meta_value(c, "Idioma").lower().startswith("ingl") else "es"},
    }
    extra = f'<script type="application/ld+json">{json.dumps(schema, ensure_ascii=False)}</script>'
    body = f"""
<section class="page-banner" style="background-image:url('assets/{c["hero"]}')"></section>
<div class="container">{crumbs}</div>
<section class="course-head container">
  <h1 class="reveal">{esc(c["title"])}</h1>
  <div class="course-head__intro reveal">{"".join(f"<p>{esc(p)}</p>" for p in c["intro"])}</div>
</section>
<div class="meta-bar"><div class="container meta-bar__inner">{meta_bar}</div></div>
<section class="course container">
  <aside class="course-side">
    <div class="course-side__sticky">
      <h3>Información sobre el curso</h3>
      <ul>{info}</ul>
      {wa_btn}
      {photo}
    </div>
  </aside>
  <div class="course-main">
    {"".join(sec_html)}
    {cert}
    {exam}
    <a class="btn btn--outline reveal" href="{WA}" target="_blank" rel="noopener">{ICONS["wa"].replace("<svg", '<svg width="18" height="18"')} Más información</a>
    {cta_block(c)}
  </div>
</section>
{bar}
"""
    return layout(c["title"], body, "entrenamiento", description=c["intro"][0][:155] if c["intro"] else "",
                  extra_head=extra).replace("<body>", '<body class="has-course-bar">', 1)


def num(text):
    m = re.search(r"[\d]+(?:[.,]\d+)?", text or "")
    return float(m.group(0).replace(",", ".")) if m else 0


def hours_value(c):
    d = meta_value(c, "Duración").lower()
    n = num(d)
    return n / 60 if "minut" in d else n


def course_card(c, *, shape, category, logo=None, logo_alt=None):
    """Product-style card: flyer-like image on top, grey info panel below."""
    mode = meta_value(c, "Modalidad")
    hours = meta_value(c, "Duración")
    title = c["title"]
    return f"""<a class="course-card course-card--{shape} reveal" href="{c["slug"]}.html"
   data-price="{num(c["price"])}" data-hours="{hours_value(c)}" data-title="{esc(title)}">
  <div class="course-card__media" style="background-image:url('assets/{c["hero"]}')">
    <span class="eyebrow">{esc(mode)} · {esc(hours)}</span>
    <h3 class="course-card__flyer">{esc(title)}</h3>
  </div>
  <div class="course-card__info">
    <span class="course-card__cat">{category}</span>
    <ul class="course-card__facts">
      <li>Idioma: {esc(meta_value(c, "Idioma") or "Español")}</li>
      <li>Examen supervisado: {esc(meta_value(c, "Examen supervisado") or "—")}</li>
    </ul>
    <span class="course-card__price">{esc(c["price"])} <small>USD</small></span>
  </div>
</a>"""


def course_grid(cards, *, cols, label):
    n = len(cards)
    return f"""<section class="container shop">
  <div class="shop__bar">
    <p>Mostrando {"el único resultado" if n == 1 else f"los {n} resultados"}</p>
    <label class="shop__sort">
      <span class="sr-only">Ordenar {label}</span>
      <select data-sort>
        <option value="default">Orden predeterminado</option>
        <option value="price-asc">Precio: menor a mayor</option>
        <option value="price-desc">Precio: mayor a menor</option>
        <option value="hours-asc">Duración: más corta</option>
        <option value="title">Nombre (A–Z)</option>
      </select>
    </label>
  </div>
  <div class="shop__grid shop__grid--{cols}">{"".join(cards)}</div>
</section>"""


def training_hub_page():
    iata_n, pgb_n = len(IATA_ORDER), 1 + len(FIRST_AID)
    body = f"""
<section class="section container narrow-head">
  <p class="eyebrow reveal">Centro de Entrenamiento</p>
  <h1 class="reveal">Formación certificada para el sector logístico y aeroportuario</h1>
  <p class="reveal">Elige el programa que necesitas: cursos avalados por IATA en modalidad e-learning, o los cursos presenciales de PGB en montacargas y primeros auxilios.</p>
</section>
<section class="container other-courses other-courses--hub">
  <a class="promo promo--tall reveal" href="cursos-iata.html" style="background-image:url('assets/1Mesa-de-trabajo-1Servicios-de-Rampa-Aeroportuaria-1-scaled.webp')"><span class="eyebrow">{iata_n} cursos · E-learning</span><h3>Cursos IATA</h3></a>
  <a class="promo promo--tall reveal" href="cursos-pgb.html" style="background-image:url('assets/1Mesa-de-trabajo-1sms.webp')"><span class="eyebrow">{pgb_n} cursos · Presencial · NSC / ACES / AIDER</span><h3>Cursos PGB</h3></a>
</section>
"""
    return layout("Centro de Entrenamiento", body, "entrenamiento")


def back_link(href, label):
    return f'<a class="back-link reveal" href="{href}"><span>←</span> {label}</a>'


def iata_page():
    body = f"""
<section class="section container narrow-head">
  {back_link("centro-de-entrenamiento.html", "Centro de Entrenamiento")}
  <p class="eyebrow reveal">Cursos IATA</p>
  <h1 class="reveal">Capacitación certificada IATA</h1>
  <p class="reveal">A través de nuestro Centro de Entrenamiento, ofrecemos cursos avalados por IATA que permiten a las organizaciones capacitar a su personal bajo estándares internacionales. Una herramienta clave para reducir riesgos operativos, mejorar la eficiencia y garantizar el cumplimiento regulatorio.</p>
</section>
{course_grid([course_card(BY_SLUG[k], shape="square", category="Cursos IATA, E-learning", logo="Mesa-de-trabajo-3-copia-5-8-1.png", logo_alt="IATA") for k in IATA_ORDER], cols=3, label="cursos IATA")}
<section class="section container cta-line reveal">
  <p>¿Buscas cursos presenciales de montacargas o primeros auxilios?</p>
  <a class="btn btn--navy" href="cursos-pgb.html">Ver Cursos PGB</a>
</section>
"""
    return layout("Cursos IATA", body, "entrenamiento")


def pgb_page():
    body = f"""
<section class="page-banner page-banner--short" style="background-image:url('assets/1Mesa-de-trabajo-1montacargas.webp')"></section>
<section class="section container narrow-head">
  {back_link("centro-de-entrenamiento.html", "Centro de Entrenamiento")}
  <p class="eyebrow reveal">Cursos PGB</p>
  <h1 class="reveal">Cursos presenciales con práctica real</h1>
  <p class="reveal">Formación teórico-práctica en nuestras instalaciones, con evaluación y certificación avalada por organismos internacionales.</p>
</section>

{course_grid(
    [course_card(BY_SLUG["curso-montacargas"], shape="wide", category="Cursos PGB, Montacargas · NSC", logo="Mesa-de-trabajo-3-8.png", logo_alt="NSC")]
    + [course_card(BY_SLUG[k], shape="wide", category="Cursos PGB, Primeros Auxilios · ACES / AIDER", logo="002.png", logo_alt="AIDER") for k in FIRST_AID],
    cols=3, label="cursos PGB")}

<section class="section container cta-line reveal">
  <p>Si estás interesado en otros cursos adicionales.</p>
  <a class="btn btn--navy" href="{WA}" target="_blank" rel="noopener">Más información</a>
</section>
"""
    return layout("Cursos PGB", body, "entrenamiento")


def first_aid_page():
    body = f"""
<section class="page-banner page-banner--short" style="background-image:url('assets/31182.opt.jpg')"></section>
<section class="section container narrow-head">
  {back_link("cursos-pgb.html", "Cursos PGB")}
  <p class="eyebrow reveal">Cursos PGB</p>
  <h1 class="reveal">Cursos de Primeros Auxilios</h1>
</section>
<section class="container split split--center">
  <div class="split__media reveal">
    <img src="assets/1Mesa-de-trabajo-2-100.opt.jpg" alt="Curso de primeros auxilios">
  </div>
  <div class="split__text">
    <img class="split__logo reveal" src="assets/002.png" alt="ACES / AIDER">
    <p class="reveal">Nuestro Centro de Entrenamiento ofrece programas especializados en soporte vital básico y gestión de emergencias, respaldados por ACES Y AIDER. A través de una formación inmersiva y práctica, capacitamos a organizaciones e individuos para identificar riesgos, intervenir eficazmente y salvar vidas, elevando los estándares de seguridad y salud ocupacional de su empresa.</p>
  </div>
</section>
<div class="shop-spacer"></div>{course_grid([course_card(BY_SLUG[k], shape="wide", category="Cursos PGB, Primeros Auxilios · ACES / AIDER", logo="002.png", logo_alt="AIDER") for k in FIRST_AID], cols=2, label="cursos de primeros auxilios")}
<section class="section container cta-line reveal">
  <p>Si estás interesado en otros cursos adicionales de primeros auxilios.</p>
  <a class="btn btn--navy" href="{WA}" target="_blank" rel="noopener">Más información</a>
</section>
"""
    return layout("Cursos – Primeros Auxilios", body, "entrenamiento")


def about_page():
    body = """
<section class="container about-intro">
  <div class="about-intro__left">
    <p class="eyebrow reveal">Nosotros</p>
    <h1 class="reveal">Líderes en Soluciones Logísticas, Manpower y Manejo de Carga en Panamá</h1>
    <img class="about-intro__a reveal" src="assets/seg.ocupaccional-scaled.webp" alt="">
  </div>
  <div class="about-intro__right">
    <img class="about-intro__b reveal" src="assets/MAXH0449-1.opt.jpg" alt="">
    <p class="reveal">Premium Ground Business S.A. con 20 años de experiencia en el sector de carga en Panamá, ofrece soluciones logísticas a los diferentes requerimientos de sus clientes.</p>
    <p class="reveal">Desde 2019 PGB avanza hacia la certificación como operador logístico en aeropuertos de Panamá ante la AAC, consolidándose en un socio confiable para sus operaciones de cargas aéreas en Panamá.</p>
  </div>
</section>
<section class="section container about-mv">
  <div class="split">
    <div class="split__text">
      <p class="eyebrow reveal">Que nos mueve</p>
      <h2 class="reveal">Nuestra Misión</h2>
      <p class="reveal">Proporcionar y facilitar soluciones logísticas competitivas y personalizadas, enfocadas en las operaciones de manejo de Carga, en las bodegas de nuestros clientes con estrictos estándares de calidad y seguridad, en miras de brindar un servicio logístico eficaz tanto en las bodegas como en la rampa.</p>
      <p class="reveal">Lograr la excelencia en la logística y manejo de mercancías confiadas a nuestra empresa, así como los manejos profesionales en las aeronaves cargueras atendidas en los aeropuertos a nivel nacional; con el fin de dar respuesta a las necesidades de nuestros clientes, cumpliendo con las normas, regulaciones y leyes nacionales e internacionales, formando parte activa en la consecución de sus objetivos.</p>
    </div>
    <div class="split__media reveal"><img src="assets/MAXH0432-1.opt.jpg" alt=""></div>
  </div>
  <div class="split split--reverse split--center">
    <div class="split__text">
      <h2 class="reveal">Nuestra Visión</h2>
      <p class="reveal">Fortalecernos como uno de los principales operadores logísticos dentro de los aeropuertos del país, así como en las zonas logísticas dentro y fuera de los aeropuertos, excediendo las expectativas, aportando soluciones profesionales y personalizadas en el ámbito del manejo de carga en bodegas, atención a vuelos cargueros, el transporte y la logística en general, con clara orientación al cliente, basada en la formación, motivación, compromiso e implicación de nuestro equipo humano, enmarcados en los estándares de calidad, seguridad y adaptabilidad a nuevas normas y regulaciones nacionales e internacionales en la aviación civil.</p>
    </div>
    <div class="split__media reveal"><img src="assets/1Mesa-de-trabajo-1pgb-scaled.webp" alt=""></div>
  </div>
</section>
"""
    return layout("Nosotros", body, "nosotros")


def facilities_page():
    gallery = "".join(
        f'<button class="gallery__item reveal" data-full="assets/pgb{i}.webp"><img src="assets/pgb{i}.webp" alt="Instalaciones PGB {i}" loading="lazy"></button>'
        for i in (8, 2, 4, 1, 11, 12, 9, 5, 3, 6, 10, 7)
    )
    items = ["Capacitaciones presenciales", "Entrenamientos prácticos con equipos reales",
             "Certificaciones y evaluaciones técnicas", "Programas de inducción y formación continua"]
    body = f"""
<section class="page-banner" style="background-image:url('assets/pgb2.webp')"></section>
<section class="section container narrow-head">
  <p class="eyebrow reveal">Instalaciones</p>
  <h1 class="reveal">Infraestructura moderna al servicio de la operación</h1>
  <p class="reveal">En PGB Panamá contamos con instalaciones modernas y completamente equipadas para garantizar operaciones logísticas seguras, entrenamientos de alto nivel y una experiencia profesional tanto para clientes como para colaboradores.</p>
</section>
<section class="container split split--center">
  <div class="split__media reveal"><img src="assets/pgb11.webp" alt=""></div>
  <div class="split__text">
    <h2 class="reveal">Más que instalaciones: un entorno profesional y centro estratégico</h2>
    <p class="reveal">Uno de los pilares de nuestras instalaciones es el <strong>área de training</strong>, creada específicamente para la formación técnica y operativa de profesionales del sector.</p>
    <p class="reveal">Este espacio está acondicionado para:</p>
    <ul class="checks reveal">{"".join(f"<li>{ICONS['check']}{x}</li>" for x in items)}</ul>
    <p class="reveal">Nuestro enfoque es brindar un entorno controlado, seguro y profesional, que permita a los participantes adquirir conocimientos prácticos con altos estándares de calidad.</p>
  </div>
</section>
<section class="section container gallery">{gallery}</section>
<div class="lightbox" id="lightbox" role="dialog" aria-modal="true" aria-label="Galería de instalaciones" hidden>
  <button class="lightbox__close" aria-label="Cerrar">&times;</button>
  <button class="lightbox__nav lightbox__nav--prev" aria-label="Foto anterior">&#8249;</button>
  <img alt="">
  <button class="lightbox__nav lightbox__nav--next" aria-label="Foto siguiente">&#8250;</button>
  <p class="lightbox__count" aria-live="polite"></p>
</div>
"""
    return layout("Instalaciones", body, "nosotros")


def services_page():
    certs = ["Manejo de montacargas", "Sistemas de Gestión de Seguridad (SMS)",
             "Seguridad de la Aviación (AVSEC)", "Manejo de Mercancías Peligrosas (DG)",
             "Operaciones de rampa", "Gestión y operación de bodegas"]

    body = f"""
<section class="svc container">
  <div class="svc__aside">
    <div class="svc__sticky">
      <h1 class="reveal">Servicios que impulsan su operación logística</h1>
      <a class="link-underline reveal" href="{WA}" target="_blank" rel="noopener">Solicitar más información</a>
    </div>
  </div>
  <div class="svc__list">
    <article class="svc-item">
      <img class="reveal" src="assets/interior-large-distribution-warehouse-with-shelves-stacked-with-palettes-goods-ready-market-1024x683.jpg" alt="">
      <h2 class="reveal">Manpower.</h2>
      <p class="reveal">Ofrecemos soluciones logísticas integrales mediante la provisión de <strong>talento humano altamente capacitado</strong>, especializado en operaciones dentro de bodega, paletizaje y despaletizaje de carga, así como en la <strong>carga y descarga de aeronaves</strong>.</p>
      <p class="reveal"><strong><u>Nuestro personal cuenta con formación y certificaciones en:</u></strong></p>
      <ul class="reveal">{"".join(f"<li>{x}</li>" for x in certs)}</ul>
      <p class="reveal"><strong>Te brindamos personal completamente entrenado y comprometido para atender todas tus operaciones:</strong></p>
      <p class="reveal">o&nbsp;&nbsp; <strong>Bodega:</strong> personal para recepción y entrega de mercancías, Paletizaje y despaletizaje de Carga, Personal de sorting para courier, operadores de montacargas, Digitados y Personal de atención al cliente.</p>
      <p class="reveal">o&nbsp;&nbsp; <strong>Rampa:</strong> Equipo para atención de vuelo pasajeros o Cargueros, Personal para Señaleros o Marshalling, Personal de Cargue y Descargue de aeronaves, drenajes y otros.</p>
      <a class="link-underline link-underline--sm reveal" href="{WA}" target="_blank" rel="noopener">Más información de manpower</a>
    </article>
    <article class="svc-item">
      <img class="reveal" src="assets/1Mesa-de-trabajo-1montacargas.webp" alt="">
      <h2 class="reveal">Manejo de Montacarga.</h2>
      <p class="reveal">Ofrecemos un servicio de <strong>recepción de carga</strong> eficiente, seguro y organizado, asegurando un manejo ágil y controlado de las mercancías desde su arribo hasta su correcta clasificación, almacenamiento y distribución. Nuestro enfoque operativo garantiza trazabilidad, orden y cumplimiento de los estándares logísticos requeridos en cada proceso.</p>
    </article>
    <article class="svc-item">
      <img class="reveal" src="assets/12311365.opt.jpg" alt="">
      <h2 class="reveal">Logística y Transporte.</h2>
      <span class="svc-tag reveal"><svg viewBox="0 0 24 24" width="16" height="16"><path fill="currentColor" d="M12 2a10 10 0 1 0 0 20 10 10 0 0 0 0-20Zm-1 17.9A8 8 0 0 1 4 12c0-.6.1-1.2.2-1.8L9 15v1a2 2 0 0 0 2 2v1.9Zm6.9-2.5A2 2 0 0 0 16 16h-1v-3a1 1 0 0 0-1-1H8v-2h2a1 1 0 0 0 1-1V7h2a2 2 0 0 0 2-2v-.4a8 8 0 0 1 2.9 12.8Z"/></svg> OPERACIONES LOGISTICAS</span>
      <p class="reveal">Ofrecemos un servicio integral de <strong>importación y exportación</strong>, enfocado en la eficiencia operativa, el cumplimiento de las normativas vigentes y la seguridad en cada etapa del proceso. Gestionamos sus operaciones de forma ordenada y confiable, asegurando una correcta coordinación logística desde el origen hasta el destino final.</p>
    </article>
    <article class="svc-item">
      <img class="reveal" src="assets/inst.jpg" alt="">
      <h2 class="reveal">Alquiler de Salones</h2>
      <p class="reveal">Ponemos a disposición nuestro Centro de Entrenamiento para la realización de capacitaciones, entrenamientos corporativos, charlas y sesiones formativas.</p>
      <p class="reveal">Nuestras instalaciones cuentan con oficinas modernas y adaptables, equipadas con tecnología de última generación, internet de alta velocidad, espacios cómodos y funcionales, y servicio de cafetería, creando un entorno profesional ideal para el aprendizaje y el desarrollo de equipos.</p>
    </article>
  </div>
</section>

<section class="ally-banner">
  <div class="ally-banner__bg" style="background-image:url('assets/2151541845.opt.jpg')"></div>
  <h2 class="reveal">Tu aliado logístico en cada etapa</h2>
</section>

"""
    return layout("Servicios", body, "servicios")


def contact_page():
    body = f"""
<section class="container contact">
  <div class="contact__info">
    <p class="eyebrow reveal">Contacto</p>
    <h1 class="reveal">¿Tiene una consulta? Estamos aquí para ayudarle</h1>
    <p class="reveal">Estamos listos para entender sus necesidades y optimizar el manejo de su carga.</p>
    <ul class="contact__list reveal">
      <li>{ICONS["pin"]}<span>Edificio Global Business Terminal,<br>Av. Domingo Díaz, Piso 5, Oficina 1.</span></li>
      <li>{ICONS["phone"]}<a href="tel:+5073756602">+507 375-6602 / 375-6601</a></li>
      <li>{ICONS["mail"]}<a href="mailto:certificaciones@pgbpanama.com">certificaciones@pgbpanama.com</a></li>
    </ul>
    {socials()}
  </div>
  <form class="contact__form reveal" id="contactForm" novalidate>
    <h2>Formulario</h2>
    <label>Nombre<input name="nombre" required autocomplete="name"></label>
    <label>Consulta
      <select name="consulta"><option>Servicios</option><option>Capacitaciones</option><option>PGB Cargo</option><option>Otro</option></select>
    </label>
    <label>Correo electrónico<input name="email" type="email" required autocomplete="email"></label>
    <label>Mensaje<textarea name="mensaje" rows="5" required></textarea></label>
    <button class="btn btn--navy" type="submit">Enviar</button>
    <p class="form-note" id="formNote" role="status" aria-live="polite"></p>
  </form>
</section>
<section class="map">
  <iframe src="https://maps.google.com/maps?t=m&amp;output=embed&amp;iwloc=near&amp;z=15&amp;q=9.0700982%2C-79.3947642" title="Ubicación de PGB – Av. Domingo Díaz, Edificio Global Business Terminal" loading="lazy" referrerpolicy="no-referrer-when-downgrade" allowfullscreen></iframe>
</section>
"""
    return layout("Contacto", body, "contacto")


def home_page():
    org = {"@context": "https://schema.org", "@type": "Organization", "name": "PGB – Premium Ground Business",
           "url": SITE_URL, "logo": f"{SITE_URL}/assets/LOGO-EDIABLTE-HORIZONTAL-PRINCIPAL.png",
           "telephone": "+507 375-6602", "email": "info@pgbpanama.com",
           "address": {"@type": "PostalAddress", "streetAddress": "Av. Domingo Díaz, Edificio Global Business Terminal, Piso 5, Oficina 1",
                       "addressLocality": "Ciudad de Panamá", "addressCountry": "PA"},
           "sameAs": [SOCIAL["ig"][1], SOCIAL["fb"][1]]}
    extra = f'<script type="application/ld+json">{json.dumps(org, ensure_ascii=False)}</script>'
    return layout(None, (BUILD / "home.html").read_text(), "inicio", solid=False, extra_head=extra)


def main():
    pages = {
        "index.html": home_page(),
        "nosotros.html": about_page(),
        "instalaciones.html": facilities_page(),
        "servicios.html": services_page(),
        "centro-de-entrenamiento.html": training_hub_page(),
        "cursos-iata.html": iata_page(),
        "cursos-pgb.html": pgb_page(),
        "primeros-auxilios.html": first_aid_page(),
        "contacto.html": contact_page(),
    }
    for c in COURSES:
        pages[f'{c["slug"]}.html'] = course_page(c)
    for name, content in pages.items():
        (ROOT / name).write_text(content)
    print(f"Built {len(pages)} pages into {ROOT}")


if __name__ == "__main__":
    main()
