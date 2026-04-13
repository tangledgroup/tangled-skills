# JavaScript-Python Communication

## JS API Bridge Overview

The JS API bridge enables direct two-way communication between Python and JavaScript without HTTP/REST overhead. This is the recommended approach for most pywebview applications.

### Exposing Python to JavaScript

**Method 1: Using `js_api` parameter (recommended)**

```python
import webview

class Calculator:
    """Python class exposed to JavaScript"""
    
    def add(self, a, b):
        return a + b
    
    def subtract(self, a, b):
        return a - b
    
    def multiply(self, a, b):
        return a * b
    
    def divide(self, a, b):
        if b == 0:
            raise ValueError("Cannot divide by zero")
        return a / b

window = webview.create_window(
    'Calculator',
    './index.html',
    js_api=Calculator()  # Instance of class
)
webview.start()
```

**JavaScript usage:**
```javascript
// Call methods (returns Promise)
pywebview.api.add(5, 3).then(result => {
    console.log('5 + 3 =', result);  // Output: 8
});

pywebview.api.divide(10, 2).then(result => {
    console.log('10 / 2 =', result);  // Output: 5
}).catch(error => {
    console.error('Error:', error.message);
});
```

**Method 2: Using `window.expose()` (runtime exposure)**

```python
import webview

def greet(name):
    return f'Hello, {name}!'

def calculate_total(items):
    return sum(item['price'] for item in items)

window = webview.create_window('Dynamic API', './index.html')

# Expose individual functions at runtime
window.expose('greet', greet)
window.expose('calculate_total', calculate_total)

webview.start()
```

**JavaScript usage:**
```javascript
pywebview.api.greet('Alice').then(message => {
    console.log(message);  // Output: Hello, Alice!
});

const items = [{price: 10}, {price: 20}, {price: 30}];
pywebview.api.calculate_total(items).then(total => {
    console.log('Total:', total);  // Output: 60
});
```

### Supported Data Types

**Python → JavaScript:**
- `int` → `number`
- `float` → `number`
- `str` → `string`
- `bool` → `boolean`
- `list` → `array`
- `dict` → `object`
- `None` → `null`
- Custom objects → Serialized as dict (if possible)

**JavaScript → Python:**
- `number` → `int` or `float`
- `string` → `str`
- `boolean` → `bool`
- `array` → `list`
- `object` → `dict`
- `null` → `None`

### Complex Data Examples

```python
import webview
import json
from datetime import datetime

class DataApi:
    def get_user(self, user_id):
        """Return complex nested data"""
        return {
            'id': user_id,
            'name': 'John Doe',
            'email': 'john@example.com',
            'active': True,
            'roles': ['admin', 'user'],
            'metadata': {
                'created': datetime.now().isoformat(),
                'last_login': '2024-01-15T10:30:00'
            }
        }
    
    def process_items(self, items):
        """Receive and process array of objects"""
        processed = []
        for item in items:
            processed.append({
                'id': item['id'],
                'name': item['name'].upper(),
                'price': item['price'] * 1.1  # Add 10% tax
            })
        return processed
    
    def log_event(self, event_data):
        """Log structured data"""
        timestamp = datetime.now().isoformat()
        log_entry = {
            'timestamp': timestamp,
            'event': event_data['type'],
            'data': event_data['payload']
        }
        print(json.dumps(log_entry, indent=2))
        return {'logged': True, 'timestamp': timestamp}

window = webview.create_window('Complex Data', './index.html', js_api=DataApi())
webview.start()
```

**JavaScript usage:**
```javascript
// Get user data
pywebview.api.get_user(123).then(user => {
    console.log('User:', user);
    console.log('Name:', user.name);
    console.log('Roles:', user.roles);
    console.log('Created:', user.metadata.created);
});

// Process items
const items = [
    {id: 1, name: 'apple', price: 1.50},
    {id: 2, name: 'banana', price: 0.75},
    {id: 3, name: 'cherry', price: 3.00}
];

pywebview.api.process_items(items).then(processed => {
    console.log('Processed items:', processed);
    // Output: [{id: 1, name: 'APPLE', price: 1.65}, ...]
});

// Log events
pywebview.api.log_event({
    type: 'button_click',
    payload: {
        button_id: 'submit',
        user_id: 123
    }
}).then(result => {
    console.log('Event logged at:', result.timestamp);
});
```

