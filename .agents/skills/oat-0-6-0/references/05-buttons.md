# Oat UI - Buttons

Complete button component documentation with variants, sizes, groups, and states.

## Basic Button

The `<button>` element is styled automatically:

```html
<button>Click me</button>
```

## Button Variants

### Primary (Default)

```html
<button>Primary Button</button>
```

Uses `--primary` color from theme.

### Secondary

```html
<button data-variant="secondary">Secondary</button>
```

Uses `--secondary` color, less prominent.

### Danger

```html
<button data-variant="danger">Danger</button>
```

Uses `--danger` color for destructive actions.

### Outline

```html
<button class="outline">Outline</button>
<button data-variant="danger" class="outline">Danger Outline</button>
```

Transparent background with border.

### Ghost

```html
<button class="ghost">Ghost</button>
```

Minimal styling, text only with hover effect.

## Button Sizes

### Small

```html
<button class="small">Small Button</button>
```

### Default (Medium)

```html
<button>Normal Button</button>
```

### Large

```html
<button class="large">Large Button</button>
```

## Button States

### Disabled

```html
<button disabled>Disabled</button>
<button data-variant="danger" disabled>Disabled Danger</button>
```

Visually muted and non-interactive.

### Loading

Use `aria-busy` with spinner:

```html
<button aria-busy="true" data-spinner="small" disabled>Loading...</button>
```

### Hover and Focus

All buttons have automatic hover and focus states. Focus ring uses `--ring` color.

## Buttons with Icons

### Icon After Text

```html
<button>
  Save
  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
    <path d="M19 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11l5 5v11a2 2 0 0 1-2 2z"/>
  </svg>
</button>
```

### Icon Before Text

```html
<button>
  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
    <circle cx="11" cy="11" r="8"/><path d="m21 21-4.35-4.35"/>
  </svg>
  Search
</button>
```

### Icon Only

```html
<button aria-label="Settings">
  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
    <circle cx="12" cy="12" r="3"/>
    <path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"/>
  </svg>
</button>
```

## Button Groups

### Horizontal Group

Wrap buttons in `<menu class="buttons">`:

```html
<menu class="buttons">
  <li><button class="outline">Left</button></li>
  <li><button class="outline">Center</button></li>
  <li><button class="outline">Right</button></li>
</menu>
```

Buttons connect with shared borders.

### Segmented Control

```html
<menu class="buttons">
  <li><button class="outline" aria-pressed="true">Daily</button></li>
  <li><button class="outline" aria-pressed="false">Weekly</button></li>
  <li><button class="outline" aria-pressed="false">Monthly</button></li>
</menu>
```

Use `aria-pressed` to indicate active state.

## Hyperlink as Button

Style `<a>` element as button:

```html
<a href="/page" class="button">Link Button</a>
<a href="/delete" class="button" data-variant="danger">Delete</a>
```

## Form Buttons

### Submit Button

```html
<form>
  <label data-field>
    Name
    <input type="text" />
  </label>
  
  <button type="submit">Submit</button>
</form>
```

### Reset Button

```html
<button type="reset" class="outline">Reset Form</button>
```

### Button in Fieldset

```html
<fieldset class="group">
  <input type="text" placeholder="Search" />
  <button>Go</button>
</fieldset>
```

## Common Patterns

### Action Buttons in Card

```html
<article class="card">
  <header>
    <h3>Document</h3>
  </header>
  <footer class="hstack">
    <button class="outline">Cancel</button>
    <button>Save</button>
  </footer>
</article>
```

### Primary and Secondary Actions

```html
<div class="hstack">
  <button class="outline">Cancel</button>
  <button>Confirm</button>
</div>
```

### Destructive Action Confirmation

```html
<div class="hstack">
  <button class="outline" popovertarget="confirm-dialog" command="show-modal">Delete</button>
  
  <dialog id="confirm-dialog">
    <form method="dialog">
      <header><h3>Delete Item?</h3></header>
      <p>This action cannot be undone.</p>
      <footer class="hstack">
        <button type="button" commandfor="confirm-dialog" command="close" class="outline">Cancel</button>
        <button type="submit" data-variant="danger" value="delete">Delete</button>
      </footer>
    </form>
  </dialog>
</div>
```

### Icon Button Group

```html
<menu class="buttons">
  <li><button class="outline" aria-label="Bold"><strong>B</strong></button></li>
  <li><button class="outline" aria-label="Italic"><em>I</em></button></li>
  <li><button class="outline" aria-label="Underline"><u>U</u></button></li>
</menu>
```

## Accessibility

### Label Requirements

- Visible text buttons: No additional labeling needed
- Icon-only buttons: Require `aria-label`
- Button groups: Consider `aria-label` on container

### Keyboard Navigation

All buttons are focusable and activable with Enter/Space keys.

### State Communication

```html
<!-- Loading state -->
<button aria-busy="true" disabled>Saving...</button>

<!-- Selected state in group -->
<button aria-pressed="true">Active</button>
<button aria-pressed="false">Inactive</button>
```

## Customization

### Button Padding

```css
button {
  --btn-padding: var(--space-3) var(--space-5);
}

button.small {
  --btn-padding: var(--space-2) var(--space-3);
}

button.large {
  --btn-padding: var(--space-4) var(--space-6);
}
```

### Button Radius

```css
button {
  border-radius: var(--radius-full);  /* Pill-shaped */
}
```

### Button Font Weight

```css
button {
  font-weight: 600;
}
```

## Best Practices

### DO

- Use semantic `<button>` element for actions
- Use clear, action-oriented labels ("Save", "Delete", not "Click here")
- Provide visual feedback on hover and focus
- Use appropriate variants (danger for destructive actions)
- Group related buttons together

### DON'T

- Use buttons for navigation (use links instead)
- Make buttons too small (minimum 44px touch target)
- Remove focus indicators
- Use multiple primary buttons in same context
- Rely only on color to convey meaning
