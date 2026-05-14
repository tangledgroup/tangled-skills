# Data Input Components

## Calendar

Styles for third-party calendar libraries (Cally, Pikaday, React Day Picker).

### Class Names

- **component**: `cally` (Cally), `pika-single` (Pikaday input), `react-day-picker` (React)

### Syntax

```html
<!-- Cally web component -->
<calendar-date class="cally"></calendar-date>

<!-- Pikaday -->
<input type="text" class="input pika-single" placeholder="Select date" />

<!-- React Day Picker -->
<DayPicker className="react-day-picker" />
```

## Checkbox

Styled checkbox input.

### Class Names

- **component**: `checkbox`
- **color**: `checkbox-primary`, `checkbox-secondary`, `checkbox-accent`, `checkbox-neutral`, `checkbox-success`, `checkbox-warning`, `checkbox-info`, `checkbox-error`
- **size**: `checkbox-xs`, `checkbox-sm`, `checkbox-md`, `checkbox-lg`, `checkbox-xl`

### Syntax

```html
<input type="checkbox" class="checkbox checkbox-primary" />
<input type="checkbox" class="checkbox checkbox-success checkbox-lg" checked />
```

## Fieldset

Groups related form elements with a legend title and optional description.

### Class Names

- **component**: `fieldset`, `label`
- **part**: `fieldset-legend`

### Syntax

```html
<fieldset class="fieldset">
  <legend class="fieldset-legend">Payment Method</legend>
  <input type="text" class="input input-bordered" placeholder="Card number" />
  <p class="label">Enter your payment details below.</p>
</fieldset>
```

### Rules

- Any element can be a direct child of fieldset for form controls

## File Input

Styled file upload input.

### Class Names

- **component**: `file-input`
- **style**: `file-input-ghost`
- **color**: `file-input-neutral`, `file-input-primary`, `file-input-secondary`, `file-input-accent`, `file-input-info`, `file-input-success`, `file-input-warning`, `file-input-error`
- **size**: `file-input-xs`, `file-input-sm`, `file-input-md`, `file-input-lg`, `file-input-xl`

### Syntax

```html
<input type="file" class="file-input file-input-primary w-full max-w-xs" />
<input type="file" class="file-input file-input-ghost lg:max-w-sm" multiple />
```

## Filter

Group of radio buttons that hides unselected options and shows a reset button.

### Class Names

- **component**: `filter`
- **part**: `filter-reset`

### Syntax

Using `<form>` (recommended):

```html
<form class="filter">
  <input class="btn btn-square" type="reset" value="×" />
  <input class="btn" type="radio" name="filter-group" aria-label="All" checked />
  <input class="btn" type="radio" name="filter-group" aria-label="Active" />
  <input class="btn" type="radio" name="filter-group" aria-label="Archived" />
</form>
```

Without form:

```html
<div class="filter">
  <input class="btn filter-reset" type="radio" name="filter-group" aria-label="×" />
  <input class="btn" type="radio" name="filter-group" aria-label="All" checked />
  <input class="btn" type="radio" name="filter-group" aria-label="Active" />
</div>
```

### Rules

- Each filter group must have a unique `name` attribute
- Use `<form>` when possible; fall back to `<div>` only when necessary
- Use `filter-reset` class for the reset button in non-form variants

## Label

Provides a name or title for input fields, supporting regular and floating labels.

### Class Names

- **component**: `label`, `floating-label`

### Syntax

Regular label:

```html
<label class="input">
  <span class="label">Email</span>
  <input type="email" placeholder="you@example.com" />
</label>
```

Floating label:

```html
<label class="floating-label">
  <input type="text" placeholder="Type here" class="input" />
  <span>Label text</span>
</label>
```

### Rules

- The `input` class styles the parent container (not the `<input>` element itself)
- Use `floating-label` for labels that animate above the input on focus

## Radio

Radio button inputs for single selection.

### Class Names

- **component**: `radio`
- **color**: `radio-neutral`, `radio-primary`, `radio-secondary`, `radio-accent`, `radio-success`, `radio-warning`, `radio-info`, `radio-error`
- **size**: `radio-xs`, `radio-sm`, `radio-md`, `radio-lg`, `radio-xl`

### Syntax

```html
<input type="radio" name="options" class="radio radio-primary" />
<input type="radio" name="options" class="radio radio-primary" checked />
<input type="radio" name="other-group" class="radio radio-success radio-lg" />
```

### Rules

- Each radio group must have a unique `name` to avoid cross-group conflicts

## Range

Slider input for selecting a value within a range.

### Class Names

- **component**: `range`
- **color**: `range-neutral`, `range-primary`, `range-secondary`, `range-accent`, `range-success`, `range-warning`, `range-info`, `range-error`
- **size**: `range-xs`, `range-sm`, `range-md`, `range-lg`, `range-xl`

### Syntax

