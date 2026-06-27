# 🖥️ ResolutionSwitcher

**Cambia la resolución de tu Mac con un clic desde la barra de menú.** Pensada
para quienes trabajan en equipos remotos y necesitan saltar rápido entre una
resolución "grande" para el monitor real y una "chica" para cuando se conectan
en remoto.

> _A tiny macOS menu bar + Dock app to switch your display resolution with one
> click. Built for people who work on remote machines._ (English summary at the
> bottom.)

---

## 💡 ¿Por qué la hice?

Cuando me conecto a mi Mac de forma **remota** (Pantalla Compartida, VNC, etc.),
la pantalla del equipo remoto se ve **diminuta**: la resolución nativa es enorme
y todo queda muy chico para trabajar cómodo desde otra máquina.

Cada vez tenía que entrar a **Ajustes → Pantallas** y cambiar la resolución a
mano: bajarla para verlo bien en remoto, y volver a subirla al sentarme frente
al equipo. Aburrido y lento.

Así que hice esta app: **dos botones grandes** para alternar al instante entre
mi resolución de **escritorio** (1920×1080) y una **"móvil"/remota** más chica
(960×540), sin abrir Ajustes y sin comandos.

## 🎯 ¿A quién le sirve?

- 🧑‍💻 **Gente que usa su Mac en remoto** (como yo): baja la resolución para
  trabajar cómodo desde otro equipo y súbela al volver, en un clic.
- 🖥️ Quien quiere **alternar resoluciones rápido** sin entrar a Ajustes cada vez.
- 📐 Cualquiera que necesite presets de resolución a mano (presentar, grabar,
  agrandar la interfaz, etc.).

## ✨ Características

- **Icono 🖥️ en la barra de menú** con accesos rápidos.
- **Icono en el Dock** que abre una ventana con **dos botones grandes**:
  Escritorio y Móvil.
- **Valores configurables** y guardados en disco (se mantienen entre reinicios).
- **Lista de todos los modos** que tu monitor soporta, por si quieres otro.
- **Arranque automático** al iniciar sesión (opcional).
- **Sin dependencias externas raras**: cambia la resolución con las APIs nativas
  de macOS (CoreGraphics/Quartz vía PyObjC). No instala herramientas de terceros
  ni necesita permisos especiales para cambiar la resolución.

## 📦 Requisitos

- **macOS** (probado en versiones recientes).
- **Python 3** (el que ya trae macOS, o el de [python.org] / Homebrew).
- Conexión a internet la **primera vez** (para instalar 2 paquetes de Python).

[python.org]: https://www.python.org/downloads/macos/

## 🚀 Instalación y uso (modo dev, lo más fácil)

Clona el repo y arráncala:

```bash
git clone https://github.com/remoideas/resolution-switcher.git
cd resolution-switcher
./run.sh
```

`run.sh` crea un entorno virtual e instala las dependencias **solo la primera
vez**; las siguientes arranca directo. Verás el icono **🖥️** en la barra de
arriba y un icono en el **Dock**.

### Cómo se usa

**Desde la barra de menú (arriba):** clic en 🖥️ →
- `Resolución Escritorio (1920×1080)` — aplica tu preset de escritorio
- `Resolución Móvil (960×540)` — aplica tu preset chico/remoto
- `Abrir ventana…`
- `Salir`

**Desde la ventana** (icono del Dock, o "Abrir ventana…"):
- **Dos botones grandes** — clic = aplica esa resolución al instante.
- **Editar valores** — cambia el `ANCHOxALTO` de cada preset y pulsa
  *Guardar y aplicar*. Se guarda y el botón grande se actualiza solo.
- **Otro modo** — lista desplegable con **todas** las resoluciones que tu
  monitor soporta, por si quieres aplicar una distinta.
- Abajo se muestra la **resolución actual** en vivo.

## ⚙️ Configuración

Los presets se guardan en:

