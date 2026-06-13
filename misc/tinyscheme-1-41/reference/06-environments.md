# Environments & Symbol Table

## Contents
- Environment Structure
- Hash Table vs Alist Backends
- Symbol Table (oblist)
- Symbol Interning
- Environment Operations
- Named Let and Recursive Bindings

## Environment Structure

Environments are chains of frames, each frame being an alist (or hash table) of variable bindings. Represented as a cons list with `T_ENVIRONMENT` flag:

```
environment = (frame_0 . (frame_1 . (frame_2 . ... NIL)))
```

Each frame is a list of `(symbol . value)` pairs. The innermost frame (car) is searched first, then outer frames via cdr traversal.

```c
static INLINE void new_frame_in_env(scheme *sc, pointer old_env) {
  pointer new_frame;
  if (old_env == sc->NIL)
    new_frame = mk_vector(sc, 461);   /* Global env: hash table */
  else
    new_frame = sc->NIL;               /* Local frame: empty alist */
  sc->envir = immutable_cons(sc, new_frame, old_env);
  setenvironment(sc->envir);
}
```

The global environment uses a hash table (vector of 461 buckets). Local frames from closures use simple alists — they're too small and transient for hashing to be worthwhile.

## Hash Table vs Alist Backends

Two implementations controlled by `USE_ALIST_ENV`:

### Hash Table Version (default)

Global environment: vector of 461 slots, each slot is an alist of bindings hashed by symbol name. Local frames: plain alists (NIL as the frame marker).

```c
static void new_slot_spec_in_env(scheme *sc, pointer env, pointer variable, pointer value) {
  pointer slot = immutable_cons(sc, variable, value);
  if (is_vector(car(env))) {
    int location = hash_fn(symname(variable), ivalue_unchecked(car(env)));
    set_vector_elem(car(env), location,
                    immutable_cons(sc, slot, vector_elem(car(env), location)));
  } else {
    car(env) = immutable_cons(sc, slot, car(env));
  }
}
```

### Alist Version (USE_ALIST_ENV defined)

All frames are simple alists, including global:

```c
static INLINE void new_slot_spec_in_env(scheme *sc, pointer env, pointer variable, pointer value) {
  car(env) = immutable_cons(sc, immutable_cons(sc, variable, value), car(env));
}
```

### Hash Function

```c
static int hash_fn(const char *key, int table_size) {
  unsigned int hashed = 0;
  int bits_per_int = sizeof(unsigned int) * 8;
  for (const char *c = key; *c; c++) {
    hashed = (hashed << 5) | (hashed >> (bits_per_int - 5));  /* rotate left 5 */
    hashed ^= *c;
  }
  return hashed % table_size;
}
```

Rotates the hash left by 5 bits then XORs each character. The rotation spreads character contributions across all bits. Table size 461 is prime, reducing collision patterns.

## Symbol Table (oblist)

The oblist interns symbols so that the same name always produces the same cell pointer (enabling `eq?` comparison). Two implementations controlled by `USE_OBJECT_LIST`:

### Hash Table Version (default)

```c
static pointer oblist_initial_value(scheme *sc) {
  return mk_vector(sc, 461);
}

static pointer oblist_add_by_name(scheme *sc, const char *name) {
  pointer x = immutable_cons(sc, mk_string(sc, name), sc->NIL);
  typeflag(x) = T_SYMBOL;
  setimmutable(car(x));
  int location = hash_fn(name, ivalue_unchecked(sc->oblist));
  set_vector_elem(sc->oblist, location,
                  immutable_cons(sc, x, vector_elem(sc->oblist, location)));
  return x;
}

static pointer oblist_find_by_name(scheme *sc, const char *name) {
  int location = hash_fn(name, ivalue_unchecked(sc->oblist));
  for (pointer x = vector_elem(sc->oblist, location); x != sc->NIL; x = cdr(x)) {
    if (stricmp(name, symname(car(x))) == 0)
      return car(x);
  }
  return sc->NIL;
}
```

