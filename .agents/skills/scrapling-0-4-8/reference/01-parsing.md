# Parsing

## Contents
- Selector Class
- Selectors (List) Class
- TextHandler and TextHandlers
- AttributesHandler
- Five Selection Methods
- DOM Traversal
- Generating Selectors

## Selector Class

The core parsing object. Import via `from scrapling import Selector` or `from scrapling.parser import Selector`.

```python
page = Selector('<html>...</html>', url='https://example.com')
```

Constructor arguments:
- `content` — HTML as `str` or `bytes` (required)
- `url` — base URL for the page (used by adaptive feature)
- `encoding` — parsing encoding, default `UTF-8`
- `keep_comments` — keep HTML comments, default `False`
- `keep_cdata` — keep CDATA sections, default `False`
- `adaptive`, `storage`, `storage_args` — for adaptive feature (see reference/03-adaptive-scraping.md)

Key properties:
- `.tag` — element tag name (`'html'` for root)
- `.text` — direct text content only
- `.get_all_text(strip=True, ignore_tags=('script', 'style'))` — all recursive text
- `.html_content` — serialized outer HTML
- `.body` — raw content (bytes on Response objects since v0.4)
- `.attrib` — element attributes as `AttributesHandler`
- `.path` — list of ancestor elements
- `.json()` — parse text content as JSON (uses raw copy if available)

All properties are lazily loaded for performance.

## Selectors (List) Class

Returned by selection methods that match multiple elements. Inherits from Python `list`, so supports indexing, slicing, iteration, and `len()`.

Additional methods:
- `.css(selector)` / `.xpath(expression)` — chain selectors on contained elements
- `.get(default=None)` — serialized string of first element, or `default` if empty
- `.getall()` — serialized strings of all elements as `TextHandlers` list
- `.extract_first` / `.extract` — Scrapy-compatible aliases for `get()` / `getall()`
- `.re(pattern)` / `.re_first(pattern)` — regex across all contained text
- `.search(fn)` — first element matching a predicate function, or `None`
- `.filter(fn)` — all elements matching a predicate function
- `.first` / `.last` — safe access to first/last element (returns `None` if empty)
- `.length` — equivalent to `len()`

Text node selectors (`::text`, `/text()`, `::attr()`, `/@attr`) return `Selector` objects with `tag` set to `"#text"`. Use `.get()` on them for the text value.

```python
page.css('.price::text').get()      # First price text
page.css('.price::text').getall()   # All price texts as TextHandlers
```

## TextHandler and TextHandlers

`TextHandler` is a string subclass returned in place of strings nearly everywhere. Supports all standard string operations, which return `TextHandler` again (chainable).

Additional methods:
- `.re(pattern, clean_match=False, case_sensitive=True)` — regex match, returns `TextHandlers`
- `.re_first(pattern, ...)` — first regex match as `TextHandler`, or `None`
- `.json()` — parse as JSON object
- `.clean(remove_entities=False)` — remove extra whitespace and consecutive spaces
- `.sort(reverse=False)` — sort characters

`TextHandlers` is a list subclass of `TextHandler` objects, with the same `.re()` and `.re_first()` methods. `re_first` on `TextHandlers` runs regex on each item and returns the first match found.

## AttributesHandler

Read-only dict-like object storing element attributes. Supports standard dict access (`attrib['href']`, `'href' in attrib`) but not mutation.

Additional methods:
- `.search_values(value, partial=False)` — find attributes by value, returns generator of `{key: value}` dicts
- `.json_string` — serialize attributes to JSON bytes

## Five Selection Methods

### 1. CSS Selectors
```python
page.css('.product')                    # All matches → Selectors
page.css('.product')[0]                 # First match → Selector
page.css('h1::text').get()              # Text of first h1
page.css('a::attr(href)').get()         # href of first a
```

CSS3 selectors per W3C spec via `cssselect`. Non-standard pseudo-elements: `::text` for text nodes, `::attr(name)` for attribute values.

### 2. XPath Selectors
```python
page.xpath('//*[@class="product"]')     # All matches → Selectors
page.xpath('//h1/text()').get()         # Text of first h1
page.xpath('//a/@href').get()           # href of first a
```

Uses `lxml` XPath engine. No `has-class()` extension — use `.has_class()` method instead.

### 3. Find by Tag/Attributes/Functions (`find` / `find_all`)
```python
page.find('div', class_='quote')                    # First match
page.find_all('div', {'class': 'quote'})            # All divs with class=quote
page.find_all({'itemtype': 'http://schema.org/...'})  # Any tag with attribute
page.find_all(lambda e: len(e.children) > 0)        # Elements with children
page.find_all(['div', 'span'], {'class': 'quote'})  # Multiple tag names
```

Waterfall filtering: tag names → attributes → regex patterns → functions. Attribute operators: `attr*` (contains), `attr$` (ends with).

### 4. Find by Text Content
```python
page.find_by_text('Product Name', first_match=True, partial=False, case_sensitive=False)
```

Arguments: `first_match`, `partial` (substring match), `case_sensitive`, `clean_match` (normalize whitespace).

### 5. Find by Regex
```python
import re
page.find_by_regex(r'£[\d\.]+', first_match=True)
page.find_by_regex(re.compile(r'£[\d\.]+'))  # Compiled pattern also accepted
```

Same arguments as `find_by_text`.

### Finding Similar Elements
```python
element = page.find_by_text('Tipping the Velvet')
similar = element.find_similar(ignore_attributes=['title'], similarity_threshold=0.2)
```

Algorithm: same DOM depth → same tag/parent/grandparent tags → fuzzy attribute matching (default 20% threshold). Useful for extracting repeated structures (product grids, table rows, reviews).

## DOM Traversal

- `.parent` — parent element
- `.children` — direct child elements
- `.below_elements` — all descendants (nested children)
- `.siblings` — sibling elements
- `.next` / `.previous` — next/previous sibling
- `.iterancestors()` — iterate up the ancestor chain
- `.find_ancestor(lambda e: ...)` — find first ancestor matching predicate
- `.has_class('classname')` — check if element has a class

## Generating Selectors

Generate reusable CSS/XPath selectors for any element:
```python
element.generate_css_selector       # Short CSS selector (uses id if available)
element.generate_full_css_selector  # Full path from root
element.generate_xpath_selector     # Short XPath
element.generate_full_xpath_selector  # Full path from root
```
