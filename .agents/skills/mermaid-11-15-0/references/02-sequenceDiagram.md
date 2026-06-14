# Sequence Diagrams

Interaction diagrams showing how processes operate with one another and in what order.

## Participants

### Implicit declaration (by first message)

```
sequenceDiagram
    Alice->>John: Hello John, how are you?
```

### Explicit declaration (controls order)

```
sequenceDiagram
    participant Alice
    participant Bob
    Bob->>Alice: Hi Alice
```

### Actors (stick figure symbol)

```
actor Alice
actor Bob
```

### Participant types (UML stereotypes)

```
participant A@{ "type": "boundary" }   %% rectangle with flap
participant B@{ "type": "control" }    %% circle with tail
participant C@{ "type": "entity" }     %% circle
participant D@{ "type": "database" }   %% cylinder
participant E@{ "type": "collections" }%% stack of rectangles
participant F@{ "type": "queue" }      %% queue symbol
```

### Aliases

```
participant A as Alice Johnson
participant API@{ "type": "boundary" } as Public API
participant DB@{ "type": "database", "alias": "User Database" }
```

External alias (`as`) takes precedence over inline `"alias"` in config object.

### Actor creation and destruction (v10.3.0+)

```
create participant Carl
create actor D as Donald
destroy Carl
destroy Bob
```

Only the recipient of a message can be created. Sender or recipient can be destroyed. Use `Alice-xCarl` for destroy-with-message.

## Grouping / Boxes

```
box Purple "Group Title"
    participant A
    participant B
end
box transparent Aqua   %% Force transparent if title matches a color name
    participant C
end
```

Colors: `transparent`, named colors, `rgb(r,g,b)`, `rgba(r,g,b,a)`.

## Messages / Arrows

### Standard arrow types

| Syntax | Description |
| --- | --- |
| `->` | Solid line, no arrowhead |
| `-->` | Dotted line, no arrowhead |
| `->>` | Solid line with arrowhead |
| `-->>` | Dotted line with arrowhead |
| `<<->>` | Bidirectional solid (v11.0.0+) |
| `<<-->>` | Bidirectional dotted (v11.0.0+) |
| `-x` | Solid line with cross (destruction) |
| `--x` | Dotted line with cross |
| `-)` | Solid async (open arrow) |
| `--)` | Dotted async |

### Half-arrows (v11.12.3+)

| Syntax | Description |
| --- | --- |
| `-\|` / `--\|` | Top half arrowhead |
| `-\|/` / `--\|/` | Bottom half arrowhead |
| `/\|-` / `/\|--` | Reverse top half |
| `\\-` / `\\--` | Reverse bottom half |
| `-\\` / `--\\` | Top stick half |
| `-//` / `--//` | Bottom stick half |
| `//-` / `//--` | Reverse top stick half |

### Message with text

```
Alice->>John: Hello John, how are you?
Alice->>John: Line one<br/>Line two
```

Use `<br/>` for line breaks in messages and actor names.

## Central connections (v11.12.3+)

Messages connecting to a central lifeline point:

```
Alice->>()John: Hello John
Alice()->>John: How are you?
John()->>()Alice: Great!
```

Append `()` to arrow syntax for central connection.

## Activations

### Explicit activate/deactivate

```
Alice->>John: Hello
activate John
John-->>Alice: Great!
deactivate John
```

### Shortcut notation (+/- suffix)

```
Alice->>+John: Hello (activates John)
John-->>-Alice: Great! (deactivates John)
```

Activations can stack on the same actor for recursive calls.

## Notes

```
Note right of John: Text in note
Note left of John: Text in note
Note over John: Text over John
Note over Alice,John: Text spanning two participants
```

## Control flow blocks

### Loop

```
loop Every minute
    John-->Alice: Great!
end
```

### Alt / Else

```
alt is sick
    Bob->>Alice: Not so good :(
else is well
    Bob->>Alice: Feeling fresh
end
```

### Opt (optional)

```
opt Extra response
    Bob->>Alice: Thanks for asking
end
```

### Parallel

```
par Alice to Bob
    Alice->>Bob: Hello!
and Alice to John
    Alice->>John: Hello!
end
```

Can be nested.

### Critical region

```
critical Establish DB connection
    Service-->DB: connect
option Network timeout
    Service-->Service: Log error
option Credentials rejected
    Service-->Service: Log different error
end
```

Options are optional (can have none). Can be nested.

### Break (exception)

```
break when booking fails
    API-->Consumer: show failure
end
```

## Background highlighting

```
rect rgb(191, 223, 255)
    Alice->>+John: Hello
end
rect rgba(0, 0, 255, 0.1)
    John-->>-Alice: Great!
end
```

Can be nested. Colors: `rgb()`, `rgba()`.

## Sequence numbers

```
sequenceDiagram
    autonumber
    Alice->>John: Hello
    John-->>Alice: Great!
```

### Start and increment (v11.15.0+)

```
autonumber 10 2   %% Start at 10, increment by 2
```

Supports decimals up to hundredths place.

## Actor menus (links)

```
link Alice: Dashboard @ https://dashboard.example.com
link John: Wiki @ https://wiki.example.com
```

Advanced JSON syntax:
```
links Alice: {"Dashboard": "https://...", "Wiki": "https://..."}
```

## Styling

Styling is done via CSS classes defined in the site's stylesheet. Key classes:

| Class | Description |
| --- | --- |
| `.actor` | Actor box styles |
| `.actor-line` | Vertical lifeline |
| `.messageLine0` | Solid message line |
| `.messageLine1` | Dotted message line |
| `.messageText` | Message arrow text |
| `.note`, `.noteText` | Note boxes |
| `.loopText`, `.loopLine` | Loop box |

## Configuration

```yaml
---
config:
  sequence:
    mirrorActors: false        %% Show actors below diagram too
    bottomMarginAdj: 1         %% Adjust bottom margin
    actorFontSize: 14
    actorFontFamily: "Open Sans"
    noteFontSize: 14
    messageFontSize: 16
    showSequenceNumbers: false
    wrap: false                %% Wrap long messages
    width: 300                 %% Diagram width
    height: 30                 %% Actor height
    messageAlign: center       %% left, center, right
    rightAngles: false         %% Use right angles for arrows
---
```

## Comments

```
%% This is a comment
sequenceDiagram
    Alice->>John: Hello
```

## Entity codes

```
A->>B: I #9829; you!
A->>B: Use #59; for semicolons in text
```

Numbers are base 10. `#` is `#35;`. Semicolons in message text must be `#59;`.
