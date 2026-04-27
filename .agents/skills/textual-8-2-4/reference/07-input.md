# Input Handling

## Key Events

Key events are sent to the focused widget. The `Key` event contains:

- `key` — string identifier (e.g., `"a"`, `"enter"`, `"ctrl+c"`)
- `character` — single printable character or `None`
- `name` — Python-safe version of key (`"ctrl_c"`, `"upper_a"`)
- `is_printable` — whether the key produces printable output
- `aliases` — list of possible key sources (e.g., `["tab", "ctrl+i"]`)

Handle with `on_key`:
```python
def on_key(self, event: Key) -> None:
    if event.key == "enter":
        self.bell()
```

Or use key methods (convenience):
```python
def key_enter(self) -> None:
    self.bell()
```

## Focus Management

Only one widget receives key events at a time. The focused widget is visually indicated (use `:focus` pseudo-class in CSS).

Tab moves focus to the next focusable widget. Shift+Tab moves backward.

Control focus programmatically:
```python
self.query_one("#name-input", Input).focus()
```

Widgets have a `can_focus` attribute. Set `can_focus=False` to exclude from focus cycling.

Focus events:
```python
def on_focus(self) -> None:
    # Widget gained focus
    ...

def on_blur(self) -> None:
    # Widget lost focus
    ...
```

## Key Bindings

Define bindings with `BINDINGS` class variable — list of `(key, action, description)` tuples:

```python
class MyApp(App):
    BINDINGS = [
        ("q", "quit", "Quit"),
        ("r", "refresh", "Refresh"),
        ("ctrl+s", "save", "Save"),
    ]

    def action_refresh(self) -> None:
        ...

    def action_save(self) -> None:
        ...
```

Bindings can be defined on App, Screen, or individual Widgets. The Footer widget automatically displays active bindings.

## Mouse Events

Handle mouse interactions:

```python
def on_click(self, event: Click) -> None:
    ...

def on_mouse_move(self, event: MouseEvent) -> None:
    ...

def on_mouse_scroll_down(self) -> None:
    ...
```

Mouse events include `offset` (position relative to widget) and `shift`/`meta`/`control` modifier flags.

## Action Strings

Actions are invoked via string syntax, not Python eval. Valid formats:

- `"bell"` — calls `action_bell()`
- `"set_color('red')"` — calls `action_set_color("red")`
- `"app.quit"` — calls action on App namespace

Parameters must be Python literals (strings, numbers, lists, dicts) — no variables.

Run actions programmatically:
```python
await self.run_action("set_color('blue')")
```
