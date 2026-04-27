# Theming

## Built-in Themes

Textual ships with several themes: `textual-dark`, `nord`, `gruvbox`, `tokyo-night`, `solarized-light`, `atom-one-dark`, `atom-one-light`.

Switch at runtime via the Command Palette (`Ctrl+P` → "Change Theme").

Set programmatically:

```python
class MyApp(App):
    def on_mount(self) -> None:
        self.theme = "nord"
```

## Creating Custom Themes

Define a theme with the `Theme` class:

```python
from textual.theme import Theme

my_theme = Theme(
    name="arctic",
    primary="#88C0D0",
    secondary="#81A1C1",
    accent="#B48EAD",
    foreground="#D8DEE9",
    background="#2E3440",
    success="#A3BE8C",
    warning="#EBCB8B",
    error="#BF616A",
    surface="#3B4252",
    panel="#434C5E",
    dark=True,
)
```

Register and activate:

```python
class MyApp(App):
    def on_mount(self) -> None:
        self.register_theme(my_theme)
        self.theme = "arctic"
```

## Base Colors

Themes define 11 base colors. Only `primary` is required — Textual generates the rest if omitted:

- `$primary` — branding color, titles, strong emphasis
- `$secondary` — alternative branding
- `$foreground` — default text color
- `$background` — screen background
- `$surface` — widget background (sits on $background)
- `$panel` — UI differentiation
- `$boost` — alpha layer for backgrounds
- `$warning` — warning indicators
- `$error` — error indicators
- `$success` — success indicators
- `$accent` — attention-drawing contrast

## Shades

Textual generates 3 dark and 3 light shades per color:

- `$primary-darken-1`, `-darken-2`, `-darken-3`
- `$primary-lighten-1`, `-lighten-2`, `-lighten-3`

Use in CSS:
```css
Widget {
    background: $surface-darken-1;
    border: $primary-lighten-2 solid;
}
```

## Custom Variables

Themes can define additional variables via the `variables` dict:

```python
my_theme = Theme(
    name="custom",
    primary="#004578",
    variables={
        "footer-key-foreground": "#00ff00",
        "input-selection-background": "#81a1c1 35%",
    },
)
```

Reference with `$variable-name` in CSS.

## Light and Dark Themes

Set `dark=True` (default) or `dark=False` on the Theme. This affects generated shade directions and default widget appearances.
