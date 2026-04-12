# Floatype.js - Floating Autocomplete

A tiny (~1200 bytes), zero-dependency floating autocomplete/autosuggestion widget for textareas.

## Overview

Add intelligent autocomplete suggestions that float above textarea content, perfect for documentation editors, markdown writers, or any rich text input.

## Installation

### CDN
```html
<script src="https://unpkg.com/floatype.js"></script>
```

### Download
```bash
wget https://raw.githubusercontent.com/knadh/floatype.js/master/dist/floatype.min.js
```

## Basic Usage

```html
<textarea placeholder="Type *bold* or _italic_..." rows="10" style="width: 100%;"></textarea>

<script src="floatype.min.js"></script>
<script>
const textarea = document.querySelector('textarea');
const ft = new Floatype(textarea, {
  triggers: ['*', '_', '~'],
  suggestions: {
    '*': ['**bold**', '*italic*'],
    '_': ['**bold**', '_italic_'],
    '~': ['~~strikethrough~~']
  }
});
</script>
```

## Advanced Configuration

### Custom Suggestions

```javascript
const ft = new Floatype(textarea, {
  triggers: ['/', '@', '#'],
  
  suggestions: {
    '/': [
      { text: '/bold', label: 'Bold text' },
      { text: '/italic', label: 'Italic text' },
      { text: '/heading', label: 'Heading' }
    ],
    
    '@': [
      { text: '@john', label: 'John Doe' },
      { text: '@jane', label: 'Jane Smith' }
    ],
    
    '#': [
      { text: '#todo', label: 'Todo tag' },
      { text: '#done', label: 'Done tag' }
    ]
  }
});
```

### Async Suggestions (API Fetch)

```javascript
const ft = new Floatype(textarea, {
  triggers: ['@'],
  
  suggestions: {
    '@': async (query) => {
      // Fetch from API based on query
      const response = await fetch(`/api/users?q=${query}`);
      const users = await response.json();
      
      return users.map(user => ({
        text: `@${user.username}`,
        label: user.name
      }));
    }
  }
});
```

### Custom Trigger Characters

```javascript
const ft = new Floatype(textarea, {
  triggers: ['!', '$', '%'],
  
  suggestions: {
    '!': ['!NOTE', '!WARNING', '!TIP'],
    '$': ['$variable', '$env'],
    '%': ['%highlight%', '%code%']
  }
});
```

## Options

```javascript
new Floatype(textarea, {
  // Characters that trigger suggestions
  triggers: ['*', '_', '/'],
  
  // Suggestions per trigger
  suggestions: {
    '*': ['**bold**', '*italic*'],
    '_': ['__bold__', '_italic_']
  },
  
  // Maximum suggestions to show
  maxSuggestions: 10,
  
  // Minimum characters before showing suggestions
  minLength: 0,
  
  // Custom CSS class for suggestion container
  className: 'floatype-suggestions',
  
  // Callback when suggestion is selected
  onSelect: (suggestion, trigger) => {
    console.log('Selected:', suggestion);
  },
  
  // Callback when suggestion popup opens
  onOpen: (trigger, query) => {
    console.log('Opened for:', trigger);
  },
  
  // Callback when suggestion popup closes
  onClose: () => {
    console.log('Closed');
  }
});
```

## Markdown Editor Example

```html
<textarea 
  id="markdown-editor" 
  placeholder="Write markdown..."
  rows="15"
  style="width: 100%; font-family: monospace; padding: 12px;"
></textarea>

<script src="floatype.min.js"></script>
<script>
const editor = document.getElementById('markdown-editor');
const ft = new Floatype(editor, {
  triggers: ['*', '_', '~', '`', '#', '-', '['],
  
  suggestions: {
    '*': [
      { text: '**bold**', label: 'Bold' },
      { text: '*italic*', label: 'Italic' }
    ],
    
    '_': [
      { text: '__bold__', label: 'Bold (alt)' },
      { text: '_italic_', label: 'Italic (alt)' }
    ],
    
    '~': [
      { text: '~~strikethrough~~', label: 'Strikethrough' }
    ],
    
    '`': [
      { text: '`code`', label: 'Inline code' },
      { text: '```javascript\n// code\n```', label: 'Code block' }
    ],
    
    '#': [
      { text: '# Heading 1', label: 'H1' },
      { text: '## Heading 2', label: 'H2' },
      { text: '### Heading 3', label: 'H3' }
    ],
    
    '-': [
      { text: '- Item', label: 'Bullet list' },
      { text: '1. Item', label: 'Numbered list' }
    ],
    
    '[': [
      { text: '[text](url)', label: 'Link' },
      { text: '![alt](url)', label: 'Image' }
    ]
  },
  
  onSelect: (suggestion) => {
    console.log('Inserted:', suggestion.text);
  }
});
</script>
```

## Documentation Example with Oat UI

```html
<article class="card">
  <header>
    <h3>Documentation Editor</h3>
    <p class="text-light">Type / for commands, @ to mention users</p>
  </header>
  
  <div style="margin-top: var(--space-4);">
    <textarea 
      id="doc-editor"
      placeholder="Start typing..."
      rows="12"
      style="width: 100%; border: 1px solid var(--input); border-radius: var(--radius-md); padding: var(--space-3); font-family: monospace;"
    ></textarea>
  </div>
  
  <footer class="hstack justify-end gap-2 mt-4">
    <button class="outline">Preview</button>
    <button>Save</button>
  </footer>
