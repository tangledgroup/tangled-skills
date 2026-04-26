---
name: pywebview-6-2
description: Cross-platform wrapper around native webview components that lets Python applications display HTML content in a native GUI window. Use when building desktop applications with web-based UIs on Windows, macOS, Linux, or Android — including two-way JavaScript↔Python communication, DOM manipulation from Python, built-in HTTP server, window management, and bundler-friendly packaging.
license: BSD-3-Clause
author: Tangled <noreply@tangledgroup.com>
version: "6.2"
tags:
  - python
  - gui
  - webview
  - desktop
  - cross-platform
  - html
  - javascript
category: gui-framework
external_references:
  - https://pywebview.flowrl.com/
  - https://github.com/r0x0r/pywebview
---

# pywebview 6.2

## Overview

pywebview is a lightweight BSD-licensed cross-platform wrapper around native webview components. It displays HTML content in its own native GUI window, giving you the power of web technologies in a desktop application while hiding the fact that the UI is browser-based.

Key capabilities:

- **Cross-platform** — Windows (WinForms/EdgeChromium/CEF), macOS (Cocoa/WebKit), Linux (GTK or Qt), Android (Kivy)
- **Two-way JavaScript↔Python communication** — call Python from JS and JS from Python without HTTP
- **Built-in HTTP server** — serves local files automatically via Bottle
- **DOM support in Python** — manipulate and traverse DOM nodes without JavaScript
- **Window management** — size, position, fullscreen, frameless, multi-window
- **Native components** — menus, file dialogs, confirmation dialogs
- **Bundler-friendly** — works with PyInstaller, Nuitka, py2app
- **Shared state** (new in 6.0) — reactive state object synced between Python and JavaScript

pywebview does not bundle a heavy GUI toolkit or web renderer, keeping frozen executables small.

Requires Python 3.8+.

## When to Use

- Building desktop applications with HTML/CSS/JavaScript UIs
- Wrapping existing web applications in a native window
- Creating tools that need two-way communication between Python backend and JavaScript frontend
- Prototyping GUIs quickly with web technologies
- Building cross-platform desktop apps without learning platform-specific GUI frameworks
- Distributing Python apps with embedded web content via PyInstaller, Nuitka, or py2app

## Installation

```bash
pip install pywebview
```

On Linux, choose a backend explicitly:

```bash
pip install pywebview[gtk]   # GTK + WebKit2
pip install pywebview[qt]    # PyQt6 + QtWebEngine
pip install pywebview[qt5]   # PyQt5
pip install pywebview[pyside6]  # PySide6
```

Optional extras:

- `pywebview[cef]` — CEF renderer (Windows only)
- `pywebview[ssl]` — SSL support for local HTTP server
- `pywebview[android]` — Android support

## Hello World

```python
import webview

webview.create_window('Hello world', 'https://pywebview.flowrl.com/')
webview.start()
```

## Core Concepts

### Application Lifecycle

1. **Create windows** with `webview.create_window()` before or during the GUI loop
2. **Start the GUI loop** with `webview.start()` — this blocks until all windows are closed
3. **Backend logic** runs in a separate thread via `webview.start(func, *args)`

```python
import webview

def backend_logic(window):
    """Runs in a separate thread after the GUI loop starts."""
    window.toggle_fullscreen()

window = webview.create_window('My App', html='<h1>Hello</h1>')
webview.start(backend_logic, window)
# Code below runs only after all windows are closed
```

### Content Loading

Three ways to load content into a window:

- **URL** — remote or local path (relative paths auto-start HTTP server)
- **HTML string** — inline HTML content
- **WSGI app** — pass a Flask/FastAPI app object directly

```python
# Remote URL
webview.create_window('Docs', 'https://pywebview.flowrl.com/')

# Inline HTML
webview.create_window('Inline', html='<h1>Hello</h1>')

# Local files (HTTP server starts automatically for relative paths)
webview.create_window('Local', 'src/index.html')

# WSGI app
from flask import Flask
app = Flask(__name__, static_folder='./assets')
webview.create_window('Flask', app)
```

