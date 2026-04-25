# Sequence Diagrams

> **Source:** https://github.com/mermaid-js/mermaid/blob/mermaid%4011.14.0/docs/syntax/sequenceDiagram.md
> **Loaded from:** SKILL.md (via progressive disclosure)

## Basic Syntax

```mermaid
sequenceDiagram
    Alice->>John: Hello John, how are you?
    John-->>Alice: Great!
    Alice-)John: See you later! (async)
```

## Participants

### Basic Participants

```mermaid
sequenceDiagram
    participant Alice
    participant Bob
    Bob->>Alice: Hi Alice
```

### Actor Types

| Type | Syntax | Description |
|------|--------|-------------|
| `participant` | `participant Alice` | Rectangle box |
| `actor` | `actor Alice` | Stick figure |
| Boundary | `participant A@{ "type" : "boundary" }` | UI boundary |
| Control | `participant A@{ "type" : "control" }` | Control element |
| Entity | `participant A@{ "type" : "entity" }` | External entity |
| Database | `participant A@{ "type" : "database" }` | Database symbol |
| Collections | `participant A@{ "type" : "collections" }` | Cylinder storage |
| Queue | `participant A@{ "type" : "queue" }` | Queue symbol |

### Aliases

```mermaid
sequenceDiagram
    participant A as Alice
    participant J as John
    API@{ "type": "boundary" } as Public API
    DB@{ "type": "database", "alias": "User DB" }
```

External alias (`as`) takes precedence over inline `"alias"` field.

## Messages

### Arrow Types

| Syntax | Description |
|--------|-------------|
| `->` | Solid, no arrow |
| `-->` | Dotted, no arrow |
| `->>` | Solid with arrowhead |
| `-->>` | Dotted with arrowhead |
| `-x` | Solid cross (error/return) |
| `--x` | Dotted cross |
| `-)` | Solid open (async) |
| `--)` | Dotted open (async) |
| `<<->>` | Bidirectional solid (v11.0.0+) |
| `<<-->>` | Bidirectional dotted (v11.0.0+) |
| `-\|` / `-\\` etc. | Half-arrows (v11.12.3+) |

### Central Connections (v11.12.3+)

```mermaid
sequenceDiagram
    Alice->>()John: Signal
    Alice()->>John: From center to John
    John()->>()Alice: Reply
```

## Activations

```mermaid
sequenceDiagram
    Alice->>John: Hello
    activate John
    John-->>Alice: Great!
    deactivate John
```

Shortcut: append `+` (activate) or `-` (deactivate) to arrow.

## Grouping / Boxes

```mermaid
sequenceDiagram
    box Purple Group Name
    participant A
    participant B
    end
    box rgb(33,66,99) Another Group
    participant C
    end
```

Use `box transparent Label` for transparent background.

## Actor Creation & Destruction (v10.3.0+)

```mermaid
sequenceDiagram
    Alice->>Bob: Hello
    create participant Carl
    Alice->>Carl: Hi Carl!
    destroy Carl
    Alice-xCarl: Too late (error)
```

Only the recipient can be created; both sender and recipient can be destroyed.

## Notes

```mermaid
sequenceDiagram
    Alice->>John: Hello
    Note right of John: John thinks long
    Note left of Alice: Alice thinks too
    Note over Alice,John: Both think together
```
