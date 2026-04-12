# DaisyUI Display Components

This guide covers display and content components in DaisyUI 5.5 including cards, alerts, badges, avatars, tables, stats, and timelines.

## Card

### Basic Card

```html
<div class="card w-96 bg-base-100 shadow-xl">
  <div class="card-body">
    <h2 class="card-title">Card Title</h2>
    <p>Card content goes here.</p>
    <div class="card-actions">
      <button class="btn btn-primary">Action</button>
    </div>
  </div>
</div>
```

### Card with Image

```html
<div class="card w-96 bg-base-100 shadow-xl">
  <figure><img src="https://picsum.photos/400/300" alt="Description" /></figure>
  <div class="card-body">
    <h2 class="card-title">Card Title</h2>
    <p>Card description.</p>
    <div class="card-actions">
      <button class="btn btn-primary">Learn More</button>
    </div>
  </div>
</div>
```

### Card with Image Bottom

```html
<div class="card w-96 bg-base-100 shadow-xl">
  <div class="card-body">
    <h2 class="card-title">Title First</h2>
    <p>Content above image.</p>
  </div>
  <figure><img src="https://picsum.photos/400/300" alt="Bottom image" /></figure>
</div>
```

### Card Side Layout

```html
<div class="card card-side bg-base-100 shadow-xl w-96">
  <figure><img src="https://picsum.photos/200/300" alt="Side image" /></figure>
  <div class="card-body">
    <h2 class="card-title">Side Card</h2>
    <p>Image on the side, content on the right.</p>
    <div class="card-actions">
      <button class="btn btn-primary">Action</button>
    </div>
  </div>
</div>
```

### Card with Full Image

```html
<div class="card image-full w-96 shadow-xl">
  <figure><img src="https://picsum.photos/400/300" alt="Full image" /></figure>
  <div class="card-body">
    <h2 class="card-title text-white">Overlay Title</h2>
  </div>
</div>
```

### Card Styles

```html
<!-- Border card -->
<div class="card card-border w-96 bg-base-100 shadow-xl">
  <div class="card-body">Border card</div>
</div>

<!-- Dash card -->
<div class="card card-dash w-96 bg-base-100 shadow-xl">
  <div class="card-body">Dash card</div>
</div>
```

### Card Sizes

| Size | Class |
|------|-------|
| Extra Small | `card-xs` |
| Small | `card-sm` |
| Medium | `card-md` |
| Large | `card-lg` |
| Extra Large | `card-xl` |

```html
<div class="card card-sm w-96 bg-base-100 shadow-xl">
  <div class="card-body">Small card</div>
</div>

<div class="card card-lg w-96 bg-base-100 shadow-xl">
  <div class="card-body">Large card</div>
</div>
```

### Card Compact

```html
<div class="card card-compact w-96 bg-base-100 shadow-xl">
  <div class="card-body">
    <h2 class="card-title">Compact Title</h2>
    <p>Less padding for compact layout.</p>
  </div>
</div>
```

### Responsive Card

```html
<div class="card w-full max-w-sm md:w-96 lg:w-96 bg-base-100 shadow-xl">
  <figure><img src="https://picsum.photos/400/300" alt="Responsive" /></figure>
  <div class="card-body">
    <h2 class="card-title">Responsive Card</h2>
    <p>Adapts to screen size.</p>
  </div>
</div>
```

## Alert

### Basic Alert

```html
<div class="alert" role="alert">
  <span>This is a default alert message.</span>
</div>
```

### Alert Colors

```html
<div class="alert alert-info" role="alert">
  <span>Info message</span>
</div>

<div class="alert alert-success" role="alert">
  <span>Success message</span>
</div>

<div class="alert alert-warning" role="alert">
  <span>Warning message</span>
</div>

<div class="alert alert-error" role="alert">
  <span>Error message</span>
</div>
```

### Alert Styles

```html
<!-- Outline style -->
<div class="alert alert-outline alert-success" role="alert">
  <span>Outline success</span>
</div>

<!-- Dash style -->
<div class="alert alert-dash alert-warning" role="alert">
  <span>Dash warning</span>
</div>

<!-- Soft style -->
<div class="alert alert-soft alert-error" role="alert">
  <span>Soft error</span>
</div>
```

### Alert with Icon

```html
<div class="alert alert-success" role="alert">
  <svg xmlns="http://www.w3.org/2000/svg" class="shrink-0 h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
  </svg>
  <span>Success with icon</span>
</div>
```

