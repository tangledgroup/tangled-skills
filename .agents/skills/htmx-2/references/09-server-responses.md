# htmx Server Responses Reference

This reference covers response headers, status codes, and server-side patterns for htmx 2.x.

## Response Headers

htmx supports special response headers that control client behavior.

### HX-Location

Redirect to a different URL:

```http
HX-Location: /new-page
```

```python
# Flask example
response = make_response(render_template('partial.html'))
response.headers['HX-Location'] = '/new-page'
return response
```

Client will navigate to `/new-page` after swap completes.

### HX-Redirect

Full page redirect:

```http
HX-Redirect: /login
```

```python
# Flask
response = make_response()
response.headers['HX-Redirect'] = '/login'
return response
```

Client performs full page navigation to `/login`.

### HX-Refresh

Refresh the entire page:

```http
HX-Refresh: true
```

```python
# Flask
response = make_response(render_template('success.html'))
response.headers['HX-Refresh'] = 'true'
return response
```

Page reloads after swap completes.

### HX-Replace-Url

Replace current URL in browser history:

```http
HX-Replace-Url: true
```

```http
HX-Replace-Url: /new-path
```

```python
# Flask
response = make_response(render_template('content.html'))
response.headers['HX-Replace-Url'] = '/new-path'
return response
```

### HX-Push-Url

Push new URL to browser history:

```http
HX-Push-Url: /new-path
```

```python
# Flask
response = make_response(render_template('content.html'))
response.headers['HX-Push-Url'] = '/articles/123'
return response
```

### HX-Trigger

Trigger client-side events:

```http
HX-Trigger: reload
```

```http
HX-Trigger: {"name": "dataLoaded", "detail": {"id": 123}}
```

```python
# Flask
response = make_response(render_template('content.html'))
response.headers['HX-Trigger'] = 'reload'
return response
```

```html
<!-- Client listens for trigger -->
<div hx-trigger="reload"
     hx-get="/refresh-content">
    Content
</div>
```

### HX-Trigger-After-Settle

Trigger event after settling completes:

```http
HX-Trigger-After-Settle: animation-start
```

```python
# Flask
response = make_response(render_template('content.html'))
response.headers['HX-Trigger-After-Settle'] = 'animate'
return response
```

### HX-Reswap

Control how content is swapped:

```http
HX-Reswap: outerHTML
HX-Reswap: none
HX-Reswap: true
```

```python
# Flask - force outerHTML swap
response = make_response(render_template('card.html'))
response.headers['HX-Reswap'] = 'outerHTML'
return response
```

**Values:**
- `innerHTML`, `outerHTML`, etc. - Standard swap styles
- `none` - Don't swap
- `true` - Use default swap

## Status Codes

htmx handles HTTP status codes with specific behaviors:

### Success Codes (2xx)

| Code | Behavior |
|------|----------|
| 200 | OK - Normal swap |
| 201 | Created - Normal swap |
| 204 | No Content - No swap, request successful |

```python
# Return 204 for successful no-content response
return '', 204
```

### Redirect Codes (3xx)

| Code | Behavior |
|------|----------|
| 301-399 | Redirect - Treated as error by default |

Configure custom handling:

```javascript
htmx.config.responseHandling = [
    { code: '302', swap: 'none', error: false }
];
```

### Client Error Codes (4xx)

| Code | Behavior |
|------|----------|
| 400 | Bad Request - Error, no swap |
| 401 | Unauthorized - Error, no swap |
| 403 | Forbidden - Error, no swap |
| 404 | Not Found - Error, no swap |
| 409 | Conflict - Error, no swap |
| 422 | Unprocessable Entity - Error, no swap |

```python
# Return validation errors
from flask import make_response

errors = {'email': 'Invalid email format'}
response = make_response(render_template('error_form.html', errors=errors), 422)
return response
```

### Server Error Codes (5xx)

| Code | Behavior |
|------|----------|
| 500 | Internal Server Error - Error, no swap |
| 502 | Bad Gateway - Error, no swap |
| 503 | Service Unavailable - Error, no swap |

### Special Codes

