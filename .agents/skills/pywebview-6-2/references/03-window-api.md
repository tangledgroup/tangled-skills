# Window API Reference

## Window Object Overview

The `Window` object is returned by `webview.create_window()` and provides methods to control window behavior, manipulate content, and handle events.

```python
import webview

window = webview.create_window('My App', 'https://example.com')
# ^-- This returns a Window object
```

## Creating Windows

### create_window() Parameters

```python
webview.create_window(
    title,                    # str - Window title
    url=None,                 # str - URL to load (or WSGI server)
    html=None,                # str - HTML content (takes precedence over url)
    js_api=None,              # object - Python object exposed to JavaScript
    width=800,                # int - Window width in pixels
    height=600,               # int - Window height in pixels
    x=None,                   # int - X position (None = centered)
    y=None,                   # int - Y position (None = centered)
    screen=None,              # int - Screen index for multi-monitor setups
    resizable=True,           # bool - Allow window resizing
    fullscreen=False,         # bool - Start in fullscreen mode
    min_size=(200, 100),      # tuple - Minimum (width, height)
    hidden=False,             # bool - Start hidden
    frameless=False,          # bool - Remove window chrome
    easy_drag=True,           # bool - Enable easy drag on frameless windows
    shadow=False,             # bool - Add drop shadow (macOS)
    focus=True,               # bool - Focus window on creation
    minimized=False,          # bool - Start minimized
    maximized=False,          # bool - Start maximized
    menu=[],                  # Menu - Native menu instance
    on_top=False,             # bool - Always on top
    confirm_close=False,      # bool - Show confirmation before closing
    background_color='#FFFFFF',  # str - Background color (hex)
    transparent=False,        # bool - Transparent background
    text_select=True,         # bool - Allow text selection
    zoomable=True,           # bool - Allow zooming (Ctrl+/-)
    draggable=False,          # bool - Enable drag-and-drop file support
    vibrancy=False,           # bool - macOS vibrancy effect
    server=http.BottleServer,  # WSGI server class for local files
    server_args={},           # dict - Server configuration arguments
    localization=None         # dict - Custom localization strings
)
```

### Window Creation Examples

**Basic window:**
```python
window = webview.create_window('Hello World', 'https://example.com')
```

**Custom size and position:**
```python
window = webview.create_window(
    'My App',
    './index.html',
    width=1200,
    height=800,
    x=100,
    y=100
)
```

**Frameless window (custom UI):**
```python
window = webview.create_window(
    'Custom Window',
    './index.html',
    frameless=True,
    easy_drag=True,  # Click and drag anywhere to move
    transparent=True,
    background_color='#00000000'  # Transparent (RGBA hex)
)
```

**Fullscreen kiosk mode:**
```python
window = webview.create_window(
    'Kiosk',
    'https://kiosk.example.com',
    fullscreen=True,
    resizable=False,
    text_select=False,
    zoomable=False
)
```

**Multiple windows:**
```python
main_window = webview.create_window('Main', './main.html', width=1000, height=700)
settings_window = webview.create_window('Settings', './settings.html', width=400, height=300)
help_window = webview.create_window('Help', 'https://help.example.com')

# Access all windows
print(f'Total windows: {len(webview.windows)}')
```

## Window Properties

### title (str)
Get or set window title:
```python
print(window.title)  # Get current title
window.title = 'New Title'  # Set new title
```

### created_at (datetime)
Timestamp when window was created:
```python
print(f'Window created at: {window.created_at}')
```

### url (str)
Current URL loaded in window:
```python
current_url = window.get_current_url()
print(f'Currently viewing: {current_url}')
```

## Window Methods

### Navigation

**load_url(url: str)**
Load a new URL:
```python
window.load_url('https://example.com')
window.load_url('./local-page.html')  # Relative path served by built-in server
```

**load_html(content: str)**
Load HTML content directly:
```python
html = '<html><body><h1>Dynamic Content</h1></body></html>'
window.load_html(html)
```

### JavaScript Execution

**evaluate_js(script: str, callback=None)**
Execute JavaScript and get result. Returns immediately or calls callback for promises:
```python
# Synchronous - returns result
title = window.evaluate_js('document.title')
print(f'Page title: {title}')

# Get element value
count = window.evaluate_js('document.getElementById("counter").textContent')

# With callback for promises
def handle_result(result):
    print(f'Promise resolved: {result}')

window.evaluate_js('''
    fetch('https://api.example.com/data')
        .then(response => response.json())
''', handle_result)

# Async/await style JavaScript
window.evaluate_js('''
    (async () => {
        const data = await fetch('/api/data').then(r => r.json());
        return data;
    })();
''')
```

