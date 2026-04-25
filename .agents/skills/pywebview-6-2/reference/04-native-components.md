# Native Components API

## Menus

### Creating Menus

```python
import webview

# Create simple menu item with callback
quit_item = webview.MenuItem(
    'Quit',
    callback=lambda: webview.windows[0].destroy()
)

# Create menu item without callback (for separators or disabled items)
new_item = webview.MenuItem('New')

# Create separator
separator = webview.MenuItem.separator()

# Build menu hierarchy
menu = webview.Menu(items=[
    webview.MenuItem('File', items=[
        webview.MenuItem('New', callback=lambda: print('New file')),
        webview.MenuItem('Open', callback=lambda: print('Open file')),
        webview.MenuItem('Save', callback=lambda: print('Save file')),
        webview.MenuItem('Save As...', callback=lambda: print('Save As')),
        separator,
        webview.MenuItem('Exit', callback=lambda: webview.windows[0].destroy())
    ]),
    webview.MenuItem('Edit', items=[
        webview.MenuItem('Undo', callback=lambda: print('Undo'), shortcut='Ctrl+Z'),
        webview.MenuItem('Redo', callback=lambda: print('Redo'), shortcut='Ctrl+Y'),
        separator,
        webview.MenuItem('Cut', callback=lambda: print('Cut'), shortcut='Ctrl+X'),
        webview.MenuItem('Copy', callback=lambda: print('Copy'), shortcut='Ctrl+C'),
        webview.MenuItem('Paste', callback=lambda: print('Paste'), shortcut='Ctrl+V')
    ]),
    webview.MenuItem('View', items=[
        webview.MenuItem('Zoom In', callback=lambda: print('Zoom in'), shortcut='Ctrl++'),
        webview.MenuItem('Zoom Out', callback=lambda: print('Zoom out'), shortcut='Ctrl+-'),
        separator,
        webview.MenuItem('Fullscreen', callback=lambda: webview.windows[0].toggle_fullscreen(), shortcut='F11')
    ]),
    webview.MenuItem('Help', items=[
        webview.MenuItem('Documentation', callback=lambda: print('Open docs')),
        webview.MenuItem('About', callback=lambda: show_about_dialog())
    ])
])

# Create window with menu
window = webview.create_window('My Application', './index.html', menu=menu)
webview.start()
```

### MenuItem Properties

```python
webview.MenuItem(
    text,           # str - Menu item text
    callback=None,  # callable - Function to call when clicked
    checked=False,  # bool - Show checkmark (for toggle items)
    enabled=True,   # bool - Enable/disable menu item
    shortcut=None,  # str - Keyboard shortcut (e.g., 'Ctrl+S', 'Cmd+Q')
    items=[]        # list - Submenu items (creates dropdown)
)
```

### Checkable Menu Items

```python
import webview

class MenuState:
    def __init__(self):
        self.dark_mode = False
        self.autosave = True

menu_state = MenuState()

def toggle_dark_mode():
    menu_state.dark_mode = not menu_state.dark_mode
    # Update UI
    window.evaluate_js(f'document.body.classList.toggle("dark-mode")')
    return menu_state.dark_mode

def toggle_autosave():
    menu_state.autosave = not menu_state.autosave
    print(f'Autosave: {"enabled" if menu_state.autosave else "disabled"}')
    return menu_state.autosave

menu = webview.Menu(items=[
    webview.MenuItem('View', items=[
        webview.MenuItem(
            'Dark Mode',
            callback=toggle_dark_mode,
            checked=menu_state.dark_mode
        ),
        webview.MenuItem(
            'Autosave',
            callback=toggle_autosave,
            checked=menu_state.autosave
        )
    ])
])

window = webview.create_window('Checkable Menus', './index.html', menu=menu)
webview.start()
```

### Updating Menu Items at Runtime

```python
import webview

# Store references to menu items
save_item = None
save_as_item = None

def update_menu_enabled_states():
    """Update menu item states based on application state"""
    has_document = True  # Check your app state
    
    if save_item:
        save_item.enabled = has_document
    if save_as_item:
        save_as_item.enabled = True  # Always enabled

# Create menu items with references
save_item = webview.MenuItem('Save', callback=lambda: print('Save'))
save_as_item = webview.MenuItem('Save As...', callback=lambda: print('Save As'))

menu = webview.Menu(items=[
    webview.MenuItem('File', items=[
        save_item,
        save_as_item
    ])
])

window = webview.create_window('Dynamic Menu', './index.html', menu=menu)

# Update menu states periodically or on events
def on_loaded(window):
    # Initially disable Save if no document
    save_item.enabled = False

window.events.loaded += on_loaded
webview.start()
```

