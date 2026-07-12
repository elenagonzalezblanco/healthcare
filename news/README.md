# Noticias del blog Privia Health

El blog se genera EXCLUSIVAMENTE a partir de los briefs que dejes en esta carpeta.
No se inventa contenido.

## Cómo añadir noticias

1. Deja aquí el fichero del brief tal cual te llega, en `.html`
   (por ejemplo `privia-brief-2026-07-08.html`).
2. En la carpeta del proyecto ejecuta:

       python3 build_blog.py

   El script recorre todos los `news/*.html`, extrae CADA noticia enlazada
   (su **título**, **fuente**, **fecha** y **enlace** originales) y reescribe la
   zona de noticias de `blog.html` con tarjetas en el formato Privia Health, ordenadas
   de más reciente a más antigua.
3. Publica:

       git add -A && git commit -m "Actualiza noticias del blog" && git push

## Qué se publica y qué no

- Se publican solo las **noticias con fuente y enlace** del brief.
- Se omiten los bloques de análisis interno ("Tendencias del sector",
  "Implicaciones para PRIVIA/Nakaia"), porque no son noticias con fuente y el
  propio brief los marca como material interno no destinado a difusión externa.

Cada tarjeta enlaza al artículo original (se abre en una pestaña nueva) y muestra
la fuente y la fecha reales.
