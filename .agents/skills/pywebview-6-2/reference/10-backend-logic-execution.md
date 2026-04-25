# Backend Logic Execution

Since `webview.start()` blocks until all windows close, run backend code in separate threads:

### Method 1: Pass function to start()

```python
import webview
import time

def background_task(window):
    while True:
        time.sleep(5)
        window.evaluate_js('updateStatus("Still running...")')

window = webview.create_window('Background Task', './index.html')
webview.start(background_task, window)
```

### Method 2: Manual threading

```python
import webview
import threading
import time

def background_worker():
    while True:
        time.sleep(1)
        # Update UI from main thread
        webview.windows[0].evaluate_js('updateCounter()')

window = webview.create_window('Worker', './index.html')
thread = threading.Thread(target=background_worker, daemon=True)
thread.start()
webview.start()
```

### Method 3: Async/await with asyncio

```python
import webview
import asyncio

async def async_task(window):
    while True:
        await asyncio.sleep(5)
        window.evaluate_js('fetchNewData()')

window = webview.create_window('Async', './index.html')
webview.start(lambda w: asyncio.run(async_task(w)), window)
```
