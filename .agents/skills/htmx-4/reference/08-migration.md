# Migration Guide: htmx 2.x to 4.0

## Overview

This guide helps migrate applications from htmx 2.x to htmx 4.0. The migration can be done incrementally - start with compatibility mode, then update features gradually.

## Quick Start Migration

### Option 1: Compatibility Extension (Recommended for Initial Upgrade)

Load the `htmx-2-compat` extension to restore htmx 2 behavior:

```html
<!-- Old -->
<script src="https://unpkg.com/htmx.org@2.0.8/dist/htmx.min.js"></script>

<!-- New with compatibility -->
<script src="https://cdn.jsdelivr.net/npm/htmx.org@4.0.0-beta1/dist/htmx.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/htmx.org@4.0.0-beta1/dist/ext/htmx-2-compat.js"></script>
```

This restores:
- Implicit attribute inheritance
- Old event names
- Previous error-swapping defaults (no swap on 4xx/5xx)

Then migrate incrementally using this guide.

### Option 2: Configuration Restore

Manually restore htmx 2 behavior via configuration:

```javascript
// Add before loading htmx script
<script>
  window.htmxConfig = {
    implicitInheritance: true,
    noSwap: [204, 304, '4xx', '5xx'],
    defaultTimeout: 0
  };
</script>
<script src="https://cdn.jsdelivr.net/npm/htmx.org@4.0.0-beta1/dist/htmx.min.js"></script>
```

## Breaking Changes Summary

### 1. Fetch API Replaces XMLHttpRequest

**Change:** All requests now use native `fetch()` instead of XMLHttpRequest.

**Impact:** Cannot be reverted. Some XHR-specific behaviors changed.

**Migration:** None needed for most apps. Test CORS and authentication flows.

### 2. Explicit Attribute Inheritance

**htmx 2 (implicit):**
```html
<div hx-confirm="Are you sure?">
  <button hx-delete="/item/1">Delete</button>
</div>
```

**htmx 4 (explicit):**
```html
<div hx-confirm:inherited="Are you sure?">
  <button hx-delete="/item/1">Delete</button>
</div>
```

**Migration:** Add `:inherited` modifier to attributes that should inherit down DOM tree.

Common attributes needing `:inherited`:
- `hx-target:inherited`
- `hx-confirm:inherited`
- `hx-include:inherited`
- `hx-disable:inherited`
- `hx-push-url:inherited`

**Alternative:** Set `htmx.config.implicitInheritance = true` (not recommended long-term).

### 3. Error Responses Now Swap

**htmx 2:** 4xx and 5xx responses did not swap by default.

**htmx 4:** All responses swap, including errors. Only 204 and 304 don't swap.

**Migration Options:**

A. Restore old behavior:
```javascript
htmx.config.noSwap = [204, 304, '4xx', '5xx'];
```

B. Design error responses as valid HTML:
```html
<!-- Server returns HTML for errors -->
<form hx-post="/save">
  <input name="email">
  <button type="submit">Save</button>
</form>
```

Server returns on 422:
```html
<div class="error-messages">
  <p>Please fix the following errors:</p>
  <ul>
    <li>Email is required</li>
  </ul>
</div>
```

C. Use `hx-status` for per-code handling:
```html
<form hx-post="/save"
      hx-status:422="swap:innerHTML target:#errors select:.error-messages"
      hx-status:5xx="swap:none">
  <button type="submit">Save</button>
</form>
```

### 4. hx-delete Excludes Form Data

**htmx 2:** `hx-delete` included enclosing form inputs.

**htmx 4:** `hx-delete` excludes form data (like `hx-get`).

**Migration:** Add `hx-include="closest form"` where needed:

```html
<!-- htmx 2 -->
<form>
  <button hx-delete="/item">Delete</button>
</form>

<!-- htmx 4 -->
<form>
  <button hx-delete="/item" hx-include="closest form">Delete</button>
</form>
```

### 5. No History Cache

**htmx 2:** Pages cached in localStorage for history navigation.

**htmx 4:** Pages re-fetched on back/forward navigation.

**Migration Options:**

A. Accept new behavior (recommended - fresher data)

B. Use full page reload:
```javascript
htmx.config.history = "reload";
```

C. Disable history:
```javascript
htmx.config.history = false;
```

### 6. OOB Swap Order Changed

**htmx 2:** OOB elements swapped before main content.

**htmx 4:** Main content swaps first, then OOB elements.

**Migration:** If OOB swaps created DOM that main swap depended on, restructure:

```html
<!-- htmx 2 pattern (may break in 4) -->
<!-- Server response -->
<div hx-swap-oob="innerHTML:#template-container">
  <template id="item-template"><div>Item</div></template>
</div>
<div>Main content using template</div>

<!-- htmx 4 pattern (independent swaps) -->
<div hx-swap-oob="innerHTML:#template-container">
  <template id="item-template"><div>Item</div></template>
</div>
<div hx-swap-oob="innerHTML:#main">Main content</div>
```

### 7. 60-Second Default Timeout

**htmx 2:** No timeout (0).

**htmx 4:** 60-second timeout (60000ms).

**Migration:** Restore unlimited timeout if needed:

```javascript
htmx.config.defaultTimeout = 0;
```

Or set custom timeout:

```javascript
htmx.config.defaultTimeout = 30000; // 30 seconds
```

### 8. Extension Loading Changed

**htmx 2:** Used `hx-ext` attribute:

```html
<div hx-get="/data" hx-ext="sse,sse-events">Load</div>
```

**htmx 4:** Include extension scripts directly:

```html
<script src="/ext/sse.js"></script>
<script src="/ext/sse-events.js"></script>
<div hx-get="/data">Load</div>
```

**Migration:** 
1. Remove all `hx-ext` attributes
2. Add `<script>` tags for needed extensions
3. Extensions auto-register when loaded

## Attribute Renames and Removals

### Removed Attributes

| htmx 2.x | htmx 4.x Alternative |
|----------|---------------------|
| `hx-vars` | `hx-vals` with `js:` prefix |
| `hx-params` | `htmx:config:request` event |
| `hx-prompt` | `hx-confirm` with `js:` prefix |
| `hx-ext` | Include extension script directly |
| `hx-disinherit` | Not needed (inheritance is explicit) |
| `hx-inherit` | Not needed (inheritance is explicit) |
| `hx-request` | `hx-config` |
| `hx-history` | Removed (no localStorage) |
| `hx-history-elt` | Removed |

### Renamed Attributes

| htmx 2.x | htmx 4.x | Notes |
|----------|----------|-------|
| `hx-disable` | `hx-ignore` | Skip htmx processing |
| `hx-disabled-elt` | `hx-disable` | Disable elements during request |

**Critical Migration Order:**

1. First, rename `hx-disable` to `hx-ignore`:
```html
<!-- Before -->
<a href="/page" hx-get="/api/page" hx-disable="true">Link</a>

<!-- After step 1 -->
<a href="/page" hx-get="/api/page" hx-ignore="true">Link</a>
```

2. Then, rename `hx-disabled-elt` to `hx-disable`:
```html
<!-- Before -->
<form hx-post="/submit" hx-disabled-elt="button[type=submit]">
  <button type="submit">Submit</button>
</form>

<!-- After step 2 -->
<form hx-post="/submit" hx-disable="button[type=submit]">
  <button type="submit">Submit</button>
</form>
```

### New Attributes in htmx 4

| Attribute | Purpose |
|-----------|---------|
| `hx-action` | Specify URL (use with `hx-method`) |
| `hx-method` | Specify HTTP method |
| `hx-config` | Per-element request configuration |
| `hx-ignore` | Disable htmx processing (was `hx-disable`) |
| `hx-validate` | Control form validation behavior |
| `hx-status:XXX` | Per-status-code swap behavior |

## Event Name Changes

All events now follow pattern: `htmx:phase:action[:sub-action]`

### Event Renames

| htmx 2.x | htmx 4.x |
|----------|----------|
| `htmx:afterOnLoad` | `htmx:after:init` |
| `htmx:afterProcessNode` | `htmx:after:init` |
| `htmx:afterRequest` | `htmx:after:request` |
| `htmx:afterSettle` | `htmx:after:swap` |
| `htmx:afterSwap` | `htmx:after:swap` |
| `htmx:beforeCleanupElement` | `htmx:before:cleanup` |
| `htmx:beforeHistorySave` | `htmx:before:history:update` |
| `htmx:beforeOnLoad` | `htmx:before:init` |
| `htmx:beforeProcessNode` | `htmx:before:process` |
| `htmx:beforeRequest` | `htmx:before:request` |
| `htmx:beforeSwap` | `htmx:before:swap` |
| `htmx:configRequest` | `htmx:config:request` |
| `htmx:historyCacheMiss` | `htmx:before:restore-history` |
| `htmx:historyRestore` | `htmx:before:restore-history` |
| `htmx:load` | `htmx:after:init` |
| `htmx:oobAfterSwap` | `htmx:after:swap` |
| `htmx:oobBeforeSwap` | `htmx:before:swap` |
| `htmx:pushedIntoHistory` | `htmx:after:history:push` |
| `htmx:replacedInHistory` | `htmx:after:history:replace` |

