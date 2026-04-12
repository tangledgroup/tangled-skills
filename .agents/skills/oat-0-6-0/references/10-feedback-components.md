# Oat UI - Feedback Components

Alerts, toasts, progress indicators, spinners, and skeleton loaders.

## Alerts

### Alert Variants

```html
<!-- Success -->
<div role="alert" data-variant="success">
  <strong>Success!</strong> Your changes have been saved.
</div>

<!-- Warning -->
<div role="alert" data-variant="warning">
  <strong>Warning!</strong> Please review before continuing.
</div>

<!-- Info (default) -->
<div role="alert">
  <strong>Info</strong> This is a default alert message.
</div>

<!-- Error/Danger -->
<div role="alert" data-variant="error">
  <strong>Error!</strong> Something went wrong.
</div>
```

### Dismissible Alert

```html
<div role="alert" data-variant="success">
  <strong>Success!</strong> Changes saved.
  <button class="outline small" onclick="this.closest('[role=alert]').remove()" style="float: right;" aria-label="Dismiss">×</button>
</div>
```

### Alert with Actions

```html
<div role="alert" data-variant="warning">
  <strong>Unsaved changes</strong>
  <p>You have unsaved changes. What would you like to do?</p>
  <div class="hstack gap-2" style="margin-top: var(--space-3);">
    <button class="small">Save</button>
    <button class="outline small">Discard</button>
  </div>
</div>
```

## Toast Notifications

### Basic Toast

```html
<button onclick="ot.toast('Action completed successfully')">Show Toast</button>
```

### Toast with Title

```html
<button onclick="ot.toast('Changes saved', 'Success')">Show Toast</button>
```

### Toast with Variant

```html
<button onclick="ot.toast('Action completed', 'All good', { variant: 'success' })">Success Toast</button>
<button onclick="ot.toast('Something went wrong', 'Oops', { variant: 'danger' })">Error Toast</button>
<button onclick="ot.toast('Please review', 'Warning', { variant: 'warning' })">Warning Toast</button>
```

### Toast Placement

```javascript
// Top right (default)
ot.toast('Message', 'Title')

// Other positions
ot.toast('Message', '', { placement: 'top-left' })
ot.toast('Message', '', { placement: 'top-center' })
ot.toast('Message', '', { placement: 'bottom-right' })
ot.toast('Message', '', { placement: 'bottom-center' })
ot.toast('Message', '', { placement: 'bottom-left' })
```

### Toast Duration

```javascript
// Auto-dismiss after 4 seconds (default)
ot.toast('Message', '', { duration: 4000 })

// Persistent toast (no auto-dismiss)
ot.toast('Message', '', { duration: 0 })

// Quick toast
ot.toast('Message', '', { duration: 2000 })
```

### Custom Toast Markup

```html
<template id="custom-toast">
  <output class="toast" data-variant="success">
    <h6 class="toast-title">Changes saved</h6>
    <p>Your document has been updated.</p>
    <button class="outline small">Okay</button>
  </output>
</template>

<button onclick="ot.toast.el(document.querySelector('#custom-toast').content.cloneNode(true))">
  Custom Toast
</button>
```

### Clearing Toasts

```javascript
// Clear all toasts
ot.toast.clear()

// Clear specific placement
ot.toast.clear('top-right')
```

## Progress Bars

### Basic Progress

```html
<progress value="60" max="100"></progress>
```

### Multiple Progress Bars

```html
<div class="vstack gap-2">
  <div>
    <span>Downloading...</span>
    <progress value="30" max="100"></progress>
  </div>
  
  <div>
    <span>Processing...</span>
    <progress value="60" max="100"></progress>
  </div>
  
  <div>
    <span>Uploading...</span>
    <progress value="90" max="100"></progress>
  </div>
</div>
```

### Indeterminate Progress

```html
<progress max=""></progress>
```

No value attribute shows indeterminate animation.

## Meter

### Basic Meter

```html
<meter value="0.8" min="0" max="1"></meter>
<meter value="0.5" min="0" max="1"></meter>
<meter value="0.2" min="0" max="1"></meter>
```

### Meter with Thresholds

```html
<!-- Low (red) -->
<meter value="0.2" min="0" max="1" low="0.3" high="0.7" optimum="1"></meter>

<!-- Medium (yellow) -->
<meter value="0.5" min="0" max="1" low="0.3" high="0.7" optimum="1"></meter>

<!-- High (green) -->
<meter value="0.8" min="0" max="1" low="0.3" high="0.7" optimum="1"></meter>
```

### Disk Usage Example

```html
<div>
  <span>Disk Usage: 75%</span>
  <meter value="0.75" min="0" max="1" low="0.5" high="0.8" optimum="0.2"></meter>
</div>
```

## Spinners

### Basic Spinner

```html
<div aria-busy="true"></div>
```

### Spinner Sizes

```html
<div class="hstack" style="gap: var(--space-4);">
  <div aria-busy="true" data-spinner="small"></div>
  <div aria-busy="true"></div>
  <div aria-busy="true" data-spinner="large"></div>
</div>
```

### Spinner in Button

```html
<button aria-busy="true" data-spinner="small" disabled>Loading...</button>
```

### Spinner Overlay

