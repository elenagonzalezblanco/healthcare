#!/usr/bin/env python3
"""Genera la sección de noticias de blog.html a partir de los BRIEFS que dejes en news/.

Flujo previsto:
  1. Dejas en la carpeta news/ uno o varios ficheros .html de brief (como
     news/privia-brief-2026-07-08.html), tal cual te llegan.
  2. Ejecutas:  python3 build_blog.py
  3. El script extrae CADA noticia real del brief — su TÍTULO, FUENTE, FECHA y
     ENLACE original — y reescribe la zona de noticias de blog.html (entre
     <!-- NEWS:START --> y <!-- NEWS:END -->) con tarjetas en el formato Privia Health.

NO se inventa contenido: solo se usan las noticias enlazadas del brief.
Se omiten los bloques de análisis interno (Tendencias / Implicaciones), que no
son noticias con fuente y que el propio brief marca como internos.
Las noticias se ordenan por fecha (más recientes primero).
"""
import os, re, glob, html
from datetime import datetime

BRIEF_GLOB = "news/*.html"
BLOG = "blog.html"

MESES = {"ene": 1, "feb": 2, "mar": 3, "abr": 4, "may": 5, "jun": 6,
         "jul": 7, "ago": 8, "sep": 9, "set": 9, "oct": 10, "nov": 11, "dic": 12}
MESES_NOMBRE = ["enero", "febrero", "marzo", "abril", "mayo", "junio",
                "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"]
MESES.update({"jan": 1, "apr": 4, "aug": 8, "dec": 12})
MONTH_NAMES = ["January", "February", "March", "April", "May", "June",
               "July", "August", "September", "October", "November", "December"]


def strip_tags(s):
    return re.sub(r"<[^>]+>", "", s)


def clean(s):
    return html.unescape(strip_tags(s)).strip().strip('"').strip("«»").strip()


def parse_date(s):
    m = re.search(r"(\d{1,2})\s+([A-Za-zñáéíóú]+)\.?\s+(\d{4})", s)
    if not m:
        return (datetime.min, s)
    day, mon, year = int(m.group(1)), m.group(2)[:3].lower(), int(m.group(3))
    month = MESES.get(mon, 1)
    try:
        d = datetime(year, month, day)
    except ValueError:
        d = datetime.min
    return (d, s)


def display_date(dt, original, language="es"):
    if dt == datetime.min:
        return original
    if language == "en":
        return f"{dt.day} {MONTH_NAMES[dt.month - 1]} {dt.year}"
    return f"{dt.day} de {MESES_NOMBRE[dt.month - 1]} de {dt.year}"


def parse_briefs(language="es"):
    items = []
    for path in sorted(glob.glob(BRIEF_GLOB)):
        if path.endswith(".en.html") != (language == "en"):
            continue
        raw = open(path, encoding="utf-8").read()
        parts = re.split(r"<h2[^>]*>(.*?)</h2>", raw, flags=re.S)
        for i in range(1, len(parts), 2):
            raw_cat = clean(parts[i])
            category = re.sub(r"\s*\(.*?\)\s*", "", raw_cat).split("·")[0].strip()
            content = parts[i + 1] if i + 1 < len(parts) else ""
            pat = re.compile(
                r'<a href="([^"]+)"[^>]*>(.*?)</a>\s*<div[^>]*color:#888[^>]*>(.*?)</div>',
                re.S,
            )
            for m in pat.finditer(content):
                link = html.unescape(m.group(1)).strip()
                title = clean(m.group(2))
                srcdate = clean(m.group(3))
                source, date_txt = srcdate, ""
                if "·" in srcdate:
                    source, date_txt = [x.strip() for x in srcdate.split("·", 1)]
                dt, _ = parse_date(date_txt)
                items.append({
                    "link": link, "title": title, "source": source,
                    "date_txt": date_txt, "date_disp": display_date(dt, date_txt, language),
                    "category": category, "_dt": dt,
                })
    return items


def card_html(n, language="es"):
    read_source = "Read the source" if language == "en" else "Leer la fuente"
    return f'''        <a class="news-card" href="{html.escape(n['link'])}" target="_blank" rel="noopener">
          <span class="tag">{html.escape(n['category'])}</span>
          <h3>{html.escape(n['title'])}</h3>
          <div class="src">{html.escape(n['source'])} · {html.escape(n['date_disp'])}</div>
          <span class="readsrc">{read_source} &#8599;</span>
        </a>'''


def main(language="es"):
    blog = "blog.en.html" if language == "en" else BLOG
    items = parse_briefs(language)
    # dedup por enlace
    seen, uniq = set(), []
    for n in items:
        if n["link"] in seen:
            continue
        seen.add(n["link"])
        uniq.append(n)
    if not uniq:
        print("No se han encontrado noticias en los briefs de news/. blog.html sin cambios.")
        return
    uniq.sort(key=lambda n: n["_dt"], reverse=True)
    cards = "\n".join(card_html(n, language) for n in uniq)
    region = (
        "  <!-- Noticias del sector -->\n"
        "  <section class=\"posts\">\n"
        "    <div class=\"container\">\n"
        "      <div class=\"grid\">\n\n"
        + cards
        + "\n\n      </div>\n    </div>\n  </section>"
    )
    with open(blog, encoding="utf-8") as f:
        page = f.read()
    new = re.sub(
        r"<!-- NEWS:START -->.*?<!-- NEWS:END -->",
        "<!-- NEWS:START -->\n" + region + "\n  <!-- NEWS:END -->",
        page, flags=re.S,
    )
    with open(blog, "w", encoding="utf-8") as f:
        f.write(new)
    print(f"{blog} actualizado con {len(uniq)} noticias reales del brief.")


if __name__ == "__main__":
    main()
    if os.path.exists("blog.en.html"):
        main("en")
