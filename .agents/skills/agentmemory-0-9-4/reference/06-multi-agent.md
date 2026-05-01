# Multi-Agent Coordination

agentmemory supports coordination between multiple AI coding agents through shared memory primitives.

## Leases

Exclusive action leases prevent multiple agents from working on the same task simultaneously:

- `memory_lease` — Acquire exclusive lease on an action
- Lease holder gets write access; others get read-only or wait
- Automatic expiry prevents deadlocks
- Multi-agent aware with conflict resolution

## Signals

Inter-agent messaging with delivery receipts:

- `memory_signal_send` — Send a message to another agent
- `memory_signal_read` — Read messages with receipt tracking
- Supports broadcast and point-to-point messaging
- Messages persist in the shared memory store

## Routines

Workflow routines define repeatable multi-step processes:

- `memory_routine_run` — Instantiate a workflow routine
- Routines carry state across agent sessions
- Support conditional branching based on memory state
- Can be triggered by sentinels or manually

## Checkpoints

External condition gates for coordinated workflows:

- `memory_checkpoint` — Create external condition gates
- Agents wait at checkpoints until conditions are met
- Supports complex dependency graphs between agents
- Integrates with actions and frontiers

## Actions and Frontiers

Structured work items with dependencies:

- `memory_action_create` — Create work items with dependencies
- `memory_action_update` — Update action status
- `memory_frontier` — Unblocked actions ranked by priority
- `memory_next` — Single most important next action
- `memory_sketch_create` — Ephemeral action graphs (draft planning)
- `memory_sketch_promote` — Promote sketch to permanent action
- `memory_crystallize` — Compact completed action chains

## Mesh Sync

Peer-to-peer synchronization between agentmemory instances:

- `memory_mesh_sync` — P2P sync between instances
- Requires `AGENTMEMORY_SECRET` on both peers
- Supports distributed team workflows
- Bidirectional conflict resolution

## Sentinels

Event-driven watchers for automated responses:

- `memory_sentinel_create` — Create event-driven watchers
- `memory_sentinel_trigger` — Fire sentinels externally
- Watch for specific memory patterns or conditions
- Trigger automated actions or notifications

## Team Memory

Namespaced shared and private memories across team members:

- `memory_team_share` — Share memories with team members
- `memory_team_feed` — Recent shared items
- Configured via `TEAM_ID`, `USER_ID`, `TEAM_MODE` environment variables
- `TEAM_MODE=private` restricts visibility to the user's own memories

## Multi-Agent Architecture

All agents share the same memory server. One instance serves all connected agents via MCP or REST. This enables:

- Cross-agent context sharing without manual handoff
- Consistent project knowledge across Claude Code, Cursor, Gemini CLI, etc.
- Coordinated multi-agent workflows through leases and signals
- Unified audit trail of all agent activity
