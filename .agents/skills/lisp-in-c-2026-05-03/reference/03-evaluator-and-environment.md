# Evaluator and Environment

## Contents
- The Eval-Apply Cycle
- LIPS Style: Complete eval() Function
- Tutorial Style: Type-Based Dispatch
- Special Forms
- User-Defined Function Calls
- Environment Chains And Lexical Scoping
- Truth Testing

## The Eval-Apply Cycle

Every Lisp evaluator follows the same pattern:

1. **Atom**: If number, return as-is. If symbol, look up in environment.
2. **List**: Evaluate first element (the operator). If it's a special form, handle directly. Otherwise evaluate all arguments, then apply the operator to them.
3. **Apply**: For builtins, call the C function. For user-defined functions, create a new environment binding parameters to evaluated arguments, then eval the body.

## LIPS Style: Complete eval() Function

```c
node *eval(node *exp, env *E) {
    if (exp == NULL || (Returntype)exp == DISPLAYED || E == NULL) {
        perror("NULL return type somewhere\n");
        return NULL;
    }

    // --- Atom case ---
    if (exp->atom) {
        char *sym = exp->data;
        char *end = calloc(1, sizeof(char));
        p_strtol(sym, &end);

        if (end == sym) {
            // Failed to parse as number → it's a symbol
            return lookup(sym, E);
        }
        // Parsed successfully → it's a number, return as-is
        return exp;
    }

    // --- List case ---
    list *ls = exp->data;
    node *cr = car(ls);  // first element (operator)
    if (cr == NULL) return NULL;

    // If operator is itself a list, eval it first
    if (!(cr->atom)) {
        node *proc = eval(cr, E);
        list *args = evaluate(cdr(ls), E);
        return call(proc, args, E);
    }

    // --- Special forms (operator is an atom but not a builtin) ---
    char *form = cr->data;

    if (!strcmp(form, "if")) {
        node *test = eval(car(cdr(ls)), E);
        if (truth(test))
            return eval(car(cdr(cdr(ls))), E);   // then branch
        return eval(car(cdr(cdr(cdr(ls)))), E);   // else branch
    }

    if (!strcmp(form, "def")) {
        define(cr->data, eval(car(cdr(cdr(ls))), E), E);
        return new_node(false, new_list());  // return empty list
    }

    if (!strcmp(form, "quote"))
        return car(cdr(ls));  // return argument without evaluation

    // --- Try builtin first ---
    list *args = evaluate(cdr(ls), E);
    node *result = builtins(form, args);

    if (result == NULL) {
        // Not a builtin → user-defined function
        node *proc = eval(cr, E);
        return call(proc, args, E);
    }

    return result;
}
```

**Number detection**: `p_strtol` attempts to parse the string as a number. If it fails (`end == sym`), the atom is treated as a symbol and looked up in the environment. This means all numbers must be valid integer strings — no floats, no leading whitespace.

**Evaluation order**: Arguments are evaluated left-to-right by `evaluate()`, which walks the list and calls `eval` on each element:

```c
list *evaluate(list *exps, env *E) {
    list *result = new_list();
    node *n = exps->start->next;
    while (n != exps->end) {
        node *n1 = new_node(n->atom, n->data);
        add(result, eval(n1, E));
        n = n->next;
    }
    return result;
}
```

## Tutorial Style: Type-Based Dispatch

The tutorial uses enum-based type checking for cleaner dispatch:

```c
int eval(Node *node, Env *env) {
    if (node->type == NODE_NUMBER)
        return node->number;

    if (node->type == NODE_SYMBOL) {
        while (env) {
            if (strcmp(env->symbol, node->symbol) == 0)
                return env->value;
            env = env->next;
        }
        fprintf(stderr, "Undefined symbol: %s\n", node->symbol);
        exit(1);
    }

    // NODE_LIST
    if (strcmp(node->list[0]->symbol, "+") == 0) {
        int sum = 0;
        for (int i = 1; i < node->list_size; i++)
            sum += eval(node->list[i], env);
        return sum;
    }

    if (strcmp(node->list[0]->symbol, "-") == 0) {
        int result = eval(node->list[1], env);
        for (int i = 2; i < node->list_size; i++)
            result -= eval(node->list[i], env);
        return result;
    }

    if (strcmp(node->list[0]->symbol, "define") == 0) {
        char *sym = node->list[1]->symbol;
        int val = eval(node->list[2], env);
        env = add_to_env(env, sym, val);
        return val;
    }

    fprintf(stderr, "Unknown operator\n");
    exit(1);
}
```

