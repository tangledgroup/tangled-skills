# Architecture Diagram

## Contents
- Groups
- Services
- Edges
- Junctions
- Icons
- Configuration

## Overview

Architecture diagrams visualize cloud and CI/CD service relationships. Available since v11.1.0.

```mermaid
architecture-beta
    group api(cloud)[API]
    service db(database)[Database] in api
    service server(server)[Server] in api
    db:L -- R:server
```

## Groups

```
group {id}({icon})[{title}] (in {parent id})?
```

```mermaid
architecture-beta
    group public(cloud)[Public API]
    group private(cloud)[Private API] in public
```

Groups can be nested using `in`.

## Services

```
service {id}({icon})[{title}] (in {parent id})?
```

```mermaid
architecture-beta
    service db(database)[Database] in private
    service cache(redis)[Cache] in private
```

## Edges

Connect services with directional edges:

```
{serviceId}:{T|B|L|R} {<}?--{>}? {T|B|L|R}:{serviceId}
```

| Connector | Description |
|---|---|
| `--` | Simple line |
| `-->` | Arrow on right |
| `<--` | Arrow on left |
| `<->` | Bidirectional arrows |

```mermaid
architecture-beta
    service a[Service A]
    service b[Service B]
    service c[Service C]
    a:R -- L:b
    a:B --> T:c
```

### Edges Out of Groups

Use `{group}` modifier:

```mermaid
architecture-beta
    group g1[Group 1]
    group g2[Group 2]
    service s1[Server] in g1
    service s2[Subnet] in g2
    s1{group}:R --> L:s2{group}
```

## Junctions

4-way split nodes for complex connections:

```mermaid
architecture-beta
    service a[A]
    service b[B]
    service c[C]
    service d[D]
    junction j
    a:R -- L:j
    b:B -- T:j
    j:R -- L:c
    j:B -- T:d
```

## Icons

Built-in icon names used in `()`:

| Icon | Description |
|---|---|
| `cloud` | Cloud |
| `database` | Database |
| `server` | Server |
| `disk` | Storage/disk |
| `lock` | Security |
| `user` | User/person |
| `monitor` | Monitor/display |
| `network` | Network |
| `storage` | Storage |
| `redis` | Redis cache |

Custom icons via URL:

```mermaid
architecture-beta
    service mySvc[My Service]
    mySvc.iconUrl = 'https://example.com/icon.svg'
```

## Configuration

```mermaid
---
config:
  architecture:
    randomSeed: 42
---
architecture-beta
    service a[A]
    service b[B]
```

| Option | Default | Description |
|---|---|---|
| `randomSeed` | random | Seed for deterministic layout |
