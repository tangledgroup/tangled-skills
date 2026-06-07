---
name: skman
description: Scaffold, validate, and inspect agent skills (SKILL.md files). Use when creating new skills, checking skill format compliance, or reviewing skill structure.
---

# Skill Manager

Tools and guidelines for creating, validating, and managing agent skills.

## Quick Start

Scaffold a new skill with the helper script:

```bash
scripts/skman.sh create <name> "<description>"
```

Discover available commands:

```bash
scripts/skman.sh --help
scripts/skman.sh <subcommand> --help
```

## Skill Format

A skill is a directory containing a `SKILL.md` file. Everything else is optional.

### Directory Layout

```
<skill-name>/
├── SKILL.md              # Required: frontmatter + instructions
├── scripts/              # Optional: helper scripts (executed, not loaded)
│   ├── <skill-name>.sh   # Bash wrapper — the entry point referenced in SKILL.md
│   └── _<skill-name>.py  # Python implementation (underscore prefix, not called directly)
├── references/           # Optional: detailed docs loaded on demand (numbered prefix)
│   └── 01-topic.md
└── assets/               # Optional: templates, configs, etc.
```

### Frontmatter Fields

| Field | Required | Rules |
|---|---|---|
| `name` | Yes | 1-64 chars, lowercase a-z, 0-9, hyphens; no leading/trailing/consecutive hyphens |
| `description` | Yes | Non-empty, max 1024 chars, third-person, no XML tags |

### Frontmatter Template

```yaml
---
name: my-skill
description: What this skill does and when to use it. Be specific.
---
```

## Creating a New Skill

Follow these steps in order:

1. **Choose a name** — lowercase, hyphens, numbers only (e.g., `pdf-processing`, `git-8-20-0`). No leading/trailing/consecutive hyphens.

2. **Write the frontmatter** — exactly `name` and `description` at minimum. The description determines when the agent loads this skill; make it specific with trigger terms.

3. **Write the body** — concise instructions, under 500 lines. Structure:
   - `# Skill Title`
   - `## Overview` — what it does
   - `## Setup` — one-time steps (omit if none)
   - `## Usage` — how to use it with examples
   - Additional sections as needed, linked to reference files for detail

4. **Create a main script** (if automation is needed) — write the implementation as `scripts/_<skill-name>.py` (underscore prefix) and a thin bash wrapper `scripts/<skill-name>.sh` that passes all arguments through. The SKILL.md references only the `.sh` file. Include `--help` at every level. Use stdlib only unless instructed otherwise.

5. **Validate** — run the validation script:
   ```bash
   scripts/skman.sh validate <path-to-skill>
   ```

### Using the Scaffold Script

```bash
# Basic scaffold
scripts/skman.sh create my-skill "Extracts text from PDF files"

# With references directory
scripts/skman.sh create my-skill "Desc" --with-references

# Into a specific parent directory
scripts/skman.sh create my-skill "Desc" -o ./custom-skills
```

The script validates name and description before creating files.

### Manual Creation

When writing files directly, ensure:
- Directory is named after the skill (or `<skill-name>-<version>`)
- `SKILL.md` exists at the directory root
- Frontmatter has valid `name` and non-empty `description`
- Body starts with a level-1 heading

## Editing a Skill

Common operations:

- **Update description** — edit the frontmatter; this is what agents see in the system prompt
- **Split long content** — move sections >100 lines into `references/NN-topic.md`, link from SKILL.md
- **Add a script** — place in `scripts/` with the skill's name as base name
- **Restructure references** — keep references one level deep; all should link directly from SKILL.md

## Validation

Run the built-in validator:

```bash
scripts/skman.sh validate ./my-skill
scripts/skman.sh validate --strict ./my-skill
```

Checks performed:
- Frontmatter presence and required fields
- Name format (case, characters, length, hyphen rules)
- Description presence and length
- Body line count warning (>500 lines)

## Best Practices