### Consolidated Error Events

All error events consolidated to `htmx:error`:

| htmx 2.x Event | Now Uses |
|----------------|----------|
| `htmx:responseError` | `htmx:error` |
| `htmx:sendError` | `htmx:error` |
| `htmx:swapError` | `htmx:error` |
| `htmx:targetError` | `htmx:error` |
| `htmx:timeout` | `htmx:error` |

**Migration:**
```javascript
// htmx 2
document.addEventListener('htmx:beforeRequest', handler);
document.addEventListener('htmx:responseError', errorHandler);

// htmx 4
document.addEventListener('htmx:before:request', handler);
document.addEventListener('htmx:error', errorHandler);
```

### Removed Events

- Validation events: `htmx:validation:validate`, `htmx:validation:failed`, `htmx:validation:halted`
- XHR events: `htmx:xhr:loadstart`, `htmx:xhr:progress`, `htmx:xhr:abort`

Use native browser validation and `htmx:finally:request` instead.

## Configuration Changes

### Renamed Config Options

| htmx 2.x | htmx 4.x |
|----------|----------|
| `defaultSwapStyle` | `defaultSwap` |
| `globalViewTransitions` | `transitions` |
| `historyEnabled` | `history` |
| `includeIndicatorStyles` | `includeIndicatorCSS` |
| `timeout` | `defaultTimeout` |

### Changed Defaults

| Config | htmx 2 | htmx 4 |
|--------|--------|--------|
| `defaultTimeout` | `0` (unlimited) | `60000` (60s) |
| `defaultSettleDelay` | `20` | `1` |

### Removed Config Options

These options were removed:
- `addedClass`, `settlingClass`, `swappingClass` (use standard class names)
- `allowEval`, `allowNestedOobSwaps`, `allowScriptTags`
- `attributesToSettle`, `getCacheBusterParam`
- `historyCacheSize`, `ignoreTitle` (per-swap only now)
- `methodsThatUseUrlParams`, `refreshOnHistoryMiss`
- `responseHandling` (use `hx-status` and `noSwap`)
- `scrollBehavior`, `scrollIntoViewOnBoost`
- `selfRequestsOnly` (use `mode`)
- `triggerSpecsCache`, `useTemplateFragments`
- `withCredentials` (use `hx-config`)
- `wsBinaryType`, `wsReconnectDelay`

## Header Changes

### Request Header Changes

| htmx 2.x | htmx 4.x | Notes |
|----------|----------|-------|
| `HX-Trigger` | `HX-Source` | Format: `tagName#id` |
| `HX-Target` | `HX-Target` | Format: `tagName#id` |
| `HX-Trigger-Name` | Removed | Use `HX-Source` |
| `HX-Prompt` | Removed | Use `hx-confirm` with `js:` |

**New headers:**
- `HX-Request-Type`: `"full"` or `"partial"`
- `Accept`: Now explicitly `text/html`

### Response Header Changes

Removed:
- `HX-Trigger-After-Swap`
- `HX-Trigger-After-Settle`

Use `HX-Trigger` or JavaScript instead.

Unchanged: `HX-Redirect`, `HX-Refresh`, `HX-Location`, `HX-Push-Url`, `HX-Replace-Url`, `HX-Retarget`, `HX-Reswap`, `HX-Reselect`.

## JavaScript API Changes

### Removed Methods

Use native JavaScript instead:

| htmx 2.x Method | Native Alternative |
|-----------------|-------------------|
| `htmx.addClass(el, name)` | `el.classList.add(name)` |
| `htmx.removeClass(el, name)` | `el.classList.remove(name)` |
| `htmx.toggleClass(el, name)` | `el.classList.toggle(name)` |
| `htmx.closest(elt, selector)` | `elt.closest(selector)` |
| `htmx.remove(element)` | `element.remove()` |
| `htmx.off(event, handler, elt)` | `removeEventListener()` |
| `htmx.location(path)` | `htmx.ajax('GET', path)` |
| `htmx.logAll()` | `htmx.config.logAll = true` |
| `htmx.logNone()` | `htmx.config.logAll = false` |

### Renamed Methods

