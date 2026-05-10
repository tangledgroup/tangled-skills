---
name: lisp-in-c-2026-05-03
description: Build a Lisp interpreter in C from scratch, covering S-expression parsing, manual memory management, hash-table environments, eval-apply cycle, and REPL. Two approaches: string-only atoms (LIPS) vs typed union AST nodes. Use when building interpreters in C, understanding evaluation with explicit memory management, or studying language implementation.
license: MIT
author: Tangled <noreply@tangledgroup.com>
version: "0.1.0"
tags:
  - lisp
  - c
  - interpreter
  - eval-apply
  - s-expression
  - linked-list
  - lexical-scoping
category: language-runtime
external_references:
  - https://github.com/hal-rock/lips
  - https://en.ittrip.xyz/c-language/minimal-lisp-in-c
---

# Lisp in C — Minimal Interpreter Guide

## Overview

Build a complete Scheme-like Lisp interpreter in C from scratch. The interpreter supports arithmetic, comparison, variables, user-defined functions with lexical scoping, conditionals, list operations, and a REPL. Two implementation approaches are covered:

- **LIPS style** (hal-rock/lips): All values stored as strings, S-expressions as linked lists with sentinel nodes, custom hash table for environments. Minimalist, ~300 lines of core logic across 9 source files.
- **Tutorial style** (ittrip.xyz): Typed union AST nodes with enum variants, strtok-based tokenizer, linked-list environment. More type-safe at the C level, closer to compiler textbook patterns.

Both approaches implement the same eval-apply cycle — the universal mechanism powering every Lisp implementation — but differ in memory representation, error handling, and data structure choices. The C-specific concerns (malloc/free discipline, pointer arithmetic, sentinel nodes, manual hash table) make this distinct from building interpreters in garbage-collected languages.

## When to Use

- Building a Lisp interpreter from scratch in C
- Understanding how language evaluation works at the systems level with explicit memory management
- Learning pointer-based data structures for language implementation (linked lists, hash tables, environment chains)
- Studying the eval-apply cycle without garbage collection abstractions
- Comparing two C representation strategies: string-only atoms vs typed union AST nodes
- Implementing lexical scoping via chained environments in C

## Core Concepts

**S-expressions**: Lisp's unified syntax for code and data. Atoms (symbols, numbers) and lists (parenthesized sequences) form a recursive structure. In C, represent as either linked lists of nodes or tree-structured AST nodes with tagged unions.

**The eval-apply cycle**: The universal evaluation loop. `eval` takes an expression and environment, returns a value. For list expressions, `eval` evaluates the operator, then applies it to evaluated arguments. User-defined functions create a new environment frame binding parameters to arguments, then evaluate the body in that frame.

**Environment chains**: Lexical scoping implemented as linked environments. Each function call creates a new frame pointing to its enclosing environment. Symbol lookup walks the chain outward until found or global scope is reached.

**Homoiconicity**: Code and data share the same representation (S-expressions). This enables `quote` to return unevaluated code as data, and user-defined functions to be stored as quoted lists of parameters and body expressions.

**Two value representations in C**:

- **String-only atoms** (LIPS): Everything is a `char*`. Numbers are digit strings, symbols are identifier strings. Simpler memory model but requires parsing on every arithmetic operation.
- **Typed union nodes** (tutorial): `enum NodeType` + `union { int number; char *symbol; Node **list; }`. Type-safe at compile time, no repeated string-to-number conversion, but more complex struct layout.

## Quick Start

Minimal working interpreter combining both approaches — typed AST with recursive eval:

```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h>

typedef enum { NODE_NUMBER, NODE_SYMBOL, NODE_LIST } NodeType;

typedef struct Node {
    NodeType type;
    union {
        int number;
        char *symbol;
        struct Node **list;
    };
    int list_size;
} Node;

// Environment: linked list of symbol -> value bindings
typedef struct Env {
    char *symbol;
    int value;
    struct Env *next;
} Env;

int eval(Node *node, Env *env);  // forward declaration

Env *add_to_env(Env *env, char *sym, int val) {
    Env *e = malloc(sizeof(Env));
    e->symbol = strdup(sym);
    e->value = val;
    e->next = env;
    return e;
}

int eval(Node *node, Env *env) {
    if (node->type == NODE_NUMBER) return node->number;

    if (node->type == NODE_SYMBOL) {
        while (env) {
            if (strcmp(env->symbol, node->symbol) == 0) return env->value;
            env = env->next;
        }
        fprintf(stderr, "Undefined symbol: %s\n", node->symbol);
        exit(1);
    }

    // NODE_LIST — eval first element as operator
    if (strcmp(node->list[0]->symbol, "+") == 0) {
        int sum = 0;
        for (int i = 1; i < node->list_size; i++)
            sum += eval(node->list[i], env);
        return sum;
    }

    if (strcmp(node->list[0]->symbol, "def") == 0) {
        // (def x expr) — define a variable
        char *sym = node->list[1]->symbol;
        int val = eval(node->list[2], env);
        // In real impl, update global env. Here just return value.
        return val;
    }

    fprintf(stderr, "Unknown operator\n");
    exit(1);
}

int main(void) {
    // Evaluate (+ 1 2 3) → 6
    Node *one = malloc(sizeof(Node));
    one->type = NODE_NUMBER; one->number = 1;

    Node *two = malloc(sizeof(Node));
    two->type = NODE_NUMBER; two->number = 2;

    Node *three = malloc(sizeof(Node));
    three->type = NODE_NUMBER; three->number = 3;

    Node *plus_sym = malloc(sizeof(Node));
    plus_sym->type = NODE_SYMBOL;
    plus_sym->symbol = strdup("+");

    Node *expr = malloc(sizeof(Node));
    expr->type = NODE_LIST;
    expr->list = malloc(4 * sizeof(Node *));
    expr->list[0] = plus_sym;
    expr->list[1] = one;
    expr->list[2] = two;
    expr->list[3] = three;
    expr->list_size = 4;

    printf("Result: %d\n", eval(expr, NULL));  // prints 6
    return 0;
}
```

Compile and run:

```bash
gcc -o lisp_quick lisp_quick.c -lm
./lisp_quick
```

## Advanced Topics

**Data Structures**: S-expression representations in C, linked lists vs AST nodes, hash table environments, memory management patterns → [Data Structures](reference/01-data-structures.md)

**Parser and Reader**: Tokenization strategies, recursive descent parsing, quote syntax sugar, print/writer functions → [Parser and Reader](reference/02-parser-and-reader.md)

**Evaluator and Environment**: The eval-apply cycle in C, special forms, user-defined function calls, lexical scoping via environment chains → [Evaluator and Environment](reference/03-evaluator-and-environment.md)

**Builtins and Extensions**: Arithmetic/list/comparison builtins, REPL wiring, error handling, garbage collection strategies, memory discipline → [Builtins and Extensions](reference/04-builtins-and-extensions.md)
