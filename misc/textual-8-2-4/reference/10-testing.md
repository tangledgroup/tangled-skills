# Testing

## Test Framework

Textual works with any async-capable test framework. The recommended setup is pytest with pytest-asyncio:

```ini
# pyproject.toml or pytest.ini
[tool.pytest.ini_options]
asyncio_mode = auto
```

## run_test() and Pilot

Use `App.run_test()` instead of `App.run()` for headless testing. It returns a `Pilot` object for simulating interactions:

```python
async def test_keys():
    app = MyApp()
    async with app.run_test() as pilot:
        await pilot.press("r")
        assert app.screen.styles.background == Color.parse("red")
```

## Simulating Key Presses

Press individual keys or type sequences:

```python
await pilot.press("a")           # Single key
await pilot.press("h", "e", "l", "l", "o")  # Type "hello"
await pilot.press("enter")       # Non-printable key
await pilot.press("ctrl+c")      # Modifier + key
```

## Simulating Clicks

Click widgets by CSS selector:

```python
await pilot.click("#submit")     # By ID
await pilot.click(Button)        # By type
await pilot.click()              # Click at (0, 0)
```

With offsets and modifiers:
```python
await pilot.click("#slider", offset=(10, -1))
await pilot.click("#btn", control=True)
await pilot.click("#btn", times=2)  # Double click
```

## Changing Screen Size

Test different terminal sizes:

```python
async with app.run_test(size=(100, 50)) as pilot:
    ...
```

Default size is (80, 24).

## Pausing the Pilot

Wait for pending messages to process:

```python
await pilot.pause()              # Wait for message queue
await pilot.pause(delay=0.1)     # Delay then wait
```

Use this when asserting state that depends on async message processing.

## Full Test Example

```python
from textual.color import Color
from myapp import MyApp

async def test_key_bindings():
    app = MyApp()
    async with app.run_test() as pilot:
        await pilot.press("r")
        assert app.screen.styles.background == Color.parse("red")

async def test_button_clicks():
    app = MyApp()
    async with app.run_test() as pilot:
        await pilot.click("#submit")
        await pilot.pause()
        assert some_state_is_correct()
```

## Snapshot Testing

Textual provides a pytest plugin for visual regression testing. It generates SVG screenshots of your app and compares them across runs. Install via the official pytest-textual-snapshot package.
