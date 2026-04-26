# Context Management

## Understanding the Context Stack

The context stack is everything sent to the LLM with each request. Because LLMs have no memory between requests, all history must be resent every time. With tool-using agents, this is not a single request but multiple back-and-forth exchanges, creating a large cumulative stack.

A typical interaction flow:

```
Request 1: System prompts + instructions + skills + user prompt
  → LLM decides to read files
Request 2: Same system prompts + instructions + skills + file contents
  → LLM writes code
Request 3: Same system prompts + instructions + skills + written code
  → LLM reads files to verify
Request 4: Same system prompts + instructions + skills + verification results
  → LLM makes corrections
Request 5: Same system prompts + instructions + skills + corrections
```

The system prompts, instructions, and skills are sent with every single request. In a simple five-turn exchange, they are transmitted five times. This is the primary driver of context consumption.

## Context Limit Issues

Different accounts and platforms have different context limits:

- **Personal licenses** often have higher or unlimited context windows
- **Enterprise/work accounts** may impose lower limits for cost control
- **Older models** have smaller context windows than newer ones

When context limits are hit, you may see errors like "No choices" — the model cannot generate a response because the input exceeds its maximum token budget. This can happen even with small codebases if the prompt stack is large and the interaction has many turns.

## Strategy 1: Minimize Prompt Content

The first and most obvious optimization is reducing the size of system prompts, instruction.md, and skill.md:

- **Be concise** — every word costs tokens
- **Avoid duplication** — don't repeat information across layers
- **Remove verbosity** — state rules directly, not as explanations
- **Prioritize critical rules** — put the most important constraints first

Example of concise vs verbose:

```markdown
# Verbose (wasteful)
When you are writing JavaScript code for Code Apps, please make sure that
you always use vanilla JavaScript and do not use React or TypeScript because
the Code Apps platform does not support those frameworks.

# Concise (efficient)
Vanilla JS only. No React, no TypeScript.
```

## Strategy 2: Send Only Relevant Data

### Dynamic Skill Loading

Do not send all skill files with every request. Instead:

1. Pass a list or description of available skills to the LLM
2. Let the LLM decide which skills are relevant to the current task
3. Load only the selected skills into the context

This approach is more effective than keyword-based filtering, which often misses relevant skills or loads unnecessary ones.

### Tight File Trees

Use file trees to help the LLM understand project structure without sending full file contents:

- File trees let the LLM know what files exist and how they relate
- The LLM can then request only the files it needs
- Control tree width — wider trees mean more text sent
- Keep trees focused on relevant directories

## Strategy 3: Manage Context History

### History Compaction

The standard approach to managing growing context history is compaction:

1. Ask the LLM to summarize the conversation history
2. Replace the full history with the summary
3. Continue the conversation with reduced context

**Trade-off:** Compaction works but can lose important context details. Use it judiciously.

### Task-Based Context Reset

An alternative approach is breaking work into discrete tasks:

1. Create a **decision log file** where the LLM stores a todo list and key decisions
2. The LLM breaks the project into individual tasks
3. Complete one task at a time
4. When a task is complete, update the decision log and **remove all tool calls and reasoning**, keeping only results
5. Start the next task with a fresh context containing just the decision log and relevant files

This approach preserves key decisions across tasks while avoiding context bloat from intermediate reasoning steps.

### Decision Log Example

```markdown
# Decision Log

## Completed Tasks
- [x] Setup project structure → Files created in /src
- [x] Implement auth flow → Uses tenant credentials via Power Platform CLI

## Key Decisions
- Using vanilla JS, not React (platform constraint)
- Connection names must match environment config exactly
- All event handlers use component.onInit() pattern

## Remaining Tasks
- [ ] Implement data binding layer
- [ ] Add deployment pipeline
```

## Trade-offs and Considerations

Context management involves balancing multiple factors:

- **Removing too much context** risks losing important information needed for correct behavior
- **Keeping too much context** risks hitting token limits
- **User context limits vary** — what works for personal accounts may fail on enterprise accounts
- **Newer models** continuously push input/output token boundaries, reducing the urgency of optimization
- **Task-based resets** add overhead but prevent runaway context growth

The right strategy depends on your specific use case, target audience, and the models your users will access. Test with the lowest common denominator context limits to ensure broad compatibility.
