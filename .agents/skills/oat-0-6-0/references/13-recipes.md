# Oat UI - Recipes and Patterns

Composable widget examples using Oat components.

## Split Button

Combine primary action with dropdown for secondary actions:

```html
<ot-dropdown>
  <menu class="buttons">
    <li><button class="outline">Save</button></li>
    <li>
      <button class="outline" popovertarget="save-actions" aria-label="More save options">
        More
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="m6 9 6 6 6-6"/>
        </svg>
      </button>
    </li>
  </menu>
  
  <menu popover id="save-actions">
    <button role="menuitem">Save draft</button>
    <button role="menuitem">Save and publish</button>
    <button role="menuitem">Save as copy</button>
    <hr>
    <button role="menuitem">Duplicate</button>
  </menu>
</ot-dropdown>
```

## Form Card

Group form fields in a card with header and action footer:

```html
<article class="card" style="max-width: 500px;">
  <header>
    <h3>Edit Profile</h3>
    <p class="text-light">Update your account information</p>
  </header>
  
  <div class="mt-4 vstack gap-3">
    <label data-field>
      Full Name
      <input type="text" value="John Doe" />
    </label>
    
    <label data-field>
      Email Address
      <input type="email" value="john@example.com" />
    </label>
    
    <label data-field>
      Bio
      <textarea rows="3">Software developer passionate about clean code.</textarea>
    </label>
    
    <label>
      <input type="checkbox" role="switch" checked /> Public profile
    </label>
  </div>
  
  <footer class="hstack justify-end gap-2 mt-4">
    <button class="outline">Cancel</button>
    <button>Save Changes</button>
  </footer>
</article>
```

## Empty State Card

Show helpful message when no data exists:

```html
<article class="card align-center" style="padding: var(--space-8); max-width: 400px;">
  <svg width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="var(--muted-foreground)" stroke-width="1" style="margin-bottom: var(--space-4);">
    <circle cx="12" cy="12" r="10"/>
    <path d="M12 6v6l4 2"/>
  </svg>
  
  <h3>No items yet</h3>
  <p class="text-light" style="margin-bottom: var(--space-4);">Get started by creating your first item.</p>
  
  <footer>
    <button>Create New Item</button>
  </footer>
</article>
```

## Stats Dashboard Cards

Compose metrics with cards, badges, and progress:

```html
<div class="container">
  <div class="row" style="gap: var(--space-4);">
    <!-- Revenue Card -->
    <div class="col-4">
      <article class="card">
        <header class="hstack justify-between items-start">
          <div>
            <h4 style="margin: 0;">Revenue</h4>
            <p class="text-light small">This month</p>
          </div>
          <span class="badge success">+12%</span>
        </header>
        
        <h2 style="margin: var(--space-3) 0;">$42,200</h2>
        
        <progress value="72" max="100"></progress>
      </article>
    </div>
    
    <!-- Completion Rate Card -->
    <div class="col-4">
      <article class="card">
        <header class="hstack justify-between items-start">
          <div>
            <h4 style="margin: 0;">Completion</h4>
            <p class="text-light small">Checkout rate</p>
          </div>
          <span class="badge warning">-2%</span>
        </header>
        
        <h2 style="margin: var(--space-3) 0;">4.6%</h2>
        
        <meter value="0.46" min="0" max="1" low="0.3" high="0.7" optimum="1"></meter>
      </article>
    </div>
    
    <!-- Support Tickets Card -->
    <div class="col-4">
      <article class="card">
        <header class="hstack justify-between items-start">
          <div>
            <h4 style="margin: 0;">Tickets</h4>
            <p class="text-light small">Open queue</p>
          </div>
          <span class="badge">14</span>
        </header>
        
        <h2 style="margin: var(--space-3) 0;">14</h2>
        
        <progress value="35" max="100"></progress>
      </article>
    </div>
  </div>
</div>
```

## User Profile Card

Display user information with avatar and actions:

```html
<article class="card align-center" style="max-width: 400px; padding: var(--space-6);">
  <figure data-variant="avatar" class="large" style="margin-bottom: var(--space-3);">
    <img src="/avatar.jpg" alt="" />
  </figure>
  
  <h3 style="margin: 0;">Jane Doe</h3>
  <p class="text-light" style="margin-bottom: var(--space-4);">jane@example.com</p>
  
  <div class="hstack justify-center gap-4" style="margin-bottom: var(--space-4);">
    <div class="vstack align-center">
      <strong>142</strong>
      <span class="text-light small">Posts</span>
    </div>
    <div class="vstack align-center">
      <strong>2.4k</strong>
      <span class="text-light small">Followers</span>
    </div>
    <div class="vstack align-center">
      <strong>389</strong>
      <span class="text-light small">Following</span>
    </div>
  </div>
  
  <footer class="hstack w-full gap-2">
    <button class="outline" style="flex: 1;">Message</button>
    <button style="flex: 1;">Follow</button>
  </footer>
</article>
```

