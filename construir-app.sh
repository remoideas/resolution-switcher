#!/usr/bin/env bash
#
# Construye ResolutionSwitcher.app (nativa, doble clic) con py2app
# y la empaqueta en un .zip listo para subir a un Release de GitHub.
#
set -euo pipefail

DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$DIR"

PY="$DIR/.venv/bin/python"

# Asegura entorno + dependencias + py2app
if [ ! -x "$PY" ]; then
  python3 -m venv .venv
fi
"$DIR/.venv/bin/pip" install --quiet --upgrade pip
"$DIR/.venv/bin/pip" install --quiet -r requirements.txt
"$DIR/.venv/bin/pip" install --quiet py2app

# Limpia builds anteriores
rm -rf build dist

echo "Construyendo .app…"
"$PY" setup.py py2app

# Empaqueta en zip (preservando el bundle .app)
cd dist
rm -f ResolutionSwitcher.zip
ditto -c -k --keepParent ResolutionSwitcher.app ResolutionSwitcher.zip
cd "$DIR"

echo
echo "✅ App construida: dist/ResolutionSwitcher.app"
echo "✅ Zip para release: dist/ResolutionSwitcher.zip"
echo "   sha256: $(shasum -a 256 dist/ResolutionSwitcher.zip | awk '{print $1}')"
