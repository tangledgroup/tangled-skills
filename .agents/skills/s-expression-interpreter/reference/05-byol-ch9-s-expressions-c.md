# S-Expressions in C — Build Your Own Lisp Chapter 9

## Contents
- lval Structure
- Constructors and Destructors
- List Operations (add/pop/take)
- Printing
- Parsing with mpc
- Evaluation
- builtin_op Arithmetic
- Forward Declarations

## lval Structure

Extended `lval` type supports four value kinds:

```c
enum { LVAL_ERR, LVAL_NUM, LVAL_SYM, LVAL_SEXPR };

typedef struct lval {
  int type;
  long num;
  char* err;           /* Error message string */
  char* sym;           /* Symbol name string */
  int count;           /* Number of cells in sexpr */
  struct lval** cell;  /* Pointer to array of lval* */
} lval;
```

S-expressions use a variable-sized array (`lval**`) rather than cons cells, chosen for simplicity over traditional linked-list representation.

## Constructors and Destructors

All constructors allocate on the heap via `malloc`:

```c
lval* lval_num(long x) {
  lval* v = malloc(sizeof(lval));
  v->type = LVAL_NUM; v->num = x;
  return v;
}

lval* lval_err(char* m) {
  lval* v = malloc(sizeof(lval));
  v->type = LVAL_ERR;
  v->err = malloc(strlen(m) + 1);
  strcpy(v->err, m);
  return v;
}

lval* lval_sym(char* s) {
  lval* v = malloc(sizeof(lval));
  v->type = LVAL_SYM;
  v->sym = malloc(strlen(s) + 1);
  strcpy(v->sym, s);
  return v;
}

lval* lval_sexpr(void) {
  lval* v = malloc(sizeof(lval));
  v->type = LVAL_SEXPR; v->count = 0; v->cell = NULL;
  return v;
}
```

Destructor recursively frees all nested values:

```c
void lval_del(lval* v) {
  switch (v->type) {
    case LVAL_NUM: break;
    case LVAL_ERR: free(v->err); break;
    case LVAL_SYM: free(v->sym); break;
    case LVAL_SEXPR:
      for (int i = 0; i < v->count; i++) { lval_del(v->cell[i]); }
      free(v->cell);
      break;
  }
  free(v);
}
```

Rule: every `malloc` has exactly one corresponding `free` via `lval_del`.

## List Operations (add/pop/take)

```c
lval* lval_add(lval* v, lval* x) {
  v->count++;
  v->cell = realloc(v->cell, sizeof(lval*) * v->count);
  v->cell[v->count-1] = x;
  return v;
}

lval* lval_pop(lval* v, int i) {
  lval* x = v->cell[i];
  memmove(&v->cell[i], &v->cell[i+1], sizeof(lval*) * (v->count-i-1));
  v->count--;
  v->cell = realloc(v->cell, sizeof(lval*) * v->count);
  return x;
}

lval* lval_take(lval* v, int i) {
  lval* x = lval_pop(v, i);
  lval_del(v);
  return x;
}
```

`lval_pop` extracts element at index `i`, shifts remaining elements, keeps original list alive. `lval_take` does same but deletes the source list — only the extracted value needs cleanup.

## Printing

Forward declaration needed for mutual recursion:

```c
void lval_print(lval* v);  /* forward declare */

void lval_expr_print(lval* v, char open, char close) {
  putchar(open);
  for (int i = 0; i < v->count; i++) {
    lval_print(v->cell[i]);
    if (i != (v->count-1)) { putchar(' '); }
  }
  putchar(close);
}

void lval_print(lval* v) {
  switch (v->type) {
    case LVAL_NUM:   printf("%li", v->num); break;
    case LVAL_ERR:   printf("Error: %s", v->err); break;
    case LVAL_SYM:   printf("%s", v->sym); break;
    case LVAL_SEXPR: lval_expr_print(v, '(', ')'); break;
  }
}
```

## Parsing with mpc

Parser rules for s-expressions (replaces Polish notation):

```c
mpca_lang(MPCA_LANG_DEFAULT,
  "                                          \
    number : /-?[0-9]+/ ;                    \
    symbol : '+' | '-' | '*' | '/' ;         \
    sexpr  : '(' <expr>* ')' ;               \
    expr   : <number> | <symbol> | <sexpr> ; \
    lispy  : /^/ <expr>* /$/ ;               \
  ",
  Number, Symbol, Sexpr, Expr, Lispy);
```

`lval_read` converts mpc AST to `lval*`:

```c
lval* lval_read(mpc_ast_t* t) {
  if (strstr(t->tag, "number")) { return lval_read_num(t); }
  if (strstr(t->tag, "symbol")) { return lval_sym(t->contents); }
  lval* x = NULL;
  if (strcmp(t->tag, ">") == 0) { x = lval_sexpr(); }
  if (strstr(t->tag, "sexpr"))  { x = lval_sexpr(); }
  for (int i = 0; i < t->children_num; i++) {
    if (strcmp(t->children[i]->contents, "(") == 0) { continue; }
    if (strcmp(t->children[i]->contents, ")") == 0) { continue; }
    if (strcmp(t->children[i]->tag,  "regex") == 0) { continue; }
    x = lval_add(x, lval_read(t->children[i]));
  }
  return x;
}
```

## Evaluation

Two-phase: read input into `lval*`, then evaluate:

```c
lval* lval_eval(lval* v) {
  if (v->type == LVAL_SEXPR) { return lval_eval_sexpr(v); }
  return v;
}

lval* lval_eval_sexpr(lval* v) {
  /* Evaluate children */
  for (int i = 0; i < v->count; i++) { v->cell[i] = lval_eval(v->cell[i]); }
  /* Error checking */
  for (int i = 0; i < v->count; i++) {
    if (v->cell[i]->type == LVAL_ERR) { return lval_take(v, i); }
  }
  /* Empty expression */
  if (v->count == 0) { return v; }
  /* Single expression */
  if (v->count == 1) { return lval_take(v, 0); }
  /* Ensure first element is symbol */
  lval* f = lval_pop(v, 0);
  if (f->type != LVAL_SYM) {
    lval_del(f); lval_del(v);
    return lval_err("S-expression Does not start with symbol!");
  }
  lval* result = builtin_op(v, f->sym);
  lval_del(f);
  return result;
}
```

## builtin_op Arithmetic

```c
lval* builtin_op(lval* a, char* op) {
  for (int i = 0; i < a->count; i++) {
    if (a->cell[i]->type != LVAL_NUM) {
      lval_del(a);
      return lval_err("Cannot operate on non-number!");
    }
  }
  lval* x = lval_pop(a, 0);
  if ((strcmp(op, "-") == 0) && a->count == 0) { x->num = -x->num; }
  while (a->count > 0) {
    lval* y = lval_pop(a, 0);
    if (strcmp(op, "+") == 0) { x->num += y->num; }
    if (strcmp(op, "-") == 0) { x->num -= y->num; }
    if (strcmp(op, "*") == 0) { x->num *= y->num; }
    if (strcmp(op, "/") == 0) {
      if (y->num == 0) {
        lval_del(x); lval_del(y);
        x = lval_err("Division By Zero!"); break;
      }
      x->num /= y->num;
    }
    lval_del(y);
  }
  lval_del(a); return x;
}
```

Supports `+`, `-` (including unary negation), `*`, `/`. Multi-argument operators fold left-to-right.
