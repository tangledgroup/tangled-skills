# Degrees of Freedom in Skill Instructions

## Contents
- What Degrees of Freedom Means
- High Freedom (Text-Based Instructions)
- Medium Freedom (Pseudocode or Parameterized Scripts)
- Low Freedom (Specific Scripts, Few Parameters)
- Decision Guide: Matching Specificity to Task Fragility
- Common Mistakes

## What Degrees of Freedom Means

Degrees of freedom refers to how much latitude you give the agent in choosing _how_ to accomplish a task. Match the level of specificity to the task's **fragility** (how easily it can go wrong) and **variability** (how many valid approaches exist).

**Analogy**: Think of the agent as a robot exploring a path:
- **Narrow bridge with cliffs on both sides**: Only one safe way forward. Provide specific guardrails and exact instructions (**low freedom**). Example: database migrations that must run in exact sequence.
- **Open field with no hazards**: Many paths lead to success. Give general direction and trust the agent to find the best route (**high freedom**). Example: code reviews where context determines the best approach.

## High Freedom (Text-Based Instructions)

Use when:
- Multiple approaches are valid
- Decisions depend on context
- Heuristics guide the approach

**Pattern**: Provide principles and guidelines, let the agent decide specifics.

```markdown
## Code Review Guidelines

When reviewing code:
- Check for security vulnerabilities (SQL injection, XSS, CSRF)
- Flag performance anti-patterns (N+1 queries, unbounded loops)
- Suggest improvements only when they add clear value
- Adapt strictness to the context: be lenient on prototypes, strict on production
```

**Why it works**: Code reviews vary widely — a review of a quick prototype differs from a security-critical module. Text instructions let the agent adapt to each context.

## Medium Freedom (Pseudocode or Parameterized Scripts)

Use when:
- A preferred pattern exists
- Some variation is acceptable
- Configuration affects behavior

**Pattern**: Provide a template with configurable parameters.

```markdown
## Generating API Documentation

Follow this structure for each endpoint:
1. List the HTTP method and path
2. Document request parameters (name, type, required, description)
3. Show a request/response example
4. List possible error codes

Adapt detail level based on audience:
- Internal APIs: include implementation notes
- Public APIs: focus on contract and examples
```

**Why it works**: There's a standard structure for API docs, but the content varies. The template ensures consistency while allowing adaptation.

## Low Freedom (Specific Scripts, Few Parameters)

Use when:
- Operations are fragile and error-prone
- Consistency is critical
- A specific sequence must be followed

**Pattern**: Provide exact commands or scripts with minimal room for interpretation.

```markdown
## Running Database Migrations

Run migrations in this exact order:
1. `python manage.py migrate --fake-initial`
2. `python manage.py collectstatic --noinput`
3. `python manage.py check --deploy`

Do not skip steps or change the order. Each step depends on the previous one completing successfully.
```

**Why it works**: Database migrations are fragile — running them out of order causes data corruption. Specific instructions prevent mistakes.

## Decision Guide: Matching Specificity to Task Fragility

Use this decision tree when writing skill instructions:

| Factor | Lean Toward High Freedom | Lean Toward Low Freedom |
|--------|--------------------------|-------------------------|
| **Number of valid approaches** | Many | One or two |
| **Cost of mistakes** | Low (easy to fix) | High (data loss, security breach) |
| **Context variability** | High (each task is unique) | Low (tasks are repetitive) |
| **Agent expertise needed** | Judgment and reasoning | Following a procedure |
| **User's tolerance for variation** | High (any good result works) | Low (must be identical each time) |

**Practical rule of thumb**:
- If the task could go wrong in more than 3 ways → **low freedom**
- If there's a preferred pattern but alternatives exist → **medium freedom**
- If the agent's judgment is the main value add → **high freedom**

## Common Mistakes

**Over-specifying creative tasks**: Giving step-by-step instructions for something that benefits from the agent's creativity (e.g., writing documentation, designing architecture). This constrains the agent unnecessarily and produces rigid output.

**Under-specifying fragile operations**: Giving vague instructions for something that must be exact (e.g., "run the build commands" instead of listing them). This leads to inconsistent results and errors.

**One-size-fits-all**: Using the same level of specificity across all sections of a skill. A good skill mixes freedom levels — high freedom for creative decisions, low freedom for procedural steps.

**Example of mixed freedom in one skill**:

```markdown
## Writing Tests (High Freedom)
Write tests that cover the main use cases and edge cases. Choose assertions
and test structure based on what best validates the behavior.

## Running the Test Suite (Low Freedom)
Execute tests with this exact command:
    pytest tests/ -v --tb=short
Do not modify the command flags.
```
