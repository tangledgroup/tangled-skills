# ☑ Plan: Create lambda-calculus Skill (v0.1.0)

**Depends On:** NONE
**Created:** 2026-05-12T00:00:00Z
**Updated:** 2026-05-12T00:00:00Z
**Current Phase:** ☑ Phase 6
**Current Task:** ☑ Task 6.4

## ☑ Phase 1 Planning

- ☑ Task 1.1 Analyze source material and define skill scope
  - Review all 5 fetched Wikipedia pages (Lambda calculus, Lambda calculus definition, Typed lambda calculus, Simply typed lambda calculus, Currying)
  - Identify core concepts for SKILL.md vs. advanced topics for reference/ files
  - Define the split: what stays inline vs. what goes to reference files

- ☑ Task 1.2 Design output structure (complex skill with reference/)
  - Determine SKILL.md sections: Overview, When to Use, Core Concepts, Quick Syntax Reference, Usage Examples, Advanced Topics
  - Plan reference file breakdown:
    - `01-reduction-and-evaluation.md` — alpha/beta/eta reduction, substitution, evaluation strategies, normal forms, confluence, Church-Rosser
    - `02-church-encoding.md` — Church numerals (arithmetic), Church Booleans (logic/predicates), pairs, lists, recursion and fixed-point combinators
    - `03-typed-lambda-calculus.md` — typed lambda calculus overview, simply typed lambda calculus (syntax, typing rules, type safety, strong normalization), System F, dependent types, lambda cube, Curry-Howard isomorphism
    - `04-currying-and-application.md` — currying definition, uncurrying, contrast with partial application, role in functional programming, category theory perspective

## ☑ Phase 2 Analysis

- ☑ Task 2.1 Draft SKILL.md YAML header and metadata
  - name: lambda-calculus (no upstream version since this is a formal system, not a software release)
  - description: concise WHAT + WHEN with key terms (lambda calculus, lambda terms, reduction, currying, Church encoding, typed lambda calculus)
  - tags: 3-7 tags covering broad and specific
  - category: `language-runtime` or `library` — decide based on best fit

- ☑ Task 2.2 Draft SKILL.md core content (inline sections)
  - Overview: what lambda calculus is, its significance as a universal model of computation, history (Church, 1930s)
  - When to Use: specific scenarios (reasoning about functions, understanding functional programming foundations, type theory, proof assistants)
  - Core Concepts: three term forms (variable, abstraction, application), free vs. bound variables, notation conventions (left-associative application, right-extending abstractions), capture-avoiding substitution
  - Quick Syntax Reference: BNF grammar, common abbreviations, simple examples (identity, constant functions)
  - Usage Examples: beta-reduction walkthroughs, currying example, Church numeral example — using plain UTF-8 characters (λ, →, ≡) instead of LaTeX/MathML

## ☑ Phase 3 Implementation

- ☑ Task 3.1 Write SKILL.md
  - Compose the full file following skman templates and anti-pattern rules
  - Use simple math syntax: λx.M, M N, →β, α-equivalence, plain text arrows and symbols
  - Keep under 500 lines; link to reference files from Advanced Topics section
  - Ensure single recommended approach, no over-explaining basics

- ☑ Task 3.2 Write reference/01-reduction-and-evaluation.md (depends on: Task 3.1)
  - Alpha-conversion (renaming bound variables), rules and pitfalls
  - Capture-avoiding substitution formal definition with examples
  - Beta-reduction: redex, reduct, step-by-step examples
  - Eta-conversion: extensionality principle
  - Normal forms: beta-normal form, strongly/weakly normalizing terms
  - Confluence and Church-Rosser theorem
  - Reduction strategies: call-by-name, call-by-value, normal-order, applicative-order