| Code | Behavior |
|------|----------|
| 286 | No Operation - Stop polling |

```python
# Stop client polling
return 'Stop', 286
```

## Response Handling Configuration

Configure how htmx handles different status codes:

```javascript
htmx.config.responseHandling = [
    // Don't swap on 204, but don't treat as error
    { code: '204', swap: 'none' },
    
    // Treat 301-399 as redirects, not errors
    { code: '301-399', swap: 'none', error: true },
    
    // Custom handling for 422 (validation errors)
    { code: '422', swap: 'innerHTML', error: false },
    
    // Handle 500 with custom error display
    { code: '500', swap: 'none', error: true }
];
```

## Server-Side Patterns

### Partial Page Responses

Return HTML fragments, not full pages:

```python
# Flask - return partial template
def get_article(request):
    article = get_article_by_id(request.args['id'])
    return render_template('article_partial.html', article=article)
```

```html
<!-- templates/article_partial.html -->
<article id="article-{{ article.id }}">
    <h2>{{ article.title }}</h2>
    <div class="content">{{ article.body }}</div>
</article>
```

### Out-of-Band Swaps in Responses

Include OOB elements in response:

```python
# Flask - response with OOB swaps
def submit_form(request):
    # Process form
    success = process_form(request.form)
    
    return render_template('form_response.html', 
                          success=success,
                          message='Form submitted!' if success else 'Error occurred',
                          counter=get_submission_count())
```

```html
<!-- templates/form_response.html -->
<!-- OOB swap for flash message -->
<div id="flash-messages" hx-swap-oob="innerHTML">
    {% if success %}
    <div class="alert alert-success">{{ message }}</div>
    {% else %}
    <div class="alert alert-danger">{{ message }}</div>
    {% endif %}
</div>

<!-- OOB swap for counter -->
<div id="submission-counter" hx-swap-oob="innerHTML">
    Submissions: {{ counter }}
</div>

<!-- Main response content -->
<div class="result">
    <p>Processing complete. <a href="/new">Submit another?</a></p>
</div>
```

### Dynamic Headers Based on Context

```python
# Flask - add headers conditionally
def process_action(request):
    response = make_response(render_template('result.html'))
    
    # Redirect after successful operation
    if request.form.get('redirect'):
        response.headers['HX-Redirect'] = '/dashboard'
    
    # Trigger client event
    response.headers['HX-Trigger'] = 'success'
    
    # Push URL to history
    response.headers['HX-Push-Url'] = f"/items/{item_id}"
    
    return response
```

### Error Handling with Partial Responses

```python
# Flask - return error HTML for specific fields
def validate_form(request):
    errors = {}
    
    if not request.form.get('email'):
        errors['email'] = 'Email is required'
    
    if errors:
        # Return 422 with error HTML
        error_html = render_template('form_errors.html', errors=errors)
        response = make_response(error_html, 422)
        response.headers['HX-Reswap'] = 'none'  # Don't swap main content
        return response
    
    # Success
    return render_template('success.html')
```

```html
<!-- templates/form_errors.html -->
<div id="email-error" hx-swap-oob="innerHTML">
    {% if errors.email %}
    <span class="error">{{ errors.email }}</span>
    {% endif %}
</div>
```

### Streaming Responses

Server-Sent Events implementation:

```python
# Flask - SSE endpoint
from flask import Response

def event_stream():
    while True:
        # Generate event data
        data = {'time': datetime.now().isoformat(), 'count': get_count()}
        
        # Yield SSE format
        yield f"event: update\n"
        yield f"data: {json.dumps(data)}\n\n"
        
        time.sleep(5)

@app.route('/events')
def events():
    return Response(event_stream(), 
                    mimetype='text/event-stream')
```

### WebSocket Implementation

```python
# Flask-SocketIO example
from flask_socketio import SocketIO, emit

socketio = SocketIO(app)

@socketio.on('connect')
def handle_connect():
    emit('connected', {'message': 'Connected to server'})

@socketio.on('chat_message')
def handle_message(data):
    # Broadcast to all clients
    emit('message', data, broadcast=True)

@socketio.on('typing')
def handle_typing(data):
    # Emit to specific room
    emit('user_typing', data, room=data['room'])
```

