# Built-in Renderables

Rich provides numerous renderable classes that can be printed to the Console. Any Rich renderable can be nested inside others (e.g., a Table inside a Panel, or a Panel inside a Tree branch).

## Tables

The `Table` class renders tabular data with unicode box characters and flexible formatting:

```python
from rich.console import Console
from rich.table import Table

table = Table(title="Star Wars Movies")
table.add_column("Released", justify="right", style="cyan", no_wrap=True)
table.add_column("Title", style="magenta")
table.add_column("Box Office", justify="right", style="green")

table.add_row("Dec 20, 2019", "Star Wars: Rise of Skywalker", "$952,110,690")
table.add_row("May 25, 2018", "Solo: A Star Wars Story", "$393,151,347")

console = Console()
console.print(table)
```

### Table Constructor Options

- `title` — Text shown above the table
- `caption` — Text shown below the table
- `width` / `min_width` — Fixed or minimum width
- `box` — Box style (from `rich.box`), or `None` for no grid
- `safe_box` — Force ASCII characters instead of unicode
- `padding` — Cell padding (int or tuple of 1-4 values)
- `collapse_padding` — Merge neighboring cell padding
- `pad_edge` — Remove edge padding if False
- `expand` — Expand to full available width
- `show_header` / `show_footer` — Show/hide header and footer rows
- `show_edge` — Disable edge line around table if False
- `show_lines` — Show lines between all rows
- `leading` — Extra space between rows
- `style` — Style applied to entire table (e.g., "on blue")
- `row_styles` — Alternating row styles for zebra stripes: `["dim", ""]`
- `header_style` / `footer_style` — Default style for header/footer cells
- `border_style` — Style for border characters
- `title_style` / `caption_style` — Style for title/caption text
- `title_justify` / `caption_justify` — "left", "right", "center", or "full"
- `highlight` — Enable automatic cell content highlighting

### Border Styles

Import preset Box styles from `rich.box`:

```python
from rich import box
table = Table(title="Movies", box=box.MINIMAL_DOUBLE_HEAD)
table = Table(box=box.SIMPLE)
table = Table(box=None)  # no borders
```

View available box styles: `python -m rich.box`

### Lines and Sections

- `show_lines=True` — Show lines between all rows
- `end_section=True` on `add_row()` — Force a line after this row
- `table.add_section()` — Add a line between current and next rows

### Adding Columns

Via constructor positional arguments:

```python
table = Table("Released", "Title", "Box Office", title="Movies")
```

With Column objects for full control:

```python
from rich.table import Column, Table
table = Table(
    "Released",
    "Title",
    Column(header="Box Office", justify="right"),
    title="Movies"
)
```

### Column Options

- `header_style` / `footer_style` — Style for header/footer text
- `style` — Style applied to all cells in the column
- `justify` — "left", "center", "right", or "full"
- `vertical` — "top", "middle", or "bottom" alignment
- `width` / `min_width` / `max_width` — Size constraints
- `ratio` — Proportional width allocation
- `no_wrap` — Prevent text wrapping in this column
- `highlight` — Enable automatic cell content highlighting

### Vertical Alignment

Per-column via `vertical` parameter, or per-cell with `Align`:

```python
table.add_row(Align("Title", vertical="middle"))
```

### Grids (Borderless Tables)

Use `Table.grid()` for layout without borders:

```python
from rich.table import Table

grid = Table.grid(expand=True)
grid.add_column()
grid.add_column(justify="right")
grid.add_row("Raising shields", "[bold magenta]COMPLETED [green]:heavy_check_mark:")
print(grid)
```

## Panels

Draw a border around text or any renderable:

```python
from rich import print
from rich.panel import Panel

print(Panel("Hello, [red]World!"))
print(Panel.fit("Fits content width"))
print(Panel("Content", title="Header", subtitle="Footer"))
```

- `expand=False` or `Panel.fit()` — Fit to content width instead of full terminal
- `title` / `subtitle` — Text above/below the panel
- `box` — Border style (same Box options as Tables)

## Trees

Display hierarchical data with guide lines:

```python
from rich.tree import Tree
from rich import print

tree = Tree("Root")
foo = tree.add("foo")
bar = tree.add("bar")
baz_tree = tree.add("baz")
baz_tree.add("[red]Red").add("[green]Green").add("[blue]Blue")
print(tree)
```

### Tree Styles

- `style` — Style for the entire branch (inherited by children)
- `guide_style` — Style for guide lines. Use "bold" for thicker lines or "underline2" for double lines.

Demo: `python -m rich.tree`

## Columns

Render items in neat columns with equal or optimal width:

```python
from rich import print
from rich.columns import Columns
import os

directory = os.listdir(".")
print(Columns(directory, equal=True, expand=True))
```

Useful for directory listings, card layouts, or any content that benefits from multi-column display.

## Padding

Add whitespace around text or renderables:

```python
from rich.padding import Padding

test = Padding("Hello", 1)                    # 1 on all sides
test = Padding("Hello", (2, 4))              # 2 top/bottom, 4 left/right
test = Padding("Hello", (1, 2, 3, 4))        # top, right, bottom, left
test = Padding("Hello", (2, 4), style="on blue", expand=False)
```

Useful for emphasizing items in tables or adding spacing within panels.

## Render Groups

Group multiple renderables where only one is expected:

```python
from rich.console import Group
from rich.panel import Panel

panel_group = Group(
    Panel("Hello", style="on blue"),
    Panel("World", style="on red"),
)
print(Panel(panel_group))
```

Or use the `@group()` decorator for dynamic content:

```python
from rich.console import group

@group()
def get_panels():
    yield Panel("Hello", style="on blue")
    yield Panel("World", style="on red")

print(Panel(get_panels()))
```

## Markdown

Render markdown documents in the terminal with syntax-highlighted code blocks:

```python
from rich.console import Console
from rich.markdown import Markdown

console = Console()
md = Markdown("# Heading\n\nSome **bold** and *italic* text.")
console.print(md)
```

Load from file:

```python
with open("README.md") as f:
    console.print(Markdown(f.read()))
```

CLI usage: `python -m rich.markdown README.md`

## Syntax Highlighting

Display code with syntax highlighting using Pygments:

```python
from rich.console import Console
from rich.syntax import Syntax

console = Console()
syntax = Syntax(code_string, "python", theme="monokai", line_numbers=True)
console.print(syntax)
```

Load from file with auto-detected language:

```python
syntax = Syntax.from_path("example.py", theme="monokai", line_numbers=True)
```

Options:

- `theme` — Pygments theme name, or "ansi_dark" / "ansi_light" for terminal colors
- `line_numbers` — Show line numbers column
- `background_color` — Override theme background ("red", "#ff0000", "default")

CLI usage: `python -m rich.syntax example.py`

## JSON

Pretty-print and style JSON data:

```python
from rich.console import Console
from rich.json import JSON

console = Console()
console.print_json('{"name": "Alice", "scores": [95, 87, 92]}')
console.log(JSON('["foo", "bar"]'))
```

Import directly: `from rich import print_json`

## Align

Align content within available space:

```python
from rich.align import Align
from rich.text import Text

text = Align.center(Text("Centered text"), vertical="middle")
```

Useful for centering panels in alternate screen mode or aligning cells vertically in tables.
