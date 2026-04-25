# Oat UI - Forms

Complete form element documentation including inputs, validation, and layouts.

## Basic Form Structure

```html
<form>
  <label data-field>
    Name
    <input type="text" placeholder="Enter your name" />
  </label>
  
  <button type="submit">Submit</button>
</form>
```

Wrap inputs in `<label>` for proper association and styling. Use `data-field` for field container styling.

## Text Inputs

### Standard Input

```html
<label data-field>
  Email
  <input type="email" placeholder="you@example.com" />
</label>
```

### With Placeholder

```html
<input type="text" placeholder="Enter your name" />
```

### With Value

```html
<input type="text" value="Pre-filled value" />
```

### Disabled Input

```html
<label data-field>
  Disabled
  <input type="text" placeholder="Disabled" disabled />
</label>
```

### Read-only Input

```html
<label data-field>
  Read-only
  <input type="text" value="Cannot edit" readonly />
</label>
```

## Password Inputs

```html
<label data-field>
  Password
  <input type="password" placeholder="Password" aria-describedby="password-hint" />
  <small id="password-hint" data-hint">Minimum 8 characters, include number</small>
</label>
```

## Textarea

```html
<label data-field>
  Message
  <textarea placeholder="Your message..." rows="4"></textarea>
</label>
```

## Select Dropdowns

### Standard Select

```html
<div data-field>
  <label>Select an option</label>
  <select aria-label="Select an option">
    <option value="">Choose...</option>
    <option value="a">Option A</option>
    <option value="b">Option B</option>
    <option value="c">Option C</option>
  </select>
</div>
```

### With Selected Value

```html
<select>
  <option value="">Choose...</option>
  <option value="a">Option A</option>
  <option value="b" selected>Option B</option>
  <option value="c">Option C</option>
</select>
```

### Multiple Select

```html
<select multiple aria-label="Select multiple options">
  <option value="a">Option A</option>
  <option value="b">Option B</option>
  <option value="c">Option C</option>
</select>
```

## Checkboxes

### Single Checkbox

```html
<label data-field>
  <input type="checkbox" /> I agree to the terms
</label>
```

### Checked State

```html
<label>
  <input type="checkbox" checked /> Already agreed
</label>
```

### Multiple Checkboxes

```html
<fieldset>
  <legend>Select options</legend>
  <label><input type="checkbox" name="opts" value="a"> Option A</label>
  <label><input type="checkbox" name="opts" value="b"> Option B</label>
  <label><input type="checkbox" name="opts" value="c"> Option C</label>
</fieldset>
```

## Radio Buttons

### Radio Group

```html
<fieldset class="hstack">
  <legend>Preference</legend>
  <label><input type="radio" name="pref" value="a"> Option A</label>
  <label><input type="radio" name="pref" value="b" checked> Option B</label>
  <label><input type="radio" name="pref" value="c"> Option C</label>
</fieldset>
```

### Vertical Radio Group

```html
<fieldset>
  <legend>Choose a plan</legend>
  <label><input type="radio" name="plan" value="basic"> Basic - $9/mo</label>
  <label><input type="radio" name="plan" value="pro" checked> Pro - $29/mo</label>
  <label><input type="radio" name="plan" value="enterprise"> Enterprise - Custom</label>
</fieldset>
```

## Range Slider

```html
<label data-field>
  Volume
  <input type="range" min="0" max="100" value="50" />
</label>
```

### With Value Display

```html
<label data-field>
  Volume: <output id="vol-val">50</output>
  <input type="range" min="0" max="100" value="50" oninput="document.getElementById('vol-val').value = this.value" />
</label>
```

## File Upload

```html
<label data-field>
  Upload file
  <input type="file" />
</label>
```

### Multiple Files

```html
<input type="file" multiple />
```

### File Type Restriction

```html
<input type="file" accept=".pdf,.doc,.docx" />
```

## Date and Time Inputs

### Date Picker

```html
<label data-field>
  Birth date
  <input type="date" />
</label>
```

### DateTime Local

```html
<label data-field>
  Event datetime
  <input type="datetime-local" />
</label>
```

### Time Picker

```html
<label data-field>
  Meeting time
  <input type="time" />
</label>
```

## Number Input

```html
<label data-field>
  Quantity
  <input type="number" min="1" max="100" value="10" />
</label>
```

## URL and Email Inputs

```html
<label data-field>
  Website
  <input type="url" placeholder="https://example.com" />
</label>

<label data-field>
  Email
  <input type="email" placeholder="you@example.com" />
</label>
```

## Input Groups

### Combined Input and Button

```html
<fieldset class="group">
  <input type="text" placeholder="Search" />
  <button>Go</button>
</fieldset>
```

### URL Builder

