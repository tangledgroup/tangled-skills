# htmx Swapping and DOM Updates

This reference covers all swap modes, options, and DOM manipulation techniques in htmx 2.x.

## Swap Styles

Swap styles control how response content is inserted into the DOM.

### innerHTML (Default)

Replace the innerHTML of the target element:

```html
<!-- Target element keeps its attributes -->
<div id="content" class="container">Loading...</div>

<!-- Response HTML -->
<h1>New Title</h1>
<p>New content</p>

<!-- Result -->
<div id="content" class="container">
    <h1>New Title</h1>
    <p>New content</p>
</div>
```

**Use case:** Updating content within a container while preserving attributes.

### outerHTML

Replace the entire target element:

```html
<!-- Original element -->
<div id="card" class="card">
    <h3>Old Title</h3>
</div>

<!-- Response HTML -->
<div id="card" class="card updated">
    <h3>New Title</h3>
    <p>Additional content</p>
</div>

<!-- Result: entire element replaced -->
<div id="card" class="card updated">
    <h3>New Title</h3>
    <p>Additional content</p>
</div>
```

**Use case:** Replacing entire elements with new markup.

### afterbegin

Insert content at the beginning of the target:

```html
<!-- Target -->
<ul id="list">
    <li>Existing item</li>
</ul>

<!-- Response -->
<li>New first item</li>

<!-- Result -->
<ul id="list">
    <li>New first item</li>
    <li>Existing item</li>
</ul>
```

**Use case:** Prepending items to lists.

### beforeend

Insert content at the end of the target (append):

```html
<!-- Target -->
<ul id="list">
    <li>Existing item</li>
</ul>

<!-- Response -->
<li>New last item</li>

<!-- Result -->
<ul id="list">
    <li>Existing item</li>
    <li>New last item</li>
</ul>
```

**Use case:** Appending new items to lists, infinite scroll.

### beforebegin

Insert content before the target element:

```html
<!-- Target -->
<div id="main">Main content</div>

<!-- Response -->
<aside id="sidebar">Sidebar</aside>

<!-- Result -->
<aside id="sidebar">Sidebar</aside>
<div id="main">Main content</div>
```

**Use case:** Inserting elements before the target (e.g., sidebar before main).

### afterend

Insert content after the target element:

```html
<!-- Target -->
<div id="main">Main content</div>

<!-- Response -->
<footer>Footer</footer>

<!-- Result -->
<div id="main">Main content</div>
<footer>Footer</footer>
```

**Use case:** Inserting elements after the target (e.g., footer, related content).

### delete

Delete the target element regardless of response:

```html
<!-- Temporary element -->
<div id="temp-message" hx-get="/process" hx-swap="delete">
    Processing...
</div>

<!-- Result: element is deleted after request completes -->
<!-- (element no longer exists in DOM) -->
```

**Use case:** Removing loading indicators, temporary messages.

### none

Don't swap content (use with OOB swaps only):

```html
<!-- Request triggers OOB swaps only -->
<button hx-post="/update-status" 
        hx-swap="none">
    Update Status
</button>

<!-- Server response contains only OOB elements -->
<div id="status" hx-swap-oob="true">Updated!</div>
<div id="counter" hx-swap-oob="true">5</div>
```

**Use case:** Triggering updates elsewhere without changing the request element.

## Swap Modifiers

### swap:Xms

Delay before swapping content:

```html
<!-- Wait 300ms before swapping -->
<div hx-get="/content" 
     hx-swap="innerHTML swap:300ms">
    Loading...
</div>

<!-- Use for smooth transitions -->
<div hx-get="/modal" 
     hx-swap="innerHTML swap:100ms">
    Open Modal
</div>
```

**Use case:** Creating pause before content change for animations.

### settle:Xms

Delay after swapping before settling attributes:

```html
<!-- Wait 500ms after swap before settling -->
<div hx-get="/content" 
     hx-swap="innerHTML settle:500ms">
    Load Content
</div>
```

**Use case:** Allowing animations to complete before attribute settlement.

### scroll:top|bottom

Scroll target to top or bottom after swap:

```html
<!-- Scroll to top of new content -->
<div hx-get="/long-article" 
     hx-target="#article"
     hx-swap="innerHTML scroll:top">
    Read Article
</div>

<!-- Scroll chat to bottom -->
<button hx-post="/send-message" 
        hx-swap="beforeend scroll:bottom">
    Send
</button>
```

### show:top|bottom

Show target's top or bottom in viewport:

```html
<!-- Show top of modal in viewport -->
<button hx-get="/modal-content" 
        hx-target="#modal"
        hx-swap="innerHTML show:top">
    Open Modal
</button>

<!-- Show bottom of new content -->
<div hx-get="/notifications" 
     hx-swap="beforeend show:bottom">
    New Notification
</div>
```

### focusScroll:true|false

Control whether focused element scrolls into view:

```html
<!-- Don't scroll focused element into view -->
<div hx-get="/content" 
     hx-swap="innerHTML focusScroll:false">
    Load
</div>

<!-- Default behavior (can be configured globally) -->
<div hx-get="/content" 
     hx-swap="innerHTML focusScroll:true">
    Load
</div>
```

### transition:true|false

Use View Transitions API for animated swap:

```html
<!-- Enable view transition for this swap -->
<button hx-get="/view-mode" 
        hx-swap="innerHTML transition:true">
    Toggle View
</button>

<!-- Global configuration -->
<script>
    htmx.config.globalViewTransitions = true;
</script>
```

**Browser support:** Chrome 116+, Edge 116+, Opera 102+

## Morph Swaps

Morphing swaps merge new content into existing DOM, preserving state.

### Idiomorph Extension

```html
<!-- Load idiomorph extension -->
<script src="https://unpkg.com/htmx.org/dist/ext/idiomorph.js"></script>

<!-- Use morph swap -->
<div hx-ext="idiomorph"
     hx-get="/content"
     hx-swap="morph">
    Existing content
</div>
```

**Benefits:**
- Preserves focus on input elements
- Maintains video/audio playback state
- Keeps third-party widget state
- Smooth transitions between similar content

### Morphdom Extension

```html
<!-- Load morphdom extension -->
<script src="https://unpkg.com/htmx.org@1.9.10/dist/ext/morphdom-swap.js"></script>

<!-- Use morphdom swap -->
<div hx-ext="morphdom-swap"
     hx-get="/content"
     hx-swap="morphdom">
    Content
</div>
```

### Alpine Morph Extension

For Alpine.js integration:

```html
<!-- Load alpine-morph extension -->
<script src="https://unpkg.com/htmx.org/dist/ext/alpine-morph.js"></script>

<!-- Use with Alpine.js -->
<div hx-ext="alpine-morph"
     hx-get="/content"
     hx-swap="alpine-morph"
     x-data="{ loaded: false }">
    Content
</div>
```

## View Transitions

htmx integrates with the View Transitions API for animated page transitions.

### Basic Usage

```html
<!-- Enable for specific element -->
<button hx-get="/toggle-theme" 
        hx-swap="outerHTML transition:true">
    Toggle Theme
</button>

<!-- Enable globally -->
<script>
    htmx.config.globalViewTransitions = true;
</script>
```

### CSS Customization

```css
/* Define transition animations */
::view-transition-old(root) {
    animation: fade-out 0.3s ease-out;
}

::view-transition-new(root) {
    animation: fade-in 0.3s ease-in;
}

@keyframes fade-out {
    from { opacity: 1; }
    to { opacity: 0; }
}

@keyframes fade-in {
    from { opacity: 0; }
    to { opacity: 1; }
}

/* Name specific elements for targeted transitions */
::view-transition-old(image) {
    animation: slide-out 0.3s;
}

::view-transition-new(image) {
    animation: slide-in 0.3s;
}
```

### JavaScript Control

```javascript
// Cancel transition if needed
document.body.addEventListener('htmx:beforeTransition', (event) => {
    if (shouldSkipTransition()) {
        event.preventDefault();
    }
});

// Custom transition logic
document.body.addEventListener('htmx:beforeTransition', (event) => {
    document.startViewTransition(() => {
        // Transition will happen here
    });
});
```

## Response Selection

### hx-select

Select specific content from response:

```html
<!-- Extract only the article content -->
<button hx-get="/article-page" 
        hx-select="#article-content"
        hx-target="#main">
    Load Article
</button>

<!-- Server returns full page -->
<!--
<!DOCTYPE html>
<html>
<head><title>Article</title></head>
<body>
    <nav>Navigation</nav>
    <div id="article-content">
        <h1>Article Title</h1>
        <p>Article body...</p>
    </div>
    <footer>Footer</footer>
</body>
</html>
-->
<!-- Only #article-content is swapped into #main -->

<!-- Select multiple elements -->
<button hx-get="/items" 
        hx-select=".item-card"
        hx-target="#item-list">
    Load Items
</button>
```

### hx-select-oob

Select elements for out-of-band swaps:

```html
<!-- Trigger element -->
<button hx-post="/submit-form" 
        hx-select-oob="#flash-message, #form-counter">
    Submit
</button>

<!-- Server response -->
<div id="flash-message" class="success">Form submitted!</div>
<div id="form-counter">Submissions: 5</div>
<div>Main response (swapped into target)</div>
```

See [Out-of-Band Swaps](05-oob-swaps.md) for comprehensive OOB documentation.

## Head Tag Handling

htmx automatically processes `<title>` and `<head>` tags in responses.

### Title Updates

```html
<!-- Response includes title -->
<!--
<title>New Page Title</title>
<div>New content</div>
-->
<!-- Document title is automatically updated to "New Page Title" -->
```

### Ignore Title

Prevent title updates:

```html
<button hx-post="/update" 
        hx-swap="innerHTML ignoreTitle:true">
    Update (don't change title)
</button>
```