### Alert with Action

```html
<div class="alert alert-info" role="alert">
  <svg xmlns="http://www.w3.org/2000/svg" class="shrink-0 h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
  </svg>
  <span>Info message with action</span>
  <button class="btn btn-sm btn-outline">Dismiss</button>
</div>
```

### Alert Direction

```html
<!-- Horizontal (default) -->
<div class="alert alert-horizontal alert-success" role="alert">
  <span>Horizontal layout</span>
</div>

<!-- Vertical -->
<div class="alert alert-vertical alert-success" role="alert">
  <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
  </svg>
  <span>Vertical layout</span>
</div>
```

### Responsive Alert

```html
<div class="alert alert-sm:alert-horizontal alert-vertical alert-success" role="alert">
  <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
  </svg>
  <span>Vertical on mobile, horizontal on larger screens</span>
</div>
```

## Badge

### Basic Badge

```html
<span class="badge">Badge</span>
```

### Badge Colors

```html
<span class="badge badge-neutral">Neutral</span>
<span class="badge badge-primary">Primary</span>
<span class="badge badge-secondary">Secondary</span>
<span class="badge badge-accent">Accent</span>
<span class="badge badge-info">Info</span>
<span class="badge badge-success">Success</span>
<span class="badge badge-warning">Warning</span>
<span class="badge badge-error">Error</span>
```

### Badge Styles

```html
<span class="badge badge-outline">Outline</span>
<span class="badge badge-dash">Dash</span>
<span class="badge badge-soft">Soft</span>
<span class="badge badge-ghost">Ghost</span>
```

### Badge Sizes

| Size | Class |
|------|-------|
| Extra Small | `badge-xs` |
| Small | `badge-sm` |
| Medium | `badge-md` |
| Large | `badge-lg` |
| Extra Large | `badge-xl` |

```html
<span class="badge badge-xs">XS</span>
<span class="badge badge-sm">SM</span>
<span class="badge badge-md">MD</span>
<span class="badge badge-lg">LG</span>
<span class="badge badge-xl">XL</span>
```

### Badge with Icon

```html
<span class="badge badge-primary gap-2">
  <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
  </svg>
  Notifications
</span>
```

### Badge in Button

```html
<button class="btn btn-primary gap-2">
  Messages
  <span class="badge badge-secondary">3</span>
</button>
```

## Avatar

### Basic Avatar

```html
<div class="avatar">
  <div class="w-16 rounded-full">
    <img src="https://picsum.photos/80" alt="User avatar" />
  </div>
</div>
```

### Avatar Group

```html
<div class="avatar-group -space-x-6 rtl:space-x-reverse">
  <div class="avatar">
    <div class="w-12 rounded-full ring ring-base-100">
      <img src="https://picsum.photos/48?random=1" alt="" />
    </div>
  </div>
  <div class="avatar">
    <div class="w-12 rounded-full ring ring-base-100">
      <img src="https://picsum.photos/48?random=2" alt="" />
    </div>
  </div>
  <div class="avatar">
    <div class="w-12 rounded-full ring ring-base-100">
      <img src="https://picsum.photos/48?random=3" alt="" />
    </div>
  </div>
  <div class="avatar placeholder">
    <div class="w-12 rounded-full ring ring-base-100 bg-neutral text-neutral-content">
      <span>+5</span>
    </div>
  </div>
</div>
```

### Avatar Online/Offline Status

```html
<!-- Online -->
<div class="avatar avatar-online">
  <div class="w-12 rounded-full">
    <img src="https://picsum.photos/48" alt="" />
  </div>
</div>

<!-- Offline -->
<div class="avatar avatar-offline">
  <div class="w-12 rounded-full">
    <img src="https://picsum.photos/48" alt="" />
  </div>
</div>
```

### Avatar Placeholder

```html
<div class="avatar placeholder">
  <div class="w-16 rounded-full bg-neutral text-neutral-content">
    <span>JD</span>
  </div>
</div>
```

### Avatar with Custom Shape

```html
<!-- Squircle -->
<div class="avatar">
  <div class="w-16 mask-squircle">
    <img src="https://picsum.photos/80" alt="" />
  </div>
</div>

<!-- Hexagon -->
<div class="avatar">
  <div class="w-16 mask-hexagon">
    <img src="https://picsum.photos/80" alt="" />
  </div>
</div>

<!-- Circle -->
<div class="avatar">
  <div class="w-16 mask-circle">
    <img src="https://picsum.photos/80" alt="" />
  </div>
</div>
```

