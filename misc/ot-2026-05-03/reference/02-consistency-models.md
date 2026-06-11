# Consistency Models

## Contents
- CC Model (Causality + Convergence)
- CCI Model (adds Intention Preservation)
- CSM Model (Single/Multi-Operation Effects)
- CA Model (Causality + Admissibility)
- Transformation Properties for Convergence
- Inverse Properties for Undo
- Property Preconditions

## CC Model (Causality + Convergence)

The original consistency model from Ellis and Gibbs (1989), requiring two properties:

**Causality Preservation**: Causally dependent operations execute in cause-effect order at all sites. The causal relationship is defined by Lamport's happened-before relation. Concurrent operations (not causally related) may execute in different orders at different replicas.

**Convergence**: All document replicas are identical at quiescence — after all generated operations have been executed at all sites.

Limitation: Convergence alone can be achieved by any serialization protocol, but serialization doesn't preserve the user's original intention. Two serialized orderings can both converge but produce different results from what the users intended.

## CCI Model (adds Intention Preservation)

Extends CC with a third property proposed by Sun et al. (1998):

**Intention Preservation**: The effect of executing an operation on any document state matches the intention defined by applying it on its generation state. The intention of operation `O` is the execution effect achieved by applying `O` on the document state from which `O` was generated.

This is the key property that distinguishes OT from simple serialization. Serialization can achieve convergence but not intention preservation — operations executed in their original form may produce wrong effects when applied out of generation order.

The CCI model is independent of document types, operation types, or supporting techniques (OT, multi-versioning, serialization). It defines generic requirements applicable to any collaborative editing system.

Intention preservation was refined at three levels:
1. Generic consistency requirement for collaborative editing systems
2. Operation context-based pre- and post-transformation conditions for generic OT functions
3. Specific verification criteria for string-wise insert/delete in plain text editors

## CSM Model (Single/Multi-Operation Effects)

An alternative formal model by Li and Li that replaces intention preservation with provable conditions:

**Causality**: Same as CC model.

**Single-operation effects**: The effect of executing any operation in any execution state achieves the same effect as in its generation state.

**Multi-operation effects**: The effects relation (object ordering) of any two operations is maintained after both are executed in any states.

The CSM model requires specifying a total order of all objects, effectively reducing to tie-breaking policies for concurrent inserts at the same position. This makes the total order application-specific and increases algorithm complexity.

## CA Model (Causality + Admissibility)

An alternative to CSM that avoids requiring explicit total order specification:

**Causality**: Same as CC model.

**Admissibility**: Every operation invocation is admissible in its execution state — it must not violate any effects relation (object ordering) established by earlier invocations. The ordering is effectively determined by the effects of operations when generated, not by an externally specified total order.

The CA model implies convergence and imposes additional constraints on object ordering, making it stronger than convergence alone. It reduces time/space complexity compared to CSM by not maintaining explicit total order in the algorithm.

In the CA approach, correctness is achieved synergistically: first identify and prove sufficient conditions for transformation functions, then design a control procedure that ensures those conditions. The control procedure and transform functions work together rather than satisfying rigid transformation properties independently.

## Transformation Properties for Convergence

Two formal properties govern convergence in OT systems. Responsibility for maintaining them can be divided between the control algorithm and the transformation functions.

### CP1 / TP1 (Pairwise Convergence)

For every pair of concurrent operations `op1` and `op2` defined on the same state:

```
op1 ∘ T(op2, op1) ≡ op2 ∘ T(op1, op2)
```

Where `∘` denotes sequential execution and `≡` denotes equivalence of results. This means executing `op1` then the transformed `op2` produces the same document state as executing `op2` then the transformed `op1`.

**Precondition**: Required only if the OT system allows two operations to execute in different orders at different sites.

### CP2 / TP2 (Triple Convergence)

For every three concurrent operations `op1`, `op2`, and `op3` defined on the same state:

```
T(op3, op1 ∘ T(op2, op1)) = T(op3, op2 ∘ T(op1, op2))
```

This ensures that transforming a third operation against two equivalent sequences (op1 then transformed op2, vs op2 then transformed op1) produces the same result. It handles the case where `op3` arrives late and must be transformed against a sequence of already-executed operations.

**Precondition**: Required only if the OT system allows two operations to be IT-transformed in two different document states (contexts). This is relevant when operations propagate through different paths in distributed systems.

Some OT systems enforce CP1/TP1 and CP2/TP2 in the transformation functions (the functions must satisfy these properties for all inputs). Others shift responsibility to the control algorithm, which constrains execution order so the functions only need to handle a subset of cases.

## Inverse Properties for Undo

Three properties govern correct group undo behavior. They are required only when the OT system supports undo operations.

### IP1 (Inverse Identity)

```
S ∘ op ∘ op̄ = S
```

The sequence `op` followed by its inverse `op̄` is equivalent to an identity operation — the document returns to state `S`. This is a basic requirement for any undo system, not specific to OT.

### IP2 (Inverse Transparency)

```
T(opx, op ∘ op̄) = opx
```

Transforming any operation `opx` against the sequence `op ∘ op̄` yields `opx` unchanged. The do-undo pair has no effect on the transformation of other operations.

**Precondition**: Required only if the system allows an operation to be transformed against a do-undo pair one-by-one.

### IP3 (Inverse Commutation)

```
op̄' = T(op̄, T(op2, op1)) = op̄₁' = overline{T(op1, op2)}
```

The transformed inverse equals the inverse of the transformed operation. This ensures that undoing a transformed operation produces the correct result.

**Precondition**: Required only if the system allows an inverse operation to be transformed against a concurrent operation defined on the same document state.

## Property Preconditions Summary

Not all properties are required in every OT system. The preconditions determine which apply:

| Property | Required When |
|----------|---------------|
| CP1/TP1 | Operations can execute in different orders at different sites |
| CP2/TP2 | Operations transformed in different document contexts (distributed propagation paths) |
| IP1 | System supports undo |
| IP2 | Operations transformed against do-undo pairs one-by-one |
| IP3 | Inverse operations transformed against concurrent operations |

Systems without undo (Google Wave, Google Docs, ShareJS) need only CP1/TP1 and possibly CP2/TP2. Systems with full group undo (adOPTed, AnyUndo, COT) require all inverse properties.
