# Command Reference

Complete reference for all Spec Kit slash commands, their parameters, and output formats.

## Core Commands

### `/speckit.constitution`

**Purpose:** Define or update project constitution (core principles and constraints).

**Syntax:**
```markdown
/speckit.constitution <constitution text>
```

**Example:**
```markdown
/speckit.constitution This project follows a "Library-First" approach. All features must be implemented as standalone libraries first. We use TDD strictly. We prefer functional programming patterns.
```

**Output:**
- Creates/updates `.specify/memory/constitution.md`
- Constitution is loaded for all subsequent planning commands

**When to use:**
- Initial project setup (first command after `specify init`)
- When project principles change
- Before starting major features that require architectural alignment

**Notes:**
- Constitution applies to entire project, not individual features
- Back up before upgrades (`specify init --here --force` overwrites it)
- Can reference organizational standards and compliance requirements

---

### `/speckit.specify`

**Purpose:** Create feature specification from natural language description.

**Syntax:**
```markdown
/speckit.specify <feature description>
```

**Example:**
```markdown
/speckit.specify Build a real-time chat system with message history, user presence indicators, and typing notifications.
```

**Parameters:**
- `$ARGUMENTS` - Feature description (required)
- `SPECIFY_FEATURE_DIRECTORY` - Override default specs directory (optional)
- `GIT_BRANCH_NAME` - Custom branch name (used by git extension hook)

**Output:**
- Git branch: `NNN-feature-name` (via git extension hook)
- Directory: `specs/NNN-feature-name/`
- Files created:
  - `spec.md` - Feature specification
  - `checklists/requirements.md` - Quality validation checklist
  - `.specify/feature.json` - Feature tracking metadata

**Specification Structure:**

```markdown
# Feature Specification: <Feature Name>

## Overview
<Brief description of what and why>

## User Scenarios & Testing
### Primary User Flow
1. Step one
2. Step two
...

## Functional Requirements
### FR-1: <Requirement Name>
- Criterion 1
- Criterion 2

## Success Criteria
- Measurable outcome 1
- Measurable outcome 2

## Key Entities
- Entity 1: <description>
- Entity 2: <description>

## Assumptions
- Assumption 1
- Assumption 2

## Acceptance Scenarios
### Scenario 1: <name>
**Given** ...
**When** ...
**Then** ...
```

**Quality Validation:**
- Maximum 3 `[NEEDS CLARIFICATION]` markers
- All requirements must be testable
- Success criteria must be technology-agnostic
- No implementation details (languages, frameworks)

**Extension Hooks:**
- `before_specify`: Runs before spec creation (git extension creates branch)
- `after_specify`: Runs after spec completion

**Common Issues:**
- "No feature description provided" - Must provide description after command
- "Cannot determine user scenarios" - Description too vague
- Too many `[NEEDS CLARIFICATION]` markers - Make more informed guesses

---

### `/speckit.clarify`

**Purpose:** Resolve ambiguities in existing specification.

**Syntax:**
```markdown
/speckit.clarify <clarification focus or details>
```

**Examples:**
```markdown
# Focus on specific areas
/speckit.clarify Focus on security and performance requirements.

# Provide specific details
/speckit.clarify Users should be able to export data in CSV and JSON formats. Export should include all filters currently applied.

# Interactive clarification (answers to NEEDS CLARIFICATION markers)
Q1: A, Q2: Custom - We need SSO with Azure AD, Q3: B
```

**Output:**
- Updates `spec.md` with clarified requirements
- Removes `[NEEDS CLARIFICATION]` markers
- Adds details to relevant sections

**When to use:**
- After `/speckit.specify` generates clarification questions
- When additional requirements emerge during stakeholder discussions
- To refine acceptance criteria before planning

**Clarification Format (Interactive Mode):**

When spec has `[NEEDS CLARIFICATION]` markers, command presents:

