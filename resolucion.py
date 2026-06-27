#!/usr/bin/env python3
"""
Resolución — app de macOS para cambiar la resolución del monitor principal.

Tiene DOS entradas:
  • Un icono 🖥️ en la barra de menú (arriba) con opciones rápidas.
  • Un icono en el Dock (abajo) que abre una ventana donde puedes ver,
    editar y aplicar las resoluciones, o elegir cualquier modo de la lista.

Presets por defecto:
  • Escritorio → 1920×1080
  • Móvil      → 960×540

Los valores se guardan en disco y se mantienen entre reinicios.
"""

import json
import os

import objc
import Quartz
from Cocoa import (
    NSApplication,
    NSApp,
    NSObject,
    NSStatusBar,
    NSMenu,
    NSMenuItem,
    NSWindow,
    NSButton,
    NSTextField,
    NSPopUpButton,
    NSAlert,
    NSMakeRect,
    NSBackingStoreBuffered,
    NSFont,
)
from PyObjCTools import AppHelper


# --------------------------------------------------------------------------
# Constantes (con respaldo por si la versión de PyObjC no las exporta)
# --------------------------------------------------------------------------

NSVariableStatusItemLength = -1.0
NSApplicationActivationPolicyRegular = 0
NSWindowStyleMaskTitled = 1
NSWindowStyleMaskClosable = 2
NSWindowStyleMaskMiniaturizable = 4
NSBezelStyleRounded = 1
NSBezelStyleRegularSquare = 2
NSTextAlignmentCenter = 2


# --------------------------------------------------------------------------
# Configuración persistente
# --------------------------------------------------------------------------

CONFIG_DIR = os.path.expanduser("~/Library/Application Support/Resolucion")
CONFIG_PATH = os.path.join(CONFIG_DIR, "config.json")

DEFAULTS = {
    "escritorio": {"width": 1920, "height": 1080},
    "movil": {"width": 960, "height": 540},
}


def load_config():
    try:
        with open(CONFIG_PATH, "r") as f:
            data = json.load(f)
        for key, val in DEFAULTS.items():
            data.setdefault(key, dict(val))
        return data
    except (FileNotFoundError, ValueError):
        return {k: dict(v) for k, v in DEFAULTS.items()}


def save_config(config):
    os.makedirs(CONFIG_DIR, exist_ok=True)
    with open(CONFIG_PATH, "w") as f:
        json.dump(config, f, indent=2)


def parse_res(text):
    """'1920x1080' -> (1920, 1080). Lanza ValueError si el formato es inválido."""
    w_str, h_str = text.lower().replace(" ", "").split("x")
    width, height = int(w_str), int(h_str)
    if width <= 0 or height <= 0:
        raise ValueError("dimensiones deben ser positivas")
    return width, height


# --------------------------------------------------------------------------
# Cambio de resolución (Quartz / CoreGraphics, sin herramientas externas)
# --------------------------------------------------------------------------

def _all_modes(display):
    options = {"kCGDisplayShowDuplicateLowResolutionModes": True}
    return Quartz.CGDisplayCopyAllDisplayModes(display, options) or []


def available_resolutions():
    """Lista de (ancho, alto) únicos disponibles, ordenada de mayor a menor."""
    display = Quartz.CGMainDisplayID()
    res = {
        (int(Quartz.CGDisplayModeGetWidth(m)), int(Quartz.CGDisplayModeGetHeight(m)))
        for m in _all_modes(display)
    }
    return sorted(res, reverse=True)


def current_resolution():
    display = Quartz.CGMainDisplayID()
    mode = Quartz.CGDisplayCopyDisplayMode(display)
    return (
        int(Quartz.CGDisplayModeGetWidth(mode)),
        int(Quartz.CGDisplayModeGetHeight(mode)),
    )


def set_resolution(width, height):
    """Cambia la resolución del monitor principal. Devuelve (ok, mensaje)."""
    display = Quartz.CGMainDisplayID()
    modes = _all_modes(display)

    exact = None
    best = None
    best_dist = None
    for mode in modes:
        w = int(Quartz.CGDisplayModeGetWidth(mode))
        h = int(Quartz.CGDisplayModeGetHeight(mode))
        if w == width and h == height:
            exact = mode
            break
        dist = abs(w - width) + abs(h - height)
        if best_dist is None or dist < best_dist:
            best_dist = dist
            best = mode

    target = exact or best
    if target is None:
        return False, "El monitor no reporta ningún modo de resolución."

    err, config = Quartz.CGBeginDisplayConfiguration(None)
    if err != 0:
        return False, "No se pudo iniciar el cambio de resolución."

    Quartz.CGConfigureDisplayWithDisplayMode(config, display, target, None)
    err = Quartz.CGCompleteDisplayConfiguration(
        config, Quartz.kCGConfigurePermanently
    )
    if err != 0:
        Quartz.CGCancelDisplayConfiguration(config)
        return False, "El sistema rechazó el cambio de resolución."

    aw = int(Quartz.CGDisplayModeGetWidth(target))
    ah = int(Quartz.CGDisplayModeGetHeight(target))
    if exact is None:
        return True, f"No existía {width}×{height}; se aplicó el más cercano: {aw}×{ah}."
    return True, f"Resolución cambiada a {aw}×{ah}."


