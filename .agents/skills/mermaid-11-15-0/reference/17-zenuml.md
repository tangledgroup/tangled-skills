# ZenUML

## Contents
- Participants and Annotators
- Aliases
- Messages (Sync, Async, Creation, Reply)
- Nesting
- Loops, Alt, Opt, Parallel
- Try/Catch/Finally

## Overview

ZenUML is an alternative sequence diagram syntax with a more programmatic feel. Uses different syntax from Mermaid's native sequence diagrams.

```mermaid
zenuml
    title Demo
    Alice->John: Hello
    John->Alice: Great!
```

## Participants

### Implicit Declaration

Participants are created on first mention in messages.

### Explicit Declaration

```mermaid
zenuml
    Bob
    Alice
    Alice->Bob: Hi
```

Order of declaration controls rendering order.

### Annotators

| Annotator | Symbol |
|---|---|
| `@Actor` | Stick figure |
| `@Database` | Database cylinder |
| `@Boundary` | Boundary symbol |
| `@Control` | Control symbol |
| `@Entity` | Entity symbol |
| `@Queue` | Queue symbol |
| `@Collections` | Collections symbol |

```mermaid
zenuml
    @Actor Alice
    @Database Bob
    Alice->Bob: Query
```

### Aliases

```mermaid
zenuml
    A as Alice
    J as John
    A->J: Hello
```

## Messages

### Sync Message (blocking)

```mermaid
zenuml
    A.SyncMessage
    A.SyncMessage(with, params) {
        B.nestedMessage()
    }
```

### Async Message

```mermaid
zenuml
    Alice->Bob: How are you?
```

### Creation Message

```mermaid
zenuml
    new A1
    new A2(with, params)
```

### Reply Message

Three ways to express replies:

```mermaid
zenuml
    a = A.SyncMessage()        ' assign to variable
    SomeType a = A.SyncMessage()  ' with type

    A.SyncMessage() {
        return result
    }

    @return
    A->B: result
```

## Nesting

Use `{ }` blocks for nested calls:

```mermaid
zenuml
    A.doSomething() {
        B.process() {
            C.validate()
        }
        D.notify()
    }
```

## Loops, Alt, Opt, Parallel

### Loop

```mermaid
zenuml
    loop Every message {
        Alice->Bob: Hello
        Bob->Alice: Hi back
    }
```

### Alt

```mermaid
zenuml
    alt Success {
        A->B: OK
    } else Failure {
        A->B: Error
    }
```

### Opt

```mermaid
zenuml
    opt Optional step {
        A->B: Maybe this
    }
```

### Parallel

```mermaid
zenuml
    par Action 1 {
        A->B: Hello
    } and Action 2 {
        B->A: Hi back
    }
```

## Try/Catch/Finally

```mermaid
zenuml
    try Attempt {
        A->B: Do something
    } catch Error {
        A->B: Handle error
    } finally Cleanup {
        A->B: Always do this
    }
```
