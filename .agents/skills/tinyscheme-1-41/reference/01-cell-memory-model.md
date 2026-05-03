# Cell Memory Model & Allocation

## Contents
- The Cell Structure
- Type System and Flags
- Number Representation
- Symbol Interning (oblist)
- Vector Storage
- Special Static Cells
- Heap Segments and Free List
- Cell Allocation Paths

## The Cell Structure

Every Scheme value is a `struct cell` on the managed heap. Defined in `scheme-private.h`:

```c
struct cell {
  unsigned int _flag;
  union {
    struct {
      char   *_svalue;
      int   _length;
    } _string;
    num _number;
    port *_port;
    foreign_func _ff;
    struct {
      struct cell *_car;
      struct cell *_cdr;
    } _cons;
  } _object;
};
```

The `_flag` field is a bit-packed integer carrying type identity and GC metadata. The union stores the value payload — exactly one variant is active per cell, determined by the type bits in `_flag`.

## Type System and Flags

### Type Codes (5 low bits: `T_MASKTYPE = 31`)

```c
enum scheme_types {
  T_STRING=1, T_NUMBER=2, T_SYMBOL=3, T_PROC=4,
  T_PAIR=5, T_CLOSURE=6, T_CONTINUATION=7, T_FOREIGN=8,
  T_CHARACTER=9, T_PORT=10, T_VECTOR=11, T_MACRO=12,
  T_PROMISE=13, T_ENVIRONMENT=14
};
```

### Metadata Flags (upper bits)

- `T_SYNTAX (4096)` — Cell is a special-form syntax object (lambda, if, define, etc.)
- `T_IMMUTABLE (8192)` — Cannot be modified by set-car!, set-cdr!, string-set!, vector-set!
- `T_ATOM (16384)` — GC-only flag: cell has no pointer fields to traverse (leaf node)
- `MARK (32768)` — GC mark bit, set during traversal

Access via macros:
```c
#define typeflag(p)   ((p)->_flag)
#define type(p)       (typeflag(p)&T_MASKTYPE)
#define is_mark(p)    (typeflag(p)&MARK)
#define setmark(p)    typeflag(p) |= MARK
#define clrmark(p)    typeflag(p) &= UNMARK  /* UNMARK = 32767 */
```

### Type Categories

- **Atoms** (T_ATOM bit set): strings, numbers, characters, ports, procedures, foreign functions — no pointers to other cells
- **Non-atoms**: pairs, closures, continuations, macros, promises, environments, vectors — contain pointers requiring GC traversal
- **Syntax objects**: symbols with T_SYNTAX flag — dispatch directly to opcodes instead of being looked up as variables

## Number Representation

Numbers use a tagged union (`struct num`) distinguishing exact integers from floating-point reals:

```c
typedef struct num {
     char is_fixnum;
     union {
          int64_t ivalue;
          double rvalue;
     } value;
} num;
```

- `is_fixnum == 1`: exact integer stored in `ivalue`
- `is_fixnum == 0`: real (double) stored in `rvalue`

Arithmetic operations preserve exactness: integer + integer = integer, but integer + real = real. Division returns integer only when the result is exact (`a % b == 0`).

Global constants:
```c
static num num_zero;  /* { .is_fixnum=1, .ivalue=0 } */
static num num_one;   /* { .is_fixnum=1, .ivalue=1 } */
```

`integer?` returns true if the cell is a number AND either `is_fixnum` is set OR the double value equals its integer truncation.

## Symbol Interning (oblist)

Symbols are **cons cells** of type `T_SYMBOL`: `(string . properties)`. The car holds an immutable string with the symbol name; the cdr holds property list data (when `USE_PLIST=1`).

```c
pointer mk_symbol(scheme *sc, const char *name) {
     pointer x = oblist_find_by_name(sc, name);
     if (x != sc->NIL) return x;       /* already interned */
     return oblist_add_by_name(sc, name);
}
```

