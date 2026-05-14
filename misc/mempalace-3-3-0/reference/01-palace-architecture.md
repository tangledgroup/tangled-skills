# Palace Architecture

## Overview

The palace is the organizational structure that makes MemPalace's verbatim storage findable. It is inspired by two historical techniques: the **method of loci** (ancient Greek memory palaces) and the **Zettelkasten method** (Niklas Luhmann's cross-referenced index cards).

## Structural Elements

**Wings** — Top-level categories. Each wing represents a person, project, or topic. As many as needed.

**Rooms** — Specific topics within a wing. Examples: `auth-migration`, `graphql-switch`, `ci-pipeline`, `costs`. Rooms can also be day-based (for conversation transcripts). When the same room name appears in different wings, a **tunnel** is created automatically to cross-reference them.

**Halls** — Memory types that connect rooms within the same wing. The same set of halls exists in every wing:

- `hall_facts` — decisions made, choices locked in
- `hall_events` — sessions, milestones, debugging
- `hall_discoveries` — breakthroughs, new insights
- `hall_preferences` — habits, likes, opinions
- `hall_advice` — recommendations and solutions

Additional topic wings include: `emotions`, `technical`, `family`, `memory`, `identity`, `consciousness`, `creative`.

**Closets** — Compact searchable indexes. Each closet line is an atomic topic pointer containing a description, entity names, and references to drawer IDs. Closets are created during mining and rebuilt on re-mine. They are the fast-scan layer that tells the searcher which drawers to open.

**Drawers** — The original verbatim content. ~800 characters per chunk with 100 character overlap. Never summarized, never paraphrased. This is where the actual words live.

**Tunnels** — Cross-wing connections. When the same room name appears in multiple wings, tunnels link them automatically.

## Visual Structure

```
WING: person_kai
├── hall_facts / auth-migration  → "Kai recommended Clerk over Auth0"
├── hall_events / auth-migration → "Kai debugged the OAuth token refresh"
└── hall_advice / ci-pipeline    → "Kai suggested GitHub Actions over CircleCI"

WING: project_driftwood
├── hall_facts / auth-migration  → "team decided to migrate auth to Clerk"
├── hall_events / ci-pipeline    → "deploy pipeline switched to GitHub Actions"
└── (tunnel) auth-migration ↔ person_kai/auth-migration

CLOSET example:
  "built auth system|Kai;Maya|→drawer_api_auth_a1b2c3"
   topic description ↑ entities ↑ points to drawer
```

## How Structure Improves Retrieval

Tested on 22,000+ real conversation memories:

- Search all drawers: 60.9% R@10
- Search within wing: 73.1% (+12%)
- Search wing + hall: 84.8% (+24%)
- Search wing + room: 94.8% (+34%)

Wings and rooms are not cosmetic — they provide a 34% retrieval improvement through metadata filtering in ChromaDB.

## Storage Implementation

Everything is stored in a single ChromaDB persistent collection (`mempalace_drawers`) with cosine distance metric (`hnsw:space=cosine`). Closets are stored in a separate collection (`mempalace_closets`).

Each drawer carries metadata:

- `wing` — top-level grouping
- `room` — named topic within wing
- `hall` — memory category
- `source_file` — original file path
- `chunk_index` — position within chunked file
- `added_by` — agent identifier (for specialist agents)
- `filed_at` — ISO timestamp
- `importance` — numeric weight for L1 loading
- `emotional_weight` — fallback weight

Drawer IDs are deterministic: `drawer_{wing}_{room}_{md5(source_file + chunk_index)[:16]}`.

Closet metadata includes `source_file` for purge-on-re-mine. Closet lines follow the format: `topic description|entity1;entity2|→drawer_id_1,drawer_id_2`.

## Configuration

MemPalace configuration lives in `~/.mempalace/config.json` with environment variable overrides:

- `MEMPALACE_PALACE_PATH` — custom palace directory (default: `~/.mempalace/palace`)
- `MEMPAL_PALACE_PATH` — alternate env var name

Configuration priority: env vars > config file > defaults.

The `people_map.json` file maps name variants to canonical names for entity disambiguation.
