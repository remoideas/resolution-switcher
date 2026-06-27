# 🖥️ ResolutionSwitcher

**Switch your Mac's display resolution with one click from the menu bar.** Built
for people who work on remote machines and need to quickly jump between a "big"
resolution for the real monitor and a "small" one for when they connect
remotely.

---

## 💡 Why I built it

When I connect to my Mac **remotely** (Screen Sharing, VNC, etc.), the remote
screen looks **tiny**: the native resolution is huge and everything is too small
to work comfortably from another machine.

Every time, I had to go into **System Settings → Displays** and change the
resolution by hand: lower it to see things well over remote, then raise it again
when sitting back at the machine. Tedious and slow.

So I built this app: **two big buttons** to instantly toggle between my
**desktop** resolution (1920×1080) and a smaller **"mobile"/remote** one
(960×540), without opening Settings and without commands.

## 🎯 Who is it for?

- 🧑‍💻 **People who use their Mac remotely** (like me): drop the resolution to
  work comfortably from another machine and raise it when you're back, in one
  click.
- 🖥️ Anyone who wants to **switch resolutions fast** without opening Settings
  every time.
- 📐 Anyone who needs resolution presets at hand (presenting, recording, making
  the UI bigger, etc.).

## ✨ Features

- **🖥️ menu bar icon** with quick actions.
- **Dock icon** that opens a window with **two big buttons**: Desktop and Mobile.
- **Configurable values** saved to disk (they persist across restarts).
- **List of every mode** your display supports, in case you want a different one.
- **Launch at login** (optional).
- **No weird external dependencies**: it changes the resolution using native
  macOS APIs (CoreGraphics/Quartz via PyObjC). No third-party tools and no
  special permissions required to change the resolution.

## 📦 Requirements

- **macOS** (tested on recent versions).
- **Python 3** (the one that ships with macOS, or from [python.org] / Homebrew).
- Internet connection the **first time** (to install 2 Python packages).

[python.org]: https://www.python.org/downloads/macos/

## 🚀 Install & run (dev mode, the easy way)

Clone the repo and run it:

```bash
git clone https://github.com/remoideas/resolution-switcher.git
cd resolution-switcher
./run.sh
```

`run.sh` creates a virtual environment and installs the dependencies **only the
first time**; after that it runs directly. You'll see the **🖥️** icon in the
menu bar and an icon in the **Dock**.

### How to use it

**From the menu bar (top):** click 🖥️ →
- `Resolución Escritorio (1920×1080)` — applies your desktop preset
- `Resolución Móvil (960×540)` — applies your small/remote preset
- `Abrir ventana…` (Open window)
- `Salir` (Quit)

**From the window** (Dock icon, or "Abrir ventana…"):
- **Two big buttons** — click = applies that resolution instantly.
- **Edit values** — change each preset's `WIDTHxHEIGHT` and hit *Guardar y
  aplicar* (Save & apply). It's saved and the big button updates itself.
- **Other mode** — dropdown with **every** resolution your display supports, in
  case you want to apply a different one.
- The **current resolution** is shown live at the bottom.

> ℹ️ The in-app UI labels are in Spanish (it started as a personal tool).
> Contributions to add English/i18n are very welcome — see *Contributing*.

## ⚙️ Configuration

Presets are saved to:

```
~/Library/Application Support/Resolucion/config.json
```

Example:

```json
{
  "escritorio": { "width": 1920, "height": 1080 },
  "movil":      { "width": 960,  "height": 540 }
}
```

You can edit them from the window (recommended) or by hand in that file.

> ℹ️ Only resolutions **your display supports** can be applied. If you enter a
> value that doesn't exist, the app applies the **closest mode** and lets you
> know. To see the available modes, check the *"Other mode"* list in the window.

## 🔁 Launch at login

To have the app open by itself every time you turn on / log into your Mac:

```bash
./instalar-inicio.sh
```

This registers a per-user **LaunchAgent** at
`~/Library/LaunchAgents/com.antonio.resolucion.plist` and lets macOS manage it
(it no longer depends on keeping a terminal open).

To remove the autostart:

```bash
./desinstalar-inicio.sh
```

If you edit `resolucion.py`, run `./instalar-inicio.sh` again to reload it.

## 🧠 How it works under the hood

- The UI (menu bar, Dock and window) uses **PyObjC** (Python bindings for
  Cocoa/AppKit).
- The resolution change uses **CoreGraphics / Quartz**:
  `CGDisplayCopyAllDisplayModes` to list the modes, and
  `CGConfigureDisplayWithDisplayMode` + `CGCompleteDisplayConfiguration` to apply
  it permanently to the main display.
- No external tools (`displayplacer`, etc.) — it's all native API.

Project structure:

```
resolucion.py          # The app (UI + resolution logic)
run.sh                 # Dev launcher (creates venv, installs deps, runs)
requirements.txt       # pyobjc-framework-Cocoa, pyobjc-framework-Quartz
instalar-inicio.sh     # Enables launch at login
desinstalar-inicio.sh  # Removes it
```

## 🩹 Troubleshooting

- **I don't see the 🖥️ icon in the menu bar:** it may be hidden if the bar is
  full; check the overflow menu. Also look at `resolucion.log` in the project
  folder.
- **Nothing happens when I apply:** that exact resolution probably doesn't exist
  on your display; use the *"Other mode"* list to see the supported ones.
- **It doesn't start on its own:** confirm the agent is loaded with
  `launchctl print gui/$(id -u)/com.antonio.resolucion` and run
  `./instalar-inicio.sh` again.
- **Logs:** everything the app prints goes to `resolucion.log` inside the repo.

## 🤝 Contributing

Contributions are welcome! Ideas that could help:

- **English / i18n** for the in-app UI labels.
- Support for **multiple monitors** (today it acts on the main one).
- More than two presets / named presets.
- Packaging as a native **`.app`** (e.g. with `py2app`).
- Global keyboard shortcuts.

Open an issue or a pull request.

## 📄 License

[MIT](LICENSE) — use it, modify it and share it freely.

---

## Resumen en español

**ResolutionSwitcher** es una pequeña app de barra de menú + Dock para macOS que
cambia la resolución de tu pantalla con un clic. La hice porque a menudo trabajo
en mi Mac de forma **remota**, y a resolución nativa todo se ve diminuto en la
pantalla remota. En vez de abrir *Ajustes → Pantallas* cada vez, esta app te da
**dos botones grandes** — Escritorio (p. ej. 1920×1080) y Móvil/remoto (p. ej.
960×540) — más una lista con todos los modos que tu monitor soporta. Los presets
son configurables y se guardan en disco, y puede **arrancar al iniciar sesión**.

Córrela en modo dev con `./run.sh`. Activa el arranque automático con
`./instalar-inicio.sh`. Cambia la resolución usando las APIs nativas de macOS
(CoreGraphics/Quartz vía PyObjC), sin herramientas de terceros. Licencia MIT.
