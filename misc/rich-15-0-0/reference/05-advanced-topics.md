# Advanced Topics

## Pretty Printing

Rich formats containers (lists, dicts, sets) with syntax highlighting and automatic word wrapping to fit terminal width.

### pprint Method

```python
from rich.pretty import pprint
pprint(locals())
```

Options:

- `indent_guides=True` — Draw vertical guides for nesting levels (default on)
- `expand_all=True` — Fully expand all data structures
- `max_length=N` — Truncate containers with more than N elements
- `max_string=N` — Truncate strings longer than N characters

```python
pprint(locals(), max_length=2, max_string=50)
```

### Pretty Renderable

Embed pretty-printed data inside other renderables:

```python
from rich import print
from rich.pretty import Pretty
from rich.panel import Panel

print(Panel(Pretty(locals())))
```

### Rich Repr Protocol

Add `__rich_repr__` to custom classes for Rich-aware formatting. This method yields tuples that control how the object is displayed:

```python
class Bird:
    def __init__(self, name, eats=None, fly=True, extinct=False):
        self.name = name
        self.eats = list(eats) if eats else []
        self.fly = fly
        self.extinct = extinct

    def __rich_repr__(self):
        yield self.name                    # positional arg
        yield "eats", self.eats           # keyword arg
        yield "fly", self.fly, True       # keyword, omit if equals default
        yield "extinct", self.extinct, False
```

Yield patterns:

- `yield value` — Positional argument
- `yield name, value` — Keyword argument
- `yield name, value, default` — Keyword, omitted when value equals default

For angular bracket style (`<ClassName ...>`), set `__rich_repr__.angular = True`.

### Automatic Rich Repr

Use the `@rich.repr.auto` decorator to generate repr automatically:

```python
import rich.repr

@rich.repr.auto
class Bird:
    def __init__(self, name, eats=None, fly=True, extinct=False):
        self.name = name
        self.eats = list(eats) if eats else []
        self.fly = fly
        self.extinct = extinct
```

With `angular=True` for `<ClassName ...>` style.

Demo: `python -m rich.repr`

## Tracebacks

Rich renders Python tracebacks with syntax highlighting, code context, and local variables — much more readable than standard Python tracebacks.

### Printing Tracebacks

```python
from rich.console import Console
console = Console()

try:
    do_something()
except Exception:
    console.print_exception(show_locals=True)
```

### Installing as Default Handler

Make Rich handle all uncaught exceptions:

```python
from rich.traceback import install
install(show_locals=True)
```

### Automatic Installation via sitecustomize.py

Create `sitecustomize.py` in your virtualenv's `site-packages`:

```python
from rich.traceback import install
install(show_locals=True)
```

This installs the handler for all code run within that environment.

### Suppressing Frames

Exclude framework code from tracebacks:

```python
import click
from rich.traceback import install
install(suppress=[click])
```

### Max Frames

Guard against massive recursion tracebacks (default: 100 frames max, shows first 50 + last 50):

```python
console.print_exception(max_frames=20)
```

Set `max_frames=0` to disable the limit.

Demo: `python -m rich.traceback`

## Prompts

Rich provides validated input prompts that loop until valid input is received:

### String Prompt

```python
from rich.prompt import Prompt
name = Prompt.ask("Enter your name")
name = Prompt.ask("Enter your name", default="Paul Atreides")
```

### Choices

Loop until user enters one of the allowed values:

```python
name = Prompt.ask("Pick a character", choices=["Paul", "Jessica", "Duncan"], default="Paul")
name = Prompt.ask("Pick", choices=["A", "B"], case_sensitive=False)
```

### Type-Specific Prompts

```python
from rich.prompt import IntPrompt, FloatPrompt, Confirm

age = IntPrompt.ask("How old are you?")
rating = FloatPrompt.ask("Rate from 0.0 to 5.0")
agree = Confirm.ask("Do you agree?")
```

### Custom Prompts

Extend `Prompt` to create custom validators. See `rich/prompt.py` for examples.

Demo: `python -m rich.prompt`

## Layout

Divide the terminal screen into regions, each with independent content. Use with `Live` for full-screen applications.

### Creating Layouts

```python
from rich.layout import Layout
from rich import print

layout = Layout()
layout.split_column(
    Layout(name="upper"),
    Layout(name="lower")
)
layout["lower"].split_row(
    Layout(name="left"),
    Layout(name="right"),
)
print(layout)
```

