#!/usr/bin/env bash
# Construye, levanta y detiene la app del equipo con Docker.
# Los datos propios de cada app (puerto, ruta de salud, comando) están en lab/app.env.
#
#   bash lab/app.sh levantar      construye la imagen desde app/ y la levanta
#   bash lab/app.sh rapido        levanta la imagen publicada por el proyecto original, si existe
#   bash lab/app.sh iniciar IMG   levanta una imagen ya construida (la usan los workflows)
#   bash lab/app.sh humo          verifica que la app responde
#   bash lab/app.sh logs          muestra la bitácora del contenedor
#   bash lab/app.sh detener       detiene y borra el contenedor
set -euo pipefail
cd "$(dirname "$0")/.."
# shellcheck source=lab/app.env
source lab/app.env

IMAGEN_LOCAL="${APP_IMAGEN_LOCAL:-lab-app:local}"
CONTENEDOR="${APP_CONTENEDOR:-lab-app}"
# APP_PUERTO_HOST cambia el puerto publicado en la máquina, si el de la app está ocupado.
PUERTO_HOST="${APP_PUERTO_HOST:-$APP_PUERTO}"
URL="http://localhost:${PUERTO_HOST}"

construir() {
  docker build -t "$IMAGEN_LOCAL" app
}

esperar() {
  local limite="${APP_ESPERA_SEGUNDOS:-180}"
  for ((i = 0; i < limite; i += 2)); do
    if curl -fsS -o /dev/null "$URL$APP_RUTA_SALUD" 2>/dev/null; then
      return 0
    fi
    if [ -z "$(docker ps -q -f "name=^${CONTENEDOR}$")" ]; then
      docker logs "$CONTENEDOR" || true
      echo "La app se detuvo antes de responder." >&2
      return 1
    fi
    sleep 2
  done
  docker logs --tail 80 "$CONTENEDOR" || true
  echo "La app no respondió en $URL$APP_RUTA_SALUD después de ${limite} s." >&2
  return 1
}

iniciar() {
  local imagen="${1:-$IMAGEN_LOCAL}"
  docker rm -f "$CONTENEDOR" >/dev/null 2>&1 || true
  docker run -d --name "$CONTENEDOR" -p "127.0.0.1:${PUERTO_HOST}:${APP_PUERTO}" \
    ${APP_DOCKER_ARGS[@]+"${APP_DOCKER_ARGS[@]}"} \
    "$imagen" \
    ${APP_COMANDO[@]+"${APP_COMANDO[@]}"} >/dev/null
  esperar
  if [ -n "${APP_RUTA_INICIAL:-}" ]; then
    curl -fsS -o /dev/null "$URL$APP_RUTA_INICIAL"
  fi
  echo "$APP_NOMBRE lista en $URL"
}

case "${1:-ayuda}" in
  construir) construir ;;
  levantar) construir && iniciar "$IMAGEN_LOCAL" ;;
  rapido)
    if [ -n "${APP_IMAGEN_UPSTREAM:-}" ]; then
      docker pull "$APP_IMAGEN_UPSTREAM" && iniciar "$APP_IMAGEN_UPSTREAM"
    else
      echo "Esta app no publica imagen oficial; se construye desde app/." && construir && iniciar "$IMAGEN_LOCAL"
    fi
    ;;
  iniciar) iniciar "${2:-$IMAGEN_LOCAL}" ;;
  humo) curl -fsS -o /dev/null -w "GET $APP_RUTA_SALUD -> %{http_code}\n" "$URL$APP_RUTA_SALUD" ;;
  logs) docker logs "$CONTENEDOR" ;;
  detener) docker rm -f "$CONTENEDOR" ;;
  url) echo "$URL" ;;
  *) sed -n '2,12p' "$0" ;;
esac
