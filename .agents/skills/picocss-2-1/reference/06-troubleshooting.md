# Troubleshooting

Common issues and solutions when working with Pico CSS.

## Elements Not Styling Correctly

### Issue: HTML elements don't have Pico styles

**Cause:** Pico CSS not loaded or loaded after custom styles.

**Solution:** Ensure Pico is in the `<head>` before other stylesheets:

```html
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <link rel="stylesheet" href="css/pico.min.css">
  <link rel="stylesheet" href="custom.css"> <!-- After Pico -->
</head>
```

### Issue: Using wrong HTML elements

**Cause:** Pico styles semantic HTML elements. Using `<div>` instead of proper elements won't work.

**Solution:** Use semantic HTML:

```html
<!-- Wrong -->
<div class="button">Click me</div>

<!-- Correct -->
<button type="button">Click me</button>
```

## Dark Mode Not Working

### Issue: Dark mode doesn't activate automatically

**Cause:** Missing color-scheme meta tag.

**Solution:** Add the meta tag to `<head>`:

```html
<meta name="color-scheme" content="light dark">
```

### Issue: Custom colors not working in dark mode

**Cause:** Only defining colors for light mode.

**Solution:** Define colors for both modes:

```css
/* Light mode */
[data-theme="light"],
:root:not([data-theme="dark"]) {
  --pico-primary: #0172ad;
}

/* Dark mode (auto) */
@media only screen and (prefers-color-scheme: dark) {
  :root:not([data-theme]) {
    --pico-primary: #01b9f9;
  }
}

/* Dark mode (forced) */
[data-theme="dark"] {
  --pico-primary: #01b9f9;
}
```

## Custom Styles Not Applying

### Issue: Custom CSS not overriding Pico styles

**Cause:** CSS specificity or cascade order.

**Solution:** Pico uses low-specificity selectors, so your styles should override naturally. Ensure your CSS loads after Pico:

```html
<link rel="stylesheet" href="css/pico.min.css">
<style>
  /* Your custom styles */
  h1 { color: #bd3c13; }
</style>
```

### Issue: Need to override specific Pico behavior

**Solution:** Use CSS variables instead of overriding selectors:

```css
/* Instead of this */
button {
  border-radius: 2rem !important;
}

/* Do this */
:root {
  --pico-border-radius: 2rem;
}
```

## Form Issues

### Issue: Form inputs not full width

**Cause:** Inputs inside non-block containers.

**Solution:** Ensure inputs are in block-level containers or set width explicitly:

```html
<form>
  <label>
    Email
    <input type="email" style="width: 100%">
  </label>
</form>
```

### Issue: Form validation not showing

**Cause:** Browser support for `:invalid` pseudo-class.

**Solution:** Pico uses `:invalid` for styling. Most modern browsers support it. For older browsers, add JavaScript validation.

## Grid Layout Issues

### Issue: Grid items not aligning properly

**Cause:** Unequal content heights or nested grids.

**Solution:** Use consistent content structure in grid items:

```html
<div class="grid">
  <article>
    <header><h3>Title</h3></header>
    <section class="content"><p>Content</p></section>
    <footer><a href="#">Link</a></footer>
  </article>
  
  <article>
    <header><h3>Title</h3></header>
    <section class="content"><p>Content</p></section>
    <footer><a href="#">Link</a></footer>
  </article>
</div>
```

### Issue: Grid not responsive on mobile

**Cause:** Grid should be responsive by default. Check for conflicting CSS.

**Solution:** Remove any custom `display` or `flex` properties that might override grid behavior.

## Typography Issues

### Issue: Font sizes not scaling

**Cause:** Fixed font-size on html/body elements.

**Solution:** Use percentage or remove fixed sizing:

```css
/* Wrong */
html { font-size: 16px; }

/* Correct */
html { font-size: 100%; }
```

### Issue: Custom fonts not loading

**Cause:** Font not loaded before Pico applies styles.

**Solution:** Preload fonts or use font-display:

```css
@import url('https://fonts.googleapis.com/css2?family=Inter&display=swap');

:root {
  --pico-font-family: "Inter", system-ui, sans-serif;
}
```

## Container Issues

### Issue: Content not centered

**Cause:** Missing `.container` class or using class-less version incorrectly.

**Solution:** Add container class:

```html
<main class="container">
  <h1>Centered Content</h1>
</main>
```

Or use semantic landmarks in class-less version:

```html
<link rel="stylesheet" href="css/pico.classless.min.css">

<body>
  <main> <!-- Automatically centered in class-less version -->
    <h1>Centered Content</h1>
  </main>
</body>
```

## Component Issues

### Issue: Modal not closing

**Cause:** Missing close handler.

**Solution:** Add proper close functionality:

```html
<dialog id="modal">
  <form method="dialog">
    <button type="submit">Close</button>
  </form>
</dialog>
```

Or use JavaScript:

```html
<button onclick="document.getElementById('modal').close()">
  Close
</button>
```

### Issue: Accordion not collapsing others

**Cause:** `<details>` elements work independently by default.

**Solution:** Add JavaScript for accordion behavior:

```javascript
document.querySelectorAll('details').forEach(detail => {
  detail.addEventListener('toggle', event => {
    if (detail.open) {
      document.querySelectorAll('details').forEach(other => {
        if (other !== detail) other.open = false;
      });
    }
  });
});
```

## Performance Issues

### Issue: Page loading slowly

**Cause:** Large custom CSS or multiple stylesheets.

**Solution:** 
- Use CDN for Pico (cached by browsers)
- Minimize custom CSS
- Use CSS variables instead of recompiling

```html
<!-- Use CDN with version pinning -->
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/@picocss/pico@2/css/pico.min.css">
```

## Browser Compatibility Issues

### Issue: Features not working in older browsers

**Cause:** Pico uses modern CSS features.

**Solution:** Check browser support and provide fallbacks:

- **CSS Custom Properties**: IE11 doesn't support (use postcss-custom-properties)
- **<dialog> element**: Use modal-polyfill for older browsers
- **<details>/<summary>**: Generally well-supported
- **prefers-color-scheme**: Add media query fallbacks

### Issue: Flexbox/Grid not working in IE

**Cause:** Pico requires modern browser support.

**Solution:** Pico v2 targets modern browsers (Chrome, Firefox, Safari, Edge). For IE11 support, consider Pico v1 or add polyfills.

## Debugging Tips

### Inspect CSS Variables

Use browser dev tools to check variable values:

```css
/* Add this temporarily to debug */
* {
  outline: 1px solid red; /* Shows box model */
}
```

### Check Theme Activation

Verify current theme in dev tools:

```javascript
// Check current theme
console.log(document.documentElement.getAttribute('data-theme'));
console.log(window.matchMedia('(prefers-color-scheme: dark)').matches);
```

### Verify Pico is Loaded

Check if Pico CSS is applied:

```javascript
// Check if pico variables exist
const style = getComputedStyle(document.documentElement);
console.log(style.getPropertyValue('--pico-spacing'));
```

## Getting Help

If you're still experiencing issues:

1. **Check the official documentation**: https://picocss.com/docs
2. **Review examples**: https://picocss.com/examples
3. **Search GitHub issues**: https://github.com/picocss/pico/issues
4. **Create a minimal reproduction**: Isolate the issue in a simple HTML file
5. **Check browser console**: Look for CSS or JavaScript errors

## Common Patterns That Don't Work

### Using classes for basic elements

```html
<!-- Don't do this -->
<div class="heading">Title</div>
<div class="button">Click</div>

<!-- Do this -->
<h1>Title</h1>
<button>Click</button>
```

### Overriding with !important

```css
/* Avoid */
button {
  background-color: red !important;
}

/* Prefer */
:root {
  --pico-primary: red;
}
```

### Using non-semantic HTML for layouts

```html
<!-- Don't do this -->
<div class="header">...</div>
<div class="main">...</div>
<div class="footer">...</div>

<!-- Do this -->
<header>...</header>
<main>...</main>
<footer>...</footer>
```
