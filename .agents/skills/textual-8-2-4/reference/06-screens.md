# Screens

## Screen Basics

Screens are full-terminal containers for widgets. Only one screen is active at a time (receives input and renders). Textual creates a default Screen implicitly if none is defined.

Create screens by subclassing `Screen`:

```python
from textual.screen import Screen
from textual.widgets import Static

class GameScreen(Screen):
    def compose(self) -> ComposeResult:
        yield Static("Game area")
```

## Screen Stack

Textual maintains a stack of screens — like sheets of paper where only the top is visible. The App class provides methods to manipulate the stack:

**push_screen** — add screen on top (makes it active):
```python
self.push_screen("settings")
# or
self.push_screen(SettingsScreen())
```

**pop_screen** — remove top screen (reveals the one below):
```python
self.pop_screen()
```

**switch_screen** — replace top screen with another:
```python
self.switch_screen("game")
```

The stack must always have at least one screen. Attempting to pop the last screen raises `ScreenStackError`.

## Named Screens

Register screens with names via `SCREENS` class variable:

```python
class MyApp(App):
    SCREENS = {
        "settings": SettingsScreen,
        "game": GameScreen,
    }
```

Or install dynamically:
```python
self.install_screen(GameScreen(), name="game")
```

Uninstall to clean up:
```python
self.uninstall_screen("game")
```

## Modal Screens

Create modal overlays using screen opacity. Set a semi-transparent background to let the underlying screen show through:

```python
class ConfirmDialog(Screen):
    CSS = """
    Screen {
        background: rgba(0, 0, 0, 0.6);
        align: center middle;
    }
    #dialog {
        width: 40;
        background: $surface;
        border: tall $primary;
        padding: 1 2;
    }
    """

    def compose(self) -> ComposeResult:
        yield Container(
            Static("Are you sure?"),
            Horizontal(
                Button("Yes", variant="success"),
                Button("No", variant="error"),
            ),
            id="dialog",
        )

    def on_button_pressed(self) -> None:
        self.app.pop_screen()
```

Push with `self.push_screen(ConfirmDialog())`. Only the top screen receives input, even though the bottom screen is partially visible.

## Screen Actions

Use action strings for screen navigation in bindings:

```python
BINDINGS = [
    ("s", "app.push_screen('settings')", "Settings"),
    ("escape", "app.pop_screen", "Back"),
    ("g", "app.switch_screen('game')", "Game"),
]
```

## Screen Events

Handle screen lifecycle events:

```python
class MyScreen(Screen):
    def on_screen_resume(self) -> None:
        # Screen became active
        ...

    def on_screen_suspend(self) -> None:
        # Screen was covered
        ...
```

## Return Values from Screens

Pop a screen with a return value:

```python
class QuestionScreen(Screen[str]):
    def on_button_pressed(self, event: Button.Pressed) -> None:
        self.pop_screen(event.button.id)

# In the app
result = await self.push_screen(QuestionScreen())
print(f"User chose: {result}")
```