### Conciseness
- Context window is shared — every token competes with conversation history
- Default assumption: the model already knows basics (what PDFs are, how libraries work)
- Challenge each paragraph: "Does this justify its token cost?"

### Match Specificity to Task Fragility
- **High freedom** (text instructions): multiple valid approaches, context-dependent decisions
- **Medium freedom** (pseudocode/scripts with parameters): preferred pattern exists, some variation OK
- **Low freedom** (exact commands): fragile operations, consistency is critical

### Description Writing
- Always third person ("Processes Excel files" not "I can help you")
- Include both what the skill does and when to use it
- Include key terms that trigger discovery (file extensions, tool names, task types)
- **Combat under-triggering** — models tend to under-use skills. Make the description slightly "pushy" by explicitly naming trigger phrases and adjacent contexts the user might say, even if they don't name the skill directly. Example:
  ```
  # Weak
  How to build a simple fast dashboard to display internal data.

  # Pushy
  How to build a simple fast dashboard to display internal data. Use this skill whenever the user mentions dashboards, data visualization, internal metrics, or wants to display any kind of company data, even if they don't explicitly ask for a "dashboard."
  ```

### Writing Style
- **Use imperative voice** — "Run this command" not "You should run this command"
- **Explain the why, avoid rigid MUST/ALWAYS/NEVER in caps** — modern models respond better to reasoning than rigid commands. If something is critical, explain why it matters
- **Use explicit Input/Output examples** to show expected transformations:
  ```markdown
  ## Example
  **Input:** Added user authentication with JWT tokens
  **Output:** feat(auth): implement JWT-based authentication
  ```
- **Define output formats with exact templates** when structure matters:
  ```markdown
  ALWAYS use this exact template:
  # [Title]
  ## Executive summary
  ## Key findings
  ```

### Progressive Disclosure
Skills use a three-level loading system:

1. **Metadata** (name + description) — always in context (~100 words). This is what determines whether the skill triggers.
2. **SKILL.md body** — loaded when skill triggers (<500 lines ideal). Contains the core instructions.
3. **Bundled resources** — loaded as needed (unlimited). Scripts execute without loading into context; reference files load on demand.

Guidelines:
- Keep SKILL.md body under 500 lines
- Move detailed content to `references/` files linked from SKILL.md
- Avoid deeply nested references — all reference files should link directly from SKILL.md
- Include a table of contents in reference files longer than 100 lines
- **Reference file naming** — use numeric prefixes (`00-`, `01-`, `02-`, …) for deterministic ordering and easy insertion. Files should be named `NN-topic.md` where `NN` is a zero-padded incrementing number
- **Multi-domain skills** — when a skill supports multiple variants (frameworks, platforms), organize by domain in references:
  ```
  cloud-deploy/
  ├── SKILL.md              # workflow + variant selection logic
  └── references/
      ├── 00-aws.md
      ├── 01-gcp.md
      └── 02-azure.md
  ```

### Model Compatibility
- SLMs (small models): need more explicit guidance, numbered steps, less ambiguity
- LLMs (large models): prefer concise instructions, avoid over-explaining
- Aim for instructions that work across both: clear structure, explicit rules, no fluff

## Generating README

After adding, removing, or renaming skills, regenerate the auto-generated section of `README.md`:

```bash
scripts/skman.sh generate
```

This scans `.agents/skills/` for all `SKILL.md` files, parses their frontmatter, and replaces everything from the auto-generated marker to end of file with a fresh Skills Table and Statistics section.

## Script Reference

```bash
scripts/skman.sh --help              # Top-level help
scripts/skman.sh create --help       # Create subcommand
scripts/skman.sh validate --help     # Validate subcommand
scripts/skman.sh info --help         # Info subcommand
scripts/skman.sh generate --help     # Generate subcommand
```

| Command | Purpose |
|---|---|
| `create <name> <desc>` | Scaffold a new skill directory with SKILL.md |
| `validate <path>` | Check SKILL.md against spec rules |
| `info <path>` | Print frontmatter and structural summary |
| `generate` | Generate Skills Table and Statistics in README.md |
