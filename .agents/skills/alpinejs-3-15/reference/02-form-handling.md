# Form Handling

Alpine.js provides powerful two-way data binding with `x-model` for seamless form handling, including validation, computed properties, and complex form patterns.

## x-model Basics

The `x-model` directive creates two-way binding between form inputs and Alpine data.

### Text Inputs

```html
<div x-data="{ name: '' }">
    <input type="text" x-model="name" placeholder="Enter name">
    <p>Hello, <span x-text="name || 'World'"></span>!</p>
</div>
```

### Textarea

```html
<div x-data="{ message: '' }">
    <textarea x-model="message" rows="4"></textarea>
    <p>Character count: <span x-text="message.length"></span></p>
</div>
```

## Input Types and Modifiers

### Number Inputs

Use `.number` modifier to automatically convert input to number:

```html
<div x-data="{ quantity: 0, price: 10 }">
    <input type="number" x-model.number="quantity" min="0" max="100">
    <p>Total: $<span x-text="quantity * price"></span></p>
</div>
```

Without `.number`, the value remains a string.

### Checkbox (Single Boolean)

```html
<div x-data="{ agreed: false }">
    <label>
        <input type="checkbox" x-model="agreed">
        I agree to terms
    </label>
    <p>Status: <span x-text="agreed ? 'Agreed' : 'Not agreed'"></span></p>
</div>
```

### Checkbox (Multiple Selection)

Bind to an array for multiple checkboxes:

```html
<div x-data="{ fruits: ['apple'] }">
    <label>
        <input type="checkbox" value="apple" x-model="fruits"> Apple
    </label>
    <label>
        <input type="checkbox" value="banana" x-model="fruits"> Banana
    </label>
    <label>
        <input type="checkbox" value="cherry" x-model="fruits"> Cherry
    </label>
    <p>Selected: <span x-text="fruits.join(', ')"></span></p>
</div>
```

### Radio Buttons

```html
<div x-data="{ color: 'blue' }">
    <label>
        <input type="radio" value="red" x-model="color"> Red
    </label>
    <label>
        <input type="radio" value="green" x-model="color"> Green
    </label>
    <label>
        <input type="radio" value="blue" x-model="color"> Blue
    </label>
    <p>Selected color: <span x-text="color"></span></p>
</div>
```

### Select Dropdowns

Single selection:

```html
<div x-data="{ fruit: 'apple' }">
    <select x-model="fruit">
        <option value="">Choose...</option>
        <option value="apple">Apple</option>
        <option value="banana">Banana</option>
        <option value="cherry">Cherry</option>
    </select>
    <p>You chose: <span x-text="fruit"></span></p>
</div>
```

Multiple selection (bind to array):

```html
<div x-data="{ fruits: [] }">
    <select x-model="fruits" multiple size="4">
        <option value="apple">Apple</option>
        <option value="banana">Banana</option>
        <option value="cherry">Cherry</option>
    </select>
    <p>Selected: <span x-text="fruits.join(', ')"></span></p>
</div>
```

### Dynamic Options with x-for

```html
<div x-data="{ 
    selected: '',
    options: [
        { id: 1, name: 'Option 1' },
        { id: 2, name: 'Option 2' },
        { id: 3, name: 'Option 3' }
    ]
}">
    <select x-model="selected">
        <option value="">Select...</option>
        <template x-for="option in options">
            <option :value="option.id" x-text="option.name"></option>
        </template>
    </select>
</div>
```

## Model Modifiers

### .lazy

Update on `change` event instead of `input` (updates when input loses focus):

```html
<input type="text" x-model.lazy="value">
```

Useful for reducing update frequency on expensive operations.

### .number

Casts value to number:

```html
<input type="number" x-model.number="quantity">
```

Equivalent to `Number(this.quantity)`.

### .boolean

Converts checkbox value to boolean:

```html
<input type="checkbox" x-model.boolean="flag">
```

Without modifier, checkboxes bound to strings use the input's value attribute.

### .trim

Trims whitespace from input:

```html
<input type="text" x-model.trim="username">
```

## Form Validation

### Basic Validation with Computed Properties

```html
<div x-data="{ 
    email: '',
    get isValid() {
        return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(this.email)
    },
    get error() {
        return this.email && !this.isValid ? 'Invalid email format' : ''
    }
}">
    <input 
        type="email" 
        x-model="email" 
        :class="{ 'error': email && !isValid }"
        placeholder="Enter email">
    
    <p x-show="error" class="error" x-text="error"></p>
    <button :disabled="!isValid" @click="$dispatch('form-valid')">Submit</button>
</div>
```

