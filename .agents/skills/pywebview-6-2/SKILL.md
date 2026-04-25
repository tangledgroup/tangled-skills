---
name: pywebview-6-2
description: A skill for building cross-platform desktop applications with native webview components using pywebview 6.2, enabling HTML/CSS/JavaScript UIs in Python applications with two-way Python-JavaScript communication, window management, and built-in HTTP server capabilities. Use when creating desktop GUI applications, wrapping web interfaces in native windows, or building hybrid applications that combine Python backend logic with modern web frontend technologies on Windows, macOS, Linux, and Android.
version: "0.2.0"
author: Tangled <noreply@tangledgroup.com>
license: MIT
tags:
  - python
  - desktop-gui
  - webview
  - cross-platform
  - native-apps
  - javascript-bridge
  - html-ui
category: development
required_environment_variables: []

external_references:
  - https://pywebview.flowrl.com/
  - https://github.com/r0x0r/pywebview
---

# pywebview 6.2


## Core Concepts

This skill covers the key concepts and fundamental ideas related to this topic.
## Overview

A skill for building cross-platform desktop applications with native webview components using pywebview 6.2, enabling HTML/CSS/JavaScript UIs in Python applications with two-way Python-JavaScript communication, window management, and built-in HTTP server capabilities. Use when creating desktop GUI applications, wrapping web interfaces in native windows, or building hybrid applications that combine Python backend logic with modern web frontend technologies on Windows, macOS, Linux, and Android.

pywebview is a lightweight BSD-licensed cross-platform wrapper around native webview components that allows displaying HTML content in native GUI windows. It provides the power of web technologies (HTML, CSS, JavaScript) in desktop applications while hiding the browser-based nature of the GUI. pywebview ships with a built-in HTTP server, DOM support in Python, and comprehensive window management functionality.

**Key capabilities:**
- Cross-platform support (Windows, macOS, Linux, Android)
- Two-way JavaScript ↔ Python communication without HTTP/REST
- Built-in HTTP server for serving static files
- Window management (size, position, title, multiple windows)
- Native GUI components (menus, dialogs, message boxes)
- DOM manipulation from Python
- Drag-and-drop file support
- Bundler-friendly (PyInstaller, Nuitka, py2app)

## When to Use

- Building desktop applications with web-based UIs
- Creating native wrappers for existing web applications
- Developing hybrid apps with Python backend and JavaScript frontend
- Needing cross-platform GUI without learning platform-specific toolkits
- Requiring two-way communication between Python and JavaScript
- Building simple browsers or kiosk applications
- Creating tools that benefit from modern CSS frameworks (React, Vue, etc.)

## Setup

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

See [Installation Details](references/01-installation.md) for complete platform requirements.

## Quick Start

### Hello World

```python
import webview

window = webview.create_window('Hello World', 'https://pywebview.flowrl.com')
webview.start()
```

### Load Local HTML

```python
import webview

# Serve local files with built-in HTTP server
window = webview.create_window('My App', './index.html')
webview.start()
```

### Inline HTML

```python
import webview

html_content = '''
<html>
  <body>
    <h1>Hello from inline HTML!</h1>
  </body>
</html>
'''
window = webview.create_window('Inline', html=html_content)
webview.start()
```

### Python-JavaScript Communication

See [JS API Integration](references/02-js-api.md) for detailed examples.

## Common Operations

### Window Management

Create and manage multiple windows:

```python
import webview

# Create first window
first = webview.create_window('First Window', 'https://example.com', width=800, height=600)

# Create second window
second = webview.create_window('Second Window', 'https://google.com', x=100, y=100)

# Access all windows
print(f'Total windows: {len(webview.windows)}')

# Get active (focused) window
active = webview.active_window()
print(f'Active window: {active.title}')

# Control window
active.toggle_fullscreen()
active.resize(1024, 768)
active.move(50, 50)
active.minimize()
active.show()
active.hide()
active.destroy()  # Close window
```

See [Window API Reference](references/03-window-api.md) for complete methods.

### Event Handling

Subscribe to window events:

