# Wardley Map Reference

## Description

Wardley Maps position components along two axes for strategic business analysis:
- **Y-axis (Visibility):** How visible/valuable a component is to users (0.0 = infrastructure, 1.0 = user-facing)
- **X-axis (Evolution):** How evolved/mature a component is (0.0 = novel, 1.0 = commodity/utility)

> **Note:** Uses `wardley-beta` keyword — experimental, syntax may evolve. (v11.14.0+)

## Basic Syntax

```mermaid
wardley-beta
    title Tea Shop Value Chain

    anchor Business [0.95, 0.63]
    component Cup of Tea [0.79, 0.61]
    component Tea [0.63, 0.81]
    component Hot Water [0.52, 0.80]
    component Kettle [0.43, 0.35]
    component Power [0.10, 0.70]

    Business -> Cup of Tea
    Cup of Tea -> Tea
    Cup of Tea -> Hot Water
    Hot Water -> Kettle
    Kettle -> Power
```

## Components

### Anchor (Root Component)

```
anchor Name [y, x]
```

The anchor is the root/top-level component of the value chain.

### Regular Components

```
component Name [y, x]
```

- `y` — Visibility (0.0 to 1.0)
- `x` — Evolution stage (0.0 to 1.0)

### Component Types

| Type | Keyword | Description |
|------|---------|-------------|
| Standard | `component` | Regular component |
| Anchor | `anchor` | Root component of value chain |

## Relationships

```
ComponentA -> ComponentB
```

- Directed dependency: A depends on B
- Multiple relationships supported

## Evolution Stages

Update a component's evolution position:

```mermaid
wardley-beta
    component Kettle [0.43, 0.35]
    evolve Kettle 0.62     %% Move to more evolved stage
```

## Notes

Add annotations at specific positions:

```mermaid
wardley-beta
    note "Standardising power allows Kettles to evolve faster" [0.30, 0.49]
```

## Styling

```mermaid
wardley-beta
    style Business fill:#f96,stroke:#333,stroke-width:2px
    style Power shape:cloud
```

### Shape Options

| Shape | Description |
|-------|-------------|
| `rectangle` | Default rectangle |
| `rounded-rectangle` | Rounded corners |
| `ellipse` | Ellipse/circle |
| `cloud` | Cloud shape |

## Configuration

| Parameter | Description | Default |
|-----------|-------------|---------|
| `xAxisLabel` | X-axis label text | `"Evolution"` |
| `yAxisLabel` | Y-axis label text | `"Visibility"` |
| `showXAxisLabels` | Show evolution stage labels | `true` |
| `showYAxisLabels` | Show visibility labels | `true` |

## Examples

### Software Architecture

```mermaid
wardley-beta
    title E-Commerce Platform

    anchor Online Shopping [0.95, 0.7]
    component User Interface [0.85, 0.6]
    component Product Catalog [0.75, 0.65]
    component Shopping Cart [0.70, 0.55]
    component Payment Processing [0.60, 0.85]
    component Order Management [0.55, 0.6]
    component Inventory System [0.45, 0.7]
    component Cloud Hosting [0.20, 0.95]
    component Internet [0.10, 1.0]

    Online Shopping -> User Interface
    User Interface -> Product Catalog
    User Interface -> Shopping Cart
    Shopping Cart -> Payment Processing
    Shopping Cart -> Order Management
    Order Management -> Inventory System
    Product Catalog -> Cloud Hosting
    Payment Processing -> Cloud Hosting
    Cloud Hosting -> Internet

    evolve Cloud Hosting 0.95
    evolve Internet 1.0
```

### With Notes

```mermaid
wardley-beta
    title Mobile App Value Chain

    anchor Mobile App [0.9, 0.6]
    component App Store [0.7, 0.9]
    component Push Notifications [0.6, 0.85]
    component User Data [0.5, 0.7]
    component API Gateway [0.4, 0.75]
    component Cloud Services [0.2, 0.95]
    component Electricity [0.05, 1.0]

    Mobile App -> App Store
    Mobile App -> Push Notifications
    Push Notifications -> User Data
    User Data -> API Gateway
    API Gateway -> Cloud Services
    Cloud Services -> Electricity

    note "Commoditized infrastructure — buy, don't build" [0.15, 0.9]
    note "Differentiation opportunity here" [0.75, 0.5]
```
