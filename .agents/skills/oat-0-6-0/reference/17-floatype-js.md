# Floatype.js - Floating Autocomplete for Textareas

A super tiny (~1200 bytes minified+gzipped), zero-dependency JavaScript autocomplete/autosuggestion library for rendering floating suggestion widgets in textareas.

[**View Demo**](https://knadh.github.io/floatype.js) | [**GitHub**](https://github.com/knadh/floatype.js)

> **Note**: For dropdown suggestions on `<input>` boxes, see [autocomp.js](https://github.com/knadh/autocomp.js)

## Features

- Floating suggestion widget positioned near cursor
- Zero dependencies, ~1200 bytes minified+gzipped
- Async query support for server-side search
- Keyboard navigation (arrow keys, enter, escape)
- Customizable appearance and behavior
- Works with any textarea element

## Installation

### npm

```bash
npm install @knadh/floatype
```

### ES Module (CDN)

```html
<script type="module">
  import { floatype } from 'https://unpkg.com/@knadh/floatype';
</script>
```

## Basic Usage

### Simple Autocomplete with Local Data

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Floatype Demo</title>
  <style>
    textarea {
      width: 100%;
      height: 200px;
      padding: 15px;
      font-size: 16px;
      border: 1px solid #ccc;
      border-radius: 4px;
    }
    
    /* Floatype widget styles */
    .floatype {
      position: absolute;
      background: #fff;
      border: 1px solid #ccc;
      border-radius: 4px;
      box-shadow: 0 2px 8px rgba(0,0,0,0.15);
      max-height: 200px;
      overflow-y: auto;
      z-index: 1000;
    }
    
    .floatype-item {
      padding: 8px 12px;
      cursor: pointer;
    }
    
    .floatype-item:hover {
      background: #f5f5f5;
    }
    
    .floatype-sel {
      background: #0066cc;
      color: #fff;
    }
  </style>
</head>
<body>
  <textarea placeholder="Type to search for fruits..."></textarea>
  
  <script type="module">
    import { floatype } from 'https://unpkg.com/@knadh/floatype';
    
    const fruits = [
      "apple", "banana", "apricot", "avocado", "blueberry",
      "blackberry", "cherry", "mango", "orange", "pineapple",
      "strawberry", "watermelon", "grapefruit", "kiwi", "peach"
    ];
    
    floatype(document.querySelector("textarea"), {
      onQuery: async (query) => {
        // Filter fruits based on query
        const q = query.trim().toLowerCase();
        return fruits
          .filter(fruit => fruit.startsWith(q))
          .slice(0, 10); // Return top 10 matches
      }
    });
  </script>
</body>
</html>
```

### Server-Side Search with fetch()

```javascript
import { floatype } from '@knadh/floatype';

floatype(document.querySelector("textarea"), {
  onQuery: async (query) => {
    // Fetch suggestions from server
    const resp = await fetch(`/api/search?q=${encodeURIComponent(query)}`);
    const results = await resp.json();
    
    // Return array of suggestion strings
    return results.map(item => item.name);
  }
});
```

### Server Response Format

Your server should return a JSON array:

```json
[
  "javascript",
  "java",
  "jquery",
  "json",
  "jasmine"
]
```

Or with more data (use a formatter):

```json
[
  {"name": "JavaScript", "language": true},
  {"name": "Java", "language": true},
  {"name": "jQuery", "library": true}
]
```

## Advanced Usage

### Custom Item Formatting

```javascript
floatype(textarea, {
  onQuery: async (query) => {
    const resp = await fetch(`/api/search?q=${query}`);
    return resp.json(); // Array of objects
  },
  
  // Custom formatter for display
  itemFormatter: (item) => {
    if (typeof item === 'string') {
      return item;
    }
    
    // For objects, create custom HTML
    const type = item.language ? 'Language' : 'Library';
    return `
      <strong>${item.name}</strong>
      <small style="color: #666;">${type}</small>
    `;
  }
});
```

### Insert Custom Text on Selection

```javascript
floatype(textarea, {
  onQuery: async (query) => {
    return [
      { value: "@john", display: "John Doe" },
      { value: "@jane", display: "Jane Smith" }
    ];
  },
  
  itemFormatter: (item) => item.display,
  
  // Custom insert behavior
  onSelect: (item, textarea) => {
    // Insert the value part instead of display
    const text = item.value || item;
    // Logic to insert at cursor position
    insertAtCursor(textarea, text);
  }
});

function insertAtCursor(textarea, text) {
  const start = textarea.selectionStart;
  const end = textarea.selectionEnd;
  const value = textarea.value;
  
  textarea.value = value.substring(0, start) + text + value.substring(end);
  textarea.selectionStart = textarea.selectionEnd = start + text.length;
}
```

### Trigger Characters

Only show suggestions when user types specific trigger characters:

```javascript
floatype(textarea, {
  // Only trigger on @ or #
  triggers: ['@', '#'],
  
  onQuery: async (query, trigger) => {
    if (trigger === '@') {
      // Fetch user mentions
      return fetchUsers(query);
    } else if (trigger === '#') {
      // Fetch hashtags/topics
      return fetchTopics(query);
    }
  }
});
```

### Debouncing Queries

```javascript
floatype(textarea, {
  onQuery: async (query) => {
    // This is automatically debounced
    const resp = await fetch(`/search?q=${query}`);
    return resp.json();
  },
  
  // Custom debounce delay (default is typically 300ms)
  debounce: 300
});
```

### Unbind/Rebind

```javascript
// Initialize and store the instance
const ft = floatype(textarea, {
  onQuery: async (q) => getSuggestions(q)
});

// Later, unbind to disable
ft.unbind();

// Re-bind when needed
ft.bind();
```

### Multiple Textareas

```javascript
document.querySelectorAll('.mention-input').forEach(textarea => {
  floatype(textarea, {
    onQuery: async (query) => {
      return fetchMentions(query);
    }
  });
});
```

## Styling

### Basic Styles

```css
/* Container for the floating widget */
.floatype {
  position: absolute;
  background: #fff;
  border: 1px solid #ccc;
  border-radius: 4px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.15);
  min-width: 200px;
  max-height: 200px;
  overflow-y: auto;
  z-index: 1000;
  font-family: inherit;
  font-size: 14px;
}

/* Individual suggestion items */
.floatype-item {
  padding: 8px 12px;
  cursor: pointer;
  border-bottom: 1px solid #eee;
}

.floatype-item:last-child {
  border-bottom: none;
}

/* Hover state */
.floatype-item:hover {
  background: #f5f5f5;
}

/* Selected/focused item */
.floatype-sel {
  background: #0066cc;
  color: #fff;
}

/* No results message */
.floatype-no-results {
  padding: 12px;
  color: #666;
  font-style: italic;
}
```

### Dark Mode Support

```css
@media (prefers-color-scheme: dark) {
  .floatype {
    background: #1a1a1a;
    border-color: #444;
    color: #fff;
  }
  
  .floatype-item {
    border-bottom-color: #333;
  }
  
  .floatype-item:hover {
    background: #333;
  }
  
  .floatype-sel {
    background: #0066cc;
    color: #fff;
  }
}
```

### Integration with Oat UI

```css
/* Use Oat's design tokens */
.floatype {
  background: var(--background);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-md);
  box-shadow: 0 4px 12px rgba(0,0,0,0.15);
  color: var(--text-color);
  font-family: var(--font-family);
  font-size: var(--font-size-base);
}

