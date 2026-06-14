# Sequence Diagram Reference

## Description

Sequence diagrams show how processes operate with one another and in what order. Participants appear as vertical lifelines; messages are horizontal arrows between them.

> **Warning:** The word `end` can break sequence diagrams. Wrap in quotes, parentheses, or brackets.

## Basic Syntax

```mermaid
sequenceDiagram
    Alice->>John: Hello John, how are you?
    John-->>Alice: Great!
    Alice-)John: See you later!
```

## Participants

### Implicit Declaration

Participants are declared by first appearance in messages.

### Explicit Declaration

```mermaid
sequenceDiagram
    participant Alice
    participant Bob
    Bob->>Alice: Hi Alice
```

### Actor Symbol

```mermaid
sequenceDiagram
    actor Alice
    actor Bob
```

### Boundary / Control / Entity Symbols

```mermaid
sequenceDiagram
    participant Alice@{ "type" : "boundary" }
    participant Bob@{ "type" : "control" }
    participant Carl@{ "type" : "entity" }
```

### Aliases

```mermaid
sequenceDiagram
    participant A as Alice
    participant B as Bob
```

## Message Types

| Syntax | Arrow Style | Description |
|--------|-------------|-------------|
| `A->>B: msg` | Solid arrow | Synchronous call |
| `A-->B: msg` | Dashed arrow | Asynchronous reply |
| `A->B: msg` | Solid line, no arrowhead | |
| `A-x B: msg` | Solid line with cross | Deleted message |
| `A--)B: msg` | Dashed arrow | Async message |
| `A-)B: msg` | Thin dashed arrow | |
| `A==B: msg` | Note/sync return | |

## Notes

```mermaid
sequenceDiagram
    participant A
    participant B
    note right of A: Note on the right side of A
    note left of B: Note on the left side of B
    note over A,B: Note spanning both participants
    note over A: Note over A
```

## Activations

```mermaid
sequenceDiagram
    participant A
    participant B
    activate A
    A->>B: Work request
    activate B
    B-->>A: Work done
    deactivate B
    deactivate A
```

Or implicit (auto-activation):

```mermaid
sequenceDiagram
    Alice->>Bob: Hello Bob, how are you?
    activate Bob
    Bob-->>Alice: Fine thank you
    deactivate Bob
```

## Loops and Conditions

```mermaid
sequenceDiagram
    participant A
    participant B
    loop Every minute
        A->>B: Hello!
        B-->>A: Is that a recurring message?
    end

    alt sick
        A->>B: Forgot to say hi
    else well
        A->>B: Hi
    end

    opt optional section
        A->>B: This is optional
    end

    par parallel action 1
        A->>B: Parallel message 1
    and parallel action 2
        A->>B: Parallel message 2
    end
```

### Supported Blocks

| Keyword | Purpose |
|---------|---------|
| `loop ... end` | Repeating section |
| `alt ... else ... end` | Conditional branches |
| `opt ... end` | Optional section |
| `par ... and ... end` | Parallel sections |
| `break ... end` | Break the sequence |
| `critical ... option ... end` | Critical section with fallback options |

## autonumber

```mermaid
sequenceDiagram
    autonumber
    Alice->>John: Hello John
    John-->>Alice: Great!
```

Auto-number messages starting from 1. Use `autonumber [offset]` to start from a different number.

## Box (Grouping Participants)

```mermaid
sequenceDiagram
    box "My Group"
        participant Alice
        participant Bob
    end
    box Another Group #Blue
        participant John
    end
```

## Configuration

| Parameter | Description | Default |
|-----------|-------------|---------|
| `width` | Participant actor width | `150` |
| `height` | Participant actor height | `65` |
| `messageAlign` | `left`, `center`, `right` | `center` |
| `mirrorActors` | Mirror actors below diagram | `false` |
| `showSequenceNumbers` | Show message numbers | `false` |
| `wrap` | Wrap long messages | `false` |
| `wrapWidth` | Characters before wrapping | `200` |
| `rightAngles` | Use right angles for arrows | `false` |

## Accessibility

```mermaid
sequenceDiagram
    accTitle: API Call Sequence
    accDescr: Shows the sequence of calls between client and server.
    Client->>Server: Request
    Server-->>Client: Response
```

## Examples

### Full Example

```mermaid
sequenceDiagram
    autonumber
    participant User
    participant Browser
    participant API
    participant DB

    User->>Browser: Enters URL
    activate Browser
    Browser->>API: GET /data
    activate API
    API->>DB: Query data
    activate DB
    DB-->>API: Results
    deactivate DB
    API-->>Browser: JSON response
    deactivate API
    Browser->>User: Displays page
    deactivate Browser
```

### With Conditions

```mermaid
sequenceDiagram
    participant Client
    participant Server

    Client->>Server: Login request
    alt Valid credentials
        Server-->>Client: 200 OK + token
    else Invalid credentials
        Server-->>Client: 401 Unauthorized
    end
```
