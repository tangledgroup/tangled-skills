# htmx Security Best Practices

This reference covers security considerations and best practices for htmx 2.x applications.

## CSRF Protection

### Always Use CSRF Tokens

Include CSRF tokens in all state-changing requests:

```html
<!-- Include token in all forms -->
<form hx-post="/submit">
    <input type="hidden" name="_token" value="{{ csrf_token }}">
    <button type="submit">Submit</button>
</form>
```

```python
# Flask example
from flask_wtf.csrf import generate_csrf, validate_csrf

@app.context_processor
def csrf_generator():
    return dict(csrf_token=generate_csrf)

@app.before_request
def validate_csrf_token():
    if request.method in ['POST', 'PUT', 'DELETE', 'PATCH']:
        validate_csrf(request.form.get('_token'))
```

### Add CSRF Token via JavaScript

Automatically add token to all requests:

```javascript
document.body.addEventListener('htmx:configRequest', (event) => {
    const token = document.querySelector('meta[name="csrf-token"]').content;
    event.detail.headers['X-CSRF-Token'] = token;
});
```

```html
<meta name="csrf-token" content="{{ csrf_token }}">
```

### Verify Origin Header

Check Origin header on server:

```python
# Flask - verify origin
@app.before_request
def check_origin():
    origin = request.headers.get('Origin')
    allowed_origins = ['https://yoursite.com']
    
    if origin and origin not in allowed_origins:
        abort(403)
```

## XSS Prevention

### Never Trust User Input

Always escape user-generated content:

```python
# Flask - use template auto-escaping
return render_template('page.html', user_content=user_input)
# Template will auto-escape {{ user_content }}

# Dangerous - don't do this
# return render_template('page.html', 
#                        user_content=mark_safe(user_input))
```

### Use CSP (Content Security Policy)

Implement strict CSP headers:

```python
# Flask - set CSP headers
@app.after_request
def set_security_headers(response):
    response.headers['Content-Security-Policy'] = (
        "default-src 'self'; "
        "script-src 'self' 'nonce-{{ nonce }}'; "
        "style-src 'self' 'unsafe-inline'; "
        "img-src 'self' data: https:; "
        "font-src 'self'; "
        "connect-src 'self'; "
        "frame-ancestors 'none'"
    )
    return response
```

### Configure htmx for CSP Compliance

```javascript
// Disable eval for CSP compliance
htmx.config.allowEval = false;

// Set nonce for inline scripts
const nonce = document.querySelector('meta[name="csp-nonce"]').content;
htmx.config.inlineScriptNonce = nonce;
htmx.config.inlineStyleNonce = nonce;
```

### Sanitize HTML Responses

If accepting HTML from users:

```python
# Use DOMPurify on server or sanitize library
from bs4 import BeautifulSoup
import html

def sanitize_html(html_content):
    # Remove dangerous tags and attributes
    soup = BeautifulSoup(html_content, 'html.parser')
    for tag in soup(['script', 'iframe', 'object', 'embed']):
        tag.decompose()
    
    for attr in ['onclick', 'onload', 'onerror', 'onmouseover']:
        for elem in soup.find_all(attrs={attr: True}):
            del elem[attr]
    
    return str(soup)
```

## Clickjacking Prevention

### Set X-Frame-Options Header

Prevent your site from being embedded in iframes:

```python
# Flask
@app.after_request
def set_frame_options(response):
    response.headers['X-Frame-Options'] = 'DENY'
    # Or 'SAMEORIGIN' if you need same-origin framing
    return response
```

Or use CSP `frame-ancestors`:

```python
response.headers['Content-Security-Policy'] = (
    "frame-ancestors 'none'"  # No framing allowed
    # or "frame-ancestors 'self' https://trusted.com"
)
```

## Clickjacking with htmx

Be careful with boosted links:

```html
<!-- Avoid boosting external links -->
<a href="https://external.com" hx-boost="true">External</a>
<!-- Can be clickjacked if external site doesn't set X-Frame-Options -->

<!-- Safe: don't boost external links -->
<a href="https://external.com" target="_blank" rel="noopener noreferrer">
    External
</a>
```

