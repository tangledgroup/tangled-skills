# Oat UI - Dialogs

Zero-JavaScript modal dialogs using native `<dialog>` element with full accessibility support.

## Basic Dialog

```html
<button commandfor="my-dialog" command="show-modal">Open Dialog</button>

<dialog id="my-dialog" closedby="any">
  <form method="dialog">
    <header>
      <h3>Dialog Title</h3>
      <p>Dialog description or subtitle.</p>
    </header>
    
    <div>
      <p>Dialog content goes here. Any HTML is allowed.</p>
    </div>
    
    <footer>
      <button type="button" commandfor="my-dialog" command="close" class="outline">Cancel</button>
      <button value="confirm">Confirm</button>
    </footer>
  </form>
</dialog>
```

### Key Attributes

- `commandfor="id"`: Button opens dialog with this ID
- `command="show-modal"`: Opens the target dialog
- `closedby="any"`: Clicking backdrop closes dialog
- `method="dialog"`: Form submits to dialog.returnValue

## Dialog with Form

```html
<button commandfor="edit-dialog" command="show-modal">Edit Profile</button>

<dialog id="edit-dialog">
  <form method="dialog">
    <header>
      <h3>Edit Profile</h3>
    </header>
    
    <div class="vstack gap-3">
      <label data-field>
        Name
        <input name="name" type="text" value="John Doe" required />
      </label>
      
      <label data-field>
        Email
        <input name="email" type="email" value="john@example.com" required />
      </label>
      
      <label data-field>
        Bio
        <textarea name="bio" rows="3">Software developer</textarea>
      </label>
    </div>
    
    <footer class="hstack justify-end gap-2 mt-4">
      <button type="button" commandfor="edit-dialog" command="close" class="outline">Cancel</button>
      <button type="submit" value="save">Save Changes</button>
    </footer>
  </form>
</dialog>
```

## Confirmation Dialog

```html
<button commandfor="delete-confirm" command="show-modal" class="danger">Delete Item</button>

<dialog id="delete-confirm">
  <form method="dialog">
    <header>
      <h3>Delete Item?</h3>
      <p>This action cannot be undone. The item will be permanently removed.</p>
    </header>
    
    <footer class="hstack justify-end gap-2">
      <button type="button" commandfor="delete-confirm" command="close" class="outline">Cancel</button>
      <button type="submit" data-variant="danger" value="delete">Delete</button>
    </footer>
  </form>
</dialog>
```

## Alert/Info Dialog

```html
<button commandfor="info-dialog" command="show-modal">Show Info</button>

<dialog id="info-dialog" closedby="any">
  <form method="dialog">
    <header>
      <h3>Information</h3>
    </header>
    
    <div>
      <p>Your changes have been saved successfully.</p>
      <p>You can now close this dialog.</p>
    </div>
    
    <footer class="justify-center">
      <button type="button" commandfor="info-dialog" command="close">Got it</button>
    </footer>
  </form>
</dialog>
```

## Dialog with Tabs

```html
<button commandfor="settings-dialog" command="show-modal">Settings</button>

<dialog id="settings-dialog">
  <form method="dialog">
    <header>
      <h3>Settings</h3>
    </header>
    
    <ot-tabs style="margin: var(--space-4) 0;">
      <div role="tablist">
        <button role="tab">General</button>
        <button role="tab">Privacy</button>
        <button role="tab">Notifications</button>
      </div>
      
      <div role="tabpanel">
        <h4>General Settings</h4>
        <label data-field>
          Display Name
          <input type="text" value="John Doe" />
        </label>
      </div>
      
      <div role="tabpanel">
        <h4>Privacy Settings</h4>
        <label><input type="checkbox" checked> Make profile public</label>
      </div>
      
      <div role="tabpanel">
        <h4>Notification Settings</h4>
        <label><input type="checkbox" checked> Email notifications</label>
        <label><input type="checkbox"> Push notifications</label>
      </div>
    </ot-tabs>
    
    <footer class="hstack justify-end gap-2">
      <button type="button" commandfor="settings-dialog" command="close" class="outline">Cancel</button>
      <button type="submit" value="save">Save Settings</button>
    </footer>
  </form>
</dialog>
```

## Handling Return Value

### JavaScript Event Listener

```javascript
const dialog = document.querySelector('#my-dialog');

dialog.addEventListener('close', (e) => {
  const result = dialog.returnValue;
  console.log('Dialog closed with:', result);
  
  if (result === 'confirm') {
    // Handle confirmation
  } else if (result === 'save') {
    // Handle save
  }
});
```

### Inline onclose Handler

```html
<dialog id="my-dialog" onclose="handleDialogClose(this)">
  <!-- content -->
</dialog>

<script>
function handleDialogClose(dialog) {
  console.log('Result:', dialog.returnValue);
}
</script>
```

### Form Data Access

```javascript
const dialog = document.querySelector('#edit-dialog');

dialog.addEventListener('close', (e) => {
  if (dialog.returnValue === 'save') {
    const formData = new FormData(dialog.querySelector('form'));
    const data = Object.fromEntries(formData);
    console.log('Form data:', data);
    // { name: 'John Doe', email: 'john@example.com', bio: '...' }
  }
});
```

