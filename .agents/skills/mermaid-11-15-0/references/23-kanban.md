# Kanban Boards

Visual workflow representation with columns and tasks.

## Syntax

```
kanban
    todo[Todo]
        task1[Task Description]
        task2[Another Task]@{ ticket: MC-123, assigned: 'alice', priority: 'High' }
    doing[In Progress]
        task3[Working on this]
    done[Done]
        task4[Completed]
```

## Columns

```
columnId[Column Title]
```

Columns represent workflow stages (Todo, In Progress, Review, Done, etc.).

## Tasks

```
taskId[Task Description]
```

Tasks are indented under their column.

## Task metadata

```
task1[Description]@{ ticket: MC-2037, assigned: 'knsv', priority: 'High' }
```

| Key | Values |
| --- | --- |
| `ticket` | Any string (issue/ticket ID) |
| `assigned` | Person name |
| `priority` | `Very High`, `High`, `Low`, `Very Low` |
