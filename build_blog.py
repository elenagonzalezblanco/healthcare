#!/usr/bin/env python3
"""Genera la sección de noticias de blog.html a partir de los ficheros de news/.

Cada noticia es un fichero .md dentro de la carpeta news/ con esta cabecera:

    ---
    title: Título de la noticia
    category: Prevención
    date: 2026-07-08
    image: images/pilar-01-tablet.jpg
    read: 5 min
    featured: true        # opcional; el destacado grande de arriba
    summary: Texto breve que aparece en la tarjeta.
    ---
    (Cuerpo opcional, para una futura página de artículo.)

Uso:
    python3 build_blog.py

Reescribe SOLO la zona entre <!-- NEWS:START --> y <!-- NEWS:END --> de blog.html.
Las noticias se ordenan por fecha (más recientes primero).
"""
import os, re, glob
from datetime import datetime

NEWS_DIR = "news"
BLOG = "blog.html"
MESES = ["enero", "febrero", "marzo", "abril", "mayo", "junio",
         "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"]


def parse(path):
    with open(path, encoding="utf-8") as f:
        raw = f.read()
    fm, body = {}, raw
    m = re.match(r"^---\s*\n(.*?)\n---\s*\n?(.*)$", raw, re.S)
    if m:
        block, body = m.group(1), m.group(2)
        for line in block.splitlines():
            if ":" in line:
                k, v = line.split(":", 1)
                fm[k.strip().lower()] = v.strip()
    fm["_body"] = body.strip()
    if not fm.get("summary"):
        fm["summary"] = body.strip().split("\n\n")[0].strip() if body.strip() else ""
    return fm


def date_es(s):
    try:
        d = datetime.strptime(s, "%Y-%m-%d")
        return f"{d.day} de {MESES[d.month - 1]} de {d.year}"
    except Exception:
        return s


def esc(s):
    return (s or "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def featured_html(n):
    return f'''  <!-- Artículo destacado -->
  <section class="featured">
    <div class="container">
      <a href="#">
        <img src="{esc(n['image'])}" alt="{esc(n['title'])}" />
        <div class="ft-body">
          <span class="tag">{esc(n.get('category', ''))}</span>
          <h2>{esc(n['title'])}</h2>
          <p>{esc(n['summary'])}</p>
          <div class="meta">{date_es(n.get('date', ''))} · {esc(n.get('read', ''))} de lectura</div>
        </div>
      </a>
    </div>
  </section>'''


def card_html(n):
    return f'''        <a class="post" href="#">
          <img src="{esc(n['image'])}" alt="{esc(n['title'])}" />
          <div class="p-body">
            <span class="tag">{esc(n.get('category', ''))}</span>
            <h3>{esc(n['title'])}</h3>
            <p>{esc(n['summary'])}</p>
            <div class="meta">{esc(n.get('category', ''))} <span class="dot"></span> {esc(n.get('read', ''))}</div>
          </div>
        </a>'''


def main():
    files = sorted(glob.glob(os.path.join(NEWS_DIR, "*.md")))
    items = [parse(f) for f in files]
    items = [i for i in items if i.get("title")]
    if not items:
        print("No hay noticias en news/. blog.html sin cambios.")
        return
    items.sort(key=lambda i: i.get("date", ""), reverse=True)
    feat = next((i for i in items if str(i.get("featured", "")).lower() == "true"), items[0])
    rest = [i for i in items if i is not feat]
    grid = "\n".join(card_html(n) for n in rest)
    region = (
        featured_html(feat)
        + "\n\n  <!-- Rejilla de artículos -->\n  <section class=\"posts\">\n"
          "    <div class=\"container\">\n      <div class=\"grid\">\n\n"
        + grid
        + "\n\n      </div>\n    </div>\n  </section>"
    )
    with open(BLOG, encoding="utf-8") as f:
        html = f.read()
    new = re.sub(
        r"<!-- NEWS:START -->.*?<!-- NEWS:END -->",
        "<!-- NEWS:START -->\n" + region + "\n  <!-- NEWS:END -->",
        html, flags=re.S,
    )
    with open(BLOG, "w", encoding="utf-8") as f:
        f.write(new)
    print(f"blog.html actualizado: 1 destacado + {len(rest)} tarjetas.")


if __name__ == "__main__":
    main()
