# Oat UI - Dropdowns and Tabs

Interactive components for navigation and content organization.

## Dropdown Menus

### Basic Dropdown

```html
<ot-dropdown>
  <button popovertarget="menu-1" class="outline">
    Options
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
      <path d="m6 9 6 6 6-6"/>
    </svg>
  </button>
  
  <menu popover id="menu-1">
    <button role="menuitem">Profile</button>
    <button role="menuitem">Settings</button>
    <button role="menuitem">Help</button>
    <hr>
    <button role="menuitem">Logout</button>
  </menu>
</ot-dropdown>
```

### Dropdown with Icons

```html
<ot-dropdown>
  <button popovertarget="menu-icons" class="outline">Actions</button>
  
  <menu popover id="menu-icons">
    <button role="menuitem">
      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/></svg>
      Edit
    </button>
    <button role="menuitem">
      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="17 8 12 3 7 8"/><line x1="12" y1="3" x2="12" y2="14"/></svg>
      Upload
    </button>
    <button role="menuitem">
      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="3 6 5 6 21 6"/><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/></svg>
      Download
    </button>
  </menu>
</ot-dropdown>
```

### Popover Dropdown (Card-style)

```html
<ot-dropdown>
  <button popovertarget="confirm-popover" class="outline">Confirm Action</button>
  
  <article class="card" popover id="confirm-popover">
    <header>
      <h4>Are you sure?</h4>
      <p>This action cannot be undone.</p>
    </header>
    
    <br />
    
    <footer>
      <button class="outline small" popovertarget="confirm-popover">Cancel</button>
      <button data-variant="danger" class="small" popovertarget="confirm-popover">Delete</button>
    </footer>
  </article>
</ot-dropdown>
```

### Dropdown with Search

```html
<ot-dropdown>
  <button popovertarget="search-menu">Select Item</button>
  
  <div popover id="search-menu" style="width: 300px; padding: var(--space-3);">
    <input type="search" placeholder="Search..." style="width: 100%; margin-bottom: var(--space-3);" />
    
    <menu style="max-height: 300px; overflow-y: auto;">
      <button role="menuitem">Item 1</button>
      <button role="menuitem">Item 2</button>
      <button role="menuitem">Item 3</button>
    </menu>
  </div>
</ot-dropdown>
```

### Avatar Dropdown (User Menu)

```html
<ot-dropdown>
  <figure data-variant="avatar" tabindex="0" popovertarget="user-menu" style="cursor: pointer;">
    <img src="/avatar.svg" alt="" />
  </figure>
  
  <menu popover id="user-menu" style="width: 200px;">
    <div style="padding: var(--space-3); border-bottom: 1px solid var(--border);">
      <strong>John Doe</strong>
      <p class="text-light small">john@example.com</p>
    </div>
    
    <button role="menuitem">Profile</button>
    <button role="menuitem">Settings</button>
    <hr>
    <button role="menuitem" data-variant="danger">Logout</button>
  </menu>
</ot-dropdown>
```

## Tabs Component

### Basic Tabs

```html
<ot-tabs>
  <div role="tablist">
    <button role="tab">Account</button>
    <button role="tab">Password</button>
    <button role="tab">Notifications</button>
  </div>
  
  <div role="tabpanel">
    <h3>Account Settings</h3>
    <p>Manage your account information here.</p>
    
    <label data-field>
      Display Name
      <input type="text" value="John Doe" />
    </label>
  </div>
  
  <div role="tabpanel">
    <h3>Password Settings</h3>
    <p>Change your password here.</p>
    
    <label data-field>
      Current Password
      <input type="password" />
    </label>
    <label data-field>
      New Password
      <input type="password" />
    </label>
  </div>
  
  <div role="tabpanel">
    <h3>Notification Settings</h3>
    <p>Configure your notification preferences.</p>
    
    <label><input type="checkbox" checked> Email notifications</label>
    <label><input type="checkbox" checked> Push notifications</label>
    <label><input type="checkbox"> SMS alerts</label>
  </div>
</ot-tabs>
```

### Tabs with Icons

```html
<ot-tabs>
  <div role="tablist">
    <button role="tab">
      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/><polyline points="9 22 9 12 15 12 15 22"/></svg>
      Home
    </button>
    <button role="tab">
      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21"/></svg>
      Settings
    </button>
    <button role="tab">
      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>
      Profile
    </button>
  </div>
  
  <div role="tabpanel">
    <h3>Dashboard</h3>
    <p>Welcome to your home page.</p>
  </div>
  
  <div role="tabpanel">
    <h3>Settings</h3>
    <p>Configure your preferences.</p>
  </div>
  
  <div role="tabpanel">
    <h3>Profile</h3>
    <p>View and edit your profile.</p>
  </div>
</ot-tabs>
```

