# Debugging and Security Guide

## Debugging Techniques

### JavaScript Console Logging

Enable JavaScript console logging to Python:

```python
import webview

class ConsoleLogger:
    def log(self, message):
        print(f'[JS LOG] {message}')
    
    def error(self, message):
        print(f'[JS ERROR] {message}', file=__import__('sys').stderr)
    
    def warn(self, message):
        print(f'[JS WARN] {message}')

window = webview.create_window(
    'Debug Demo',
    './index.html',
    js_api=ConsoleLogger()
)
webview.start()
```

**JavaScript usage:**

```javascript
// Override console methods
const originalLog = console.log;
const originalError = console.error;
const originalWarn = console.warn;

console.log = function(...args) {
    originalLog.apply(console, args);
    if (window.pywebview && window.pywebview.api) {
        pywebview.api.log(args.map(a => String(a)).join(' '));
    }
};

console.error = function(...args) {
    originalError.apply(console, args);
    if (window.pywebview && window.pywebview.api) {
        pywebview.api.error(args.map(a => String(a)).join(' '));
    }
};

// Now all console.log calls appear in Python console
console.log('This appears in both consoles');
```

### Remote Debugging (Chrome DevTools)

Enable remote debugging for Qt backend:

```python
import webview

# Start with remote debugging enabled
window = webview.create_window(
    'Debug Demo',
    './index.html',
    # Remote debugging args vary by backend
)

# For Qt, use command-line args or environment variables
# See platform-specific sections below
webview.start()
```

**Qt Backend (Linux/Windows):**

Run with debugging flags:
```bash
# Enable Chrome DevTools on port 9222
QTWEBENGINE_CHROMIUM_FLAGS="--remote-debugging-port=9222" python your_app.py
```

Then open: http://localhost:9222 in Chrome/Edge

**CEF Backend (Windows):**

```python
import webview

# CEF supports remote debugging
window = webview.create_window(
    'CEF Debug',
    './index.html'
)

# Start with CEF remote debugging
webview.start(gui='cef')
```

### Inspecting DOM from Python

```python
import webview

window = webview.create_window('DOM Inspector', './index.html')

def on_loaded(window):
    # Get page title
    title = window.evaluate_js('document.title')
    print(f'Page title: {title}')
    
    # Get all elements with a class
    elements = window.get_elements('.my-class')
    print(f'Found {len(elements)} elements with class "my-class"')
    
    # Get element text
    first_element = window.get_first_element('#content')
    if first_element:
        print(f'Content: {first_element.text[:100]}...')
    
    # Inspect specific element
    href = window.get_element_attribute('a.external-link', 'href')
    print(f'External link: {href}')

window.events.loaded += on_loaded
webview.start()
```

### Debugging Window Events

```python
import webview

def log_event(event_name):
    def handler(window):
        print(f'[{event_name}] Window: {window.title}')
    return handler

window = webview.create_window('Event Logger', 'https://example.com')

# Log all events
window.events.closed += log_event('closed')
window.events.closing += log_event('closing')
window.events.loaded += log_event('loaded')
window.events.before_load += log_event('before_load')
window.events.before_show += log_event('before_show')
window.events.shown += log_event('shown')
window.events.minimized += log_event('minimized')
window.events.maximized += log_event('maximized')
window.events.restored += log_event('restored')
window.events.resized += log_event('resized')
window.events.moved += log_event('moved')

webview.start()
```

### Performance Monitoring

```python
import webview
import time

class PerformanceMonitor:
    def __init__(self):
        self.metrics = {}
    
    def measure_js_execution(self, window, script, name):
        start = time.time()
        try:
            result = window.evaluate_js(script)
            elapsed = time.time() - start
            self.metrics[name] = elapsed
            print(f'{name}: {elapsed*1000:.2f}ms')
            return result
        except Exception as e:
            print(f'{name} failed: {e}')
            return None

monitor = PerformanceMonitor()

window = webview.create_window('Performance', './index.html')

def on_loaded(window):
    # Measure various operations
    monitor.measure_js_execution(
        window,
        'document.querySelectorAll("*").length',
        'DOM query'
    )
    
    monitor.measure_js_execution(
        window,
        'JSON.stringify({test: "data", count: 123})',
        'JSON stringify'
    )

window.events.loaded += on_loaded
webview.start()
```