## Table

### Basic Table

```html
<div class="overflow-x-auto">
  <table class="table">
    <thead>
      <tr>
        <th>Name</th>
        <th>Role</th>
        <th>Status</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td>
          <div class="flex items-center gap-3">
            <div class="avatar">
              <div class="w-10 rounded-full">
                <img src="https://picsum.photos/40?random=1" alt="" />
              </div>
            </div>
            <div>
              <div class="font-bold">John Doe</div>
              <div class="text-sm opacity-50">john@example.com</div>
            </div>
          </div>
        </td>
        <td>Developer</td>
        <td><span class="badge badge-success">Active</span></td>
      </tr>
    </tbody>
  </table>
</div>
```

### Table with Zebra Striping

```html
<div class="overflow-x-auto">
  <table class="table table-zebra">
    <thead>
      <tr>
        <th>#</th>
        <th>Name</th>
        <th>Status</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td>1</td>
        <td>Item 1</td>
        <td>Active</td>
      </tr>
      <tr>
        <td>2</td>
        <td>Item 2</td>
        <td>Inactive</td>
      </tr>
    </tbody>
  </table>
</div>
```

### Table Sizes

| Size | Class |
|------|-------|
| Extra Small | `table-xs` |
| Small | `table-sm` |
| Medium | `table-md` |
| Large | `table-lg` |
| Extra Large | `table-xl` |

```html
<div class="overflow-x-auto">
  <table class="table table-sm">
    <thead>
      <tr>
        <th>Small Table</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td>Content</td>
      </tr>
    </tbody>
  </table>
</div>
```

### Table with Pinned Rows/Columns

```html
<!-- Pin rows -->
<div class="overflow-x-auto">
  <table class="table table-pin-rows">
    <thead>
      <tr>
        <th>Pinned Header</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td>Row 1</td>
      </tr>
      <tr>
        <td>Row 2</td>
      </tr>
    </tbody>
    <tfoot>
      <tr>
        <th>Pinned Footer</th>
      </tr>
    </tfoot>
  </table>
</div>

<!-- Pin columns -->
<div class="overflow-x-auto">
  <table class="table table-pin-cols">
    <thead>
      <tr>
        <th>#</th>
        <th>Name</th>
        <th>Email</th>
        <th>Role</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td>1</td>
        <td>John Doe</td>
        <td>john@example.com</td>
        <td>Developer</td>
      </tr>
    </tbody>
  </table>
</div>
```

## Stats

### Basic Stats

```html
<div class="stats shadow w-full">
  <div class="stat">
    <div class="stat-title">Total Users</div>
    <div class="stat-value text-primary">1,234</div>
    <div class="stat-desc">↗︎ 14% more than last month</div>
  </div>
  
  <div class="stat">
    <div class="stat-title">Revenue</div>
    <div class="stat-value text-secondary">$12,345</div>
    <div class="stat-desc">↘︎ 4% less than last month</div>
  </div>
  
  <div class="stat">
    <div class="stat-title">Active Sessions</div>
    <div class="stat-value">567</div>
    <div class="stat-desc">↗︎ 23% increase</div>
  </div>
</div>
```

### Stats with Figure

```html
<div class="stats shadow w-full">
  <div class="stat">
    <div class="stat-figure text-primary">
      <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" class="inline-block w-8 h-8 stroke-current">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 11V7a4 4 0 00-8 0v4M5 9h14l1 12H4L5 9z" />
      </svg>
    </div>
    <div class="stat-title">Total Sales</div>
    <div class="stat-value text-primary">$1,234</div>
    <div class="stat-desc">↗︎ 20% more sales</div>
  </div>
  
  <div class="stat">
    <div class="stat-figure text-secondary">
      <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" class="inline-block w-8 h-8 stroke-current">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
      </svg>
    </div>
    <div class="stat-title">Total Users</div>
    <div class="stat-value text-secondary">3,456</div>
    <div class="stat-desc">↘︎ 2% less users</div>
  </div>
</div>
```

### Stats Vertical

```html
<div class="stats stats-vertical shadow w-56">
  <div class="stat">
    <div class="stat-title">Downloads</div>
    <div class="stat-value text-primary">1,234</div>
  </div>
  
  <div class="stat">
    <div class="stat-title">Revenue</div>
    <div class="stat-value text-secondary">$567</div>
  </div>
</div>
```