### Multi-field Validation

```html
<div x-data="{
    form: {
        name: '',
        email: '',
        password: '',
        confirmPassword: ''
    },
    errors: {},
    
    validateField(field) {
        const validations = {
            name: value => value.length >= 2 || 'Name must be at least 2 characters',
            email: value => /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value) || 'Invalid email',
            password: value => value.length >= 8 || 'Password must be 8+ characters',
            confirmPassword: value => value === this.form.password || 'Passwords do not match'
        }
        
        const error = validations[field](this.form[field])
        this.errors[field] = error
        
        return !error
    },
    
    get isValid() {
        return Object.keys(this.errors).every(field => !this.errors[field])
    }
}">
    <form @submit.prevent="isValid && $dispatch('submit')">
        <div>
            <label>Name</label>
            <input 
                type="text" 
                x-model="form.name"
                @blur="validateField('name')"
                :class="{ 'error': errors.name }">
            <span x-show="errors.name" x-text="errors.name"></span>
        </div>
        
        <div>
            <label>Email</label>
            <input 
                type="email" 
                x-model="form.email"
                @blur="validateField('email')"
                :class="{ 'error': errors.email }">
            <span x-show="errors.email" x-text="errors.email"></span>
        </div>
        
        <div>
            <label>Password</label>
            <input 
                type="password" 
                x-model="form.password"
                @blur="validateField('password')"
                :class="{ 'error': errors.password }">
            <span x-show="errors.password" x-text="errors.password"></span>
        </div>
        
        <button type="submit" :disabled="!isValid">Submit</button>
    </form>
</div>
```

### Real-time Validation with $watch

```html
<div x-data="{
    username: '',
    availability: null,
    
    checkAvailability() {
        if (this.username.length < 3) {
            this.availability = null
            return
        }
        
        // Simulate API call
        setTimeout(() => {
            this.availability = Math.random() > 0.5
        }, 500)
    }
}" 
x-init="$watch('username', value => {
    if (value.length >= 3) checkAvailability()
})">
    <input type="text" x-model="username" placeholder="Username">
    
    <span x-show="availability === true" class="success">✓ Available</span>
    <span x-show="availability === false" class="error">✗ Taken</span>
    <span x-show="availability === null && username.length >= 3" class="loading">Checking...</span>
</div>
```

## Form Submission

### Prevent Default and Submit

```html
<div x-data="{ 
    submitted: false,
    submitForm() {
        this.submitted = true
        // Handle form data here
        console.log('Form submitted')
    }
}">
    <form @submit.prevent="submitForm">
        <input type="text" x-model="name" required>
        <button type="submit">Submit</button>
    </form>
    
    <div x-show="submitted" x-transition>
        Thank you for submitting!
    </div>
</div>
```

### Form State Management

```html
<div x-data="{
    form: { name: '', email: '' },
    status: 'idle', // 'idle' | 'submitting' | 'success' | 'error'
    message: '',
    
    async submit() {
        this.status = 'submitting'
        
        try {
            // Simulate API call
            await new Promise(resolve => setTimeout(resolve, 1000))
            
            this.status = 'success'
            this.message = 'Form submitted successfully!'
            this.form = { name: '', email: '' } // Reset form
        } catch (error) {
            this.status = 'error'
            this.message = 'Submission failed. Please try again.'
        }
    }
}">
    <form @submit.prevent="submit">
        <input type="text" x-model="form.name" placeholder="Name" required :disabled="status === 'submitting'">
        <input type="email" x-model="form.email" placeholder="Email" required :disabled="status === 'submitting'">
        
        <button type="submit" :disabled="status === 'submitting'">
            <span x-show="status !== 'submitting'">Submit</span>
            <span x-show="status === 'submitting'">Submitting...</span>
        </button>
    </form>
    
    <div x-show="status === 'success'" class="success" x-text="message"></div>
    <div x-show="status === 'error'" class="error" x-text="message"></div>
</div>
```

## Computed Properties

Use getters in `x-data` for computed values:

```html
<div x-data="{
    firstName: 'John',
    lastName: 'Doe',
    get fullName() {
        return this.firstName + ' ' + this.lastName
    },
    
    items: [1, 2, 3, 4, 5],
    get evenItems() {
        return this.items.filter(n => n % 2 === 0)
    },
    get total() {
        return this.items.reduce((sum, n) => sum + n, 0)
    }
}">
    <p>Name: <span x-text="fullName"></span></p>
    <p>Evens: <span x-text="evenItems.join(', ')"></span></p>
    <p>Total: <span x-text="total"></span></p>
</div>
```

