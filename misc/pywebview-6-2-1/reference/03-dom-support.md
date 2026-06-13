# DOM Support

Starting from version 5.0, pywebview supports basic DOM manipulation, traversal, and event handling directly from Python — without writing JavaScript.

## Accessing Elements

```python
# Get document, body, window as Element objects
body = window.dom.body
document = window.dom.document
win = window.dom.window

# Query by CSS selector
element = window.dom.get_element('#my-id')       # First match or None
elements = window.dom.get_elements('div.item')    # List of matches
```

## Creating Elements

```python
# Create from HTML string, append to body as last child
element = window.dom.create_element('<div>new element</div>')

# Insert into a specific parent
element = window.dom.create_element(
    '<h1>Warning</h1>',
    parent='#container',
    mode=webview.dom.ManipulationMode.FirstChild
)
```

### ManipulationMode

Controls where the new element is inserted:

- `LastChild` — appended as last child (default)
- `FirstChild` — inserted as first child
- `Before` — inserted before target
- `After` — inserted after target
- `Replace` — replaces target

## Element Properties

### Read-only

```python
element.tag        # Tag name, e.g. 'div'
element.children   # List of child Element objects
element.parent     # Parent Element or None
element.next       # Next sibling or None
element.previous   # Previous sibling or None
element.visible    # Whether element is visible (bool)
element.focused    # Whether element is focused (bool)
```

### Read-write

```python
element.id = 'new-id'              # Get/set element id
element.text = 'New content'       # Get/set text content
element.value = 'input value'      # Get/set value (input elements only)
element.tabindex = 108             # Get/set tabindex
```

### Attributes (dict-like)

```python
# Set attribute
element.attributes['data-flag'] = '1337'

# Remove attribute
element.attributes['id'] = None
del element.attributes['data-flag']
```

### Classes (list-like with toggle)

```python
# Overwrite all classes
element.classes = ['container', 'red', 'dotted']

# Individual operations
element.classes.add('blue')
element.classes.remove('red')
element.classes.toggle('dotted')
element.classes.clear()
```

### Styles (dict-like)

```python
element.style['width'] = '100px'
element.style['display'] = 'flex'

# Reset a style
element.style['width'] = None
del element.style['display']
```

## Element Manipulation

```python
# Copy element
copy = element.copy()                                    # Copy as parent's last child
copy = element.copy('#target', webview.dom.ManipulationMode.Before, 'new-id')

# Move element
element.move('#new-container')                           # As last child
element.move(target_element, webview.dom.ManipulationMode.FirstChild)

# Remove element
element.remove()

# Empty container
container.empty()

# Append HTML
container.append('<span>new content</span>')
container.append('<span>more</span>', mode=webview.dom.ManipulationMode.FirstChild)
```

## Element Visibility and Focus

```python
element.hide()     # Sets display: none
element.show()     # Restores previous display or sets display: block
element.toggle()   # Toggle visibility

element.focus()    # Focus the element
element.blur()     # Remove focus
```

## DOM Events from Python

Subscribe to any DOM event directly from Python using `+=` or `.on()`:

```python
def on_click(e):
    print('Clicked!', e)

# Two equivalent ways to subscribe
element.events.click += on_click
element.on('click', on_click)

# Unsubscribe
element.events.click -= on_click
element.off('click', on_click)
```

### DOMEventHandler for Advanced Control

Use `webview.dom.DOMEventHandler` to control event propagation and debouncing:

```python
from webview.dom import DOMEventHandler

def on_drag(e):
    print('Drag event')

# Prevent default, stop propagation, debounce 500ms
window.dom.document.events.dragover += DOMEventHandler(
    on_drag,
    prevent_default=True,
    stop_propagation=True,
    stop_immediate_propagation=True,
    debounce=500
)
```

Parameters:

- `callback` — The handler function
- `prevent_default` — Call `event.preventDefault()` (default: False)
- `stop_propagation` — Call `event.stopPropagation()` (default: False)
- `stop_immediate_propagation` — Call `event.stopImmediatePropagation()` (default: False)
- `debounce` — Debounce in milliseconds. Useful for high-frequency events like `dragover`, `mouseover`

### File Drop with Full Path

pywebview enhances the `drop` event to include full file paths on the Python side:

```python
def on_drop(e):
    # Access dropped file's full path
    file_path = e['dataTransfer']['files'][0]['pywebviewFullPath']
    print(f'Dropped file: {file_path}')

window.dom.document.events.drop += DOMEventHandler(
    on_drop,
    prevent_default=True,
    stop_propagation=True
)
```

## Complete Example

```python
import webview

html = '''
<div id="container">
    <p class="item">Item 1</p>
    <p class="item">Item 2</p>
</div>
<button id="add-btn">Add Item</button>
'''

def on_loaded(window):
    container = window.dom.get_element('#container')

    # Add a new item
    container.append('<p class="item">Item 3</p>')

    # Style the button
    btn = window.dom.get_element('#add-btn')
    btn.style['background'] = '#4CAF50'
    btn.style['color'] = 'white'

    # Subscribe to click
    def on_add_click(e):
        container.append('<p class="item">New Item</p>')

    btn.events.click += on_add_click

window = webview.create_window('DOM Demo', html=html)
window.events.loaded += on_loaded
webview.start()
```
