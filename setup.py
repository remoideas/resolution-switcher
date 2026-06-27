"""
Empaqueta ResolutionSwitcher como una app nativa de macOS (.app) con py2app.

Uso:
    ./construir-app.sh
o manualmente:
    .venv/bin/python setup.py py2app
El resultado queda en dist/ResolutionSwitcher.app
"""

from setuptools import setup

APP = ["resolucion.py"]

OPTIONS = {
    "argv_emulation": False,
    "plist": {
        "CFBundleName": "ResolutionSwitcher",
        "CFBundleDisplayName": "ResolutionSwitcher",
        "CFBundleIdentifier": "com.remoideas.resolutionswitcher",
        "CFBundleVersion": "1.0.0",
        "CFBundleShortVersionString": "1.0.0",
        "LSMinimumSystemVersion": "10.13",
        "NSHumanReadableCopyright": "© 2026 Antonio Reyes — MIT License",
    },
    # PyObjC trae los frameworks que usamos (Cocoa/Quartz).
    "packages": ["objc", "Cocoa", "Quartz"],
}

setup(
    app=APP,
    name="ResolutionSwitcher",
    options={"py2app": OPTIONS},
    setup_requires=["py2app"],
)