The **oblist** (object list) interns symbols by name. Case-insensitive per R5RS §2 using `stricmp()`. Two implementations:

- **Hash table** (default): vector of 461 buckets, each bucket is an alist of symbols. `hash_fn()` rotates left 5 bits then XORs each character.
- **Linear list**: single cons list scanned sequentially.

Symbols are immutable — the string in car is marked `T_IMMUTABLE`.

## Vector Storage

Vectors use **consecutive cells** packed 2-elements-per-cell via car/cdr pairs:

```c
static pointer vector_elem(pointer vec, int ielem) {
     int n = ielem / 2;
     if (ielem % 2 == 0) return car(vec + 1 + n);
     else                return cdr(vec + 1 + n);
}
```

The first cell stores the vector's length in its number field and has type `T_VECTOR | T_ATOM`. Elements start at `vec + 1`, each pair of elements stored as one cons cell (marked immutable so set-car!/set-cdr! don't corrupt the structure).

For a vector of length N, `N/2 + N%2 + 1` consecutive cells are needed. Allocation uses `get_consecutive_cells()` which searches the free list for consecutive address ranges — maintained by keeping the free list sorted by address.

## Special Static Cells

Four special cells are statically allocated inside `struct scheme` and never GC'd (permanently marked):

- **NIL** (`sc->_NIL`) — Empty list, also used as null pointer in free list
- **T** (`sc->_HASHT`) — Boolean true (`#t`)
- **F** (`sc->_HASHF`) — Boolean false (`#f`)
- **EOF_OBJ** (`sc->_EOF_OBJ`) — End-of-file object

Additionally, **sink** (`sc->_sink`) is a pair used as the out-of-memory sentinel. Its car holds recently allocated objects not yet reachable from GC roots (see garbage collection).

All are initialized in `scheme_init()`:
```c
typeflag(sc->NIL) = T_ATOM | MARK;
car(sc->NIL) = cdr(sc->NIL) = sc->NIL;
```

## Heap Segments and Free List

Cells are allocated in **segments** of `CELL_SEGSIZE` (5000) cells. Up to `CELL_NSEGMENT` (10) segments can exist simultaneously, stored in parallel arrays:

```c
char *alloc_seg[CELL_NSEGMENT];   /* raw malloc pointers */
pointer cell_seg[CELL_NSEGMENT];  /* aligned cell array pointers */
int last_cell_seg;                 /* highest used index */
```

`alloc_cellseg()` allocates a segment, aligns it to `ADJ` (32) boundary, then inserts both the raw pointer and aligned pointer into their arrays sorted by address. Each new segment's cells are linked into the free list in **address order**.

The free list is maintained as a singly-linked chain through cdr fields of free cells:
```c
pointer free_cell;  /* head of free list */
int64_t fcells;     /* count of free cells */
```

Address-sorted ordering serves two purposes:
1. GC sweep can scan in address order and rebuild the free list efficiently
2. `find_consecutive_cells()` can find runs of adjacent cells for vector allocation

## Cell Allocation Paths

Three allocation paths depending on requirements:

### Single cell: `get_cell(sc, a, b)`
1. Try `get_cell_x()` — pop from free list head
2. If empty, call `_get_cell()`: run GC, try again
3. If still empty, allocate new segment via `alloc_cellseg(sc, 1)`
4. If all fail, return `sc->sink` (out of memory sentinel)

Recent allocations are protected from premature GC via `push_recent_alloc()` — they're linked through `car(sc->sink)` so the GC marks them even though no root points to them yet.

### Consecutive cells: `get_consecutive_cells(sc, n)`
1. Search free list with `find_consecutive_cells()` for a run of n adjacent addresses
2. If not found, GC and retry
3. If still not found, allocate new segment and retry
4. New segments start with all cells consecutive, so this always succeeds if malloc works

### Reserve: `reserve_cells(sc, n)`
Ensures at least n free cells exist. Returns T on success, NIL on failure. Used before operations that need guaranteed allocation (e.g., before building a list of known length).
