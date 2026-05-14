# Devtools and CLI

## textual run

Run apps with the Textual CLI for development features:

```bash
textual run my_app.py --dev
```

The `--dev` flag enables:
- **Live CSS editing** — changes to `.tcss` files reload instantly
- **Console logging** — `self.log()` output visible in devtools
- **Error overlay** — exceptions displayed in-app

## Console Logging

Write to the devtools console from your app:

```python
class MyApp(App):
    def on_mount(self) -> None:
        self.log("App started")
        self.log(f"Screen size: {self.size}")
```

Console is visible when running with `--dev`.

## Markup Playground

Interactive markup testing tool:

```bash
python -m textual.markup
```

Enter markup in the top textarea, see rendered output below. Supports variable substitution tab.

## Keys Inspector

See all key event identifiers:

```bash
textual keys
```

Press keys to see their `key`, `character`, `name`, and `aliases` values. Useful for debugging key handling.

## Demo

Run the built-in demo to explore Textual capabilities:

```bash
python -m textual
```

## Command Palette

Access via `Ctrl+P` in any app. Provides:
- Theme switching
- Action search
- Navigation help
- Debug information

## Inline Mode

Run apps beneath the shell prompt (non-fullscreen):

```python
if __name__ == "__main__":
    app = MyApp()
    app.run(inline=True)
```

Not supported on Windows. Useful for CLI tools that integrate with terminal workflow.

## ANSI Colors

Preserve terminal ANSI theme colors instead of Textual defaults:

```python
app = MyApp(ansi_color=True)
```

Recommended for inline apps; default behavior (overriding ANSI) is better for full-screen apps.