### Multiple Windows

Create as many windows as needed. All windows are tracked in `webview.windows`:

```python
import webview

first = webview.create_window('First', 'https://example.com')
second = webview.create_window('Second', 'https://other.com')

# Access the currently focused window
active = webview.active_window()
print(f'Active: {active.title}')
print(f'Total windows: {len(webview.windows)}')

webview.start()
```

### Settings

Global settings override default behavior via `webview.settings`:

```python
import webview

webview.settings['ALLOW_DOWNLOADS'] = True
webview.settings['OPEN_EXTERNAL_LINKS_IN_BROWSER'] = False
webview.settings['IGNORE_SSL_ERRORS'] = True
```

Available settings:

- `ALLOW_DOWNLOADS` — allow file downloads (default: False)
- `ALLOW_FILE_URLS` — enable `file://` URLs (default: False)
- `DRAG_REGION_SELECTOR` — CSS selector for drag region in frameless windows
- `DRAG_REGION_DIRECT_TARGET_ONLY` — only direct matches are draggable
- `OPEN_EXTERNAL_LINKS_IN_BROWSER` — open `target=_blank` links externally (default: True)
- `OPEN_DEVTOOLS_IN_DEBUG` — auto-open DevTools in debug mode (default: True)
- `IGNORE_SSL_ERRORS` — ignore SSL certificate errors (default: False)
- `REMOTE_DEBUGGING_PORT` — port for remote debugging (edgechromium/qt)
- `SHOW_DEFAULT_MENUS` — show default menus on macOS (default: True)
- `WEBVIEW2_RUNTIME_PATH` — path to bundled WebView2 runtime

## Usage Examples

### Basic Window with Events

```python
import webview

def on_closing():
    print('Window is about to close')

def on_loaded(window):
    print(f'Page loaded: {window.get_current_url()}')

window = webview.create_window('My App', 'https://example.com')
window.events.closing += on_closing
window.events.loaded += lambda: on_loaded(window)
webview.start()
```

### JavaScript to Python Communication

```python
import webview

class Api:
    def greet(self, name):
        return f'Hello, {name}!'

    def add(self, a, b):
        return a + b

html = '''
<button onclick="callPython()">Call Python</button>
<script>
  window.addEventListener('pywebviewready', () => {
    pywebview.api.greet('World').then(result => alert(result));
  });
</script>
'''

webview.create_window('JS API', html=html, js_api=Api())
webview.start()
```

### Shared State (6.0+)

```python
import webview

html = '''
<button onclick="pywebview.state.counter++">Increment</button>
<span id="counter"></span>
<script>
  window.addEventListener('pywebviewready', () => {
    pywebview.state.addEventListener('change', e => {
      document.getElementById('counter').innerText = pywebview.state.counter;
    });
  });
</script>
'''

def on_change(event_type, key, value):
    print(f'{event_type}: {key} = {value}')

window = webview.create_window('State', html=html)
window.state.counter = 0
window.state += on_change
webview.start()
```

### Window with SSL and Custom User Agent

```python
import webview

webview.create_window('Secure', 'src/index.html')
webview.start(ssl=True, user_agent='MyApp/1.0')
```

## Advanced Topics

**Full API Reference**: `create_window`, `start`, `Window` methods, events → [API Reference](reference/01-api-reference.md)

**JavaScript↔Python Bridge**: JS API, expose, shared state, evaluate_js, run_js → [JavaScript-Python Bridge](reference/02-javascript-python-bridge.md)

**DOM Support**: Element manipulation, traversal, events from Python → [DOM Support](reference/03-dom-support.md)

**Platforms and Renderers**: Web engines per platform, installation, dependencies → [Platforms and Renderers](reference/04-platforms-and-renderers.md)

**Advanced Topics**: Freezing/bundling, security, debugging, HTTP server, menus, file dialogs → [Advanced Topics](reference/05-advanced-topics.md)