### Head Merge Extension

For advanced head tag handling:

```html
<!-- Load head-support extension -->
<script src="https://unpkg.com/htmx.org/dist/ext/head.js"></script>

<!-- Merge head tags -->
<div hx-ext="head"
     hx-get="/content"
     hx-swap="innerHTML head:merge">
    Content
</div>
```

**Head swap modes:**
- `merge` - Merge new head tags with existing
- `append` - Append new head tags
- `false` - Don't process head tags

## Settle Operations

After swapping, htmx "settles" attributes on the new content.

### Attributes Settled

By default, these attributes are settled:

- `class`
- `style`
- `width`
- `height`

```javascript
// Customize settled attributes
htmx.config.attributesToSettle = [
    'class', 'style', 'width', 'height', 'data-custom'
];
```

### Settle Delay

Control timing of attribute settlement:

```html
<!-- Default 20ms settle delay -->
<div hx-get="/content">Content</div>

<!-- Custom settle delay -->
<div hx-get="/content" 
     hx-swap="innerHTML settle:500ms">
    Content
</div>

<!-- Global configuration -->
<script>
    htmx.config.defaultSettleDelay = 100;
</script>
```

## Advanced Swap Patterns

### Conditional Swapping

```javascript
// Modify swap based on response
document.body.addEventListener('htmx:beforeSwap', (event) => {
    if (event.detail.serverResponse.includes('<error>')) {
        event.detail.swapOverride = 'none';
        showErrorMessage(event.detail.serverResponse);
    }
});
```

### Progressive Enhancement

```html
<!-- Fallback content shown while loading -->
<div hx-get="/content" 
     hx-swap="innerHTML swap:100ms">
    <div class="skeleton-loader">
        <!-- Skeleton UI shown during load -->
        <div class="skeleton-title"></div>
        <div class="skeleton-text"></div>
    </div>
</div>
```

### Animation Integration

```html
<!-- Fade in new content -->
<div hx-get="/content" 
     hx-swap="innerHTML swap:0ms"
     class="fade-container">
    Loading...
</div>

<style>
.htmx-added {
    opacity: 0;
    transition: opacity 0.3s ease-in;
}

.htmx-settling .htmx-added {
    opacity: 1;
}
</style>
```

### Preserve Element State

```html
<!-- Use morph swap to preserve state -->
<div hx-ext="idiomorph"
     hx-get="/content"
     hx-swap="morph">
    
    <!-- Input focus preserved -->
    <input name="data" value="existing">
    
    <!-- Video state preserved -->
    <video src="movie.mp4" controls></video>
</div>
```

## Swap Performance

### Minimize Repaints

```html
<!-- Use innerHTML for minimal DOM manipulation -->
<div hx-get="/content" 
     hx-swap="innerHTML">
    Fast swap
</div>

<!-- outerHTML causes more reflows -->
<div hx-get="/content" 
     hx-swap="outerHTML">
    Slower swap
</div>
```

### Batch Updates

```html
<!-- Use OOB swaps for multiple updates -->
<button hx-post="/update-all">
    Update Multiple Sections
</button>

<!-- Server returns -->
<div id="header" hx-swap-oob="true">New header</div>
<div id="content" hx-swap-oob="true">New content</div>
<div id="footer" hx-swap-oob="true">New footer</div>
```

### Lazy Loading

```html
<!-- Load content only when visible -->
<div hx-get="/heavy-content" 
     hx-trigger="revealed"
     hx-swap="outerHTML">
    <img src="thumbnail.jpg" alt="Preview">
</div>
```

## Troubleshooting

### Content Not Swapping

**Check:**
1. Response is valid HTML
2. Target element exists in DOM
3. No JavaScript errors in console
4. `hx-select` matches response content

```javascript
// Debug swap
document.body.addEventListener('htmx:beforeSwap', (event) => {
    console.log('Swapping:', {
        target: event.detail.target,
        response: event.detail.serverResponse.substring(0, 100),
        swapStyle: event.detail.requestConfig.swapSpec.swapStyle
    });
});
```

### Infinite Loops

**Prevent triggering on swapped content:**

```html
<!-- Use 'once' modifier -->
<div hx-get="/load-more" 
     hx-trigger="click once">
    Load More
</div>

<!-- Or use OOB swaps -->
<button hx-post="/add-item" 
        hx-swap="none">
    Add Item (OOB updates list)
</button>
```

### Focus Loss

**Preserve focus with morph swaps:**

```html
<!-- Use idiomorph to preserve focus -->
<div hx-ext="idiomorph"
     hx-get="/content"
     hx-swap="morph">
    <input name="search" autofocus>
</div>
```

## Next Steps

- [Out-of-Band Swaps](05-oob-swaps.md) - OOB swap patterns and techniques
- [Common Patterns](10-common-patterns.md) - Real-world swap examples
- [Extensions](07-extensions.md) - Morph extensions and custom swaps
