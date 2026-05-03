# Builtins and Extensions

## Contents
- Arithmetic Builtins
- Comparison Builtins
- List Operation Builtins
- Display And Print
- Number Conversion Utilities
- REPL Implementation
- File Interpretation Mode
- Error Handling Patterns
- Garbage Collection Strategies
- Memory Discipline

## Arithmetic Builtins

All arithmetic operates on string-encoded integers. Each builtin parses all arguments, computes, then converts back to string:

```c
node *plus(list *args) {
    long sum = 0L;
    char *dummy;
    node *n = args->start->next;
    while (n != args->end) {
        sum += p_strtol(n->data, &dummy);
        n = n->next;
    }
    return new_node(true, ltoa(sum));
}

node *mul(list *args) {
    long prod = 1L;
    char *dummy;
    node *n = args->start->next;
    while (n != args->end) {
        prod *= p_strtol(n->data, &dummy);
        n = n->next;
    }
    return new_node(true, ltoa(prod));
}
```

**sub** has special single-argument behavior (negation):

```c
node *sub(list *args) {
    if (args->start->next == args->end) return NULL;
    long sum = 0L;
    char *dummy;
    // For single arg: (- x) → -x. For multi: (- a b c) → a - b - c
    if (args->start->next->next != args->end)
        sum += 2 * p_strtol(args->start->next->data, &dummy);

    node *n = args->start->next;
    while (n != args->end) {
        sum -= p_strtol(n->data, &dummy);
        n = n->next;
    }
    return new_node(true, ltoa(sum));
}
```

The `sum += 2 * first` trick: for single arg, `0 + 2*x - x = x`, then `-x` from the loop gives `-x`. For multiple args, `2*a - a - b - c = a - b - c`.

**divi** (integer division) with reciprocal for single argument:

```c
node *divi(list *args) {
    if (args->start->next == args->end) return NULL;
    long prod = 1L;
    char *dummy;
    long num = p_strtol(args->start->next->data, &dummy);

    if (args->start->next->next == args->end) {
        // Single arg: (/ x) → 1/x (integer division)
        if (num == 0L) return NULL;
        prod /= num;
    } else {
        prod = num;
    }

    node *n = args->start->next->next;
    while (n != args->end) {
        num = p_strtol(n->data, &dummy);
        if (num == 0L) return NULL;  // division by zero → NULL
        prod /= num;
        n = n->next;
    }
    return new_node(true, ltoa(prod));
}
```

## Comparison Builtins

All return `"1"` (true) or `"0"` (false) as string atoms:

```c
node *gth(list *args) {
    char *truth = "1";
    char *dummy;
    node *n = args->start->next;
    while (n != args->end) {
        node *m = n->next;
        if (m != args->end) {
            long nl = p_strtol(n->data, &dummy);
            long ml = p_strtol(m->data, &dummy);
            if (nl <= ml) truth = "0";
        }
        n = m;
    }
    return new_node(true, truth);
}
```

**>** checks strict decrease: `(> 5 3 1)` → `"1"`, `(> 5 3 3)` → `"0"`.

**<** checks strict increase. **=** checks all equal. Same structure, different comparison operators.

## List Operation Builtins

```c
node *bcar(list *args) {
    node *n = car(args);
    if (n->atom) return NULL;
    return car(n->data);
}

node *bcdr(list *args) {
    node *n = car(args);
    if (n->atom) return NULL;
    return new_node(false, cdr(n->data));
}

node *cons(list *args) {
    node *ca = args->start->next;
    node *cd = args->start->next->next;
    if (cd->atom) {
        // cons onto atom: create new list
        list *new = new_list();
        insert(new, cd);
        insert(new, ca);
        return new_node(false, new);
    }
    // cons onto list: prepend to existing
    insert(cd->data, new_node(ca->atom, ca->data));
    return args->start->next->next;
}

node *blist(list *args) {
    return new_node(false, args);  // wrap argument list as a node
}
```

**eq?** compares two arbitrary S-expressions (atoms or lists):

```c
node *lequ(list *args) {
    node *ca = args->start->next;
    node *cd = args->start->next->next;

    if (ca->atom && cd->atom)
        return equ(args);  // reuse numeric equality

    char *eq = "1";
    if (!ca->atom && !cd->atom) {
        bool equal = ls_compare(ca->data, cd->data);
        if (!equal) eq = "0";
    } else {
        eq = "0";  // atom vs list → not equal
    }
    return new_node(true, eq);
}
```

**ls_compare** recursively compares two lists element by element:

```c
bool ls_compare(list *L1, list *L2) {
    node *n = L1->start->next;
    node *m = L2->start->next;
    while (n != L1->end && m != L2->end) {
        if (n->atom != m->atom) return false;
        if (n->atom) {
            if (strcmp(n->data, m->data)) return false;
        } else {
            if (!ls_compare(n->data, m->data)) return false;
        }
        n = n->next;
        m = m->next;
    }
    return n == L1->end && m == L2->end;
}
```

## Display And Print

**display** evaluates its argument and prints to stdout:

```c
node *display(list *args) {
    if (args->start->next == args->end) return NULL;
    s_print(args->start->next);
    printf("\n");
    Returntype ret = DISPLAYED;
    return (node *)ret;  // special return value
}
```

Returns a cast enum value (`DISPLAYED = 0x1`) rather than a real node. Callers check for this to avoid printing the return value in REPL output.

## Number Conversion Utilities

**ltoa** — long to string, returns pointer into pre-allocated buffer:

