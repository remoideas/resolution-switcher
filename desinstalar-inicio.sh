#!/usr/bin/env bash
#
# Quita el arranque automático de la app "Resolución".
#
set -euo pipefail

LABEL="com.antonio.resolucion"
PLIST="$HOME/Library/LaunchAgents/$LABEL.plist"

launchctl bootout "gui/$(id -u)/$LABEL" 2>/dev/null || true
rm -f "$PLIST"

echo "✅ Arranque automático desinstalado."
echo "   (La app que esté abierta ahora sigue corriendo hasta que la cierres.)"
