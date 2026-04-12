# Highlighted-Input.js - Keyword Highlighting

A super tiny (~450 bytes), zero-dependency JavaScript library that highlights specific keywords and tags in an `<input>` field.

## Overview

Highlight specific text patterns within input fields, useful for tagging inputs, command interfaces, or syntax highlighting.

## Installation

### CDN
```html
<script src="https://unpkg.com/highlighted-input.js"></script>
```

### Download
```bash
wget https://raw.githubusercontent.com/knadh/highlighted-input.js/master/dist/highlighted-input.min.js
```

## Basic Usage

### Highlight Keywords

```html
<input type="text" placeholder="Type @username or #tag..." />

<script src="highlighted-input.min.js"></script>
<script>
const input = new HighlightedInput(document.querySelector('input'), {
  highlights: ['@', '#']
});
</script>
```

Text starting with `@` or `#` will be automatically highlighted.

### Custom Highlight Styles

```javascript
const input = new HighlightedInput(element, {
  highlights: [
    { prefix: '@', className: 'highlight-mention' },
    { prefix: '#', className: 'highlight-tag' }
  ]
});
</script>

<style>
.highlight-mention {
  background-color: #e0f2fe;
  color: #0369a1;
  padding: 2px 4px;
  border-radius: 3px;
}

.highlight-tag {
  background-color: #fef3c7;
  color: #92400e;
  padding: 2px 4px;
  border-radius: 3px;
}
</style>
```

### Highlight Specific Words

```javascript
const input = new HighlightedInput(element, {
  highlights: [
    { words: ['help', 'exit', 'quit'], className: 'command' },
    { prefix: '/', className: 'slash-command' }
  ]
});
```

## Options

```javascript
new HighlightedInput(element, {
  // Array of highlight patterns
  highlights: [
    { prefix: '@' },           // Highlight text starting with @
    { prefix: '#' },           // Highlight text starting with #
    { words: ['foo', 'bar'] }, // Highlight exact words
    { regex: /\d+/g }          // Highlight numbers
  ],
  
  // Default class name if not specified per pattern
  className: 'highlight',
  
  // Debounce delay in ms
  debounce: 150
});
```

## Real-world Example: Tagging Input

```html
<input 
  type="text" 
  placeholder="Mention someone with @name or add a #tag..."
  style="font-family: monospace; padding: 8px; font-size: 14px;"
/>

<script src="highlighted-input.min.js"></script>
<script>
const tagInput = new HighlightedInput(document.querySelector('input'), {
  highlights: [
    { 
      prefix: '@', 
      className: 'mention' 
    },
    { 
      prefix: '#', 
      className: 'tag' 
    }
  ]
});
</script>

<style>
.mention {
  background: linear-gradient(180deg, #bfdbfe 0%, #dbeafe 100%);
  color: #1e40af;
  padding: 1px 3px;
  border-radius: 3px;
  font-weight: 500;
}

.tag {
  background: linear-gradient(180deg, #fde68a 0%, #fef3c7 100%);
  color: #854d0e;
  padding: 1px 3px;
  border-radius: 3px;
  font-weight: 500;
}
</style>
```

## Example: Command Interface

```html
<input 
  type="text" 
  placeholder="Type a command..."
  style="font-family: monospace; background: #1e1e1e; color: #d4d4d4;"
/>

<script>
const commandInput = new HighlightedInput(document.querySelector('input'), {
  highlights: [
    { 
      words: ['help', 'exit', 'clear', 'ls', 'cd'], 
      className: 'command' 
    },
    { 
      prefix: '-', 
      className: 'flag' 
    },
    { 
      prefix: '--', 
      className: 'long-flag' 
    }
  ]
});
</script>

<style>
.command {
  color: #569cd6;
  font-weight: bold;
}

.flag {
  color: #4ec9b0;
}

.long-flag {
  color: #4ec9b0;
  font-style: italic;
}
</style>
```

## Integration with Oat UI

```html
<label data-field>
  Search
  <input 
    type="text" 
    placeholder="Search @user #tag..."
    style="width: 100%;"
  />
</label>

<script src="oat.min.js" defer></script>
<script src="highlighted-input.min.js" defer></script>
<script>
const searchInput = new HighlightedInput(
  document.querySelector('label[data-field] input'),
  {
    highlights: [
      { prefix: '@', className: 'oat-mention' },
      { prefix: '#', className: 'oat-tag' }
    ]
  }
);
</script>

<style>
.oat-mention {
  background-color: var(--primary);
  color: var(--primary-foreground);
  padding: 2px 6px;
  border-radius: var(--radius-sm);
  font-weight: 500;
}

.oat-tag {
  background-color: var(--secondary);
  color: var(--secondary-foreground);
  padding: 2px 6px;
  border-radius: var(--radius-sm);
  font-weight: 500;
}
</style>
```

## Advanced Patterns

### Highlight with Autocomplete Trigger

```javascript
const input = new HighlightedInput(element, {
  highlights: [{ prefix: '@' }],
  onHighlight: (match) => {
    // Show autocomplete when @ is typed
    showUserAutocomplete(match.start, match.end);
  }
});
```

### Multiple Inputs

```javascript
document.querySelectorAll('.tag-input').forEach(input => {
  new HighlightedInput(input, {
    highlights: ['@', '#']
  });
});
```

## Browser Support

- Modern browsers (Chrome, Firefox, Safari, Edge)
- Requires CSS pseudo-element support
- Graceful degradation (input works without JS)

## Limitations

- Works best with single-line inputs
- May not work perfectly with very long text
- Highlighting is visual only (doesn't affect submitted value)

Perfect for adding syntax highlighting to tagging inputs, command interfaces, or any text input where you want to visually distinguish patterns!
