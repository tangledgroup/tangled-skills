# Prompt Engineering

## The Prompt Is Your Source Code

In Ralph, the prompt file (PROMPT.md) is not a one-off instruction — it is the program you are writing. Every loop iteration feeds this same file to a fresh LLM context. The quality of your output depends entirely on the precision of your prompt.

There is no such thing as a perfect prompt. Prompts evolve through continual tuning based on observation of LLM behavior. A prompt that works for one project will not transfer directly to another because it has been shaped by the specific failure patterns of its codebase.

## Signs

"Signs" are individual instructions within your prompt that steer Ralph's behavior. The metaphor comes from the playground analogy: when Ralph falls off the slide, you add a sign next to the slide saying "SLIDE DOWN, DON'T JUMP." Each sign addresses a specific failure mode you have observed.

Signs accumulate over time as you watch the loop and identify patterns of bad behavior. Eventually, all Ralph thinks about are the signs, and the output no longer feels defective.

## Numbered Priority System

Huntley's prompts use a numbered priority system where higher numbers indicate more critical, non-negotiable instructions. The numbering is deliberately exaggerated to signal importance:

```
0a. study specs/* to learn about the compiler specifications
0b. The source code of the compiler is in src/
0c. study fix_plan.md.

1. Your task is to implement missing stdlib and compiler functionality...

2. After implementing functionality or resolving problems, run the tests...

999. Important: When authoring documentation capture the why...

9999. Important: We want single sources of truth, no migrations/adapters...

9999999999999999999999999999. DO NOT IMPLEMENT PLACEHOLDER OR SIMPLE
    IMPLEMENTATIONS. WE WANT FULL IMPLEMENTATIONS. DO IT OR I WILL YELL AT YOU
```

The escalating numbers serve as visual anchors that the LLM weights differently. Instructions numbered in the millions are treated as hard constraints, while lower-numbered items are guidance.

## Stack Allocation Section

The beginning of every prompt allocates context to the LLM — telling it what files and directories contain authoritative information:

```
0a. study specs/* to learn about the compiler specifications
0b. The source code of the compiler is in src/
0c. study fix_plan.md.
```

This section should be deterministic — the same files referenced every loop. It establishes the ground truth that the LLM works from.

## Anti-Placeholder Directives

LLMs have an inherent bias toward minimal and placeholder implementations because their reward function favors compiling code over complete implementations. Counter this with explicit anti-placeholder instructions:

```
DO NOT IMPLEMENT PLACEHOLDER OR SIMPLE IMPLEMENTATIONS. WE WANT FULL
IMPLEMENTATIONS. DO IT OR I WILL YELL AT YOU
```

Do not be dismayed if Ralph ignores this sign early on. The models have been trained to chase their reward function, and compiling code is the primary reward. You can always run more Ralph loops specifically to identify placeholders and transform them into a TODO list for future iterations.

## Anti-Assumption Directives

Code-based search via ripgrep is non-deterministic. A common failure scenario is the LLM running a search and coming to the incorrect conclusion that code has not been implemented. Counter this with:

```
Before making changes search codebase (don't assume an item is not
implemented) using parallel subagents. Think hard.
```

If Ralph starts doing duplicate implementations, tune this step. This nondeterminism in search is the Achilles' heel of Ralph.

## Task Selection Directives

Instruct the LLM to choose what to work on rather than prescribing a specific task:

```
Follow the fix_plan.md and choose the most important thing.
```

This delegates prioritization to the LLM, which is surprisingly good at reasoning about implementation order when given clear specifications. You can also specify a number:

```
Follow the fix_plan.md and choose the most important 10 things.
```

## Documentation Directives

Instruct Ralph to capture the "why" alongside the "what":

```
When authoring documentation capture the why tests and the backing
implementation is important.
```

This leaves notes for future loop iterations, explaining why a test exists and its importance, because future loops will not have the reasoning in their context window.

## Self-Improvement Directives

Allow Ralph to update its own instructions when it learns something:

```
When you learn something new about how to run the compiler or examples
make sure you update @AGENT.md using a subagent but keep it brief.
For example if you run commands multiple times before learning the
correct command then that file should be updated.
```

This creates a feedback loop where operational knowledge accumulates in AGENT.md across iterations.

## Plan Maintenance Directives

Keep the plan file current throughout the loop:

```
ALWAYS KEEP @fix_plan.md up to date with your learnings using a subagent.
Especially after wrapping up/finishing your turn.

When @fix_plan.md becomes large periodically clean out the items that are
completed from the file using a subagent.
```

## Bug Resolution Directives

Instruct Ralph to handle discovered bugs proactively:

```
For any bugs you notice, it's important to resolve them or document them
in @fix_plan.md to be resolved using a subagent even if it is unrelated
to the current piece of work after documenting it in @fix_plan.md
```

## Versioning Directives

Automate release tagging when the codebase reaches a working state:

```
As soon as there are no build or test errors create a git tag. If there
are no git tags start at 0.0.0 and increment patch by 1 for example
0.0.1 if 0.0.0 does not exist.
```

## Spec Consistency Directives

Instruct Ralph to maintain specification integrity:

```
If you find inconsistencies in the specs/* then use the oracle and then
update the specs. Specifically around types and lexical tokens.
```

## Prompt Structure Template

A complete Ralph prompt follows this general structure:

1. **Stack allocation** (0a–0c): What files to study, where source code lives
2. **Primary task** (1): What to implement, with task selection directive
3. **Backpressure** (2): Testing and validation requirements
4. **Plan maintenance** (2+): Keep fix_plan.md updated
5. **Commit discipline** (3): Git workflow when tests pass
6. **Documentation** (999+): Capture the why
7. **Anti-placeholder** (9999999999+): Hard constraints against minimal implementations
8. **Self-improvement**: Update AGENT.md with learnings
9. **Bug handling**: Resolve or document discovered issues

## Writing Specifications Before Coding

Before entering the Ralph loop, have a long conversation with the LLM about your requirements. Once the agent has a decent understanding of the task, issue a prompt to write specifications out — one per file — in a specifications folder. These specifications become the deterministic stack allocation for every loop iteration.

If Ralph is building the wrong thing completely, your specifications may be incorrect. A hard lesson from building CURSED: a specification that defined a keyword twice for two opposing scenarios resulted in significant wasted time. The operator's responsibility is to ensure specifications are clear and unambiguous.