```markdown
## Question 1: Authentication Method

**Context**: "Users can log in to the system"

**What we need to know**: Authentication method not specified - email/password, SSO, OAuth?

**Suggested Answers**:

| Option | Answer | Implications |
|--------|--------|--------------|
| A      | Email/password | Simplest implementation, requires password reset flow |
| B      | OAuth2 (Google, GitHub) | Leverages existing accounts, faster onboarding |
| C      | SSO (SAML/OIDC) | Enterprise-ready, requires identity provider setup |
| Custom | Provide your own answer | Describe your authentication requirements |

**Your choice**: _[Wait for user response]_
```

---

### `/speckit.checklist`

**Purpose:** Validate specification quality against completeness criteria.

**Syntax:**
```markdown
/speckit.checklist
```

**Output:**
- Creates/updates `specs/<feature>/checklists/requirements.md`
- Validates each checklist item with pass/fail status
- Documents specific issues found

**Checklist Items:**

**Content Quality:**
- [ ] No implementation details (languages, frameworks, APIs)
- [ ] Focused on user value and business needs
- [ ] Written for non-technical stakeholders
- [ ] All mandatory sections completed

**Requirement Completeness:**
- [ ] No `[NEEDS CLARIFICATION]` markers remain
- [ ] Requirements are testable and unambiguous
- [ ] Success criteria are measurable
- [ ] Success criteria are technology-agnostic
- [ ] All acceptance scenarios defined
- [ ] Edge cases identified
- [ ] Scope clearly bounded
- [ ] Dependencies and assumptions identified

**Feature Readiness:**
- [ ] All functional requirements have clear acceptance criteria
- [ ] User scenarios cover primary flows
- [ ] Feature meets measurable outcomes
- [ ] No implementation details leak into specification

**When to use:**
- Before running `/speckit.plan` (recommended)
- After major specification updates
- As gate before implementation begins

---

### `/speckit.plan`

**Purpose:** Generate technical implementation plan from specification.

**Syntax:**
```markdown
/speckit.plan <technology stack and architecture choices>
```

**Example:**
```markdown
/speckit.plan Use React with TypeScript for frontend, Node.js/Express for backend API, PostgreSQL for database, Redis for caching. Implement JWT authentication. Deploy to AWS with ECS Fargate.
```

**Parameters:**
- `$ARGUMENTS` - Technology stack description (required)
- Scripts executed:
  - Bash: `scripts/bash/setup-plan.sh --json`
  - PowerShell: `scripts/powershell/setup-plan.ps1 -Json`

**Output Files:**
- `plan.md` - Main implementation plan
- `research.md` - Technology research findings
- `data-model.md` - Entity schemas and relationships
- `contracts/` - API/interface contracts (if applicable)
- `quickstart.md` - Key validation scenarios
- Agent context file updated (`.claude/`, `.gemini/`, etc.)

**Plan Structure:**

```markdown
# Implementation Plan: <Feature Name>

## Technical Context

### Technology Stack
- Frontend: <technologies>
- Backend: <technologies>
- Database: <technologies>
- Infrastructure: <technologies>

### Architecture Decisions
#### Decision 1: <title>
**Rationale**: <why chosen>
**Alternatives considered**: <what else evaluated>

## Constitution Compliance

✅ **<Principle>**: <how addressed>
⚠️ **<Principle>**: <deferred with justification>

## Data Model

### <Entity> Entity
```<language>
<Entity schema or class definition>
```

## API Contracts

### <Endpoint> API
- `GET /path` - Description
- `POST /path` - Description

## Quickstart Validation

1. Step one
2. Step two
...
```

**Phases:**

**Phase 0: Research**
- Extract unknowns from technical context
- Generate research tasks for each `[NEEDS CLARIFICATION]`
- Consolidate findings in `research.md`

**Phase 1: Design & Contracts**
- Generate `data-model.md` from specification entities
- Create interface contracts in `contracts/` (if applicable)
- Update agent context with new technologies
- Re-evaluate constitution compliance

**Extension Hooks:**
- `before_plan`: Runs before planning starts
- `after_plan`: Runs after plan completion

**Gates:**
- ERROR if constitution violations are unjustified
- ERROR if `[NEEDS CLARIFICATION]` markers remain unresolved
- WARNING if research incomplete but proceeding

---

### `/speckit.tasks`

**Purpose:** Break down implementation plan into executable task list.

