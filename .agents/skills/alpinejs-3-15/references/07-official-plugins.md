# Official Plugins

Alpine.js offers official plugins that extend functionality with common features like focus management, persistent state, form masking, and more. All plugins are maintained by the Alpine team.

## Plugin Installation

### CDN Installation

Include plugins BEFORE Alpine core:

```html
<!-- Plugins first -->
<script defer src="https://cdn.jsdelivr.net/npm/@alpinejs/focus@3.15.0/dist/cdn.min.js"></script>
<script defer src="https://cdn.jsdelivr.net/npm/@alpinejs/persist@3.15.0/dist/cdn.min.js"></script>
<script defer src="https://cdn.jsdelivr.net/npm/@alpinejs/mask@3.15.0/dist/cdn.min.js"></script>

<!-- Then Alpine core -->
<script defer src="https://cdn.jsdelivr.net/npm/alpinejs@3.15.0/dist/cdn.min.js"></script>
```

### NPM Installation

```bash
npm install @alpinejs/focus @alpinejs/persist @alpinejs/mask
```

```javascript
import Alpine from 'alpinejs'
import focus from '@alpinejs/focus'
import persist from '@alpinejs/persist'
import mask from '@alpinejs/mask'

Alpine.plugin(focus)
Alpine.plugin(persist)
Alpine.plugin(mask)

Alpine.start()
```

## Focus Plugin

Manages focus behavior, including trapping focus within elements and programmatically focusing elements.

### Installation

```html
<script defer src="https://cdn.jsdelivr.net/npm/@alpinejs/focus@3.15.0/dist/cdn.min.js"></script>
<script defer src="https://cdn.jsdelivr.net/npm/alpinejs@3.15.0/dist/cdn.min.js"></script>
```

### x-focus

Focus an element when condition is true:

```html
<div x-data="{ showModal: false }">
    <button @click="showModal = true">Open Modal</button>
    
    <div x-show="showModal" x-ref="modal">
        <input x-focus="showModal" autofocus placeholder="Auto-focused">
        <button @click="showModal = false">Close</button>
    </div>
</div>
```

### x-trap.noscroll

Trap focus within an element (prevents tabbing outside):

```html
<div x-data="{ open: false }">
    <button @click="open = true">Open Modal</button>
    
    <div x-show="open" 
         x-trap.noscroll="open"
         style="position: fixed; inset: 0; display: flex; align-items: center; justify-content: center;">
        <div style="background: white; padding: 2rem;">
            <p>Tab through these elements - focus stays trapped</p>
            <input type="text" placeholder="Field 1">
            <input type="text" placeholder="Field 2">
            <button @click="open = false">Close</button>
        </div>
    </div>
</div>
```

The `.noscroll` modifier prevents background scrolling while trapped.

### $focus.magic()

Programmatically focus elements:

```html
<div x-data="{ 
    steps: [0],
    nextStep() {
        this.steps.push(this.steps.length)
        this.$focus(document.querySelector(`[id="step-${this.steps[this.steps.length - 1]}"]`))
    }
}">
    <template x-for="(step, index) in steps">
        <input 
            :id="'step-' + step"
            type="text" 
            placeholder="Step " + (index + 1)>
    </template>
    <button @click="nextStep">Add Step (focuses new input)</button>
</div>
```

### Focus Loop Pattern for Modals

```html
<div x-data="{ modalOpen: false }">
    <button @click="modalOpen = true">Open Modal</button>
    
    <div x-show="modalOpen" 
         x-trap.noscroll="modalOpen"
         @click.away="modalOpen = false"
         style="position: fixed; inset: 0; background: rgba(0,0,0,0.5); display: flex; align-items: center; justify-content: center;">
        <div style="background: white; padding: 2rem; border-radius: 8px;">
            <h2>Modal Title</h2>
            <input type="text" x-focus="modalOpen" placeholder="Enter something">
            <button @click="modalOpen = false">Close</button>
        </div>
    </div>
</div>
```

## Persist Plugin

Persists data to localStorage or sessionStorage automatically.

### Installation

```html
<script defer src="https://cdn.jsdelivr.net/npm/@alpinejs/persist@3.15.0/dist/cdn.min.js"></script>
<script defer src="https://cdn.jsdelivr.net/npm/alpinejs@3.15.0/dist/cdn.min.js"></script>
```

### Basic Usage

Persist a value with `$persist`:

```html
<div x-data="{ 
    theme: $persist('light').as('theme-preference')
}">
    <button @click="theme = 'light'">Light</button>
    <button @click="theme = 'dark'">Dark</button>
    <button @click="theme = 'system'">System</button>
    
    <p>Current theme: <span x-text="theme"></span></p>
    <p>This persists to localStorage!</p>
</div>
```

### Persist Specific Properties

