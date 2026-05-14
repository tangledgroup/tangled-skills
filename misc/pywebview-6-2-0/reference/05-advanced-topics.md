# Advanced Topics

## Freezing / Bundling

pywebview is designed to work with popular Python bundlers without adding significant size overhead.

### PyInstaller (Windows / Linux)

Basic packaging with local HTML:

```bash
pyinstaller main.py --add-data index.html:.
```

Single-file build:

```bash
pyinstaller main.py --add-data index.html:. --onefile
```

With a JavaScript framework build output:

```bash
pyinstaller main.py --add-data dist_output:.
```

**Linux note:** If you get a `cannot find python3.xx.so` error, add the shared library:

```bash
pyinstaller main.py --add-data index.html:. --add-binary /usr/lib/x86_64-linux-gnu/libpython3.x.so:. --onefile
```

PyInstaller picks up all dependencies found in pywebview even if unused. Exclude unwanted backends in your `.spec` file's `excludes` list (e.g., exclude `PyQt5` if using EdgeChromium on Windows).

### Nuitka

```bash
python -m nuitka --standalone main.py
```

Use `--nofollow-import-to` to exclude unwanted dependencies.

### py2app (macOS)

Use py2app for macOS distribution. Reference `setup.py` configurations are available in the pywebview repository.

### Android (buildozer)

See Platforms and Renderers section for buildozer configuration.

## Security

### SSL for Local HTTP Server

Enable SSL encryption between the webview and internal server:

```python
import webview
webview.start(ssl=True)
```

Requires the `cryptography` package: `pip install pywebview[ssl]`.

### CSRF Protection

pywebview generates a session-unique token accessible as `webview.token` (Python) and `window.pywebview.token` (JavaScript). Include this token in API requests to prevent CSRF attacks:

```python
from flask import Flask, request
import webview

app = Flask(__name__)

@app.route('/api/action', methods=['POST'])
def action():
    # Validate CSRF token
    if request.headers.get('X-CSRF-Token') != webview.token:
        return 'Unauthorized', 403
    return 'OK'

webview.create_window('Secure App', app)
webview.start(ssl=True)
```

### Private Mode

By default, pywebview runs in private mode — cookies and localStorage are not persisted between sessions:

```python
# Default: private_mode=True (no persistence)
webview.start(private_mode=True)

# Disable private mode to persist data
webview.start(private_mode=False, storage_path='/path/to/storage')
```

## Debugging

### JavaScript Debugging

Enable debug mode:

```python
import webview
webview.create_window('Debug', 'https://example.com')
webview.start(debug=True)
```

This enables:

- Web Inspector on macOS (right-click → Inspect), GTK, and Qt (QtWebEngine only)
- JavaScript error reporting
- Right-click context menu

Disable auto-opening of DevTools:

```python
webview.settings['OPEN_DEVTOOLS_IN_DEBUG'] = False
```

### Remote Debugging (EdgeChromium / Qt)

```python
import webview
webview.settings['REMOTE_DEBUGGING_PORT'] = 9222
webview.start()
```

Then open `chrome://inspect` in Chrome/Edge to debug the webview.

### Python Logging

Set the `PYWEBVIEW_LOG` environment variable for pywebview's internal debug logging:

```bash
PYWEBVIEW_LOG=debug python main.py
```

This takes precedence over the `debug` parameter for log level.

## Built-in HTTP Server

pywebview uses Bottle internally as its HTTP server. It starts automatically for relative local paths and cannot be disabled for those cases.

### Automatic Mode (Relative Paths)

```python
# HTTP server starts automatically, serves everything under 'src/'
webview.create_window('App', 'src/index.html')
```

### Absolute Paths

Enable explicitly with `http_server=True`:

```python
webview.create_window('App', '/absolute/path/index.html')
webview.start(http_server=True)
```

### Custom Port

```python
webview.start(http_port=8080)
```

### External WSGI Server

Pass any WSGI-compatible application as the URL:

```python
from flask import Flask, render_template
import webview

app = Flask(__name__, static_folder='./assets', template_folder='./templates')

@app.route('/')
def index():
    return render_template('index.html')

webview.create_window('Flask App', app)
webview.start()
```

FastAPI and other WSGI/ASGI frameworks work similarly.

### Multiple Servers

Each window gets its own HTTP server instance. For multiple windows with different roots, each serves independently.

## Native File Dialogs

```python
import webview

window = webview.create_window('Dialogs', html='<h1>Test</h1>')

# Open file dialog
files = window.create_file_dialog(
    dialog_type=webview.FileDialog.OPEN,
    directory='/tmp',
    allow_multiple=True,
    file_types=('Text Files (*.txt;*.md)', 'All Files (*.*)')
)

# Save file dialog
result = window.create_file_dialog(
    dialog_type=webview.FileDialog.SAVE,
    save_filename='output.txt',
    file_types=('Text Files (*.txt)',)
)

# Folder dialog
folder = window.create_file_dialog(
    dialog_type=webview.FileDialog.FOLDER,
    directory='/home'
)
```

## Frameless Windows and Drag Regions

Create a frameless window (no title bar or chrome):

```python
window = webview.create_window('Frameless', html='...', frameless=True, easy_drag=True)
```

For fine-grained drag control, add the class `pywebview-drag-region` to specific elements:

```html
<div class='pywebview-drag-region'>Drag here to move window</div>
```

Override the default selector:

```python
webview.settings['DRAG_REGION_SELECTOR'] = '.my-custom-drag-area'
```

## Window State Management

```python
# Check current state
state = window.state  # Shared state object (6.0+)

# Window lifecycle events
window.events.minimized += lambda: print('Minimized')
window.events.maximized += lambda: print('Maximized')
window.events.restored += lambda: print('Restored')
```

## Localization

Override default UI strings:

```python
import webview

localization = {
    'close_confirmation': 'Are you sure?',
    'ok_button': 'Yes',
    'cancel_button': 'No'
}

webview.start(localization=localization)
```

Per-window localization:

```python
window = webview.create_window('App', html='...', localization=localization)
```

## Multiprocess Architecture (6.2+)

pywebview 6.2 includes a multiprocess example demonstrating non-blocking multi-process architecture. This pattern is useful for long-running backend tasks that should not block the GUI thread.

## User Agent

Customize the browser user agent:

```python
webview.start(user_agent='MyApp/1.0 (Windows NT 10.0; Win64; x64)')
```

## Icons

Set application icon programmatically:

```python
webview.start(icon='path/to/icon.ico')  # .ico on Windows, .icns on macOS, .png on Linux
```

Generally icons should be specified during bundling rather than at runtime.
