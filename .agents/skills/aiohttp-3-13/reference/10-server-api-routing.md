# Server API: Routing

Complete reference for aiohttp routing, including route tables, decorators, and advanced routing patterns.

## RouteTableDef (Decorator Style)

Define routes using decorators similar to Flask:

```python
from aiohttp import web

routes = web.RouteTableDef()

@routes.get('/')
async def index(request):
    return web.Response(text="Home")

@routes.post('/users')
async def create_user(request):
    data = await request.json()
    return web.json_response({'id': 123, **data}, status=201)

@routes.get('/users/{user_id}')
async def get_user(request):
    user_id = request.match_info['user_id']
    return web.json_response({'id': user_id})

@routes.put('/users/{user_id}')
async def update_user(request):
    user_id = request.match_info['user_id']
    data = await request.json()
    return web.json_response({'id': user_id, **data})

@routes.delete('/users/{user_id}')
async def delete_user(request):
    user_id = request.match_info['user_id']
    return web.Response(status=204)

app = web.Application()
app.add_routes(routes)
```

## add_routes (List Style)

Define routes as a list of route tuples:

```python
from aiohttp import web

async def index(request):
    return web.Response(text="Home")

async def create_user(request):
    return web.json_response({'created': True})

async def get_user(request):
    return web.json_response({'id': request.match_info['user_id']})

app = web.Application()
app.add_routes([
    web.get('/', index),
    web.post('/users', create_user),
    web.get('/users/{user_id}', get_user),
    web.put('/users/{user_id}', update_user),
    web.delete('/users/{user_id}', delete_user),
    web.patch('/users/{user_id}', patch_user),
    web.head('/users/{user_id}', head_user),
    web.options('/users', options_handler),
])
```

## HTTP Method Routes

All standard HTTP methods are supported:

```python
app.add_routes([
    web.get('/', handler),           # GET
    web.post('/', handler),          # POST
    web.put('/', handler),           # PUT
    web.patch('/', handler),         # PATCH
    web.delete('/', handler),        # DELETE
    web.head('/', handler),          # HEAD
    web.options('/', handler),       # OPTIONS
    
    # All methods (catch-all)
    web.route('*', '/path', handler),
])
```

## Path Parameters

### Single Parameter

```python
@routes.get('/users/{user_id}')
async def get_user(request):
    user_id = request.match_info['user_id']
    return web.json_response({'id': user_id})

# Matches: /users/123, /users/abc, /users/any-value
```

### Multiple Parameters

```python
@routes.get('/users/{user_id}/posts/{post_id}')
async def get_post(request):
    user_id = request.match_info['user_id']
    post_id = request.match_info['post_id']
    
    return web.json_response({
        'user_id': user_id,
        'post_id': post_id
    })

# Matches: /users/123/posts/456
```

### Named Parameters with Regex

```python
@routes.get('/users/{user_id:\\d+}')
async def get_user(request):
    # Only matches numeric user_id
    user_id = int(request.match_info['user_id'])
    return web.json_response({'id': user_id})

# Matches: /users/123
# Does NOT match: /users/abc
```

### Common Regex Patterns

```python
@routes.get('/articles/{slug:[a-z-]+}')  # URL slugs
async def get_article(request):
    slug = request.match_info['slug']

@routes.get('/files/{filename:.+\\.[a-zA-Z]{3}}')  # Files with extension
async def get_file(request):
    filename = request.match_info['filename']

@routes.get('/version/{ver:v\\d+}')  # Version strings like v1, v2.0
async def get_version(request):
    ver = request.match_info['ver']
```

## Route Priority

Routes are matched in order of addition. More specific routes should be added first:

```python
# Correct: Specific route before parameterized route
app.add_routes([
    web.get('/users/new', new_user),      # Specific
    web.get('/users/{user_id}', get_user), # Parameterized
])

# Incorrect: May cause /users/new to match as user_id='new'
app.add_routes([
    web.get('/users/{user_id}', get_user), # Parameterized
    web.get('/users/new', new_user),       # Specific (never reached)
])
```

## Static File Serving

### Basic Static Route

```python
# Serve files from directory
app.router.add_static('/static', path='/var/www/static')

# URLs:
# /static/css/style.css -> /var/www/static/css/style.css
# /static/images/logo.png -> /var/www/static/images/logo.png
```

### Static with Custom Name

```python
app.router.add_static('/static', '/var/www/static', name='static')

# Generate URLs in handlers
async def handler(request):
    css_url = request.app.router['static'].url_for(filename='css/style.css')
    return web.Response(text=f'<link rel="stylesheet" href="{css_url}">')
```

### Multiple Static Routes

```python
app.router.add_static('/assets', '/var/www/assets')
app.router.add_static('/uploads', '/var/uploads', name='uploads')
app.router.add_static('/media', '/var/media', name='media')
```

### Static Route Options

```python
app.router.add_static(
    '/static',
    path='/var/www/static',
    name='static',
    expect_handler=None,  # Custom Expect handler
    append_version=True,  # Append version query param for cache busting
)
```

## View Classes

Class-based views for organizing handlers:

```python
from aiohttp import web

class UserView(web.View):
    async def get(self):
        """GET /users - List all users"""
        users = await self.get_all_users()
        return web.json_response(users)
    
    async def post(self):
        """POST /users - Create new user"""
        data = await self.request.json()
        user = await self.create_user(data)
        return web.json_response(user, status=201)

class UserDetailView(web.View):
    async def get(self):
        """GET /users/{id} - Get user by ID"""
        user_id = self.request.match_info['user_id']
        user = await self.get_user(user_id)
        return web.json_response(user)
    
    async def put(self):
        """PUT /users/{id} - Update user"""
        user_id = self.request.match_info['user_id']
        data = await self.request.json()
        user = await self.update_user(user_id, data)
        return web.json_response(user)
    
    async def delete(self):
        """DELETE /users/{id} - Delete user"""
        user_id = self.request.match_info['user_id']
        await self.delete_user(user_id)
        return web.Response(status=204)

# Register views
app.router.add_view('/users', UserView)
app.router.add_view('/users/{user_id}', UserDetailView)
```

## Dynamic Route Generation

### url_for Method

Generate URLs from route names:

```python
@routes.get('/', name='index')
async def index(request):
    # Generate URL for this route
    url = request.app.router['index'].url_for()
    
@routes.get('/users/{user_id}', name='user')
async def get_user(request):
    # Generate URL with parameters
    url = request.app.router['user'].url_for(user_id=123)
    # Returns: /users/123

@routes.get('/posts', name='posts')
async def list_posts(request):
    # Generate URL with query params
    url = request.app.router['posts'].url_for(query={'page': 2, 'limit': 10})
    # Returns: /posts?page=2&limit=10
```

### Static URL Generation

```python
app.router.add_static('/static', '/var/www/static', name='static')

# Generate static file URL
async def handler(request):
    css_url = request.app.router['static'].url_for(filename='css/style.css')
    # Returns: /static/css/style.css
```

## Route Information

### Accessing Route Metadata

```python
for route in app.router.routes():
    print(f"Method: {route.method}")
    print(f"Path: {route.path}")
    print(f"Handler: {route.handler}")
    print(f"Name: {route.name}")
```

### Route Matching Info

```python
@routes.get('/users/{user_id}/posts/{post_id}')
async def get_post(request):
    # Access matched parameters
    info = request.match_info
    
    user_id = info['user_id']
    post_id = info['post_id']
    
    # Check if parameter exists
    if 'comment_id' in info:
        comment_id = info['comment_id']
```

## Advanced Routing

### Custom Router

Implement custom routing logic:

```python
from aiohttp import abc

class CustomRouter(abc.AbstractRouter):
    def __init__(self):
        self._routes = []
    
    async def resolve(self, request):
        # Custom resolution logic
        for route in self._routes:
            if route.matches(request):
                return route
        
        # No match found
        return MatchInfoFound(None, HTTPNotFound())
    
    def add_route(self, method, path, handler, **kwargs):
        route = Route(method, path, handler)
        self._routes.append(route)

app = web.Application(router=CustomRouter())
```

### Conditional Routes

Add routes conditionally:

```python
from aiohttp import web

def add_api_routes(app, enable_v2=False):
    app.add_routes([
        web.get('/api/v1/users', users_v1),
        web.post('/api/v1/users', create_user_v1),
    ])
    
    if enable_v2:
        app.add_routes([
            web.get('/api/v2/users', users_v2),
            web.post('/api/v2/users', create_user_v2),
        ])

app = web.Application()
add_api_routes(app, enable_v2=True)
```

### Route Groups (Manual)

Create logical route groups:

```python
def setup_user_routes(app):
    app.add_routes([
        web.get('/users', list_users),
        web.post('/users', create_user),
        web.get('/users/{user_id}', get_user),
        web.put('/users/{user_id}', update_user),
        web.delete('/users/{user_id}', delete_user),
    ])

def setup_post_routes(app):
    app.add_routes([
        web.get('/posts', list_posts),
        web.post('/posts', create_post),
        web.get('/posts/{post_id}', get_post),
    ])

app = web.Application()
setup_user_routes(app)
setup_post_routes(app)
```

## URL Query Parameters in Routes

### Accessing Query Params

```python
@routes.get('/search')
async def search(request):
    # Get query parameters
    q = request.query.get('q', '')
    page = request.query.get('page', '1')
    limit = request.query.get('limit', '10')
    
    # Or as dict
    params = dict(request.query)
    
    return web.json_response({
        'query': q,
        'page': int(page),
        'limit': int(limit)
    })

# GET /search?q=hello&page=2&limit=20
```

### Query Parameter Validation

```python
@routes.get('/items')
async def list_items(request):
    try:
        page = int(request.query.get('page', '1'))
        limit = int(request.query.get('limit', '10'))
        
        if page < 1:
            raise web.HTTPBadRequest("Page must be >= 1")
        if not 1 <= limit <= 100:
            raise web.HTTPBadRequest("Limit must be between 1 and 100")
            
    except ValueError:
        raise web.HTTPBadRequest("Invalid numeric parameter")
    
    items = await fetch_items(page=page, limit=limit)
    return web.json_response(items)
```

## Route Error Handling

### Method Not Allowed

```python
# Only GET is allowed
app.add_routes([web.get('/resource', get_resource)])

# POST to /resource will return 405 Method Not Allowed automatically
```

### Custom 405 Handler

```python
async def method_not_allowed_handler(request):
    return web.json_response(
        {'error': 'Method not allowed'},
        status=405,
        headers={'Allow': 'GET, HEAD'}
    )

# Add to specific route or globally
```
