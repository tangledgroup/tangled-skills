# CSS Reference

## Selectors

Textual CSS supports several selector types:

**Type selector** — matches widget class name:
```css
Button { width: 15; }
```

**ID selector** — matches widget `id` attribute:
```css
#submit-btn { background: green; }
```

**Class selector** — matches widget `classes` attribute:
```css
.active { color: yellow; }
```

**Descendant combinator** — space-separated, matches nested widgets:
```css
Container Button { width: 10; }
```

**Child combinator** — `>` for direct children only:
```css
Screen > Header { dock: top; }
```

**Pseudo-class selectors:**
- `:focus` — widget currently has input focus
- `:disabled` — widget is disabled
- `:blank` — widget has no content
- `:first-child`, `:last-child`, `:only-child`
- `:hover` — mouse is over the widget
- `:descendant-has(:focus)` — widget contains a focused descendant

## Specificity

Specificity determines which rule wins when multiple selectors match the same widget. Order from lowest to highest:

1. `DEFAULT_CSS` on widgets (lowest)
2. External `.tcss` files and `CSS` class variable
3. Inline styles via `widget.styles` property (highest)

Within the same level, more specific selectors override less specific ones (ID > class > type).

## Theme Variables

Themes provide CSS variables prefixed with `$`. Reference them in any CSS rule:

```css
MyWidget {
    background: $surface;
    color: $text;
    border: tall $primary;
}
```

Available base colors: `$primary`, `$secondary`, `$accent`, `$foreground`, `$background`, `$surface`, `$panel`, `$boost`, `$warning`, `$error`, `$success`.

Generated shades: `$primary-darken-1` through `-darken-3`, `$primary-lighten-1` through `-lighten-3`.

## Common Properties

**Dimensions:**
```css
Widget {
    width: 80;           /* fixed cells */
    width: 100%;         /* percentage of parent */
    width: 1fr;          /* flex unit */
    height: auto;        /* content-determined */
}
```

**Positioning:**
```css
Widget {
    dock: top;           /* dock to edge */
    offset: 5 3;         /* absolute position */
    margin: 1 2;         /* top-bottom left-right */
    padding: 1 2;        /* internal spacing */
}
```

**Appearance:**
```css
Widget {
    background: blue;
    color: white;
    border: solid $primary;
    opacity: 50%;        /* transparency (0-100%) */
}
```

**Text:**
```css
Widget {
    text-align: center;
    text-style: bold italic underline;
    text-overflow: ellipsis;
}
```

**Scrolling:**
```css
Widget {
    overflow-x: auto;    /* scrollbar when needed */
    overflow-y: hidden;  /* no scrollbar, clip content */
    scrollbar-gutter: stable;  /* reserve scrollbar space */
}
```

## Scoped CSS

`DEFAULT_CSS` on widget classes is scoped by default — rules only affect the widget and its descendants. This prevents bundled widget CSS from affecting unrelated parts of the app.

Disable scoping with `SCOPED_CSS = False`:

```python
class MyWidget(Widget):
    SCOPED_CSS = False
    DEFAULT_CSS = """
    Screen { background: red; }  /* affects entire screen */
    """
```

## Live Editing

Run with `textual run my_app.py --dev` to enable live CSS reloading. Changes to `.tcss` files are reflected immediately without restarting the app.
