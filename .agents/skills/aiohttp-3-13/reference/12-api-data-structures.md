# API: Data Structures

Complete reference for aiohttp data structures including FrozenList, ChainMapProxy, and other internal types.

## FrozenList

Mutable list that can be frozen to become immutable.

### Constructor

```python
from aiohttp import FrozenList

# Create from iterable
fl = FrozenList([1, 2, 3, 4, 5])

# Create empty
fl = FrozenList()
```

### Mutable Operations (Before Freeze)

```python
fl = FrozenList([1, 2, 3])

# Add items
fl.append(4)
fl.extend([5, 6])
fl.insert(0, 0)

# Remove items
fl.remove(3)
item = fl.pop()  # Last item
item = fl.pop(0)  # First item

# Modify
fl[0] = 100

# Check frozen status
print(fl.frozen)  # False
```

### Freezing

```python
fl = FrozenList([1, 2, 3])
fl.freeze()

print(fl.frozen)  # True

# These will raise RuntimeError
# fl.append(4)      # RuntimeError
# fl[0] = 100       # RuntimeError
# fl.remove(1)      # RuntimeError

# Read operations still work
print(len(fl))     # 3
print(fl[0])       # 1
for item in fl:    # Iteration works
    print(item)
```

### Use Cases

**Immutable middleware list:**

```python
from aiohttp import FrozenList

class MiddlewareManager:
    def __init__(self):
        self._middlewares = FrozenList()
    
    def add_middleware(self, mw):
        if self._middlewares.frozen:
            raise RuntimeError("Cannot add middleware after freeze")
        self._middlewares.append(mw)
    
    def freeze(self):
        self._middlewares.freeze()
    
    async def handle(self, request, handler):
        # Iterate over frozen list (thread-safe)
        for mw in self._middlewares:
            handler = mw(self.app, handler)
        return await handler(request)
```

**Configuration that shouldn't change:**

```python
async def init_app(app):
    cors_origins = FrozenList([
        'https://example.com',
        'https://app.example.com',
        'https://api.example.com'
    ])
    cors_origins.freeze()
    app['cors_origins'] = cors_origins

async def handler(request):
    # Safe to read, cannot be modified
    origins = request.app['cors_origins']
    if origin in origins:
        response.headers['Access-Control-Allow-Origin'] = origin
```

## ChainMapProxy

Immutable view over multiple mappings (dictionaries).

### Constructor

```python
from aiohttp import ChainMapProxy

# Create from list of dicts
dict1 = {'a': 1, 'b': 2}
dict2 = {'b': 20, 'c': 30}

proxy = ChainMapProxy([dict1, dict2])
```

### Lookup Behavior

Searches mappings in order, returns first match:

```python
proxy = ChainMapProxy([
    {'a': 1, 'b': 2},   # First priority
    {'b': 20, 'c': 30}, # Second priority
])

print(proxy['a'])  # 1 (from first dict)
print(proxy['b'])  # 2 (from first dict, not 20)
print(proxy['c'])  # 30 (from second dict)

# Check existence
print('a' in proxy)  # True
print('d' in proxy)  # False

# Get with default
print(proxy.get('d', 'default'))  # 'default'

# Iterate over keys
for key in proxy:
    print(key, proxy[key])
```

### Use Cases

**Request context layers:**

```python
# Inner scope takes precedence over outer
request_config = ChainMapProxy([
    request.config_dict,      # Request-specific (highest priority)
    request.app['config'],    # App config
    global_defaults           # Global defaults (lowest priority)
])

# Get setting with proper precedence
debug = request_config.get('debug', False)
```

**Environment configuration:**

```python
app_config = ChainMapProxy([
    os.environ,                           # Env vars (highest)
    app['config'],                        # App config
    default_settings                      # Defaults (lowest)
])

api_key = app_config.get('API_KEY')
```

## CIMultiDict

Case-insensitive multi-dictionary for HTTP headers.

### Basic Usage

```python
from multidict import CIMultiDict

headers = CIMultiDict()

# Add headers
headers['Content-Type'] = 'application/json'
headers['X-Custom'] = 'value'

# Case-insensitive access
print(headers['content-type'])  # 'application/json'
print(headers['CONTENT-TYPE'])  # 'application/json'

# Multiple values for same header
headers.add('Set-Cookie', 'session=abc')
headers.add('Set-Cookie', 'theme=dark')

# Get all values
cookies = headers.getall('Set-Cookie')  # ['session=abc', 'theme=dark']

# Get first value
first_cookie = headers.get('Set-Cookie')  # 'session=abc'
```

### Common Operations

```python
headers = CIMultiDict([
    ('Content-Type', 'application/json'),
    ('X-Request-ID', '123'),
    ('X-Request-ID', '456'),  # Duplicate key
])

# Get items
for key, value in headers.items():
    print(f"{key}: {value}")

# Get keys (includes duplicates)
for key in headers.keys():
    print(key)

# Get values
for value in headers.values():
    print(value)

# Check existence
print('Content-Type' in headers)  # True
print('content-type' in headers)  # True (case-insensitive)

# Delete
del headers['X-Request-ID']  # Removes all with this key

# Pop
value = headers.pop('Content-Type')  # Removes and returns
```