**Syntax:**
```markdown
/speckit.tasks
```

**Input Files (read in order):**
1. `plan.md` (required)
2. `data-model.md` (if present)
3. `contracts/` (if present)
4. `research.md` (if present)

**Output:**
- `tasks.md` - Executable task list with dependencies

**Task Format:**

```markdown
# Tasks: <Feature Name>

## Phase 1: <Phase Name> [P]

- [ ] **T1**: <Task description>
  - Dependencies: T2, T3 (or "None")
  - Acceptance: <how to verify completion>
  
- [ ] **T2**: <Task description>
  - Dependencies: None
  - Acceptance: <verification criteria>

## Parallelization Notes

- **[P]** marked phases can run tasks in parallel
- Phase dependencies listed explicitly
- Safe parallel groups outlined

## Estimated Effort

- Phase 1: X hours
- **Total**: Y hours (can be reduced with parallel execution)
```

**Task Derivation:**
- Contracts → API implementation tasks
- Entities → Database migration tasks
- Scenarios → Test task generation
- Architecture decisions → Infrastructure setup tasks

**When to use:**
- After `/speckit.plan` completes
- Before starting implementation
- To understand task dependencies and parallelization opportunities

---

### `/speckit.analyze`

**Purpose:** Audit implementation plan for completeness and issues.

**Syntax:**
```markdown
/speckit.analyze
```

**Analysis Checks:**
- Constitution compliance (flags violations)
- API contract completeness
- Data model consistency with specification
- Task dependency correctness
- Missing acceptance criteria
- Technology stack conflicts

**Output:**
- Analysis report with issues categorized by severity:
  - **ERROR**: Must fix before proceeding
  - **WARNING**: Should address but can proceed
  - **INFO**: Recommendations for improvement

**Example Output:**

```markdown
# Plan Analysis: Create Taskify

## Errors (Must Fix)

❌ **Missing Entity**: Specification mentions "Comment" but data-model.md only has User, Project, Task

## Warnings (Should Address)

⚠️ **Constitution Deferral**: WCAG 2.1 AA compliance deferred to Phase 2
   - Justification provided: MVP timeline constraints
   - Recommendation: Create follow-up feature for accessibility audit

⚠️ **Missing Contract**: Tasks API lacks error response schemas

## Info (Recommendations)

ℹ️ **Optimization**: Consider adding Redis cache for frequently accessed project lists
ℹ️ **Testing**: No integration test tasks identified in task list

## Summary

- Errors: 1 (blocking)
- Warnings: 2 (non-blocking)
- Recommendations: 2

**Action Required**: Fix errors before running `/speckit.implement`
```

**When to use:**
- After `/speckit.plan` to validate before task generation
- After `/speckit.tasks` to verify task completeness
- Before `/speckit.implement` as final gate

---

### `/speckit.implement`

**Purpose:** Execute code generation from task list.

**Syntax:**
```markdown
/speckit.implement
```

**Input:**
- `tasks.md` - Task list to execute
- All design artifacts (plan, data-model, contracts)

**Execution Flow:**
1. Read tasks in dependency order
2. Execute each task (AI agent generates code)
3. Verify acceptance criteria for each task
4. Report completion status

**Output:**
- Generated source code in `src/`
- Updated task list with completion status
- Implementation summary report

**Phased Implementation:**

For complex features, implement in phases:

```markdown
/speckit.implement Phase 1 tasks only (T1-T3)
```

**When to use:**
- After all planning and validation complete
- When ready to generate actual code
- Can be run multiple times for phased implementation

**Best Practices:**
- Run `/speckit.analyze` first to catch issues
- Implement in phases for large features
- Review generated code before committing
- Update tasks.md if additional tasks discovered during implementation

---

## Extension Commands

Extensions add domain-specific commands with namespaced syntax: `speckit.<extension-id>.<command-name>`

### Git Extension Commands (Built-in)

**`/speckit.git.initialize`**
- Initialize git repository (if not already initialized)
- Configure git hooks for SDD workflow

**`/speckit.git.feature`**
- Create and switch to feature branch
- Branch name: `NNN-feature-name`

