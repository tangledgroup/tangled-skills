# Kanban Diagram

## Contents
- Columns
- Tasks
- Metadata
- Configuration

## Overview

Kanban diagrams visualize tasks across workflow stages.

```mermaid
kanban
    todo[Todo]
        task1[Design UI]
        task2[Write specs]
    doing[In Progress]
        task3[Implement API]
    done[Done]
        task4[Setup repo]
```

## Columns

Define workflow stages:

```
columnId[Column Title]
```

```mermaid
kanban
    backlog[Backlog]
    active[Active]
    review[Review]
    deployed[Deployed]
```

## Tasks

Indent tasks under their column:

```
taskId[Task Description]
```

```mermaid
kanban
    todo[Todo]
        t1[Create login page]
        t2[Setup database]
```

## Metadata

Add metadata with `@{ ... }`:

| Key | Values |
|---|---|
| `assigned` | Person name |
| `ticket` | Ticket/issue number |
| `priority` | 'Very High', 'High', 'Low', 'Very Low' |

```mermaid
kanban
    todo[Todo]
        t1[Update API]@{ ticket: MC-2037, assigned: 'Alice', priority: 'High' }
```

## Configuration

```mermaid
---
config:
  kanban:
    ticketBaseUrl: 'https://jira.example.com/browse/#TICKET#'
---
kanban
    todo[Todo]
        t1[Task]@{ ticket: MC-100 }
```

`ticketBaseUrl` replaces `#TICKET#` with the actual ticket value to create a clickable link.
