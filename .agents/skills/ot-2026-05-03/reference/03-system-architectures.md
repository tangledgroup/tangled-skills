# System Architectures

## Contents
- Server-Based vs Distributed OT
- Communication Topologies
- Control Algorithms Overview
- Timestamp Schemes
- Transparent Adaptation Approach
- Industry Products

## Server-Based vs Distributed OT

### Server-Based OT (SOT)

A central server performs part of the transformation work and broadcasts operations to clients. Clients send their operations to the server; the server transforms and applies them, then sends transformed operations back.

**Examples**: Google Wave, Google Docs, ShareJS, CKEditor collaboration, NICE, Jupiter, QuillJS, SlateJS.

**Characteristics**:
- Different OT algorithms run at server and client
- Server acts as the single point of truth for operation ordering
- Simpler client-side logic (server handles complex transforms)
- Requires always-on server connection
- Centralized bottleneck for transformation computation

### Distributed OT (DOT)

All sites run the same OT algorithm. No central transformation server is required. Sites exchange operations directly or through a message relay.

**Examples**: adOPTed, GOT, GOTO, TIBOT, COT, POT, SOCT2, REDUCE, CoWord, CoMaya.

**Characteristics**:
- Same algorithm at all sites
- Can work with intermittent connectivity (operations queued locally)
- More complex client-side logic
- No single point of failure for transformation
- May still use a server for session management and message broadcast

**Note**: SOCT3/4 is special — it uses a server to issue continuous total ordering numbers, but the server performs no transformation.

### Common Misconception

A central server is not required for OT to work. Many published OT solutions are fully distributed. The server in systems like Google Docs exists for practical reasons (document storage, session management, message broadcast), not because OT fundamentally requires one.

## Communication Topologies

Three topologies are used in practice:

**Star topology with OT server**: Clients connect to a central server that handles transformation and broadcast. Used by server-based OT solutions.

**Star topology with message relay**: A non-OT server relays messages between clients, but each client performs its own transformations. Common in distributed OT solutions where a relay simplifies peer discovery and message delivery.

**Fully-connected (P2P)**: Clients exchange operations directly without any server involvement. Used by REDUCE and some Codox Apps. Requires clients to discover each other and manage connections independently.

## Control Algorithms Overview

OT control algorithms determine which operations are transformed against others and in what order. Key design dimensions:

**Causality-based**: Causally related operations execute in causal order; concurrent operations are transformed before execution. This is the most common approach.

**Context-based**: The theory of operation context explicitly represents document state, allowing more precise transformation conditions beyond simple concurrency detection. Used by COT (Context-based OT).

**Total-ordering-based**: Operations receive a total ordering (continuous or discontinuous), and transformations follow that order. Used by SOCT4 (continuous) and GOT/GOTO (discontinuous).

### Notable Control Algorithms

| Algorithm | Transform Type | Undo Support | Ordering | Timestamp |
|-----------|---------------|--------------|----------|-----------|
| dOPT (GROVE) | IT only | No | Causal order | State vector |
| adOPTed (JOINT EMACS) | L-Transform (IT) | Chronological undo | Causal order | State vector |
| GOT (REDUCE) | IT + ET | No | Causal + discontinuous total order | State vector |
| GOTO (REDUCE, CoWord) | IT + ET | No | Causal order | State vector |
| Google Wave OT | Transform + composition (IT) | No | Causal + central server + stop'n'wait | Scalar |
| COT (REDUCE, CoWord) | IT only | Undo any op | Causal + discontinuous total order | Context vector |
| TIBOT | IT only | No | Causal order | Scalar |
| SOCT4 | Forward transform (IT) | No | Continuous total order | Scalar |

## Timestamp Schemes

Two timestamp approaches are used across OT and CRDT systems:

**Vector-based timestamps**: Each site maintains a vector with one element per co-editing participant. Used by adOPTed, GOT, GOTO, SOCT2, COT. Provides precise causality detection but scales linearly with participant count.

**Scalar timestamps**: Fixed number of variables regardless of participant count. Used by Jupiter, NICE, Google Wave/Docs, TIBOT, POT, SOCT3/4. Simpler but requires additional mechanisms for causality tracking.

Neither scheme is unique to OT or CRDT — both approaches appear in solutions from each family.

## Transparent Adaptation Approach

The Transparent Adaptation (TA) approach separates collaboration capabilities from editing functionality:

1. **Single-user editor**: Existing editor handles all conventional editing (UI, rendering, local operations)
2. **Collaboration adaptor**: Bridges the editor and OT engine, converting between editor-native operations and OT-compliant operations
3. **OT engine**: Handles transformation, propagation, and consistency

This approach avoids building co-editors from scratch. CoWord (for Microsoft Word), CoPPT (for PowerPoint), and Codox Apps (for Gmail, Evernote, WordPress, TinyMCE, Quill, Slate) use this pattern.

The success of TA depends on the correctness and efficiency of the bridging layer — mapping between editor-native data models and OT-compliant operation representations.

## Industry Products

### Major OT-Based Products

- **Google Docs** (2010): Server-based OT, scalar timestamps, stop'n'wait propagation
- **Google Wave / Apache Wave** (2009): Server-based OT, application-specific transform functions
- **ShareJS**: Open-source OT engine, server-based, supports any data type
- **CKEditor Collaboration**: Server-based OT with real-time co-editing
- **Etherpad**: Open-source collaborative editor using OT
- **Dropbox Paper** (2017): OT-based rich-text co-editor
- **Box Notes** (2017): OT-based collaboration in Box cloud storage
- **Tencent TAPD** (2018): OT integrated into cloud-based agile development platform
- **SubEthaEdit**: P2P collaborative text editor using OT

### Design Trend

The emerging pattern separates collaboration from editing: encapsulate OT-powered collaboration in reusable components, then integrate with separately designed single-user editors via APIs. This complements the TA approach and reduces engineering investment for new co-editors.
