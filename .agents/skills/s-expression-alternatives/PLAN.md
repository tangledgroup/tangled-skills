# ☑ Plan: s-expression-alternatives skill

**Depends On:** NONE
**Created:** 2026-05-13T00:00:00Z
**Updated:** 2026-05-13T00:00:00Z
**Current Phase:** ☑ Phase 3
**Current Task:** ☑ Task 3.3

## ☑ Phase 1 Research and Content Analysis

- ☑ Task 1.1 Analyze Sweet-expressions (David Wheeler, readable.sourceforge.net)
  - Key concepts: curly-infix `{a op b}`, neoteric `f(...)`, sweet indentation-based parens
  - 3-layer approach: curly-infix → modern/neo-expressions → sweet-expressions
  - Preserves homoiconicity and generality via abbreviations on any s-expression
  - Compatible with any Lisp dialect (Common Lisp, Scheme, Emacs Lisp, ACL2, etc.)

- ☑ Task 1.2 Analyze I-expressions (SRFI-49, Felix Springer implementation)
  - Key concepts: indentation-based grouping replaces parentheses
  - INDENT/DEDENT tokens derived from whitespace comparison
  - Mixes freely with s-expressions for readability
  - `group` keyword for lists whose first element is also a list
  - Felix Springer's Haskell implementation (haskeme) translates I→S expressions

- ☑ Task 1.3 Analyze O-expressions (Olivier Breuleux, breuleux.net)
  - Key concepts: operator-based syntax with Apply/Op/List/Seq/Group AST nodes
  - Left-associative juxtaposition as currying, `[a, b]` for lists, `(...)` grouping
  - Aggregative operators (`@if_@then_@else`) for extensibility without precedence
  - Design principles: context invariance, ubiquity, genericity, AST simplicity

- ☑ Task 1.4 Analyze Liso (Olivier Breuleux, GitHub breuleux/liso)
  - Racket implementation of o-expressions as alternative Lisp syntax
  - Predetermined operator priority table, supports macros
  - Key rules: Operator, Apply, List, Apply+List, Group, Arrow, Control, Sexp passthrough
  - Aliases: `@define`, `@lambda`, `@set!`, `@quote`, operators like `**`, `::`, `++`

## ☑ Phase 2 Write Reference Files

- ☑ Task 2.1 Write `reference/01-sweet-expressions.md` (depends on: Task 1.1)
  - Cover curly-infix, neoteric-expressions, sweet-expressions layers
  - Include code examples showing s-expression → sweet-expression translations
  - Explain indentation rules and compatibility guarantees

- ☑ Task 2.2 Write `reference/02-i-expressions.md` (depends on: Task 1.2)
  - Cover SRFI-49 specification, INDENT/DEDENT mechanics
  - Include Felix Springer's Haskell implementation approach
  - Show mixed I/S expression examples and `group` keyword usage

- ☑ Task 2.3 Write `reference/03-o-expressions.md` (depends on: Task 1.3)
  - Cover o-expression AST design (Apply, Op, List, Seq, Group nodes)
  - Explain design principles: context invariance, ubiquity, genericity
  - Include aggregative operators pattern (`@word` as operator tokens)
  - Show iteration examples from the blog post

- ☑ Task 2.4 Write `reference/04-liso.md` (depends on: Task 1.4)
  - Cover Liso's Racket implementation and usage (`#lang reader`)
  - Explain operator priority table and syntax rules (Operator, Apply, List, Group, Arrow, Control)
  - Include aliases (`@define`, `@lambda`, `@set!`, etc.)
  - Show code examples with s-expression equivalents

## ☑ Phase 3 Write SKILL.md and Validate

- ☑ Task 3.1 Write `SKILL.md` (depends on: Task 2.1 , Task 2.2 , Task 2.3 , Task 2.4)
  - YAML header with proper metadata
  - Overview section comparing all three approaches at high level
  - When to Use section with specific scenarios
  - Core Concepts covering shared motivations (homoiconicity, readability, extensibility)
  - Advanced Topics linking to reference files

- ☑ Task 3.2 Validate skill structure (depends on: Task 3.1)
  - Run `validate-skill.sh` on the skill directory
  - Check YAML header, section presence, file naming
  - Verify no anti-patterns (backslash paths, over-explanation, multiple options)

- ☑ Task 3.3 Regenerate README.md skills table (depends on: Task 3.2)
  - Run `gen-skills-table.sh` to update the public index
