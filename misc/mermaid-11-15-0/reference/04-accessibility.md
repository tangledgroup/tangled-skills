# Accessibility

## Contents
- accTitle (Short Descriptive Title)
- accDescr (Single-Line Description)
- accDescr (Multi-Line Description)
- aria-roledescription and aria-labelledby
- Per-Diagram Examples

## Overview

Mermaid supports accessibility attributes that generate proper ARIA tags in the rendered SVG, making diagrams accessible to screen readers. Use `accTitle` for a short title and `accDescr` for a detailed description.

## accTitle (Short Descriptive Title)

Place at the top of diagram code. Renders as `<title>` inside the SVG.

```mermaid
flowchart LR
    accTitle: Login Flow
    A --> B
```

## accDescr (Single-Line Description)

Use `accDescr:` followed by a single line of text. Renders as `<desc>`.

```mermaid
sequenceDiagram
    accTitle: API Request Sequence
    accDescr: Client sends request, server validates and responds.
    Client->>Server: GET /api/data
    Server-->>Client: 200 OK
```

## accDescr (Multi-Line Description)

Use `accDescr { ... }` without a colon for multi-line descriptions.

```mermaid
flowchart LR
    accTitle: Deployment Pipeline
    accDescr {
        This diagram shows the CI/CD pipeline stages.
        Code is committed, tested, built, and deployed to production.
        Each stage has automated quality gates.
    }
    Commit --> Test --> Build --> Deploy
```

## aria-roledescription and aria-labelledby

Mermaid automatically adds `aria-roledescription="mermaid diagram"` to the SVG root element. The title is linked via `aria-labelledby`. This ensures screen readers announce the diagram type and read the title.

## Per-Diagram Examples

### Flowchart
```mermaid
flowchart LR
    accTitle: Order Processing
    accDescr: Customer places order, system validates inventory, processes payment, ships item.
    Order --> Validate --> Payment --> Ship
```

### Sequence Diagram
```mermaid
sequenceDiagram
    accTitle: Authentication Flow
    accDescr {
        User enters credentials.
        Browser sends POST to auth endpoint.
        Server validates against database.
        Token returned on success.
    }
    User->>Browser: Enter credentials
    Browser->>Server: POST /auth
    Server->>DB: Query user
    DB-->>Server: User data
    Server-->>Browser: JWT token
```

### Gantt
```mermaid
gantt
    accTitle: Project Timeline
    accDescr: Three-month project with planning, development, and deployment phases.
    section Planning
    Requirements :2024-01-01, 14d
```

### Class Diagram
```mermaid
classDiagram
    accTitle: User System Classes
    accDescr: Core classes for user management including User, Role, and Permission.
    class User
    class Role
    User "1" -- "*" Role
```

### State Diagram
```mermaid
stateDiagram-v2
    accTitle: Order States
    accDescr: Order lifecycle from created through shipped or cancelled.
    [*] --> Created
    Created --> Shipped
    Created --> Cancelled
```

### ER Diagram
```mermaid
erDiagram
    accTitle: E-Commerce Schema
    accDescr: Customers place orders, orders contain items, items reference products.
    CUSTOMER ||--o{ ORDER : places
    ORDER ||--|{ ITEM : contains
```

### Pie Chart
```mermaid
pie
    accTitle: Budget Allocation
    accDescr: Annual budget split across engineering, marketing, and operations.
    "Engineering" : 50
    "Marketing" : 30
    "Operations" : 20
```
