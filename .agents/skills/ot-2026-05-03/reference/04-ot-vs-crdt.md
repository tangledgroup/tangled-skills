# OT vs CRDT

## Contents
- Core Mechanism Differences
- When to Choose OT vs CRDT
- Industry Adoption Patterns
- P2P Co-Editing Myths
- Practical Observations from CRDT Implementations
- Summary Comparison

## Core Mechanism Differences

**Conflict Resolution**: OT explicitly transforms concurrent operations against each other using inclusion/exclusion rules before application, requiring operation serialization. CRDTs embed conflict-freedom in the data type via commutative, associative, idempotent merge functions — operations commute inherently without transformation.

**State vs Operation Focus**: OT sends raw operations and transforms them on receipt to match the receiver's state, decoupling operations from content models. CRDTs mutate local state directly (with metadata like unique IDs or tombstones), sending states or operations that merge deterministically regardless of order.

**Concurrency Handling**: OT handles concurrency through transformation — adjusting operation parameters based on what has already been applied. CRDTs handle concurrency through design — the data structure guarantees convergence by construction.

## When to Choose OT vs CRDT

### Choose OT when:

- **Rich-text editing is required**: OT natively supports complex operations (formatting, tables, images) through application-specific transform functions. Most production rich-text co-editors use OT.
- **Intention preservation matters**: OT explicitly preserves the user's original edit intention. CRDT convergence may produce correct state but not always the intended result for complex edits.
- **Group undo is needed**: OT has well-developed inverse transformation theory (IP1-IP3 properties) for collaborative undo. CRDT undo support is limited and often ad-hoc.
- **Integrating with existing editors**: The Transparent Adaptation approach works cleanly with OT, retrofitting collaboration onto established single-user editors.
- **Production readiness**: OT has decades of production experience in Google Docs, CKEditor, and other widely-used products.

### Choose CRDT when:

- **Offline-first operation is critical**: CRDTs handle arbitrary disconnect/reconnect scenarios without a server coordinating transformations.
- **Plain-text editing suffices**: CRDT sequence types (WOOT, RGA, Logoot) work well for character-level text editing.
- **Peer-to-peer topology is desired**: While not exclusive to CRDTs, the commutative merge model maps naturally to P2P architectures.
- **Simpler correctness reasoning**: CRDT correctness follows from algebraic properties (commutativity, associativity, idempotency) rather than case-specific transform functions.

## Industry Adoption Patterns

### OT Dominates Production

Most commercial collaborative editing products use OT: Google Docs, CKEditor, Dropbox Paper, Box Notes, Tencent TAPD. The reason is practical — OT research has been driven by building working co-editors from the start, with continuous validation against real-world requirements.

### CRDT Mostly in Prototypes

As of the source material's publication, most CRDT-based co-editors are GitHub prototypes built by practitioners exploring the technology:

- **Teletype** (Atom + WOOT): Desktop collaborative editing for Atom editor. Experienced tombstone overhead — significant memory increase and performance degradation as deletions accumulate.
- **Alchemy Book** (CodeMirror + Logoot): Web-based collaborative editing. Experienced concurrent-insert-random-interleaving results and document inconsistencies under numerous scenarios.
- **Yjs**: A WOOT-like CRDT extended for rich-text via an intermediate layer between the CRDT core and the editor API. Still in early development with known correctness issues in its garbage collection scheme.

No major industry co-editing product (beyond Teletype) was documented as using CRDT. The gap reflects that CRDT research has taken predominantly theoretical approaches with limited experimental validation in working systems.

## P2P Co-Editing Myths

Several common claims about CRDT being inherently better for peer-to-peer co-editing are incorrect:

**"CRDT requires no server, OT requires a server"**: False. Many OT solutions (adOPTed, GOT, GOTO, TIBOT, COT, POT) are fully distributed with no central transformation server. Google Docs uses a server for practical reasons (storage, session management), not because OT requires one.

**"CRDT is designed for P2P"**: Misleading. All CRDT-based co-editors examined used a client-server architecture for at least session management and message broadcast. No working P2P co-editor (OT or CRDT) has been documented as fully operational in production.

**"Vector timestamps are a CRDT thing"**: False. Both OT and CRDT solutions use vector and scalar timestamps. Scalar timestamps appeared in OT long before the first CRDT was proposed.

**"Causal ordering is unique to CRDT"**: False. All OT solutions require causally-ordered operation execution. Most CRDT solutions also require it (except WOOT variants, which use weaker conditions that don't ensure causality preservation).

All P2P-related factors — server requirement, causal ordering, timestamp scheme — are orthogonal to the OT/CRDT distinction. They are features of individual solutions, not inherent properties of either approach.

## Practical Observations from CRDT Implementations

Examining working CRDT co-editors revealed steps missed in theoretical publications:

1. **Position-to-ID conversion**: User-generated position-based operations must be converted to identifier-based operations at the local site before sending. This step is obscured in Logoot and ignored in WOOT/RGA publications.

2. **ID-to-position conversion**: Remote identifier-based operations must be converted back to position-based operations at the receiving site for display. Also missing from theoretical descriptions.

3. **Tombstone overhead**: WOOT-based systems (Teletype) accumulate deleted object tombstones indefinitely, causing memory bloat and performance degradation proportional to deletion count.

4. **Non-native operations**: Neither OT nor CRDT operations are native to real editors. Both require a bridging layer between the editor's operation model and the consistency mechanism's operation model.

5. **Rich-text complexity**: Extending CRDT beyond plain text (as Yjs attempted) requires additional layers and conversion schemes, introducing correctness and efficiency challenges comparable to OT's transform function design.

## Summary Comparison

| Factor | OT | CRDT |
|--------|----|------|
| Conflict resolution | Transform concurrent ops | Commutative merge by design |
| Rich-text support | Native (application-specific transforms) | Limited (requires extra layers) |
| Undo support | Formal theory (IP1-IP3) | Ad-hoc, limited |
| Production track record | Google Docs, CKEditor, ShareJS, Etherpad | Teletype (Atom), Yjs (early) |
| Server requirement | Optional (distributed OT exists) | Optional (but all implementations use one) |
| Correctness approach | Case-specific transform functions + control algorithm | Algebraic properties (commute/associate/idempotent) |
| Space complexity | O(1) per operation | O(deletions) for tombstone-based variants |
| Existing editor integration | Transparent Adaptation approach | Requires ID-based operation conversion |
| Research maturity | 35+ years, production-driven | Theoretical, limited implementation validation |
