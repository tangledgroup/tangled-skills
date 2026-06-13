# Advanced Patterns

## Subagent Delegation

### The Context Window Scheduler Pattern

Ralph's primary context window should operate as a **scheduler**, delegating expensive work to subagents rather than allocating everything to the main context. This extends effective context beyond the physical limit.

Geoffrey Huntley's approach:

```markdown
Your task is to implement missing stdlib and compiler functionality using parallel subagents.
You may use up to 500 parallel subagents for all operations but only 1 subagent for build/tests of rust.
```

### Why Subagents?

Each tool call and its result allocates space in the context window. If you run a full test suite in the main context, the output fills thousands of tokens — tokens that could be used for reasoning about the next task.

By delegating to subagents:
- The main context stays lean (scheduler role)
- Subagents handle expensive operations (searching, testing, summarizing)
- Only the subagent's summary returns to the main context

### Controlling Parallelism

Uncontrolled parallelism causes backpressure problems. If hundreds of subagents all try to run the build simultaneously, they contend for resources and produce garbled output.

**Rule**: Limit parallelism for resource-intensive operations:

```markdown
You may use up to 500 parallel subagents for all operations but only 1 subagent for build/tests of rust.
```

This allows parallel file searching and writing (independent operations) while serializing builds and tests (resource-intensive, order-dependent).

### Subagent Use Cases

- **Codebase searching**: Multiple subagents search different directories simultaneously
- **Test execution**: Single subagent runs the full test suite, returns summary
- **Documentation generation**: Parallel subagents document different modules
- **Spec comparison**: Subagents compare source code against specifications

## Context Window Management

### The Real Context Window

Advertised context windows are larger than effective context windows:

- Claude 3.7: Advertised 200k, effective ~147k-152k (quality clips beyond this)
- Other models vary but follow similar patterns

The "clipping" point is where output quality degrades. Past this point, the model may miss instructions, produce incomplete code, or lose track of context.

### Minimizing Context Allocation

Every loop burns the same allocations:

1. Prompt template (fixed cost per iteration)
2. PRD / task list (scales with number of stories)
3. Progress log (grows over time)
4. Specifications (if included in prompt)

Strategies to minimize allocation:

- Keep the prompt template concise
- Limit prd.json to one feature's stories at a time
- Use Codebase Patterns section for condensed progress summary
- Reference external files (@specs/*, @fix_plan.md) rather than inlining them

### The Wasteful But Necessary Tradeoff

Ralph burns context every loop — specifications and prompt text are re-read each iteration. This is wasteful but necessary because each iteration is a fresh process with no internal memory.

The tradeoff: waste some context on repeated allocation, but gain focused, clean iterations without accumulated conversation history.

## Planning Mode vs. Building Mode

For complex projects, separate planning from building:

### Planning Mode

A dedicated Ralph loop that studies the codebase and generates or updates a task list:

```markdown
study specs/* to learn about the compiler specifications and fix_plan.md to understand plan so far.

First task is to study existing source code and compare it against the compiler specifications.
From that create/update a fix_plan.md which is a bullet point list sorted in priority of items yet to be implemented.

Consider searching for TODO, minimal implementations and placeholders.
```

### Building Mode

The standard Ralph loop that implements tasks from the plan:

```markdown
Follow the fix_plan.md and choose the most important thing.
After implementing functionality, run tests for that unit of code.
```

### When to Switch Modes

- Start with planning mode to generate the initial task list
- Switch to building mode for implementation
- Return to planning mode when:
  - The task list is stale or incorrect
  - Ralph goes off track
  - New specifications are added
  - Major architectural decisions need reconsideration

Geoffrey's approach: "I throw out the TODO list often." When the plan becomes unreliable, run a planning loop to regenerate it.

## Self-Improving Loops

Ralph can improve its own documentation and processes over time:

### Updating Build Documentation

```markdown
When you learn something new about how to run the compiler or examples, make sure you update AGENT.md using a subagent but keep it brief.
```

This creates a feedback loop where Ralph discovers the correct build command on iteration 3 and records it for iterations 4+.

### Bug Tracking

```markdown
For any bugs you notice, it's important to resolve them or document them in fix_plan.md to be resolved using a subagent even if it is unrelated to the current piece of work.
```

Ralph doesn't ignore discovered bugs — it either fixes them immediately or tracks them for future resolution.

### Plan Maintenance

```markdown
When @fix_plan.md becomes large, periodically clean out the items that are completed from the file using a subagent.
```

This prevents the plan file from growing unbounded and becoming unwieldy.

## The Todo List Pattern

### Generating the Todo List

For projects without a pre-defined PRD, Ralph can generate a task list by comparing existing code against specifications:

```markdown
First task is to study fix_plan.md (it may be incorrect) and use up to 500 subagents to study existing source code and compare it against the specifications.

From that create/update a fix_plan.md which is a bullet point list sorted in priority of items yet to be implemented.

Consider searching for TODO, minimal implementations and placeholders.
```

### Maintaining the Todo List

- Update as items are completed
- Search for TODO comments and placeholder implementations
- Keep sorted by priority
- Clean out completed items periodically

### When the Todo List Goes Bad

If Ralph generates an incorrect todo list (marks implemented features as incomplete, or misses unimplemented features):

1. Delete the todo list
2. Run a fresh planning loop
3. Verify the new list against the codebase

Geoffrey's approach during CURSED development: "I have deleted the TODO list multiple times."

## Loop-Back Patterns

### Self-Evaluation Loops

Instruct Ralph to evaluate its own output and loop back for correction:

```markdown
You may add extra logging if required to be able to debug the issues.
```

This enables Ralph to add diagnostic information, observe the results, and use that information in subsequent iterations.

### Compiler Self-Host Pattern

For projects like compilers, Ralph can compile its own output and evaluate the result:

```markdown
Compile the application and look at the LLVM IR representation to verify correctness.
```

This creates a tight feedback loop where Ralph generates code, compiles it, examines the output, and iterates.

## Multi-Language Coordination

When building projects that span multiple languages (e.g., a Rust compiler generating a custom language), Ralph needs coordination:

```markdown
The standard library should be authored in cursed itself and tests authored.
If you find rust implementation then delete it/migrate to implementation in the cursed language.
```

This ensures Ralph migrates bootstrap code from the host language to the target language as the project matures.

## Handling Non-Determinism

### The Ripgrep Problem

Code-based search (ripgrep) is non-deterministic — it may return different results on different runs, or truncate results. A common failure scenario:

1. Ralph searches for a function implementation
2. Ripgrep returns partial or no results
3. Ralph incorrectly concludes the function doesn't exist
4. Ralph creates a duplicate implementation

**Solution**: Add explicit instructions:

```markdown
Before making changes search codebase (don't assume not implemented) using subagents. Think hard.
```

Use multiple subagents to search different parts of the codebase, reducing the chance of missing existing implementations.

### Spec Inconsistency Detection

```markdown
If you find inconsistencies in the specs, use the oracle and then update the specs.
Specifically around types and lexical tokens.
```

Ralph can detect and resolve specification inconsistencies, preventing cascading errors from contradictory requirements.

## Scaling Ralph

### Multiple Ralph Loops

For very large projects, run multiple Ralph loops in parallel on different features:

1. Each Ralph operates on a separate git branch
2. Features are merged after completion
3. Coordination happens at the integration level

### Iteration Budgets

Adjust max_iterations based on project size:

- Small feature (4-6 stories): 10-15 iterations
- Medium feature (8-12 stories): 20-30 iterations
- Large project (20+ stories): 50+ iterations, consider splitting into multiple Ralph runs

### Nightly Runs

The classic Ralph use case: start a run before bed, wake up to completed features.

```bash
# Start Ralph with enough iterations for overnight work
./scripts/ralph/ralph.sh --tool claude 50
```

With iterations taking 2-5 minutes each, 50 iterations covers approximately 2-4 hours of autonomous work.

## Advanced Prompt Techniques from CURSED

Geoffrey's production prompt for building a compiler demonstrates advanced patterns:

### Numbered Priority System with Emphasis

```markdown
9999999999999999999999999999. DO NOT IMPLEMENT PLACEHOLDER OR SIMPLE IMPLEMENTATIONS.
WE WANT FULL IMPLEMENTATIONS. DO IT OR I WILL YELL AT YOU
```

The increasing number of 9s creates visual emphasis that the model attends to. This is a practical technique for ensuring critical instructions are not overlooked.

### Multi-Task Coordination

```markdown
Your task is to implement missing stdlib (see @specs/stdlib/*) and compiler functionality
and produce a compiled application in the cursed language via LLVM for that functionality
using parallel subagents. Follow the fix_plan.md and choose the most important 10 things.
```

This instructs Ralph to work on multiple related tasks within a single iteration, but only after the project has proven stable with single-task iterations.

### Cross-Language Migration

```markdown
IMPORTANT: The standard library in src/stdlib should be built in cursed itself, not rust.
If you find stdlib authored in rust then it must be noted that it needs to be migrated.
```

This ensures Ralph progressively migrates bootstrap code to the target language, achieving self-hosting.

## When Advanced Patterns Are Appropriate

Start simple. Use advanced patterns only when:

1. The basic Ralph loop has proven reliable for your project
2. You have observed specific failure modes that require these patterns
3. The project complexity justifies the additional prompt overhead

Geoffrey's CURSED prompt evolved over months of observation. Don't start with it — start with the default and tune from there.