.floatype-item {
  padding: var(--space-2) var(--space-3);
  border-bottom: 1px solid var(--border-color-light);
}

.floatype-item:last-child {
  border-bottom: none;
}

.floatype-item:hover {
  background: var(--hover-background);
}

.floatype-sel {
  background: var(--primary);
  color: var(--primary-foreground);
}
```

## Real-World Example: Social Media Composer

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Social Post Composer</title>
  <link rel="stylesheet" href="oat.min.css">
  
  <style>
    .composer {
      max-width: 600px;
      margin: 50px auto;
      padding: 20px;
    }
    
    .composer textarea {
      width: 100%;
      height: 150px;
      resize: vertical;
    }
    
    .floatype {
      position: absolute;
      background: var(--background);
      border: 1px solid var(--border-color);
      border-radius: var(--radius-md);
      box-shadow: 0 4px 16px rgba(0,0,0,0.2);
      max-height: 250px;
      overflow-y: auto;
      z-index: 1000;
    }
    
    .floatype-item {
      padding: var(--space-2) var(--space-3);
      cursor: pointer;
      display: flex;
      align-items: center;
      gap: var(--space-2);
    }
    
    .floatype-item:hover,
    .floatype-sel {
      background: var(--primary);
      color: var(--primary-foreground);
    }
    
    .floatype-avatar {
      width: 32px;
      height: 32px;
      border-radius: 50%;
      background: var(--primary);
      display: flex;
      align-items: center;
      justify-content: center;
      color: var(--primary-foreground);
      font-weight: bold;
    }
  </style>
</head>
<body>
  <div class="composer">
    <h1>Compose Post</h1>
    <textarea 
      placeholder="Write something... Mention @friends or add #hashtags"
    ></textarea>
    <button type="button" class="primary">Post</button>
  </div>
  
  <script src="oat.min.js" defer></script>
  <script type="module">
    import { floatype } from 'https://unpkg.com/@knadh/floatype';
    
    // Mock user data
    const users = [
      { id: 1, name: 'john', avatar: 'JD' },
      { id: 2, name: 'jane', avatar: 'JS' },
      { id: 3, name: 'bob', avatar: 'BD' },
      { id: 4, name: 'alice', avatar: 'AL' },
      { id: 5, name: 'charlie', avatar: 'CH' }
    ];
    
    // Popular hashtags
    const hashtags = [
      'javascript', 'webdev', 'coding', 'programming',
      'frontend', 'backend', 'fullstack', 'react',
      'vue', 'angular', 'nodejs', 'python'
    ];
    
    const textarea = document.querySelector('textarea');
    
    floatype(textarea, {
      triggers: ['@', '#'],
      
      onQuery: async (query, trigger) => {
        if (trigger === '@') {
          // Filter users by name
          return users
            .filter(u => u.name.toLowerCase().startsWith(query.toLowerCase()))
            .slice(0, 5);
        } else if (trigger === '#') {
          // Filter hashtags
          return hashtags
            .filter(h => h.startsWith(query.toLowerCase()))
            .slice(0, 8)
            .map(h => '#' + h);
        }
      },
      
      itemFormatter: (item) => {
        if (typeof item === 'string') {
          // Hashtag
          return `<strong>${item}</strong>`;
        } else {
          // User mention with avatar
          return `
            <span class="floatype-avatar">${item.avatar}</span>
            <span>@${item.name}</span>
          `;
        }
      },
      
      onSelect: (item, textarea) => {
        if (typeof item === 'string') {
          // Insert hashtag
          insertAtCursor(textarea, item + ' ');
        } else {
          // Insert mention
          insertAtCursor(textarea, '@' + item.name + ' ');
        }
      }
    });
    
    function insertAtCursor(textarea, text) {
      const start = textarea.selectionStart;
      const end = textarea.selectionEnd;
      const value = textarea.value;
      
      textarea.value = value.substring(0, start) + text + value.substring(end);
      textarea.selectionStart = textarea.selectionEnd = start + text.length;
      textarea.focus();
    }
  </script>
</body>
</html>
```

