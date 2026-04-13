# Installation and Architecture Patterns

## Complete Installation Guide

### Basic Installation

```bash
pip install pywebview
```

This installs pywebview with default dependencies for each platform.

### Linux Installation Options

On Linux, explicitly choose between Qt and GTK backends:

**GTK Backend:**
```bash
pip install pywebview[gtk]
```

**Qt Backend (default):**
```bash
pip install pywebview[qt]  # Installs PyQt6 by default
```

**Alternative Qt Options:**
```bash
pip install pywebview[qt5]      # PyQt5
pip install pywebview[pyside2]  # PySide2  
pip install pywebview[pyside6]  # PySide6
```

**System Dependencies (Debian/Ubuntu):**

For QtWebEngine (modern, preferred):
```bash
sudo apt install python3-pyqt5 python3-pyqt5.qtwebengine python3-pyqt5.qtwebchannel libqt5webkit5-dev
```

For QtWebKit (legacy, more platform support):
```bash
sudo apt install python3-qtwebkit
```

For GTK:
```bash
sudo apt install python3-gi python3-gi-cairo gir12-gtk-3.0 gir12-webkit2-4.0
```

### Optional Dependencies

```bash
pip install pywebview[android]  # Android support (requires additional setup)
pip install pywebview[cef]      # Chromium Embedded Framework (Windows only)
pip install pywebview[ssl]      # HTTPS support for local HTTP server
```

## Platform-Specific Requirements

### Windows