- `htmx.defineExtension()` → `htmx.registerExtension()`

### Still Available

- `htmx.ajax()`
- `htmx.config`
- `htmx.find()`
- `htmx.findAll()`
- `htmx.on()`
- `htmx.onLoad()` (now listens on `htmx:after:process`)
- `htmx.parseInterval()`
- `htmx.process()`
- `htmx.swap()`
- `htmx.trigger()`

## Swap Style Changes

### New Swap Styles

- `innerMorph` / `outerMorph`: Morph swaps using idiomorph algorithm
- `textContent`: Set text content (no HTML parsing)
- `delete`: Remove target element entirely

### Scroll Modifier Syntax Changed

**htmx 2:**
```html
<div hx-swap="innerHTML show:#other:top">Load</div>
```

**htmx 4:**
```html
<div hx-swap="innerHTML show:top showTarget:#other">Load</div>
<div hx-swap="innerHTML scroll:bottom scrollTarget:#other">Load</div>
```

Use separate keys for scroll position and target.

### Swap Style Aliases

New convenient aliases:
- `before` → `beforebegin`
- `after` → `afterend`
- `prepend` → `afterbegin`
- `append` → `beforeend`

## Migration Checklist

### Phase 1: Preparation

- [ ] Backup current application
- [ ] Set up test environment
- [ ] Document custom extensions in use
- [ ] List all htmx attributes used in codebase
- [ ] Identify custom event handlers

### Phase 2: Initial Upgrade

- [ ] Update htmx script URL to 4.0
- [ ] Load `htmx-2-compat` extension
- [ ] Verify application still works
- [ ] Test all major user flows

### Phase 3: Attribute Migration

- [ ] Rename `hx-disable` to `hx-ignore`
- [ ] Rename `hx-disabled-elt` to `hx-disable`
- [ ] Add `:inherited` to inherited attributes
- [ ] Remove `hx-ext` attributes, add script includes
- [ ] Replace `hx-vars` with `hx-vals` and `js:` prefix
- [ ] Replace `hx-request` with `hx-config`

### Phase 4: Event Migration

- [ ] Update event names in JavaScript handlers
- [ ] Update `hx-on` attributes with new event names
- [ ] Consolidate error handlers to `htmx:error`
- [ ] Remove validation event handlers (use native)

### Phase 5: Configuration Updates

- [ ] Rename config options (`defaultSwapStyle` → `defaultSwap`, etc.)
- [ ] Set appropriate timeout value
- [ ] Configure error response handling
- [ ] Update history configuration if needed

### Phase 6: Testing

- [ ] Test all AJAX requests
- [ ] Test form submissions
- [ ] Test attribute inheritance
- [ ] Test error handling (4xx/5xx responses)
- [ ] Test history navigation
- [ ] Test real-time features (SSE/WebSocket if used)
- [ ] Test extensions

### Phase 7: Remove Compatibility Layer

- [ ] Gradually remove `htmx-2-compat` extension
- [ ] Fix any remaining htmx 2-only features
- [ ] Final testing without compatibility layer

## Common Migration Issues

### "Inheritance Not Working"

**Problem:** Attributes not inheriting down DOM tree.

**Solution:** Add `:inherited` modifier:
```html
<div hx-confirm:inherited="Are you sure?">
  <button hx-delete="/item">Delete</button>
</div>
```

### "Error Responses Not Showing"

**Problem:** 4xx/5xx responses not appearing.

**Solution A:** Configure to swap errors:
```javascript
// Default in htmx 4 - errors DO swap
// If using compat extension, remove it or configure:
htmx.config.noSwap = [204, 304];
```

**Solution B:** Design error responses as HTML:
```html
<!-- Server returns valid HTML for all status codes -->
<div class="error">Please fix errors</div>
```

### "Events Not Firing"

**Problem:** Event handlers not triggered.

**Solution:** Update event names:
```javascript
// Old
document.addEventListener('htmx:beforeRequest', handler);

// New
document.addEventListener('htmx:before:request', handler);
```

### "Form Data Not Sending with DELETE"

**Problem:** `hx-delete` not including form inputs.

**Solution:** Add explicit include:
```html
<button hx-delete="/item" hx-include="closest form">Delete</button>
```

## Getting Help

- [htmx 4 Documentation](https://four.htmx.org)
- [GitHub Discussions](https://github.com/bigskysoftware/htmx/discussions)
- [Discord Community](https://htmx.org/discord)
- [Migration Patterns](https://four.htmx.org/patterns)