## Search Bar with Filters

```html
<article class="card">
  <header class="hstack gap-3 items-center flex-wrap">
    <div style="flex: 1; min-width: 200px;">
      <fieldset class="group">
        <input type="search" placeholder="Search..." />
        <button>
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <circle cx="11" cy="11" r="8"/><path d="m21 21-4.35-4.35"/>
          </svg>
        </button>
      </fieldset>
    </div>
    
    <ot-dropdown>
      <button popovertarget="filter-menu" class="outline small">
        Filters
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <line x1="4" y1="21" x2="4" y2="14"/><line x1="4" y1="10" x2="4" y2="3"/><line x1="12" y1="21" x2="12" y2="12"/><line x1="12" y1="8" x2="12" y2="3"/><line x1="20" y1="21" x2="20" y2="16"/><line x1="20" y1="12" x2="20" y2="3"/><line x1="1" y1="14" x2="7" y2="14"/><line x1="9" y1="8" x2="15" y2="8"/><line x1="17" y1="16" x2="23" y2="16"/>
        </svg>
      </button>
      
      <div popover id="filter-menu" style="width: 250px; padding: var(--space-3);">
        <h4 style="margin: 0 0 var(--space-3);">Filter by</h4>
        
        <label style="display: block; margin-bottom: var(--space-2);">
          <input type="checkbox" checked /> Show active
        </label>
        <label style="display: block; margin-bottom: var(--space-2);">
          <input type="checkbox" /> Show inactive
        </label>
        
        <hr style="margin: var(--space-3) 0;">
        
        <button style="width: 100%;">Apply Filters</button>
      </div>
    </ot-dropdown>
    
    <ot-dropdown>
      <button popovertarget="sort-menu" class="outline small">Sort ▾</button>
      <menu popover id="sort-menu">
        <button role="menuitem">Newest first</button>
        <button role="menuitem">Oldest first</button>
        <button role="menuitem">A-Z</button>
        <button role="menuitem">Z-A</button>
      </menu>
    </ot-dropdown>
  </header>
</article>
```

## Notification Badge

```html
<button class="relative" style="position: relative;">
  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
    <path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"/>
    <path d="M13.73 21a2 2 0 0 1-3.46 0"/>
  </svg>
  
  <span class="badge danger" style="position: absolute; top: -4px; right: -4px; width: 16px; height: 16px; padding: 0; border-radius: 50%; font-size: var(--text-1); display: flex; align-items: center; justify-content: center;">5</span>
</button>
```

## Callout/Info Box

```html
<article class="card" style="border-left: 4px solid var(--primary);">
  <header class="hstack items-start gap-3">
    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="var(--primary)" stroke-width="2" style="flex-shrink: 0;">
      <circle cx="12" cy="12" r="10"/><line x1="12" y1="16" x2="12" y2="12"/><line x1="12" y1="8" x2="12.01" y2="8"/>
    </svg>
    
    <div>
      <h4 style="margin: 0 0 var(--space-1);">Important Note</h4>
      <p style="margin: 0; color: var(--muted-foreground);">This information is critical for understanding the feature.</p>
    </div>
  </header>
</article>
```

## Tooltip on Hover

Use native `title` attribute (Oat styles it automatically):

```html
<button title="Click to save your changes">Save</button>
<button title="Delete this item permanently" data-variant="danger">Delete</button>
```

For custom positioning:

```html
<button title="Save changes" data-tooltip-placement="top">Top</button>
<button title="Save changes" data-tooltip-placement="bottom">Bottom</button>
<button title="Save changes" data-tooltip-placement="left">Left</button>
<button title="Save changes" data-tooltip-placement="right">Right</button>
```

## Confirm Dialog Pattern

```html
<template id="confirm-template">
  <dialog>
    <form method="dialog">
      <header>
        <h3 id="confirm-title">Confirm Action</h3>
        <p id="confirm-message">Are you sure?</p>
      </header>
      
      <footer class="hstack justify-end gap-2">
        <button type="button" commandfor="this.closest('dialog')" command="close" class="outline">Cancel</button>
        <button type="submit" data-variant="danger" value="confirm">Confirm</button>
      </footer>
    </form>
  </dialog>
</template>

<button onclick="showConfirm('Delete Item', 'This will permanently delete the item. Continue?')">
  Delete Item
</button>

<script>
function showConfirm(title, message) {
  const template = document.getElementById('confirm-template');
  const dialog = template.content.querySelector('dialog').cloneNode(true);
  
  dialog.querySelector('#confirm-title').textContent = title;
  dialog.querySelector('#confirm-message').textContent = message;
  
  document.body.appendChild(dialog);
  
  dialog.addEventListener('close', () => {
    if (dialog.returnValue === 'confirm') {
      console.log('Action confirmed');
      // Perform action
    }
    dialog.remove();
  });
  
  dialog.showModal();
}
</script>
```