## Options

```javascript
floatype(textarea, {
  // Required: Async function that returns suggestions
  onQuery: async (query, trigger) => {
    return ['suggestion1', 'suggestion2'];
  },
  
  // Optional: Characters that trigger suggestions (default: none, always active)
  triggers: ['@', '#'],
  
  // Optional: Custom formatter for display (default: use string as-is)
  itemFormatter: (item) => item,
  
  // Optional: Callback when item is selected
  onSelect: (item, textarea) => {
    // Default behavior inserts the item text
  },
  
  // Optional: Debounce delay in ms (default: 300)
  debounce: 300,
  
  // Optional: CSS class for the widget container
  className: 'floatype',
  
  // Optional: CSS class for selected item
  selClassName: 'floatype-sel'
});
```

## Methods

The floatype instance provides these methods:

```javascript
const ft = floatype(textarea, options);

// Unbind the widget (disable suggestions)
ft.unbind();

// Re-bind the widget (enable suggestions)
ft.bind();
```

## Browser Support

- Modern browsers with ES6 support
- Chrome, Firefox, Safari, Edge (latest versions)
- Requires fetch API for server-side search

## Tips and Best Practices

### DO

- Debounce server requests to avoid excessive API calls
- Limit results to 5-10 items for better UX
- Provide clear visual feedback for selected items
- Support keyboard navigation (arrow keys, enter, escape)
- Handle empty results gracefully

### DON'T

- Return too many suggestions (performance issue)
- Forget to handle async errors
- Use without proper CSS styling
- Expect it to work on `<input>` elements (use autocomp.js instead)

## Limitations

- Works only with `<textarea>` elements
- For `<input>` autocomplete, use [autocomp.js](https://github.com/knadh/autocomp.js)
- No built-in caching (implement in onQuery if needed)
- Positioning may need adjustment for fixed/absolute parent containers

## Related Libraries

- **autocomp.js**: Dropdown autocomplete for input fields
- **highlighted-input.js**: Keyword highlighting in inputs
- **tinyrouter.js**: Client-side routing

Licensed under the MIT License.
