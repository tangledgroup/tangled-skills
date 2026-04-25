# DaisyUI Form Components

This guide covers all form-related components in DaisyUI 5.5 including inputs, selects, checkboxes, radios, ranges, and file inputs.

## Input (Text Fields)

### Basic Input

```html
<input class="input input-bordered" type="text" placeholder="Type here" />
```

### Input Styles

| Style | Class | Description |
|-------|-------|-------------|
| Bordered | `input-bordered` | Default bordered input |
| Ghost | `input-ghost` | No background or border |

### Input Colors

```html
<input class="input input-primary" type="text" placeholder="Primary" />
<input class="input input-secondary" type="text" placeholder="Secondary" />
<input class="input input-accent" type="text" placeholder="Accent" />
<input class="input input-info" type="text" placeholder="Info" />
<input class="input input-success" type="text" placeholder="Success" />
<input class="input input-warning" type="text" placeholder="Warning" />
<input class="input input-error" type="text" placeholder="Error" />
```

### Input Sizes

| Size | Class |
|------|-------|
| Extra Small | `input-xs` |
| Small | `input-sm` |
| Medium | `input-md` |
| Large | `input-lg` |
| Extra Large | `input-xl` |

```html
<input class="input input-sm" type="text" placeholder="Small" />
<input class="input input-md" type="text" placeholder="Medium" />
<input class="input input-lg" type="text" placeholder="Large" />
```

### Input with Icon

```html
<div class="join">
  <button class="join-item btn">https://</button>
  <input class="join-item input" type="text" placeholder="google.com" />
</div>
```

### Input Types

```html
<!-- Text -->
<input class="input" type="text" placeholder="Text input" />

<!-- Email -->
<input class="input" type="email" placeholder="Email address" />

<!-- Password -->
<input class="input" type="password" placeholder="Password" />

<!-- Number -->
<input class="input" type="number" placeholder="Number" />

<!-- Tel -->
<input class="input" type="tel" placeholder="Phone number" />

<!-- URL -->
<input class="input" type="url" placeholder="Website URL" />
```

### Floating Label

```html
<div class="floating-label">
  <span>Username</span>
  <input type="text" placeholder="Enter username" />
</div>
```

## Select (Dropdown)

### Basic Select

```html
<select class="select select-bordered">
  <option disabled selected>Select an option</option>
  <option>Option 1</option>
  <option>Option 2</option>
  <option>Option 3</option>
</select>
```

### Select Styles

```html
<select class="select select-ghost">
  <option>Ghost select</option>
</select>
```

### Select Colors

```html
<select class="select select-primary">
  <option>Primary select</option>
</select>

<select class="select select-success">
  <option>Success select</option>
</select>
```

### Select Sizes

```html
<select class="select select-sm">
  <option>Small</option>
</select>

<select class="select select-lg">
  <option>Large</option>
</select>
```

### Multiple Select

```html
<select class="select" multiple>
  <option>Option 1</option>
  <option>Option 2</option>
  <option>Option 3</option>
</select>
```

## Checkbox

### Basic Checkbox

```html
<label class="label cursor-pointer label-checkbox">
  <span class="label-text">Remember me</span>
  <input type="checkbox" class="checkbox" />
</label>
```

### Checkbox Colors

```html
<input type="checkbox" class="checkbox checkbox-primary" />
<input type="checkbox" class="checkbox checkbox-secondary" />
<input type="checkbox" class="checkbox checkbox-accent" />
<input type="checkbox" class="checkbox checkbox-success" />
<input type="checkbox" class="checkbox checkbox-warning" />
<input type="checkbox" class="checkbox checkbox-error" />
```

### Checkbox Sizes

```html
<input type="checkbox" class="checkbox checkbox-xs" />
<input type="checkbox" class="checkbox checkbox-sm" />
<input type="checkbox" class="checkbox checkbox-md" />
<input type="checkbox" class="checkbox checkbox-lg" />
<input type="checkbox" class="checkbox checkbox-xl" />
```

### Checkbox with Label

```html
<div class="form-control">
  <label class="label cursor-pointer">
    <span class="label-text">Subscribe to newsletter</span>
    <input type="checkbox" class="checkbox checkbox-primary" />
  </label>
</div>
```

### Checked State

```html
<input type="checkbox" class="checkbox" checked />
```

## Radio Buttons

### Basic Radio Group

