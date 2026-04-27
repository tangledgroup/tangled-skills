# Console API

The `Console` class is the central hub for all Rich rendering. Most applications require a single Console instance, typically created at the module level.

## Creating a Console

```python
from rich.console import Console
console = Console()
```

Create it once and import from anywhere in your project:

```python
# console.py
from rich.console import Console
console = Console()

# elsewhere
from my_project.console import console
```

The Console auto-detects terminal capabilities and converts colors as necessary.

## Auto-Detected Attributes

- `size` — Current terminal dimensions (updates on resize)
- `encoding` — Default encoding (typically "utf-8")
- `is_terminal` — Boolean indicating if writing to a terminal
- `color_system` — Detected color system string

## Color Systems

Rich auto-detects the appropriate color system, or you can set it manually:

- `None` — Disables color entirely
- `"auto"` — Auto-detect (default)
- `"standard"` — 8 colors with normal/bright variations (16 total)
- `"256"` — 16 standard + 240 palette colors
- `"truecolor"` — 16.7 million colors
- `"windows"` — 8 colors for legacy Windows terminal

```python
console = Console(color_system="truecolor")
```

## Printing

`console.print()` converts objects to strings, applies syntax highlighting, pretty-prints containers, and renders console markup:

```python
console.print([1, 2, 3])
console.print("[blue underline]Looks like a link[/]")
console.print(locals())
console.print("FOO", style="white on blue")
```

It also renders any object supporting the Console Protocol (Text, Table, Syntax, custom renderables).

## Logging

`console.log()` adds timestamp and caller location columns:

```python
console.log("Hello from server!")
# [16:32:08] Hello from server!    server.py:42
```

Use `log_locals=True` to display a table of local variables at the call site.

## Printing JSON

```python
console.print_json('[false, true, null, "foo"]')
```

Or import directly:

```python
from rich import print_json
print_json('{"key": "value"}')
```

CLI usage: `python -m rich.json data.json`

## Low-Level Output

`console.out()` converts arguments to strings without pretty-printing, word-wrapping, or markup parsing. Useful for raw output with optional basic styling:

```python
console.out("Locals", locals())
```

## Rules

Draw horizontal separator lines with optional titles:

```python
console.rule("[bold red]Chapter 2")
# ───────────────────────────── Chapter 2 ─────────────────────────────
```

Parameters: `style` for line color, `align` ("left", "center", "right") for title position.

## Status

Display a spinner animation with a message without blocking console output:

```python
with console.status("Working..."):
    do_work()

with console.status("Monkeying around...", spinner="monkey"):
    do_work()
```

View available spinners: `python -m rich.spinner`

## Justify / Alignment

Set `justify` on print/log to "default", "left", "right", "center", or "full":

```python
console.print("Rich", style="bold white on blue")
console.print("Rich", style="bold white on blue", justify="center")
console.print("Rich", style="bold white on blue", justify="right")
```

"left" pads the right with spaces; "default" does not (visible when background color is set).

## Overflow

Control how text exceeding available space is handled:

- `"fold"` — Wrap to next line (default)
- `"crop"` — Truncate silently
- `"ellipsis"` — Truncate with "..."
- `"ignore"` — Allow overflow to next line

```python
console = Console(width=14)
console.print("supercalifragilisticexpialidocious", overflow="ellipsis")
# supercalifrag…
```

## Console Style

Apply a default style to everything printed:

```python
blue_console = Console(style="white on blue")
blue_console.print("All text is now on blue background")
```

## Soft Wrapping and Cropping

- `soft_wrap=True` — Disable word wrapping, let text run on like built-in `print`
- `crop=False` — Allow content to exceed terminal width (default is `True`)

## Input

`console.input()` works like Python's built-in but supports Rich renderables as prompts:

```python
name = console.input("What is [i]your[/i] [bold red]name[/]? :smiley: ")
```

## Exporting

Record console output and export to text, SVG, or HTML:

```python
console = Console(record=True)
console.print("[bold]Hello[/]")

console.save_text("output.txt")
console.save_svg("output.svg", theme=MONOKAI)
console.save_html("output.html")
```

SVGs reference the Fira Code font. Use `theme` parameter with themes from `rich.terminal_theme`.

## Error Console

Write to stderr for separating errors from regular output:

```python
error_console = Console(stderr=True, style="bold red")
error_console.print("Something went wrong!")
```

## File Output

Redirect console to a file:

```python
from datetime import datetime

with open("report.txt", "wt") as f:
    console = Console(file=f, width=80)
    console.rule(f"Report Generated {datetime.now().ctime()}")
```

Set explicit `width` when writing to files since terminal width detection won't work.

## Capturing Output

Capture what would have been written to the terminal:

```python
with console.capture() as capture:
    console.print("[bold red]Hello[/] World")
output = capture.get()
```

For unit tests, use `StringIO`:

```python
from io import StringIO
console = Console(file=StringIO())
console.print("[bold red]Hello[/] World")
output = console.file.getvalue()
```

## Paging

Display long output through a system pager:

```python
with console.pager():
    console.print(long_content)
```

Set `styles=True` if your pager supports color. Rich checks `MANPAGER` then `PAGER` environment variables. On Linux/macOS, set `PAGER=less -r` for ANSI support.

## Alternate Screen

Full-screen mode that preserves the command prompt:

```python
with console.screen():
    console.print(locals())
    sleep(5)
```

Or update with renderables:

```python
with console.screen(style="bold white on red") as screen:
    for count in range(5, 0, -1):
        text = Align.center(Text.from_markup(f"{count}"), vertical="middle")
        screen.update(Panel(text))
        sleep(1)
```

Type `reset` in terminal if stuck in alternate mode.

## Terminal Detection and Environment Variables

Rich auto-detects terminal capabilities. Key environment variables:

- `TERM=dumb` or `TERM=unknown` — Disable color/style and cursor movement
- `FORCE_COLOR` — Enable color regardless of TERM
- `NO_COLOR` — Disable all color (takes precedence over FORCE_COLOR; styles preserved)
- `TTY_COMPATIBLE=1` — Force terminal escape sequence support
- `TTY_INTERACTIVE=0` — Disable animations (progress bars, spinners)
- `COLUMNS` / `LINES` — Override console dimensions

For CI/GitHub Actions: set `TTY_COMPATIBLE=1` and `TTY_INTERACTIVE=0`.

Force terminal output: `Console(force_terminal=True)`

Force interactive mode: `Console(force_interactive=True/False)`