```
~/Library/Application Support/Resolucion/config.json
```

Ejemplo:

```json
{
  "escritorio": { "width": 1920, "height": 1080 },
  "movil":      { "width": 960,  "height": 540 }
}
```

Puedes editarlos desde la ventana (recomendado) o a mano en ese archivo.

> ℹ️ Solo se aplican resoluciones que **tu monitor soporta**. Si pones un valor
> que no existe, la app aplica el **modo más cercano** y te avisa. Para ver los
> modos disponibles, mira la lista *"Otro modo"* en la ventana.

## 🔁 Arranque automático al iniciar sesión

Para que la app se abra sola cada vez que enciendes/entras a tu Mac:

```bash
./instalar-inicio.sh
```

Esto registra un **LaunchAgent** del usuario en
`~/Library/LaunchAgents/com.antonio.resolucion.plist` y la deja gestionada por
macOS (ya no depende de tener la terminal abierta).

Para quitar el arranque automático:

```bash
./desinstalar-inicio.sh
```

Si editas `resolucion.py`, vuelve a correr `./instalar-inicio.sh` para
recargarla.

## 🧠 ¿Cómo funciona por dentro?

- La interfaz (barra de menú, Dock y ventana) usa **PyObjC** (los bindings de
  Python para Cocoa/AppKit).
- El cambio de resolución usa **CoreGraphics / Quartz**:
  `CGDisplayCopyAllDisplayModes` para listar los modos y
  `CGConfigureDisplayWithDisplayMode` + `CGCompleteDisplayConfiguration` para
  aplicarlo de forma permanente sobre el monitor principal.
- No usa herramientas externas (`displayplacer`, etc.) — todo es API nativa.

Estructura del proyecto:

```
resolucion.py          # La app (UI + lógica de resolución)
run.sh                 # Arranque en dev (crea venv, instala deps, corre)
requirements.txt       # pyobjc-framework-Cocoa, pyobjc-framework-Quartz
instalar-inicio.sh     # Activa el arranque automático al iniciar sesión
desinstalar-inicio.sh  # Lo quita
```

## 🩹 Solución de problemas

- **No veo el icono 🖥️ en la barra:** puede estar oculto si la barra está llena;
  mira en el menú de overflow. Revisa también `resolucion.log` en la carpeta del
  proyecto.
- **No pasa nada al aplicar:** probablemente esa resolución exacta no existe en
  tu monitor; usa la lista *"Otro modo"* para ver las soportadas.
- **No arranca sola:** confirma que el agente está cargado con
  `launchctl print gui/$(id -u)/com.antonio.resolucion` y vuelve a correr
  `./instalar-inicio.sh`.
- **Logs:** todo lo que imprime la app va a `resolucion.log` dentro del repo.

## 🤝 Contribuir

¡Las contribuciones son bienvenidas! Ideas que podrían ayudar:

- Soporte para **varios monitores** (hoy actúa sobre el principal).
- Más de dos presets / presets con nombre.
- Empaquetado como **`.app`** nativa (p. ej. con `py2app`).
- Atajos de teclado globales.

Abre un *issue* o un *pull request*.

## 📄 Licencia

[MIT](LICENSE) — úsalo, modifícalo y compártelo libremente.

---

## English summary

**Resolución** is a small macOS menu bar + Dock app that switches your display
resolution with one click. I built it because I often work on my Mac
**remotely**, and at native resolution everything looks tiny on the remote
screen. Instead of opening *System Settings → Displays* every time, this app
gives you **two big buttons** — Desktop (e.g. 1920×1080) and Mobile/remote
(e.g. 960×540) — plus a dropdown with every mode your display supports. Presets
are configurable and saved to disk, and it can **launch at login**.

Run it in dev mode with `./run.sh`. Enable autostart with `./instalar-inicio.sh`.
It changes resolution through native macOS CoreGraphics/Quartz APIs (via PyObjC),
with no third-party tools. MIT licensed.