**`/speckit.git.remote`**
- Configure remote repository
- Push feature branch

**`/speckit.git.commit`**
- Commit current changes with conventional commit message
- Include feature number in commit message

**`/speckit.git.validate`**
- Validate branch naming convention
- Check for required files in feature directory

### Example: Jira Extension Commands

**`/speckit.jira.specstoissues`**
- Convert specifications to Jira issues
- Maintain traceability between spec and issues

**`/speckit.jira.sync`**
- Sync task status with Jira
- Update Jira comments from implementation notes

### Example: Linear Extension Commands

**`/speckit.linear.create`**
- Create Linear issues from specifications
- Link issues to feature directory

---

## Command Configuration

### Frontmatter Fields

Command files use YAML frontmatter for metadata:

```yaml
---
description: "Command description"
handoffs:
  - label: "Next step label"
    agent: speckit.next-command
    prompt: "Prompt for next command"
    send: true
scripts:
  sh: scripts/bash/command.sh --json
  ps: scripts/powershell/command.ps1 -Json
agent_scripts:
  sh: scripts/bash/update-agent-context.sh __AGENT__
  ps: scripts/powershell/update-agent-context.ps1 -AgentType __AGENT__
---
```

**Fields:**
- `description`: Command description shown in AI agent UI
- `handoffs`: Suggested next commands with prompts
- `scripts`: Bash/PowerShell scripts to execute
- `agent_scripts`: Agent context update scripts

### Placeholders

Commands use placeholders replaced at execution:

| Placeholder | Replaced With |
|-------------|---------------|
| `$ARGUMENTS` | User-provided arguments |
| `{SCRIPT}` | Path to bash/powershell script |
| `{{args}}` | Arguments (TOML format for Gemini) |
| `__AGENT__` | AI agent name (claude, copilot, etc.) |

---

## Hook System

Extensions can register hooks that execute at lifecycle events:

### Available Hooks

| Hook Event | When It Runs |
|------------|--------------|
| `before_specify` | Before `/speckit.specify` creates spec |
| `after_specify` | After spec creation complete |
| `before_plan` | Before `/speckit.plan` generates plan |
| `after_plan` | After plan generation complete |
| `before_tasks` | Before `/speckit.tasks` creates task list |
| `after_tasks` | After task list generated |
| `before_implement` | Before `/speckit.implement` starts |
| `after_implement` | After implementation complete |
| `before_analyze` | Before `/speckit.analyze` runs audit |

### Hook Configuration

In `.specify/extensions.yml`:

```yaml
hooks:
  before_specify:
    - extension: git
      command: speckit.git.feature
      optional: false
      prompt: "Create feature branch?"
      description: "Creates git branch for this feature"
      condition: null  # Always run if enabled
```

**Hook Fields:**
- `extension`: Extension ID
- `command`: Command to execute
- `optional`: If true, prompts user; if false, auto-executes
- `prompt`: Prompt text for optional hooks
- `description`: Hook description
- `condition`: Optional condition expression (evaluated by HookExecutor)

---

## Troubleshooting Commands

### Command Not Recognized

**Symptom:** AI agent says "Unknown command: /speckit.specify"

**Solutions:**
1. Verify command files exist: `ls -la .claude/commands/` (or appropriate agent folder)
2. Restart IDE/editor completely
3. Re-run `specify init --here --force --ai <agent>`

### Command Fails Mid-Execution

**Symptom:** Command stops with error partway through

**Check:**
1. Review error message for specific issue
2. Verify all prerequisite files exist
3. Check `.specify/feature.json` for correct feature directory
4. Run `/speckit.analyze` to validate plan before implementation

### Hook Execution Fails

**Symptom:** Hook command fails during core command execution

**Solutions:**
1. Check `.specify/extensions.yml` for hook configuration
2. Disable problematic hook: set `enabled: false`
3. Run hook command manually to see full error
4. Review extension documentation for requirements

---

## Next Steps

- Explore [Extensions Guide](references/04-extensions.md) for custom commands
- Review [AI Agent Support](references/05-ai-agents.md) for agent-specific configurations
- Read [SDD Methodology](references/06-sdd-methodology.md) for workflow context
