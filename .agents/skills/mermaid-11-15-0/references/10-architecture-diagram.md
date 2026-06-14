# Architecture Diagram Reference

## Description

Architecture diagrams show relationships between cloud services and CI/CD resources. Services (nodes) are connected by edges. Related services can be grouped to illustrate organization.

> **Note:** Uses `architecture-beta` keyword — experimental, syntax may evolve.

## Basic Syntax

```mermaid
architecture-beta
    group api(cloud)[API]
    service db(database)[Database] in api
    service disk1(disk)[Storage] in api
    service server(server)[Server] in api
    db:L -- R:server
    disk1:T -- B:server
```

## Elements

### Groups

```mermaid
architecture-beta
    group id(icon)[Label]
    group id(icon)[Label] in parentGroup
```

- `id` — Unique identifier
- `(icon)` — Icon name (optional)
- `[Label]` — Display label
- `in parentGroup` — Nested in another group

### Services

```mermaid
architecture-beta
    service id(icon)[Label]
    service id(icon)[Label] in group
```

### Edges

```mermaid
architecture-beta
    A:L -- R:B      %% Left of A to Right of B
    A:T -- B:R      %% Top of A to Right of B
    A:B -- T:B      %% Bottom of A to Top of B
```

#### Edge Directions

| Direction | Meaning |
|-----------|---------|
| `T` | Top |
| `B` | Bottom |
| `L` | Left |
| `R` | Right |

### Junctions

```mermaid
architecture-beta
    junction j1
    A -- j1
    B -- j1
    C -- j1
```

## Icons

Common icon names: `cloud`, `database`, `disk`, `server`, `monitor`, `network`, `storage`, `security`, `code`, `people`, `gear`, `flag`, `heart`, `star`.

## Examples

### Cloud Architecture

```mermaid
architecture-beta
    group cloud(cloud)[Cloud Infrastructure]
        group api(api)[API Layer]
            service lb(loadbalancer)[Load Balancer] in api
            service web1(server)[Web Server 1] in api
            service web2(server)[Web Server 2] in api
        end
        group data(data)[Data Layer]
            service db(database)[Primary DB] in data
            service dbrep(database)[Replica DB] in data
            service cache(memory)[Cache] in data
        end
    end

    lb:L -- R:web1
    lb:L -- R:web2
    web1:B -- T:db
    web2:B -- T:cache
    db:L -- R:dbrep
```

### CI/CD Pipeline

```mermaid
architecture-beta
    group ci(CI)[CI/CD Pipeline]
        service git(code)[Git Repo] in ci
        service build(gear)[Build Server] in ci
        service test(test)[Test Runner] in ci
        service deploy(rocket)[Deploy] in ci
    end

    group prod(prod)[Production]
        service app(server)[Application] in prod
        service db(database)[Database] in prod
    end

    git --> build
    build --> test
    test --> deploy
    deploy --> app
    app:B -- T:db
```
