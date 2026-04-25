# Setup

### Installation

Install pywebview with pip:

```bash
pip install pywebview
```

This installs pywebview with default dependencies for each platform.

### Platform-Specific Installation

**Linux - GTK:**
```bash
pip install pywebview[gtk]
```

**Linux - Qt (default):**
```bash
pip install pywebview[qt]  # Installs PyQT6
```

**Linux - Alternative Qt options:**
```bash
pip install pywebview[qt5]      # PyQt5
pip install pywebview[pyside2]  # PySide2
pip install pywebview[pyside6]  # PySide6
```

**Linux - System dependencies (Debian/Ubuntu):**
```bash
# For QtWebEngine (modern, preferred)
sudo apt install python3-pyqt5 python3-pyqt5.qtwebengine python3-pyqt5.qtwebchannel libqt5webkit5-dev

# For QtWebKit (legacy, more platforms)
sudo apt install python3-qtwebkit
```

**Optional dependencies:**
```bash
pip install pywebview[android]  # Android support
pip install pywebview[cef]      # Chromium Embedded Framework (Windows only)
pip install pywebview[ssl]      # HTTPS support for local server
```

### Platform Dependencies

| Platform | Required Dependencies |
|----------|---------------------|
| **Windows** | pythonnet (.NET 4.0+), WebView2 Runtime (for latest Chromium), or cefpython (for CEF) |
| **macOS** | pyobjc-core, pyobjc-framework-Cocoa, pyobjc-framework-Quartz, pyobjc-framework-WebKit, pyobjc-framework-security |
| **Linux** | PyQt5/PyQt6 with QtWebEngine or GTK3 libraries |

See [Installation Details](reference/01-installation.md) for complete platform requirements.
