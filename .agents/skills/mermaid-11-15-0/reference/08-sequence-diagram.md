# Sequence Diagram

## Contents
- Participants and Actors
- Participant Types (boundary, control, entity, database, queue, collections)
- Aliases
- Actor Creation/Destruction
- Grouping (Boxes)
- Message Types
- Central Connections (v11.12.3+)
- Activations
- Notes
- Line Breaks
- Loops, Alt, Parallel, Critical, Break
- Styling
- Configuration

## Overview

Sequence diagrams show interactions between participants over time. Messages flow top-to-bottom along lifelines.

```mermaid
sequenceDiagram
    Alice->>John: Hello John, how are you?
    John-->>Alice: Great!
    Alice-)John: See you later!
```

## Participants and Actors

### Implicit Declaration

Participants are created on first mention in messages. Rendered in order of first appearance.

### Explicit Declaration

```mermaid
sequenceDiagram
    participant Alice
    participant Bob
    Bob->>Alice: Hi Alice
```

### Actor Symbol

Use `actor` keyword for stick-figure representation:

```mermaid
sequenceDiagram
    actor Alice
    actor Bob
    Alice->>Bob: Hello
```

### Participant Types

Specify special shapes via inline config:

| Type | Syntax | Shape |
|---|---|---|
| boundary | `participant A@{ "type": "boundary" }` | Boundary symbol |
| control | `participant A@{ "type": "control" }` | Control symbol (circle + arrow) |
| entity | `participant A@{ "type": "entity" }` | Entity (circle with bar) |
| database | `participant A@{ "type": "database" }` | Database cylinder |
| collections | `participant A@{ "type": "collections" }` | Collections symbol |
| queue | `participant A@{ "type": "queue" }` | Queue symbol |

## Aliases

### External Alias (`as` keyword)

```mermaid
sequenceDiagram
    participant A as Alice
    participant J as John
    A->>J: Hello
```

Combine with type:

```mermaid
sequenceDiagram
    participant API@{ "type": "boundary" } as Public API
    actor DB@{ "type": "database" } as User Database
```

### Inline Alias

```mermaid
sequenceDiagram
    participant API@{ "type": "boundary", "alias": "Public API" }
```

External alias (`as`) takes precedence over inline `"alias"`.

## Actor Creation/Destruction (v10.3.0+)

```mermaid
sequenceDiagram
    Alice->>Bob: Hello
    create participant Carl
    Alice->>Carl: Hi Carl!
    create actor D as Donald
    destroy Carl
    Alice-xCarl: Too many
```

Only recipients can be created; senders or recipients can be destroyed.

## Grouping (Boxes)

Group participants in colored boxes:

```mermaid
sequenceDiagram
    box Purple Frontend
    participant A
    participant J
    end
    box Backend
    participant B
    end
    A->>B: Request
```

Use `transparent` to force no color when name matches a color keyword.

## Message Types

| Syntax | Line | Arrowhead | Description |
|---|---|---|---|
| `->>` | Solid | Arrow | Synchronous call |
| `-->>` | Dotted | Arrow | Return message |
| `->` | Solid | None | Simple line |
| `--` | Dotted | None | Simple dotted |
| `-x` | Solid | Cross | Destroy/dead letter |
| `--x` | Dotted | Cross | Dotted destroy |
| `-)` | Solid | Open arrow | Async message |
| `--)` | Dotted | Open arrow | Dotted async |
| `<<->>` | Solid | Bidirectional | Both directions (v11.0.0+) |
| `-->>` | Dotted | Bidirectional | Dotted both directions |

### Half-Arrows (v11.12.3+)

Top/bottom half-arrowheads for more expressive diagrams:

| Syntax | Description |
|---|---|
| `-\|/` | Top half arrowhead |
| `-\/` | Bottom half arrowhead |
| `/\|-` | Reverse top half |
| `\\-` | Reverse bottom half |

Add `--` for dotted variants.

## Central Connections (v11.12.3+)

Connect messages to central lifeline points using `()`:

```mermaid
sequenceDiagram
    participant Alice
    participant John
    Alice->>()John: Hello
    Alice()->>John: How are you?
```

## Activations

Show when participants are active:

```mermaid
sequenceDiagram
    Alice->>+John: Hello
    John-->>-Alice: Great!
```

Shortcut: `+` activates, `-` deactivates. Stacking supported:

```mermaid
sequenceDiagram
    Alice->>+John: Call 1
    Alice->>+John: Call 2
    John-->>-Alice: Return 1
    John-->>-Alice: Return 2
```

Or explicit declarations:

```mermaid
sequenceDiagram
    Alice->>John: Hello
    activate John
    John-->>Alice: Great!
    deactivate John
```

## Notes

```mermaid
sequenceDiagram
    participant John
    Note right of John: Text in note
    Note left of John: Left side note
    Note over John: Centered note
    Note over Alice,John: Spanning note
```

## Line Breaks

Use `<br/>` in messages and notes. For actor names, use aliases:

```mermaid
sequenceDiagram
    participant A as Alice<br/>Johnson
    A->>B: Hello<br/>How are you?
```

## Loops, Alt, Parallel, Critical, Break

### Loop

```mermaid
sequenceDiagram
    loop Every message
        Alice->>Bob: Hello
        Bob-->>Alice: Hi back
    end
```

### Alt / Else

```mermaid
sequenceDiagram
    alt Success
        A->>B: OK
    else Failure
        A->>B: Error
    end
```

### Opt (Optional)

```mermaid
sequenceDiagram
    opt Optional step
        A->>B: Maybe this
    end
```

### Parallel

```mermaid
sequenceDiagram
    par Action by Alice
        Alice->>Bob: Hello
    and Action by Bob
        Bob->>Alice: Hi back
    end
```

### Critical Region

```mermaid
sequenceDiagram
    critical Create an account for the user
        A->>B: Generating
    option Better case
        B-->>A: Generated
    option Something unusual
        B-->>A: Warning
    end
```

### Break

```mermaid
sequenceDiagram
    break Exception event
        A->>B: Error occurs
    end
```

## Styling

Use `rect` for background highlighting:

```mermaid
sequenceDiagram
    rect rgb(0, 255, 0)
    Alice->>Bob: All good
    end
    rect rgb(255, 0, 0)
    Alice->>Bob: Error!
    end
```

## Configuration

```mermaid
---
config:
  sequence:
    mirrorActors: true
    wrap: true
    width: 300
    height: 50
    messageAlign: center
    rightAngles: false
    showSequenceNumbers: true
---
sequenceDiagram
    A->>B: Hello
```

| Option | Default | Description |
|---|---|---|
| `mirrorActors` | false | Show actors at bottom too |
| `wrap` | false | Wrap long messages |
| `width` / `height` | auto | Actor box dimensions |
| `messageAlign` | left | Message label alignment |
| `rightAngles` | false | Right-angle message lines |
| `showSequenceNumbers` | false | Show message numbers |
