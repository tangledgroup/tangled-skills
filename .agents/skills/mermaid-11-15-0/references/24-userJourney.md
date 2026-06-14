# User Journey Diagrams

High-level user workflow visualization with satisfaction scores.

## Syntax

```
journey
    title My Working Day
    section Go to work
        Make tea: 5: Me
        Go upstairs: 3: Me
        Do work: 1: Me, Cat
    section Go home
        Go downstairs: 5: Me
        Sit down: 5: Me
```

## Structure

### Sections

Group related tasks: `section Section Name`

### Tasks

```
Task name: <score>: <actor1>, <actor2>
```

- `score`: Number 1–5 (satisfaction level)
- Actors: Comma-separated list of participants
