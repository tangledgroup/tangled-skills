# Context Engineering

How production agents build context, manage prompts, and avoid context window rot. **Context engineering is UX engineering** - the product decides what the model sees and when.

## The Core Problem

During pre-training, models learn common languages (Python, Rust, etc.). During context building, they learn your workspace conventions and schemas.

**Key insight**: From the agent's point of view, anything it can't access in-context while running effectively doesn't exist.

## The AGENTS.md Pattern

OpenAI learned this the hard way while building Codex.

### Failed Approach: One Big Manual

They tried the "one big AGENTS.md" approach and it failed in predictable ways:

- **Crowds out task and code**: Giant instruction file fills context window, leaving less room for actual work
- **Too much guidance becomes noise**: Models struggle with excessive instructions
- **Rots quickly**: As repository changes, the manual becomes outdated
- **Hard to verify mechanically**: Difficult to ensure accuracy across large documents

### Working Approach: Table of Contents

**Treat AGENTS.md as the table of contents, not the encyclopedia.**

```markdown
# AGENTS.md (~100 lines)

## Project Overview
Brief description of what this project does.

## Quick Start
- Run `make test` to verify setup
- Main entry point: `src/main.rs`

## Architecture
See [docs/architecture.md](docs/architecture.md) for detailed system design.

## Development Guide
See [docs/development.md](docs/development.md) for coding standards and workflows.

## API Reference
See [docs/api.md](docs/api.md) for function signatures and usage examples.

## Common Tasks
- Adding a feature: See docs/features.md
- Fixing bugs: See docs/debugging.md
- Running tests: `make test`

## Knowledge Base
The repository's knowledge base lives in the `docs/` directory, treated as the system of record.
```

**Benefits**:
- Short AGENTS.md (~100 lines) gets injected into context
- Serves primarily as a map with pointers to deeper sources of truth
- Detailed documentation stays out of context until needed
- Agent can load specific docs when relevant

## Context Building Strategies

### 1. File Selection

Agents need to know which files are relevant to the current task:

**Strategies**:
- **Dependency analysis**: Load files that imported/depend on modified files
- **Semantic search**: Find files with similar content to what agent is working on
- **Recency**: Prioritize recently modified files
- **Explicit mentions**: Load files user or agent explicitly references

**Example from Cursor's dynamic context discovery**:
```typescript
// Automatically discover relevant files based on:
// 1. Import/dependency graph
// 2. Semantic similarity to current task
// 3. Files mentioned in conversation
// 4. Recently modified files in same directory
```

### 2. Context Compaction

Context windows are finite (even 1M tokens runs out). Strategies for managing long conversations:

**Summarization**:
- Periodically summarize earlier turns
- Replace detailed history with concise summary
- Keep summary in context, discard details

**Selective Forgetting**:
- Identify and remove irrelevant context
- Keep task-relevant information
- Archive old turns to external storage

**Hierarchical Context**:
- Maintain multiple context layers
- High-level summary always in context
- Detailed info loaded on-demand

### 3. Prompt Design Patterns

#### System Prompt Structure

```
[Role Definition]
You are an expert software engineer working on [project type].

[Capabilities]
You can:
- Read and write code files
- Execute commands in a sandboxed environment
- Search the codebase
- Access documentation

[Constraints]
- Always verify changes compile before marking complete
- Ask for approval before destructive operations
- Follow existing code style and patterns

[Workflow]
1. Understand the task
2. Explore relevant code
3. Plan the implementation
4. Implement with tests
5. Verify everything works
6. Summarize changes made

[Anti-Patterns to Avoid]
- DO NOT implement placeholder or simple implementations
- DO NOT skip tests or verification steps
- DO NOT assume context not explicitly provided exists
```

#### Tool Descriptions as Prompts

Tool descriptions aren't just technical specs - they're instructions about how to behave:

**Example from OpenCode's bash.txt**:
```markdown
# Bash Tool

Execute shell commands in a sandboxed environment.

## Usage Guidelines

1. **Think before executing**: Consider what the command does and potential side effects
2. **Use safe defaults**: Prefer `--dry-run`, `-n`, or similar safety flags when available
3. **Check results**: Always verify command output matches expectations
4. **Handle errors**: Check exit codes and error messages
5. **Be explicit**: Use full paths, avoid relying on current directory

## Command Patterns

### Safe exploration
- `ls -la` to list files
- `cat file.txt` to read files
- `grep -r "pattern" .` to search codebase

### Dangerous operations (require approval)
- `rm`, `mv`, `cp` with destructive effects
- `sudo` commands
- Network operations that modify state
```

This does workflow steering that isn't about Bash at all - it gives the model instructions about how to behave.

#### Time-Grounded Prompts

OpenCode injects environment state:

```typescript
`Today's date: ${new Date().toDateString()}`
```

**Why this matters**:
- Models have no inherent sense of time
- "Recent" means different things without grounding
- Version numbers, deadlines, and timelines need context
- Bug reports and error messages often contain dates

**Trade-off**: Makes prompt bytes time-dependent. Great for grounding, bad for reproducibility.

## Model-Specific Optimization

### Anthropic Models (Claude)

**Optimized for**: Cursor, general coding tasks

**Characteristics**:
- Better tool use and output formatting inside IDEs
- Feel "native" in Cursor environment
- Consistently strong for coding across models

**Why**: Cursor is Anthropic's largest customer (~25% of revenue with GitHub Copilot). Models end up optimized for IDE workflows.

### OpenAI Models (GPT)

**Optimization**: Codex harness, Responses API

**Characteristics**:
- Blunder more with Cursor's system prompts
- Better in Codex's native environment
- Strong reasoning models (o1, o3, o4-mini) for complex tasks

**Note**: Model performance varies significantly by harness. A model optimized for one agent may underperform in another.

### Google Models (Gemini)

**Strengths**: Multilingual quality, especially Hebrew

**Use cases**:
- Non-English conversations
- Easily-searchable topics
- Multimodal tasks (images, videos)

## Context Window Management

### The Rot Problem

Context window rot is a real problem that limits all long-running agents:

**Symptoms**:
- Agent forgets earlier instructions
- Quality degrades over time
- Repetition and loops increase
- Task drift becomes common

**Causes**:
- Too much irrelevant context
- No compaction or summarization
- Model attention dilution across tokens
- Instruction buried in conversation history

### Mitigation Strategies

#### 1. Periodic Fresh Starts

Cursor's scaling experiments found they needed periodic fresh starts to combat drift and tunnel vision:

```
[Agent runs for X hours/tokens]
    ↓
[Fresh agent with summarized context]
    ↓
[Continue from checkpoint]
```

#### 2. Context Summarization

After N turns or token threshold:
1. Summarize conversation so far
2. Extract key decisions and facts
3. Replace detailed history with summary
4. Keep summary in new context window

#### 3. Selective Context Loading

Don't load everything into every turn:
- Load only task-relevant files
- Cache frequently accessed documentation
- Stream context as needed rather than upfront
- Use retrieval to find relevant historical turns

#### 4. Instruction Pinning

Keep critical instructions at the start and end of context:
```
[SYSTEM INSTRUCTIONS - PINNED]
...
[Conversation history]
...
[REMINDER: Key constraints and goals]
```

This helps with "lost in the middle" phenomenon where models pay less attention to tokens in the middle of long contexts.

## Cost Considerations

OpenAI notes: "Generally, the cost of sampling the model dominates the cost of network traffic, making sampling the primary target of our efficiency efforts. This is why prompt caching is so important."

**Strategies**:
- **Prompt caching**: Cache frequent context portions (system prompts, documentation)
- **Model routing**: Cheap models for simple steps, frontier models for hard parts
- **Context minimization**: Load only what's needed for each turn
- **Batching**: Combine multiple small requests when possible

## Best Practices

### 1. Give Agents a Map, Not an Encyclopedia

- Short AGENTS.md as table of contents (~100 lines)
- Detailed docs in structured directories
- Pointers to deeper sources of truth
- Load documentation on-demand when relevant

### 2. Context Engineering Is UX Engineering

- Product decides what model sees and when
- Design context loading like you design UI
- Test different context strategies empirically
- Measure impact on task success rate

### 3. Ground Models in Time and Environment

- Inject current date
- Include environment variables (when safe)
- Provide project-specific context
- Make implicit information explicit

### 4. Plan for Context Rot

- Implement compaction strategies
- Periodic fresh starts
- Summarization pipelines
- Selective loading mechanisms

### 5. Optimize for Your Harness

- Models perform differently in different harnesses
- Test models in your specific environment
- Don't assume benchmark performance transfers
- Consider model-harness co-optimization

## Common Mistakes

### ❌ One Giant Instruction File

```markdown
# AGENTS.md (2000+ lines)

[Everything about the project...]
[All coding standards...]
[Every API documented...]
[Complete deployment guide...]
```

**Problem**: Crowds out task and code, becomes noise, rots quickly.

**Fix**: Table of contents pattern with pointers to detailed docs.

### ❌ Loading Everything Into Context

```python
# Bad: Load entire codebase
all_files = get_all_files()
context = "\n".join(read_file(f) for f in all_files)
```

**Problem**: Wastes tokens, dilutes attention, increases cost.

**Fix**: Selective loading based on relevance.

### ❌ No Time Grounding

Agent has no sense of "now," making it struggle with:
- Version numbers ("latest" means what?)
- Deadlines ("due soon" is ambiguous)
- Recent changes ("what was just modified?")

**Fix**: Inject current date and relevant timestamps.

### ❌ Ignoring Harness Optimization

Using a model that's great on benchmarks but poor in your specific harness.

**Fix**: Test models in your actual environment, not just on leaderboards.

## References

- **OpenAI AGENTS.md Guide**: https://github.blog/ai-and-ml/github-copilot/how-to-write-a-great-agents-md-lessons-from-over-2500-repositories/
- **Anthropic Context Engineering**: https://www.anthropic.com/engineering/building-effective-agents
- **Cursor Dynamic Context Discovery**: https://cursor.com/blog/dynamic-context-discovery
- **OpenAI Prompt Caching**: https://openai.com/index/harness-engineering/

## Key Takeaways

1. **Context engineering is UX engineering** - Product decides what model sees and when
2. **AGENTS.md as map, not manual** - ~100 lines with pointers to detailed docs
3. **Tool descriptions are prompts too** - They steer behavior, not just specify APIs
4. **Time grounding matters** - Inject current date and environment context
5. **Context rot is real** - Implement compaction, summarization, fresh starts
6. **Model-harness co-optimization** - Models perform differently in different harnesses
7. **Selective loading wins** - Load only task-relevant context, not everything
8. **Cost follows context** - Prompt caching and minimization reduce costs significantly
