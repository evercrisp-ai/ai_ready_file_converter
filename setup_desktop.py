"""
py2app setup script for AI Ready File Converter desktop application.

Build the macOS app with:
    python setup_desktop.py py2app

For development/testing:
    python setup_desktop.py py2app -A
"""

import sys
from pathlib import Path
from setuptools import setup

# Ensure we're on macOS
if sys.platform != "darwin":
    print("Error: py2app only works on macOS", file=sys.stderr)
    sys.exit(1)

APP = ["desktop_app.py"]
APP_NAME = "AI Ready File Converter"
APP_VERSION = "1.0.0"

# Data files to include in the bundle
DATA_FILES = [
    ("templates", ["templates/index.html"]),
    ("static/css", ["static/css/style.css"]),
    ("static/js", ["static/js/app.js"]),
]

# Packages to include
PACKAGES = [
    "uvicorn",
    "fastapi",
    "starlette",
    "pydantic",
    "pydantic_core",
    "jinja2",
    "multipart",
    "PIL",
    "docx",
    "pdfplumber",
    "pptx",
    "openpyxl",
    "openai",
    "anthropic",
    "httpx",
    "httpcore",
    "anyio",
    "sniffio",
    "certifi",
    "idna",
    "charset_normalizer",
    "converters",
    "converters.vision",
]

# Try to include pytesseract if available
try:
    import pytesseract
    PACKAGES.append("pytesseract")
except ImportError:
    pass

# Skip google-generativeai - namespace packages cause py2app issues
# The app will work without Google AI features

OPTIONS = {
    "argv_emulation": False,
    "iconfile": "resources/icon.icns" if Path("resources/icon.icns").exists() else None,
    "plist": {
        "CFBundleName": APP_NAME,
        "CFBundleDisplayName": APP_NAME,
        "CFBundleIdentifier": "com.aiready.fileconverter",
        "CFBundleVersion": APP_VERSION,
        "CFBundleShortVersionString": APP_VERSION,
        "NSHighResolutionCapable": True,
        "NSRequiresAquaSystemAppearance": False,  # Support dark mode
        "LSMinimumSystemVersion": "10.15",
        "CFBundleDocumentTypes": [
            {
                "CFBundleTypeName": "PDF Document",
                "CFBundleTypeExtensions": ["pdf"],
                "CFBundleTypeRole": "Viewer",
            },
            {
                "CFBundleTypeName": "Word Document",
                "CFBundleTypeExtensions": ["docx", "doc"],
                "CFBundleTypeRole": "Viewer",
            },
            {
                "CFBundleTypeName": "Excel Spreadsheet",
                "CFBundleTypeExtensions": ["xlsx", "xls", "csv"],
                "CFBundleTypeRole": "Viewer",
            },
            {
                "CFBundleTypeName": "PowerPoint Presentation",
                "CFBundleTypeExtensions": ["pptx", "ppt"],
                "CFBundleTypeRole": "Viewer",
            },
            {
                "CFBundleTypeName": "Image",
                "CFBundleTypeExtensions": ["png", "jpg", "jpeg", "gif", "bmp", "tiff", "tif", "webp"],
                "CFBundleTypeRole": "Viewer",
            },
        ],
    },
    "packages": PACKAGES,
    "includes": [
        "main",
        "webview",
        "uvicorn.logging",
        "uvicorn.loops",
        "uvicorn.loops.auto",
        "uvicorn.protocols",
        "uvicorn.protocols.http",
        "uvicorn.protocols.http.auto",
        "uvicorn.protocols.websockets",
        "uvicorn.protocols.websockets.auto",
        "uvicorn.lifespan",
        "uvicorn.lifespan.on",
    ],
    "excludes": [
        "tkinter",
        "matplotlib",
        "numpy",
        "scipy",
        "pandas",
        "test",
        "tests",
        "unittest",
        "google",
        "google.generativeai",
        "google.ai",
        "google.auth",
        "google.api_core",
        "grpc",
        "grpcio",
        "uvloop",  # uvloop C extensions don't work properly in py2app bundle
    ],
    "site_packages": True,
    "strip": True,
    "optimize": 2,
}

# Remove None iconfile if not present
if OPTIONS["iconfile"] is None:
    del OPTIONS["iconfile"]

setup(
    name=APP_NAME,
    version=APP_VERSION,
    app=APP,
    data_files=DATA_FILES,
    options={"py2app": OPTIONS},
    setup_requires=["py2app"],
)