### Linear List Version

```c
static pointer oblist_find_by_name(scheme *sc, const char *name) {
  for (pointer x = sc->oblist; x != sc->NIL; x = cdr(x)) {
    if (stricmp(name, symname(car(x))) == 0)
      return car(x);
  }
  return sc->NIL;
}

static pointer oblist_add_by_name(scheme *sc, const char *name) {
  pointer x = immutable_cons(sc, mk_string(sc, name), sc->NIL);
  typeflag(x) = T_SYMBOL;
  setimmutable(car(x));
  sc->oblist = immutable_cons(sc, x, sc->oblist);
  return x;
}
```

Linear scan is O(n) but simpler. The hash version is O(1) average case.

## Symbol Interning

Symbols are **case-insensitive** per R5RS §2. All symbol names are lowercased during creation (`strlwr()`). Comparison uses `stricmp()`:

```c
pointer mk_symbol(scheme *sc, const char *name) {
     pointer x = oblist_find_by_name(sc, name);
     if (x != sc->NIL) return x;      /* Already interned — return existing */
     return oblist_add_by_name(sc, name);  /* Create new symbol */
}
```

Once created, a symbol cell is immutable and its identity is stable. `eq?` on symbols compares cell pointers — same name always gives same pointer.

The `oblist` procedure returns all interned symbols as a list:
```c
static pointer oblist_all_symbols(scheme *sc) {
  /* Hash version: iterate all buckets, collect symbols */
  /* Linear version: return sc->oblist directly */
}
```

## Environment Operations

Four primitive operations on environments:

### new_frame_in_env(sc, old_env)
Creates a new frame and prepends it to the environment chain. Used when entering a closure or let body.

### new_slot_in_env(sc, variable, value)
Adds a binding to the current (innermost) frame. For hash frames, computes bucket and inserts at head. For alist frames, conses to front.

### find_slot_in_env(sc, env, symbol, all)
Searches for a binding. Walks environment chain from inner to outer. Returns the slot (cons cell) if found, NIL otherwise. `all=1` means search all frames; `all=0` stops at first frame (used by `defined?`).

```c
static pointer find_slot_in_env(scheme *sc, pointer env, pointer hdl, int all) {
  for (pointer x = env; x != sc->NIL; x = cdr(x)) {
    pointer y;
    if (is_vector(car(x))) {
      int location = hash_fn(symname(hdl), ivalue_unchecked(car(x)));
      y = vector_elem(car(x), location);
    } else {
      y = car(x);
    }
    for (; y != sc->NIL; y = cdr(y))
      if (caar(y) == hdl) break;  /* Pointer comparison — same interned symbol */
    if (y != sc->NIL) break;
    if (!all) return sc->NIL;
  }
  return (x != sc->NIL) ? car(y) : sc->NIL;
}
```

### set_slot_in_env(sc, slot, value)
Modifies an existing binding's value: `cdr(slot) = value`. This is how `set!` works — find the slot, modify its cdr.

## Named Let and Recursive Bindings

Named let creates a recursive closure bound to the let name:

```c
/* In OP_LET2, named let case: */
if (is_symbol(car(sc->code))) {
    /* Build parameter list for closure */
    for (x = cadr(sc->code), sc->args = sc->NIL; x != sc->NIL; x = cdr(x))
        sc->args = cons(sc, caar(x), sc->args);

    /* Create closure: (lambda (params...) body) in current env */
    x = mk_closure(sc,
        cons(sc, reverse_in_place(sc, sc->NIL, sc->args), cddr(sc->code)),
        sc->envir);

    /* Bind the closure to the let name in the new frame */
    new_slot_in_env(sc, car(sc->code), x);
    sc->code = cddr(sc->code);  /* Body */
}
```

The closure captures `sc->envir` (the environment **before** the let bindings), so when the closure is called recursively, it creates a fresh frame on top of the same base — each recursive invocation gets its own binding frame.