## Authentication & Authorization

### Check Auth on Server Side

Never rely on client-side auth checks:

```python
# Always verify on server
@app.route('/admin', methods=['POST'])
def admin_action():
    if not current_user.is_authenticated:
        abort(401)
    
    if not current_user.has_role('admin'):
        abort(403)
    
    # Process request
```

### Handle Auth Failures Gracefully

Return appropriate responses for auth failures:

```python
# Flask - return login prompt on 401
@app.errorhandler(401)
def unauthorized(error):
    if request.headers.get('HX-Request'):
        # Return login form for htmx
        return render_template('login_partial.html'), 401
    else:
        # Redirect to login for full page
        return redirect(url_for('login'))
```

### Use Response Headers for Auth

Redirect to login via headers:

```python
response = make_response(render_template('login_prompt.html'), 401)
response.headers['HX-Redirect'] = '/login'
return response
```

## Sensitive Data Protection

### Never Expose Secrets in Responses

Avoid including sensitive data in HTML responses:

```python
# Bad - exposes internal IDs
return render_template('user.html', 
                      user={'id': user.internal_id, 'name': user.name})

# Good - use public IDs only
return render_template('user.html', 
                      user={'id': user.public_id, 'name': user.name})
```

### Use OOB Swaps Carefully

Don't leak data through OOB swaps:

```html
<!-- Bad - admin-only data in response visible to all -->
<div id="admin-panel" hx-swap-oob="true">
    {% if user.is_admin %}{{ sensitive_data }}{% endif %}
</div>

<!-- Good - server checks permissions before including -->
{% if user.is_admin %}
<div id="admin-panel" hx-swap-oob="true">
    {{ sensitive_data }}
</div>
{% endif %}
```

## Rate Limiting

### Implement Server-Side Rate Limiting

Prevent abuse of htmx endpoints:

```python
# Flask with flask-limiter
from flask_limiter import Limiter

limiter = Limiter(app, key_func=get_remote_address)

@limiter.limit("10/minute")
@app.route('/api/action', methods=['POST'])
def api_action():
    # Process request
```

### Client-Side Request Throttling

Use htmx synchronization:

```html
<!-- Prevent rapid repeated requests -->
<button hx-post="/action" 
        hx-sync="#action-button @cancel"
        hx-disabled-elt="this">
    Submit Action
</button>
```

## Input Validation

### Validate All Inputs on Server

Never trust client validation:

```python
# Flask with WTForms
class SubmissionForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    message = TextAreaField('Message', validators=[DataRequired(), Length(max=1000)])

@app.route('/submit', methods=['POST'])
def submit():
    form = SubmissionForm()
    if form.validate():
        # Process validated data
        return process(form.email.data, form.message.data)
    else:
        # Return validation errors
        return render_template('form_errors.html', errors=form.errors), 422
```

### Sanitize File Uploads

Validate and sanitize uploaded files:

```python
import os
from werkzeug.utils import secure_filename

ALLOWED_EXTENSIONS = {'png', 'jpg', 'gif'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        abort(400)
    
    file = request.files['file']
    if file.filename == '':
        abort(400)
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        # Additional: check file content, not just extension
        # Check file size, magic bytes, etc.
        file.save(os.path.join(upload_folder, filename))
        return 'File uploaded'
    
    abort(400)
```

## Secure WebSocket/SSE Connections

### Validate WebSocket Messages

Sanitize all incoming WebSocket data:

```python
# Flask-SocketIO
@socketio.on('chat_message')
def handle_message(data):
    # Validate user
    if not current_user.is_authenticated:
        emit('error', 'Unauthorized')
        return
    
    # Sanitize message
    message = sanitize_html(data.get('message', ''))
    
    # Validate length
    if len(message) > 500:
        emit('error', 'Message too long')
        return
    
    # Process safe message
    emit('message', {'text': message}, broadcast=True)
```

### Use WSS (Secure WebSocket)