## Dialogs

### MessageBox

Display message dialogs with buttons:

```python
import webview

# Info message (OK button)
result = webview.MessageBox.show(
    title='Information',
    message='This is an informational message.',
    box_type=webview.MessageBoxType.INFO
)

# Warning message
webview.MessageBox.show(
    'Warning',
    'Please be careful!',
    webview.MessageBoxType.WARNING
)

# Error message
webview.MessageBox.show(
    'Error',
    'Something went wrong!',
    webview.MessageBoxType.ERROR
)

# Question (Yes/No buttons)
if webview.MessageBox.yes_no('Confirm', 'Are you sure you want to continue?'):
    print('User clicked Yes')
else:
    print('User clicked No')

# Yes/No/Cancel
result = webview.MessageBox.yes_no_cancel(
    'Confirm',
    'What do you want to do?'
)

if result == webview.MessageBoxResult.YES:
    print('Yes clicked')
elif result == webview.MessageBoxResult.NO:
    print('No clicked')
else:
    print('Cancel clicked')
```

**MessageBox types:**
- `MessageBoxType.INFO` - Information icon
- `MessageBoxType.WARNING` - Warning icon
- `MessageBoxType.ERROR` - Error icon
- `MessageBoxType.QUESTION` - Question icon

### File Dialogs

**Open File Dialog:**

```python
import webview

# Single file selection
file_path = webview.FileDialog.open(
    title='Open File',
    directory='/home/user/Documents',
    filters=[
        ('Python files', '*.py'),
        ('Text files', '*.txt'),
        ('All files', '*.*')
    ]
)

if file_path:
    print(f'Selected file: {file_path}')
    with open(file_path, 'r') as f:
        content = f.read()
else:
    print('No file selected (user cancelled)')

# Multiple file selection
files = webview.FileDialog.open_multiple(
    title='Open Multiple Files',
    directory='./',
    filters=[
        ('Images', '*.png *.jpg *.gif'),
        ('All files', '*.*')
    ]
)

if files:
    print(f'Selected {len(files)} files:')
    for file_path in files:
        print(f'  - {file_path}')
```

**Save File Dialog:**

```python
import webview

file_path = webview.FileDialog.save(
    title='Save File',
    directory='/home/user/Documents',
    filename='output.txt',  # Default filename
    filters=[
        ('Text files', '*.txt'),
        ('JSON files', '*.json'),
        ('All files', '*.*')
    ]
)

if file_path:
    print(f'Saving to: {file_path}')
    with open(file_path, 'w') as f:
        f.write('Hello, World!')
else:
    print('Save cancelled')
```

**Open Folder Dialog:**

```python
import webview

folder_path = webview.FileDialog.open_folder(
    title='Select Folder',
    directory='/home/user'
)

if folder_path:
    print(f'Selected folder: {folder_path}')
else:
    print('No folder selected')
```

**File Dialog Filters:**

Filters follow platform-specific formats:
- Windows: `('Description', '*.ext1 *.ext2')`
- macOS/Linux: `('Description', '*.ext1 *.ext2')`

Common patterns:
```python
filters = [
    ('Python files', '*.py'),
    ('JavaScript files', '*.js *.jsx *.ts *.tsx'),
    ('Images', '*.png *.jpg *.jpeg *.gif *.webp *.svg'),
    ('Videos', '*.mp4 *.avi *.mov *.mkv'),
    ('Audio', '*.mp3 *.wav *.ogg *.flac'),
    ('Documents', '*.pdf *.doc *.docx *.txt *.md'),
    ('Archives', '*.zip *.tar *.gz *.rar'),
    ('All files', '*.*')
]
```

### Color Dialog

```python
import webview

# Open color picker
color = webview.ColorDialog.pick(
    title='Select Color',
    default_color='#3498db'  # Default RGB hex color
)

if color:
    print(f'Selected color: {color}')  # Returns hex string like '#RRGGBB'
    # Apply to window or UI
    window.evaluate_js(f'document.body.style.backgroundColor = "{color}"')
else:
    print('Color selection cancelled')
```

## Drag and Drop

### Enable Drag and Drop

