# Implementation Patterns

## Simplified UI-Based CLI Commands

For domain-specific coding agents, abstract away complex CLI commands behind simple button-driven interfaces. This makes the agent more accessible and reduces the chance of LLM errors in command construction.

Example pipeline for Power Platform Code Apps:

1. **Setup** — Initialize CodeApp JS files
2. **Authenticate** — Connect with tenant credentials
3. **Select environment** — List available environments, update config files
4. **Create connections** — Generate connections based on written code
5. **Deploy** — Push the app to the Power Platform environment

By moving these operations into deterministic UI buttons rather than relying on the LLM to construct CLI commands, you eliminate a major source of errors. Code is deterministic — whenever possible, move functionality to traditional code and UI rather than prompt-based instruction.

## Iterative Agent Training

The core methodology for building effective system prompts and skill files is iterative experience-driven learning:

1. **Build apps** using the agent extensively
2. **Read the reasoning** output from each LLM interaction
3. **Identify bugs and failures** in the generated code
4. **Document resolutions** into instruction.md and skill.md files
5. **Repeat** until the agent produces correct results consistently

This process is time-consuming, repetitive, and expensive in terms of API usage — but the goal is to only make each mistake once. Once documented, the agent should never repeat that error.

### The Learning Cycle

```
Build → Test → Find Bug → Document Fix → Update Skill/Instructions → Repeat
```

Each iteration adds knowledge to your instruction.md and skill.md files. Over time, these files become a comprehensive domain knowledge base that guides the LLM away from common pitfalls.

### Tracking Usage Spikes

Monitor your AI tool usage to identify active testing/learning periods. Spikes in Copilot or API usage typically correspond to intensive agent training sessions. This helps you track progress and estimate when the agent has converged on stable behavior.

## System Prompt Design

The system prompt is always active (unlike skills which are loaded dynamically). It should:

- Prevent the LLM from relying on general training data that conflicts with your domain
- Establish clear boundaries for what the agent should and should not do
- Reference available tools and their capabilities
- Be concise — every token counts toward context limits

For niche domains like vanilla JavaScript in Power Platform Code Apps, the system prompt is critical because the LLM's general JavaScript training data actively leads it astray. The system prompt redirects the model toward domain-specific patterns.

## Skill File Creation

Skills are created through the same iterative process as system prompts:

1. Start with a broad skill covering the domain
2. As specific patterns of failure emerge, create narrower skills
3. Each skill should address a specific class of problems or tasks
4. Skills should be self-contained and referenceable independently

Example skill structure for a niche framework:

```markdown
# Code App JavaScript Patterns

## Connection Handling
- Always use `PowerApps.createConnection()` not standard fetch
- Connection names must match environment config

## Event Handlers
- Use `component.onInit()` for initialization
- Never use React lifecycle methods

## Data Binding
- Bind to `context.data` not local state
- Refresh with `context.refresh()` after mutations
```

## Model Selection Impact

The choice of underlying model has a massive impact on agent performance:

- **Top-tier models** (e.g., Opus 4.6, GPT-5.4) deliver great results even in niche domains
- **Mid-tier models** (e.g., Auto mode, GPT-4.1) can deliver terrible results for specialized tasks

There is little you can do about this other than:

- Recommend better models during agent setup
- Provide documentation on how to prompt and structure builds for older or smaller models
- Accept that some domains require larger context windows and stronger reasoning capabilities

## External Dependency Risks

Relying on external dependencies like CLI tools and VS Code extensions introduces risks:

- **Duplicate installs** — Multiple versions of the same CLI can confuse the agent
- **Version drift** — Outdated CLI versions may not support current patterns
- **Environment differences** — What works on one machine may fail on another

Mitigation strategies:

- Build more functionality into deterministic UI rather than relying on CLI commands
- Have the LLM guide users to use UI buttons when it encounters issues
- Validate tool availability and version before executing commands
- Document known environment-specific issues in instruction.md
