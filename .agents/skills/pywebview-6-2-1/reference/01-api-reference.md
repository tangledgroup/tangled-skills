# API Reference

## webview.create_window

Create a new pywebview window and return its instance. Windows created before `webview.start()` are shown when the GUI loop starts. Windows created during the GUI loop are shown immediately.

```python
window = webview.create_window(
    title,
    url=None,
    html=None,
    js_api=None,
    width=800,
    height=600,
    x=None,
    y=None,
    screen=None,
    resizable=True,
    fullscreen=False,
    min_size=(200, 100),
    hidden=False,
    frameless=False,
    easy_drag=True,
    shadow=False,
    focus=True,
    minimized=False,
    maximized=False,
    menu=[],
    on_top=False,
    confirm_close=False,
    background_color='#FFFFFF',
    transparent=False,
    text_select=False,
    zoomable=False,
    draggable=False,
    vibrancy=False,
    server=http.BottleServer,
    server_args={},
    localization=None
)
```

### Parameters

**title** — Window title string.

**url** — URL to load. Without a protocol prefix, resolved as a path relative to the application entry point. Alternatively pass a WSGI server object.

**html** — HTML code to load. Takes precedence over `url` if both are specified.

**js_api** — Python object instance to expose to JavaScript. Methods available as `window.pywebview.api.methodName()`. Only basic Python types (int, str, dict, list) can be returned to JS.

**width / height** — Window dimensions in logical pixels. Defaults: 800×600.

**x / y** — Window position in logical pixels. Default: centered on screen.

**screen** — Screen instance from `webview.screens` to display the window on.

**resizable** — Whether window can be resized. Default: True.

**fullscreen** — Start in fullscreen mode. Default: False.

**min_size** — Tuple `(width, height)` for minimum window size. Default: (200, 100).

**hidden** — Create window hidden by default. Default: False.

**frameless** — Create a frameless window (no title bar/chrome). Default: False.

**easy_drag** — For frameless windows, allow dragging from any point. Default: True. Has no effect on normal windows.

**shadow** — Add window shadow. Windows only. Default: False.

**focus** — Create a focusable window. Set to False for non-focusable overlays. Default: True.

**minimized / maximized** — Initial window state.

**menu** — List of `webview.menu.Menu` objects for a window-specific menu. Overrides application menu from `webview.start()`. Not supported on GTK.

**on_top** — Always-on-top window. Default: False.

**confirm_close** — Show confirmation dialog before closing. Default: False.

**background_color** — Hex color shown before WebView loads. Default: '#FFFFFF'.

**transparent** — Transparent window background. Not supported on Windows. Default: False. Does not hide chrome — set `frameless=True` for that.

**text_select** — Enable text selection in the document. Default: False. Use CSS `user-select` for per-element control.

**zoomable** — Enable document zooming. Default: False.

**draggable** — Enable image and link object dragging. Default: False.

**vibrancy** — Enable window vibrancy effect. macOS only. Default: False.

**server** — Custom WSGI server instance for this window. Default: BottleServer.

**server_args** — Dictionary of arguments passed to server instantiation.

**localization** — Per-window localization dictionary.

## webview.start

Start the GUI loop and display previously created windows. Must be called from the main thread. Blocks until all windows are destroyed.

```python
webview.start(
    func=None,
    args=None,
    localization={},
    gui=None,
    debug=False,
    http_server=False,
    http_port=None,
    user_agent=None,
    private_mode=True,
    storage_path=None,
    menu=[],
    server=http.BottleServer,
    ssl=False,
    server_args={},
    icon=None
)
```

### Parameters

**func** — Function to invoke in a separate thread upon starting the GUI loop.

**args** — Arguments for `func`. Single value or tuple.

**localization** — Dictionary with localized strings. Keys defined in `localization.py`.

**gui** — Force a specific GUI renderer: `'cef'`, `'qt'`, `'gtk'`, `'edgechromium'`, `'mshtml'`. See Platforms and Renderers for details.

**debug** — Enable debug mode (web inspector, JS error reporting). See Debugging section.

**http_server** — Enable built-in HTTP server for absolute local paths. Relative paths always use HTTP server. Ignored for non-local URLs.

**http_port** — Fixed port for the HTTP server. Default: randomized.

**user_agent** — Custom user agent string.

**private_mode** — Control persistent storage (cookies, localStorage). Default: True (nothing stored between sessions).

**storage_path** — Custom path for persistent data. Default: `~/.pywebview` on Unix, `%APPDATA%\pywebview` on Windows.

**menu** — Application-level menu as a list of `Menu` objects.

**server** — Custom WSGI server instance (global default).

**ssl** — Enable SSL for the internal HTTP server. Requires `cryptography` package (`pip install pywebview[ssl]`).

**server_args** — Arguments passed to server instantiation.

**icon** — Path to application icon (.ico on Windows, .icns on macOS, .png on Linux).

## webview.active_window()

Return the currently focused window instance.

```python
active = webview.active_window()
print(active.title)
```

## webview.screens

Return a list of available displays as `Screen` objects. Primary display is first.

```python
screens = webview.screens
for s in screens:
    print(f'{s.width}x{s.height} at ({s.x}, {s.y}), scale={s.scale}')
```

### Screen Properties