```html
<div x-data="{ 
    user: $persist({
        name: '',
        preferences: {
            notifications: true,
            newsletter: false
        }
    }).as('user-data')
}">
    <input type="text" x-model="user.name" placeholder="Name">
    <label>
        <input type="checkbox" x-model="user.preferences.notifications">
        Notifications
    </label>
    
    <pre x-text="JSON.stringify(user, null, 2)"></pre>
</div>
```

### Session Storage

Use `.using()` to specify storage:

```html
<div x-data="{ 
    tempData: $persist('').using(Alpine.storage.session).as('session-temp')
}">
    <input type="text" x-model="tempData" placeholder="Session-only data">
    <p>This only persists for the session (cleared on tab close)</p>
</div>
```

### Custom Storage Driver

```javascript
Alpine.storage.custom = {
    get(key) {
        return sessionStorage.getItem(key) || null
    },
    set(key, value) {
        sessionStorage.setItem(key, value)
    }
}
```

```html
<div x-data="{ 
    data: $persist('').using(Alpine.storage.custom).as('custom-storage')
}">
    <input type="text" x-model="data">
</div>
```

### Persist with Default Values

```html
<div x-data="{ 
    settings: $persist({
        theme: 'light',
        language: 'en',
        fontSize: 16
    }).as('app-settings')
}">
    <select x-model="settings.theme">
        <option value="light">Light</option>
        <option value="dark">Dark</option>
    </select>
    
    <select x-model="settings.language">
        <option value="en">English</option>
        <option value="es">Spanish</option>
    </select>
    
    <input type="range" x-model="settings.fontSize" min="12" max="24">
</div>
```

## Mask Plugin

Provides input masking for phone numbers, credit cards, dates, and custom patterns.

### Installation

```html
<script defer src="https://cdn.jsdelivr.net/npm/@alpinejs/mask@3.15.0/dist/cdn.min.js"></script>
<script defer src="https://cdn.jsdelivr.net/npm/alpinejs@3.15.0/dist/cdn.min.js"></script>
```

### Basic Usage

```html
<div x-data="{ phoneNumber: '' }">
    <input 
        type="tel" 
        x-mask="(999) 999-9999" 
        x-model="phoneNumber"
        placeholder="Phone number">
    
    <p>Formatted: <span x-text="phoneNumber"></span></p>
</div>
```

The `9` character represents a digit (0-9).

### Common Masks

#### Phone Numbers

```html
<input type="tel" x-mask="(999) 999-9999" x-model="usPhone">
<input type="tel" x-mask="999-999-9999" x-model="simplePhone">
<input type="tel" x-mask="+1 (999) 999-9999" x-model="intlPhone">
```

#### Credit Cards

```html
<input type="text" x-mask="9999 9999 9999 9999" x-model="cardNumber">
```

#### Dates

```html
<input type="text" x-mask="99/99/9999" x-model="date" placeholder="MM/DD/YYYY">
<input type="text" x-mask="9999-99-99" x-model="isoDate" placeholder="YYYY-MM-DD">
```

#### ZIP Codes

```html
<input type="text" x-mask="99999" x-model="zip">
<input type="text" x-mask="99999-9999" x-model="zipPlus4">
```

#### Time

```html
<input type="text" x-mask="99:99" x-model="time" placeholder="HH:MM">
<input type="text" x-mask="99:99:99" x-model="preciseTime" placeholder="HH:MM:SS">
```

### Dynamic Masks

Change mask based on selection:

```html
<div x-data="{ 
    country: 'us',
    phone: ''
}">
    <select x-model="country">
        <option value="us">United States</option>
        <option value="uk">United Kingdom</option>
        <option value="de">Germany</option>
    </select>
    
    <input 
        type="tel"
        :x-mask="getMask()"
        x-model="phone">
    
    <script>
        function getMask() {
            const masks = {
                us: '(999) 999-9999',
                uk: '99999 999999',
                de: '999 9999999'
            }
            return masks[this.country] || '(999) 999-9999'
        }
    </script>
</div>
```

### Custom Characters

Use `A` for letters, `*` for any character:

```html
<input type="text" x-mask="AAA-999" x-model="code" placeholder="ABC-123">
<input type="text" x-mask="****-****" x-model="pin" placeholder="Password">
```

### Clearing Masked Values

```html
<div x-data="{ maskedValue: '' }">
    <input type="text" x-mask="999-999-9999" x-model="maskedValue">
    <button @click="maskedValue = ''">Clear</button>
    <p>Raw value: <span x-text="maskedValue"></span></p>
</div>
```

## Collapse Plugin

Provides smooth height transitions for collapsible content.

### Installation

```html
<script defer src="https://cdn.jsdelivr.net/npm/@alpinejs/collapse@3.15.0/dist/cdn.min.js"></script>
<script defer src="https://cdn.jsdelivr.net/npm/alpinejs@3.15.0/dist/cdn.min.js"></script>
```

