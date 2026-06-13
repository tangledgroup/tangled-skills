# SDD Methodology

## The Power Inversion

For decades, code has been king. Specifications served code — they were the scaffolding we built and then discarded once the "real work" of coding began. We wrote PRDs to guide development, created design docs to inform implementation, drew diagrams to visualize architecture. But these were always subordinate to the code itself. Code was truth. Everything else was, at best, good intentions.

Spec-Driven Development (SDD) inverts this power structure. Specifications don't serve code — code serves specifications. The PRD isn't a guide for implementation; it's the source that generates implementation. Technical plans aren't documents that inform coding; they're precise definitions that produce code. This eliminates the gap between intent and implementation by making specifications executable.

When specifications and implementation plans generate code, there is no gap — only transformation.

## Why SDD Matters Now

Three trends make SDD not just possible but necessary:

**AI capabilities have reached a threshold** where natural language specifications can reliably generate working code. This isn't about replacing developers — it's about amplifying their effectiveness by automating the mechanical translation from specification to implementation. It can amplify exploration and creativity, support "start-over" easily, and support addition, subtraction, and critical thinking.

**Software complexity continues to grow exponentially.** Modern systems integrate dozens of services, frameworks, and dependencies. Keeping all these pieces aligned with original intent through manual processes becomes increasingly difficult. SDD provides systematic alignment through specification-driven generation.

**The pace of change accelerates.** Requirements change far more rapidly today than ever before. Pivoting is no longer exceptional — it's expected. Traditional development treats changes as disruptions. SDD transforms requirement changes from obstacles into normal workflow. When specifications drive implementation, pivots become systematic regenerations rather than manual rewrites.

## Core Principles

**Specifications as the Lingua Franca**: The specification becomes the primary artifact. Code becomes its expression in a particular language and framework. Maintaining software means evolving specifications.

**Executable Specifications**: Specifications must be precise, complete, and unambiguous enough to generate working systems. This eliminates the gap between intent and implementation.

**Continuous Refinement**: Consistency validation happens continuously, not as a one-time gate. AI analyzes specifications for ambiguity, contradictions, and gaps as an ongoing process.

**Research-Driven Context**: Research agents gather critical context throughout the specification process, investigating technical options, performance implications, and organizational constraints.

**Bidirectional Feedback**: Production reality informs specification evolution. Metrics, incidents, and operational learnings become inputs for specification refinement.

**Branching for Exploration**: Generate multiple implementation approaches from the same specification to explore different optimization targets — performance, maintainability, user experience, cost.

## Development Phases

**0-to-1 Development ("Greenfield")**: Start with high-level requirements, generate specifications, plan implementation steps, build production-ready applications.

**Creative Exploration**: Explore diverse solutions, support multiple technology stacks and architectures, experiment with UX patterns.

**Iterative Enhancement ("Brownfield")**: Add features iteratively, modernize legacy systems, adapt processes.

## The Workflow In Practice

The workflow begins with an idea — often vague and incomplete. Through iterative dialogue with AI, this idea becomes a comprehensive PRD. The AI asks clarifying questions, identifies edge cases, and helps define precise acceptance criteria.

From the PRD, AI generates implementation plans that map requirements to technical decisions. Every technology choice has documented rationale. Every architectural decision traces back to specific requirements.

Code generation begins as soon as specifications and their implementation plans are stable enough, but they do not have to be "complete." Early generations might be exploratory — testing whether the specification makes sense in practice. Domain concepts become data models. User stories become API endpoints. Acceptance scenarios become tests.

The feedback loop extends beyond initial development. Production metrics and incidents don't just trigger hotfixes — they update specifications for the next regeneration. Performance bottlenecks become new non-functional requirements. Security vulnerabilities become constraints that affect all future generations.

## Constitution as Governance

The constitution is the foundational governance document for a Spec Kit project. It lives in `.specify/memory/constitution.md` and defines:

- Architectural principles (library-first, CLI-first)
- Development practices (test-first, simplicity gates)
- Anti-patterns to avoid (anti-abstraction rules)
- Integration and testing standards

The constitution is created via `/speckit.constitution` and guides all subsequent specification, planning, and implementation phases. It ensures consistent decision-making across the entire development lifecycle.
