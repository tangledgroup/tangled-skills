# Garbage Collection (Schorr-Waite)

## Contents
- Algorithm Overview
- Mark Phase: Link Inversion
- GC Roots
- Sweep Phase
- Finalization
- Recent Allocation Protection
- Allocation Triggers

## Algorithm Overview

TinyScheme uses the **Schorr-Deutsch-Waite** algorithm (Algorithm E from Knuth, TAOCP Vol.1, §2.3.5), a **link-inversion** mark-and-sweep garbage collector that traverses the object graph using the objects' own pointer fields as temporary back-pointers. This avoids needing a separate traversal stack — critical for an embedded interpreter with limited memory.

The algorithm works in two phases:
1. **Mark**: Traverse from roots, marking reachable cells by temporarily rewiring car/cdr pointers
2. **Sweep**: Scan all cells, reclaiming unmarked ones into the free list

## Mark Phase: Link Inversion

The `mark()` function implements the Schorr-Waite traversal. It uses a single back-pointer variable `t` and repurposes the car/cdr fields of traversed cells to remember the path back up the tree.

```c
static void mark(pointer a) {
     pointer t, q, p;
     t = (pointer)0;
     p = a;

E2:  setmark(p);
     /* Handle vectors: mark all element cells */
     if(is_vector(p)) {
          int num = ivalue_unchecked(p)/2 + ivalue_unchecked(p)%2;
          for(i=0; i<num; i++) mark(p+1+i);
     }
     if (is_atom(p)) goto E6;

     /* E4: traverse car */
     q = car(p);
     if (q && !is_mark(q)) {
          setatom(p);   /* flag: car was moved */
          car(p) = t;   /* store back-pointer in car */
          t = p;
          p = q;
          goto E2;
     }

E5:  /* E5: traverse cdr */
     q = cdr(p);
     if (q && !is_mark(q)) {
          cdr(p) = t;   /* store back-pointer in cdr */
          t = p;
          p = q;
          goto E2;
     }

E6:  /* Up: undo link switching */
     if (!t) return;
     q = t;
     if (is_atom(q)) {
          /* car was used for back-pointer */
          clratom(q);
          t = car(q);
          car(q) = p;
          p = q;
          goto E5;
     } else {
          /* cdr was used for back-pointer */
          t = cdr(q);
          cdr(q) = p;
          p = q;
          goto E6;
     }
}
```

### How Link Inversion Works

The key insight: when descending into a child via car or cdr, the parent temporarily stores its back-pointer (`t`) in that same field. The `T_ATOM` bit on the parent indicates "car was moved" (vs cdr). When backtracking up, the algorithm restores the original pointer and continues with the other child.

Traversal pattern:
1. Mark current cell
2. Try to descend via car — if unmarked child exists, save back-pointer in car, go down
3. If car already marked or null, try cdr — if unmarked child exists, save back-pointer in cdr, go down
4. If both children done (marked or null), backtrack up using the saved back-pointers
5. During backtrack, restore original car/cdr and continue with remaining child

### The T_ATOM Bit as "Car Moved" Flag

When `car(p)` is overwritten with a back-pointer, `setatom(p)` sets the T_ATOM bit. During backtrack at E6, `is_atom(q)` checks whether car or cdr was used:
- If atom bit set → car was used, restore from car, clear bit, continue to E5 (cdr)
- If not atom → cdr was used, restore from cdr, continue to E6 (backtrack further)

## GC Roots

The `gc()` function marks all root objects before sweeping:

```c
static void gc(scheme *sc, pointer a, pointer b) {
  /* System globals */
  mark(sc->oblist);
  mark(sc->global_env);

  /* Current registers */
  mark(sc->args);
  mark(sc->envir);
  mark(sc->code);
  dump_stack_mark(sc);
  mark(sc->value);
  mark(sc->inport);
  mark(sc->save_inport);
  mark(sc->outport);
  mark(sc->loadport);

  /* Recent allocations not yet reachable from roots */
  mark(car(sc->sink));
  mark(sc->c_nest);

  /* Parameters passed to gc (cells being constructed) */
  mark(a);
  mark(b);
  /* ... sweep phase follows ... */
}
```

