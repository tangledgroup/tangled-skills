# Common Operations

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

See [Window API Reference](reference/03-window-api.md) for complete methods.

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

See [JavaScript Integration](reference/02-js-api.md) for complete guide.

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

See [Dialog API](reference/04-native-components.md) for all dialog types.

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

See [Menu API](reference/04-native-components.md) for complete menu system.