## Platform-Specific Debugging

### Windows

**WebView2 DevTools:**

```python
import webview

# Enable WebView2 debugging
import os
os.environ['WEBVIEW2_ADDITIONAL_ARGS'] = '--remote-debugging-port=9222'

window = webview.create_window('Windows Debug', './index.html')
webview.start()
```

Then open: http://localhost:9222

**View WebView2 Logs:**

WebView2 logs are located at:
- `%LOCALAPPDATA%\Microsoft\EdgeWebview2\Application\<version>\User Data\Default\Logs\`

### macOS

**WebKit Debugging:**

```bash
# Enable WebKit debugging
export WEBKIT_DISABLE_COMPOSITING_MODE=1
python your_app.py
```

**Console App Logs:**

Open Console.app and filter by your application name to see WebKit logs.

### Linux

**QtWebEngine Debugging:**

```bash
# Enable verbose logging
QT_LOGGING_RULES="qt.webengine*=true" python your_app.py

# Or enable Chrome flags
QTWEBENGINE_CHROMIUM_FLAGS="--enable-logging=stderr --v=1" python your_app.py
```

**GTK WebKit2 Debugging:**

```bash
# Enable GTK debugging
GTK_DEBUG=interactive python your_app.py

# Enable WebKit logging
GST_DEBUG=*:5 python your_app.py
```

## Common Issues and Solutions

### "Module not found" Errors

**Issue:** `ModuleNotFoundError: No module named 'webview'` or backend-specific errors

**Solutions:**

1. **Install pywebview:**
   ```bash
   pip install pywebview
   ```

2. **Linux - Install platform dependencies:**
   ```bash
   # For Qt
   sudo apt install python3-pyqt5 python3-pyqt5.qtwebengine
   
   # For GTK
   sudo apt install python3-gi python3-gi-cairo gir12-gtk-3.0 gir12-webkit2-4.0
   ```

3. **Windows - Install WebView2 Runtime:**
   - Download from: https://developer.microsoft.com/en-us/microsoft-edge/webview2/
   - Or use CEF backend: `pip install pywebview[cef]`

4. **macOS - Install PyObjC:**
   ```bash
   pip install pyobjc-core pyobjc-framework-Cocoa pyobjc-framework-WebKit
   ```

### Window Appears Blank

**Issue:** Window opens but shows blank/white screen

**Debugging steps:**

```python
import webview

window = webview.create_window('Debug', './index.html')

def on_loaded(window):
    print('Page loaded!')
    
    # Check if content loaded
    title = window.evaluate_js('document.title')
    print(f'Title: {title}')
    
    # Check for errors
    body_html = window.evaluate_js('document.body.innerHTML.substring(0, 200)')
    print(f'Body (first 200 chars): {body_html}')
    
    # Try loading external URL
    # window.load_url('https://example.com')

window.events.loaded += on_loaded

def on_before_load(window):
    print('About to load page...')

window.events.before_load += on_before_load

webview.start()
```

**Common causes:**
1. **File path issues:** Use absolute paths or ensure relative path is correct
   ```python
   import os
   abs_path = os.path.abspath('./index.html')
   window = webview.create_window('App', abs_path)
   ```

2. **JavaScript errors blocking render:** Check console logs
3. **CSS hiding content:** Inspect with DevTools
4. **Wrong MIME type:** Built-in server should handle this automatically

### JavaScript Exceptions

**Issue:** `webview.errors.JavascriptException` raised

**Solution - Proper error handling:**

```python
import webview

window = webview.create_window('Error Handling', './index.html')

def safe_js_execution(script):
    try:
        result = window.evaluate_js(script)
        print(f'Success: {result}')
        return result
    except webview.errors.JavascriptException as e:
        print(f'JavaScript error: {e}')
        print(f'Error name: {e.name}')
        print(f'Error message: {e.message}')
        return None
    except Exception as e:
        print(f'Unexpected error: {e}')
        return None

# Test with valid and invalid JS
safe_js_execution('2 + 2')  # Success
safe_js_execution('nonExistentFunction()')  # Error handled gracefully

webview.start()
```

### HTTPS/SSL Errors

**Issue:** SSL certificate errors with local server

**Solution 1 - Install SSL support:**
```bash
pip install pywebview[ssl]
```

**Solution 2 - Use HTTP for development:**
```python
# Disable SSL verification (development only!)
import ssl
ssl._create_default_https_context = ssl._create_unverified_context
```

**Solution 3 - Self-signed certificate:**
```python
from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import rsa
import webview

