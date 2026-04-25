# Transitions and Effects

Alpine.js provides built-in transition support and reactive effects for creating smooth animations without external animation libraries.

## x-transition

The `x-transition` directive adds CSS transitions to elements when they appear or disappear from the DOM.

### Basic Usage with x-show

```html
<div x-data="{ open: false }">
    <button @click="open = !open">Toggle</button>
    
    <div x-show="open" x-transition>
        Content fades and slides in/out
    </div>
</div>
```

By default, `x-transition` applies a fade + slide animation.

### Transition with x-if

For elements conditionally rendered with `x-if`:

```html
<div x-data="{ show: false }">
    <button @click="show = !show">Toggle</button>
    
    <template x-if="show">
        <div x-transition>Appears with transition</div>
    </template>
</div>
```

### Transition Modifiers

#### Duration Control

```html
<div x-data="{ open: false }">
    <button @click="open = !open">Toggle</button>
    
    <!-- 500ms transition -->
    <div x-show="open" x-transition.duration.500ms>Faster/slower transition</div>
</div>
```

Set different durations for enter and leave:

```html
<div x-show="open" 
     x-transition:enter.duration.200ms
     x-transition:leave.duration.500ms">
    Different enter/leave speeds
</div>
```

#### Opacity Only

```html
<div x-data="{ open: false }">
    <button @click="open = !open">Toggle</button>
    
    <!-- Fade only, no slide -->
    <div x-show="open" x-transition.opacity>Fade in/out</div>
</div>
```

#### None (No Transition)

```html
<div x-show="open" x-transition.none>
    No transition effect
</div>
```

### Custom Transition Stages

Alpine applies CSS classes during transitions that you can customize:

**Enter stages:** `enter-start`, `enter-end`, `enter-active`
**Leave stages:** `leave-start`, `leave-end`, `leave-active`

```html
<div x-data="{ open: false }">
    <button @click="open = !open">Toggle</button>
    
    <div x-show="open" 
         x-transition:enter.start="opacity: 0; transform: translateY(-10px)"
         x-transition:enter.end="opacity: 1; transform: translateY(0)">
        Custom enter animation
    </div>
</div>
```

### Full Custom Transition Example

```html
<style>
    .fade-slide-enter-start {
        opacity: 0;
        transform: translateY(-20px);
    }
    .fade-slide-enter-end {
        opacity: 1;
        transform: translateY(0);
    }
    .fade-slide-leave-start {
        opacity: 1;
    }
    .fade-slide-leave-end {
        opacity: 0;
        transform: translateY(-20px);
    }
</style>

<div x-data="{ open: false }">
    <button @click="open = !open">Toggle</button>
    
    <div x-show="open" 
         x-transition:enter.start.classes="fade-slide-enter-start"
         x-transition:enter.end.classes="fade-slide-enter-end"
         x-transition:leave.start.classes="fade-slide-leave-start"
         x-transition:leave.end.classes="fade-slide-leave-end">
        Fully custom transition
    </div>
</div>
```

### Transition with x-for Lists

When animating list items, always use `:key` for proper transitions:

```html
<div x-data="{ 
    items: ['Apple', 'Banana', 'Cherry'],
    query: ''
}">
    <input type="text" x-model="query" placeholder="Filter...">
    
    <ul>
        <template x-for="item in filteredItems" :key="item">
            <li x-transition x-text="item"></li>
        </template>
    </ul>
</div>

<script>
    // In actual implementation, compute filteredItems based on query
</script>
```

### Staggered Transitions

Create staggered animations for list items:

```html
<div x-data="{ 
    items: ['One', 'Two', 'Three'],
    show: false
}">
    <button @click="show = !show">Toggle List</button>
    
    <template x-if="show">
        <ul>
            <template x-for="(item, index) in items" :key="index">
                <li 
                    x-transition
                    :style="{ transitionDelay: (index * 100) + 'ms' }"
                    x-text="item"></li>
            </template>
        </ul>
    </template>
</div>
```

## x-effect

The `x-effect` directive runs a function whenever any reactive dependency it accesses changes.

### Basic Usage

```html
<div x-data="{ count: 0 }">
    <button @click="count++">Increment</button>
    
    <script x-effect="
        console.log('Count changed to:', count)
        // This runs whenever 'count' changes
    "></script>
</div>
```

### Side Effects with Cleanup

