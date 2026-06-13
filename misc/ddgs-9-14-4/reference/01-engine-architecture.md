# Search Engine Architecture

## Contents
- DDGS Class and Lazy Loading
- BaseSearchEngine
- Engine Registration
- Result Aggregation
- Adding a Custom Backend

## DDGS Class and Lazy Loading

The `DDGS` class uses a metaclass proxy (`_ProxyMeta`) for lazy loading. The real implementation is imported only on first instantiation:

```python
class _ProxyMeta(type):
    _lock: threading.Lock = threading.Lock()
    _real_cls: type["DDGS"] | None = None

    @classmethod
    def _load_real(cls) -> type["DDGS"]:
        if cls._real_cls is None:
            with cls._lock:
                if cls._real_cls is None:
                    cls._real_cls = importlib.import_module(".ddgs", package=__name__).DDGS
        return cls._real_cls
```

This avoids importing heavy dependencies until the class is actually used. The `globals()["DDGS"]` is replaced with the real class after first load, so subsequent calls bypass the proxy entirely.

## BaseSearchEngine

All search backends inherit from `BaseSearchEngine[T]` (generic over result type). Key attributes and methods:

### Class Variables

| Variable | Type | Description |
|----------|------|-------------|
| `name` | `ClassVar[str]` | Unique engine key (e.g., `"google"`, `"bing"`) |
| `category` | `ClassVar[Literal["text","images","videos","news","books"]]` | Search category |
| `provider` | `ClassVar[str]` | Source name (e.g., `"Bing"` for DuckDuckGo results) |
| `disabled` | `ClassVar[bool]` | If True, engine is skipped |
| `priority` | `ClassVar[float]` | Ranking priority (default: 1) |
| `search_url` | `str` | Search endpoint URL |
| `search_method` | `ClassVar[str]` | `"GET"` or `"POST"` |
| `headers_update` | `ClassVar[Mapping[str, str]]` | Additional HTTP headers |
| `items_xpath` | `ClassVar[str]` | XPath for result items in HTML |
| `elements_xpath` | `ClassVar[Mapping[str, str]]` | Key→XPath mapping for fields |
| `elements_replace` | `ClassVar[Mapping[str, str]]` | Post-extraction string replacements |

### Constructor

```python
def __init__(self, proxy: str | None = None, timeout: int | None = None, *, verify: bool | str = True)
```

Creates an `HttpClient` instance and applies header updates.

### Key Methods

- `build_payload(query, region, safesearch, timelimit, page, **kwargs)` — Build request parameters (abstract, must override)
- `request(*args, **kwargs)` — Make HTTP request, returns HTML text or None
- `extract_tree(html_text)` — Parse HTML with lxml
- `pre_process_html(html_text)` — Pre-process before extraction (hook for subclasses)
- `extract_results(html_text)` — Parse HTML tree, extract fields via XPath
- `post_extract_results(results)` — Post-process results list (hook for subclasses)
- `search(query, region, safesearch, timelimit, page, **kwargs)` — Full search pipeline

## Engine Registration

Engines are registered in `ddgs/engines/__init__.py` via an `ENGINES` dict:

```python
ENGINES = {
    "text": {"google": Google, "bing": Bing, ...},
    "images": {"duckduckgo": Duckduckgo, "bing": Bing},
    "videos": {"duckduckgo": Duckduckgo},
    "news": {"bing": Bing, "duckduckgo": Duckduckgo, "yahoo": Yahoo},
    "books": {"annasarchive": AnnasArchive},
}
```

The `DDGS._search()` method uses this dict to find engines by category and name.

## Result Aggregation

When `backend="auto"` (default), DDGS:

1. Spawns threads via `ThreadPoolExecutor` calling each engine's `search()` in parallel
2. Collects results from all engines
3. Deduplicates by URL
4. Ranks using `ResultsAggregator` and `SimpleFilterRanker`
5. Returns top N results

## Adding a Custom Backend

To add a new search engine:

1. Create `ddgs/engines/<name>.py`
2. Subclass `BaseSearchEngine[T]` where T is the result dataclass (`TextResult`, `ImagesResult`, etc.)
3. Set class variables: `name`, `category`, `provider`, `search_url`, `search_method`, `items_xpath`, `elements_xpath`
4. Implement `build_payload()` to construct request parameters
5. Register in `ddgs/engines/__init__.py` under the correct category in the `ENGINES` dict
6. Add integration tests in `tests/`

## Exception Handling

DDGS defines custom exceptions in `ddgs/exceptions.py`:

- `DDGSException` — Base exception
- `RatelimitException` — HTTP 429 / rate limit hit
- `TimeoutException` — Request timed out

Pattern: `raise SomeException(msg)` with `raise ... from ex` for chained exceptions.
