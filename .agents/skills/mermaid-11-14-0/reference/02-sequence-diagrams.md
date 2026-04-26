# Sequence Diagrams

Sequence diagrams show how processes operate with one another and in what order.

## Participants

Participants are declared implicitly (by appearing in messages) or explicitly:

```mermaid
sequenceDiagram
  participant Alice
  participant Bob
  Bob->>Alice: Hi Alice
  Alice->>Bob: Hi Bob
```

### Actor Symbol

Use `actor` instead of `participant` for the stick-figure symbol:

```mermaid
sequenceDiagram
  actor Alice
  actor Bob
```

### Participant Types (JSON config syntax)

Specify UML participant stereotypes using `@{ "type": "..." }`:

- `boundary` — Boundary symbol
- `control` — Control symbol (circle with tail)
- `entity` — Entity symbol (circle)
- `database` — Database symbol (cylinder)
- `collections` — Collections symbol
- `queue` — Queue symbol

```mermaid
sequenceDiagram
  participant API@{ "type": "boundary" } as Public API
  actor DB@{ "type": "database" } as User Database
  participant Svc@{ "type": "control" } as Auth Service
  API->>Svc: Authenticate
  Svc->>DB: Query user
```

### Aliases

Define short identifiers with display labels using `as`:

```mermaid
sequenceDiagram
  participant A as Alice
  participant J as John
  A->>J: Hello John
```

Inline alias in config object:

```mermaid
sequenceDiagram
  participant API@{ "type": "boundary", "alias": "Public API" }
```

When both inline and external alias are provided, **external takes precedence**.

### Actor Creation and Destruction (v10.3.0+)

```mermaid
sequenceDiagram
  Alice->>Bob: Hello Bob
  create participant Carl
  Alice->>Carl: Hi Carl!
  create actor D as Donald
  destroy Carl
  destroy Bob
```

### Grouping / Box

Group participants in colored boxes:

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
```

Use `box transparent <name>` if the group name is a color keyword.

## Messages

### Arrow Types

**Standard:**

- `->` — Solid line, no arrowhead
- `-->` — Dotted line, no arrowhead
- `->>` — Solid line with arrowhead
- `-->>` — Dotted line with arrowhead
- `-x` — Solid line with cross at end
- `--x` — Dotted line with cross
- `-)` — Solid line with open arrow (async)
- `--)` — Dotted line with open arrow

**Bidirectional (v11.0.0+):**

- `<<->>` — Solid bidirectional
- `<<-->>` — Dotted bidirectional

**Half-Arrows (v11.12.3+):**

- `-\|` / `--\|` — Top half arrowhead
- `-\|/` / `--\|/` — Bottom half arrowhead
- `/\|-` / `/\|--` — Reverse top half
- `\\-` / `\\--` — Reverse bottom half
- `-\\` / `--\\` — Top stick half
- `-//` / `--//` — Bottom stick half
- `//-` / `//--` — Reverse top stick half

### Central Connections (v11.12.3+)

Use `()` for central lifeline connections:

```mermaid
sequenceDiagram
  Alice->>()John: Hello John
  Alice()->>John: How are you?
  John()->>()Alice: Great!
```

## Activations

Show when an actor is active:

```mermaid
sequenceDiagram
  Alice->>+John: Hello
  John-->>-Alice: Great!
```

Or with explicit activate/deactivate:

```mermaid
sequenceDiagram
  Alice->>John: Hello
  activate John
  John-->>Alice: Great!
  deactivate John
```

Activations stack for the same actor.

## Notes

```mermaid
sequenceDiagram
  participant John
  Note right of John: Text in note
  Note left of John: Left side note
  Note over John: Above note
  Note over Alice,John: Spanning note
```

Use `<br/>` for line breaks in notes and messages.

## Loops, Alt, Parallel, Critical

### Loop

```mermaid
sequenceDiagram
  loop HealthCheck
    John->>John: Fight hypochondria
  end
```

### Alt / Else

```mermaid
sequenceDiagram
  alt successful
    Alice->>Bob: Hello!
  else not so successful
    Alice->>Bob: Never mind!
  end
```

### Optional

```mermaid
sequenceDiagram
  opt Extra description
    Alice->>Bob: Description?
  end
```

### Parallel

```mermaid
sequenceDiagram
  par Activity one
    Alice->>Bob: Hello!
  and Activity two
    Alice->>Bob: How are you?
  and Activity three
    Alice->>Bob: Chatter
  end
```

### Critical Region

```mermaid
sequenceDiagram
  critical Build the tower
    Alice->>Bob: Careful build
  option Not at all steady
    Alice->>Bob: Quick, retake
  option A bit unsteady
    Alice->>Bob: Quick, take a hold
  end
```

### Break

```mermaid
sequenceDiagram
  Alice->>Bob: Try this
  break Something weird
    Alice->>Bob: Get coffee
  end
```

## Styling

```mermaid
sequenceDiagram
  participant A
  participant B
  box Light Blue A & B
    participant A
    participant B
  end
```

## Configuration

- `mirrorActors` — Mirror actors on right side of diagram
- `actorMargin` — Margin around actors
- `messageMargin` — Margin around messages
- `boxMargin` — Margin around boxes
- `boxTextMargin` — Margin inside box text
- `activateDuration` — Animation duration for activations
- `alignMessagesTitle` — Alignment of message titles
- `showActivationNumbers` — Show activation order numbers
