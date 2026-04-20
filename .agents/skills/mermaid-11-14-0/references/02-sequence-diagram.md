# Sequence Diagram Syntax

A Sequence diagram shows how processes operate with one another and in what order.

## Basic Example

```mermaid
sequenceDiagram
    Alice->>John: Hello John, how are you?
    John-->>Alice: Great!
    Alice-)John: See you later!
```

> Warning: The word "end" could break the diagram. Use parentheses, quotes, or brackets to enclose it.

## Participants

### Implicit Participants

Participants render in order of appearance in messages:

```mermaid
sequenceDiagram
    Alice->>John: Hello John
    John->>Alice: Hi Alice
```

### Explicit Participant Declaration

```mermaid
sequenceDiagram
    participant Alice
    participant Bob
    Bob->>Alice: Hi Alice
    Alice->>Bob: Hi Bob
```

### Actor Types

Use `actor` keyword for actor symbols instead of rectangles:

```mermaid
sequenceDiagram
    actor Alice
    actor Bob
    Alice->>Bob: Hi Bob
```

### Participant Stereotypes (v10+)

Use JSON configuration for specialized participant shapes:

| Type | Syntax |
|---|---|
| Boundary | `participant Alice@{ "type" : "boundary" }` |
| Control | `participant Alice@{ "type" : "control" }` |
| Entity | `participant Alice@{ "type" : "entity" }` |
| Database | `participant Alice@{ "type" : "database" }` |
| Collections | `participant Alice@{ "type" : "collections" }` |
| Queue | `participant Alice@{ "type" : "queue" }` |

### Aliases

**External alias syntax:**
```mermaid
sequenceDiagram
    participant A as Alice
    participant J as John
    A->>J: Hello John
```

**Inline alias syntax:**
```mermaid
sequenceDiagram
    participant API@{ "type": "boundary", "alias": "Public API" }
    participant Auth@{ "type": "control", "alias": "Auth Service" }
    API->>Auth: Login request
```

**Combined (external alias takes precedence):**
```mermaid
sequenceDiagram
    participant API@{ "type": "boundary", "alias": "Internal Name" } as External Name
```

### Actor Creation & Destruction (v10.3.0+)

```mermaid
sequenceDiagram
    Alice->>Bob: Hello Bob
    create participant Carl
    Alice->>Carl: Hi Carl!
    create actor D as Donald
    Carl->>D: Hi!
    destroy Carl
    Alice-xCarl: We are too many
    destroy Bob
```

### Autonumber

```mermaid
sequenceDiagram
    autonumber
    Alice->>John: Hello John, how are you?
    John->>Alice: Great!
    Alice->>John: See you later!
```

Autonumber can be customized with a range: `autonumber 10 5` (start at 10, increment by 5).

## Messages

| Syntax | Type |
|---|---|
| `A->>B: msg` | Solid open arrow (async) |
| `A->B: msg` | Solid filled arrow |
| `A-->>B: msg` | Dashed open arrow |
| `A-->B: msg` | Dashed filled arrow |
| `A->>B` | Arrow without text |
| `A-)B: msg` | Dotted open arrow (async) |
| `A->)B: msg` | Dotted filled arrow |
| `A-x>>B: msg` | Cross return arrow |
| `A--)B: msg` | Dashed cross return |

### Self-References

```mermaid
sequenceDiagram
    Alice->>Alice: Internal processing
    Alice->>Bob: External call
```

### Central Connections (v11.12.3+)

```mermaid
sequenceDiagram
    autonumber
    participant A as Alice
    participant B as Bob
    A-)B: Request
    B--)A: Response
```

## Notes

```mermaid
sequenceDiagram
    Alice->>John: Hello John
    Note right of John: John thinks long
    John->>Alice: Hi!
    Note left of Alice: Alice thinks back
    Note over Alice,John: Both talking
```

| Syntax | Position |
|---|---|
| `Note right of B: text` | Right side of participant |
| `Note left of B: text` | Left side of participant |
| `Note over A,B: text` | Spanning both participants |
| `A Note right of B: text` | From participant A, positioned right of B |

## Loops

```mermaid
sequenceDiagram
    loop Every minute
        Alice->>John: Heartbeat
        John-->>Alice: Heartbeat response
    end
```

Can include condition: `loop if healthy`.

## Alt (Conditional)

```mermaid
sequenceDiagram
    Alice->>Bob: Hello
    alt is case
        Bob->>Alice: Happy
    else
        Bob->>Alice: Sad
    end
```

Multiple `else` branches supported:
```mermaid
sequenceDiagram
    Alice->>Bob: Request
    opt optional part
        Bob->>Alice: Optional response
    end
    alt success
        Bob->>Alice: Result
    else error
        Bob->>Alice: Error message
    end
```

## Parallel (par)

```mermaid
sequenceDiagram
    par Parallel request
        Alice->>Bob: Hello Bob
        Alice->>Carol: Hello Carol
    and
        Bob->>Alice: Hello Alice
    and
        Carol->>Alice: Hello Alice
    end
```

## Critical Region

```mermaid
sequenceDiagram
    critical section
        Alice->>Bob: Important operation
    option Rollback
        Bob->>Alice: Error
    end
```

## Activations

### Auto-Activate/Deactivate

```mermaid
sequenceDiagram
    participant A
    participant B
    activate A
    A->>B: Hello
    deactivate A
    activate B
    B->>A: Reply
    deactivate B
```

### Nested Activations

```mermaid
sequenceDiagram
    Alice->>John: Hello John
    activate John
    Alice->>John: Another message
    activate John
    John-->>Alice: OK
    deactivate John
    John-->>Alice: Bye
    deactivate John
```

## Grouping / Boxes

```mermaid
sequenceDiagram
    box Purple Alice & John
    participant A
    participant J
    end
    box Another Group
    participant B
    participant C
    end
    A->>J: Hello John
    A->>B: Hello Bob
```

Box colors: `box Purple Title`, `box rgb(33,66,99)`, `box rgba(33,66,99,0.5)`, `box transparent Title`

## Comments

```mermaid
sequenceDiagram
    %% This is a comment
    Alice->>John: Hello John
    % Single-line comment
    John->>Alice: Hi
```

## Styling

### Class-based Styling

```mermaid
sequenceDiagram
    classDef active fill:#90EE90,stroke:#333,stroke-width:2px;
    classDef important stroke-dasharray: 5 5;
    Alice->>John: Hello
    John->>Alice: Hi
    class Alice,John active;
```

### Styling Activation Boxes

```mermaid
sequenceDiagram
    activate John
    Alice->>John: Hello
    deactivate John
    style activationBox1 fill:#f9f,stroke:#333
```

## Line Breaks in Messages

Use `<br/>` for line breaks:
```mermaid
sequenceDiagram
    Alice->>John: This is<br/>a multi-line message
```

## Configuration

```javascript
{
    sequence: {
        width: 200,
        height: 20,
        messageAlign: 'left' | 'center' | 'right',
        mirrorActors: true,
        useMaxWidth: false,
        rightAngles: true,
        showSequenceNumbers: false,
        wrap: false
    }
}
```

## Entity Codes for Special Characters

| Code | Character |
|---|---|
| `&lt;` | < |
| `&gt;` | > |
| `&amp;` | & |
| `&quot;` | " |
| `&#39;` | ' |