### Error Handling

**Python side - Raise exceptions:**

```python
import webview

class Api:
    def divide(self, a, b):
        if b == 0:
            raise ValueError("Division by zero is not allowed")
        return a / b
    
    def fetch_user(self, user_id):
        if user_id < 1:
            raise ValueError(f"Invalid user ID: {user_id}")
        
        # Simulate database lookup
        users = {1: 'Alice', 2: 'Bob', 3: 'Charlie'}
        if user_id not in users:
            raise KeyError(f"User {user_id} not found")
        
        return users[user_id]

window = webview.create_window('Error Handling', './index.html', js_api=Api())
webview.start()
```

**JavaScript side - Catch errors:**

```javascript
// Handle division by zero
pywebview.api.divide(10, 0)
    .then(result => console.log('Result:', result))
    .catch(error => {
        console.error('Error type:', error.name);  // ValueError
        console.error('Error message:', error.message);  // Division by zero...
        alert('Cannot divide by zero!');
    });

// Handle missing user
pywebview.api.fetch_user(999)
    .then(user => console.log('User:', user))
    .catch(error => {
        if (error.name === 'KeyError') {
            alert('User not found');
        } else {
            alert('Error: ' + error.message);
        }
    });

// Using async/await
async function handleUserLookup(id) {
    try {
        const user = await pywebview.api.fetch_user(id);
        console.log('Found user:', user);
    } catch (error) {
        console.error('Failed to fetch user:', error.message);
        throw error;  // Re-throw if needed
    }
}
```

### JavaScript to Python Events

Trigger Python callbacks from JavaScript:

```python
import webview

class EventApi:
    def __init__(self):
        self.event_log = []
    
    def on_button_click(self, button_id, timestamp):
        """Called when button is clicked"""
        print(f'Button {button_id} clicked at {timestamp}')
        self.event_log.append({
            'type': 'click',
            'button': button_id,
            'time': timestamp
        })
        return {'status': 'recorded'}
    
    def on_form_submit(self, form_data):
        """Called when form is submitted"""
        print(f'Form submitted: {form_data}')
        # Process form data
        validation_result = self.validate_form(form_data)
        return validation_result
    
    def validate_form(self, data):
        errors = []
        if not data.get('email'):
            errors.append('Email is required')
        if not data.get('password') or len(data['password']) < 8:
            errors.append('Password must be at least 8 characters')
        
        return {
            'valid': len(errors) == 0,
            'errors': errors
        }
    
    def get_event_history(self):
        """Return all logged events"""
        return self.event_log

api = EventApi()
window = webview.create_window('Events', './index.html', js_api=api)
webview.start()
```

**JavaScript usage:**
```javascript
// Button click handler
document.getElementById('submitBtn').addEventListener('click', () => {
    const timestamp = new Date().toISOString();
    
    pywebview.api.on_button_click('submitBtn', timestamp)
        .then(result => {
            console.log('Event recorded:', result.status);
        });
});

// Form submission
document.getElementById('loginForm').addEventListener('submit', (e) => {
    e.preventDefault();
    
    const formData = {
        email: document.getElementById('email').value,
        password: document.getElementById('password').value
    };
    
    pywebview.api.on_form_submit(formData)
        .then(result => {
            if (result.valid) {
                alert('Form is valid! Submitting...');
                // Proceed with submission
            } else {
                result.errors.forEach(error => {
                    console.error('Validation error:', error);
                });
                alert('Form validation failed: ' + result.errors.join(', '));
            }
        });
});

// Get event history
pywebview.api.get_event_history()
    .then(events => {
        console.log('Event history:', events);
    });
```

### Python to JavaScript Callbacks

Call JavaScript functions from Python:

```python
import webview

def update_ui():
    """Called periodically to update UI"""
    window.evaluate_js('''
        document.getElementById('counter').textContent = 
            document.getElementById('counter').textContentAsNumber + 1;
    ''')

window = webview.create_window('Python Callbacks', './index.html')

# Call JavaScript function directly
window.evaluate_js('alert("Hello from Python!")')

# Get value from JavaScript
result = window.evaluate_js('document.title')
print(f'Page title: {result}')

webview.start(update_ui)
```