```c
const int MAX_DIGITS = 33;

char *ltoa(long num) {
    char *convert = calloc(MAX_DIGITS + 1, sizeof(char));
    int i = 0;
    long anum = abs(num);

    if (anum == 0) {
        convert[MAX_DIGITS - 1] = '0';
        return convert + MAX_DIGITS - 1;
    }

    while (anum > 0L) {
        convert[MAX_DIGITS - i - 1] = '0' + (char)(anum % 10);
        anum /= 10;
        i++;
    }

    if (num < 0) {
        convert[MAX_DIGITS - i - 1] = '-';
        return convert + MAX_DIGITS - i - 1;
    }
    return convert + MAX_DIGITS - i;
}
```

Returns a pointer into the middle of the buffer (right-aligned). Caller must free from the buffer start, not the returned pointer — this is a known memory management issue in LIPS.

## REPL Implementation

LIPS uses `tmpfile()` to buffer stdin line by line, avoiding direct stdin parsing issues:

```c
const int LINE_LENGTH = 1024;

FILE *buff_stdin(void) {
    char *str = malloc(LINE_LENGTH * sizeof(char));
    str = fgets(str, LINE_LENGTH, stdin);

    if (feof(stdin)) {
        printf("Moritorus te saluto.\n");  // "I greet you as you depart"
        exit(1);
    }

    FILE *tmp = tmpfile();
    fputs(str, tmp);
    return tmp;
}

void repl(env *G) {
    while (1) {
        printf("--> ");
        FILE *tmp = buff_stdin();
        node *tree = parse_exp(tmp);
        fclose(tmp);
        s_print(eval(tree, G));
        printf("\n");
    }
}
```

**Why tmpfile?**: Direct `getc(stdin)` in the tokenizer conflicts with `fgets` buffering. Writing each line to a temporary file gives the parser a clean FILE* to read from without interfering with readline buffering.

**Exit**: Ctrl-D on empty line triggers EOF → `feof(stdin)` → graceful exit.

## File Interpretation Mode

Run Lisp source files sequentially, sharing the global environment:

```c
void interpret(char *fname, env *G) {
    FILE *src = fopen(fname, "r");
    if (src == NULL) {
        printf("Error opening file.\n");
        exit(1);
    }

    while (!feof(src)) {
        node *tree = parse_exp(src);
        if (tree == NULL) break;
        eval(tree, G);
    }
    fclose(src);
}

int main(int argc, char **argv) {
    env *global = new_env(GLOBAL_SIZE, NULL);

    if (argc == 1) { repl(global); return 0; }

    bool interactive = false;
    for (int i = 0; i < argc; i++) {
        if (!strcmp(argv[i], "-i") || !strcmp(argv[i], "--interactive"))
            interactive = true;
        else
            interpret(argv[i], global);
    }

    if (interactive) repl(global);
    return 0;
}
```

Files run in order, each inheriting definitions from previous files. `-i` flag opens REPL after file execution.

## Error Handling Patterns

LIPS' default: segfault on most errors. Improvement patterns:

**Return NULL for error**: Check at eval entry point:

```c
if (exp == NULL) {
    fprintf(stderr, "Error: NULL expression\n");
    return NULL;
}
```

**Use special return type**: Extend the DISPLAYED pattern:

```c
enum Returntype { OK = 0, DISPLAYED = 0x1, ERROR = 0x2 };
// After eval: if ((Returntype)result == ERROR) handle_error();
```

**Error messages with context**: Include the expression that failed:

```c
if (node->list_size < 2) {
    fprintf(stderr, "Error: '-' requires at least one argument\n");
    return NULL;
}
```

## Garbage Collection Strategies

LIPS has no GC — it relies on short-lived usage. For longer sessions, consider:

**Reference counting**: Add `int refcount` to each node. Increment on copy/share, decrement on destroy. Free when count reaches zero. Simple but cannot handle cycles.

**Mark-and-sweep**: Two-phase collection:
1. **Mark**: Starting from root set (global env, current eval stack), walk all reachable nodes, set a `marked` flag
2. **Sweep**: Walk all allocated nodes, free unmarked ones

**Semi-space copying**: Maintain two equal-sized heaps. Copy live objects to the "to" space during collection, then swap. Efficient for short-lived objects (common in interpreters).

**Tutorial approach**: The tutorial code has no GC and no systematic free — it leaks memory on every expression evaluation. Add destroy calls after each REPL iteration:

```c
void repl(env *G) {
    while (1) {
        printf("lisp> ");
        if (!fgets(input, 256, stdin)) break;

        TokenList tokens = tokenize(input);
        Node *ast = parse_tokens(tokens.tokens, &pos, tokens.count);
        int result = eval(ast, G);
        printf("%d\n", result);

        // Cleanup
        destroy_ast(ast);
        free_tokens(tokens);
    }
}
```

## Memory Discipline

Rules for C-based Lisp interpreters:

- **Every malloc needs a free**: Track allocations in eval, call, and REPL loops
- **Deep copy on sharing**: When a value enters a new scope, copy it (don't share pointers)
- **Destroy before return**: In REPL, destroy the AST after evaluation
- **Environment cleanup**: Destroy function-local envs after `call` returns (LIPS does this with `env_destroy`)
- **Global environment**: Leaked on program exit — acceptable for short-lived interpreters, needs explicit cleanup for embedded use
- **String allocation**: Every `strdup`, `malloc` for tokens, and `ltoa` buffer needs tracking
- **Sentinel nodes**: LIPS allocates two sentinel nodes per list — destroy both in `ls_destroy`

**Common leak sources**:
1. REPL loop without destroying parsed trees
2. `ltoa` returning offset pointer (caller can't free from returned address)
3. `cons` modifying existing lists (shared ownership ambiguity)
4. Environment entries never freed (hash table only frees the table struct, not entries)
