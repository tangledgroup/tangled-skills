# Layout System

## Overview

Layout defines how child widgets are arranged inside a container. Textual supports vertical, horizontal, grid, dock, and overlay layouts. Layouts can be set via CSS (`layout: vertical`) or programmatically (`widget.styles.layout = "vertical"`).

The default layout for `Screen` is `vertical`.

## Vertical Layout

Arranges children top-to-bottom:

```css
Screen {
    layout: vertical;
}
```

Widgets expand to fill the width of their parent by default. Use `height: 1fr` to distribute available height equally among children:

```python
from textual.app import App, ComposeResult
from textual.widgets import Static

class VerticalApp(App):
    CSS = """
    .box { height: 1fr; background: blue; }
    """

    def compose(self) -> ComposeResult:
        yield Static("One", classes="box")
        yield Static("Two", classes="box")
        yield Static("Three", classes="box")
```

When children exceed available space, `overflow-y: auto` (default on Screen) adds a scrollbar.

## Horizontal Layout

Arranges children left-to-right:

```css
Screen {
    layout: horizontal;
}
```

Unlike vertical layout, widgets do not expand to fill height automatically. Set `height: 100%` explicitly:

```css
Screen {
    layout: horizontal;
}
.box {
    width: 1fr;
    height: 100%;
}
```

Horizontal overflow requires explicit `overflow-x: auto`.

## Grid Layout

Grid arranges children in rows and columns using `grid-size`, `grid-gutter`, and `grid-columns`/`grid-rows`:

```css
Screen {
    layout: grid;
    grid-size: 2;
    grid-gutter: 1;
}
.box {
    background: $surface;
    border: $primary solid;
}
```

For variable column widths, use `grid-columns`:

```css
Screen {
    layout: grid;
    grid-columns: 1fr 2fr;
}
```

## Dock

The `dock` property attaches a widget to an edge of its parent (`top`, `bottom`, `left`, `right`). Docked widgets are removed from the normal layout flow and positioned before other content is laid out:

```css
Header {
    dock: top;
    height: 3;
}
Footer {
    dock: bottom;
    height: 1;
}
```

## Overlay

`overlay` positions a widget absolutely within its parent using `offset(x, y)`. Like docked widgets, overlaid widgets are removed from the normal layout flow:

```css
#tooltip {
    overlay: 10 5;
}
```

## Utility Containers

Textual provides container widgets with pre-configured layouts:

- `Vertical` — vertical layout
- `Horizontal` — horizontal layout
- `Grid` — grid layout
- `Container` — default layout (no predefined layout)
- `VerticalScroll` — vertical layout with `overflow-y: auto`
- `HorizontalScroll` — horizontal layout with `overflow-x: auto`

Use context managers for clean nesting in compose:

```python
from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widgets import Static

class LayoutApp(App):
    def compose(self) -> ComposeResult:
        with Horizontal():
            with Vertical(classes="column"):
                yield Static("One")
                yield Static("Two")
            with Vertical(classes="column"):
                yield Static("Three")
                yield Static("Four")
```

## Flex Units (fr)

The `fr` unit distributes available space proportionally:

```css
/* Three equal columns */
.column { width: 1fr; }

/* Variable ratio: first gets 1 part, second gets 2 parts */
.col-a { width: 1fr; }
.col-b { width: 2fr; }
```

Combine `fr` with fixed sizes:

```css
.sidebar { width: 20; }
.main { width: 1fr; }
```

## Align and Content-Align

`align` positions child widgets within the container. `content-align` positions content within a single widget:

```css
Screen {
    align: center middle;
}
Static {
    content-align: center middle;
}
```

Valid values: `left`, `center`, `right` (horizontal) and `top`, `middle`, `bottom` (vertical).
