# Content and Markup

## Content Types

Widgets display content in three ways:

1. **Markup strings** — text with embedded style tags
2. **Content objects** — programmatic content construction
3. **Rich renderables** — any object printable by Rich (tables, panels, etc.)

## Markup Tags

Markup uses square brackets for inline styling. Tags are removed from output:

```python
# Bold text
"[bold]Hello[/bold], World!"

# Combined styles
"[bold italic underline]Important[/]"

# Auto-close
"[red]Error:[/ ] something went wrong"
```

### Style Tags

- `bold` / `b` — bold text
- `dim` / `d` — slightly transparent
- `italic` / `i` — italic
- `underline` / `u` — underlined
- `strike` / `s` — strikethrough
- `reverse` / `r` — swap foreground/background

Combine: `[bold italic]`, invert: `[not bold]`.

### Color Tags

```python
"[red]Error[/]"
"[on blue]Highlighted[/]"
"[#ff8800]Custom hex[/]"
"[rgb(255,128,0)]RGB color[/]"
```

### Link Tags

Embed clickable actions in text:

```python
"Click [@click=app.bell]here[/] to ring the bell"
```

Links are rendered underlined by default.

### Variable Substitution

Use `{variable}` syntax with a variables dict:

```python
from textual.content import Content

template = "Hello, {name}! You have {count} messages."
content = Content.from_markup(template, variables={"name": "Alice", "count": 5})
```

## Rich Renderables

Any Rich renderable can be displayed in a widget:

```python
from rich.table import Table
from rich.panel import Panel

table = Table()
table.add_column("Name")
table.add_column("Age")
table.add_row("Alice", "30")
self.update(table)
```

## Disabling Markup

Set `markup=False` on Static widgets to treat brackets as literal text:

```python
from textual.widgets import Static
yield Static("[not a tag]", markup=False)
```

## Content Playground

Experiment with markup interactively:

```bash
python -m textual.markup
```
