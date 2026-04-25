# Common Components

This reference provides complete, production-ready component patterns built with Alpine.js. Each component includes accessibility considerations and best practices.

## Dropdown Component

### Basic Dropdown

```html
<div x-data="{ open: false }" class="relative">
    <button 
        @click="open = !open"
        @click.away="open = false"
        :aria-expanded="open"
        aria-haspopup="true"
        class="px-4 py-2 bg-blue-500 text-white rounded">
        Menu
        <span x-text="open ? '↑' : '↓'"></span>
    </button>
    
    <div 
        x-show="open" 
        x-transition.opacity
        @click.away="open = false"
        class="absolute mt-2 w-48 bg-white shadow-lg rounded-lg z-50">
        <a href="#" class="block px-4 py-2 hover:bg-gray-100">Option 1</a>
        <a href="#" class="block px-4 py-2 hover:bg-gray-100">Option 2</a>
        <a href="#" class="block px-4 py-2 hover:bg-gray-100">Option 3</a>
    </div>
</div>
```

### Select Dropdown with Search

```html
<div x-data="{ 
    open: false,
    selected: '',
    query: '',
    options: ['Apple', 'Banana', 'Cherry', 'Date', 'Elderberry'],
    
    get filtered() {
        if (!this.query) return this.options
        return this.options.filter(opt => 
            opt.toLowerCase().includes(this.query.toLowerCase())
        )
    },
    
    select(option) {
        this.selected = option
        this.query = ''
        this.open = false
    }
}" class="relative">
    
    <button 
        @click="open = !open"
        @click.away="open = false"
        :aria-expanded="open"
        class="w-full px-4 py-2 text-left border rounded">
        <span x-text="selected || 'Select...'"></span>
    </button>
    
    <div 
        x-show="open"
        x-transition
        class="absolute mt-1 w-full bg-white border shadow-lg rounded z-50">
        <input 
            type="text" 
            x-model="query"
            @focus.prevent="open = true"
            placeholder="Search..."
            class="w-full px-4 py-2 border-b">
        
        <ul class="max-h-48 overflow-auto">
            <template x-for="option in filtered">
                <li 
                    @click="select(option)"
                    :class="{ 'bg-blue-50': selected === option }"
                    class="px-4 py-2 cursor-pointer hover:bg-gray-100"
                    x-text="option"></li>
            </template>
            <li x-show="filtered.length === 0" class="px-4 py-2 text-gray-500">
                No results found
            </li>
        </ul>
    </div>
</div>
```

## Modal Component

### Basic Modal

```html
<div x-data="{ open: false }">
    <button @click="open = true" class="px-4 py-2 bg-blue-500 text-white rounded">
        Open Modal
    </button>
    
    <!-- Backdrop -->
    <div 
        x-show="open"
        x-transition.opacity
        @click="open = false"
        class="fixed inset-0 bg-black bg-opacity-50 z-40"></div>
    
    <!-- Modal -->
    <div 
        x-show="open"
        x-transition:enter.start="opacity: 0; transform: scale(0.95)"
        x-transition:enter.end="opacity: 1; transform: scale(1)"
        x-transition:leave.start="opacity: 1; transform: scale(1)"
        x-transition:leave.end="opacity: 0; transform: scale(0.95)"
        class="fixed top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-full max-w-md bg-white rounded-lg shadow-xl z-50"
        role="dialog"
        aria-modal="true">
        
        <div class="p-6">
            <h2 class="text-xl font-bold mb-4">Modal Title</h2>
            <p class="mb-4">Modal content goes here.</p>
            
            <div class="flex justify-end space-x-2">
                <button 
                    @click="open = false"
                    class="px-4 py-2 border rounded">
                    Cancel
                </button>
                <button 
                    @click="open = false"
                    class="px-4 py-2 bg-blue-500 text-white rounded">
                    Confirm
                </button>
            </div>
        </div>
    </div>
</div>
```

### Modal with Focus Trap (using Focus Plugin)

