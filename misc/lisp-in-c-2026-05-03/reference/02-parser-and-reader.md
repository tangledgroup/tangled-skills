# Parser and Reader

## Contents
- Tokenization Strategies
- LIPS Style: Char-By-Char Tokenizer
- Tutorial Style: strtok Tokenizer
- Recursive Descent Parser
- Quote Syntax Sugar
- Error Handling
- Print/Writer Functions

## Tokenization Strategies

Tokenization breaks input text into atoms, `(`, and `)`. Two approaches differ in how they handle whitespace and delimiters.

## LIPS Style: Char-By-Char Tokenizer

Reads one character at a time from a FILE*, skipping whitespace, then accumulating until a delimiter:

```c
const int MAX_SYMBOL_LENGTH = 32;

bool sym_end(int c) {
    return c == ' ' || c == '\t' || c == '\n' ||
           c == EOF || c == '(' || c == ')' || c == '\'';
}

char *next_token(FILE *src) {
    char *tok = malloc(MAX_SYMBOL_LENGTH + 1);
    int i = 0;
    int c = ' ';

    // skip whitespace
    while (c == ' ' || c == '\t' || c == '\n')
        c = getc(src);

    // accumulate token
    while (i < MAX_SYMBOL_LENGTH && !sym_end(c)) {
        tok[i] = (char)c;
        c = getc(src);
        i++;
    }

    // handle edge cases: paren immediately after whitespace
    if (c == ')') {
        if (tok[0] != '\0') { ungetc(c, src); tok[i] = '\0'; }
        else { tok[0] = c; tok[1] = '\0'; }
    } else if (c == '(' || c == '\'') {
        tok[0] = c; tok[1] = '\0';
    } else {
        tok[i] = '\0';
    }

    // EOF signal
    if (i == 0 && c == EOF) tok[0] = '\0';
    return tok;
}
```

**Key design**: `ungetc` pushes back the `)` when it follows a token (not whitespace). This handles `(a))` correctly — the first `)` closes the list, second `)` is seen by the caller.

**Limitation**: Tokens capped at 32 characters. Symbols or numbers longer than this are silently truncated.

## Tutorial Style: strtok Tokenizer

Uses `strtok` with parentheses and whitespace as delimiters:

```c
typedef struct {
    char **tokens;
    int count;
} TokenList;

TokenList tokenize(const char *input) {
    TokenList result = {NULL, 0};
    char *copy = strdup(input);
    char *token = strtok(copy, " \t\n()");

    while (token) {
        result.tokens = realloc(result.tokens,
            sizeof(char *) * (result.count + 1));
        result.tokens[result.count++] = strdup(token);
        token = strtok(NULL, " \t\n()");
    }
    free(copy);
    return result;
}
```

**Difference**: strtok consumes `(` and `)` as delimiters rather than tokens. The parser must track nesting via position index, not by seeing paren tokens. This simplifies the tokenizer but shifts complexity to the parser.

## Recursive Descent Parser

Both approaches use recursive descent, matching the recursive structure of S-expressions:

```c
// Entry point — dispatch on first token
node *parse_exp(FILE *src) {
    char *tok = next_token(src);
    if (tok[0] == '(')   return parse_list(src);
    if (tok[0] == '\'')  return parse_quote(src);
    if (tok[0] == '\0')  return NULL;
    return parse_atom(tok);
}

// Parse a parenthesized list
node *parse_list(FILE *src) {
    char *tok = next_token(src);
    list *tree = new_list();

    while (tok[0] != '\0' && tok[0] != ')') {
        if (tok[0] == '\'') {
            // inline quote: '(a b) → (quote (a b))
            node *q = new_node(true, strdup("quote"));
            node *expr = parse_exp(src);
            list *both = new_list();
            add(both, q);
            add(both, expr);
            add(tree, new_node(false, both));
        } else if (tok[0] == '(') {
            add(tree, parse_list(src));  // recursive
        } else {
            add(tree, new_node(true, tok));  // atom
        }
        tok = next_token(src);
    }

    if (tok[0] == '\0') {
        perror("syntax error: mismatched parentheses\n");
        return new_node(false, new_list());
    }

    return new_node(false, tree);
}
```

