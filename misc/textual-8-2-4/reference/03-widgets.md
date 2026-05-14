# Widget Catalog

## Core Widgets

### Static

Base content widget. Caches rendered output and provides `update()` to change content:

```python
from textual.widgets import Static

label = Static("Hello")
label.update("Goodbye")
```

### Label

Like Static but with `height: auto` by default (single-line text):

```python
from textual.widgets import Label
yield Label("Status: Ready")
```

### Button

Clickable button with variants (`primary`, `success`, `warning`, `error`, `default`):

```python
from textual.widgets import Button
yield Button("Submit", variant="primary", id="submit")
```

Sends `Button.Pressed` event on click. Handle with `on_button_pressed` or `@on(Button.Pressed)`.

### Input

Single-line text input:

```python
from textual.widgets import Input
yield Input(placeholder="Enter name", id="name-input")
```

Events: `Input.Changed`, `Input.Submitted` (on Enter). Access value via `widget.value`.

### TextArea

Multi-line code editor with syntax highlighting (requires `textual[syntax]`):

```python
from textual.widgets import TextArea
yield TextArea(code, language="python", id="editor")
```

### Footer

Displays key bindings at the bottom of the screen:

```python
from textual.widgets import Footer
yield Footer()
```

### Header

Displays app title and subtitle at the top:

```python
from textual.widgets import Header
yield Header()
```

## Data Widgets

### DataTable

Tabular data display with sorting, selection, and keying:

```python
from textual.widgets import DataTable

table = DataTable(id="data")
table.add_columns("Name", "Age", "City")
table.add_row("Alice", 30, "NYC", key="alice")
table.add_row("Bob", 25, "LA", key="bob")
```

Features: column sorting (`fixed_z_index`), row selection, fixed columns, z-index layering.

### OptionList

Selectable list of options:

```python
from textual.widgets import OptionList

options = OptionList(
    *[(label, index) for index, label in enumerate(items)]
)
```

Events: `OptionList.OptionHighlighted`, `OptionList.OptionSelected`.

### SelectionList

Multi-select list with toggleable items:

```python
from textual.widgets import SelectionList

sl = SelectionList(
    SelectionList.Option("Python", "python", True),
    SelectionList.Option("Rust", "rust"),
    SelectionList.Option("Go", "go"),
)
```

### Digits

Displays large numeric values:

```python
from textual.widgets import Digits
yield Digits("42", id="score")
```

## Tree Widgets

### Tree

Hierarchical tree with expandable nodes:

```python
from textual.widgets import Tree

tree = Tree("Root", id="file-tree")
node = tree.root
child = node.add("Child")
child.add("Grandchild")
```

### DirectoryTree

Filesystem browser:

```python
from textual.widgets import DirectoryTree
yield DirectoryTree(".", id="files")
```

Events: `DirectoryTree.FileSelected`.

## Display Widgets

### RichLog

Scrolling log output with Rich rendering:

```python
from textual.widgets import RichLog
log = RichLog(id="output")
log.write("Log entry")
```

### Log

Plain text scrolling log (no Rich formatting):

```python
from textual.widgets import Log
yield Log(id="console")
```

### Markdown / MarkdownViewer

Render Markdown content:

```python
from textual.widgets import Markdown
yield Markdown("# Hello\nSome **markdown** text")
```

`MarkdownViewer` adds a scrollbar and file navigation.

### Sparkline

ASCII sparkline chart:

```python
from textual.widgets import Sparkline
yield Sparkline([1, 3, 2, 5, 4, 6], id="chart")
```

### ProgressBar

Visual progress indicator:

```python
from textual.widgets import ProgressBar
bar = ProgressBar(total=100, show_percentage=True)
bar.update(progress=50)
```

### LoadingIndicator

Animated loading spinner:

```python
from textual.widgets import LoadingIndicator
yield LoadingIndicator()
```

## Form Widgets

### Checkbox

Toggle checkbox:

```python
from textual.widgets import Checkbox
yield Checkbox("Remember me", id="remember")
```

Access state via `widget.value` (boolean).

### Switch

Toggle switch (on/off):

```python
from textual.widgets import Switch
yield Switch(text="Dark mode", id="dark-mode")
```

### RadioButton / RadioSet

Single-select radio group:

```python
from textual.widgets import RadioSet, RadioButton

with RadioSet(id="theme"):
    yield RadioButton("Light")
    yield RadioButton("Dark")
    yield RadioButton("System")
```

### Select

Dropdown selector:

```python
from textual.widgets import Select
yield Select(
    [("Option A", "a"), ("Option B", "b"), ("Option C", "c")],
    id="choice"
)
```

## Structural Widgets

### Collapsible

Expandable/collapsible content section:

```python
from textual.widgets import Collapsible
with Collapsible("Settings", id="settings"):
    yield Input(placeholder="API Key")
```

### TabbedContent

Tab-based content switching:

```python
from textual.widgets import TabbedContent, TabPanel

with TabbedContent() as tabs:
    with TabPanel("Overview", "overview"):
        yield Static("Overview content")
    with TabPanel("Details", "details"):
        yield Static("Detailed content")
```

### ContentSwitcher

Switch between content panels programmatically:

```python
from textual.widgets import ContentSwitcher

with ContentSwitcher(initial="panel-a", id="switcher"):
    yield Static("Panel A", id="panel-a")
    yield Static("Panel B", id="panel-b")
```

### Rule

Horizontal or vertical divider line:

```python
from textual.widgets import Rule
yield Rule()  # horizontal
yield Rule(line="=", caption="Section")
```

### Placeholder

Temporary content placeholder:

```python
from textual.widgets import Placeholder
yield Placeholder("Coming soon")
```

## Link

Clickable link that triggers an action:

```python
from textual.widgets import Link
yield Link("Go Home", url="app.go_home")
```
