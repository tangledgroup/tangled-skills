# Quick Start

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

See [JS API Integration](reference/02-js-api.md) for detailed examples.
