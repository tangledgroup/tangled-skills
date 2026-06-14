# Architecture Diagrams (v11.1.0+)

Cloud-style diagrams showing relationships between services and resources in deployments.

## Syntax

```
architecture-beta
    group api(cloud)[API]
    service db(database)[Database] in api
    service server(server)[Server] in api

    db:L -- R:server
```

## Components

### Groups

```
group {id}({icon})[{label}] (in {parent_id})?
```

- `id`: Unique identifier
- `icon()`: Icon name (see icon list below)
- `[label]`: Display text
- `in {parent}`: Optional nesting

### Services

```
service {id}({icon})[{label}] (in {group_id})?
```

Same syntax as groups. Services are leaf nodes.

### Edges

```
{id}:{T|B|L|R} -- {T|B|L|R}:{id}
{id}:R --> L:{id2}      %% With arrow
{id}:T <--> B:{id2}     %% Bidirectional
```

Direction: `T` (top), `B` (bottom), `L` (left), `R` (right).

### Junctions

```
junction j1
db:R -- L:j1
j1:R -- L:server
```

Junctions are connection points for multiple edges.

## Icons

Common icons: `cloud`, `database`, `disk`, `server`, `lock`, `user`, `gear`, `code`, `monitor`, `network`, `storage`, `firewall`, `loadbalancer`, `queue`, `lambda`, `container`, `kubernetes`, `docker`, `git`, `ci-cd`, `api`, `web`, `mobile`, `email`, `chat`, `search`, `analytics`, `ml`, `cache`, `cdn`, `dns`.
