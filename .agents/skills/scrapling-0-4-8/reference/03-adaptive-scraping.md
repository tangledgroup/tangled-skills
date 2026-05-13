# Adaptive Scraping

## Contents
- How It Works
- Enabling Adaptive Mode
- CSS/XPath Selection Way (auto_save + adaptive)
- Manual Save/Retrieve/Relocate
- Unique Properties Tracked
- Storage System

## How It Works

Adaptive scraping lets scrapers survive website structure changes by intelligently tracking and relocating elements. Two phases:

1. **Save Phase** — Store unique properties of found elements in a database (SQLite by default)
2. **Match Phase** — When elements aren't found with the original selector, compare all page elements against saved properties using similarity scoring

No AI involved — uses deterministic similarity algorithms comparing tag names, text, attributes, siblings, and DOM path.

## Enabling Adaptive Mode

Enable globally on Selector or fetcher:

```python
# With Selector
from scrapling import Selector
page = Selector(html_doc, adaptive=True, url='https://example.com')

# With any fetcher
from scrapling.fetchers import Fetcher
Fetcher.adaptive = True
page = Fetcher.get('https://example.com')
```

The `url` argument (or the fetcher's URL) isolates adaptive data per domain. Use `adaptive_domain` to treat different URLs as the same site:

```python
Fetcher.configure(adaptive=True, adaptive_domain='stackoverflow.com')
```

## CSS/XPath Selection Way (auto_save + adaptive)

The simplest approach — the selector string itself serves as the database identifier:

```python
# First run: element exists, save its properties
element = page.css('#p1', auto_save=True)

# Later, after website redesign: element not found normally, relocate it
element = page.css('#p1', adaptive=True)
```

Works with `xpath()` too. The selector string is used as the identifier automatically. Override with `identifier='custom_name'` on both `auto_save` and `adaptive`.

## Manual Save/Retrieve/Relocate

For elements found by any method (text search, regex, filters), use manual control:

```python
# Find element by any method
element = page.find_by_text('Tipping the Velvet', first_match=True)

# Save with custom identifier
page.save(element, 'my_special_element')

# Later, retrieve and relocate
element_dict = page.retrieve('my_special_element')
results = page.relocate(element_dict, selector_type=True)  # Returns list of Selector objects
# Without selector_type=True, returns list of lxml.etree elements
```

## Unique Properties Tracked

For each saved element, Scrapling stores:
- Element: tag name, text, attributes (names and values), siblings (tag names only), path (tag names only)
- Parent: tag name, attributes (names and values), text

Comparison is similarity-based, not exact. Attribute value order is considered (e.g., class name ordering).

## Known Limitations

- `auto_save` only saves properties of the **first element** in selection results
- Combined CSS selectors (comma-separated) are split and each executed alone
- If no match is found, verify data was saved: `page.retrieve('identifier')`

Troubleshooting wrong matches: use more specific selectors or save with more context (e.g., the parent element).

## Storage System

Default storage is SQLite. Custom backends are supported for shared databases across machines (e.g., Redis, Firebase).

To write a custom storage:
1. Inherit from `scrapling.core.storage.StorageSystemMixin`, accept `url` string in `__init__`
2. Decorate class with `@functools.lru_cache(None)` (Singleton pattern)
3. Implement `save(element, identifier)` — convert element to dict via `_StorageTools.element_to_dict()`, store with unique key of `(url, identifier)`
4. Implement `retrieve(identifier)` — return element dict or `None`

Pass custom storage to Selector or fetcher:
```python
page = Selector(html, adaptive=True, storage=RedisStorage, storage_args={'host': 'localhost'})
```