## Dialog Options

### Close on Backdrop Click

```html
<dialog closedby="any">
  <!-- Clicking backdrop closes dialog -->
</dialog>
```

### No Backdrop Close (Modal)

```html
<dialog>
  <!-- Must click button to close -->
</dialog>
```

### Custom Backdrop

```html
<dialog>
  <div class="backdrop" onclick="this.closest('dialog').close()"></div>
  <!-- content -->
</dialog>
```

## Stacking Multiple Dialogs

```html
<button commandfor="dialog-1" command="show-modal">Open First</button>

<dialog id="dialog-1">
  <form method="dialog">
    <h3>First Dialog</h3>
    <p>This is the first dialog.</p>
    
    <button commandfor="dialog-2" command="show-modal">Open Second Dialog</button>
    
    <footer>
      <button type="button" commandfor="dialog-1" command="close">Close</button>
    </footer>
  </form>
</dialog>

<dialog id="dialog-2">
  <form method="dialog">
    <h3>Second Dialog</h3>
    <p>This dialog is on top of the first one.</p>
    <footer>
      <button type="button" commandfor="dialog-2" command="close">Close</button>
    </footer>
  </form>
</dialog>
```

## Full-Screen Dialog

```html
<dialog class="full-screen">
  <form method="dialog">
    <header>
      <h3>Full Screen Content</h3>
      <button type="button" commandfor="this.closest('dialog')" command="close" class="outline">Close</button>
    </header>
    
    <div style="height: 60vh;">
      <!-- Full screen content -->
    </div>
  </form>
</dialog>
```

```css
dialog.full-screen {
  width: 100vw;
  height: 100vh;
  max-width: none;
  max-height: none;
  border-radius: 0;
  position: fixed;
  inset: 0;
}
```

## Narrow Dialog (for Mobile)

```html
<dialog class="narrow">
  <!-- Content -->
</dialog>
```

```css
dialog.narrow {
  width: 90%;
  max-width: 400px;
}
```

## Programmatic Control

### Open Dialog

```javascript
const dialog = document.querySelector('#my-dialog');
dialog.showModal();
```

### Close Dialog

```javascript
dialog.close();
```

### Close with Return Value

```javascript
dialog.close('confirmed');
```

### Check if Open

```javascript
if (dialog.open) {
  console.log('Dialog is open');
}
```

## Accessibility Features

### Focus Trapping

Native `<dialog>` automatically traps focus within the dialog when open.

### Keyboard Navigation

- **Escape**: Closes dialog (if allowed)
- **Tab**: Cycles through focusable elements
- **Shift+Tab**: Reverse cycle

### Screen Reader Support

Dialog announces as modal window to screen readers.

### aria Attributes

```html
<dialog aria-labelledby="dialog-title" aria-describedby="dialog-desc">
  <h3 id="dialog-title">Title</h3>
  <p id="dialog-desc">Description</p>
</dialog>
```

## Customization

### Dialog Size

```css
dialog {
  width: 500px;
  max-width: 90%;
}

dialog.large {
  width: 700px;
}

dialog.small {
  width: 400px;
}
```

### Dialog Padding

```css
dialog::backdrop {
  background: rgb(0 0 0 / 0.5);
}

dialog > form {
  padding: var(--space-6);
}
```

### Dialog Border Radius

```css
dialog {
  border-radius: var(--radius-lg);
}
```

## Best Practices

### DO

- Use clear, descriptive titles
- Provide cancel/close options
- Keep dialogs focused on single task
- Use appropriate button variants (danger for destructive)
- Handle return values to know user action

### DON'T

- Nest too many dialogs (max 2-3 levels)
- Put critical actions without confirmation
- Make dialogs too large or complex
- Trap users (always provide escape)
- Use dialogs for simple inline edits

## Common Patterns

### Edit Form Pattern

```html
<article class="card">
  <header>
    <h3>User Profile</h3>
  </header>
  
  <p>Name: John Doe</p>
  <p>Email: john@example.com</p>
  
  <footer>
    <button commandfor="edit-user" command="show-modal">Edit</button>
  </footer>
</article>

<dialog id="edit-user">
  <!-- Edit form -->
</dialog>
```

### Delete Confirmation Pattern

```html
<button onclick="confirmDelete('item-123')">Delete Item</button>

<template id="delete-dialog-template">
  <dialog>
    <form method="dialog">
      <header><h3>Delete?</h3></header>
      <p>This cannot be undone.</p>
      <footer class="hstack">
        <button type="button" commandfor="this.closest('dialog')" command="close" class="outline">Cancel</button>
        <button type="submit" data-variant="danger" value="delete">Delete</button>
      </footer>
    </form>
  </dialog>
</template>

<script>
function confirmDelete(itemId) {
  const template = document.getElementById('delete-dialog-template');
  const dialog = template.content.querySelector('dialog').cloneNode(true);
  document.body.appendChild(dialog);
  
  dialog.addEventListener('close', () => {
    if (dialog.returnValue === 'delete') {
      deleteItem(itemId);
    }
    dialog.remove();
  });
  
  dialog.showModal();
}
</script>
```
