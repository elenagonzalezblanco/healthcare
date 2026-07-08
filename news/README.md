# Noticias del blog Nakaia

Deja aquí cada noticia como un fichero `.md`. Al recargar la web NO se actualiza sola:
hay que regenerar el blog ejecutando en la carpeta del proyecto:

    python3 build_blog.py

Eso reescribe la zona de noticias de `blog.html` (entre `<!-- NEWS:START -->` y `<!-- NEWS:END -->`)
con el mismo formato de tarjetas. Después: `git add -A && git commit -m "..." && git push`.

## Formato de cada noticia (.md)

```
---
title: Título de la noticia
category: Prevención
date: 2026-07-08
image: images/pilar-01-tablet.jpg
read: 5 min
featured: true        # opcional: marca el artículo destacado grande de arriba
summary: Texto breve que aparece en la tarjeta.
---
Cuerpo opcional (para una futura página de artículo).
```

- `date` en formato `AAAA-MM-DD`. Las noticias se ordenan de más reciente a más antigua.
- `image`: ruta relativa a una imagen dentro de `images/`.
- Solo una noticia debería llevar `featured: true` (si hay varias, se usa la más reciente).
- El nombre del fichero recomendado: `AAAA-MM-DD-titulo-corto.md`.