Computed properties are reactive and update automatically when dependencies change.

## Dynamic Forms

### Repeating Form Fields

```html
<div x-data="{
    fields: [{ value: '' }],
    
    addField() {
        this.fields.push({ value: '' })
    },
    
    removeField(index) {
        this.fields.splice(index, 1)
    }
}">
    <template x-for="(field, index) in fields" :key="index">
        <div style="display: flex; gap: 0.5rem; margin-bottom: 0.5rem;">
            <input type="text" x-model="field.value" placeholder="Value">
            <button @click="removeField(index)" type="button" x-show="fields.length > 1">Remove</button>
        </div>
    </template>
    
    <button @click="addField" type="button">Add Field</button>
    
    <pre x-text="JSON.stringify(fields, null, 2)"></pre>
</div>
```

## Form Reset

### Reset to Initial Values

```html
<div x-data="{
    initialForm: { name: '', email: '' },
    form: { name: '', email: '' },
    
    reset() {
        this.form = { ...this.initialForm }
    }
}">
    <form @submit.prevent="$dispatch('submit', { ...form })">
        <input type="text" x-model="form.name">
        <input type="email" x-model="form.email">
        <button type="submit">Submit</button>
        <button type="button" @click="reset">Reset</button>
    </form>
</div>
```

## Advanced Patterns

### Debounced Search Input

```html
<div x-data="{
    query: '',
    results: [],
    searchQuery: '',
    
    async search() {
        if (!this.searchQuery) {
            this.results = []
            return
        }
        
        // Simulate API call
        this.results = [
            { id: 1, name: 'Result for ' + this.searchQuery },
            { id: 2, name: 'Another result' }
        ]
    }
}"
x-init="$watch('query', value => {
    // Debounce search by 300ms
    clearTimeout(this.searchTimeout)
    this.searchTimeout = setTimeout(() => {
        this.searchQuery = value
        this.search()
    }, 300)
})">
    <input type="text" x-model="query" placeholder="Search...">
    
    <ul x-show="results.length > 0">
        <template x-for="result in results">
            <li x-text="result.name"></li>
        </template>
    </ul>
</div>
```

See [Advanced Patterns](10-advanced-patterns.md) for more complex async form patterns.

### Auto-complete with Keyboard Navigation

```html
<div x-data="{
    query: '',
    options: ['Apple', 'Apricot', 'Avocado', 'Banana', 'Blueberry'],
    filtered: [],
    selectedIndex: -1,
    
    get suggestions() {
        this.filtered = this.options.filter(opt => 
            opt.toLowerCase().includes(this.query.toLowerCase())
        )
        return this.filtered
    },
    
    select(index) {
        this.query = this.suggestions[index]
        this.selectedIndex = -1
    },
    
    handleKeydown(e) {
        if (e.key === 'ArrowDown') {
            e.preventDefault()
            this.selectedIndex = Math.min(this.selectedIndex + 1, this.suggestions.length - 1)
        } else if (e.key === 'ArrowUp') {
            e.preventDefault()
            this.selectedIndex = Math.max(this.selectedIndex - 1, -1)
        } else if (e.key === 'Enter' && this.selectedIndex >= 0) {
            e.preventDefault()
            this.select(this.selectedIndex)
        }
    }
}">
    <div style="position: relative;">
        <input 
            type="text" 
            x-model="query" 
            @keydown="handleKeydown"
            placeholder="Type to search...">
        
        <ul x-show="suggestions.length > 0" 
            style="position: absolute; border: 1px solid #ccc; width: 100%; max-height: 200px; overflow-y: auto;">
            <template x-for="(suggestion, index) in suggestions">
                <li 
                    @click="select(index)"
                    :style="{ background: selectedIndex === index ? '#eee' : 'white' }"
                    style="padding: 8px; cursor: pointer;"
                    x-text="suggestion"></li>
            </template>
        </ul>
    </div>
</div>
```

## Tips and Best Practices

1. **Use `.number` modifier** for numeric inputs to avoid string comparison issues
2. **Validate on blur** for better UX than real-time validation on every keystroke
3. **Show loading states** during form submission to prevent double-submission
4. **Preserve form state** when showing errors so users don't lose their input
5. **Use computed properties** for derived values instead of manual calculations
6. **Reset forms properly** by copying initial state, not just clearing fields
