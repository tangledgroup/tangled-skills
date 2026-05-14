# Reactivity

## Reactive Attributes

Create reactive attributes using `reactive()` from `textual.reactive`. They auto-refresh the widget when their value changes:

```python
from textual.reactive import reactive
from textual.widget import Widget

class Counter(Widget):
    count = reactive(0)

    def render(self) -> str:
        return f"Count: {self.count}"
```

Get and set like normal attributes: `self.count = 5`, `self.count += 1`.

### Dynamic Defaults

Pass a callable for dynamic defaults evaluated at widget creation time:

```python
from time import time

class Timer(Widget):
    start_time = reactive(time)  # Called when widget is created
```

### Typing

Add type hints when the type is broader than the default value:

```python
name: reactive[str | None] = reactive("default")
```

## var — Non-Refreshing Reactive

Use `var()` when you want reactive superpowers (watch, validate) without auto-refresh:

```python
from textual.reactive import var

class MyWidget(Widget):
    count = var(0)  # Changing this won't trigger render()
```

## Watch Methods

Watch methods observe reactive attribute changes. Name them `watch_<attribute_name>`:

```python
class ColorApp(App):
    color = reactive("white")

    def watch_color(self, old_value: str, new_value: str) -> None:
        print(f"Color changed from {old_value} to {new_value}")
```

Single-argument form receives only the new value. Two-argument form receives old and new.

### When Watch Methods Are Called

Watch methods fire after the attribute value is set but before refresh occurs. If multiple reactive attributes change in the same event loop tick, watch methods fire for each, but refresh is batched into a single update.

## Validation

Validate methods constrain values before they are assigned. Name them `validate_<attribute_name>`:

```python
class BoundedCounter(Widget):
    count = reactive(0)

    def validate_count(self, value: int) -> int:
        return max(0, min(value, 100))  # Clamp to 0-100
```

The validator receives the incoming value and returns the value to actually set. It can transform, reject (raise ValueError), or pass through.

## Layout Trigger

By default, changing a reactive attribute triggers `render()` but not layout recalculation. Set `layout=True` to also trigger layout:

```python
class DynamicWidth(Widget):
    text = reactive("Hello", layout=True)

    def render(self) -> str:
        return self.text
```

This is useful when the content length affects the widget's required size.

## Combining Features

All reactive features compose together:

```python
from textual.reactive import reactive

class TemperatureDisplay(Widget):
    celsius = reactive(20.0, layout=True)

    def validate_celsius(self, value: float) -> float:
        return max(-273.15, value)

    def watch_celsius(self, old: float, new: float) -> None:
        self.border_title = f"{new:.1f}°C"

    def render(self) -> str:
        fahrenheit = self.celsius * 9/5 + 32
        return f"F: {fahrenheit:.1f}°F"
```