# --------------------------------------------------------------------------
# Helpers de UI
# --------------------------------------------------------------------------

def make_label(text, x, y, w, h, bold=False, size=13):
    f = NSTextField.alloc().initWithFrame_(NSMakeRect(x, y, w, h))
    f.setStringValue_(text)
    f.setEditable_(False)
    f.setSelectable_(False)
    f.setBezeled_(False)
    f.setDrawsBackground_(False)
    if bold:
        f.setFont_(NSFont.boldSystemFontOfSize_(size))
    else:
        f.setFont_(NSFont.systemFontOfSize_(size))
    return f


def make_field(text, x, y, w, h):
    f = NSTextField.alloc().initWithFrame_(NSMakeRect(x, y, w, h))
    f.setStringValue_(text)
    return f


def make_button(title, x, y, w, h, target, action):
    b = NSButton.alloc().initWithFrame_(NSMakeRect(x, y, w, h))
    b.setTitle_(title)
    b.setBezelStyle_(NSBezelStyleRounded)
    b.setTarget_(target)
    b.setAction_(action)
    return b


def make_big_button(title, x, y, w, h, target, action):
    b = NSButton.alloc().initWithFrame_(NSMakeRect(x, y, w, h))
    b.setTitle_(title)
    b.setBezelStyle_(NSBezelStyleRegularSquare)
    b.setFont_(NSFont.boldSystemFontOfSize_(15))
    b.setAlignment_(NSTextAlignmentCenter)
    b.setTarget_(target)
    b.setAction_(action)
    return b


# --------------------------------------------------------------------------
# Delegado de la app (barra de menú + Dock + ventana)
# --------------------------------------------------------------------------

