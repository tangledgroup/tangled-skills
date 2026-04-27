# Progress and Live Display

Rich provides powerful tools for displaying continuously updating information in the terminal, including progress bars for long-running tasks and live-updating displays for real-time data.

## Basic Progress — track()

For simple single-task progress, wrap any iterable with `track()`:

```python
from rich.progress import track
import time

for i in track(range(100), description="Processing..."):
    time.sleep(0.05)  # Simulate work
```

This yields values from the sequence while displaying a progress bar with description, percentage, and estimated time remaining.

## Advanced Progress — Progress Class

For multiple tasks or custom columns, use the `Progress` class as a context manager:

```python
from rich.progress import Progress
import time

with Progress() as progress:
    task1 = progress.add_task("[red]Downloading...", total=1000)
    task2 = progress.add_task("[green]Processing...", total=1000)
    task3 = progress.add_task("[cyan]Cooking...", total=1000)

    while not progress.finished:
        progress.update(task1, advance=0.5)
        progress.update(task2, advance=0.3)
        progress.update(task3, advance=0.9)
        time.sleep(0.02)
```

### Task Management

- `add_task(description, total=N)` — Add a task, returns a Task ID
- `update(task_id, advance=N)` — Increment progress by N steps
- `update(task_id, completed=N)` — Set absolute completion
- `progress.finished` — Boolean, True when all tasks complete

The `total` value is the number of steps to reach 100%. A step can be bytes processed, items handled, or any unit meaningful to your application.

### Starting and Stopping

Context manager is recommended. Without it, call `start()` and `stop()` explicitly:

```python
progress = Progress()
progress.start()
try:
    task = progress.add_task("Working...", total=100)
    do_work(task)
finally:
    progress.stop()
```

### Indeterminate Progress

When you don't know the total yet, use `start=False` or `total=None` for a pulsing animation:

```python
task = progress.add_task("Waiting...", start=False)
# ... later when you know the total ...
progress.start_task(task, total=1000)
```

### Hiding Tasks

Set `visible=False` on `add_task()` or update the task's `visible` property.

### Transient Progress

Make the display disappear on exit instead of leaving the last frame:

```python
with Progress(transient=True) as progress:
    task = progress.add_task("Working", total=100)
    do_work(task)
```

### Auto Refresh

Default refresh rate is 10 times per second. Adjust with `refresh_per_second`:

```python
progress = Progress(refresh_per_second=2)
```

Disable entirely with `auto_refresh=False` and call `progress.refresh()` manually.

### Expand

Stretch progress to full terminal width: `Progress(expand=True)`

## Progress Columns

Customize what information appears in the progress display:

```python
from rich.progress import Progress, SpinnerColumn, TimeElapsedColumn

progress = Progress(
    SpinnerColumn(),
    *Progress.get_default_columns(),
    TimeElapsedColumn(),
)
```

### Default Columns

Equivalent to:

```python
Progress(
    TextColumn("[progress.description]{task.description}"),
    BarColumn(),
    TaskProgressColumn(),
    TimeRemainingColumn(),
)
```

### Available Column Classes

- `BarColumn` — The progress bar itself
- `TextColumn` — Arbitrary text (format string with `{task.*}` access)
- `TimeElapsedColumn` — Time since task started
- `TimeRemainingColumn` — Estimated time remaining
- `MofNCompleteColumn` — "completed/total" format
- `FileSizeColumn` — Progress as file size (steps = bytes)
- `TotalFileSizeColumn` — Total file size display
- `DownloadColumn` — Download progress display
- `TransferSpeedColumn` — Transfer speed (steps = bytes)
- `SpinnerColumn` — Spinner animation
- `RenderableColumn` — Arbitrary Rich renderable

Custom columns: extend `ProgressColumn`.

### Format Strings

Access task properties in column format strings:

