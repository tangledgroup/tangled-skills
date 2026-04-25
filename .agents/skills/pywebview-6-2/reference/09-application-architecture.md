# Application Architecture

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

See [JS API Integration](reference/02-js-api.md) for complete guide.

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

See [Architecture Patterns](reference/01-installation.md) for detailed comparison.