### Stats with Actions

```html
<div class="stats shadow w-full">
  <div class="stat">
    <div class="stat-figure text-primary">📊</div>
    <div class="stat-title">Total Views</div>
    <div class="stat-value text-primary">12,345</div>
    <div class="stat-desc">Last 30 days</div>
    <div class="stat-actions">
      <button class="btn btn-xs btn-primary">View Report</button>
    </div>
  </div>
</div>
```

## Timeline

### Basic Timeline

```html
<ul class="timeline">
  <li>
    <hr />
    <div class="timeline-middle">
      <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" class="h-5 w-5 text-primary">
        <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.857-9.809a.75.75 0 00-1.214-.882l-3.483 4.79-1.88-1.88a.75.75 0 10-1.06 1.061l2.5 2.5a.75.75 0 001.137-.089l4-5.5z" clip-rule="evenodd" />
      </svg>
    </div>
    <div class="timeline-start">Event 1</div>
    <hr />
  </li>
  
  <li>
    <hr />
    <div class="timeline-middle">
      <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" class="h-5 w-5 text-primary">
        <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.857-9.809a.75.75 0 00-1.214-.882l-3.483 4.79-1.88-1.88a.75.75 0 10-1.06 1.061l2.5 2.5a.75.75 0 001.137-.089l4-5.5z" clip-rule="evenodd" />
      </svg>
    </div>
    <div class="timeline-end">Event 2</div>
    <hr />
  </li>
  
  <li>
    <hr />
    <div class="timeline-middle">
      <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" class="h-5 w-5 text-primary">
        <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.857-9.809a.75.75 0 00-1.214-.882l-3.483 4.79-1.88-1.88a.75.75 0 10-1.06 1.061l2.5 2.5a.75.75 0 001.137-.089l4-5.5z" clip-rule="evenodd" />
      </svg>
    </div>
    <div class="timeline-start">Event 3</div>
    <hr />
  </li>
</ul>
```

### Timeline with Content

```html
<ul class="timeline timeline-snap-icon max-md:timeline-compact">
  <li>
    <hr />
    <div class="timeline-middle">
      <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" class="h-5 w-5 text-primary">
        <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.857-9.809a.75.75 0 00-1.214-.882l-3.483 4.79-1.88-1.88a.75.75 0 10-1.06 1.061l2.5 2.5a.75.75 0 001.137-.089l4-5.5z" clip-rule="evenodd" />
      </svg>
    </div>
    <div class="timeline-start timeline-box">
      <h3 class="font-bold">Project Started</h3>
      <p>Initial project setup and planning completed.</p>
    </div>
    <div class="timeline-end timeline-box opacity-0 md:opacity-100">
      <time>January 15, 2024</time>
    </div>
    <hr />
  </li>
  
  <li>
    <hr />
    <div class="timeline-middle">
      <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" class="h-5 w-5 text-primary">
        <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.857-9.809a.75.75 0 00-1.214-.882l-3.483 4.79-1.88-1.88a.75.75 0 10-1.06 1.061l2.5 2.5a.75.75 0 001.137-.089l4-5.5z" clip-rule="evenodd" />
      </svg>
    </div>
    <div class="timeline-end timeline-box">
      <h3 class="font-bold">Development Phase</h3>
      <p>Core features implemented and tested.</p>
    </div>
    <div class="timeline-start timeline-box opacity-0 md:opacity-100">
      <time>February 1, 2024</time>
    </div>
    <hr />
  </li>
  
  <li>
    <hr />
    <div class="timeline-middle">
      <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" class="h-5 w-5 text-primary">
        <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.857-9.809a.75.75 0 00-1.214-.882l-3.483 4.79-1.88-1.88a.75.75 0 10-1.06 1.061l2.5 2.5a.75.75 0 001.137-.089l4-5.5z" clip-rule="evenodd" />
      </svg>
    </div>
    <div class="timeline-start timeline-box">
      <h3 class="font-bold">Launched</h3>
      <p>Project successfully deployed to production.</p>
    </div>
    <div class="timeline-end timeline-box opacity-0 md:opacity-100">
      <time>March 15, 2024</time>
    </div>
    <hr />
  </li>
</ul>
```

## Progress

### Basic Progress

