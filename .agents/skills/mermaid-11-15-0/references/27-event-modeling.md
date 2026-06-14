# Event Modeling Reference

## Description

Event Modeling diagrams describe systems by showing how information changes over time. Entities are organized in swimlanes forming a timeline. Relations among entities are inferred by default for rapid creation.

> **Note:** Uses `eventmodeling` keyword. (v11.15.0+)

## Basic Syntax

```mermaid
eventmodeling
    tf 01 ui CartUI
    tf 02 cmd AddItem
    tf 03 evt ItemAdded
```

## Time Frames

Time frames are the key building blocks, typed by entity type:

| Token (compact) | Token (relaxed) | Entity Type |
|-----------------|-----------------|-------------|
| `tf` | `timeframe` | Time frame declaration |
| `ui` | `ui` | User Interface / View |
| `cmd` | `command` | Command |
| `evt` | `event` | Event |
| `proc` | `processor` | Processor |

### Compact Notation

```mermaid
eventmodeling
    tf 01 ui CartUI
    tf 02 cmd AddItem
    tf 03 evt ItemAdded
```

### Relaxed Notation

```mermaid
eventmodeling
    timeframe 01 ui CartUI
    timeframe 02 command AddItem
    timeframe 03 event ItemAdded
```

## Entity Types

### UI (User Interface / Read Model)

```mermaid
eventmodeling
    tf 01 ui ShoppingCartView
```

### Command

```mermaid
eventmodeling
    tf 02 cmd AddItemToCart
```

### Event

```mermaid
eventmodeling
    tf 03 evt ItemAddedToCart
```

### Processor

```mermaid
eventmodeling
    tf 04 proc InventoryProcessor
```

## Commands and Events with Properties

```mermaid
eventmodeling
    tf 01 ui CartUI
    tf 02 cmd AddItem {
        itemId: string
        quantity: number
    }
    tf 03 evt ItemAdded {
        itemId: string
        quantity: number
        timestamp: date
    }
```

## Relationships

Relationships between entities are inferred by default based on timeline order. Explicit relationships can be declared:

```mermaid
eventmodeling
    tf 01 ui CartUI
    tf 02 cmd AddItem
    tf 03 evt ItemAdded
    tf 04 cmd UpdateInventory
    tf 05 evt InventoryUpdated
```

## Examples

### Shopping Cart Flow

```mermaid
eventmodeling
    title Shopping Cart

    tf 01 ui CartUI
    tf 02 cmd AddItem
    tf 03 evt ItemAdded
    tf 04 cmd RemoveItem
    tf 05 evt ItemRemoved
    tf 06 cmd Checkout
    tf 07 evt OrderPlaced
    tf 08 ui OrderConfirmation
```

### With Properties

```mermaid
eventmodeling
    title User Registration

    tf 01 ui RegistrationForm
    tf 02 cmd RegisterUser {
        username: string
        email: string
        password: string
    }
    tf 03 evt UserRegistered {
        userId: string
        username: string
        email: string
    }
    tf 04 cmd SendWelcomeEmail
    tf 05 evt WelcomeEmailSent {
        userId: string
    }
    tf 06 ui UserProfile
```

### Complex Workflow

```mermaid
eventmodeling
    title Order Processing

    tf 01 ui ProductCatalog
    tf 02 cmd BrowseProducts
    tf 03 evt ProductsViewed
    tf 04 cmd AddToCart
    tf 05 evt ItemAddedToCart
    tf 06 cmd ProceedToCheckout
    tf 07 evt PaymentProcessed
    tf 08 proc OrderProcessor
    tf 09 evt OrderConfirmed
    tf 10 cmd ShipOrder
    tf 11 evt OrderShipped
    tf 12 ui OrderTracking
```