**Key difference**: Tutorial returns `int` directly (single return type), while LIPS returns `node*` (unified S-expression type). The tutorial approach is simpler but cannot represent lists or functions as return values from eval — only numbers.

## Special Forms

Special forms control evaluation order. They are recognized by name and handled before argument evaluation:

**if**: Evaluate test, then evaluate exactly one branch:

```c
if (!strcmp(form, "if")) {
    node *test = eval(car(cdr(ls)), E);
    if (truth(test))
        return eval(car(cdr(cdr(ls))), E);
    return eval(car(cdr(cdr(cdr(ls)))), E);
}
```

Note: Only the chosen branch is evaluated. The other branch is ignored entirely.

**def/define**: Bind a symbol to an evaluated value in the current environment:

```c
if (!strcmp(form, "def")) {
    define((char*)car(cdr(ls))->data, eval(car(cdr(cdr(ls))), E), E);
    return new_node(false, new_list());
}
```

The value expression is evaluated; the symbol name is not (it's taken directly from the AST).

**quote**: Return the argument without evaluation:

```c
if (!strcmp(form, "quote"))
    return car(cdr(ls));
```

## User-Defined Function Calls

Functions are stored as quoted lists: `(def plus1 '((x) (+ x 1)))`. The value of `plus1` is a list containing the parameter list `(x)` and body `((+ x 1))`.

**call** creates a new environment frame, binds parameters to evaluated arguments, then evaluates the body:

```c
const int ENV_SIZE = 10;

node *call(node *func, list *passed_args, env *E) {
    list *fn = func->data;
    list *fn_args = car(fn)->data;    // parameter names
    list *fn_body = cdr(fn);          // body expressions

    env *fn_env = new_env(ENV_SIZE, E);  // new frame, outer = caller's env

    node *arg1 = fn_args->start->next;
    node *arg2 = passed_args->start->next;
    while (arg1 != fn_args->end && arg2 != passed_args->end) {
        define(arg1->data, arg2, fn_env);
        arg1 = arg1->next;
        arg2 = arg2->next;
    }

    if (arg1 != fn_args->end || arg2 != passed_args->end) {
        perror("Function called with wrong number of arguments");
        return NULL;
    }

    node *retval;
    node *n = fn_body->start->next;
    while (n != fn_body->end) {
        retval = eval(n, fn_env);  // last expression's value wins
        n = n->next;
    }

    env_destroy(fn_env);
    return retval;
}
```

**Tutorial style** function call with typed nodes:

```c
typedef struct Function {
    char **parameters;
    int param_count;
    Node *body;
} Function;

// In eval, when symbol resolves to a function:
if (env_entry->is_function) {
    Function *func = env_entry->function;
    Env *new_env = env;
    for (int i = 0; i < func->param_count; i++) {
        int arg_value = eval(node->list[i + 1], env);
        new_env = add_to_env(new_env, func->parameters[i], arg_value);
    }
    return eval(func->body, new_env);
}
```

## Environment Chains And Lexical Scoping

Each function call creates a new environment frame. The `outer` pointer chains to the enclosing scope:

```c
env *new_env(int size, env *outer) {
    env *E = malloc(sizeof(env));
    E->outer = outer;
    E->table = hcreate(size);
    return E;
}

node *lookup(char *sym, env *E) {
    if (E == NULL) return NULL;
    entry *var = hsearch(sym, E->table);
    if (var == NULL)
        return lookup(sym, E->outer);  // walk up the chain
    return var->data;
}
```

**Lexical scoping**: The environment chain captures the scope at function definition time. When `call` creates `fn_env` with `outer = E`, it captures whatever `E` was at call time — not at definition time. This works correctly because the function body is stored as a quoted list that references symbols by name, and those symbols are resolved against the chain starting from `fn_env`.

**Tutorial style** achieves the same with linked-list environments:

```c
Env *add_to_env(Env *env, char *sym, int val) {
    Env *e = malloc(sizeof(Env));
    e->symbol = strdup(sym);
    e->value = val;
    e->next = env;  // chain to outer scope
    return e;
}
```

Lookup walks the linked list. If not found in current frame, continues via `next` pointer.

## Truth Testing

Lisp truth is simple: nonzero values are true, zero and NULL are false:

```c
bool truth(node *n) {
    if (n == NULL) return false;
    if (!n->atom) return true;  // non-empty list is always true

    char *dat = n->data;
    char *dum;
    return p_strtol(dat, &dum) != 0L;  // "0" → false, anything else → true
}
```

Lists are always truthy (they're non-null structures). Atoms are truthy unless they parse as the number `0`.
