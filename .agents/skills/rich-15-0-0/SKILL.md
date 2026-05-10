---
name: rich-15-0-0
description: Python library for rich text and beautiful formatting in the terminal. Provides color, tables, progress bars, markdown rendering, syntax highlighting, tracebacks, logging handlers, prompts, live displays, layouts, and pretty printing. Use when building CLI applications that need styled output, displaying data in tables or trees, showing progress during long operations, or enhancing debugging with improved tracebacks and pretty-printed data structures.
license: MIT
author: Tangled <noreply@tangledgroup.com>
version: "0.1.0"
tags:
  - terminal
  - cli
  - formatting
  - color
  - tables
  - progress
  - python
category: library
external_references:
  - https://github.com/Textualize/rich
  - https://rich.readthedocs.io/en/stable/index.html
---

# Rich 15.0.0

## Overview

Rich is a Python library for _rich_ text and beautiful formatting in the terminal. It makes it easy to add color and style to terminal output, and can render pretty tables, progress bars, markdown, syntax-highlighted source code, tracebacks, trees, columns, panels, live displays, layouts, and more — out of the box.

Rich works with Linux, macOS, and Windows (including both legacy cmd.exe and the new Windows Terminal). It requires Python 3.8 or later and works with Jupyter notebooks with no additional configuration required for basic usage.

Key capabilities:

- **Styled text output** via console markup (BBCode-like syntax) and programmatic styles
- **Console object** as the central hub for all rendering, with auto-detected terminal capabilities
- **Built-in renderables**: Tables, Panels, Trees, Columns, Padding, Progress bars, Syntax highlighting, Markdown, and more
- **Progress tracking** with `track()` for simple loops or full `Progress` class for multi-task displays
- **Live display** for continuously updating terminal content (dashboards, real-time data)
- **Layout system** for dividing the terminal screen into regions
- **Pretty printing** of Python data structures with syntax highlighting and indent guides
- **Enhanced tracebacks** with code context, local variables, and frame suppression
- **Logging handler** that colorizes Python's standard `logging` module output
- **Prompt utilities** for validated user input (strings, integers, floats, confirmations)

## When to Use

- Building CLI applications that need visually appealing output with colors, styles, and structured layouts
- Displaying tabular data in the terminal with flexible formatting options
- Tracking progress of long-running operations (file transfers, batch processing, data pipelines)
- Rendering markdown documents or code with syntax highlighting directly in the terminal
- Enhancing debugging output with pretty-printed data structures and improved tracebacks
- Creating real-time dashboards or live-updating displays in the terminal
- Adding styled prompts for user input with validation
- Integrating rich formatting into Python's `logging` module

## Installation / Setup

Install from PyPI:

```bash
python -m pip install rich
```

For Jupyter notebook support, include the extra dependencies:

```bash
python -m pip install "rich[jupyter]"
```

Test the installation with the built-in demo:

```bash
python -m rich
```

## Usage Examples

### Quick Start — Drop-in Print Replacement

Import Rich's `print` as a drop-in replacement for Python's built-in:

```python
from rich import print

print("Hello, [bold magenta]World[/bold magenta]!", ":vampire:")
print({"name": "Alice", "score": 95})
```

Rich automatically pretty-prints data structures and renders console markup for styling.

### Using the Console Object

For full control, create a `Console` instance:

```python
from rich.console import Console

console = Console()
console.print("Hello, World!", style="bold red")
console.print("[blue underline]This looks like a link[/]")
console.print(locals())
```

### Progress Tracking

Track any iterable with minimal code:

```python
from rich.progress import track
import time

for i in track(range(100), description="Processing..."):
    time.sleep(0.05)
```

### Tables

Render tabular data with flexible formatting:

```python
from rich.console import Console
from rich.table import Table

console = Console()
table = Table(title="Movie Schedule")

table.add_column("Release", justify="right", style="cyan", no_wrap=True)
table.add_column("Title", style="magenta")
table.add_column("Box Office", justify="right", style="green")

table.add_row("Dec 20, 2019", "Star Wars: Rise of Skywalker", "$952,110,690")
table.add_row("May 25, 2018", "Solo: A Star Wars Story", "$393,151,347")

console.print(table)
```

### Syntax Highlighting

Display code with syntax highlighting:

```python
from rich.console import Console
from rich.syntax import Syntax

console = Console()
syntax = Syntax.from_path("example.py", theme="monokai", line_numbers=True)
console.print(syntax)
```

## Advanced Topics

**Console API**: Console object, printing, logging, JSON output, exporting to text/HTML/SVG, input, capturing, paging, alternate screen → [Console API](reference/01-console-api.md)

**Styles and Markup**: Style definitions, color systems, console markup syntax, themes, custom highlighters → [Styles and Markup](reference/02-styles-and-markup.md)

**Built-in Renderables**: Tables, panels, trees, columns, padding, groups, markdown, syntax highlighting → [Renderables](reference/03-renderables.md)

**Progress and Live Display**: Progress bars, track function, multi-task progress, live updating displays, status spinners → [Progress and Live Display](reference/04-progress-and-live.md)

**Advanced Topics**: Pretty printing, tracebacks, prompts, layout system, console protocol for custom renderables, REPL integration → [Advanced Topics](reference/05-advanced-topics.md)