```python
import webview

# Enable drag-and-drop file support
window = webview.create_window(
    'Drag and Drop Demo',
    './index.html',
    draggable=True  # Enable D&D
)

# Handle dropped files
def on_file_dropped(files):
    print(f'{len(files)} file(s) dropped:')
    for file_path in files:
        print(f'  - {file_path}')

window.events.file_dropped += on_file_dropped
webview.start()
```

### JavaScript Side Handling

```html
<!DOCTYPE html>
<html>
<head>
    <style>
        #drop-zone {
            width: 100%;
            height: 200px;
            border: 2px dashed #3498db;
            border-radius: 10px;
            display: flex;
            align-items: center;
            justify-content: center;
            transition: all 0.3s;
        }
        
        #drop-zone.drag-over {
            background: #3498db;
            color: white;
        }
    </style>
</head>
<body>
    <h1>Drag and Drop Files Here</h1>
    <div id="drop-zone">Drop files here</div>
    <div id="file-list"></div>

    <script>
        const dropZone = document.getElementById('drop-zone');
        const fileList = document.getElementById('file-list');

        // Prevent default behavior
        ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
            dropZone.addEventListener(eventName, preventDefaults, false);
            document.body.addEventListener(eventName, preventDefaults, false);
        });

        function preventDefaults(e) {
            e.preventDefault();
            e.stopPropagation();
        }

        // Highlight drop zone
        ['dragenter', 'dragover'].forEach(eventName => {
            dropZone.addEventListener(eventName, highlight, false);
        });

        ['dragleave', 'drop'].forEach(eventName => {
            dropZone.addEventListener(eventName, unhighlight, false);
        });

        function highlight() {
            dropZone.classList.add('drag-over');
        }

        function unhighlight() {
            dropZone.classList.remove('drag-over');
        }

        // Handle dropped files
        dropZone.addEventListener('drop', handleDrop, false);

        function handleDrop(e) {
            const dt = e.dataTransfer;
            const files = dt.files;

            handleFiles(files);
        }

        function handleFiles(files) {
            fileList.innerHTML = '<h3>Dropped Files:</h3><ul></ul>';
            const ul = fileList.querySelector('ul');

            ([...files]).forEach(file => {
                const li = document.createElement('li');
                li.textContent = `${file.name} (${formatSize(file.size)})`;
                ul.appendChild(li);

                // Log to Python
                if (window.pywebview && window.pywebview.api) {
                    window.pywebview.api.log_file_drop(file.name, file.size);
                }
            });
        }

        function formatSize(bytes) {
            if (bytes < 1024) return bytes + ' B';
            if (bytes < 1048576) return (bytes / 1024).toFixed(1) + ' KB';
            return (bytes / 1048576).toFixed(1) + ' MB';
        }
    </script>
</body>
</html>
```

**Python handler:**

```python
import webview

class DropHandler:
    def __init__(self):
        self.dropped_files = []
    
    def log_file_drop(self, filename, size):
        print(f'File dropped: {filename} ({size} bytes)')
        self.dropped_files.append({'name': filename, 'size': size})
    
    def get_drop_history(self):
        return self.dropped_files

handler = DropHandler()
window = webview.create_window('D&D', './index.html', js_api=handler, draggable=True)
webview.start()
```

## Screens and Displays

### Get Screen Information

```python
import webview

# Get all screens
screens = webview.screens
print(f'Number of screens: {len(screens)}')

for i, screen in enumerate(screens):
    print(f'\nScreen {i}:')
    print(f'  Width: {screen.width}')
    print(f'  Height: {screen.height}')
    print(f'  Position X: {screen.x}')
    print(f'  Position Y: {screen.y}')
    print(f'  Scale factor: {screen.scale_factor}')

# Get primary screen
primary = webview.screens[0]
print(f'\nPrimary screen: {primary.width}x{primary.height}')
```

### Position Windows on Specific Screens

```python
import webview

if len(webview.screens) > 1:
    # Get second screen
    secondary_screen = webview.screens[1]
    
    # Center window on secondary screen
    x = secondary_screen.x + (secondary_screen.width - 800) // 2
    y = secondary_screen.y + (secondary_screen.height - 600) // 2
    
    window = webview.create_window(
        'Secondary Screen',
        'https://example.com',
        width=800,
        height=600,
        x=x,
        y=y
    )
else:
    window = webview.create_window('Single Screen', 'https://example.com')

webview.start()
```

## Platform-Specific Features

### macOS-Specific

**Vibrancy Effect:**

```python
import webview

window = webview.create_window(
    'Vibrancy Demo',
    './index.html',
    transparent=True,
    vibrancy=True  # macOS-only
)
webview.start()
```

