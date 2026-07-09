#!/bin/bash
# Regenera el blog desde news/*.html y publica los cambios en GitHub.
# Se ejecuta a diario a las 8:00 mediante el LaunchAgent com.nakaia.blog.daily.
REPO="$HOME/Nakaia/healthcare"
cd "$REPO" || exit 1
export PATH="/opt/homebrew/bin:/usr/bin:/bin:/usr/sbin:/sbin"
LOG="$HOME/Library/Logs/nakaia-blog.log"
{
  echo "==== $(date '+%Y-%m-%d %H:%M:%S') ===="
  # Traer posibles cambios remotos para evitar rechazos en el push
  git pull --rebase --autostash origin main || echo "aviso: pull falló, continúo"
  # Regenerar blog.html a partir de los briefs de news/
  /usr/bin/python3 build_blog.py
  # Publicar solo si hay algo nuevo (nuevo brief y/o blog regenerado)
  if [ -n "$(git status --porcelain)" ]; then
    git add -A
    git -c user.name="elenagonzalezblanco" \
        -c user.email="elenagonzalezblanco@users.noreply.github.com" \
        commit -m "Actualiza noticias del blog ($(date +%F))"
    if git push origin main; then
      echo "push OK"
    else
      echo "push FALLO"
    fi
  else
    echo "sin cambios"
  fi
  echo ""
} >> "$LOG" 2>&1
