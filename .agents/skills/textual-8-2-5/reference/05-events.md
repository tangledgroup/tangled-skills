# Events and Messages

## Message Queue Model

Every App and Widget has its own asyncio message queue. Messages are dispatched one at a time by the widget's background task. This ensures orderly processing even under high event volume.

Each widget runs in its own asyncio task, started when the widget is mounted.

## Event Handlers

Two ways to define handlers:

**Naming convention** — `on_<namespace>_<message>`:
```python
def on_key(self, event: Key) -> None:
    ...

def on_input_changed(self, event: Input.Changed) -> None:
    ...
```

**@on decorator** — explicit message type:
```python
from textual import on

@on(Button.Pressed)
def handle_click(self, event: Button.Pressed) -> None:
    ...
```

The decorator approach lets you name the method freely and can target specific widgets via CSS selectors.

## Handler Naming Rules

Handler names are derived from the message class:

1. Start with `on_`
2. Add namespace (parent class name in snake_case + `_`) if the message is a nested class
3. Add message class name in snake_case

Examples:
- `Key` event → `on_key`
- `Input.Changed` → `on_input_changed`
- `Button.Pressed` → `on_button_pressed`

Check handler name at runtime: `Input.Changed.handler_name` returns `'on_input_changed'`.

## Bubbling

Messages bubble up the DOM by default. A `Key` event received by a focused Button bubbles to its parent Container, then to Screen, then to App. Each level can handle it.

Stop bubbling with `event.stop()`:
```python
def on_key(self, event: Key) -> None:
    if event.key == "enter":
        event.stop()  # Don't let parent see this
```

## Preventing Default Behaviors

Base class handlers run automatically after your handler. Call `event.prevent_default()` to skip them:

```python
def on_key(self, event: Key) -> None:
    event.prevent_default()  # Skip Widget.on_key
```

Use sparingly — base class handlers often implement core functionality.

## Custom Messages

Define custom messages as nested classes extending `Message`:

```python
from textual.message import Message
from textual.widget import Widget

class ColorButton(Widget):
    class Selected(Message):
        def __init__(self, color: str) -> None:
            self.color = color
            super().__init__()

    def on_click(self) -> None:
        self.post_message(self.Selected("red"))
```

Handler in parent: `on_color_button_selected(self, message: ColorButton.Selected)`.

## Posting and Preventing Messages

Post messages with `post_message()`:
```python
self.post_message(self.MyMessage(data))
```

Temporarily prevent specific message types with the `prevent()` context manager:
```python
with self.prevent(Input.Changed):
    self.query_one(Input).value = ""  # No Changed event fired
```

## Common Event Types

**Keyboard:**
- `Key` — key press (attributes: `key`, `character`, `name`, `is_printable`)

**Mouse:**
- `Click` — mouse click
- `MouseDown`, `MouseUp` — button press/release
- `MouseMove` — cursor movement
- `MouseScrollUp`, `MouseScrollDown` — scroll wheel

**Focus:**
- `Focus` — widget gained focus
- `Blur` — widget lost focus

**Lifecycle:**
- `Mount` — widget added to DOM
- `Unmount` — widget removed from DOM
- `Show` / `Hide` — visibility changes
- `Resize` — terminal size changed
- `Load` — widget initialized

**Screen:**
- `ScreenResume` — screen became active
- `ScreenSuspend` — screen was covered by another

## @on with Widget Filtering

The `@on` decorator can filter by CSS selector to handle messages from specific widgets:

```python
@on(Button.Pressed, "#submit")
def on_submit(self, event: Button.Pressed) -> None:
    ...  # Only fires for button with id="submit"
```