**With callback for async operations:**

```python
import webview

def handle_js_result(result):
    """Callback for JavaScript promise"""
    print(f'Received from JavaScript: {result}')

# Execute JavaScript that returns a promise
window.evaluate_js('''
    new Promise(resolve => {
        setTimeout(() => {
            resolve({message: 'Hello after 2 seconds!', timestamp: Date.now()});
        }, 2000);
    });
''', handle_js_result)
```

### Running JavaScript Without Return Value

Use `run_js()` for fire-and-forget JavaScript execution:

```python
import webview

window = webview.create_window('Run JS', './index.html')

# Execute without waiting for result
window.run_js('''
    console.log('This runs but returns nothing');
    document.body.style.backgroundColor = '#f0f0f0';
''')

# Trigger JavaScript event
window.run_js('''
    const event = new CustomEvent('dataUpdated', {detail: {source: 'python'}});
    document.dispatchEvent(event);
''')

webview.start()
```

### DOM Manipulation from Python

pywebview provides limited DOM support without writing JavaScript:

```python
import webview

window = webview.create_window('DOM Demo', './index.html')

# Get elements by selector (returns list)
elements = window.get_elements('div.class-name')
print(f'Found {len(elements)} elements')

# Get element text
first_element = window.get_first_element('#username')
if first_element:
    print(f'Username: {first_element.text}')

# Set element text
window.set_element_text('#status', 'Loading...')

# Get attribute
href = window.get_element_attribute('a.link', 'href')
print(f'Link href: {href}')

# Set attribute
window.set_element_attribute('img.logo', 'src', 'new-logo.png')

webview.start()
```

**Note:** DOM methods are limited. For complex DOM manipulation, use `evaluate_js()` with custom JavaScript.

### Multiple Windows with Shared API

```python
import webview

class SharedApi:
    def __init__(self):
        self.shared_data = {}
    
    def set_value(self, key, value):
        self.shared_data[key] = value
        return True
    
    def get_value(self, key):
        return self.shared_data.get(key)
    
    def broadcast(self, message):
        """Send message to all windows"""
        for window in webview.windows:
            window.evaluate_js(f'window.receiveMessage("{message}")')

api = SharedApi()

# Create multiple windows with same API instance
window1 = webview.create_window('Window 1', './index.html', js_api=api)
window2 = webview.create_window('Window 2', './index.html', js_api=api)

webview.start()
```

**JavaScript in each window:**
```javascript
// Receive broadcasts from Python
window.receiveMessage = function(message) {
    console.log('Received broadcast:', message);
};

// Share data between windows via Python
pywebview.api.set_value('shared_key', 'hello from window 1')
    .then(() => {
        return pywebview.api.get_value('shared_key');
    })
    .then(value => {
        console.log('Shared value:', value);
    });
```

### Performance Tips

1. **Batch operations:** Combine multiple API calls when possible
2. **Avoid large data transfers:** Only send necessary data
3. **Use callbacks for async:** Don't block the UI thread
4. **Cache results:** Store frequently-used data in JavaScript
5. **Minimize round trips:** Design API to reduce call count

```python
# ❌ Inefficient: Multiple calls
pywebview.api.get_user_id()
pywebview.api.get_user_name()
pywebview.api.get_user_email()

# ✅ Efficient: Single call
pywebview.api.get_user_profile()  # Returns {id, name, email}
```

### Security Considerations

1. **Validate all input:** Never trust JavaScript-provided data
2. **Sanitize outputs:** Prevent XSS when returning HTML
3. **Implement authentication:** Protect sensitive API methods
4. **Rate limiting:** Prevent abuse of expensive operations

```python
import webview
from functools import wraps

def validate_input(func):
    """Decorator for input validation"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        # Validate all arguments
        for arg in args:
            if isinstance(arg, str) and len(arg) > 1000:
                raise ValueError("Input too long")
        return func(*args, **kwargs)
    return wrapper

class SecureApi:
    @validate_input
    def process_data(self, user_input):
        # Safe to process validated input
        return user_input.upper()
```

See [Security Guide](references/05-debugging.md) for comprehensive security recommendations.