```python
TextColumn("{task.description}")
TextColumn("{task.completed} of {task.total}")
TextColumn("Info: {task.fields[extra]}")  # Custom fields from update()
```

Pass extra fields via `progress.update(task_id, extra="some value")`, accessed as `task.fields["extra"]`.

### Table Column Ratios

Control column widths in the progress table:

```python
from rich.table import Column
from rich.progress import Progress, BarColumn, TextColumn

text_col = TextColumn("{task.description}", table_column=Column(ratio=1))
bar_col = BarColumn(bar_width=None, table_column=Column(ratio=2))
progress = Progress(text_col, bar_col, expand=True)
```

## Print / Log During Progress

Access the internal console via `progress.console`:

```python
with Progress() as progress:
    task = progress.add_task("Working", total=10)
    for job in range(10):
        progress.console.print(f"Working on job #{job}")
        run_job(job)
        progress.advance(task)
```

Or pass your own Console: `Progress(console=my_console)`

## Redirecting stdout/stderr

By default, Rich redirects stdout/stderr so built-in `print()` doesn't break the progress display. Disable with `redirect_stdout=False` or `redirect_stderr=False`.

## Reading Files with Progress

Track file reading progress automatically:

```python
import json
import rich.progress

with rich.progress.open("data.json", "rb") as f:
    data = json.load(f)
```

Wrap existing file objects with `wrap_file()`:

```python
from rich.progress import wrap_file
from urllib.request import urlopen

response = urlopen("https://example.com")
size = int(response.headers["Content-Length"])

with wrap_file(response, size) as f:
    for line in f:
        process(line)
```

## Nesting Progress Bars

Create progress bars within existing progress contexts — inner bars display below the outer:

```python
from rich.progress import track

for count in track(range(10)):
    for letter in track("ABCDEF", transient=True):
        print(f"Stage {count}{letter}")
```

## Multiple Progress Instances

Use a `Live` display to host multiple Progress instances with different columns:

```python
from rich.live import Live
from rich.progress import Progress

live = Live()
live.start()
progress1 = Progress(console=live.console)
progress2 = Progress(console=live.console)
```

## Customizing Progress

Override `get_renderables()` to wrap the display:

```python
from rich.panel import Panel
from rich.progress import Progress

class MyProgress(Progress):
    def get_renderables(self):
        yield Panel(self.make_tasks_table(self.tasks))
```

## Live Display

The `Live` class builds custom continuously-updating terminal displays:

```python
import time
from rich.live import Live
from rich.table import Table

table = Table()
table.add_column("ID")
table.add_column("Value")

with Live(table, refresh_per_second=4):
    for i in range(20):
        time.sleep(0.3)
        table.add_row(str(i), f"value {i}")
```

### Updating the Renderable

Replace the entire renderable with `live.update()`:

```python
with Live(initial_table(), refresh_per_second=4) as live:
    for _ in range(40):
        time.sleep(0.4)
        live.update(generate_new_table())
```

### Alternate Screen

Full-screen mode: `Live(renderable, screen=True)`

### Transient Display

Disappear on exit: `Live(renderable, transient=True)`

### Auto Refresh

Default 4 times/second. Set `refresh_per_second=N` or disable with `auto_refresh=False`.

### Vertical Overflow

- `"ellipsis"` — Show "..." when content exceeds terminal height (default)
- `"crop"` — Hide overflow silently
- `"visible"` — Show entire renderable (cannot properly clear display)

### Print / Log During Live

```python
with Live(table, refresh_per_second=4) as live:
    live.console.print("Working on row #5")
```

### Nesting Lives

Inner `Live` instances display below the outer one (supported since 14.0.0).

## Status and Spinners

Display a spinner with a message while work is in progress:

```python
with console.status("Working...") as status:
    do_work()

with console.status("Monkeying around...", spinner="monkey"):
    do_work()
```

View available spinners: `python -m rich.spinner`

Demo: `python -m rich.status`