class AppDelegate(NSObject):

    def applicationDidFinishLaunching_(self, notification):
        self.config = load_config()
        NSApp.setActivationPolicy_(NSApplicationActivationPolicyRegular)
        self._build_status_item()
        self._build_window()
        self._refresh_labels()
        self.showWindow_(None)

    # ---- icono de la barra de menú -------------------------------------

    @objc.python_method
    def _build_status_item(self):
        bar = NSStatusBar.systemStatusBar()
        self.status_item = bar.statusItemWithLength_(NSVariableStatusItemLength)
        self.status_item.button().setTitle_("🖥️")

        menu = NSMenu.alloc().init()

        self.menu_escritorio = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_(
            "Resolución Escritorio", "aplicarEscritorioPreset:", ""
        )
        self.menu_escritorio.setTarget_(self)
        menu.addItem_(self.menu_escritorio)

        self.menu_movil = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_(
            "Resolución Móvil", "aplicarMovilPreset:", ""
        )
        self.menu_movil.setTarget_(self)
        menu.addItem_(self.menu_movil)

        menu.addItem_(NSMenuItem.separatorItem())

        ventana = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_(
            "Abrir ventana…", "showWindow:", ""
        )
        ventana.setTarget_(self)
        menu.addItem_(ventana)

        menu.addItem_(NSMenuItem.separatorItem())

        salir = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_(
            "Salir", "terminate:", "q"
        )
        menu.addItem_(salir)

        self.status_item.setMenu_(menu)

    # ---- ventana --------------------------------------------------------

    @objc.python_method
    def _build_window(self):
        W, H = 420, 400
        style = (
            NSWindowStyleMaskTitled
            | NSWindowStyleMaskClosable
            | NSWindowStyleMaskMiniaturizable
        )
        self.window = NSWindow.alloc().initWithContentRect_styleMask_backing_defer_(
            NSMakeRect(0, 0, W, H), style, NSBackingStoreBuffered, False
        )
        self.window.setTitle_("Resolución")
        self.window.center()
        self.window.setReleasedWhenClosed_(False)
        content = self.window.contentView()

        content.addSubview_(
            make_label("Selecciona una resolución", 20, H - 38, W - 40, 24,
                       bold=True, size=16)
        )

        # --- Dos botones grandes para aplicar de un clic ---
        self.btn_escritorio = make_big_button(
            "", 20, H - 168, 185, 110, self, "aplicarEscritorioPreset:"
        )
        content.addSubview_(self.btn_escritorio)

        self.btn_movil = make_big_button(
            "", 215, H - 168, 185, 110, self, "aplicarMovilPreset:"
        )
        content.addSubview_(self.btn_movil)

        # --- Editar los valores de cada preset ---
        content.addSubview_(
            make_label("Editar valores (se guardan al aplicar):", 20, H - 196,
                       W - 40, 18, size=11)
        )

        content.addSubview_(make_label("Escritorio:", 20, H - 228, 80, 22))
        self.field_escritorio = make_field("1920x1080", 105, H - 230, 110, 24)
        content.addSubview_(self.field_escritorio)
        content.addSubview_(
            make_button("Guardar y aplicar", 230, H - 232, 170, 28, self,
                        "aplicarEscritorio:")
        )

        content.addSubview_(make_label("Móvil:", 20, H - 264, 80, 22))
        self.field_movil = make_field("960x540", 105, H - 266, 110, 24)
        content.addSubview_(self.field_movil)
        content.addSubview_(
            make_button("Guardar y aplicar", 230, H - 268, 170, 28, self,
                        "aplicarMovil:")
        )

        # --- Cualquier otro modo soportado por el monitor ---
        content.addSubview_(make_label("Otro modo:", 20, H - 312, 80, 22))
        self.popup = NSPopUpButton.alloc().initWithFrame_pullsDown_(
            NSMakeRect(105, H - 314, 110, 26), False
        )
        self.popup.addItemsWithTitles_(
            ["{}x{}".format(w, h) for (w, h) in available_resolutions()]
        )
        content.addSubview_(self.popup)
        content.addSubview_(
            make_button("Aplicar selección", 230, H - 314, 170, 28, self,
                        "aplicarPopup:")
        )

        self.current_label = make_label("", 20, 18, W - 40, 20, size=12)
        content.addSubview_(self.current_label)

    # ---- refrescos ------------------------------------------------------

    @objc.python_method
    def _refresh_labels(self):
        e = self.config["escritorio"]
        m = self.config["movil"]
        self.menu_escritorio.setTitle_(
            "Resolución Escritorio ({}×{})".format(e["width"], e["height"])
        )
        self.menu_movil.setTitle_(
            "Resolución Móvil ({}×{})".format(m["width"], m["height"])
        )
        if hasattr(self, "btn_escritorio"):
            self.btn_escritorio.setTitle_(
                "🖥️ Escritorio\n{}×{}".format(e["width"], e["height"])
            )
            self.btn_movil.setTitle_(
                "📱 Móvil\n{}×{}".format(m["width"], m["height"])
            )
        if hasattr(self, "field_escritorio"):
            self.field_escritorio.setStringValue_("{}x{}".format(e["width"], e["height"]))
            self.field_movil.setStringValue_("{}x{}".format(m["width"], m["height"]))
        self._refresh_current()

    @objc.python_method
    def _refresh_current(self):
        if hasattr(self, "current_label"):
            w, h = current_resolution()
            self.current_label.setStringValue_("Resolución actual: {}×{}".format(w, h))

    @objc.python_method
    def _alert(self, titulo, mensaje):
        a = NSAlert.alloc().init()
        a.setMessageText_(titulo)
        a.setInformativeText_(mensaje)
        a.runModal()

    @objc.python_method
    def _aplicar_valor(self, width, height):
        ok, msg = set_resolution(width, height)
        if not ok:
            self._alert("No se pudo cambiar", msg)
        self._refresh_current()
        return ok

    @objc.python_method
    def _aplicar_desde_campo(self, key, field, nombre):
        try:
            width, height = parse_res(field.stringValue())
        except ValueError:
            self._alert("Formato inválido",
                        "Usa el formato ANCHOxALTO, por ejemplo 1920x1080.")
            return
        self.config[key] = {"width": width, "height": height}
        save_config(self.config)
        self._refresh_labels()
        self._aplicar_valor(width, height)

    # ---- acciones (selectores ObjC) ------------------------------------

    def showWindow_(self, sender):
        self._refresh_current()
        self.window.makeKeyAndOrderFront_(None)
        NSApp.activateIgnoringOtherApps_(True)

    def aplicarEscritorio_(self, sender):
        self._aplicar_desde_campo("escritorio", self.field_escritorio, "Escritorio")

    def aplicarMovil_(self, sender):
        self._aplicar_desde_campo("movil", self.field_movil, "Móvil")

    def aplicarEscritorioPreset_(self, sender):
        e = self.config["escritorio"]
        self._aplicar_valor(e["width"], e["height"])

    def aplicarMovilPreset_(self, sender):
        m = self.config["movil"]
        self._aplicar_valor(m["width"], m["height"])

    def aplicarPopup_(self, sender):
        title = self.popup.titleOfSelectedItem()
        if not title:
            return
        try:
            width, height = parse_res(title)
        except ValueError:
            return
        self._aplicar_valor(width, height)

    # Clic en el icono del Dock cuando no hay ventanas visibles
    def applicationShouldHandleReopen_hasVisibleWindows_(self, app, has_visible):
        if not has_visible:
            self.showWindow_(None)
        return True


def main():
    app = NSApplication.sharedApplication()
    delegate = AppDelegate.alloc().init()
    app.setDelegate_(delegate)
    AppHelper.runEventLoop()


if __name__ == "__main__":
    main()
