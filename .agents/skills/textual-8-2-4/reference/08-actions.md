# Actions

## Action Methods

Action methods are regular methods prefixed with `action_`. They can be sync or async:

```python
class MyApp(App):
    def action_set_background(self, color: str) -> None:
        self.screen.styles.background = color

    async def action_fetch_data(self, url: str) -> None:
        ...
```

Actions are intended to be invoked through string syntax (bindings, links) rather than direct calls.

## Action String Syntax

Action strings replicate Python function call syntax without using `eval`:

- `"bell"` → `action_bell()`
- `"set_bg('red')"` → `action_set_bg("red")`
- `"push_screen('modal')"` → `action_push_screen("modal")`

Parameters must be valid Python literals: strings, numbers, booleans, lists, dicts. Variables and expressions are not allowed.

## Running Actions Programmatically

Use `run_action()` to parse and dispatch action strings:

```python
await self.run_action("set_bg('blue')")
```

This is a coroutine — the calling method must be async.

## Namespaces

Actions resolve on the class where they are defined. Use namespaces to target specific objects:

- `app` — invokes on the App
- `screen` — invokes on the current Screen
- `focused` — invokes on the focused widget

Example in a link:
```python
Static("Click [@click=app.quit]here[/] to quit")
```

## Links in Content

Embed clickable action links in markup with `@click`:

```python
Static("[@click=bell]Ring bell[/] or [@click=quit]Quit[/]")
```

Links are underlined by default, indicating they are clickable.

## Dynamic Actions (check_action)

Control whether an action is available at runtime using `check_action`:

```python
def check_action(self, name: str, parameters: tuple) -> bool | None:
    if name == "prev_page" and self.page == 0:
        return False   # Hide the key binding
    if name == "next_page" and self.page == self.max_page:
        return None    # Show dimmed (disabled but visible)
    return True        # Normal behavior
```

Return values:
- `True` — show key, allow action
- `False` — hide key, block action
- `None` — show dimmed, block action

This keeps the Footer bindings accurate to current state.

## Built-in Actions

Textual provides many built-in actions on App and Screen:

- `quit` / `exit` — exit the application
- `bell` — play terminal bell
- `push_screen(name)` / `pop_screen` — screen navigation
- `scroll_up` / `scroll_down` / `scroll_left` / `scroll_right`
- `toggle_theme` — cycle through registered themes
- `suspend_process` — suspend the app (Ctrl+Z equivalent, Unix only)