```html
<fieldset class="group">
  <legend>https://</legend>
  <input type="text" placeholder="subdomain" />
  <select>
    <option>.example.com</option>
    <option>.example.net</option>
  </select>
  <button>Go</button>
</fieldset>
```

## Field Validation

### Required Field

```html
<label data-field>
  Email *
  <input type="email" required />
</label>
```

Browser shows native validation.

### Error State

```html
<div data-field="error">
  <label for="email">Email</label>
  <input type="email" id="email" aria-invalid="true" aria-describedby="error-msg" value="invalid-email" />
  <div id="error-msg" class="error" role="status">Please enter a valid email address.</div>
</div>
```

### Success State

```html
<div data-field="success">
  <label for="username">Username</label>
  <input type="text" id="username" value="available-user" aria-describedby="success-msg" />
  <div id="success-msg" class="success" role="status">Username is available!</div>
</div>
```

### Inline Validation Message

```html
<label data-field>
  Password
  <input type="password" aria-describedby="pwd-hint" />
  <small id="pwd-hint" data-hint">Must be at least 8 characters</small>
</label>
```

## Fieldset and Legend

### Grouped Fields

```html
<fieldset>
  <legend>Contact Information</legend>
  
  <label data-field>
    Phone
    <input type="tel" placeholder="(555) 123-4567" />
  </label>
  
  <label data-field>
    Address
    <input type="text" placeholder="123 Main St" />
  </label>
</fieldset>
```

## Complete Form Example

```html
<form>
  <h2>Create Account</h2>
  
  <label data-field>
    Full Name
    <input type="text" name="name" required placeholder="John Doe" />
  </label>
  
  <label data-field>
    Email Address
    <input type="email" name="email" required placeholder="john@example.com" />
  </label>
  
  <label data-field>
    Password
    <input type="password" name="password" required minlength="8" aria-describedby="pwd-requirements" />
    <small id="pwd-requirements" data-hint">Minimum 8 characters, include uppercase and number</small>
  </label>
  
  <label data-field>
    <input type="checkbox" name="terms" required /> I agree to the Terms of Service
  </label>
  
  <fieldset class="hstack">
    <legend>Newsletter</legend>
    <label><input type="radio" name="newsletter" value="yes"> Yes</label>
    <label><input type="radio" name="newsletter" value="no" checked> No</label>
  </fieldset>
  
  <div class="hstack justify-end gap-2">
    <button type="reset" class="outline">Reset</button>
    <button type="submit">Create Account</button>
  </div>
</form>
```

## Form Layouts

### Single Column (Default)

```html
<form>
  <label data-field><input type="text" /></label>
  <label data-field><input type="email" /></label>
  <label data-field><input type="password" /></label>
</form>
```

### Two Column Grid

```html
<form class="grid">
  <div class="col-6">
    <label data-field>
      First Name
      <input type="text" />
    </label>
  </div>
  <div class="col-6">
    <label data-field>
      Last Name
      <input type="text" />
    </label>
  </div>
  
  <div class="col-12">
    <label data-field>
      Email
      <input type="email" />
    </label>
  </div>
</form>
```

## Accessibility

### Label Association

Always wrap inputs in `<label>` or use `for` attribute:

```html
<!-- Preferred -->
<label data-field>
  Email
  <input type="email" />
</label>

<!-- Also valid -->
<label for="email">Email</label>
<input type="email" id="email" />
```

### Required Field Indication

```html
<label data-field>
  Email <span class="required" aria-hidden="true">*</span>
  <input type="email" required aria-required="true" />
</label>
```

### Error Announcements

```html
<input type="email" aria-invalid="true" aria-describedby="email-error" />
<div id="email-error" role="alert" class="error">Invalid email format</div>
```

### Fieldset for Grouping

```html
<fieldset>
  <legend>Billing Information</legend>
  <!-- Related fields -->
</fieldset>
```

## Customization

### Input Height

```css
input, textarea, select {
  --input-height: 2.5rem;  /* Taller inputs */
}
```

### Input Border Radius

```css
input, textarea, select {
  border-radius: var(--radius-full);  /* Pill-shaped */
}
```

### Focus Ring

```css
input:focus, textarea:focus, select:focus {
  --ring: rgb(59 130 246);  /* Blue focus ring */
  outline-width: 2px;
}
```

## Best Practices

### DO

- Always label form fields
- Use appropriate input types (email, tel, url)
- Provide clear error messages
- Group related fields with fieldset
- Place labels above inputs for mobile friendliness
- Use placeholders as examples, not labels

### DON'T

- Remove labels for "cleaner" design
- Use red color alone to indicate errors
- Require unnecessary fields
- Use generic error messages ("Invalid input")
- Disable copy/paste in password fields
