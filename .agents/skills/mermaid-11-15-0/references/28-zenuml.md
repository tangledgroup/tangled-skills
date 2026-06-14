# ZenUML Reference

## Description

ZenUML is an alternative sequence diagram syntax with a cleaner, more concise notation. Supports annotators (participant symbols), groups, and activation boxes. Different from the standard `sequenceDiagram` syntax.

## Basic Syntax

```mermaid
zenuml
    title Demo
    Alice->John: Hello John, how are you?
    John->Alice: Great!
    Alice->John: See you later!
```

## Participants

### Implicit Declaration

Participants appear on first use in messages.

### Explicit Declaration

```mermaid
zenuml
    title Declare participants
    Bob
    Alice
    Alice->Bob: Hi Bob
    Bob->Alice: Hi Alice
```

### Annotators (Symbol Types)

```mermaid
zenuml
    title Annotators
    @actor Alice
    @boundary Bob
    @control Carl
    @entity Dave
    Alice->Bob: Message
```

| Annotator | Symbol | Description |
|-----------|--------|-------------|
| `@actor` | Stick figure | Human participant |
| `@boundary` | Screen icon | UI/boundary component |
| `@control` | Circle with arrow | Control/logic component |
| `@entity` | Cylinder | Data/entity component |

## Message Types

| Syntax | Arrow Style | Description |
|--------|-------------|-------------|
| `A->B: msg` | Solid arrow | Synchronous |
| `A-->B: msg` | Dashed arrow | Asynchronous reply |
| `A=>B: msg` | Thick arrow | |
| `A~>B: msg` | Dotted arrow | |
| `A~~>B: msg` | Dotted dashed | |

## Groups

```mermaid
zenuml
    title Groups
    Alice
    Bob
    alt happy path
        Alice->Bob: Request
        Bob->Alice: Success
    else error
        Alice->Bob: Request
        Bob->Alice: Error
    end
```

### Supported Group Types

| Keyword | Purpose |
|---------|---------|
| `alt ... else ... end` | Conditional branches |
| `opt ... end` | Optional section |
| `loop ... end` | Repeating section |
| `par ... and ... end` | Parallel sections |
| `break ... end` | Break sequence |

## Notes

```mermaid
zenuml
    title Notes
    Alice
    Bob
    note over Alice: Note about Alice
    note over Alice, Bob: Note spanning both
```

## Activation Boxes

```mermaid
zenuml
    title Activation
    Alice
    Bob
    Alice->Bob: Request [activate Bob]
    Bob->Alice: Response [deactivate Bob]
```

## Examples

### Full Sequence

```mermaid
zenuml
    title User Login Flow
    @actor User
    @boundary LoginPage
    @control AuthController
    @entity UserDatabase

    User->LoginPage: Enter credentials
    LoginPage->AuthController: Validate login
    AuthController->UserDatabase: Query user
    UserDatabase-->AuthController: User data
    alt valid user
        AuthController-->LoginPage: Auth token
        LoginPage-->User: Redirect to dashboard
    else invalid user
        AuthController-->LoginPage: Error message
        LoginPage-->User: Show error
    end
```

### API Call

```mermaid
zenuml
    title REST API Flow
    Client
    @boundary API Gateway
    @control Order Service
    @entity Database

    Client->API Gateway: POST /orders
    API Gateway->Order Service: Create order
    Order Service->Database: Save order
    Database-->Order Service: Order ID
    Order Service-->API Gateway: 201 Created
    API Gateway-->Client: { id: 123 }

    note over Client, API Gateway: Request authenticated via JWT
```

### With Groups

```mermaid
zenuml
    title Retry Logic
    Client
    @control Service
    @entity Database

    loop retry up to 3 times
        Client->Service: Process request
        alt success
            Service-->Client: OK
        else failure
            Service-->Client: Error
            Client->Client: Wait and retry
        end
    end
```