**PyStray System Tray Icon:**

```python
import webview
import pystray
from PIL import Image

def create_tray_icon():
    """Create a simple tray icon"""
    img = Image.new('RGB', (64, 64), color='blue')
    return img

def on_click(icon, widget):
    print('Tray icon clicked!')
    window.show()
    window.focus()

def main():
    global window
    
    # Create main window
    window = webview.create_window('My App', './index.html')
    
    # Create tray icon
    icon = pystray.Icon('name', create_tray_icon(), 'My Application')
    
    with icon:
        # Run pywebview
        webview.start()

if __name__ == '__main__':
    main()
```

### Windows-Specific

**Custom Window Icon:**

```python
import webview

# Set window icon (ICO file)
window = webview.create_window(
    'My App',
    './index.html',
    # Icon handling is platform-specific
)

# On Windows, you can use:
# import ctypes
# from ctypes import windll
# 
# myappid = 'mycompany.myapp.version'
# ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
```

### Linux-Specific

**GTK Theme Integration:**

```python
import webview

# Use GTK backend for better system integration
window = webview.create_window(
    'Linux App',
    './index.html'
)

# Start with GTK explicitly
webview.start(gui='gtk')
```

## Combining Native Components

### Complete Application Menu Example

```python
import webview

class App:
    def __init__(self):
        self.file_path = None
    
    def new_file(self):
        self.file_path = None
        window.evaluate_js('app.newFile()')
    
    def open_file(self):
        path = webview.FileDialog.open(
            title='Open File',
            filters=[('All files', '*.*')]
        )
        if path:
            self.file_path = path
            window.evaluate_js(f'app.loadFile("{path}")')
    
    def save_file(self):
        if self.file_path:
            window.evaluate_js(f'app.saveFile("{self.file_path}")')
        else:
            self.save_as()
    
    def save_as(self):
        path = webview.FileDialog.save(
            title='Save As',
            filename='untitled.txt',
            filters=[('Text files', '*.txt'), ('All files', '*.*')]
        )
        if path:
            self.file_path = path
            window.evaluate_js(f'app.saveFile("{path}")')
    
    def show_about(self):
        webview.MessageBox.show(
            'About My App',
            'My Application v1.0\n\nA pywebview demo application.',
            webview.MessageBoxType.INFO
        )
    
    def quit_app(self):
        window.destroy()

app = App()

# Create comprehensive menu
menu = webview.Menu(items=[
    webview.MenuItem('File', items=[
        webview.MenuItem('New', callback=app.new_file, shortcut='Ctrl+N'),
        webview.MenuItem('Open...', callback=app.open_file, shortcut='Ctrl+O'),
        webview.MenuItem('Save', callback=app.save_file, shortcut='Ctrl+S'),
        webview.MenuItem('Save As...', callback=app.save_as, shortcut='Ctrl+Shift+S'),
        webview.MenuItem.separator(),
        webview.MenuItem('Exit', callback=app.quit_app, shortcut='Alt+F4')
    ]),
    webview.MenuItem('Edit', items=[
        webview.MenuItem('Undo', shortcut='Ctrl+Z'),
        webview.MenuItem('Redo', shortcut='Ctrl+Y'),
        webview.MenuItem.separator(),
        webview.MenuItem('Cut', shortcut='Ctrl+X'),
        webview.MenuItem('Copy', shortcut='Ctrl+C'),
        webview.MenuItem('Paste', shortcut='Ctrl+V')
    ]),
    webview.MenuItem('View', items=[
        webview.MenuItem('Fullscreen', callback=lambda: window.toggle_fullscreen(), shortcut='F11')
    ]),
    webview.MenuItem('Help', items=[
        webview.MenuItem('About', callback=app.show_about)
    ])
])

# Create window with menu
window = webview.create_window(
    'My Application',
    './index.html',
    width=1000,
    height=700,
    menu=menu,
    draggable=True  # Enable drag-and-drop
)

webview.start()
```

## Best Practices

1. **Use meaningful menu labels:** Follow platform conventions (e.g., "Quit" on macOS, "Exit" on Windows)
2. **Provide keyboard shortcuts:** Common operations should have shortcuts
3. **Handle dialog cancellations:** Always check if user cancelled the dialog
4. **Use appropriate file filters:** Help users find the right files
5. **Update menu states:** Enable/disable items based on application state
6. **Test on all platforms:** Native components may behave differently across OS