Always use WSS in production:

```html
<!-- Production -->
<div hx-ws="connect:wss://yoursite.com/ws">
    Secure WebSocket
</div>

<!-- Development only -->
<div hx-ws="connect:ws://localhost/ws">
    Insecure (dev only)
</div>
```

## Security Headers

### Essential Headers

Set these headers on all responses:

```python
@app.after_request
def set_security_headers(response):
    # Prevent MIME type sniffing
    response.headers['X-Content-Type-Options'] = 'nosniff'
    
    # Disable IE compatibility mode
    response.headers['X-Compatibles'] = 'IE=Edge'
    
    # Prevent clickjacking
    response.headers['X-Frame-Options'] = 'DENY'
    
    # Enable XSS filter
    response.headers['X-XSS-Protection'] = '1; mode=block'
    
    # Referrer policy
    response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
    
    return response
```

### HSTS (HTTP Strict Transport Security)

Force HTTPS:

```python
response.headers['Strict-Transport-Security'] = (
    'max-age=31536000; includeSubDomains; preload'
)
```

## Secure Configuration

### Disable eval for CSP

```javascript
// Prevent code injection via hx-vars
htmx.config.allowEval = false;
```

### Restrict Script Tags

```javascript
// Don't evaluate script tags in responses
htmx.config.allowScriptTags = false;
```

### Same-Origin Requests Only

```javascript
// Prevent requests to other domains
htmx.config.selfRequestsOnly = true;
```

### Limit History Cache

```javascript
// Reduce localStorage usage
htmx.config.historyCacheSize = 5;
```

## Logging & Monitoring

### Log Suspicious Activity

```python
# Flask - log potential attacks
import logging

logger = logging.getLogger(__name__)

@app.before_request
def log_suspicious_activity():
    # Log unusual request patterns
    if request.headers.get('HX-Request'):
        logger.info(f"htmx request from {request.remote_addr} to {request.path}")
    
    # Log failed auth attempts
    if request.method == 'POST' and '/login' in request.path:
        # Track failed attempts for rate limiting
        pass
```

### Monitor for Abuse

Track metrics:
- Request frequency per user/IP
- Failed authentication attempts
- Unusual htmx event patterns
- WebSocket connection counts

## Security Checklist

- [ ] CSRF tokens on all forms and state-changing requests
- [ ] Content Security Policy headers set
- [ ] X-Frame-Options or frame-ancestors CSP directive
- [ ] Input validation on server side
- [ ] Output escaping in templates
- [ ] Authentication checked on server
- [ ] Rate limiting implemented
- [ ] File upload validation (type, size, content)
- [ ] WebSocket/SSE message sanitization
- [ ] HTTPS enforced (HSTS)
- [ ] Sensitive data not exposed in responses
- [ ] Logging enabled for security events
- [ ] Dependencies kept up to date
- [ ] htmx.config.allowEval = false (if using CSP)
- [ ] htmx.config.selfRequestsOnly = true

## Testing Security

### Manual Testing

1. Try accessing protected routes without auth
2. Attempt CSRF attacks (requests from other domains)
3. Test XSS via form inputs
4. Verify file upload restrictions
5. Check WebSocket authentication

### Automated Testing

```python
# Flask test example
def test_csrf_protection(self):
    response = self.client.post('/submit', data={
        'message': 'test'
        # No CSRF token
    })
    assert response.status_code == 403

def test_xss_prevention(self):
    malicious = '<script>alert("xss")</script>'
    response = self.client.post('/comment', data={'text': malicious})
    assert b'<script>' not in response.data
```

## Resources

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [Content Security Policy Guide](https://developer.mozilla.org/en-US/docs/Web/HTTP/CSP)
- [Flask Security Best Practices](https://flask.palletsprojects.com/en/latest/security/)
- [htmx Security Essay](https://htmx.org/essays/web-security-basics-with-htmx/)

## Next Steps

- [Performance Optimization](13-performance-optimization.md) - Performance tips
- [Common Patterns](10-common-patterns.md) - Secure pattern implementations
