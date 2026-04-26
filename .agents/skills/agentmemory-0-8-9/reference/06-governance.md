# Memory Governance

## Auto-Forgetting

agentmemory implements automatic memory decay and eviction to prevent unbounded growth. Three mechanisms work together:

### TTL Expiry

Memories can have a `forgetAfter` timestamp. When the current time exceeds this threshold, the memory is eligible for eviction.

### Importance-Based Eviction

Low-importance memories are evicted first when storage pressure increases. Importance scores are assigned during compression and adjusted over time based on access frequency.

### Contradiction Detection

When new observations contradict existing memories, the system detects conflicts and resolves them — typically by superseding the older memory with a `supersedes` reference chain.

## Retention Scoring

Since v0.8.3, retention scoring reflects real agent-side reads. The formula combines:

- **Time decay** — Ebbinghaus forgetting curve reduces strength over time
- **Frequency boost** — Each access reinforces the memory
- **Access log** — Per-memory access timestamps persisted at `mem:access`
- **Ring buffer** — Last 20 access timestamps bounded per memory

Every read endpoint (`mem::search`, `mem::smart-search`, `mem::context`, `mem::timeline`, `mem::file-context`) writes to the access log fire-and-forget so reads never block on tracker writes. Concurrent access tracking is race-safe via `withKeyedLock` keyed mutex.

## 4-Tier Consolidation Pipeline

The consolidation pipeline (`CONSOLIDATION_ENABLED=true` by default) progresses memories through four tiers:

1. **Working → Episodic** — Raw observations compressed into session summaries
2. **Episodic → Semantic** — Session summaries distilled into facts and patterns
3. **Semantic → Procedural** — Recurring patterns extracted as workflows
4. **Procedural decay** — Unused workflows fade via Ebbinghaus curve

The pipeline runs on a cron schedule via iii-engine's Cron worker. Manual trigger:

```
memory_consolidate()
```

## Memory Versioning & Supersession

Each memory has a `version` number and `isLatest` flag. When a memory is updated:

- A new version is created with incremented `version`
- The `parentId` links to the original memory
- `supersedes` lists the IDs of replaced versions
- Only `isLatest: true` memories appear in search results

This enables full history tracking and rollback.

## Citation Provenance

Every memory tracks its source observations via `sourceObservationIds`. Use `memory_verify(memoryId)` to trace any memory back to the original tool uses, file edits, or conversations that generated it. This ensures auditability and trust in retrieved context.

## Governance Delete

`memory_governance_delete` provides auditable deletion:

```
memory_governance_delete(memoryIds: ["mem-001", "mem-002"])
```

Returns `{deleted, requested, reason}` with full audit trail. Unknown IDs are skipped rather than causing errors.

## Snapshots

When `SNAPSHOT_ENABLED=true`, memory state can be versioned like git:

```
memory_snapshot_create(label: "before-refactor")
```

Snapshots enable rollback and diff of memory state over time. The access log is included in export/import round-trips (since v0.8.3) so reinforcement signals survive backup/restore cycles.

## Lessons & Decay

When `LESSON_DECAY_ENABLED=true`, learned lessons follow the Ebbinghaus forgetting curve. Frequently accessed lessons strengthen; unused lessons fade. The `src/functions/lessons.ts` module manages lesson lifecycle with decay scheduling.

## Audit Trail

All state-changing operations are recorded via `recordAudit()`. The audit trail includes:

- Operation type (create, update, delete, consolidate, etc.)
- Timestamp
- Memory IDs affected
- Before/after state for mutations

Query via `memory_audit(limit)` or `GET /agentmemory/audit`.

## Diagnostics & Self-Healing

**memory_diagnose** — Health checks covering:

- iii-engine connection state
- Worker status
- Memory usage (heap, RSS)
- CPU usage and event loop lag
- KV connectivity with latency measurements
- Circuit breaker states

**memory_heal** — Auto-fix stuck states:

- Reset circuit breakers
- Rebuild search indexes
- Clear dead leases
- Recover from partial failures
