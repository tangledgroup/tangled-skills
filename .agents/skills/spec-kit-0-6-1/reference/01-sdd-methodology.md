# SDD Methodology

## The Power Inversion

For decades, code has been king. Specifications served code — scaffolding built and discarded once the "real work" of coding began. Spec-Driven Development inverts this: specifications don't serve code, code serves specifications. The PRD isn't a guide for implementation; it's the source that generates implementation. Technical plans aren't documents that inform coding; they're precise definitions that produce code.

This transformation is now possible because AI can understand and implement complex specifications. But raw AI generation without structure produces chaos. SDD provides that structure through specifications and implementation plans that are precise, complete, and unambiguous enough to generate working systems.

In this new world:
- **Maintaining software** means evolving specifications
- **Debugging** means fixing specifications that generate incorrect code
- **Refactoring** means restructuring specifications for clarity
- **New features** mean revisiting specifications and creating new implementation plans

## Core Principles

**Specifications as the Lingua Franca**: The specification becomes the primary artifact. Code becomes its expression in a particular language and framework.

**Executable Specifications**: Specifications must be precise, complete, and unambiguous enough to generate working systems. This eliminates the gap between intent and implementation.

**Continuous Refinement**: Consistency validation happens continuously, not as a one-time gate. AI analyzes specifications for ambiguity, contradictions, and gaps as an ongoing process.

**Research-Driven Context**: Research agents gather critical context throughout the specification process, investigating technical options, performance implications, and organizational constraints.

**Bidirectional Feedback**: Production reality informs specification evolution. Metrics, incidents, and operational learnings become inputs for specification refinement.

**Branching for Exploration**: Generate multiple implementation approaches from the same specification to explore different optimization targets — performance, maintainability, user experience, cost.

## Development Phases

### 0-to-1 Development (Greenfield)

Start with high-level requirements, generate specifications, plan implementation steps, and build production-ready applications from scratch.

### Creative Exploration

Explore diverse solutions in parallel. Support multiple technology stacks and architectures. Experiment with UX patterns.

### Iterative Enhancement (Brownfield)

Add features iteratively. Modernize legacy systems. Adapt processes incrementally.

## Template-Driven Quality

The true power of SDD commands lies in how templates guide LLM behavior toward higher-quality specifications:

### Preventing Premature Implementation Details

The feature specification template explicitly instructs to focus on WHAT users need and WHY, avoiding HOW to implement (no tech stack, APIs, code structure). This keeps specifications stable even as implementation technologies change.

### Forcing Explicit Uncertainty Markers

Templates mandate `[NEEDS CLARIFICATION]` markers for ambiguities. Instead of guessing, the LLM must mark uncertainties — e.g., `[NEEDS CLARIFICATION: auth method not specified - email/password, SSO, OAuth?]`.

### Structured Thinking Through Checklists

Templates include comprehensive checklists that act as "unit tests" for the specification, forcing the LLM to self-review output systematically.

### Constitutional Compliance Through Gates

The implementation plan template enforces architectural principles through phase gates that prevent over-engineering. If a gate fails, the LLM must document why in the "Complexity Tracking" section.

### Hierarchical Detail Management

Templates enforce proper information architecture — the main plan stays high-level and readable, while detailed code samples and algorithms go into `implementation-details/` files.

### Test-First Thinking

The implementation template enforces file creation order: contracts → tests (contract → integration → e2e → unit) → source files. This ensures testability is considered before implementation.

## The Constitutional Foundation

At the heart of SDD lies a constitution — a set of immutable principles that govern how specifications become code. The constitution (`memory/constitution.md`) acts as the architectural DNA of the system.

### The Nine Articles of Development

**Article I: Library-First Principle** — Every feature must begin as a standalone library. This forces modular design from the start.

**Article II: CLI Interface Mandate** — Every library must expose functionality through a command-line interface. All CLI interfaces must accept text as input and produce text as output, supporting JSON format.

**Article III: Test-First Imperative** — Non-negotiable TDD. No implementation code before unit tests are written, validated, approved, and confirmed to fail (Red phase).

**Articles VII & VIII: Simplicity and Anti-Abstraction** — Maximum 3 projects for initial implementation. Use framework features directly rather than wrapping them.

**Article IX: Integration-First Testing** — Tests must use realistic environments. Prefer real databases over mocks, actual service instances over stubs. Contract tests mandatory before implementation.

### Constitutional Enforcement

The implementation plan template operationalizes articles through concrete checkpoints:

```markdown
### Phase -1: Pre-Implementation Gates

#### Simplicity Gate (Article VII)
- [ ] Using ≤3 projects?
- [ ] No future-proofing?

#### Anti-Abstraction Gate (Article VIII)
- [ ] Using framework directly?
- [ ] Single model representation?

#### Integration-First Gate (Article IX)
- [ ] Contracts defined?
- [ ] Contract tests written?
```

These gates act as compile-time checks for architectural principles. The LLM cannot proceed without either passing the gates or documenting justified exceptions.

### Constitutional Evolution

While principles are immutable, their application can evolve. Modifications require explicit documentation of rationale, review and approval by maintainers, and backwards compatibility assessment.

## Why SDD Matters Now

Three trends make SDD necessary:

1. **AI capabilities** have reached a threshold where natural language specifications can reliably generate working code — amplifying developer effectiveness by automating mechanical translation
2. **Software complexity** continues to grow exponentially — keeping pieces aligned with original intent through manual processes becomes increasingly difficult
3. **Pace of change accelerates** — pivoting is expected, not exceptional. SDD transforms requirement changes from obstacles into normal workflow