**run_js(script: str)**
Execute JavaScript without returning value (fire-and-forget):
```python
window.run_js('console.log("No return value")')
window.run_js('document.body.classList.add("dark-mode")')
```

### Window State Control

**show()**
Show a hidden window:
```python
window.hide()
# ... later
window.show()
```

**hide()**
Hide the window (doesn't close):
```python
window.hide()  # Window still exists, just not visible
```

**toggle_fullscreen()**
Toggle between fullscreen and windowed mode:
```python
window.toggle_fullscreen()
```

**minimize()**
Minimize window to taskbar/dock:
```python
window.minimize()
```

**maximize()**
Maximize window to fill screen:
```python
window.maximize()
```

**restore()**
Restore from minimized or maximized state:
```python
window.restore()
```

**focus()**
Bring window to front and focus:
```python
window.focus()
```

### Window Geometry

**resize(width: int, height: int)**
Change window size:
```python
window.resize(1920, 1080)  # Full HD
window.resize(800, 600)    # Smaller
```

**move(x: int, y: int)**
Move window to new position:
```python
window.move(100, 100)  # Top-left corner at (100, 100)
```

### Window Destruction

**destroy()**
Close and destroy the window:
```python
window.destroy()  # Window is closed and removed from webview.windows
```

## Window Events

Window events are accessed via `window.events` container. Subscribe with `+=`, unsubscribe with `-=`.

### Available Events

- **closed** - Window was closed
- **closing** - Window is about to close (can be prevented)
- **loaded** - Page finished loading
- **before_load** - Before page starts loading
- **before_show** - Before window is shown
- **shown** - Window was shown
- **minimized** - Window was minimized
- **maximized** - Window was maximized
- **restored** - Window was restored
- **resized** - Window was resized
- **moved** - Window was moved

### Event Subscription

```python
import webview

def on_shown(window):
    print(f'Window shown: {window.title}')

def on_closing(window):
    print(f'Window closing: {window.title}')
    return True  # Return False to prevent closing

def on_loaded(window):
    print('Page loaded successfully')

def on_resized(window):
    print(f'Window resized (event triggered)')

window = webview.create_window('Events Demo', 'https://example.com')

# Subscribe to events
window.events.shown += on_shown
window.events.closing += on_closing
window.events.loaded += on_loaded
window.events.resized += on_resized

webview.start()
```

### Preventing Window Close

```python
import webview

def on_closing(window):
    result = webview.MessageBox.yes_no(
        'Confirm Close',
        'Are you sure you want to close? Unsaved changes will be lost.'
    )
    return result  # True = allow close, False = prevent close

window = webview.create_window('Confirm Close', './index.html', confirm_close=True)
window.events.closing += on_closing
webview.start()
```

### Event Unsubscription

```python
def handler(window):
    print('Event triggered')

window.events.shown += handler
# ... later
window.events.shown -= handler  # Remove handler
```

## Window Management Utilities

### Active Window

Get currently focused window:
```python
active = webview.active_window()
print(f'Active window: {active.title}')
```

### All Windows

Access all open windows:
```python
print(f'Total windows: {len(webview.windows)}')

for i, window in enumerate(webview.windows):
    print(f'{i+1}. {window.title} - {window.get_current_url()}')
```

### Window by Index

```python
first_window = webview.windows[0]
last_window = webview.windows[-1]
```

## Advanced Window Features

### Frameless Windows with Custom Title Bar

```python
import webview

html = '''
<!DOCTYPE html>
<html>
<head>
    <style>
        .title-bar {
            height: 30px;
            background: #333;
            color: white;
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 0 10px;
            user-select: none;
        }
        .title-bar-left {
            font-size: 14px;
        }
        .title-bar-right {
            display: flex;
            gap: 10px;
        }
        .window-button {
            width: 30px;
            height: 30px;
            display: flex;
            align-items: center;
            justify-content: center;
            cursor: pointer;
        }
        .window-button:hover {
            background: #555;
        }
        .window-button.close:hover {
            background: #e81123;
        }
        #content {
            padding: 20px;
        }
    </style>
</head>
<body>
    <div class="title-bar" data-webview-drag-region>
        <div class="title-bar-left">My Custom Window</div>
        <div class="title-bar-right">
            <div class="window-button minimize" onclick="pywebview.api.minimize()">─</div>
            <div class="window-button maximize" onclick="pywebview.api.toggle_maximize()">□</div>
            <div class="window-button close" onclick="pywebview.api.close()">✕</div>
        </div>
    </div>
    <div id="content">
        <h1>Custom Title Bar Demo</h1>
        <p>This window has a custom title bar with native window controls.</p>
    </div>
    
    <script>
        // Expose window control functions
        window.pywebview = window.pywebview || {};
        window.pywebview.api = {
            minimize: () => pywebview.api.minimize_window(),
            toggle_maximize: () => pywebview.api.toggle_maximize_window(),
            close: () => pywebview.api.close_window()
        };
    </script>
</body>
</html>
'''

class WindowControls:
    def minimize_window(self):
        webview.active_window().minimize()
    
    def toggle_maximize_window(self):
        window = webview.active_window()
        # Toggle between maximize and restore
        # (simplified - actual implementation may need state tracking)
        window.maximize()
    
    def close_window(self):
        webview.active_window().destroy()

window = webview.create_window(
    'Custom Window',
    html=html,
    js_api=WindowControls(),
    frameless=True,
    easy_drag=True  # Enables dragging from title bar
)
webview.start()
```

### Transparent Windows (macOS vibrancy)

```python
import webview

window = webview.create_window(
    'Vibrancy Demo',
    './index.html',
    transparent=True,
    background_color='#00000000',  # Fully transparent
    vibrancy=True  # macOS-only: adds system vibrancy effect
)
webview.start()
```

**CSS for transparent windows:**
```css
body {
    margin: 0;
    padding: 20px;
}

.card {
    background: rgba(255, 255, 255, 0.8);  /* Semi-transparent */
    backdrop-filter: blur(10px);  /* Blur background */
    border-radius: 10px;
    padding: 20px;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}
```

### Multi-Monitor Support

```python
import webview

# Get window on specific screen
window1 = webview.create_window('Screen 0', 'https://example.com', screen=0)
window2 = webview.create_window('Screen 1', 'https://google.com', screen=1)

# Position windows side by side on different screens
# (requires knowing screen dimensions - platform-specific)
```

### Window State Persistence

```python
import webview
import json

class WindowState:
    def __init__(self):
        self.state_file = '.window_state.json'
    
    def save_state(self, window):
        state = {
            'x': window.x,  # If available
            'y': window.y,
            'width': window.width,  # If available
            'height': window.height,
            'maximized': window.is_maximized()  # If available
        }
        with open(self.state_file, 'w') as f:
            json.dump(state, f)
    
    def load_state(self):
        try:
            with open(self.state_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return None

state_manager = WindowState()

# Load previous state
previous_state = state_manager.load_state()
x, y = None, None
maximized = False

if previous_state:
    x = previous_state.get('x')
    y = previous_state.get('y')
    maximized = previous_state.get('maximized', False)

window = webview.create_window(
    'My App',
    './index.html',
    x=x,
    y=y,
    maximized=maximized
)

# Save state on close
def on_closing(window):
    state_manager.save_state(window)
    return True

window.events.closing += on_closing
webview.start()
```

## Platform-Specific Behavior

### Windows
- Frameless windows require manual title bar implementation
- WebView2 is default backend (requires runtime installation)
- Easy drag works on any element with `data-webview-drag-region` attribute

### macOS
- Native window traffic lights (close/min/max buttons) can be hidden in frameless mode
- Vibrancy effect requires `vibrancy=True` and translucent background
- Shadow effect available with `shadow=True`

### Linux
- GTK backend may have different window decorations
- Qt backend provides more consistent cross-platform behavior
- Frameless windows may need WM hints for proper behavior

## Troubleshooting Window Issues

**Window appears blank:**
```python
# Check if page loaded
def on_loaded(window):
    print('Page loaded successfully')
    # Try to get title
    title = window.evaluate_js('document.title')
    print(f'Page title: {title}')

window.events.loaded += on_loaded
```

**JavaScript not executing:**
```python
# Ensure page is loaded before executing JS
def on_loaded(window):
    result = window.evaluate_js('console.log("JS works!"); return "success";')
    print(f'Result: {result}')

window.events.loaded += on_loaded
```

**Window events not firing:**
- Ensure handlers are added before `webview.start()`
- Check for typos in event names
- Verify handler signature matches expected format