### Setting Content

```python
from rich.panel import Panel

layout["left"].update("Some content here")
layout["right"].split(
    Layout(Panel("Hello")),
    Layout(Panel("World!"))
)
```

### Sizing

- Fixed: `layout["upper"].size = 10` (rows for vertical, characters for horizontal)
- Ratio: `layout["upper"].ratio = 2` (takes 2/3 of space when sibling has ratio 1)
- Minimum: `layout["lower"].minimum_size = 10`

### Visibility

Toggle regions: `layout["upper"].visible = False`

### Tree View

Visualize layout structure: `print(layout.tree)`

Demo: `python -m rich.layout`

## Console Protocol

Add Rich rendering to custom objects.

### __rich__ Method

Return a renderable or string (rendered as console markup):

```python
class MyObject:
    def __rich__(self) -> str:
        return "[bold cyan]MyObject()"
```

### __rich_console__ Method

For advanced multi-renderable output:

```python
from rich.console import Console, ConsoleOptions, RenderResult
from rich.table import Table

class Student:
    def __init__(self, id, name, age):
        self.id = id
        self.name = name
        self.age = age

    def __rich_console__(self, console: Console, options: ConsoleOptions) -> RenderResult:
        yield f"[b]Student:[/b] #{self.id}"
        my_table = Table("Attribute", "Value")
        my_table.add_row("name", self.name)
        my_table.add_row("age", str(self.age))
        yield my_table
```

### __rich_measure__ Method

Tell Rich how much space your renderable needs:

```python
from rich.console import Console, ConsoleOptions
from rich.measure import Measurement

class ChessBoard:
    def __rich_measure__(self, console: Console, options: ConsoleOptions) -> Measurement:
        return Measurement(8, options.max_width)
```

### Low-Level Segment Rendering

For complete control, yield `Segment` objects:

```python
from rich.segment import Segment
from rich.style import Style

class MyObject:
    def __rich_console__(self, console, options):
        yield Segment("My", Style(color="magenta"))
        yield Segment("Object", Style(color="green"))
        yield Segment("()", Style(color="cyan"))
```

## Rich Inspect

Generate a detailed report on any Python object:

```python
from rich import inspect
from rich.color import Color

color = Color.parse("red")
inspect(color, methods=True)
```

Useful for debugging and exploring objects.

## REPL Integration

Install Rich in the Python REPL for automatic pretty printing:

```python
>>> from rich import pretty
>>> pretty.install()
>>> ["Rich and pretty", True]
```

### IPython Extension

Load in IPython/Jupyter:

```python
In [1]: %load_ext rich
```

Add "rich" to `c.InteractiveShellApp.extensions` in IPython config for auto-loading.

## Text Class

The `Text` class provides fine-grained control over styled text:

### Building Styled Text

```python
from rich.text import Text

# Method 1: stylize by range
text = Text("Hello, World!")
text.stylize("bold magenta", 0, 6)

# Method 2: append with style
text = Text()
text.append("Hello", style="bold magenta")
text.append(" World!")

# Method 3: from ANSI codes
text = Text.from_ansi("\033[1;35mHello\033[0m, World!")

# Method 4: assemble from parts
text = Text.assemble(("Hello", "bold magenta"), ", World!")
```

### Highlighting Words/Patterns

```python
text.highlight_words(["Hello", "World"], "bold yellow")
text.highlight_regex(r"\d+", "cyan")
```

### Text Attributes

- `justify` — "left", "center", "right", or "full"
- `overflow` — "fold", "crop", or "ellipsis"
- `no_wrap` — Prevent wrapping
- `tab_size` — Characters per tab

Use Text instances anywhere a string is accepted in the Rich API.

## Logging Handler

Integrate Rich formatting with Python's `logging` module:

```python
import logging
from rich.logging import RichHandler

FORMAT = "%(message)s"
logging.basicConfig(
    level="NOTSET", format=FORMAT, datefmt="[%X]", handlers=[RichHandler()]
)

log = logging.getLogger("rich")
log.info("Hello, World!")
```

Enable console markup per message:

```python
log.error("[bold red]Server shutting down![/]", extra={"markup": True})
```

Enable Rich tracebacks in logs:

```python
handlers=[RichHandler(rich_tracebacks=True)]
```

Suppress framework frames:

```python
RichHandler(rich_tracebacks=True, tracebacks_suppress=[click])
```