### Basic Usage

```html
<div x-data="{ open: false }">
    <button @click="open = !open">Toggle Content</button>
    
    <div x-show="open" x-collapse>
        <p>This content collapses with smooth height animation</p>
        <p>Multiple lines of content here...</p>
    </div>
</div>
```

### With x-transition

Combine with `x-transition` for opacity effects:

```html
<div x-data="{ open: false }">
    <button @click="open = !open">Toggle</button>
    
    <div x-show="open" 
         x-collapse 
         x-transition.opacity>
        Smooth height + fade transition
    </div>
</div>
```

### Accordion Pattern

```html
<div x-data="{ active: null }">
    <div class="accordion-item">
        <button 
            @click="active = active === 0 ? null : 0"
            :class="{ 'active': active === 0 }">
            Section 1
        </button>
        <div x-show="active === 0" x-collapse>
            <p>Content for section 1</p>
        </div>
    </div>
    
    <div class="accordion-item">
        <button 
            @click="active = active === 1 ? null : 1"
            :class="{ 'active': active === 1 }">
            Section 2
        </button>
        <div x-show="active === 1" x-collapse>
            <p>Content for section 2</p>
        </div>
    </div>
    
    <div class="accordion-item">
        <button 
            @click="active = active === 2 ? null : 2"
            :class="{ 'active': active === 2 }">
            Section 3
        </button>
        <div x-show="active === 2" x-collapse>
            <p>Content for section 3</p>
        </div>
    </div>
</div>
```

## Intersect Plugin

Detects when elements enter/leave the viewport (Intersection Observer).

### Installation

```html
<script defer src="https://cdn.jsdelivr.net/npm/@alpinejs/intersect@3.15.0/dist/cdn.min.js"></script>
<script defer src="https://cdn.jsdelivr.net/npm/alpinejs@3.15.0/dist/cdn.min.js"></script>
```

### Basic Usage

```html
<div x-data="{ visible: false }">
    <div x-intersect="visible = true">
        <p x-show="visible" x-transition.fade>
            I'm in the viewport!
        </p>
    </div>
</div>
```

### Once Modifier

Trigger only once when element enters viewport:

```html
<div x-data="{ animated: false }">
    <div x-intersect.once="animated = true"
         :class="{ 'fade-in': animated }">
        Animates once when scrolled into view
    </div>
</div>
```

### Threshold Option

Trigger at specific visibility threshold:

```html
<div x-data="{ loaded: false }">
    <div x-intersect.threshold.50="loaded = true">
        <p x-show="loaded">50% of this element is visible</p>
    </div>
</div>
```

Threshold values: 0, 0.25, 0.5, 0.75, 1

### Lazy Loading Images

```html
<div x-data="{ loaded: false }">
    <img 
        x-intersect.once="loaded = true"
        :src="loaded ? 'https://example.com/image.jpg' : 'data:image/svg+xml,%3Csvg xmlns=\'http://www.w3.org/2000/svg\' width=\'200\' height=\'200\'%3E%3C/svg%3E'"
        alt="Lazy loaded image">
</div>
```

### Infinite Scroll

```html
<div x-data="{ 
    page: 1,
    loading: false,
    items: [],
    
    async loadMore() {
        if (this.loading) return
        this.loading = true
        
        // Simulate API call
        await new Promise(r => setTimeout(r, 500))
        
        for (let i = 0; i < 10; i++) {
            this.items.push(`Item ${this.page * 10 + i}`)
        }
        
        this.page++
        this.loading = false
    }
}">
    <ul>
        <template x-for="item in items">
            <li x-text="item"></li>
        </template>
    </ul>
    
    <div x-intersect="loadMore()">
        <p x-show="loading">Loading...</p>
    </div>
</div>
```

## Resize Plugin

Detects element size changes and provides dimensions.

### Installation

```html
<script defer src="https://cdn.jsdelivr.net/npm/@alpinejs/resize@3.15.0/dist/cdn.min.js"></script>
<script defer src="https://cdn.jsdelivr.net/npm/alpinejs@3.15.0/dist/cdn.min.js"></script>
```

### Basic Usage

```html
<div x-data="{ width: 0, height: 0 }">
    <div 
        x-resize="({ width, height }) => { 
            this.width = width 
            this.height = height 
        }"
        style="border: 1px solid #ccc; padding: 1rem;">
        Resize me!
        <p>Width: <span x-text="width"></span></p>
        <p>Height: <span x-text="height"></span></p>
    </div>
</div>
```

### Responsive Behavior

