#!/usr/bin/env bash
#
# Registra la app "Resolución" para que arranque automáticamente al iniciar
# sesión en macOS (mediante un LaunchAgent del usuario).
#
set -euo pipefail

DIR="$(cd "$(dirname "$0")" && pwd)"
LABEL="com.antonio.resolucion"
PLIST="$HOME/Library/LaunchAgents/$LABEL.plist"
PYTHON="$DIR/.venv/bin/python"

# Asegura que el entorno exista (lo crea run.sh la primera vez).
if [ ! -x "$PYTHON" ]; then
  echo "Creando entorno virtual…"
  python3 -m venv "$DIR/.venv"
  "$DIR/.venv/bin/pip" install --quiet --upgrade pip
  "$DIR/.venv/bin/pip" install --quiet -r "$DIR/requirements.txt"
fi

mkdir -p "$HOME/Library/LaunchAgents"

cat > "$PLIST" <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN"
  "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>$LABEL</string>
    <key>ProgramArguments</key>
    <array>
        <string>$PYTHON</string>
        <string>$DIR/resolucion.py</string>
    </array>
    <key>WorkingDirectory</key>
    <string>$DIR</string>
    <key>RunAtLoad</key>
    <true/>
    <key>StandardOutPath</key>
    <string>$DIR/resolucion.log</string>
    <key>StandardErrorPath</key>
    <string>$DIR/resolucion.log</string>
</dict>
</plist>
EOF

# Recarga el agente (lo descarga si ya estaba) y lo arranca.
launchctl bootout "gui/$(id -u)/$LABEL" 2>/dev/null || true
launchctl bootstrap "gui/$(id -u)" "$PLIST"

echo "✅ Arranque automático instalado."
echo "   La app 'Resolución' se abrirá sola cada vez que inicies sesión."
echo "   Para quitarlo: ./desinstalar-inicio.sh"