## Inline Edit Pattern

```html
<div class="hstack items-center gap-2">
  <span id="display-name">John Doe</span>
  <button class="outline small" onclick="startEdit()">Edit</button>
</div>

<template id="edit-template">
  <div class="hstack items-center gap-2">
    <input type="text" id="edit-input" style="width: 200px;" />
    <button class="small" onclick="saveEdit()">Save</button>
    <button class="outline small" onclick="cancelEdit()">Cancel</button>
  </div>
</template>

<script>
let editing = false;

function startEdit() {
  if (editing) return;
  
  const display = document.getElementById('display-name');
  const template = document.getElementById('edit-template');
  
  display.hidden = true;
  
  const editDiv = template.content.cloneNode(true);
  editDiv.querySelector('#edit-input').value = display.textContent;
  
  display.after(editDiv);
  editDiv.querySelector('input').focus();
  
  editing = true;
}

function saveEdit() {
  const input = document.getElementById('edit-input');
  const display = document.getElementById('display-name');
  
  display.textContent = input.value;
  display.hidden = false;
  
  input.parentElement.remove();
  editing = false;
}

function cancelEdit() {
  const display = document.getElementById('display-name');
  display.hidden = false;
  
  document.querySelector('#edit-input')?.parentElement.remove();
  editing = false;
}
</script>
```

## Loading State Replacement

```html
<div id="content-area">
  <!-- Skeleton loading state -->
  <div class="vstack gap-3" id="skeleton">
    <div role="status" class="skeleton line"></div>
    <div role="status" class="skeleton line" style="width: 80%;"></div>
    <div role="status" class="skeleton line" style="width: 60%;"></div>
  </div>
  
  <!-- Actual content (hidden initially) -->
  <div id="actual-content" hidden>
    <h3>Data Loaded</h3>
    <p>This is the actual content.</p>
  </div>
</div>

<script>
async function loadContent() {
  try {
    const response = await fetch('/api/data');
    const data = await response.json();
    
    // Hide skeleton, show content
    document.getElementById('skeleton').hidden = true;
    document.getElementById('actual-content').hidden = false;
    
    // Populate content
    document.querySelector('#actual-content p').textContent = data.message;
  } catch (error) {
    // Show error state
    document.getElementById('skeleton').innerHTML = `
      <div role="alert" data-variant="error">Failed to load data. Please try again.</div>
    `;
  }
}

loadContent();
</script>
```

## Toast Feedback Pattern

```html
<form id="contact-form">
  <label data-field>
    Email
    <input type="email" required />
  </label>
  
  <button type="submit">Send Message</button>
</form>

<script>
document.getElementById('contact-form').addEventListener('submit', async (e) => {
  e.preventDefault();
  
  const btn = e.target.querySelector('button');
  const originalText = btn.textContent;
  
  // Show loading
  btn.setAttribute('aria-busy', 'true');
  btn.disabled = true;
  btn.textContent = 'Sending...';
  
  try {
    await fetch('/api/contact', {
      method: 'POST',
      body: new FormData(e.target)
    });
    
    // Success toast
    ot.toast('Message sent successfully!', 'Success', { 
      variant: 'success',
      duration: 3000
    });
    
    e.target.reset();
  } catch (error) {
    // Error toast
    ot.toast('Failed to send message. Please try again.', 'Error', { 
      variant: 'danger' 
    });
  } finally {
    btn.setAttribute('aria-busy', 'false');
    btn.disabled = false;
    btn.textContent = originalText;
  }
});
</script>
```

## Card with Actions Overlay

```html
<article class="card" style="position: relative; overflow: hidden;">
  <img src="/image.jpg" alt="" style="width: 100%; border-radius: var(--radius-md) var(--radius-md) 0 0;" />
  
  <div style="padding: var(--space-4);">
    <h3>Project Title</h3>
    <p class="text-light">Project description goes here.</p>
  </div>
  
  <!-- Overlay actions (hidden by default, shown on hover) -->
  <div style="position: absolute; top: 0; left: 0; right: 0; bottom: 0; background: rgb(0 0 0 / 0.5); display: flex; align-items: center; justify-content: center; gap: var(--space-2); opacity: 0; transition: opacity 0.2s;" onmouseenter="this.style.opacity = 1" onmouseleave="this.style.opacity = 0">
    <button class="outline">View</button>
    <button>Edit</button>
    <button data-variant="danger">Delete</button>
  </div>
</article>
```

These recipes demonstrate common patterns you can compose using Oat's primitive components. Mix and match to build your own custom widgets!