```html
<div x-data="{ 
    isLarge: false,
    isSmall: false
}">
    <div 
        x-resize="({ width }) => {
            this.isLarge = width > 600
            this.isSmall = width < 300
        }">
        <p x-show="isSmall">Small view</p>
        <p x-show="!isSmall && !isLarge">Medium view</p>
        <p x-show="isLarge">Large view</p>
    </div>
</div>
```

## Morph Plugin

Smoothly morphs between different HTML structures.

### Installation

```html
<script defer src="https://cdn.jsdelivr.net/npm/@alpinejs/morph@3.15.0/dist/cdn.min.js"></script>
<script defer src="https://cdn.jsdelivr.net/npm/alpinejs@3.15.0/dist/cdn.min.js"></script>
```

### Basic Usage

```html
<div x-data="{ 
    items: [
        { id: 1, text: 'First' },
        { id: 2, text: 'Second' }
    ]
}">
    <ul x-morph.text>
        <template x-for="item in items">
            <li :key="item.id" x-text="item.text"></li>
        </template>
    </ul>
    
    <button @click="items.push({ id: Date.now(), text: 'New Item' })">
        Add Item
    </button>
</div>
```

### Morph Modes

```html
<div x-data="{ view: 'list' }">
    <button @click="view = 'list'">List View</button>
    <button @click="view = 'grid'">Grid View</button>
    
    <div x-morph>
        <template x-if="view === 'list'">
            <ul>
                <li>List item 1</li>
                <li>List item 2</li>
            </ul>
        </template>
        
        <template x-if="view === 'grid'">
            <div style="display: grid; grid-template-columns: 1fr 1fr;">
                <div>Grid item 1</div>
                <div>Grid item 2</div>
            </div>
        </template>
    </div>
</div>
```

Modes:
- `x-morph`: Full morph (default)
- `x-morph.text`: Only text content changes
- `x-morph.style`: Only style changes
- `x-morph.class`: Only class changes

## Sort Plugin

Provides sortable lists with drag-and-drop.

### Installation

```html
<script defer src="https://cdn.jsdelivr.net/npm/@alpinejs/sort@3.15.0/dist/cdn.min.js"></script>
<script defer src="https://cdn.jsdelivr.net/npm/alpinejs@3.15.0/dist/cdn.min.js"></script>
```

### Basic Usage

```html
<div x-data="{ 
    items: ['Apple', 'Banana', 'Cherry', 'Date']
}">
    <ul x-sort="items">
        <template x-for="(item, index) in items" :key="index">
            <li draggable="true" x-text="item"></li>
        </template>
    </ul>
</div>
```

### With Objects

```html
<div x-data="{ 
    todos: [
        { id: 1, text: 'Learn Alpine', done: false },
        { id: 2, text: 'Build something', done: false },
        { id: 3, text: 'Share it', done: false }
    ]
}">
    <ul x-sort="todos">
        <template x-for="todo in todos" :key="todo.id">
            <li draggable="true">
                <input type="checkbox" x-model="todo.done">
                <span :class="{ 'line-through': todo.done }" x-text="todo.text"></span>
            </li>
        </template>
    </ul>
</div>
```

## Plugin Combination Examples

### Form with Mask and Persist

```html
<div x-data="{ 
    contact: $persist({
        name: '',
        phone: '',
        email: ''
    }).as('contact-form')
}">
    <form @submit.prevent="alert('Submitted!')">
        <input type="text" x-model="contact.name" placeholder="Name">
        <input type="tel" x-mask="(999) 999-9999" x-model="contact.phone" placeholder="Phone">
        <input type="email" x-model="contact.email" placeholder="Email">
        <button type="submit">Submit</button>
    </form>
    
    <p>Form data persists across page reloads!</p>
</div>
```

### Modal with Focus Trap and Persist

```html
<div x-data="{ 
    modalOpen: $persist(false).as('modal-state'),
    formData: { value: '' }
}">
    <button @click="modalOpen = true">Open Modal</button>
    
    <div x-show="modalOpen" 
         x-trap.noscroll="modalOpen"
         style="position: fixed; inset: 0; background: rgba(0,0,0,0.5); display: flex; align-items: center; justify-content: center;">
        <div style="background: white; padding: 2rem;">
            <input type="text" x-model="formData.value" x-focus="modalOpen">
            <button @click="modalOpen = false">Close</button>
        </div>
    </div>
</div>
```

## Available Plugins

Official Alpine.js plugins:
- `@alpinejs/focus` - Focus management and trapping
- `@alpinejs/persist` - Persistent state storage
- `@alpinejs/mask` - Input masking
- `@alpinejs/collapse` - Smooth height transitions
- `@alpinejs/intersect` - Intersection observer
- `@alpinejs/resize` - Element resize detection
- `@alpinejs/morph` - DOM morphing
- `@alpinejs/sort` - Sortable lists

All plugins follow semantic versioning and are compatible with Alpine 3.x.
