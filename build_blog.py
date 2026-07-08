#!/usr/bin/env python3
"""Genera la sección de noticias de blog.html a partir de los BRIEFS que dejes en news/.

Flujo previsto:
  1. Dejas en la carpeta news/ uno o varios ficheros .html de brief (como
     news/privia-brief-2026-07-08.html), tal cual te llegan.
  2. Ejecutas:  python3 build_blog.py
  3. El script extrae CADA noticia real del brief — su TÍTULO, FUENTE, FECHA y
     ENLACE original — y reescribe la zona de noticias de blog.html (entre
     <!-- NEWS:START --> y <!-- NEWS:END -->) con tarjetas en el formato Nakaia.

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


def display_date(dt, original):
    if dt == datetime.min:
        return original
    return f"{dt.day} de {MESES_NOMBRE[dt.month - 1]} de {dt.year}"


def parse_briefs():
    items = []
    for path in sorted(glob.glob(BRIEF_GLOB)):
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
                    "date_txt": date_txt, "date_disp": display_date(dt, date_txt),
                    "category": category, "_dt": dt,
                })
    return items


def card_html(n):
    return f'''        <a class="news-card" href="{html.escape(n['link'])}" target="_blank" rel="noopener">
          <span class="tag">{html.escape(n['category'])}</span>
          <h3>{html.escape(n['title'])}</h3>
          <div class="src">{html.escape(n['source'])} · {html.escape(n['date_disp'])}</div>
          <span class="readsrc">Leer la fuente &#8599;</span>
        </a>'''


def main():
    items = parse_briefs()
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
    cards = "\n".join(card_html(n) for n in uniq)
    region = (
        "  <!-- Noticias del sector -->\n"
        "  <section class=\"posts\">\n"
        "    <div class=\"container\">\n"
        "      <div class=\"grid\">\n\n"
        + cards
        + "\n\n      </div>\n    </div>\n  </section>"
    )
    with open(BLOG, encoding="utf-8") as f:
        page = f.read()
    new = re.sub(
        r"<!-- NEWS:START -->.*?<!-- NEWS:END -->",
        "<!-- NEWS:START -->\n" + region + "\n  <!-- NEWS:END -->",
        page, flags=re.S,
    )
    with open(BLOG, "w", encoding="utf-8") as f:
        f.write(new)
    print(f"blog.html actualizado con {len(uniq)} noticias reales del brief.")


if __name__ == "__main__":
    main()
