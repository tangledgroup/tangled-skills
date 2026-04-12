# Forms

All form elements are fully responsive with pure semantic HTML, enabling forms to scale gracefully across devices and viewports.

## Basic Form Structure

Inputs are `width: 100%` by default and match button sizes for consistency:

```html
<form>
  <fieldset>
    <label>
      First name
      <input name="first_name" placeholder="First name" autocomplete="given-name">
    </label>
    <label>
      Email
      <input type="email" name="email" placeholder="Email" autocomplete="email">
    </label>
  </fieldset>

  <input type="submit" value="Subscribe">
</form>
```

### Input Inside or Outside Label

Both patterns work:

```html
<form>
  <!-- Input inside label -->
  <label>
    First name
    <input name="first_name" placeholder="First name" autocomplete="given-name">
  </label>

  <!-- Input outside label -->
  <label for="email">Email</label>
  <input type="email" id="email" placeholder="Email" autocomplete="email">
</form>
```

## Helper Text

Use `<small>` below form elements for helper text (automatically muted):

```html
<input
  type="email"
  name="email"
  placeholder="Email"
  aria-describedby="email-helper"
>
<small id="email-helper">
  We'll never share your email with anyone else.
</small>
```

## Input Types

### Text Input

```html
<input type="text" placeholder="Text input">
```

### Email Input

```html
<input type="email" placeholder="Email address">
```

### Password Input

```html
<input type="password" placeholder="Password">
```

### Number Input

```html
<input type="number" placeholder="Number">
```

### Tel Input

```html
<input type="tel" placeholder="Phone number">
```

### URL Input

```html
<input type="url" placeholder="Website URL">
```

### Search Input

```html
<input type="search" placeholder="Search...">
```

### Date Inputs

```html
<input type="date">
<input type="datetime-local">
<input type="time">
<input type="week">
<input type="month">
```

### Color Input

```html
<input type="color">
```

## Textarea

```html
<label for="message">Message</label>
<textarea id="message" rows="4" placeholder="Your message..."></textarea>
```

## Select

```html
<label for="browser">Choose a browser</label>
<select id="browser">
  <option value="">Select...</option>
  <option value="chrome">Chrome</option>
  <option value="firefox">Firefox</option>
  <option value="safari">Safari</option>
  <option value="edge">Edge</option>
</select>
```

### Multiple Select

```html
<select multiple>
  <option value="chrome">Chrome</option>
  <option value="firefox">Firefox</option>
  <option value="safari">Safari</option>
</select>
```

## Checkboxes

```html
<fieldset>
  <legend>Select your preferences</legend>
  
  <label>
    <input type="checkbox" name="newsletter" checked>
    Subscribe to newsletter
  </label>
  
  <label>
    <input type="checkbox" name="updates">
    Receive product updates
  </label>
  
  <label>
    <input type="checkbox" name="offers">
    Get special offers
  </label>
</fieldset>
```

## Radios

```html
<fieldset>
  <legend>Choose a plan</legend>
  
  <label>
    <input type="radio" name="plan" value="basic" checked>
    Basic - $9/month
  </label>
  
  <label>
    <input type="radio" name="plan" value="pro">
    Pro - $19/month
  </label>
  
  <label>
    <input type="radio" name="plan" value="enterprise">
    Enterprise - Custom pricing
  </label>
</fieldset>
```

## Switch

```html
<label>
  <input type="checkbox" role="switch" checked>
  Enable notifications
</label>
```

## Range

```html
<label for="volume">Volume</label>
<input type="range" id="volume" min="0" max="100" value="50">
```

## File Input

```html
<label for="file">Upload a file</label>
<input type="file" id="file">
```

Multiple files:

```html
<input type="file" multiple>
```

## Buttons

### Submit Button

```html
<button type="submit">Submit</button>
<!-- or -->
<input type="submit" value="Submit">
```

### Primary Button

```html
<button type="submit">Subscribe</button>
```

### Secondary Button

```html
<button type="button" class="secondary">Cancel</button>
```

### Outline Button

```html
<button type="button" class="outline">Learn more</button>
```

### Ghost Button

```html
<button type="button" class="ghost">Dismiss</button>
```

### Disabled Button

```html
<button type="submit" disabled>Submit</button>
```

### Button with Icon

```html
<button type="button">
  <svg aria-hidden="true" ...>...</svg>
  Download
</button>
```

## Form Validation

Pico styles invalid inputs automatically using the `:invalid` pseudo-class:

```html
<form>
  <label>
    Email
    <input type="email" required>
  </label>
  
  <label>
    Password
    <input type="password" minlength="8" required>
  </label>
  
  <button type="submit">Sign up</button>
</form>
```

## Form Layouts

### Using Grid

```html
<form>
  <fieldset class="grid">
    <input name="login" placeholder="Login" aria-label="Login">
    <input type="password" name="password" placeholder="Password">
    <input type="submit" value="Log in">
  </fieldset>
</form>
```

### Using Group

```html
<form>
  <div role="group">
    <input type="email" placeholder="Email">
    <button type="submit">Subscribe</button>
  </div>
</form>
```

## Autocomplete Attributes

Use autocomplete attributes for better UX and browser support:

```html
<form>
  <label>
    Full name
    <input name="name" autocomplete="name">
  </label>
  
  <label>
    Email
    <input type="email" name="email" autocomplete="email">
  </label>
  
  <label>
    Phone
    <input type="tel" name="phone" autocomplete="tel">
  </label>
  
  <label>
    Address
    <input name="address" autocomplete="street-address">
  </label>
  
  <label>
    City
    <input name="city" autocomplete="address-level2">
  </label>
  
  <label>
    ZIP Code
    <input name="zip" autocomplete="postal-code">
  </label>
  
  <label>
    Credit Card
    <input name="card" autocomplete="cc-number">
  </label>
</form>
```

Common autocomplete values: `name`, `email`, `tel`, `username`, `password`, `given-name`, `family-name`, `street-address`, `address-level2`, `postal-code`, `country`, `cc-number`, `cc-exp`.

## Accessibility

- Always use `<label>` elements associated with inputs
- Use `aria-describedby` for helper text
- Use `required` attribute for mandatory fields
- Provide clear error messages
- Use appropriate input types for better mobile UX

```html
<form>
  <label for="email">Email address *</label>
  <input 
    type="email" 
    id="email" 
    name="email" 
    required
    aria-describedby="email-error"
  >
  <small id="email-error" role="alert">
    Please enter a valid email address.
  </small>
</form>
```