- `width` / `height` — Display dimensions in logical pixels
- `x` / `y` — Top-left corner coordinates in logical pixels
- `scale` — DPI scale factor (e.g., 2.0 for Retina/HiDPI)
- `physical_width` / `physical_height` — Dimensions in physical pixels (`width * scale`)
- `physical_x` / `physical_y` — Coordinates in physical pixels (`x * scale`)
- `dpi` — Dots per inch (`scale * 96`)

## webview.token

CSRF token unique to the session. Same value exposed as `window.pywebview.token` in JavaScript. Use for securing REST APIs.

## webview.windows

List of all open windows in creation order.

## Window Properties

- `window.title` — Get or set window title
- `window.on_top` — Get or set always-on-top
- `window.x` / `window.y` — Window position in logical pixels
- `window.width` / `window.height` — Window dimensions in logical pixels
- `window.native` — Native window object (available after `before_show` event)
  - Windows: `System.Windows.Forms.Form`
  - macOS: `AppKit.NSWindow`
  - GTK: `Gtk.ApplicationWindow`
  - Qt: `QMainWindow`
  - Android: `kivy.uix.widget.Widget`

## Window Methods

### Content Loading

- `window.load_url(url)` — Load a new URL
- `window.load_html(content, base_uri=None)` — Load HTML string. Cannot use hashbang anchors this way
- `window.load_css(css)` — Inject CSS as a string

### JavaScript Execution

- `window.evaluate_js(script, callback=None)` — Execute JS and return result of last expression. If callback supplied, resolves promises. Throws `webview.errors.JavascriptException` on error. Uses `eval` internally (won't work with `unsafe-eval` CSP).
- `window.run_js(code)` — Execute JS as-is without wrapper. No return value. Works with `unsafe-eval` CSP.

### Window Manipulation

- `window.resize(width, height, fix_point=FixPoint.NORTH | FixPoint.WEST)` — Resize window. `fix_point` anchors the resize
- `window.move(x, y)` — Move window to coordinates in logical pixels
- `window.toggle_fullscreen()` — Toggle fullscreen on active monitor
- `window.maximize()` — Maximize window
- `window.minimize()` — Minimize window
- `window.restore()` — Restore minimized/maximized window
- `window.hide()` — Hide window
- `window.show()` — Show hidden window
- `window.destroy()` — Close/destroy the window

### Dialogs and Data

- `window.create_file_dialog(dialog_type=FileDialog.OPEN, directory='', allow_multiple=False, save_filename='', file_types=())` — Open file/folder/save dialog. Returns tuple of selected files or None if cancelled
- `window.create_confirmation_dialog(title, message)` — OK/Cancel confirmation dialog
- `window.get_current_url()` — Current URL or None
- `window.get_cookies()` — List of cookies as SimpleCookie
- `window.clear_cookies()` — Clear all cookies including HttpOnly

### DOM Access

- `window.dom.body` — Document body as Element
- `window.dom.document` — Document as Element
- `window.dom.window` — Window object as Element
- `window.dom.get_element(selector)` — First matching Element or None
- `window.dom.get_elements(selector)` — List of matching Elements
- `window.dom.create_element(html, parent=None, mode=ManipulationMode.LastChild)` — Create element from HTML string

### State (6.0+)

- `window.state` — Observable shared state object between Python and JavaScript. Supports both dot notation (`state.key`) and index notation (`state['key']`). Subscribe with `window.state += callback`.

## Window Events

Subscribe with `+=`, unsubscribe with `-=`:

```python
window.events.loaded += on_loaded_handler
window.events.loaded -= on_loaded_handler
```

Pass `window` as first parameter to access the window from the handler. Most events are asynchronous (separate threads). `before_show` and `before_load` are synchronous and block the main thread.

### Lifecycle Events

- `events.initialized` — Fired after GUI/renderer is chosen, before window creation. First argument is renderer name. Return False to cancel window creation. **Blocking.**
- `events.before_show` — Fired just before window is shown. Earliest event exposing `window.native`. **Blocking.**
- `events.before_load` — Fired right before pywebview code injection (roughly DOMContentLoaded). **Blocking.**
- `events.shown` — Window is shown
- `events.loaded` — DOM is ready
- `events.closed` — Window is closed

### Window State Events

- `events.closing` — About to close. Return False to cancel (when `confirm_close=True`, fires before confirmation dialog)
- `events.minimized` — Window minimized
- `events.maximized` — Window maximized (fullscreen on macOS)
- `events.restored` — Window restored from minimized/maximized
- `events.resized` — Window resized. Handler can accept `(width, height)` arguments
- `events.moved` — Window moved

### Network Events (6.0+)

- `events.request_sent` — HTTP request sent. Handler receives `Request` object with `url`, `method`, `headers` (mutable). Not emitted for every request on macOS (main document only)
- `events.response_received` — HTTP response received. Handler receives `Response` object with `url`, `status`, `headers`. Not supported on Qt

## Menu API

```python
import webview.menu as menu

# Application menu
file_menu = menu.Menu('File', items=[
    menu.MenuAction('Open', open_callback),
    menu.MenuSeparator(),
    menu.MenuAction('Exit', exit_callback)
])

# macOS application menu (use __app__ title)
app_menu = menu.Menu('__app__', items=[
    menu.MenuAction('About', about_callback)
])

webview.start(menu=[app_menu, file_menu])

# Window-specific menu
window = webview.create_window('App', menu=[file_menu])
```

## FileDialog Enum

```python
webview.FileDialog.OPEN   # Open file dialog
webview.FileDialog.SAVE   # Save file dialog
webview.FileDialog.FOLDER # Open folder dialog
```