```python
import webview

def on_shown(window):
    print(f'Window shown: {window.title}')

def on_closing(window):
    print(f'Window closing: {window.title}')
    return True  # Allow close (False would prevent it)

def on_loaded(window):
    print('Page loaded')

window = webview.create_window('Events Demo', 'https://example.com')
window.events.shown += on_shown
window.events.closing += on_closing
window.events.loaded += on_loaded

webview.start()
```

Available events: `closed`, `closing`, `loaded`, `before_load`, `before_show`, `shown`, `minimized`, `maximized`, `restored`, `resized`, `moved`

### JavaScript Execution

Execute JavaScript from Python:

```python
import webview

window = webview.create_window('JS Demo', html='<h1 id="title">Hello</h1>')

# Synchronous execution (returns result)
result = window.evaluate_js('document.getElementById("title").innerText')
print(result)  # Output: Hello

# Execute without return value
window.run_js('console.log("No return value")')

# Async execution with callback
def handle_result(result):
    print(f'Promise resolved: {result}')

window.evaluate_js('fetch("https://api.example.com/data")', handle_result)

# Error handling
try:
    window.evaluate_js('nonExistentFunction()')
except webview.errors.JavascriptException as e:
    print(f'JavaScript error: {e}')
```

See [JavaScript Integration](references/02-js-api.md) for complete guide.

### Native Dialogs

Use native system dialogs:

```python
import webview

# Message box
result = webview.MessageBox.show('Title', 'Message', webview.MessageBoxType.INFO)

# Confirmation dialog
if webview.MessageBox.yes_no('Confirm', 'Are you sure?'):
    print('User clicked Yes')

# File open dialog
files = webview.FileDialog.open(
    title='Open files',
    directory='/home/user',
    filters=[
        ('Python files', '*.py'),
        ('All files', '*.*')
    ]
)

# File save dialog
filepath = webview.FileDialog.save(
    title='Save file',
    directory='/home/user',
    filename='output.txt',
    filters=[('Text files', '*.txt')]
)
```

See [Dialog API](references/04-native-components.md) for all dialog types.

### Native Menus

Create application menus:

```python
import webview

# Create menu items
quit_item = webview.MenuItem('Quit', callback=lambda: webview.windows[0].destroy())
about_item = webview.MenuItem('About', callback=lambda: webview.MessageBox.show('About', 'pywebview demo'))

# Create menu with items
menu = webview.Menu(items=[
    webview.MenuItem('File', items=[
        webview.MenuItem('New'),
        webview.MenuItem('Open'),
        webview.MenuItem('Save'),
        webview.MenuItem.separator(),
        quit_item
    ]),
    webview.MenuItem('Help', items=[about_item])
])

# Create window with menu
window = webview.create_window('Menu Demo', 'https://example.com', menu=menu)
webview.start()
```

See [Menu API](references/04-native-components.md) for complete menu system.

## Application Architecture

Choose from three architectural patterns:

### 1. Pure Web Server (External)

Point to remote or local web server:

```python
import webview
from flask import Flask

# Remote URL
window = webview.create_window('Browser', 'https://example.com')

# Local Flask server
app = Flask(__name__, static_folder='static', template_folder='templates')

@app.route('/')
def index():
    return app.send_static_file('index.html')

window = webview.create_window('Flask App', app)
webview.start()
```

### 2. JS API with Internal HTTP Server (Recommended)

Use built-in server for static files + direct Python-JS communication:

```python
import webview

class Api:
    def get_data(self):
        return {'message': 'Hello from Python!'}
    
    def log(self, value):
        print(f'JavaScript says: {value}')

# Serve local files with JS API bridge
window = webview.create_window(
    'Hybrid App',
    './index.html',  # Built-in server serves this
    js_api=Api()     # Expose to JavaScript
)
webview.start()
```

JavaScript usage:
```javascript
// Call Python function
pywebview.api.get_data().then(result => {
    console.log(result.message);
});

// Send data to Python
pywebview.api.log('Hello from JavaScript!');
```

See [JS API Integration](references/02-js-api.md) for complete guide.

### 3. Serverless (Inline HTML)

Load HTML directly without any server:

```python
import webview

html = '''
<!DOCTYPE html>
<html>
<head>
    <style>body { font-family: sans-serif; }</style>
</head>
<body>
    <h1>Serverless App</h1>
    <button onclick="pywebview.api.alert()">Click me</button>
    <script>
        pywebview.api.alert = () => alert('Hello from Python!');
    </script>
</body>
</html>
'''

class Api:
    def alert(self):
        webview.MessageBox.show('Alert', 'Hello from Python!')

window = webview.create_window('Serverless', html=html, js_api=Api())
webview.start()
```

**Limitations:** No file system access, assets must be inline/Base64.

See [Architecture Patterns](references/01-installation.md) for detailed comparison.

## Backend Logic Execution

Since `webview.start()` blocks until all windows close, run backend code in separate threads:

### Method 1: Pass function to start()

```python
import webview
import time

def background_task(window):
    while True:
        time.sleep(5)
        window.evaluate_js('updateStatus("Still running...")')

window = webview.create_window('Background Task', './index.html')
webview.start(background_task, window)
```

### Method 2: Manual threading

```python
import webview
import threading
import time

def background_worker():
    while True:
        time.sleep(1)
        # Update UI from main thread
        webview.windows[0].evaluate_js('updateCounter()')

window = webview.create_window('Worker', './index.html')
thread = threading.Thread(target=background_worker, daemon=True)
thread.start()
webview.start()
```

### Method 3: Async/await with asyncio

```python
import webview
import asyncio

async def async_task(window):
    while True:
        await asyncio.sleep(5)
        window.evaluate_js('fetchNewData()')

window = webview.create_window('Async', './index.html')
webview.start(lambda w: asyncio.run(async_task(w)), window)
```

## Troubleshooting

### Common Issues

**"Module not found" errors on Linux:**
- Install platform-specific dependencies (see Installation section)
- Try alternative GUI backends: `pip install pywebview[gtk]` or `pywebview[qt]`

**WebView2 Runtime missing on Windows:**
- Download from: https://developer.microsoft.com/en-us/microsoft-edge/webview2/
- Or use CEF backend: `pip install pywebview[cef]`

**HTTPS errors with local server:**
- Install SSL support: `pip install pywebview[ssl]`
- Or use HTTP for development

**JavaScript exceptions not caught:**
- Wrap `evaluate_js()` calls in try/except blocks
- Catch `webview.errors.JavascriptException`

**Window appears blank:**
- Check console for JavaScript errors
- Verify file paths are correct (relative to application entry point)
- Try loading a remote URL first to confirm pywebview works

See [Debugging Guide](references/05-debugging.md) for detailed troubleshooting.

## Reference Files

- [`references/01-installation.md`](references/01-installation.md) - Complete installation guide, platform dependencies, and architecture patterns
- [`references/02-js-api.md`](references/02-js-api.md) - JavaScript-Python communication, API exposure, and interdomain messaging
- [`references/03-window-api.md`](references/03-window-api.md) - Complete Window object methods, properties, and event handlers
- [`references/04-native-components.md`](references/04-native-components.md) - Menus, dialogs, and native GUI element APIs
- [`references/05-debugging.md`](references/05-debugging.md) - Debugging techniques, remote debugging, and troubleshooting

**Note:** `{baseDir}` refers to the skill's base directory (`.agents/skills/pywebview-6-2/`). All paths are relative to this directory.

## Examples

See the official pywebview repository for complete examples:
- https://github.com/r0x0r/pywebview/tree/master/examples

Notable examples:
- **todos** - Serverless app with JS API
- **flask_app** - Flask integration
- **simple_browser** - Basic browser implementation
- **multiple_windows** - Window management demo
- **menu_demo** - Native menu system

## Additional Resources

- **Official Documentation:** https://pywebview.flowrl.com/
- **GitHub Repository:** https://github.com/r0x0r/pywebview
- **Changelog:** https://pywebview.flowrl.com/changelog
- **Contributing Guidelines:** https://pywebview.flowrl.com/contributing
- **React Boilerplate:** https://github.com/r0x0r/pywebview-react-boilerplate

## Security Considerations

When using local web servers, protect API endpoints against CSRF attacks. Enable HTTPS for production applications with sensitive data. Validate all JavaScript input from untrusted sources. See [Security Guide](references/05-debugging.md) for detailed security recommendations.

## Advanced Topics

For more details on advanced usage, refer to the official documentation listed in the References section.
