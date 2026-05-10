---
name: textual-8-2-5
description: Python framework for building terminal and browser UIs. Provides widget-based DOM, CSS styling (.tcss), reactive attributes, event system, Workers API for concurrency, command palette, and theming. Use when building terminal UIs, CLI tools with rich interfaces, data dashboards, interactive forms, or any Python application requiring a graphical interface in the terminal.
license: MIT
author: Tangled <noreply@tangledgroup.com>
version: "0.1.0"
tags:
  - tui
  - terminal-ui
  - python
  - framework
  - reactive
  - widgets
  - css
category: framework
external_references:
  - https://github.com/Textualize/textual
  - https://textual.textualize.io/
---

# Textual 8.2.5

## Overview

Textual is a Rapid Application Development (RAD) framework for Python, built by Textualize.io. It lets you build sophisticated user interfaces with a simple Python API that run in the terminal or a web browser (via textual-serve). Textual runs on Linux, macOS, Windows, and any OS where Python runs — including single-board computers and over SSH.

Key characteristics:

- **Widget-based DOM** — hierarchical tree of widgets, each managing a rectangular screen region
- **CSS styling** — `.tcss` files with selectors, pseudo-classes, and theme variables (`$primary`, `$surface`)
- **Reactive attributes** — auto-refresh on value change, with watch/validate hooks
- **Event/message system** — asyncio-powered message queues per widget, bubbling, custom messages
- **Screen stack** — push/pop/switch screens for modal dialogs and navigation
- **Workers API** — background coroutines and threads with state tracking
- **Command palette** — built-in `Ctrl+P` palette for actions and theme switching
- **Inline mode** — run apps beneath the shell prompt (non-fullscreen)
- **Devtools** — live CSS editing, console logging via `textual run --dev`
- **ANSI themes** — new in 8.2.5: `ansi-dark` and `ansi-light` themes with `ansi` color mode

## When to Use

- Building terminal user interfaces (TUIs) with Python
- Creating interactive CLI tools that need buttons, forms, tables, or trees
- Developing data dashboards or monitoring displays in the terminal
- Prototyping UIs rapidly without browser tooling
- Building apps that must run over SSH or on low-resource hardware
- Creating cross-platform terminal apps (Linux, macOS, Windows)

## Core Concepts

### App and Widgets

Every Textual application starts by subclassing `App`. Widgets are components that manage portions of the screen. The app composes widgets via a `compose()` generator method:

```python
from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Static

class MyApp(App):
    def compose(self) -> ComposeResult:
        yield Header()
        yield Static("Hello, Textual!")
        yield Footer()

if __name__ == "__main__":
    MyApp().run()
```

### CSS Styling (TCSS)

Textual uses a CSS-like language in `.tcss` files to style widgets. Reference external stylesheets with `CSS_PATH`:

```python
class MyApp(App):
    CSS_PATH = "my_app.tcss"
```

Or embed inline:

```python
class MyApp(App):
    CSS = """
    Screen {
        align: center middle;
    }
    Static {
        color: green;
        text-style: bold;
    }
    """
```

CSS selectors include type (`Button`), ID (`#submit`), class (`.active`), and pseudo-classes (`:focus`, `:disabled`).

### Reactive Attributes

Reactive attributes auto-refresh the widget when changed. Create them with `reactive()` from `textual.reactive`:

```python
from textual.reactive import reactive
from textual.widget import Widget

class Counter(Widget):
    count = reactive(0)

    def render(self) -> str:
        return f"Count: {self.count}"
```

Use `var()` for reactive attributes that should not trigger refresh. Use `watch_<name>()` methods to observe changes, and `validate_<name>()` methods to constrain values.

### Events and Messages

Textual uses an asyncio message queue per widget. Event handlers use the `on_<event_name>` naming convention or the `@on(Event)` decorator:

```python
from textual import on
from textual.widgets import Button

class MyApp(App):
    @on(Button.Pressed)
    def handle_click(self, event: Button.Pressed) -> None:
        self.bell()
```

Messages bubble up the DOM tree by default. Call `event.stop()` to prevent bubbling, or `event.prevent_default()` to skip base class handlers.

### Key Bindings

Define key bindings with a `BINDINGS` class variable — a list of `(key, action, description)` tuples:

```python
class MyApp(App):
    BINDINGS = [
        ("q", "quit", "Quit"),
        ("r", "refresh", "Refresh"),
    ]

    def action_refresh(self) -> None:
        ...
```

### Screens

Textual manages a stack of screens. Push, pop, or switch screens for modal dialogs and navigation:

```python
from textual.screen import Screen

class ModalScreen(Screen):
    def compose(self) -> ComposeResult:
        yield Static("Modal content")

class MyApp(App):
    SCREENS = {"modal": ModalScreen}
    BINDINGS = [("m", "push_screen('modal')", "Modal")]
```

### Workers

Run background tasks without blocking the UI using `run_worker()` or the `@work` decorator:

```python
from textual import work

class MyApp(App):
    @work(exclusive=True)
    async def fetch_data(self, url: str) -> None:
        # Runs in background, exclusive cancels previous runs
        ...
```

## Installation / Setup

Install via pip:

```bash
pip install textual
```

For development tools (live CSS editing, devtools):

```bash
pip install textual-dev
```

For syntax highlighting in TextArea widgets:

```bash
pip install "textual[syntax]"
```

Run the demo to see what Textual can do:

```bash
python -m textual
```

Run apps in development mode with live CSS reloading:

```bash
textual run my_app.py --dev
```

## Usage Examples

### Basic App with Compose and CSS

```python
from textual.app import App, ComposeResult
from textual.containers import Horizontal
from textual.widgets import Button, Footer, Header

class QuestionApp(App):
    CSS = """
    Screen {
        align: center middle;
    }
    Horizontal {
        width: auto;
        height: auto;
    }
    Button {
        width: 20;
    }
    """

    def compose(self) -> ComposeResult:
        yield Header()
        with Horizontal():
            yield Button("Yes", variant="success", id="yes")
            yield Button("No", variant="error", id="no")
        yield Footer()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        self.exit(event.button.id)

if __name__ == "__main__":
    app = QuestionApp()
    result = app.run()
    print(f"Answer: {result}")
```

### Custom Widget with DEFAULT_CSS

```python
from textual.widgets import Static

class StatusBadge(Static):
    DEFAULT_CSS = """
    StatusBadge {
        dock: bottom;
        width: 100%;
        background: $boost;
        color: $text-muted;
        text-align: center;
    }
    """

    def on_mount(self) -> None:
        self.update("Ready")
```

### Reactive Widget with Watch

```python
from textual.app import App, ComposeResult
from textual.reactive import reactive
from textual.widgets import Input, Static

class ColorApp(App):
    CSS = """
    Screen { align: center middle; }
    """

    color = reactive("white")

    def compose(self) -> ComposeResult:
        yield Input(placeholder="Enter a color name")
        yield Static("Preview", id="preview")

    def on_input_changed(self, event: Input.Changed) -> None:
        self.color = event.value

    def watch_color(self, old_color: str, new_color: str) -> None:
        preview = self.query_one("#preview", Static)
        preview.styles.background = new_color
        preview.update(f"Color: {new_color}")
```

## Advanced Topics

**Layout System**: Vertical, horizontal, grid, dock, and overlay layouts with flex units (`fr`) → [Layout System](reference/01-layout.md)

**CSS Deep Dive**: Selectors, specificity, pseudo-classes, theme variables, scoped CSS, inline styles → [CSS Reference](reference/02-css.md)

**Widget Catalog**: Builtin widgets (Button, Input, DataTable, Tree, TextArea, OptionList, etc.) with usage patterns → [Widget Catalog](reference/03-widgets.md)

**Reactivity System**: Reactive attributes, var, watch methods, validation, dynamic defaults, layout triggers → [Reactivity](reference/04-reactivity.md)

**Events and Messages**: Message queues, bubbling, custom messages, @on decorator, handler naming, prevent/stop → [Events and Messages](reference/05-events.md)

**Screens and Navigation**: Screen stack, push/pop/switch, modal screens, opacity, install/uninstall → [Screens](reference/06-screens.md)

**Input Handling**: Key events, focus management, bindings, mouse events, action strings → [Input](reference/07-input.md)

**Actions**: Action methods, run_action(), namespaces (app/screen/focused), dynamic check_action() → [Actions](reference/08-actions.md)

**Workers and Concurrency**: run_worker(), @work decorator, exclusive workers, thread workers, WorkerState lifecycle → [Workers](reference/09-workers.md)

**Testing with Pilot**: run_test(), pilot.press(), pilot.click(), snapshot testing, screen size simulation → [Testing](reference/10-testing.md)

**Content and Markup**: Content markup tags, links (@click), variable substitution, Rich renderables → [Content and Markup](reference/11-content.md)

**Theming**: Built-in themes (including new ansi-dark/ansi-light in 8.2.5), Theme class, base colors, shades, custom theme registration, light/dark, `App.ansi_color` → [Theming](reference/12-theming.md)

**Devtools and CLI**: textual run --dev, console logging, markup playground, keys inspector → [Devtools](reference/13-devtools.md)