```html
<!-- Include focus plugin first -->
<script defer src="https://cdn.jsdelivr.net/npm/@alpinejs/focus@3.15.0/dist/cdn.min.js"></script>
<script defer src="https://cdn.jsdelivr.net/npm/alpinejs@3.15.0/dist/cdn.min.js"></script>

<div x-data="{ open: false }">
    <button @click="open = true">Open Modal</button>
    
    <div 
        x-show="open"
        x-trap.noscroll="open"
        class="fixed inset-0 flex items-center justify-center z-50">
        
        <!-- Backdrop -->
        <div @click="open = false" class="absolute inset-0 bg-black bg-opacity-50"></div>
        
        <!-- Modal -->
        <div class="relative bg-white rounded-lg p-6 w-full max-w-md">
            <h2 class="text-xl font-bold mb-4">Focused Modal</h2>
            
            <input type="text" 
                   x-focus="open"
                   placeholder="Focus trapped here"
                   class="w-full px-3 py-2 border rounded mb-4">
            
            <button @click="open = false" class="px-4 py-2 bg-blue-500 text-white rounded">
                Close
            </button>
        </div>
    </div>
</div>
```

### Confirmation Modal

```html
<div x-data="{ 
    open: false,
    callback: null,
    
    confirm() {
        if (this.callback) this.callback(true)
        this.open = false
    },
    
    cancel() {
        if (this.callback) this.callback(false)
        this.open = false
    }
}">
    <button @click="open = true; callback = (confirmed) => console.log(confirmed)">
        Delete Item
    </button>
    
    <div x-show="open" class="fixed inset-0 flex items-center justify-center z-50">
        <div @click="open = false" class="absolute inset-0 bg-black bg-opacity-50"></div>
        
        <div class="relative bg-white rounded-lg p-6 w-full max-w-sm">
            <h2 class="text-xl font-bold mb-2">Confirm Delete</h2>
            <p class="mb-4 text-gray-600">Are you sure you want to delete this item?</p>
            
            <div class="flex justify-end space-x-2">
                <button @click="cancel" class="px-4 py-2 border rounded">
                    Cancel
                </button>
                <button @click="confirm" class="px-4 py-2 bg-red-500 text-white rounded">
                    Delete
                </button>
            </div>
        </div>
    </div>
</div>
```

## Tabs Component

### Basic Tabs

```html
<div x-data="{ activeTab: 'tab1' }" class="tabs">
    <!-- Tab Headers -->
    <div class="border-b">
        <button 
            @click="activeTab = 'tab1'"
            :class="{ 'active': activeTab === 'tab1' }"
            class="px-4 py-2 border-b-2">
            Tab 1
        </button>
        <button 
            @click="activeTab = 'tab2'"
            :class="{ 'active': activeTab === 'tab2' }"
            class="px-4 py-2 border-b-2">
            Tab 2
        </button>
        <button 
            @click="activeTab = 'tab3'"
            :class="{ 'active': activeTab === 'tab3' }"
            class="px-4 py-2 border-b-2">
            Tab 3
        </button>
    </div>
    
    <!-- Tab Content -->
    <div class="p-4">
        <div x-show="activeTab === 'tab1'" x-transition.fade>
            <h3>Tab 1 Content</h3>
            <p>Content for the first tab.</p>
        </div>
        
        <div x-show="activeTab === 'tab2'" x-transition.fade>
            <h3>Tab 2 Content</h3>
            <p>Content for the second tab.</p>
        </div>
        
        <div x-show="activeTab === 'tab3'" x-transition.fade>
            <h3>Tab 3 Content</h3>
            <p>Content for the third tab.</p>
        </div>
    </div>
</div>
```

### Dynamic Tabs with Data

```html
<div x-data="{ 
    activeTab: 'overview',
    tabs: [
        { id: 'overview', label: 'Overview' },
        { id: 'details', label: 'Details' },
        { id: 'settings', label: 'Settings' }
    ]
}" class="tabs">
    <div class="border-b">
        <template x-for="tab in tabs">
            <button 
                @click="activeTab = tab.id"
                :class="{ 'active': activeTab === tab.id }"
                class="px-4 py-2 border-b-2"
                x-text="tab.label"></button>
        </template>
    </div>
    
    <div class="p-4">
        <template x-for="tab in tabs">
            <div 
                x-show="activeTab === tab.id" 
                x-transition.fade
                :id="'tab-' + tab.id">
                <h3 x-text="tab.label"></h3>
                <p>Content for <span x-text="tab.label"></span></p>
            </div>
        </template>
    </div>
</div>
```

## Accordion Component

### Single Open Accordion

