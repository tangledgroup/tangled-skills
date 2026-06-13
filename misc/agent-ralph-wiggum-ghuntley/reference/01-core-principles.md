# Core Principles

## The Loop Is the Program

In Ralph, you do not write code. You program the loop. The prompt file (PROMPT.md) is your source code. The bash while-loop is your runtime environment. Every iteration of the loop feeds the same prompt to a fresh LLM context, which reads the current state of the repository and acts on it.

This reframes the engineer's role from writing implementations to programming behavior through context engineering. You are not directing individual tool calls — you are shaping the probability distribution of what the LLM does next by carefully constructing its context.

## Monolithic Architecture

Ralph is intentionally monolithic. It operates as a single process within a single repository, performing one task per loop iteration. This stands in direct contrast to multi-agent architectures:

- Multi-agent systems introduce non-determinism that compounds across independent agents
- Coordinating multiple non-deterministic processes creates complexity similar to microservices
- Ralph avoids this by keeping everything in one context window with one agent

The monolithic approach scales vertically rather than horizontally. The single context window is the constraint to manage, not a distributed coordination problem.

## One Task Per Loop

Each loop iteration should accomplish exactly one thing. This discipline serves multiple purposes:

- Keeps context window usage minimal (practical limit ~170k tokens)
- Makes failure modes easier to diagnose and tune
- Forces prioritization — the LLM decides what is most important next
- Prevents the agent from scattering effort across too many concerns

As a project matures, you may relax this constraint. But if things go off the rails, narrow back down to one item per loop immediately.

## Trust the LLM's Prioritization

A radical aspect of Ralph: you trust the LLM to decide what is most important to implement next. This is full hands-off development that tests the bounds of responsible engineering. LLMs are surprisingly good at reasoning about implementation priority and next steps when given clear specifications.

> "Frequent question: how do you plan? I don't. The models know what a compiler is better than I do. I just ask it."

## Deterministic Stack Allocation

Every loop iteration receives the same deterministic stack allocation. The items allocated to context every loop are:

- Your specifications (specs/\*)
- Your plan file (fix_plan.md or equivalent)
- The prompt instructions themselves

While this burns tokens every loop by re-allocating specifications rather than reusing them, it ensures that every iteration starts from the same authoritative reference. Inconsistency in what the LLM sees is a source of failure.

## Eventual Consistency

Ralph operates on eventual consistency, not immediate correctness. The codebase may be broken at any given moment. Ralph will take wrong directions. The operator's job is to believe that through enough iterations with proper tuning, the system converges toward working software.

This requires patience and a specific mindset:

- Do not blame the tools when Ralph does something bad
- Look inward — examine your prompt, your specifications, your signs
- Every failure is data for tuning
- The TODO list may need to be thrown out and regenerated multiple times

## Tuning Through Observation

Ralph improves through watching the stream and identifying patterns of bad behavior. The process is analogous to tuning a guitar:

1. Ralph is given instructions to construct a playground (initial implementation)
2. Ralph comes home bruised because it fell off the slide (failure observed)
3. You add a sign next to the slide: "SLIDE DOWN, DON'T JUMP" (prompt tuning)
4. Ralph becomes more likely to look and see the sign (behavior corrected)
5. Eventually all Ralph thinks about are the signs, and the output no longer feels defective

## The Pottery Wheel Mindset

Software in the Ralph paradigm is clay on a pottery wheel. If something isn't right, you throw it back on the wheel to address items that need resolving. This applies across multiple modes:

- **Forward mode**: Building autonomously from specifications
- **Reverse mode**: Clean-rooming existing systems
- **Verification mode**: Running system verification loops
- **Evolutionary mode**: Loops that evolve products and optimize automatically

## Watch the Loop

Personal development and learning come from watching the loop, not from writing code. When you observe a failure domain, put on your engineering hat and resolve the problem so it never happens again. This means:

- Adding prompt signs to prevent recurrence
- Updating specifications when they are ambiguous or contradictory
- Improving backpressure mechanisms to catch issues earlier
- Refining subagent delegation patterns

## Greenfield Only

Ralph is designed for bootstrapping greenfield projects. It is not intended for existing codebases with established architecture, legacy constraints, or complex dependencies. The technique expects to reach approximately 90% completion autonomously, with the remaining 10% finished manually by engineers.

> "There's no way in heck would I use Ralph in an existing code base."

## Engineers Are Still Required

Despite its autonomy, Ralph requires senior engineering expertise to guide it effectively. The operator must:

- Write clear, unambiguous specifications
- Design effective backpressure mechanisms
- Watch the loop and identify failure patterns
- Make judgment calls on recovery strategies
- Tune prompts based on observed behavior

Anyone claiming that engineers are no longer required is mistaken. However, the Ralph technique can displace a large majority of traditional SWE effort for greenfield projects.

## Ralph Has Three States

> "Ralph has three states. Under baked, baked, or baked with unspecified latent behaviours (which are sometimes quite nice!)"

Accept that Ralph's output will have gaps and quirks. The goal is not perfection in a single pass — it is convergence through iteration. Any problem created by AI can be resolved through a different series of prompts and more loops.