### Tabs in Dialog

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
        <button role="tab">Security</button>
        <button role="tab">Billing</button>
      </div>
      
      <div role="tabpanel">
        <label data-field>
          Company Name
          <input type="text" value="Acme Inc" />
        </label>
      </div>
      
      <div role="tabpanel">
        <label><input type="checkbox" checked> Two-factor authentication</label>
        <label><input type="checkbox"> IP whitelist</label>
      </div>
      
      <div role="tabpanel">
        <p>Current plan: <strong>Pro</strong></p>
        <button class="outline">Upgrade Plan</button>
      </div>
    </ot-tabs>
    
    <footer class="hstack justify-end gap-2">
      <button type="button" commandfor="settings-dialog" command="close" class="outline">Cancel</button>
      <button type="submit" value="save">Save Changes</button>
    </footer>
  </form>
</dialog>
```

### Tabs with Pill Style

```css
ot-tabs[aria-orientation="horizontal"] [role="tablist"] {
  background: var(--muted);
  padding: var(--space-1);
  border-radius: var(--radius-full);
}

ot-tabs[aria-orientation="horizontal"] [role="tab"] {
  border-radius: var(--radius-full);
  padding: var(--space-2) var(--space-4);
}

ot-tabs[aria-orientation="horizontal"] [role="tab"][aria-selected="true"] {
  background: var(--primary);
  color: var(--primary-foreground);
}
```

## Tab with Content Loading

```html
<ot-tabs>
  <div role="tablist">
    <button role="tab">Overview</button>
    <button role="tab">Details</button>
    <button role="tab">History</button>
  </div>
  
  <div role="tabpanel">
    <h3>Overview</h3>
    <p>Quick summary of the item.</p>
  </div>
  
  <div role="tabpanel">
    <div aria-busy="true" data-spinner="large">Loading...</div>
    <!-- Content loads here -->
  </div>
  
  <div role="tabpanel">
    <h3>Activity History</h3>
    <ul>
      <li>Created on Jan 1, 2024</li>
      <li>Updated on Jan 15, 2024</li>
    </ul>
  </div>
</ot-tabs>
```

## Accessibility

### Keyboard Navigation

**Dropdowns:**
- Enter/Space: Open/close dropdown
- Escape: Close dropdown
- Arrow keys: Navigate menu items

**Tabs:**
- Arrow Left/Right: Move between tabs
- Home: First tab
- End: Last tab

### ARIA Attributes

Both components use proper ARIA roles:

```html
<!-- Dropdown -->
<button popovertarget="menu" aria-haspopup="true" aria-expanded="false">
<menu popover id="menu" role="menu">
  <button role="menuitem">Item</button>
</menu>

<!-- Tabs -->
<div role="tablist">
  <button role="tab" aria-selected="true" aria-controls="panel-1">Tab 1</button>
  <button role="tab" aria-selected="false" aria-controls="panel-2">Tab 2</button>
</div>
<div role="tabpanel" id="panel-1" tabindex="0">Content 1</div>
<div role="tabpanel" id="panel-2" tabindex="-1" hidden>Content 2</div>
```

## Customization

### Dropdown Positioning

```css
[popover] {
  /* Default: below trigger */
}

/* Position above */
[popover].position-top {
  top: auto;
  bottom: 100%;
}

/* Position left */
[popover].align-right {
  right: 0;
  left: auto;
}
```

### Tab Styles

```css
/* Underline style */
[role="tablist"] {
  border-bottom: 2px solid var(--border);
}

[role="tab"][aria-selected="true"] {
  border-bottom: 2px solid var(--primary);
  margin-bottom: -2px;
}

/* Box style */
[role="tablist"] {
  display: flex;
  gap: var(--space-1);
}

[role="tab"] {
  padding: var(--space-3) var(--space-4);
  border-radius: var(--radius-md);
  background: var(--muted);
}
```

## Best Practices

### Dropdowns

- DO use for secondary actions and overflow menus
- DO include icons for visual scanning
- DO group related items with dividers
- DON'T nest dropdowns deeply
- DON'T put critical actions only in dropdowns

### Tabs

- DO use for organizing related content
- DO keep tab count reasonable (3-5 tabs)
- DO make tab labels concise
- DON'T use tabs for navigation between pages
- DON't auto-switch tabs without user action