## Content-Type Handling

### HTML Responses (Default)

```python
# Flask - default HTML response
response = make_response(render_template('content.html'))
response.headers['Content-Type'] = 'text/html'
return response
```

### JSON Responses with Extensions

Use `json-enc` extension for JSON responses:

```python
# Flask - JSON response
from flask import jsonify

@app.route('/api/data')
def get_data():
    return jsonify({
        'items': [1, 2, 3],
        'total': 3
    })
```

```html
<!-- Client with json-enc extension -->
<div hx-ext="json-enc"
     hx-get="/api/data"
     hx-swap="innerHTML">
    Loading...
</div>
```

### Template Rendering for JSON

Use `client-side-templates` extension:

```python
# Flask - return JSON
@app.route('/api/user/<id>')
def get_user(id):
    user = get_user_by_id(id)
    return jsonify({
        'name': user.name,
        'email': user.email,
        'active': user.active
    })
```

```html
<!-- Template -->
<template id="user-template">
    <div class="user">
        <h3>{{name}}</h3>
        <p>{{email}}</p>
        <span class="{{active ? 'active' : 'inactive'}}">{{active ? 'Active' : 'Inactive'}}</span>
    </div>
</template>

<!-- Usage -->
<div hx-ext="client-side-templates"
     hx-get="/api/user/123"
     data-template="user-template">
    Loading...
</div>
```

## Caching Strategies

### Cache-Control Headers

```python
# Flask - control caching
response = make_response(render_template('content.html'))

# No caching for dynamic content
response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate'

# Or cache for 1 hour
response.headers['Cache-Control'] = 'public, max-age=3600'

return response
```

### ETag Validation

```python
# Flask - ETag support
from wsgiref.utils import get_current_url

def get_article(request):
    article_id = request.args['id']
    article = get_article(article_id)
    
    # Check If-None-Match header
    if_none_match = request.headers.get('If-None-Match')
    article_etag = generate_etag(article)
    
    if if_none_match == article_etag:
        return '', 304  # Not Modified
    
    response = make_response(render_template('article.html', article=article))
    response.headers['ETag'] = article_etag
    return response
```

## Security Headers

### CSRF Protection

```python
# Flask - include CSRF token
from flask_wtf.csrf import generate_csrf

@app.context_processor
def csrf_generator():
    return dict(csrf_token=generate_csrf)
```

```html
<!-- Include in all forms -->
<form hx-post="/submit">
    <input type="hidden" name="csrf_token" value="{{ csrf_token }}">
    <button type="submit">Submit</button>
</form>
```

### Content Security Policy

```python
# Flask - CSP headers
response = make_response(render_template('content.html'))
response.headers['Content-Security-Policy'] = (
    "default-src 'self'; "
    "script-src 'self' 'nonce-{{ nonce }}'; "
    "style-src 'self' 'unsafe-inline'"
)
return response
```

## Performance Optimization

### Conditional Rendering

```python
# Flask - check if request is from htmx
def is_htmx_request(request):
    return request.headers.get('HX-Request') == 'true'

@app.route('/page')
def page():
    if is_htmx_request(request):
        # Return partial for htmx
        return render_template('page_partial.html')
    else:
        # Return full page for initial load
        return render_template('page_full.html')
```

### Template Inheritance

```html
<!-- templates/base.html -->
<!DOCTYPE html>
<html>
<head>
    <title>{% block title %}My Site{% endblock %}</title>
    <script src="htmx.min.js"></script>
</head>
<body>
    <nav>{% block nav %}{% endblock %}</nav>
    <main>
        {% block content %}{% endblock %}
    </main>
</body>
</html>

<!-- templates/partial.html (for htmx) -->
{% extends "base.html" %}

{% block content %}
<div class="dynamic-content">
    {{ content }}
</div>
{% endblock %}
```

## Next Steps

- [Common Patterns](10-common-patterns.md) - Complete UI patterns
- [Security Best Practices](12-security-best-practices.md) - Security guidance
- [Performance Optimization](13-performance-optimization.md) - Performance tips
