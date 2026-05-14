# Workers and Concurrency

## Why Workers

Blocking the UI thread (message handler) freezes the interface. Network requests, file I/O, and CPU-heavy work should run concurrently. Textual's Worker API manages this safely.

## run_worker()

Schedule a coroutine to run in the background:

```python
async def on_input_changed(self, event: Input.Changed) -> None:
    self.run_worker(self.fetch_data, event.value, exclusive=True)
```

Returns a `Worker` object immediately without blocking. The worker runs concurrently with UI updates.

### Exclusive Workers

Set `exclusive=True` to cancel any previous workers from the same function before starting a new one. This prevents stale results from out-of-order responses:

```python
self.run_worker(self.fetch_data, city, exclusive=True)
```

## @work Decorator

Alternative to manual `run_worker()` — decorates a method to auto-create workers:

```python
from textual import work

class MyApp(App):
    @work(exclusive=True)
    async def fetch_data(self, url: str) -> None:
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            self.update_display(response.text)
```

Call it like a regular method — no `await` needed:
```python
self.fetch_data("https://api.example.com/data")
```

## Worker Return Values

Access results after completion via `worker.result`:

```python
worker = self.run_worker(self.compute, data)
# Later...
if worker.state == WorkerState.SUCCESS:
    print(worker.result)
```

Or use `await worker.wait()` to block until complete (but this blocks the handler — prefer events instead).

## Worker State Lifecycle

Workers transition through states:

- `PENDING` → created, not yet started
- `RUNNING` → currently executing
- `SUCCESS` → completed, result available in `worker.result`
- `ERROR` → raised exception, error in `worker.error`
- `CANCELLED` → cancelled before completion

Check state: `worker.state`.

## Worker Events

Handle state changes:

```python
def on_worker_state_changed(self, event: Worker.StateChanged) -> None:
    if event.worker.state == WorkerState.SUCCESS:
        self.notify("Fetch complete")
    elif event.worker.state == WorkerState.ERROR:
        self.notify(f"Error: {event.worker.error}")
```

## Cancelling Workers

Cancel a running worker:

```python
worker.cancel()
```

Raises `CancelledError` inside the coroutine.

## Error Handling

By default, worker exceptions exit the app. Set `exit_on_error=False` to handle gracefully:

```python
self.run_worker(self.risky_task, exit_on_error=False)
```

Or with decorator:
```python
@work(exit_on_error=False)
async def risky_task(self) -> None:
    ...
```

## Thread Workers

For non-async APIs, run functions in threads:

```python
self.run_worker(self.cpu_heavy_function, thread=True)
```

The `@work` decorator also accepts `thread=True`.

## Worker Manager

Access all active workers via `app.workers`:

```python
for worker in self.workers:
    print(worker.state)
```

Workers are tied to the DOM node where they were created. Removing a widget or popping a screen automatically cancels its workers.