```html
<input type="range" min="0" max="100" value="40" class="range range-primary range-sm" />
```

### Rules

- Must specify `min` and `max` attributes

## Rating

Star-based rating using radio inputs.

### Class Names

- **component**: `rating`
- **modifier**: `rating-half`, `rating-hidden`
- **size**: `rating-xs`, `rating-sm`, `rating-md`, `rating-lg`, `rating-xl`

### Syntax

```html
<div class="rating rating-lg">
  <input type="radio" name="rating-1" class="mask mask-star-2 bg-orange-400" />
  <input type="radio" name="rating-1" class="mask mask-star-2 bg-orange-400" />
  <input type="radio" name="rating-1" class="mask mask-star-2 bg-orange-400" />
  <input type="radio" name="rating-1" class="mask mask-star-2 bg-orange-400" />
  <input type="radio" name="rating-1" class="mask mask-star-2 bg-orange-400" />
</div>
```

### Rules

- Each rating group must have a unique `name`
- Add `rating-hidden` to the first radio input to allow clearing the rating
- `rating-half` enables half-star precision

## Select

Styled dropdown select element.

### Class Names

- **component**: `select`
- **style**: `select-ghost`
- **color**: `select-neutral`, `select-primary`, `select-secondary`, `select-accent`, `select-info`, `select-success`, `select-warning`, `select-error`
- **size**: `select-xs`, `select-sm`, `select-md`, `select-lg`, `select-xl`

### Syntax

```html
<select class="select select-primary w-full max-w-xs">
  <option disabled selected>Select option</option>
  <option>Option 1</option>
  <option>Option 2</option>
</select>
```

## Input Field

Text input field supporting all HTML input types.

### Class Names

- **component**: `input`
- **style**: `input-ghost`
- **color**: `input-neutral`, `input-primary`, `input-secondary`, `input-accent`, `input-info`, `input-success`, `input-warning`, `input-error`
- **size**: `input-xs`, `input-sm`, `input-md`, `input-lg`, `input-xl`

### Syntax

```html
<input type="text" placeholder="Type here" class="input input-bordered w-full" />
<input type="email" placeholder="Email" class="input input-primary w-full max-w-xs" />
<input type="password" placeholder="Password" class="input input-error input-lg" />

<!-- Input with icon -->
<label class="input has-[:focus:not(:placeholder-shown):border-primary]">
  <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" fill="currentColor" class="h-5 w-5 opacity-70"><path fill-rule="evenodd" d="M1.5 4.5a3 3 0 013-3h1.372c.81 0 1.54.31 2.123.827a.96.96 0 01.09.103l.084.101A4.49 4.49 0 018 2.25c1.19 0 2.279.414 3.135 1.107.06.047.12.099.179.155l.084.101a.96.96 0 01.09.103A3 3 0 0114.5 6v6.75a3 3 0 01-3 3h-7a3 3 0 01-3-3V4.5z" clip-rule="evenodd" /></svg>
  <input type="text" class="grow" placeholder="Search..." />
</label>
```

### Rules

- Works with any input type (text, password, email, number, etc.)
- Use `input` class on the parent when wrapping multiple elements

## Textarea

Multi-line text input.

### Class Names

- **component**: `textarea`
- **style**: `textarea-ghost`
- **color**: `textarea-neutral`, `textarea-primary`, `textarea-secondary`, `textarea-accent`, `textarea-info`, `textarea-success`, `textarea-warning`, `textarea-error`
- **size**: `textarea-xs`, `textarea-sm`, `textarea-md`, `textarea-lg`, `textarea-xl`

### Syntax

```html
<textarea class="textarea textarea-bordered w-full" placeholder="Bio"></textarea>
<textarea class="textarea textarea-primary h-32" placeholder="Message"></textarea>
```

## Toggle

Switch-style checkbox input.

### Class Names

- **component**: `toggle`
- **color**: `toggle-primary`, `toggle-secondary`, `toggle-accent`, `toggle-neutral`, `toggle-success`, `toggle-warning`, `toggle-info`, `toggle-error`
- **size**: `toggle-xs`, `toggle-sm`, `toggle-md`, `toggle-lg`, `toggle-xl`

### Syntax

```html
<input type="checkbox" class="toggle toggle-primary" />
<input type="checkbox" class="toggle toggle-success toggle-lg" checked />
```

## Validator

Changes form element colors to error/success based on native HTML validation.

### Class Names

- **component**: `validator`
- **part**: `validator-hint`

### Syntax

```html
<div class="form-control w-full max-w-xs">
  <label class="label">
    <span class="label-text">Email (required)</span>
  </label>
  <input type="email" placeholder="email@example.com" class="input input-bordered w-full validator" required />
  <p class="validator-hint">Please enter a valid email address.</p>
</div>
```

### Rules

- Use with `input`, `select`, or `textarea` elements
- Relies on HTML5 validation attributes (`required`, `pattern`, `minlength`, etc.)
