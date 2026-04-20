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
| `A Note right of B: text` | Note on right |
| `A Note left of B: text` | Note on left |
| `Note right of B: text` | Note without participant |
| `Note over A,B: text` | Note over both participants |

### Notes

```mermaid
sequenceDiagram
    Alice->>John: Hello John
    Note right of John: John thinks long
    John->>Alice: Hi!
    Note left of Alice: Alice thinks back
    Note over Alice,John: Both talking
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
    B->>C: Hello Charley
```

Box colors: `box Purple Title`, `box rgb(33,66,99)`, `box rgba(33,66,99,0.5)`, `box transparent Title`

## Auto-Activate / Deactivate

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

Multiple activations (nesting):

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

## Self-References

```mermaid
sequenceDiagram
    Alice->>Alice: Internal processing
    Alice->>Bob: External call
```

## Sequence Numbers

Enable with config: `sequence: { showSequenceNumbers: true }`

## Wrapping Long Messages

Enable with config: `sequence: { wrap: true }`
