# Styles and Markup

Styles define text color and attributes (bold, italic, underline, etc.). They can be specified as strings or `Style` class instances.

## Defining Styles

A style definition is a space-separated string of color names and attribute keywords.

### Foreground Color

Use one of the 256 standard colors by name:

```python
console.print("Hello", style="magenta")
```

By number (0-255):

```python
console.print("Hello", style="color(5)")
```

Hex or RGB for truecolor (16.7M colors):

```python
console.print("Hello", style="#af00ff")
console.print("Hello", style="rgb(175,0,255)")
```

### Background Color

Precede the color with "on":

```python
console.print("DANGER!", style="red on white")
```

Use `"default"` to reset to terminal defaults:

```python
console.print("Reset", style="default on default")
```

### Style Attributes

- `"bold"` or `"b"` — Bold text
- `"dim"` — Dim/faded text
- `"italic"` or `"i"` — Italic (not supported on Windows legacy)
- `"underline"` or `"u"` — Underlined
- `"blink"` — Flashing text
- `"blink2"` — Rapid flash (rarely supported)
- `"reverse"` or `"r"` — Foreground/background swapped
- `"strike"` or `"s"` — Strikethrough
- `"conceal"` — Hidden text (rarely supported)
- `"overline"` or `"o"` — Overlined
- `"underline2"` or `"uu"` — Double underline

Less widely supported:

- `"frame"` — Framed text
- `"encircle"` — Encircled text

Combine freely:

```python
console.print("Danger!", style="blink bold red underline on white")
```

### Negating Styles

Prefix with "not" to turn off styles within overlapping regions:

```python
console.print("foo [not bold]bar[/not bold] baz", style="bold")
# "foo" and "baz" are bold, "bar" is normal
```

### Links

Add clickable hyperlinks (terminal-dependent):

```python
console.print("Google", style="link https://google.com")
```

## Style Class

Use `Style` directly instead of parsing strings:

```python
from rich.style import Style

danger_style = Style(color="red", blink=True, bold=True)
console.print("Danger!", style=danger_style)
```

Parse explicitly or combine:

```python
base = Style.parse("cyan")
console.print("Hello", style=base + Style(underline=True))
```

## Console Markup

Rich supports BBCode-like markup for inline styling in strings. Works everywhere Rich accepts a string (print, log, Table cells, Panel content).

### Syntax

Open with `[style]`, close with `[/style]`:

```python
from rich import print
print("[bold red]alert![/bold red] Something happened")
```

Unclosed tags apply to end of string:

```python
print("[bold italic yellow on red]This is impossible to read")
```

Shorthand close (closes last opened tag):

```python
print("[bold red]Bold and red[/] not bold or red")
```

Tags can overlap and don't need strict nesting:

```python
print("[bold]Bold[italic] bold+italic [/bold]italic[/italic]")
```

### Links in Markup

```python
print("Visit my [link=https://example.com]blog[/link]!")
```

### Escaping

Escape literal brackets with backslash:

```python
print(r"foo\[bar]")  # prints: foo[bar]
```

Use `rich.markup.escape()` for dynamic content to prevent injection:

```python
from rich.markup import escape
def greet(name):
    console.print(f"Hello {escape(name)}!")
```

### Emoji

Insert emoji by name between colons:

```python
print(":warning:")  # ⚠️
print(":red_heart-emoji:")  # color variant
print(":red_heart-text:")   # monochrome variant
```

View all emojis: `python -m rich.emoji`

### Disabling Markup

Set `markup=False` on `print()` or on the Console constructor:

```python
console = Console(markup=False)
console.print("[bold]This won't be bold[/]")
```

## Style Themes

Define reusable named styles to avoid repeating style strings:

```python
from rich.console import Console
from rich.theme import Theme

custom_theme = Theme({
    "info": "dim cyan",
    "warning": "magenta",
    "danger": "bold red"
})
console = Console(theme=custom_theme)
console.print("This is information", style="info")
console.print("[warning]The pod bay doors are locked[/warning]")
```

Style names must be lowercase, start with a letter, and contain only letters, `.`, `-`, `_`.

### Customizing Defaults

Themes inherit Rich's built-in styles. Override by using the same name:

```python
console = Console(theme=Theme({"repr.number": "bold green blink"}))
console.print("The total is 128")  # numbers now bold green blinking
```

Disable inheritance with `inherit=False`.

View default theme: `python -m rich.theme` or `python -m rich.default_styles`

### Loading Themes from Config

External config file format:

```ini
[styles]
info = dim cyan
warning = magenta
danger = bold red
```

Load with `Theme.read("config.cfg")`.

## Highlighting

Rich automatically highlights patterns in text: numbers, strings, collections, booleans, None, file paths, URLs, UUIDs.

Disable with `highlight=False` on `print()`, `log()`, or the Console constructor.

### Custom Highlighters

Extend `RegexHighlighter` for pattern-based highlighting:

```python
from rich.console import Console
from rich.highlighter import RegexHighlighter
from rich.theme import Theme

class EmailHighlighter(RegexHighlighter):
    base_style = "example."
    highlights = [r"(?P<email>[\w-]+@([\w-]+\.)+[\w-]+)"]

theme = Theme({"example.email": "bold magenta"})
console = Console(highlighter=EmailHighlighter(), theme=theme)
console.print("Send funds to money@example.org")
```

Group names in regexes are prefixed with `base_style` to form style names. Use the highlighter as a callable for granular control:

```python
highlight_emails = EmailHighlighter()
console.print(highlight_emails("Email me at user@example.com"))
```

For full custom logic, extend `Highlighter` and implement the `highlight(self, text)` method.

### Builtin Highlighters

- `ISO8601Highlighter` — Highlights ISO 8601 datetime strings
- `JSONHighlighter` — Highlights JSON-formatted strings