```html
<div x-data="{ active: null }" class="accordion">
    <div class="accordion-item" v-for="(item, index) in items">
        <button 
            @click="active = active === index ? null : index"
            :aria-expanded="active === index"
            :class="{ 'active': active === index }"
            class="w-full px-4 py-3 text-left font-semibold">
            <span x-text="item.title"></span>
            <span x-text="active === index ? '−' : '+'" class="float-right"></span>
        </button>
        
        <div 
            x-show="active === index"
            x-collapse
            class="px-4 py-3 border-t">
            <p x-text="item.content"></p>
        </div>
    </div>
</div>

<script>
const items = [
    { title: 'Section 1', content: 'Content for section 1...' },
    { title: 'Section 2', content: 'Content for section 2...' },
    { title: 'Section 3', content: 'Content for section 3...' }
]
</script>
```

### Multiple Open Accordion

```html
<div x-data="{ 
    items: [
        { id: 1, open: false, title: 'Section 1', content: 'Content 1' },
        { id: 2, open: false, title: 'Section 2', content: 'Content 2' },
        { id: 3, open: false, title: 'Section 3', content: 'Content 3' }
    ]
}" class="accordion">
    
    <template x-for="item in items">
        <div class="accordion-item border-b">
            <button 
                @click="item.open = !item.open"
                :aria-expanded="item.open"
                class="w-full px-4 py-3 text-left font-semibold">
                <span x-text="item.title"></span>
                <span x-text="item.open ? '−' : '+'" class="float-right"></span>
            </button>
            
            <div 
                x-show="item.open"
                x-collapse
                class="px-4 py-3">
                <p x-text="item.content"></p>
            </div>
        </div>
    </template>
</div>
```

## Toast Notifications

### Simple Toast

```html
<div x-data="{ 
    toasts: [],
    
    addToast(message, type = 'info') {
        const id = Date.now()
        this.toasts.push({ id, message, type })
        
        setTimeout(() => {
            this.toasts = this.toasts.filter(t => t.id !== id)
        }, 3000)
    }
}" style="position: fixed; top: 20px; right: 20px; z-index: 1000;">
    
    <template x-for="toast in toasts">
        <div 
            x-show="true"
            x-transition:enter.start="opacity: 0; transform: translateX(100%)"
            x-transition:enter.end="opacity: 1; transform: translateX(0)"
            x-transition:leave.start="opacity: 1; transform: translateX(0)"
            x-transition:leave.end="opacity: 0; transform: translateX(100%)"
            :class="{
                'bg-green-500': toast.type === 'success',
                'bg-red-500': toast.type === 'error',
                'bg-blue-500': toast.type === 'info'
            }"
            class="text-white px-6 py-3 rounded shadow-lg mb-2">
            <span x-text="toast.message"></span>
        </div>
    </template>
</div>

<!-- Usage -->
<button @click="$dispatch('addToast', { message: 'Success!', type: 'success' })">
    Show Success Toast
</button>
```

### Advanced Toast with Actions

```html
<div x-data="{ 
    toasts: [],
    
    addToast(options) {
        const id = Date.now()
        this.toasts.push({ 
            id, 
            message: options.message,
            type: options.type || 'info',
            action: options.action,
            actionLabel: options.actionLabel
        })
        
        if (!options.persistent) {
            setTimeout(() => {
                this.removeToast(id)
            }, options.duration || 3000)
        }
    },
    
    removeToast(id) {
        this.toasts = this.toasts.filter(t => t.id !== id)
    }
}" style="position: fixed; top: 20px; right: 20px; z-index: 1000;">
    
    <template x-for="toast in toasts">
        <div 
            x-transition.opacity
            :class="{
                'bg-green-500': toast.type === 'success',
                'bg-red-500': toast.type === 'error',
                'bg-blue-500': toast.type === 'info',
                'bg-yellow-500': toast.type === 'warning'
            }"
            class="text-white px-6 py-4 rounded shadow-lg mb-2 min-w-80 max-w-sm">
            
            <div class="flex items-start justify-between">
                <span class="flex-1" x-text="toast.message"></span>
                <button @click="removeToast(toast.id)" class="ml-4 opacity-75 hover:opacity-100">
                    ×
                </button>
            </div>
            
            <template x-if="toast.action">
                <button 
                    @click="toast.action(); removeToast(toast.id)"
                    class="mt-3 w-full px-4 py-2 bg-white text-gray-800 rounded hover:bg-gray-100">
                    <span x-text="toast.actionLabel || 'Action'"></span>
                </button>
            </template>
        </div>
    </template>
</div>

<!-- Usage -->
<button @click="$dispatch('addToast', { 
    message: 'Item deleted',
    type: 'info',
    actionLabel: 'Undo',
    action: () => console.log('Undo delete')
})">
    Delete with Undo
</button>
```

