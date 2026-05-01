# Out-of-Band Swaps

## Overview

Out-of-band (OOB) swaps let you update DOM elements elsewhere on the page from a single response, piggybacking updates alongside the main target swap.

## `hx-swap-oob`

Mark an element in your server response with `hx-swap-oob` to swap it into the DOM at a location other than the primary target:

```html
<!-- Server response -->
<div>
    <!-- This goes to the normal hx-target -->
    <p>Main content update</p>
</div>

<!-- This swaps into #alerts regardless of the target -->
<div id="alerts" hx-swap-oob="true">
    Saved!
</div>
```

The first `div` swaps into the target normally. The second `div` replaces the element with `id="alerts"` on the page and does not appear in the target.

### Swap Values

`hx-swap-oob` accepts:

- **`true`** or **`outerHTML`** — Swap inline (equivalent)
- Any valid `hx-swap` value — Use that swap strategy, stripping the encapsulating tag
- Any swap value followed by `:<CSS selector>` — Target specific elements

```html
<!-- Append to #notifications -->
<div hx-swap-oob="beforeend:#notifications">
    New notification
</div>
```

If no selector is given, htmx finds the element with a matching ID.

### Alternate Swap Strategies

When using strategies other than `true` or `outerHTML`, encapsulating tags are stripped. Wrap returned data with appropriate container tags:

```html
<!-- Inserting <tr> into a table with <tbody> -->
<tbody hx-swap-oob="beforeend:#table tbody">
    <tr>...</tr>
</tbody>

<!-- Plain table -->
<table hx-swap-oob="beforeend:#table2">
    <tr>...</tr>
</table>

<!-- List items wrapped in container -->
<ul hx-swap-oob="beforeend:#list1">
    <li>...</li>
</ul>
```

### Template Tags for Tricky Elements

Use `<template>` to encapsulate elements that can't stand alone in the DOM (`<tr>`, `<td>`, `<th>`, `<thead>`, `<tbody>`, `<tfoot>`, `<colgroup>`, `<caption>`, `<col>`, `<li>`):

```html
<div>
    <!-- main response content -->
</div>
<template>
    <tr id="row" hx-swap-oob="true">
        <td>New row data</td>
    </tr>
</template>
```

Template tags are removed from the final page content.

### SVG Elements

SVG uses a specific XML namespace. Wrap SVG content in `<template>` to prevent child elements from breaking during swap:

```html
<template>
    <svg id="chart" hx-swap-oob="true">
        <!-- svg content -->
    </svg>
</template>
```

## `hx-select`

Select specific content from the response before swapping. Useful when the server returns a full HTML document but you only want a fragment:

```html
<div hx-get="/page" hx-select="#main-content">
    Loading...
</div>
```

Only the element matching `#main-content` from the response is swapped in.

## `hx-select-oob`

Select OOB content using a CSS selector rather than matching by ID:

```html
<div hx-get="/page" hx-select-oob="#sidebar">
    ...
</div>
```

In the response, the element matching `#sidebar` is swapped into its matching position on the page.

## Preserving Elements (`hx-preserve`)

Keep certain elements unchanged between requests:

```html
<div hx-get="/update" hx-target="this" hx-swap="outerHTML">
    <div id="keep-me" hx-preserve="true">I stay</div>
    <p>This gets replaced</p>
</div>
```

Elements with `hx-preserve` are not replaced during the swap. They retain their current state, event listeners, and child content.

## Nested OOB Swaps

By default (`htmx.config.allowNestedOobSwaps = true`), OOB swaps within nested response elements are processed. Set to `false` to disable:

```js
htmx.config.allowNestedOobSwaps = false;
```
