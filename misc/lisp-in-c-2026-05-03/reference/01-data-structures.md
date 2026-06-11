# Data Structures

## Contents
- S-Expression Representation
- LIPS Style: Linked Lists With Sentinel Nodes
- Tutorial Style: Typed Union AST Nodes
- Hash Table Implementation (LIPS)
- Environment Structure
- Memory Management Patterns
- Approach Comparison

## S-Expression Representation

All Lisp values are S-expressions: atoms or lists. In C, you need a way to represent this recursive structure with explicit memory management. Two main approaches exist.

## LIPS Style: Linked Lists With Sentinel Nodes

LIPS uses circular linked lists with sentinel start/end markers. Every S-expression is a `node` (atom or list). Lists are wrapped in `linked_list` structs with sentinel nodes that simplify boundary checks.

```c
typedef struct list_node {
    bool atom;      // true = atom (string), false = list
    void *data;     // char* for atoms, list* for non-atoms
    struct list_node *next;
} node;

typedef struct linked_list {
    node *start;  // sentinel — not a real element
    node *end;    // sentinel — marks end of list
} list;
```

**Sentinel pattern**: `start` and `end` are dummy nodes. Real elements sit between them (`start->next` through `end->prev`). This eliminates null checks at boundaries:

```c
list *new_list(void) {
    list *L = malloc(sizeof(list));
    L->start = new_node(false, NULL);
    L->end = new_node(false, NULL);
    L->start->next = L->end;
    L->end->next = L->start;  // circular
    return L;
}

node *car(list *L) {
    if (L->start->next == L->end) return NULL;  // empty list
    return nd_copy(L->start->next);
}
```

**String-only values**: All atoms store `char*`. Numbers are digit strings. This means arithmetic requires parsing on every operation:

```c
// p_strtol — "perfect" strtol, no leading whitespace tolerance
long p_strtol(char *str, char **end) {
    long num = 0;
    char *i = str;
    while (*i != '\0') {
        if (i == str && *i == '-') { i++; continue; }
        if (*i < '0' || *i > '9') { *end = str; break; }
        num *= 10;
        num += (long)*i - '0';
        i++;
    }
    if (*str == '-') num = -num;
    return num;
}
```

**Constants**: `MAX_SYMBOL_LENGTH = 32` — tokens are capped at 32 characters. `MAX_DIGITS = 33` — buffer for long-to-string conversion including sign.

## Tutorial Style: Typed Union AST Nodes

The tutorial approach uses a tagged union with enum discriminant, providing compile-time type safety:

```c
typedef enum { NODE_NUMBER, NODE_SYMBOL, NODE_LIST } NodeType;

typedef struct Node {
    NodeType type;
    union {
        int number;
        char *symbol;
        struct Node **list;  // array of pointers
    };
    int list_size;  // element count for NODE_LIST
} Node;
```

**Advantages over LIPS style**:
- Numbers stored as `int`, no repeated string parsing
- Type check is enum comparison, not runtime string inspection
- List size known upfront (no traversal to count)
- Closer to textbook compiler AST representation

**Disadvantages**:
- More complex struct layout (union + enum + array pointer)
- Manual list management (realloc on append)
- No sentinel pattern — explicit null/size checks everywhere

## Hash Table Implementation (LIPS)

LIPS implements its own hash table for environment storage. Open addressing with linear probing:

```c
typedef struct table_entry {
    char *key;
    void *data;
} entry;

typedef struct hash_table {
    int size;
    entry **table;
} htab;

int hash(char *key) {
    int sum = 0;
    for (; *key != '\0'; key++)
        sum = (sum + *key) * 31;
    return sum;
}

bool hoverwrite(entry *new, htab *H) {
    int key = hash(new->key) % H->size;
    for (int i = key; i < key + H->size; i++) {
        entry *spot = H->table[i % H->size];
        if (spot == NULL || !strcmp(new->key, spot->key)) {
            H->table[i % H->size] = new;
            return true;
        }
    }
    return false;  // table full
}

entry *hsearch(char *key, htab *H) {
    int hkey = hash(key) % H->size;
    for (int i = hkey; i < hkey + H->size; i++) {
        entry *spot = H->table[i % H->size];
        if (spot != NULL && !strcmp(key, spot->key))
            return spot;
    }
    return NULL;
}
```

**Hash function**: Djb2-style (`sum = (sum + *c) * 31`). Simple, fast, adequate for interpreter symbol tables.

**Linear probing**: On collision, scan forward until empty slot or matching key found. Wraps via modulo. Returns false if table is full (all slots occupied with different keys).

**Constants**: `GLOBAL_SIZE = 31` (prime, good for hash distribution). `ENV_SIZE = 10` for function-local environments — assumes no more than 10 parameters per function.

## Environment Structure

Both approaches chain environments for lexical scoping. The outer pointer creates the scope chain:

```c
typedef struct environment {
    struct environment *outer;  // NULL for global scope
    struct hash_table *table;   // or linked list in tutorial style
} env;
```

**Lookup walks outward**:

```c
node *lookup(char *sym, env *E) {
    if (E == NULL) return NULL;
    entry *var = hsearch(sym, E->table);
    if (var == NULL) return lookup(sym, E->outer);
    return var->data;
}
```

**Tutorial style environment** uses a simpler linked list:

```c
typedef struct Env {
    char *symbol;
    int value;
    struct Env *next;
} Env;

Env *add_to_env(Env *env, char *sym, int val) {
    Env *e = malloc(sizeof(Env));
    e->symbol = strdup(sym);
    e->value = val;
    e->next = env;
    return e;
}
```

## Memory Management Patterns

Without garbage collection, every `malloc` needs a matching `free`. Two patterns emerge:

**Destroy functions** (LIPS): Recursive cleanup mirrors the recursive structure:

```c
void nd_destroy(node *n) {
    if (n == NULL) return;
    if (n->atom) { free(n->data); free(n); return; }
    ls_destroy(n->data);
    free(n);
}

void ls_destroy(list *L) {
    if (L == NULL) return;
    node *n = L->start;
    while (n != L->end) {
        node *tmp = n->next;
        nd_destroy(n);
        n = tmp;
    }
    nd_destroy(L->end);
    free(L);
}
```

**Deep copy** is needed when values are shared across scopes:

```c
node *nd_copy(node *n) {
    if (n == NULL) return NULL;
    if (n->atom) {
        char *data = malloc(MAX_SYMBOL_LENGTH + 1);
        return new_node(n->atom, strcpy(data, n->data));
    }
    return new_node(false, ls_copy(n->data));
}
```

**Tutorial style** has simpler but less systematic cleanup — the tutorial code doesn't include free functions, which is a memory leak in long-running sessions.

## Approach Comparison

| Concern | LIPS Style | Tutorial Style |
|---------|-----------|----------------|
| Type safety | None (void*, runtime checks) | Compile-time (enum + union) |
| Number handling | String parsing every op | Native int storage |
| List operations | Sentinel nodes simplify bounds | Explicit size tracking |
| Memory discipline | Systematic destroy functions | Ad-hoc, leak-prone |
| Environment lookup | O(1) hash + chain walk | O(n) per frame + chain walk |
| Code complexity | More boilerplate (sentinels, copy) | Simpler structs, fewer functions |
| Extensibility | Hard to add new types (string-only) | Easy: add enum variant + union field |

**Recommendation**: Use tutorial style for learning and extensibility. Use LIPS style when studying sentinel-node patterns and hash table implementations from scratch.
