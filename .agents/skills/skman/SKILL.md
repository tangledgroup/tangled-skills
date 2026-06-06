---
name: skman
description: Scaffold, validate, and inspect agent skills (SKILL.md files). Use when creating new skills, checking skill format compliance, or reviewing skill structure.
---

# Skill Manager

Tools and guidelines for creating, validating, and managing agent skills.

## Quick Start

Scaffold a new skill with the helper script:

```bash
python3 -B scripts/skman.py create <name> "<description>"
```

Discover available commands:

```bash
python3 -B scripts/skman.py --help
python3 -B scripts/skman.py <subcommand> --help
```

## Skill Format

A skill is a directory containing a `SKILL.md` file. Everything else is optional.

### Directory Layout

```
<skill-name>/
├── SKILL.md              # Required: frontmatter + instructions
├── scripts/              # Optional: helper scripts (executed, not loaded)
│   └── <skill-name>.py  # Main script matching skill name
├── reference/            # Optional: detailed docs loaded on demand
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

4. **Create a main script** (if automation is needed) — place in `scripts/<skill-name>.py` or `scripts/<skill-name>.sh`. Include `--help` at every level. Use stdlib only unless instructed otherwise.

5. **Validate** — run the validation script:
   ```bash
   python3 -B scripts/skman.py validate <path-to-skill>
   ```

### Using the Scaffold Script

```bash
# Basic scaffold
python3 -B scripts/skman.py create my-skill "Extracts text from PDF files"

# With reference directory
python3 -B scripts/skman.py create my-skill "Desc" --with-reference

# Into a specific parent directory
python3 -B scripts/skman.py create my-skill "Desc" -o ./custom-skills
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
- **Split long content** — move sections >100 lines into `reference/NN-topic.md`, link from SKILL.md
- **Add a script** — place in `scripts/` with the skill's name as base name
- **Restructure references** — keep references one level deep; all should link directly from SKILL.md

## Validation

Run the built-in validator:

```bash
python3 -B scripts/skman.py validate ./my-skill
python3 -B scripts/skman.py validate --strict ./my-skill
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

### Progressive Disclosure
- Keep SKILL.md body under 500 lines
- Move detailed content to `reference/` files linked from SKILL.md
- Avoid deeply nested references — all reference files should link directly from SKILL.md
- Include a table of contents in reference files longer than 100 lines

### Model Compatibility
- SLMs (small models): need more explicit guidance, numbered steps, less ambiguity
- LLMs (large models): prefer concise instructions, avoid over-explaining
- Aim for instructions that work across both: clear structure, explicit rules, no fluff

## Script Reference

```bash
python3 -B scripts/skman.py --help              # Top-level help
python3 -B scripts/skman.py create --help       # Create subcommand
python3 -B scripts/skman.py validate --help     # Validate subcommand
python3 -B scripts/skman.py info --help         # Info subcommand
```

| Command | Purpose |
|---|---|
| `create <name> <desc>` | Scaffold a new skill directory with SKILL.md |
| `validate <path>` | Check SKILL.md against spec rules |
| `info <path>` | Print frontmatter and structural summary |
