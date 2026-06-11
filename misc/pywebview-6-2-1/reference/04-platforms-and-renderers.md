# Platforms and Renderers

## Supported Platforms

| Platform | GUI Framework | Web Renderer | Notes |
|----------|--------------|--------------|-------|
| Windows | WinForms | EdgeChromium (default) | Requires .NET Framework 4.6.2+ and WebView2 Runtime |
| Windows | WinForms | CEF (optional) | Chrome 66+, via `pywebview[cef]` |
| Windows | WinForms | MSHTML (deprecated) | IE11, fallback renderer |
| macOS | Cocoa | WebKit.WKWebView | Bundled with OS |
| Linux | GTK | WebKit2 | Requires WebKit2 >= 2.22 |
| Linux | Qt | QtWebEngine / QtWebKit | PyQt6, PyQt5, PySide2, or PySide6 |
| Android | Kivy | WebView | Via buildozer |

## Renderer Selection Order on Windows

1. `edgechromium` — ever-green Chromium (default, requires Edge Runtime)
2. `mshtml` — IE11 MSHTML (fallback, deprecated)

Force a specific renderer:

```python
import webview
webview.start(gui='cef')       # Use CEF
webview.start(gui='edgechromium')  # Use EdgeChromium
webview.start(gui='qt')        # Use Qt (any platform)
webview.start(gui='gtk')       # Use GTK (Linux only)
```

Or via environment variable:

```bash
export PYWEBVIEW_GUI=cef
```

## Installation by Platform

### Windows

```bash
pip install pywebview
```

Dependencies: `pythonnet` (requires .NET 4.0+)

For EdgeChromium: WebView2 Runtime must be installed. Download from Microsoft if not present.

For CEF: `pip install pywebview[cef]`

### macOS

```bash
pip install pywebview
```

Dependencies (PyObjC):

- `pyobjc-core`
- `pyobjc-framework-Cocoa`
- `pyobjc-framework-Quartz`
- `pyobjc-framework-WebKit`
- `pyobjc-framework-security`
- `pyobjc-framework-UniformTypeIdentifiers`

PyObjC comes preinstalled with the Python bundled in macOS. For standalone Python, install separately.

### Linux — GTK

```bash
pip install pywebview[gtk]
```

System dependencies (Ubuntu/Debian):

```bash
sudo apt install python3-gi python3-gi-cairo gir1.2-gtk-3.0 gir1.2-webkit2-4.1
```

WebKit2 version 2.22 or greater is required.

### Linux — Qt

```bash
pip install pywebview[qt]    # PyQt6 + QtWebEngine (recommended)
pip install pywebview[qt5]   # PyQt5
pip install pywebview[pyside6]  # PySide6
pip install pywebview[pyside2]  # PySide2
```

System dependencies (Ubuntu/Debian):

```bash
sudo apt install python3-pyqt5 python3-pyqt5.qtwebengine python3-pyqt5.qtwebchannel libqt5webkit5-dev
```

### Android

```bash
pip install pywebview[android]
```

Build with buildozer. Add to `buildozer.spec`:

```
requirements = python3,kivy,pywebview
android.add_jars = <path_to_pywebview-android.jar>
```

Find the JAR path:

```python
from webview import util
print(util.android_jar_path())
```

## Platform-Specific Limitations

- **QtWebKit** — Debugging is not supported
- **MSHTML** — No external debugger can be attached, deprecated
- **macOS** — `window.native` returns `AppKit.NSWindow`; Y-coordinate is converted from bottom-origin to top-origin for cross-platform consistency
- **GTK** — Window-specific menus are not supported
- **Windows** — Transparent windows are not supported
- **Android** — Python debugging only via logcat (`adb -s <DEVICE_ID> logcat | grep python`)

## WebView2 Runtime Distribution on Windows

Bundle the WebView2 runtime with your application:

```python
import webview
webview.settings['WEBVIEW2_RUNTIME_PATH'] = 'path/to/WebView2Runtime'
```

Supports relative paths resolved from the application entry point, with bundler path resolution support.

## HiDPI / Display Scaling (6.2+)

Screen objects now report proper DPI-aware dimensions:

```python
import webview

for screen in webview.screens:
    print(f'Logical: {screen.width}x{screen.height}')
    print(f'Physical: {screen.physical_width}x{screen.physical_height}')
    print(f'Scale: {screen.scale}, DPI: {screen.dpi}')
```
