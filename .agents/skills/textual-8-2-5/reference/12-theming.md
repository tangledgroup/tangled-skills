# Theming

## Built-in Themes

Textual ships with several themes: `textual-dark`, `nord`, `gruvbox`, `tokyo-night`, `solarized-light`, `atom-one-dark`, `atom-one-light`, `ansi-dark`, `ansi-light`.

The `ansi-dark` and `ansi-light` themes (new in 8.2.5) use terminal ANSI color palette rather than custom colors, making them ideal for terminals with limited color support or when you want to respect the user's terminal color scheme.

Switch at runtime via the Command Palette (`Ctrl+P` → "Change Theme").

Set programmatically:

```python
class MyApp(App):
    def on_mount(self) -> None:
        self.theme = "nord"
```

## ANSI Color Mode (8.2.5+)

Textual 8.2.5 introduced an `ansi` value for themes and changed `App.ansi_color` to accept `None`. When `App.ansi_color` is `None` (the default with ansi-themed setups), Textual uses the `ansi` value from the active theme.

```python
class MyApp(App):
    # Set to None to inherit ansi setting from the theme
    ansi_color = None

    def on_mount(self) -> None:
        self.theme = "ansi-dark"
```

When using `ansi-dark` or `ansi-light` themes, colors are mapped to the terminal's standard 16 ANSI color slots rather than hardcoded RGB values. This means the theme adapts to the user's terminal color configuration.

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
