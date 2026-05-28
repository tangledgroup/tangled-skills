# Building htmx Extensions

How to create custom htmx extensions using the extension API.

## Defining an Extension

```javascript
htmx.defineExtension('my-ext', {
  init: function(api) {
    // Called once when extension is registered
    // Store api reference for later use
  },

  getSelectors: function() {
    // Return object mapping attribute names to CSS selectors
    // Used for efficient element discovery
    return {
      'my-attr': '[my-attr]'
    };
  },

  onEvent: function(name, evt) {
    // Handle htmx events
    // Return true to continue processing, false to stop
    console.log('Event:', name, evt);
    return true;
  },

  transformResponse: function(text, xhr, elt) {
    // Modify response text before parsing
    return text.replace(/old/g, 'new');
  },

  isInlineSwap: function(swapStyle) {
    // Return true if swapStyle is handled by this extension
    return swapStyle === 'my-swap';
  },

  handleSwap: function(swapStyle, target, fragment, settleInfo) {
    // Custom swap logic
    // Return true if swap was handled
    if (swapStyle === 'my-swap') {
      target.textContent = fragment.textContent;
      return true;
    }
    return false;
  },

  encodeParameters: function(xhr, parameters, elt) {
    // Custom parameter encoding
    // Return encoded string or null to use default
    return null;
  }
});
```

## Extension Lifecycle

1. **Registration**: `htmx.defineExtension()` called — `init()` fires
2. **Element Discovery**: `getSelectors()` tells htmx which attributes to watch
3. **Event Handling**: `onEvent()` receives all htmx events (beforeRequest, afterSwap, etc.)
4. **Request Phase**: `encodeParameters()` can modify request body
5. **Response Phase**: `transformResponse()` can modify response text
6. **Swap Phase**: `isInlineSwap()` + `handleSwap()` for custom swap strategies

## Extension Points Reference

### `init(api)`

Called once when extension is defined. The `api` object provides access to htmx internals:

```javascript
init: function(api) {
  this.api = api;
  // Access internal helpers
  api.triggerEvent(elt, 'my:event');
}
```

### `getSelectors()`

Returns attribute-to-selector mapping for efficient DOM scanning:

```javascript
getSelectors: function() {
  return {
    'ws-connect': '[ws-connect]',
    'ws-send': '[ws-send]'
  };
}
```

### `onEvent(name, evt)`

Receive all htmx events. Return `true` to continue event propagation:

```javascript
onEvent: function(name, evt) {
  if (name === 'htmx:beforeRequest') {
    // Add custom header
    evt.detail.headers['X-My-Ext'] = 'value';
  }
  return true;
}
```

### `transformResponse(text, xhr, elt)`

Modify response before DOM parsing:

```javascript
transformResponse: function(text, xhr, elt) {
  // Strip HTML comments
  return text.replace(/<!--[\s\S]*?-->/g, '');
}
```

### `isInlineSwap(swapStyle)` / `handleSwap(swapStyle, target, fragment, settleInfo)`

Implement custom swap strategies:

```javascript
isInlineSwap: function(swapStyle) {
  return swapStyle.startsWith('fade-');
},

handleSwap: function(swapStyle, target, fragment, settleInfo) {
  if (swapStyle === 'fade-innerHTML') {
    target.style.opacity = '0';
    setTimeout(function() {
      target.innerHTML = fragment.innerHTML;
      target.style.opacity = '1';
    }, 300);
    return true;
  }
  return false;
}
```

## Naming Conventions

- Extension names: dash-separated, short and descriptive (`my-extension`)
- Attribute names: use extension name as prefix or unique namespace
- Avoid `hx-` prefix (reserved for core attributes)

## Publishing

1. Publish to npm: `npm publish`
2. Host on CDN (jsDelivr, unpkg)
3. Add to [htmx-extensions](https://github.com/bigskysoftware/htmx-extensions) repo for community visibility
4. Document installation via CDN, download, and npm

## Example: Simple Logging Extension

```javascript
htmx.defineExtension('request-logger', {
  onEvent: function(name, evt) {
    if (name.startsWith('htmx:')) {
      console.log(`[${name}]`, {
        element: evt.detail.elt?.tagName,
        path: evt.detail.path,
        timestamp: new Date().toISOString()
      });
    }
    return true;
  }
});
```

## Example: Custom Swap Strategy

```javascript
htmx.defineExtension('slide-swap', {
  isInlineSwap: function(swapStyle) {
    return swapStyle === 'slide';
  },

  handleSwap: function(swapStyle, target, fragment) {
    const newContent = document.createElement('div');
    newContent.innerHTML = fragment.innerHTML;
    newContent.style.opacity = '0';
    newContent.style.transform = 'translateY(-10px)';

    target.parentNode.insertBefore(newContent, target.nextSibling);

    // Animate in
    requestAnimationFrame(function() {
      newContent.style.transition = 'all 300ms ease';
      newContent.style.opacity = '1';
      newContent.style.transform = 'translateY(0)';
    });

    // Remove old after animation
    setTimeout(function() {
      target.remove();
    }, 300);

    return true;
  }
});
```