Root categories:
- **System**: oblist, global_env — always reachable
- **Registers**: args, envir, code, value — current evaluation state
- **Dump stack**: saved contexts from nested evaluations
- **Ports**: inport, outport, save_inport, loadport — I/O state
- **Recent allocs**: objects allocated but not yet stored in any root
- **C nesting**: `c_nest` stack for C→Scheme→C call chains

## Sweep Phase

After marking, all cells are scanned in address order (highest segment to lowest):

```c
  clrmark(sc->NIL);
  sc->fcells = 0;
  sc->free_cell = sc->NIL;
  for (i = sc->last_cell_seg; i >= 0; i--) {
    p = sc->cell_seg[i] + CELL_SEGSIZE;
    while (--p >= sc->cell_seg[i]) {
      if (is_mark(p)) {
        clrmark(p);
      } else {
        /* reclaim cell */
        if (typeflag(p) != 0) {
          finalize_cell(sc, p);
          typeflag(p) = 0;
          car(p) = sc->NIL;
        }
        ++sc->fcells;
        cdr(p) = sc->free_cell;
        sc->free_cell = p;
      }
    }
  }
```

Key details:
- NIL is explicitly unmarked before sweep (it's permanently marked)
- Cells are scanned downward within each segment (high to low address)
- Unmarked cells are prepended to the free list — since scanning goes high-to-low and prepending reverses order, the free list ends up sorted by address
- `finalize_cell()` frees C heap memory for strings (the `_svalue` pointer) and ports (the `port *` struct)
- Reclaimed cells have their type cleared to 0

## Finalization

```c
static void finalize_cell(scheme *sc, pointer a) {
  if(is_string(a)) {
    sc->free(strvalue(a));
  } else if(is_port(a)) {
    if(a->_object._port->kind & port_file
       && a->_object._port->rep.stdio.closeit) {
      port_close(sc, a, port_input | port_output);
    }
    sc->free(a->_object._port);
  }
}
```

Strings allocate their character data via `sc->malloc()` in `store_string()`. Ports allocate the `struct port` on the C heap. Both must be freed during GC sweep since they're not part of the cell segment.

## Recent Allocation Protection

The `sink` pair's car field holds a chain of recently allocated cells that aren't yet reachable from any GC root:

```c
static void push_recent_alloc(scheme *sc, pointer recent, pointer extra) {
  pointer holder = get_cell_x(sc, recent, extra);
  typeflag(holder) = T_PAIR | T_IMMUTABLE;
  car(holder) = recent;
  cdr(holder) = car(sc->sink);
  car(sc->sink) = holder;
}

static INLINE void ok_to_freely_gc(scheme *sc) {
  car(sc->sink) = sc->NIL;
}
```

This solves a subtle race: when `get_cell()` allocates a new cell and returns it, the caller hasn't stored it anywhere reachable yet. If GC runs before storage completes, the cell would be collected. `push_recent_alloc()` prevents this by making the cell reachable through `car(sc->sink)`.

`ok_to_freely_gc()` is called at the start of each opcode execution in `Eval_Cycle()`, clearing the recent alloc chain now that all cells should be properly rooted.

## Allocation Triggers

GC is triggered automatically during allocation:

1. **`_get_cell()`**: If free list empty, runs GC. If fewer than `last_cell_seg * 8` cells recovered, allocates a new segment to avoid fruitless repeated GCs.
2. **`reserve_cells()`**: Checks if enough cells exist → GC if not → allocate segment if still not enough.
3. **`get_consecutive_cells()`**: Searches for consecutive run → GC → search again → allocate segment → search again.

The `gc()` function can also be called explicitly via the Scheme-level `(gc)` procedure. Verbose mode via `(gc-verbose #t)` prints recovery counts to the output port.