## Carousel/Slider

### Basic Carousel

```html
<div x-data="{ 
    current: 0,
    slides: [
        { title: 'Slide 1', content: 'First slide content' },
        { title: 'Slide 2', content: 'Second slide content' },
        { title: 'Slide 3', content: 'Third slide content' }
    ],
    
    next() {
        this.current = (this.current + 1) % this.slides.length
    },
    
    prev() {
        this.current = (this.current - 1 + this.slides.length) % this.slides.length
    }
}" class="relative w-full max-w-2xl mx-auto">
    
    <!-- Slides -->
    <div class="overflow-hidden rounded-lg">
        <template x-for="(slide, index) in slides">
            <div 
                x-show="current === index"
                x-transition:enter.start="opacity: 0; transform: translateX(100%)"
                x-transition:enter.end="opacity: 1; transform: translateX(0)"
                x-transition:leave.start="opacity: 1; transform: translateX(0)"
                x-transition:leave.end="opacity: 0; transform: translateX(-100%)"
                class="absolute inset-0 p-8 bg-gradient-to-r from-blue-500 to-purple-500 text-white">
                <h3 class="text-2xl font-bold" x-text="slide.title"></h3>
                <p class="mt-2" x-text="slide.content"></p>
            </div>
        </template>
    </div>
    
    <!-- Navigation -->
    <button 
        @click="prev"
        class="absolute left-2 top-1/2 transform -translate-y-1/2 bg-white bg-opacity-50 hover:bg-opacity-75 rounded-full p-2">
        ←
    </button>
    
    <button 
        @click="next"
        class="absolute right-2 top-1/2 transform -translate-y-1/2 bg-white bg-opacity-50 hover:bg-opacity-75 rounded-full p-2">
        →
    </button>
    
    <!-- Indicators -->
    <div class="flex justify-center mt-4 space-x-2">
        <template x-for="(slide, index) in slides">
            <button 
                @click="current = index"
                :class="{ 'bg-white': current === index, 'bg-white bg-opacity-50': current !== index }"
                class="w-3 h-3 rounded-full transition-all"></button>
        </template>
    </div>
</div>
```

## Toggle Switch

### Basic Toggle

```html
<div x-data="{ enabled: false }" class="flex items-center">
    <button 
        @click="enabled = !enabled"
        role="switch"
        :aria-checked="enabled"
        :class="{ 'bg-green-500': enabled, 'bg-gray-300': !enabled }"
        class="relative w-12 h-6 rounded-full transition-colors">
        <span 
            :class="{ 'translate-x-6': enabled, 'translate-x-0': !enabled }"
            class="absolute top-1 left-1 w-4 h-4 bg-white rounded-full transition-transform">
        </span>
    </button>
    <span class="ml-3" x-text="enabled ? 'On' : 'Off'"></span>
</div>
```

## Progress Bar

### Animated Progress

```html
<div x-data="{ progress: 0 }" class="w-full max-w-md">
    <div class="flex justify-between mb-1">
        <span>Progress</span>
        <span x-text="progress + '%'"></span>
    </div>
    
    <div class="w-full bg-gray-200 rounded-full h-2.5">
        <div 
            :style="'width: ' + progress + '%'"
            x-transition:enter="transition-all duration-300 ease-out"
            class="bg-blue-500 h-2.5 rounded-full"></div>
    </div>
    
    <button @click="progress += 10" :disabled="progress >= 100">
        Increment
    </button>
    <button @click="progress = 0">Reset</button>
</div>
```

## Loading Spinner

### Inline Loader

```html
<div x-data="{ loading: false }">
    <button 
        @click="loading = true; setTimeout(() => loading = false, 2000)"
        :disabled="loading">
        
        <span x-show="!loading">Click me</span>
        
        <span x-show="loading" class="inline-flex items-center">
            <svg class="animate-spin h-5 w-5 mr-2" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            Loading...
        </span>
    </button>
</div>
```

## Accessibility Tips

1. **Use ARIA attributes**: `aria-expanded`, `aria-haspopup`, `aria-modal`
2. **Focus management**: Use Focus plugin for modals and dropdowns
3. **Keyboard navigation**: Ensure all interactive elements are keyboard accessible
4. **Announce changes**: Use `aria-live` regions for dynamic content updates
5. **Semantic HTML**: Use proper tags (`<button>`, `<nav>`, `<dialog>`)

See [Advanced Patterns](10-advanced-patterns.md) for more complex component architectures.