### In HTTP Context

```python
async def handler(request):
    # Request headers are CIMultiDictProxy (read-only)
    content_type = request.headers.get('Content-Type')
    
    # Response headers can be modified
    response = web.Response()
    response.headers['Content-Type'] = 'application/json'
    response.headers.add('Set-Cookie', 'session=abc')
    response.headers.add('Set-Cookie', 'theme=dark')
```

## MultiDict

Ordered multi-dictionary (case-sensitive).

### Usage

```python
from multidict import MultiDict

md = MultiDict()

# Add items
md['key'] = 'value1'
md.add('key', 'value2')  # Same key, different value

# Get all values
values = md.getall('key')  # ['value1', 'value2']

# Get first value
first = md.get('key')  # 'value1'

# Case-sensitive!
md['Key'] = 'different'
print(md['key'])   # 'value1'
print(md['Key'])   # 'different'
```

### Query Parameters

```python
async def handler(request):
    # request.query is MultiDictProxy
    
    # GET /search?q=foo&q=bar&page=1
    all_queries = request.query.getall('q')  # ['foo', 'bar']
    first_query = request.query.get('q')     # 'foo'
    page = request.query.get('page', '1')    # '1'
```

## FrozenDict

Immutable dictionary.

### Usage

```python
from aiohttp import FrozenDict

# Create from dict
fd = FrozenDict({'a': 1, 'b': 2})

# Read operations work
print(fd['a'])        # 1
print(fd.get('c'))    # None
print('a' in fd)      # True

# Modification raises TypeError
# fd['c'] = 3         # TypeError
# fd['a'] = 100       # TypeError
# del fd['a']         # TypeError
```

### Use Cases

**Immutable route info:**

```python
# Route match_info is typically FrozenDict
async def handler(request):
    # request.match_info is read-only
    user_id = request.match_info['user_id']
    
    # Cannot modify
    # request.match_info['new_key'] = 'value'  # TypeError
```

## URL (yarl.URL)

URL parsing and manipulation (from yarl library).

### Creating URLs

```python
from yarl import URL

# From string
url = URL('https://example.com:8080/path?query=1#fragment')

# From components
url = URL(
    scheme='https',
    host='example.com',
    port=8080,
    path='/path',
    query={'query': '1'},
    fragment='fragment'
)
```

### URL Properties

```python
url = URL('https://user:pass@example.com:8080/path/to/resource?foo=bar&baz=qux#section')

print(url.scheme)        # 'https'
print(url.host)          # 'example.com'
print(url.port)          # 8080
print(url.user)          # 'user'
print(url.password)      # 'pass'
print(url.path)          # '/path/to/resource'
print(url.query)         # MultiDictProxy({'foo': 'bar', 'baz': 'qux'})
print(url.fragment)      # 'section'
print(url.authority)     # 'user:pass@example.com:8080'
```

### URL Manipulation

```python
url = URL('https://example.com/path')

# Add query parameters
new_url = url.with_query({'page': 1, 'limit': 10})
# https://example.com/path?page=1&limit=10

# Update query
new_url = url.with_query(page=2)
# https://example.com/path?page=2

# Change path
new_url = url.with_path('/new/path')
# https://example.com/new/path

# Change host
new_url = url.with_host('other.com')
# https://other.com/path

# Combine URLs
base = URL('https://example.com/api/')
relative = URL('v1/users')
full = base / relative
# https://example.com/api/v1/users
```

### In aiohttp Context

```python
async def handler(request):
    # request.url is yarl.URL
    url: URL = request.url
    
    print(url.scheme)  # 'http' or 'https'
    print(url.host)    # Hostname
    print(url.path)    # Path
    
    # Generate new URL
    new_url = url.with_query(page=2)
    
    # Relative URL (no scheme/host/port)
    rel_url = request.rel_url
```

## Other Data Types

### AsyncContextManager

For session management:

```python
async with aiohttp.ClientSession() as session:
    # Session automatically closed after block
    async with session.get(url) as resp:
        data = await resp.text()
```

### Signal

For event handling:

```python
from aiohttp import Signal

# Create signal
on_startup = Signal()

# Register handler
async def handler(app):
    print("Starting up")

on_startup.append(handler)

# Fire signal
await on_startup.send(app)
```

### Best Practices

**Use FrozenList for:**
- Middleware chains (after initialization)
- Immutable configuration lists
- Route registries

**Use ChainMapProxy for:**
- Layered configuration
- Request context with fallbacks
- Environment variable precedence

**Use CIMultiDict for:**
- HTTP headers (case-insensitive, multiple values)
- Cookie handling

**Use MultiDict for:**
- Query parameters
- Form data

**Use FrozenDict for:**
- Route match information
- Immutable configuration dicts