# Generate self-signed cert (do this once and save)
# Then use with your local server
```

### Multiple Windows Communication

**Issue:** Need to communicate between multiple windows

**Solution - Shared state via Python:**

```python
import webview

class SharedState:
    def __init__(self):
        self.data = {}
        self.listeners = []
    
    def set_value(self, key, value):
        self.data[key] = value
        # Notify all windows
        for window in webview.windows:
            try:
                window.evaluate_js(f'window.onDataUpdate({{key: "{key}", value: {value}}})')
            except:
                pass
        return True
    
    def get_value(self, key):
        return self.data.get(key)

state = SharedState()

# Create multiple windows with shared state
window1 = webview.create_window('Window 1', './index.html', js_api=state)
window2 = webview.create_window('Window 2', './index.html', js_api=state)

webview.start()
```

**JavaScript listener:**

```javascript
// In each window's HTML
window.onDataUpdate = function(data) {
    console.log('Data updated:', data);
    // Update UI based on new data
};
```

## Security Considerations

### Input Validation

Always validate JavaScript-provided data:

```python
import webview
import re
from functools import wraps

def validate_input(max_length=1000, allowed_pattern=None):
    """Decorator for validating input from JavaScript"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Validate string arguments
            for arg in args:
                if isinstance(arg, str):
                    if len(arg) > max_length:
                        raise ValueError(f"Input too long: {len(arg)} > {max_length}")
                    if allowed_pattern and not re.match(allowed_pattern, arg):
                        raise ValueError(f"Input doesn't match pattern: {arg}")
            return func(*args, **kwargs)
        return wrapper
    return decorator

class SecureApi:
    @validate_input(max_length=100, allowed_pattern=r'^[a-zA-Z0-9_]+$')
    def get_user_profile(self, username):
        """Get user profile with validated username"""
        # Safe to use - input is validated
        return {'username': username, 'exists': True}
    
    @validate_input(max_length=500)
    def process_text(self, text):
        """Process text input with length validation"""
        return text.upper()
    
    def dangerous_operation(self, user_input):
        """Example of what NOT to do - always validate!"""
        # ❌ Never trust JavaScript input directly
        # This could lead to injection attacks
        pass

### CSRF Protection

When using external web servers, protect against CSRF:

```python
from flask import Flask, request, session
import secrets

app = Flask(__name__)
app.secret_key = secrets.token_hex(32)

# Generate CSRF token
def generate_csrf_token():
    if '_csrf_token' not in session:
        session['_csrf_token'] = secrets.token_hex(32)
    return session['_csrf_token']

# Verify CSRF token
def verify_csrf_token(token):
    return session.get('_csrf_token') == token

@app.route('/api/data', methods=['POST'])
def handle_data():
    token = request.form.get('csrf_token')
    if not verify_csrf_token(token):
        return {'error': 'CSRF token invalid'}, 403
    
    # Process request safely
    return {'status': 'success'}

window = webview.create_window('Secure App', app)
webview.start()
```

### Content Security Policy (CSP)

Implement CSP to prevent XSS:

```python
from flask import Flask, Response

app = Flask(__name__)

@app.after_request
def add_security_headers(response):
    # Content Security Policy
    response.headers['Content-Security-Policy'] = (
        "default-src 'self'; "
        "script-src 'self'; "
        "style-src 'self' 'unsafe-inline'; "
        "img-src 'self' data: https:;"
    )
    
    # Other security headers
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    
    return response

window = webview.create_window('Secure', app)
webview.start()
```

### Sandboxing JavaScript

Limit JavaScript capabilities:

```python
import webview

class SandboxedApi:
    """Limited API surface exposed to JavaScript"""
    
    # Only expose specific safe methods
    def get_greeting(self, name):
        # Validate and sanitize input
        if not isinstance(name, str) or len(name) > 50:
            raise ValueError("Invalid name")
        name = ''.join(c for c in name if c.isalnum() or c == ' ')
        return f"Hello, {name}!"
    
    def calculate(self, a, b, operation):
        """Safe calculator - only allows specific operations"""
        allowed_ops = {'add': lambda x, y: x + y,
                      'subtract': lambda x, y: x - y,
                      'multiply': lambda x, y: x * y,
                      'divide': lambda x, y: x / y if y != 0 else None}
        
        if operation not in allowed_ops:
            raise ValueError(f"Operation not allowed: {operation}")
        
        result = allowed_ops[operation](a, b)
        return result
    
    # Don't expose dangerous methods like:
    # - os.system()
    # - subprocess.run()
    # - file system access (except through controlled APIs)
    # - network requests (except through controlled APIs)

window = webview.create_window('Sandboxed', './index.html', js_api=SandboxedApi())
webview.start()
```

### Secure File Operations

Control file access through safe APIs:

```python
import webview
import os
from pathlib import Path

class SafeFileApi:
    def __init__(self, allowed_base_path):
        self.base_path = Path(allowed_base_path).resolve()
    
    def read_file(self, relative_path):
        """Read file with path validation"""
        # Prevent directory traversal
        target = (self.base_path / relative_path).resolve()
        
        if not str(target).startswith(str(self.base_path)):
            raise PermissionError(f"Access denied: {relative_path}")
        
        if not target.is_file():
            raise FileNotFoundError(f"File not found: {relative_path}")
        
        with open(target, 'r') as f:
            return f.read()
    
    def list_directory(self, relative_path='.'):
        """List directory contents safely"""
        target = (self.base_path / relative_path).resolve()
        
        if not str(target).startswith(str(self.base_path)):
            raise PermissionError(f"Access denied: {relative_path}")
        
        if not target.is_dir():
            raise NotADirectoryError(f"Not a directory: {relative_path}")
        
        return [f.name for f in target.iterdir()]

# Restrict to specific directory
file_api = SafeFileApi('/app/data')
window = webview.create_window('Secure Files', './index.html', js_api=file_api)
webview.start()

### Security Checklist

- [ ] Validate all JavaScript input before processing
- [ ] Sanitize output to prevent XSS when returning HTML
- [ ] Implement CSRF protection for external servers
- [ ] Use Content Security Policy headers
- [ ] Limit API surface - only expose necessary methods
- [ ] Restrict file system access to safe directories
- [ ] Avoid executing shell commands from JavaScript input
- [ ] Use HTTPS for production applications
- [ ] Keep pywebview and dependencies updated
- [ ] Review security implications of third-party JavaScript libraries

## Troubleshooting Checklist

### Installation Issues

1. **Check Python version:** pywebview requires Python 3.7+
   ```bash
   python --version
   ```

2. **Verify platform dependencies:**
   - Windows: .NET Framework 4.0+, WebView2 Runtime
   - macOS: PyObjC frameworks
   - Linux: Qt or GTK libraries

3. **Try alternative backend:**
   ```python
   webview.start(gui='qt')  # or 'gtk', 'cef', etc.
   ```

### Runtime Issues

1. **Check for JavaScript errors:**
   - Enable console logging to Python
   - Use remote debugging (DevTools)
   - Add error handlers in JavaScript

2. **Verify file paths:**
   - Use absolute paths during development
   - Check working directory: `print(os.getcwd())`
   - Ensure files exist before loading

3. **Test with simple example:**
   ```python
   import webview
   webview.create_window('Test', 'https://example.com')
   webview.start()
   ```
   If this works, issue is application-specific

4. **Check window events:**
   - Add event handlers to track lifecycle
   - Verify `loaded` event fires
   - Check for `closing` event issues

### Performance Issues

1. **Profile JavaScript execution:**
   ```python
   import time
   start = time.time()
   result = window.evaluate_js('heavyComputation()')
   print(f'Execution time: {time.time() - start:.2f}s')
   ```

2. **Reduce API call frequency:**
   - Batch operations when possible
   - Cache results in JavaScript
   - Use debouncing for frequent updates

3. **Check memory usage:**
   - Monitor with system tools
   - Close unused windows
   - Clear JavaScript caches

## Additional Resources

- **Official Documentation:** https://pywebview.flowrl.com/
- **GitHub Issues:** https://github.com/r0x0r/pywebview/issues
- **Examples Repository:** https://github.com/r0x0r/pywebview/tree/master/examples
- **Changelog:** https://pywebview.flowrl.com/changelog
- **Community Support:** Check GitHub Discussions for help
```
```