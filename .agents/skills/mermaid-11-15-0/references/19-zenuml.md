# ZenUML

ZenUML-style sequence diagrams with simplified syntax. Different from standard Mermaid sequence diagrams.

## Basic syntax

```
zenuml
    title Demo
    Alice->John: Hello John
    John->Alice: Great!
```

## Participants

### Implicit (by first message)

```
Alice->Bob: Hi
```

### Explicit declaration (controls order)

```
Bob
Alice
Alice->Bob: Hi Bob
```

### Annotators (participant types)

```
@Actor Alice
@Database Bob
@Boundary API
@Control Auth
@Entity Record
@Collections Cache
@Queue MessageQueue
```

## Messages

```
Alice->Bob: Synchronous message
Alice-->Bob: Asynchronous message
Alice=>Bob: Complete message (with response)
```

## Self-messages

```
Alice->Alice: Self call
```

## Notes

```
note over Alice: This is a note
note right of Bob: Right-side note
```

## Loops and conditions

```
loop Every minute
    Alice->Bob: Check status
end

alt Success
    Bob->Alice: OK
else Failure
    Bob->Alice: Error
end
```

## Activations

```
activate Alice
Alice->Bob: Request
deactivate Alice
```