`x-effect` supports cleanup functions (like React's useEffect):

```html
<div x-data="{ 
    value: '',
    subscription: null
}">
    <input type="text" x-model="value">
    
    <script x-effect="() => {
        // Setup
        console.log('Watching value:', value)
        
        // Cleanup (runs before next effect execution)
        return () => {
            console.log('Cleanup: old value was', value)
        }
    }"></script>
</div>
```

### Debounced API Calls

Use `x-effect` for debounced search or auto-save features:

```html
<div x-data="{
    query: '',
    results: [],
    
    async fetchResults() {
        if (!this.query) {
            this.results = []
            return
        }
        
        // Simulate API call
        console.log('Searching for:', this.query)
        this.results = [
            { id: 1, name: 'Result 1 for ' + this.query },
            { id: 2, name: 'Result 2 for ' + this.query }
        ]
    }
}">
    <input type="text" x-model="query" placeholder="Search...">
    
    <script x-effect="() => {
        // Debounce the search
        const timeout = setTimeout(() => {
            $dispatch.fetchResults()
        }, 300)
        
        // Cleanup: clear timeout if effect re-runs
        return () => clearTimeout(timeout)
    }"></script>
    
    <ul>
        <template x-for="result in results">
            <li x-text="result.name"></li>
        </template>
    </ul>
</div>
```

### DOM Manipulation on Data Change

```html
<div x-data="{ focused: false }">
    <input 
        type="text" 
        @focus="focused = true" 
        @blur="focused = false"
        :class="{ 'focused': focused }">
    
    <script x-effect="() => {
        const input = $el.querySelector('input')
        if (focused && input) {
            input.scrollIntoView({ behavior: 'smooth', block: 'center' })
        }
    }"></script>
</div>
```

## x-cloak

Prevents Alpine templates from "flashing" before JavaScript loads.

### Usage

Add CSS rule to hide elements with `x-cloak`:

```html
<style>
    [x-cloak] { display: none !important; }
</style>

<div x-data="{ loaded: false }" x-cloak>
    <div x-show="loaded">Content appears after Alpine loads</div>
</div>
```

Alpine automatically removes the `x-cloak` attribute once initialized.

### Use Cases

- Prevent FOUC (Flash of Unstyled Content)
- Hide skeleton/loading states until content is ready
- Avoid showing empty templates before data loads

## Transition Timing Functions

Customize animation easing with CSS:

```html
<style>
    .ease-in { transition-timing-function: cubic-bezier(0.4, 0, 1, 1); }
    .ease-out { transition-timing-function: cubic-bezier(0, 0, 0.2, 1); }
    .ease-in-out { transition-timing-function: cubic-bezier(0.4, 0, 0.2, 1); }
</style>

<div x-data="{ open: false }">
    <button @click="open = !open">Toggle</button>
    
    <div x-show="open" 
         x-transition
         class="ease-out"
         style="transition-duration: 300ms;">
        Smooth easing transition
    </div>
</div>
```

## Common Transition Patterns

### Modal with Backdrop

```html
<div x-data="{ modalOpen: false }">
    <button @click="modalOpen = true">Open Modal</button>
    
    <!-- Backdrop -->
    <div x-show="modalOpen" 
         x-transition.opacity
         @click="modalOpen = false"
         style="position: fixed; inset: 0; background: rgba(0,0,0,0.5); z-index: 10;">
    </div>
    
    <!-- Modal -->
    <div x-show="modalOpen"
         x-transition:start="opacity: 0; transform: scale(0.95)"
         x-transition:end="opacity: 1; transform: scale(1)"
         style="position: fixed; top: 50%; left: 50%; transform: translate(-50%, -50%); background: white; padding: 2rem; border-radius: 8px; z-index: 20;">
        <h2>Modal Title</h2>
        <p>Modal content here</p>
        <button @click="modalOpen = false">Close</button>
    </div>
</div>
```

### Collapsible Section

```html
<div x-data="{ expanded: false }">
    <button @click="expanded = !expanded">Toggle Details</button>
    
    <div x-show="expanded" 
         x-transition:enter.start="height: 0; opacity: 0"
         x-transition:enter.end="height: auto; opacity: 1"
         x-transition:leave.start="height: auto; opacity: 1"
         x-transition:leave.end="height: 0; opacity: 0"
         style="overflow: hidden; transition: height 0.3s ease, opacity 0.3s ease;">
        <div style="padding: 1rem;">
            Collapsible content here
        </div>
    </div>
</div>
```

### Toast Notification

```html
<div x-data="{ showToast: false, message: '' }" style="position: relative;">
    <button @click="message = 'Action completed!'; showToast = true">Show Toast</button>
    
    <div x-show="showToast"
         x-transition:enter.start="opacity: 0; transform: translateY(20px)"
         x-transition:enter.end="opacity: 1; transform: translateY(0)"
         x-transition:leave.start="opacity: 1; transform: translateY(0)"
         x-transition:leave.end="opacity: 0; transform: translateY(20px)"
         style="position: absolute; bottom: 0; left: 50%; transform: translateX(-50%); 
                background: #333; color: white; padding: 1rem 2rem; border-radius: 4px;">
        <span x-text="message"></span>
    </div>
    
    <script x-init="$watch('showToast', value => {
        if (value) {
            setTimeout(() => showToast = false, 3000)
        }
    })"></script>
</div>
```

### Tab Content Transitions

```html
<div x-data="{ activeTab: 'tab1' }">
    <button @click="activeTab = 'tab1'" :class="{ 'active': activeTab === 'tab1' }">Tab 1</button>
    <button @click="activeTab = 'tab2'" :class="{ 'active': activeTab === 'tab2' }">Tab 2</button>
    <button @click="activeTab = 'tab3'" :class="{ 'active': activeTab === 'tab3' }">Tab 3</button>
    
    <div x-show="activeTab === 'tab1'" x-transition>Tab 1 Content</div>
    <div x-show="activeTab === 'tab2'" x-transition>Tab 2 Content</div>
    <div x-show="activeTab === 'tab3'" x-transition>Tab 3 Content</div>
</div>
```

## Performance Tips

1. **Use `x-transition.opacity`** for simpler fade animations (more performant)
2. **Avoid animating width/height** - use `max-height` or CSS transforms instead
3. **Use `transform` and `opacity`** for GPU-accelerated animations
4. **Limit transition duration** to 200-500ms for best UX
5. **Combine with `x-cloak`** to prevent unanimated initial render

## Browser Compatibility

Alpine's transitions use standard CSS transitions and transforms, supported in all modern browsers:

- Chrome/Edge: Full support
- Firefox: Full support  
- Safari: Full support (including iOS Safari)
- IE11: Limited support (no `x-transition`, but other directives work)

For older browser support, consider providing fallback styles or using polyfills.