**Default Backend (WinForms + WebView2):**
- pythonnet package (requires .NET 4.0 or higher)
- WebView2 Runtime from Microsoft Edge
  - Download: https://developer.microsoft.com/en-us/microsoft-edge/webview2/
  - For distribution: Review [distribution guidelines](https://docs.microsoft.com/en-us/microsoft-edge/webview2/concepts/distribution)

**Alternative Backend (CEF):**
- cefpython package
- `pip install pywebview[cef]`

**Qt Backend:**
- PyQt5 or PyQt6 with QtWebEngine

### macOS

**Default Backend (Cocoa + WebKit):**
- pyobjc packages:
  ```bash
  pip install pyobjc-core
  pip install pyobjc-framework-Cocoa
  pip install pyobjc-framework-Quartz
  pip install pyobjc-framework-WebKit
  pip install pyobjc-framework-security
  ```
- Note: PyObjC comes preinstalled with Python bundled in macOS
- For standalone Python installations (Homebrew, python.org), install separately

**Alternative Backend (Qt):**
- PyQt5 or PyQt6 works on macOS as well

### Linux

**Qt Backend:**
```bash
# Ubuntu/Debian (PyQt5)
sudo apt install python3-pyqt5 python3-pyqt5.qtwebengine python3-pyqt5.qtwebchannel

# Fedora
sudo dnf install python3-pyqt5 Qt5WebEngine

# Arch Linux
sudo pacman -S pyqt5 webkit2gtk
```

**GTK Backend:**
```bash
# Ubuntu/Debian
sudo apt install python3-gi python3-gi-cairo gir12-gtk-3.0 gir12-webkit2-4.0

# Fedora
sudo dnf install python3-gobject gtk3 webkit2gtk3

# Arch Linux
sudo pacman -S python-gobject gtk2 webkit2gtk
```

### Android

Android support requires additional setup:
```bash
pip install pywebview[android]
```

See Android-specific documentation for build requirements and APK generation.

## Architecture Patterns

Choose from three main architectural approaches:

### Pattern 1: Pure Web Server (External)

**Best for:** Wrapping existing web applications, simple browsers

**Remote URL:**
```python
import webview

window = webview.create_window('Simple Browser', 'https://example.com')
webview.start()
```

**Local Flask Server:**
```python
import webview
from flask import Flask

app = Flask(__name__, static_folder='static', template_folder='templates')

@app.route('/')
def index():
    return app.send_static_file('index.html')

@app.route('/api/data')
def get_data():
    return {'status': 'success', 'data': [1, 2, 3]}

window = webview.create_window('Flask App', app)
webview.start()
```

**Local Bottle Server:**
```python
import webview
from bottle import Bottle, static

app = Bottle()

@app.route('/')
def index():
    return static('index.html', root='.')

@app.route('/<filepath:path>')
def serve_file(filepath):
    return static(filepath, root='.', download=True)

window = webview.create_window('Bottle App', app)
webview.start()
```

**Pros:**
- Simple to implement
- Works with existing web servers
- Full web server features available

**Cons:**
- Requires running HTTP server
- Communication via HTTP/REST (slower)
- CSRF protection needed for API calls

### Pattern 2: JS API with Internal HTTP Server (Recommended)

**Best for:** Most applications, hybrid apps with Python backend + web frontend

```python
import webview

class Api:
    """Python API exposed to JavaScript"""
    
    def get_user_data(self):
        # Fetch from database, API, etc.
        return {
            'name': 'John Doe',
            'email': 'john@example.com',
            'preferences': {'theme': 'dark'}
        }
    
    def save_settings(self, settings):
        print(f'Saving settings: {settings}')
        # Save to database or file
        return {'status': 'saved'}
    
    def log_message(self, message):
        import datetime
        timestamp = datetime.datetime.now().isoformat()
        print(f'[{timestamp}] {message}')
        return True

# Create window with local files + JS API bridge
window = webview.create_window(
    title='My Hybrid App',
    url='./index.html',  # Built-in server serves this file
    js_api=Api(),         # Expose Python class to JavaScript
    width=1200,
    height=800,
    resizable=True
)

webview.start()
```

**JavaScript Usage:**
```javascript
// Call Python functions (returns Promise)
pywebview.api.get_user_data().then(userData => {
    console.log('User:', userData.name);
    document.getElementById('username').textContent = userData.name;
});

// Save settings
pywebview.api.save_settings({theme: 'light', lang: 'en'}).then(result => {
    console.log('Settings saved:', result.status);
});

// Log messages
pywebview.api.log_message('User clicked button');

// Handle errors
pywebview.api.get_user_data()
    .then(data => console.log(data))
    .catch(error => console.error('API error:', error));
```

**HTML Example (index.html):**
```html
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Hybrid App</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .loading { color: #666; }
    </style>
</head>
<body>
    <h1>Welcome, <span id="username">Loading...</span></h1>
    
    <button onclick="updateSettings()">Update Settings</button>
    <button onclick="pywebview.api.log_message('Test log')">Log Message</button>
    
    <script>
        // Load user data on page load
        window.addEventListener('DOMContentLoaded', () => {
            pywebview.api.get_user_data()
                .then(userData => {
                    document.getElementById('username').textContent = userData.name;
                    console.log('Data loaded:', userData);
                })
                .catch(error => {
                    console.error('Failed to load data:', error);
                    document.getElementById('username').textContent = 'Error';
                });
        });
        
        function updateSettings() {
            const newSettings = {
                theme: 'dark',
                notifications: true
            };
            
            pywebview.api.save_settings(newSettings)
                .then(result => alert('Settings saved!'))
                .catch(error => alert('Save failed: ' + error));
        }
    </script>
</body>
</html>
```

**Pros:**
- Direct Python-JavaScript communication (fast, no HTTP overhead)
- Built-in HTTP server for static files
- Simple file-based deployment
- No external dependencies

**Cons:**
- Static files only (no dynamic routing without custom server)
- Limited to relative paths from entry point

### Pattern 3: Serverless (Inline HTML)

**Best for:** Simple tools, utilities, quick prototypes

```python
import webview

class Api:
    def show_alert(self, message):
        webview.MessageBox.show('Alert', message, webview.MessageBoxType.INFO)
        return True
    
    def get_timestamp(self):
        import datetime
        return datetime.datetime.now().isoformat()

html_content = '''
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Serverless App</title>
    <style>
        body { 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            max-width: 600px; 
            margin: 50px auto; 
            padding: 20px;
        }
        button { 
            padding: 10px 20px; 
            margin: 5px;
            cursor: pointer;
        }
        #timestamp { color: #666; }
    </style>
</head>
<body>
    <h1>Serverless Application</h1>
    <p>No web server required - all HTML is inline!</p>
    
    <button onclick="showAlert()">Show Alert</button>
    <button onclick="updateTime()">Get Timestamp</button>
    
    <p>Current time: <span id="timestamp">-</span></p>
    
    <script>
        function showAlert() {
            pywebview.api.show_alert('Hello from inline HTML!')
                .then(result => console.log('Alert shown'));
        }
        
        function updateTime() {
            pywebview.api.get_timestamp()
                .then(time => {
                    document.getElementById('timestamp').textContent = time;
                });
        }
        
        // Auto-update every second
        setInterval(updateTime, 1000);
    </script>
</body>
</html>
'''

window = webview.create_window(
    title='Serverless Demo',
    html=html_content,
    js_api=Api(),
    width=800,
    height=600
)

webview.start()
```

**Pros:**
- No HTTP server needed
- Simplest deployment (single Python file)
- Fast startup
- Perfect for small tools/utilities

**Cons:**
- No file system access from JavaScript
- All assets must be inline or Base64 encoded
- HTML limited to what fits in Python string
- Not suitable for large applications

### Pattern Comparison

| Feature | External Server | Internal Server + JS API | Serverless |
|---------|----------------|--------------------------|------------|
| Complexity | Medium | Low | Lowest |
| Performance | Medium (HTTP overhead) | High (direct calls) | High |
| File System Access | Yes | Yes (static files) | No |
| Dynamic Content | Yes | Limited | No |
| Deployment Size | Larger | Small | Smallest |
| Best For | Existing web apps | Most applications | Simple tools |

## Web Engine Selection

pywebview supports multiple web renderers. Change the backend with the `gui` parameter:

```python
import webview

# Use default backend for platform
webview.start()

# Force specific backend
webview.start(gui='qt')      # Qt WebEngine
webview.start(gui='gtk')     # GTK WebKit2
webview.start(gui='cef')     # Chromium Embedded Framework (Windows)
webview.start(gui='winforms') # Windows Forms + WebView2
webview.start(gui='webkit')  # macOS WebKit
```

**Backend Recommendations:**
- **Windows:** WinForms (default) or CEF for latest Chromium features
- **macOS:** WebKit (default, native) or Qt for cross-platform consistency
- **Linux:** Qt (modern) or GTK (lightweight)

See [Web Engine Guide](https://pywebview.flowrl.com/guide/web_engine) for detailed backend comparison.

## Freezing and Distribution

### PyInstaller

```bash
pip install pyinstaller
pyinstaller --onefile --windowed your_app.py
```

**Linux additional flags:**
```bash
pyinstaller --onefile --windowed \
    --add-data "static:static" \
    --add-data "templates:templates" \
    your_app.py
```

### Nuitka

```bash
pip install nuitka
python -m nuitka --onefile --windows-disable-console your_app.py
```

### py2app (macOS)

```bash
pip install py2app
python setup.py py2app
```

**setup.py example:**
```python
from setuptools import setup

APP = ['your_app.py']
OPTIONS = {
    'packages': ['webview'],
    'datas': [('static', 'static'), ('templates', 'templates')]
}

setup(
    app=APP,
    options={'py2app': OPTIONS},
    setup_requires=['py2app']
)
```

See [Freezing Guide](https://pywebview.flowrl.com/guide/freezing) for platform-specific bundling instructions.