```html
<div class="form-control">
  <label class="label">
    <span class="label-text">Choose an option</span>
  </label>
  <label class="label cursor-pointer">
    <span class="label-text">Option 1</span>
    <input type="radio" name="option" class="radio" />
  </label>
  <label class="label cursor-pointer">
    <span class="label-text">Option 2</span>
    <input type="radio" name="option" class="radio" />
  </label>
  <label class="label cursor-pointer">
    <span class="label-text">Option 3</span>
    <input type="radio" name="option" class="radio" />
  </label>
</div>
```

### Radio Colors

```html
<input type="radio" name="color" class="radio radio-primary" />
<input type="radio" name="color" class="radio radio-success" />
<input type="radio" name="color" class="radio radio-warning" />
<input type="radio" name="color" class="radio radio-error" />
```

### Radio Sizes

```html
<input type="radio" name="size" class="radio radio-sm" />
<input type="radio" name="size" class="radio radio-md" />
<input type="radio" name="size" class="radio radio-lg" />
```

### Selected State

```html
<input type="radio" name="option" class="radio" checked />
```

## Range Slider

### Basic Range

```html
<input 
  type="range" 
  min="1" 
  max="100" 
  value="50" 
  class="range range-primary" 
/>
```

### Range Colors

```html
<input type="range" min="1" max="100" class="range range-secondary" />
<input type="range" min="1" max="100" class="range range-accent" />
<input type="range" min="1" max="100" class="range range-success" />
```

### Range Sizes

```html
<input type="range" min="1" max="100" class="range range-sm" />
<input type="range" min="1" max="100" class="range range-md" />
<input type="range" min="1" max="100" class="range range-lg" />
```

### Range with Labels

```html
<div class="w-full">
  <div class="flex justify-between mb-2">
    <span>Volume</span>
    <span>75%</span>
  </div>
  <input 
    type="range" 
    min="0" 
    max="100" 
    value="75" 
    class="range range-primary w-full" 
  />
</div>
```

### Dual Range (Custom Implementation)

```html
<div class="relative w-full">
  <input 
    type="range" 
    min="0" 
    max="100" 
    value="30" 
    class="range range-primary w-full" 
    id="range-min"
  />
  <input 
    type="range" 
    min="0" 
    max="100" 
    value="70" 
    class="range range-secondary w-full absolute top-0" 
    id="range-max"
  />
</div>
```

## File Input

### Basic File Input

```html
<input type="file" class="file-input file-input-bordered" />
```

### File Input Styles

```html
<input type="file" class="file-input file-input-ghost" />
```

### File Input Colors

```html
<input type="file" class="file-input file-input-primary" />
<input type="file" class="file-input file-input-success" />
<input type="file" class="file-input file-input-error" />
```

### File Input Sizes

```html
<input type="file" class="file-input file-input-sm" />
<input type="file" class="file-input file-input-md" />
<input type="file" class="file-input file-input-lg" />
```

### File Input with Attributes

```html
<input 
  type="file" 
  class="file-input file-input-bordered file-input-primary w-full max-w-xs" 
  accept="image/*" 
  multiple
/>
```

## Textarea

### Basic Textarea

```html
<textarea 
  class="textarea textarea-bordered" 
  placeholder="Leave a comment here"
></textarea>
```

### Textarea Sizes

```html
<textarea class="textarea textarea-sm" placeholder="Small"></textarea>
<textarea class="textarea textarea-md" placeholder="Medium"></textarea>
<textarea class="textarea textarea-lg" placeholder="Large"></textarea>
```

### Textarea Colors

```html
<textarea class="textarea textarea-primary" placeholder="Primary"></textarea>
<textarea class="textarea textarea-error" placeholder="Error state"></textarea>
```

### Resizable Textarea

```html
<textarea 
  class="textarea textarea-bordered h-32" 
  placeholder="Resizable textarea"
></textarea>
```

## Fieldset

### Basic Fieldset

```html
<fieldset class="fieldset">
  <legend class="fieldset-legend">Account Settings</legend>
  <p>Manage your account preferences</p>
  
  <div class="form-control">
    <label class="label">
      <span class="label-text">Email</span>
    </label>
    <input type="email" class="input input-bordered" placeholder="your@email.com" />
  </div>
</fieldset>
```

## Form Layout Examples

### Vertical Form