```html
<progress class="progress progress-primary" value="70" max="100"></progress>
```

### Progress Colors

```html
<progress class="progress progress-primary" value="70" max="100"></progress>
<progress class="progress progress-secondary" value="50" max="100"></progress>
<progress class="progress progress-accent" value="30" max="100"></progress>
<progress class="progress progress-success" value="80" max="100"></progress>
```

## Radial Progress

### Basic Radial Progress

```html
<div class="radial-progress" role="progressbar" aria-valuenow="75" aria-valuemin="0" aria-valuemax="100" style="--value:75;">
  75%
</div>
```

### Radial Progress with Custom Size

```html
<div class="radial-progress text-primary" role="progressbar" aria-valuenow="60" aria-valuemin="0" aria-valuemax="100" style="--value:60; --size:4rem;">
  60%
</div>
```

### Radial Progress without Text

```html
<div class="radial-progress" role="progressbar" aria-valuenow="85" aria-valuemin="0" aria-valuemax="100" style="--value:85;"></div>
```

## Loading

### Loading Styles

```html
<!-- Spinner -->
<span class="loading loading-spinner"></span>

<!-- Dots -->
<span class="loading loading-dots"></span>

<!-- Ring -->
<span class="loading loading-ring"></span>

<!-- Ball -->
<span class="loading loading-ball"></span>

<!-- Bars -->
<span class="loading loading-bars"></span>

<!-- Infinity -->
<span class="loading loading-infinity"></span>
```

### Loading Colors

```html
<span class="loading loading-spinner text-primary"></span>
<span class="loading loading-spinner text-secondary"></span>
<span class="loading loading-spinner text-accent"></span>
```

### Loading Sizes

| Size | Class |
|------|-------|
| Extra Small | `loading-xs` |
| Small | `loading-sm` |
| Medium | `loading-md` |
| Large | `loading-lg` |
| Extra Large | `loading-xl` |

```html
<span class="loading loading-spinner loading-sm"></span>
<span class="loading loading-spinner loading-md"></span>
<span class="loading loading-spinner loading-lg"></span>
```

### Loading in Button

```html
<button class="btn btn-primary" disabled>
  <span class="loading loading-spinner"></span>
  Loading...
</button>
```

## Skeleton

### Basic Skeleton

```html
<div class="skeleton h-4 w-full"></div>
```

### Skeleton Text

```html
<div class="flex items-center gap-4">
  <div class="skeleton rounded-full h-12 w-12"></div>
  <div class="flex-1 space-y-2">
    <div class="skeleton h-4 w-full"></div>
    <div class="skeleton h-4 w-5/6"></div>
    <div class="skeleton h-4 w-4/6"></div>
  </div>
</div>
```

### Skeleton Card

```html
<div class="card w-96 bg-base-100 shadow-xl">
  <figure class="py-10">
    <div class="skeleton h-40 w-full"></div>
  </figure>
  <div class="card-body space-y-3">
    <div class="skeleton h-6 w-1/2"></div>
    <div class="skeleton h-4 w-full"></div>
    <div class="skeleton h-4 w-full"></div>
    <div class="skeleton h-8 w-24"></div>
  </div>
</div>
```

## Status

### Basic Status

```html
<div class="badge badge-primary gap-2">
  <div class="status status-primary" aria-label="Primary status"></div>
  Processing
</div>
```

### Status Colors

```html
<div class="status status-primary"></div>
<div class="status status-secondary"></div>
<div class="status status-accent"></div>
<div class="status status-success"></div>
<div class="status status-warning"></div>
<div class="status status-error"></div>
```

### Status Sizes

| Size | Class |
|------|-------|
| Extra Small | `status-xs` |
| Small | `status-sm` |
| Medium | `status-md` |
| Large | `status-lg` |
| Extra Large | `status-xl` |

```html
<div class="status status-primary status-sm"></div>
<div class="status status-primary status-md"></div>
<div class="status status-primary status-lg"></div>
```

## Component Best Practices

1. **Use semantic colors** - Let themes control the color scheme
2. **Make components responsive** - Use Tailwind breakpoints for different screen sizes
3. **Include alt text** - All images should have descriptive alt attributes
4. **Test accessibility** - Ensure keyboard navigation and screen reader support
5. **Use loading states** - Show skeleton or loading indicators during data fetch
6. **Group related content** - Use cards to organize information logically
7. **Provide context** - Use alerts for important messages and feedback
