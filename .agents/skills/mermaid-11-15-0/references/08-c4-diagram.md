# C4 Diagram Reference

## Description

C4 model diagrams represent software architecture at different abstraction levels. Compatible with plantUML C4 syntax. Four diagram types: Context, Container, Component, Dynamic, and Deployment.

> **Note:** Experimental diagram — syntax may change in future releases.

## Diagram Types

| Keyword | Level | Purpose |
|---------|-------|---------|
| `C4Context` | System Context | System and its users/external systems |
| `C4Container` | Container | Containers (apps, databases, file systems) within a system |
| `C4Component` | Component | Components within a container |
| `C4Dynamic` | Dynamic | Runtime interactions between containers/components |
| `C4Deployment` | Deployment | Deployment topology |

## Elements

### People

```mermaid
C4Context
    Person(user, "End User", "A user of the system")
    Person_Ext(admin, "Admin", "External administrator")
```

### Systems

```mermaid
C4Context
    System(webApp, "Web Application", "The main web application")
    SystemDb(database, "Database", "Stores application data")
    SystemQueue(queue, "Message Queue", "Async message processing")
    System_Ext(email, "Email System", "External email service")
```

### Containers

```mermaid
C4Container
    Container(webApp, "Web App", "react", "User-facing web interface")
    Container(api, "API", "nodejs", "Backend REST API")
    ContainerDb(db, "Database", "postgresql", "Application data store")
    ContainerQueue(queue, "Message Queue", "rabbitmq", "Async processing")
```

### Components

```mermaid
C4Component
    Component(auth, "Auth Service", "Handles authentication")
    Component(api, "REST API", "Exposes REST endpoints")
    ComponentDb(db, "Data Store", "Persisted data")
```

### Boundaries

```mermaid
C4Context
    Enterprise_Boundary(b0, "Company Boundary") {
        System(sys, "System", "Description")
    }
    System_Boundary(b1, "Web Platform") {
        Container(web, "Web App", "react", "Frontend")
        Container(api, "API", "nodejs", "Backend")
    }
    Boundary(b2, "External Services", "boundary") {
        System_Ext(email, "Email", "SMTP service")
    }
```

## Relationships

```mermaid
C4Context
    Rel(user, webApp, "Uses")
    Rel(webApp, api, "Calls", "HTTPS")
    BiRel(user, webApp, "Interacts with")
    Rel_U(user, webApp, "Uses", "HTTPS")
    Rel_D(webApp, db, "Reads/Writes", "TCP")
    Rel_R(api, queue, "Publishes to")
    Rel_L(queue, worker, "Consumes from")
```

### Relationship Directions

| Keyword | Direction |
|---------|-----------|
| `Rel` | Auto (default) |
| `Rel_U` | Up |
| `Rel_D` | Down |
| `Rel_L` | Left |
| `Rel_R` | Right |
| `BiRel` | Bidirectional |

## Styling

```mermaid
C4Context
    UpdateElementStyle(user, $fontColor="red", $bgColor="grey", $borderColor="red")
    UpdateRelStyle(user, webApp, $textColor="blue", $lineColor="blue", $offsetY="-10")
```

### Style Properties

| Property | Description |
|----------|-------------|
| `$fontColor` | Text color |
| `$bgColor` | Background color |
| `$borderColor` | Border color |
| `$textColor` | Relationship text color |
| `$lineColor` | Relationship line color |
| `$offsetX` | Horizontal offset |
| `$offsetY` | Vertical offset |

## Layout

```mermaid
C4Context
    UpdateLayoutConfig($c4ShapeInRow="3", $c4BoundaryInRow="1")
```

## Examples

### System Context Diagram

```mermaid
C4Context
    title System Context Diagram

    Person(user, "Customer", "A customer of the system")
    Person(admin, "Admin", "System administrator")

    System_Boundary(system, "E-Commerce System") {
        System(webApp, "Web Application", "Main web application")
        System(api, "REST API", "Backend API service")
        SystemDb(db, "Database", "Stores all data")
    }

    System_Ext(email, "Email Service", "SMTP server")
    System_Ext(payment, "Payment Gateway", "Stripe/PayPal")

    Rel(user, webApp, "Uses", "HTTPS")
    Rel(admin, webApp, "Manages", "HTTPS")
    Rel(webApp, api, "Calls", "HTTPS")
    Rel(api, db, "Reads/Writes", "TCP")
    Rel(api, payment, "Processes payments", "HTTPS")
    Rel(api, email, "Sends emails", "SMTP")
```

### Container Diagram

```mermaid
C4Container
    title Container Diagram

    Person(user, "User", "App user")

    Container_Spa(spa, "Single Page App", "react", "User-facing interface")
    Container(mobile, "Mobile App", "flutter", "Mobile application")
    Container(api, "API Service", "nodejs", "Backend API")
    ContainerDb(db, "Database", "postgresql", "Data store")
    Container(queue, "Message Queue", "rabbitmq", "Async jobs")

    Rel(user, spa, "Uses")
    Rel(user, mobile, "Uses")
    Rel(spa, api, "Calls", "HTTPS/JSON")
    Rel(mobile, api, "Calls", "HTTPS/JSON")
    Rel(api, db, "Reads/Writes", "TCP")
    Rel(api, queue, "Publishes to", "AMQP")
```