</article>

<script src="oat.min.js" defer></script>
<script src="floatype.min.js" defer></script>
<script>
const docEditor = new Floatype(document.getElementById('doc-editor'), {
  triggers: ['/', '@', '#'],
  
  suggestions: {
    '/': [
      { text: '/h1 Heading', label: 'Heading 1' },
      { text: '/h2 Heading', label: 'Heading 2' },
      { text: '/bold **text**', label: 'Bold' },
      { text: '/italic *text*', label: 'Italic' },
      { text: '/list - item', label: 'Bullet List' }
    ],
    
    '@': [
      { text: '@alice', label: 'Alice Johnson' },
      { text: '@bob', label: 'Bob Smith' },
      { text: '@carol', label: 'Carol White' }
    ],
    
    '#': [
      { text: '#todo', label: 'Todo' },
      { text: '#done', label: 'Done' },
      { text: '#wip', label: 'Work in Progress' }
    ]
  }
});
</script>

<style>
/* Custom suggestion styling */
.floatype-suggestions {
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: var(--radius-md);
  box-shadow: var(--shadow-lg);
  max-height: 300px;
  overflow-y: auto;
}

.floatype-suggestion {
  padding: var(--space-2) var(--space-3);
  cursor: pointer;
}

.floatype-suggestion:hover,
.floatype-suggestion.active {
  background: var(--primary);
  color: var(--primary-foreground);
}
</style>
```

## Code Editor Example

```javascript
const codeEditor = new Floatype(textarea, {
  triggers: ['import', 'function', 'const', 'let', 'var'],
  
  suggestions: {
    'import': [
      { text: "import { something } from 'package'", label: 'Import statement' },
      { text: "import pkg from 'package'", label: 'Default import' }
    ],
    
    'function': [
      { text: 'function name() { }\n', label: 'Function declaration' },
      { text: 'const name = () => { }\n', label: 'Arrow function' }
    ],
    
    'const': [
      { text: 'const name = value\n', label: 'Const declaration' },
      { text: "const { a, b } = obj\n", label: 'Destructuring' }
    ]
  }
});
```

## Custom Styling

```css
.floatype-suggestions {
  position: absolute;
  z-index: 1000;
  background: white;
  border: 1px solid #ddd;
  border-radius: 4px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.15);
  max-height: 300px;
  overflow-y: auto;
  min-width: 200px;
}

.floatype-suggestion {
  padding: 8px 12px;
  cursor: pointer;
  border-bottom: 1px solid #eee;
}

.floatype-suggestion:last-child {
  border-bottom: none;
}

.floatype-suggestion:hover,
.floatype-suggestion.active {
  background: #f0f0f0;
}

.floatype-suggestion-label {
  font-weight: 500;
  color: #333;
}

.floatype-suggestion-text {
  font-size: 12px;
  color: #666;
  margin-top: 2px;
}
```

## Keyboard Navigation

Built-in support for:
- **Arrow Up/Down**: Navigate suggestions
- **Enter**: Select suggestion
- **Escape**: Close popup
- **Tab**: Select and insert

## Browser Support

- Chrome, Firefox, Safari, Edge (modern versions)
- Requires textarea support
- Graceful degradation (textarea works without JS)

## Tips

1. Use descriptive labels for better UX
2. Limit suggestions to 5-10 items max
3. Consider async loading for large suggestion sets
4. Style suggestions to match your app theme
5. Add keyboard shortcuts documentation

Perfect for markdown editors, documentation tools, code editors, or any textarea where contextual suggestions improve the writing experience!