**Tutorial style parser** processes tokens by position index rather than FILE*:

```c
Node *parse_tokens(char **tokens, int *pos, int count) {
    if (*pos >= count) return NULL;

    char *current = tokens[*pos];
    (*pos)++;

    if (isdigit(current[0])) {
        Node *node = malloc(sizeof(Node));
        node->type = NODE_NUMBER;
        node->number = atoi(current);
        return node;
    } else if (strcmp(current, "(") == 0) {
        Node *node = malloc(sizeof(Node));
        node->type = NODE_LIST;
        node->list = NULL;
        node->list_size = 0;

        while (*pos < count && strcmp(tokens[*pos], ")") != 0) {
            node->list = realloc(node->list,
                sizeof(Node *) * (node->list_size + 1));
            node->list[node->list_size++] =
                parse_tokens(tokens, pos, count);
        }
        (*pos)++;  // skip ')'
        return node;
    } else {
        Node *node = malloc(sizeof(Node));
        node->type = NODE_SYMBOL;
        node->symbol = strdup(current);
        return node;
    }
}
```

## Quote Syntax Sugar

The `'` prefix is syntactic sugar for `(quote ...)`. The parser handles it by wrapping the next expression:

```c
node *parse_quote(FILE *src) {
    list *tree = new_list();
    add(tree, new_node(true, strdup("quote")));
    add(tree, parse_exp(src));
    return new_node(false, tree);
}
```

So `'x` becomes `(quote x)` and `'(a b c)` becomes `(quote (a b c))`. The evaluator then returns the quoted expression without evaluation.

In LIPS, inline quotes inside lists are also handled in `parse_list`:

```c
// In parse_list, when token is '
if (tok[0] == '\'') {
    node *quote = new_node(true, strdup("quote"));
    node *next = parse_exp(src);
    list *both = new_list();
    add(both, quote);
    add(both, next);
    add(tree, new_node(false, both));
}
```

## Error Handling

Both sources have minimal error handling:

- **Mismatched parentheses**: LIPS detects `tok[0] == '\0'` (EOF) when expecting `)`, calls `perror`, returns empty list
- **Token overflow**: Silent truncation at 32 characters
- **NULL nodes**: Eval checks for NULL and calls `perror`
- **Division by zero**: Returns NULL (becomes segfault downstream)

**Improvement pattern**: Add error return type. LIPS uses `enum Returntype { DISPLAYED = 0x1 }` cast to node* as a sentinel. Extend this for errors:

```c
enum Returntype { OK = 0, DISPLAYED = 0x1, ERROR = 0x2 };
// Check: if ((Returntype)node == ERROR) handle_error();
```

## Print/Writer Functions

Recursive printer walks the S-expression tree:

```c
void s_print(node *sexp) {
    if (sexp == NULL || (Returntype)sexp == DISPLAYED) return;
    else if (sexp->atom) {
        printf("%s ", sexp->data);
    } else {
        printf("(");
        list *ls = sexp->data;
        node *n = ls->start->next;
        while (n != ls->end) {
            s_print(n);
            n = n->next;
        }
        if (n == ls->start->next) printf(" ");  // empty list: "( )"
        printf("\b) ");  // backspace removes trailing space before ')'
    }
    fflush(stdout);
}
```

**Trailing space trick**: Each element prints with a trailing space. The `\b` backspace before `)` removes the last space, producing `(a b c)` not `(a b c )`.

Tutorial style uses similar recursion on AST nodes:

```c
void print_ast(Node *node) {
    if (node->type == NODE_NUMBER)
        printf("%d", node->number);
    else if (node->type == NODE_SYMBOL)
        printf("%s", node->symbol);
    else {
        printf("(");
        for (int i = 0; i < node->list_size; i++) {
            print_ast(node->list[i]);
            if (i < node->list_size - 1) printf(" ");
        }
        printf(")");
    }
}
```
