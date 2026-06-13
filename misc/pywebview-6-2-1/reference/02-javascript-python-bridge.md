# JavaScript-Python Bridge

pywebview provides two-way communication between JavaScript and Python without requiring an HTTP server.

## Shared State (6.0+)

The `window.state` object (Python) and `pywebview.state` object (JavaScript) share data automatically. Changes on either side propagate to the other.

```python
# Python
window.state.counter = 0
window.state.message = 'Hello'
```

```javascript
// JavaScript
pywebview.state.counter++;
console.log(pywebview.state.message);  // 'Hello'
```

**Rules:**

- Only top-level property changes are propagated. Mutating nested objects does not sync
- State is specific to its window and preserved between page loads
- Both dot notation (`state.key`) and index notation (`state['key']`) are supported
- Binary data should be passed as Base64

### Subscribing to State Changes (Python)

```python
def on_change(event_type, key, value):
    # event_type: 'change' or 'delete'
    # key: property name
    # value: new value (None for delete events)
    print(f'{event_type}: {key} = {value}')

window.state += on_change
```

### Subscribing to State Changes (JavaScript)

```javascript
pywebview.state.addEventListener('change', (e) => {
    console.log(e.detail); // { key, value }
});

pywebview.state.addEventListener('delete', (e) => {
    console.log(e.detail.key);
});
```

### Full Example

```python
import webview

html = '''
<button onclick="pywebview.state.counter++">Increment from JS</button>
<span id="counter"></span>
<script>
  window.addEventListener('pywebviewready', () => {
    pywebview.state.addEventListener('change', e => {
      document.getElementById('counter').innerText = pywebview.state.counter;
    });
  });
</script>
'''

def decrease_counter():
    window.state.counter -= 1

def on_loaded(window):
    window.expose(decrease_counter)

window = webview.create_window('State Demo', html=html)
window.state.counter = 0
window.events.loaded += on_loaded
webview.start()
```

## Running JavaScript from Python

### window.evaluate_js(script, callback=None)

Execute JavaScript and return the result of the last evaluated expression. Uses `eval` internally.

```python
result = window.evaluate_js('2 + 2')  # Returns 4

# With DOM
title = window.evaluate_js('document.title')

# With promise (callback)
def on_result(result):
    print(result)

window.evaluate_js('fetch("/api/data").then(r => r.json())', callback=on_result)
```

JavaScript types are converted to Python types: objects to dicts, arrays to lists, undefined to None. DOM nodes are serialized with custom serialization (functions omitted, circular references become `[Circular Reference]`).

If JavaScript throws an error, `webview.errors.JavascriptException` is raised.

### window.run_js(code)

Execute JavaScript as-is without wrapping in `eval`. Does not return a result. Useful when `unsafe-eval` CSP is set.

```python
window.run_js('document.body.style.color = "deepred"')
```

## Running Python from JavaScript

### Method 1: js_api Parameter

Pass a Python class instance to `create_window`. All public methods are exposed under `pywebview.api`.

```python
import webview

class Api:
    def greet(self, name):
        return f'Hello, {name}!'

    def add(self, a, b):
        return a + b

# Nested classes are supported
class MathApi:
    def square(self, x):
        return x * x

class RootApi:
    math = MathApi()

webview.create_window('API', html='...', js_api=RootApi())
webview.start()
```

```javascript
// In JavaScript
pywebview.api.greet('World').then(result => console.log(result));
pywebview.api.math.square(5).then(result => console.log(result));  // 25
```

**Rules:**

- Methods must not start with underscore (`_`)
- Class attributes starting with `_` are not exposed
- Nested classes with `_serializable = False` are omitted from exposure
- Exposed functions return a Promise resolved to the result
- Exceptions are rejected as JavaScript Error objects (stack trace available via `error.stack`)
- Only basic Python types can be returned (int, str, dict, list, bool, None)
- Functions execute in separate threads — they are not thread-safe

### Method 2: window.expose(func)

Expose individual functions at runtime:

```python
import webview

def my_function(x):
    return x * 2

window = webview.create_window('Dynamic API', html='...')

# Expose during runtime (e.g., after page loads)
def on_loaded(window):
    window.expose(my_function)

window.events.loaded += on_loaded
webview.start()
```

```javascript
// In JavaScript — available as pywebview.api.my_function
pywebview.api.my_function(21).then(result => console.log(result));  // 42
```

If there is a name clash between `js_api` and `expose`, the exposed function takes precedence.

## pywebviewready Event

`pywebview.api` is not guaranteed to be available on `window.onload`. Subscribe to `pywebviewready` instead:

```javascript
window.addEventListener('pywebviewready', () => {
    // pywebview.api is now ready
    pywebview.api.someMethod().then(result => {
        console.log(result);
    });
});
```

## CSRF Token

`webview.token` (Python) and `window.pywebview.token` (JavaScript) provide a session-unique token for securing REST APIs against CSRF attacks.

```python
# Python side — validate incoming requests
import webview

expected_token = webview.token
```

```javascript
// JavaScript side — include in requests
fetch('/api/action', {
    method: 'POST',
    headers: { 'X-CSRF-Token': window.pywebview.token }
});
```

## Platform Property

`window.pywebview.platform` returns the current renderer in use (e.g., `'edgechromium'`, `'webkit'`, `'gtk'`).