```html
<form class="space-y-4">
  <div class="form-control">
    <label class="label">
      <span class="label-text">Full Name</span>
    </label>
    <input type="text" class="input input-bordered" placeholder="John Doe" />
  </div>
  
  <div class="form-control">
    <label class="label">
      <span class="label-text">Email</span>
    </label>
    <input type="email" class="input input-bordered" placeholder="john@example.com" />
  </div>
  
  <div class="form-control">
    <label class="label">
      <span class="label-text">Password</span>
    </label>
    <input type="password" class="input input-bordered" placeholder="********" />
  </div>
  
  <div class="form-control">
    <label class="label cursor-pointer">
      <input type="checkbox" class="checkbox checkbox-primary" />
      <span class="label-text ml-2">Remember me</span>
    </label>
  </div>
  
  <button type="submit" class="btn btn-primary w-full">Submit</button>
</form>
```

### Horizontal Form

```html
<form class="space-y-4">
  <div class="flex items-center gap-4">
    <label class="label w-32">
      <span class="label-text">Full Name</span>
    </label>
    <input type="text" class="input input-bordered flex-1" placeholder="John Doe" />
  </div>
  
  <div class="flex items-center gap-4">
    <label class="label w-32">
      <span class="label-text">Email</span>
    </label>
    <input type="email" class="input input-bordered flex-1" placeholder="john@example.com" />
  </div>
  
  <div class="flex items-center gap-4">
    <label class="label w-32">
      <span class="label-text">Role</span>
    </label>
    <select class="select select-bordered flex-1">
      <option>Admin</option>
      <option>User</option>
      <option>Guest</option>
    </select>
  </div>
  
  <div class="flex items-center gap-4">
    <label class="label w-32"></label>
    <button type="submit" class="btn btn-primary">Submit</button>
  </div>
</form>
```

### Form with Validation States

```html
<form class="space-y-4">
  <!-- Success state -->
  <div class="form-control">
    <label class="label">
      <span class="label-text">Email</span>
    </label>
    <input type="email" class="input input-bordered input-success" value="valid@email.com" />
    <label class="label">
      <span class="label-text-alt text-success">Valid email</span>
    </label>
  </div>
  
  <!-- Error state -->
  <div class="form-control">
    <label class="label">
      <span class="label-text">Password</span>
    </label>
    <input type="password" class="input input-bordered input-error" placeholder="Enter password" />
    <label class="label">
      <span class="label-text-alt text-error">Password is required</span>
    </label>
  </div>
  
  <!-- Warning state -->
  <div class="form-control">
    <label class="label">
      <span class="label-text">Username</span>
    </label>
    <input type="text" class="input input-bordered input-warning" value="taken_username" />
    <label class="label">
      <span class="label-text-alt text-warning">Username already taken</span>
    </label>
  </div>
</form>
```

### Join Multiple Inputs

```html
<div class="join">
  <input class="join-item input" type="text" placeholder="First name" />
  <input class="join-item input" type="text" placeholder="Last name" />
  <button class="join-item btn">Submit</button>
</div>
```

### Input with Addons

```html
<div class="join">
  <button class="join-item btn">-</button>
  <input class="join-item input" type="number" value="5" />
  <button class="join-item btn">+</button>
</div>
```

## Label Component

### Basic Label

```html
<label class="label">
  <span class="label-text">Form label text</span>
</label>
```

### Label with Text and Error

```html
<label class="label">
  <span class="label-text">Required field</span>
  <span class="label-text-alt text-error">Error message</span>
</label>
```

## Form Best Practices

1. **Use semantic HTML** - Wrap forms in `<form>` tags, use proper input types
2. **Associate labels** - Use `for` attribute or wrap inputs in label elements
3. **Provide placeholders** - Give hints about expected input format
4. **Show validation states** - Use color classes for success/error/warning
5. **Make forms accessible** - Include error messages and required indicators
6. **Use consistent sizing** - Keep form elements the same size within a form
7. **Group related fields** - Use fieldset for logical groups
8. **Consider mobile** - Use responsive widths and touch-friendly sizes

## Accessibility Tips

```html
<!-- Required field indicator -->
<label class="label">
  <span class="label-text">Email <span class="text-error">*</span></span>
</label>
<input type="email" required class="input input-bordered" />

<!-- Error description -->
<div class="form-control">
  <label class="label" id="email-label">
    <span class="label-text">Email</span>
  </label>
  <input 
    type="email" 
    class="input input-bordered input-error" 
    aria-describedby="email-error"
    aria-invalid="true"
  />
  <label class="label" id="email-error">
    <span class="label-text-alt text-error">Please enter a valid email</span>
  </label>
</div>

<!-- Success feedback -->
<div role="alert" aria-live="polite">
  <div class="alert alert-success">
    <span>Form submitted successfully!</span>
  </div>
</div>
```