- ☑ Task 3.3 Write reference/02-church-encoding.md (depends on: Task 3.1)
  - Church numerals: definition of 0, 1, 2, 3... and the "repeat n times" intuition
  - Arithmetic operations: SUCC, PLUS, MULT, POW, PRED — with definitions in plain lambda syntax
  - Church Booleans: TRUE, FALSE, AND, OR, NOT, IF-THEN-ELSE with reduction examples
  - Predicates: ISZERO, LEQ, equality testing
  - Pairs and lists: PAIR, FIRST, SECOND, NIL, NULL
  - Recursion and fixed-point combinators: Y-combinator, Omega term

- ☑ Task 3.4 Write reference/03-typed-lambda-calculus.md (depends on: Task 3.1)
  - Typed vs. untyped: trade-offs (expressiveness vs. provability)
  - Simply typed lambda calculus (STLC): base types, arrow type constructor, syntax with type annotations
  - Typing rules and contexts (typing judgments, derivation rules)
  - Strong normalization theorem for STLC (all reductions terminate)
  - Type inference: Hindley-Milner, principal types
  - Bidirectional type checking overview
  - Beyond simple types: System T, System F (polymorphism), dependent types, lambda cube, pure type systems
  - Curry-Howard isomorphism: types as propositions, terms as proofs

- ☑ Task 3.5 Write reference/04-currying-and-application.md (depends on: Task 3.1)
  - Currying definition: transforming multi-argument functions into chains of single-argument functions
  - Formal notation: curry and uncurry transformations with type signatures
  - Contrast with partial application (related but different)
  - Role in lambda calculus: why single-argument functions suffice, how currying enables this
  - Practical impact on functional programming languages (ML, Haskell)
  - Category theory perspective: exponential objects, cartesian closed categories (brief overview)

## ☑ Phase 4 Validation

- ☑ Task 4.1 Run structural validator on SKILL.md (depends on: Task 3.1)
  - `bash .agents/skills/skman/scripts/validate-skill.sh --strict lambda-calculus`
  - Fix any reported errors

- ☑ Task 4.2 LLM judgment review of all files (depends on: Task 4.1)
  - Check YAML header fields against skman rules
  - Verify no hallucinated content — all from fetched sources
  - Consistent terminology throughout (always "lambda term", not sometimes "expression")
  - No over-explaining basics, no multiple options where one suffices
  - Simple math syntax used consistently (UTF-8 λ, →, ≡, not LaTeX)
  - SKILL.md under 500 lines
  - Reference files properly linked from Advanced Topics section
  - No chained references

## ☑ Phase 5 Finalization

- ☑ Task 5.1 Create skill directory and move files (depends on: Task 4.2)
  - Create `.agents/skills/lambda-calculus/`
  - Place SKILL.md and `reference/01-*.md` through `reference/04-*.md`

- ☑ Task 5.2 Regenerate README.md skills table (depends on: Task 5.1)
  - `bash .agents/skills/skman/scripts/gen-skills-table.sh`

- ☑ Task 5.3 Final validation pass (depends on: Task 5.2)
  - Run validator one more time from final location
  - Confirm README.md table includes the new skill
  - Report completion with file tree

## ☑ Phase 6 Additional Source: Fixed-Point Combinators

- ☑ Task 6.1 Fetch and analyze fixed-point combinator source (https://en.wikipedia.org/wiki/Fixed-point_combinator)
  - Review content: Y combinator, Z combinator, Turing fixed-point combinator, strict vs lazy evaluation
  - Add URL to external_references in YAML header

- ☑ Task 6.2 Update SKILL.md: explain why we need fixed-point combinators
  - Add a Core Concepts subsection explaining the recursion problem in lambda calculus (no named functions, no self-reference)
  - Explain how fixed-point combinators solve this by enabling anonymous recursion
  - Keep it concise — detailed definitions go in reference file

- ☑ Task 6.3 Enhance reference/02-church-encoding.md with fixed-point combinator details
  - Expand the existing Recursion section with Y combinator, Z combinator (strict/call-by-value), Turing combinator
  - Explain call-by-name vs call-by-value behavior
  - Add factorial example walkthrough

- ☑ Task 6.4 Re-validate and regenerate README
  - Run structural validator
  - Regenerate skills table
