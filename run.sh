#!/usr/bin/env bash
#
# Corre la app de barra de menú "Resolución" en modo dev.
# Crea un entorno virtual la primera vez, instala dependencias y arranca.
#
set -euo pipefail

cd "$(dirname "$0")"

VENV=".venv"

if [ ! -d "$VENV" ]; then
  echo "Creando entorno virtual…"
  python3 -m venv "$VENV"
  "$VENV/bin/pip" install --quiet --upgrade pip
  "$VENV/bin/pip" install --quiet -r requirements.txt
fi

exec "$VENV/bin/python" resolucion.py
