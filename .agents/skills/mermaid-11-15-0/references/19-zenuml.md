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

### Opt blocks

Optional fragments with `opt`:

```
opt Condition met
    Alice->Bob: Optional action
end
```

### Parallel blocks

Concurrent actions with `par`:

```
par
    Alice->Bob: Action 1
    Bob->Charlie: Action 2
end
```

### Try/Catch/Finally (Break)

Exception modeling:

```
try
    Alice->Bob: Request
catch
    Bob->Alice: Error response
finally
    Alice->Log: Record result
end
```

## Nesting

Sync messages nest with `{}` to show call hierarchy:

```
zenuml
    A.method() {
      B.nested_sync_method()
      B->C: nested async message
    }
```

## Activations

```
activate Alice
Alice->Bob: Request
deactivate Alice
```