```html
<article class="card" aria-busy="true" data-spinner="large overlay">
  <header><h3>Loading Card</h3></header>
  <p>Content is dimmed while loading...</p>
  <footer>
    <button class="outline">Cancel</button>
    <button>Save</button>
  </footer>
</article>
```

The overlay dims the content and centers the spinner.

## Skeleton Loaders

### Basic Skeleton

```html
<div role="status" class="skeleton line"></div>
<div role="status" class="skeleton box"></div>
```

### Skeleton Text Lines

```html
<div class="vstack gap-2">
  <div role="status" class="skeleton line"></div>
  <div role="status" class="skeleton line" style="width: 80%;"></div>
  <div role="status" class="skeleton line" style="width: 60%;"></div>
</div>
```

### Skeleton Box (Image)

```html
<div role="status" class="skeleton box" style="width: 200px; height: 150px;"></div>
```

### Skeleton Card

```html
<article style="display: flex; gap: var(--space-3); padding: var(--space-4);">
  <!-- Avatar placeholder -->
  <div role="status" class="skeleton box" style="width: 60px; height: 60px; border-radius: 50%;"></div>
  
  <!-- Text placeholders -->
  <div style="flex: 1; display: flex; flex-direction: column; gap: var(--space-2);">
    <div role="status" class="skeleton line" style="width: 60%;"></div>
    <div role="status" class="skeleton line" style="width: 80%;"></div>
  </div>
</article>
```

### Skeleton List

```html
<div class="vstack gap-3">
  <!-- Item 1 -->
  <article style="display: flex; gap: var(--space-3); padding: var(--space-3);">
    <div role="status" class="skeleton box" style="width: 50px; height: 50px;"></div>
    <div style="flex: 1;">
      <div role="status" class="skeleton line"></div>
      <div role="status" class="skeleton line" style="width: 60%; margin-top: var(--space-2);"></div>
    </div>
  </article>
  
  <!-- Item 2 -->
  <article style="display: flex; gap: var(--space-3); padding: var(--space-3);">
    <div role="status" class="skeleton box" style="width: 50px; height: 50px;"></div>
    <div style="flex: 1;">
      <div role="status" class="skeleton line"></div>
      <div role="status" class="skeleton line" style="width: 60%; margin-top: var(--space-2);"></div>
    </div>
  </article>
</div>
```

## Loading States Pattern

### Before/After Loading

```html
<!-- Initial state with skeleton -->
<div id="content-area">
  <div class="vstack gap-3">
    <!-- Skeleton items -->
    <div role="status" class="skeleton line"></div>
    <div role="status" class="skeleton line"></div>
    <div role="status" class="skeleton line"></div>
  </div>
</div>

<script>
async function loadContent() {
  // Show skeleton (already in HTML)
  
  const data = await fetch('/api/data');
  
  // Replace with actual content
  document.getElementById('content-area').innerHTML = `
    <h3>Results</h3>
    <p>${data.results}</p>
  `;
}

loadContent();
</script>
```

### Spinner to Content

```html
<div id="loading-container" aria-busy="true">
  <div class="align-center" style="padding: var(--space-8);">
    <div aria-busy="true" data-spinner="large"></div>
    <p class="text-light mt-3">Loading...</p>
  </div>
</div>

<script>
async function loadData() {
  const data = await fetch('/api/data');
  
  document.getElementById('loading-container').innerHTML = `
    <h3>Data Loaded</h3>
    <p>${data.content}</p>
  `;
}

loadData();
</script>
```

## Success/Error States

### Form Submission Pattern

```html
<form id="contact-form">
  <label data-field>
    Email
    <input type="email" required />
  </label>
  
  <button type="submit" aria-busy="false">Send Message</button>
</form>

<div id="form-result"></div>

<script>
document.getElementById('contact-form').addEventListener('submit', async (e) => {
  e.preventDefault();
  
  const btn = e.target.querySelector('button');
  const resultDiv = document.getElementById('form-result');
  
  // Show loading
  btn.setAttribute('aria-busy', 'true');
  btn.disabled = true;
  
  try {
    await fetch('/api/contact', { method: 'POST', body: new FormData(e.target) });
    
    // Show success
    resultDiv.innerHTML = '<div role="alert" data-variant="success">Message sent successfully!</div>';
  } catch (err) {
    // Show error
    resultDiv.innerHTML = '<div role="alert" data-variant="error">Failed to send message. Please try again.</div>';
  } finally {
    btn.setAttribute('aria-busy', 'false');
    btn.disabled = false;
  }
});
</script>
```

## Accessibility

### Progress and Meter Labels

```html
<progress value="60" max="100" aria-valuetext="60 percent complete"></progress>
<meter value="0.75" aria-label="Disk usage">75%</meter>
```

### Spinner Announcements

```html
<div aria-busy="true" aria-live="polite">Loading items...</div>
```

### Skeleton Role

```html
<div role="status" class="skeleton">
  <!-- Screen readers announce as loading -->
</div>
```

## Customization

### Alert Padding

```css
[role="alert"] {
  padding: var(--space-4);
}
```

### Toast Styling

```css
.toast {
  --toast-padding: var(--space-4);
  --toast-radius: var(--radius-md);
  --toast-shadow: var(--shadow-lg);
}
```

### Progress Height

```css
progress {
  height: 0.5rem;
}
```
