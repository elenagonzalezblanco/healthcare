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
  # Aviso si falta el brief de hoy (a partir de las 8:00, como mucho una vez al día)
  TODAY=$(date +%F); HOUR=$(date +%H); FLAG="$HOME/Library/Logs/.nakaia-notified-$TODAY"
  if ls news/*"$TODAY"*.html >/dev/null 2>&1; then
    echo "brief de hoy ($TODAY): presente"
  elif [ "$HOUR" -ge 8 ] && [ ! -f "$FLAG" ]; then
    /usr/bin/osascript -e 'display notification "No encuentro el brief de hoy en la carpeta local (Escritorio → Nakaia-briefs). El blog no se ha actualizado con noticias nuevas." with title "Privia Health · Blog" sound name "Ping"' || true
    touch "$FLAG"
    echo "brief de hoy ($TODAY): FALTA -> aviso enviado"
  else
    echo "brief de hoy ($TODAY): falta (sin aviso: antes de las 8h o ya avisado)"
  fi
  echo ""
} >> "$LOG" 2>&1
