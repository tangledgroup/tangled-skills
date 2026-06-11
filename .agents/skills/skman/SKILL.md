---
name: skman
description: Scaffold, validate, and inspect agent skills (SKILL.md files). Use when creating new skills, checking skill format compliance, or reviewing skill structure.
---

# skman

Tools and guidelines for creating, validating, and managing agent skills.

## Usage

Scaffold a new skill with the helper script:

```bash
skman.sh create <name> "<description>"
```

Discover available commands:

```bash
skman.sh --help
skman.sh <subcommand> --help
```

## Skill Format

A skill is a directory containing a `SKILL.md` file. Everything else is optional.

### Directory Layout

```
<skill-name>/
├── SKILL.md              # Required: frontmatter + instructions
├── scripts/              # Optional: helper scripts (executed, not loaded into context)
│   ├── <skill-name>.sh   # Bash wrapper — the entry point referenced in SKILL.md
│   └── _<skill-name>.py  # Python implementation (underscore prefix, not called directly)

> Use `skman.sh create --with-scripts` to scaffold these.
├── references/           # Optional: detailed docs loaded on demand (numbered prefix)
│   └── 01-topic.md
│   └── 02-abc.md
│   └── 03-xyz.md
└── assets/               # Optional: templates, configs, etc.
```

### Frontmatter Fields

| Field | Required | Rules |
|---|---|---|
| `name` | Yes | 1-64 chars, lowercase a-z, 0-9, hyphens; no leading/trailing/consecutive hyphens; must match directory name exactly (e.g., `uv-0-11-19` for `uv-0-11-19/`); meta skills without versions use plain name (e.g., `skman`, `plan`) |
| `description` | Yes | Non-empty, max 1024 chars, third-person, must not contain XML/HTML tags (`<tag>`) |

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

2. **Write the frontmatter** — exactly `name` and `description` at minimum. The `name` must match the directory name exactly (e.g., `name: uv-0-11-19` for `uv-0-11-19/`). The description determines when the agent loads this skill; make it specific with trigger terms.

3. **Write the body** — concise instructions, under 500 lines. Must start with a level-1 heading matching `# <name>` or `# <name> <version>`. Structure:
   - `# <name>` (e.g., `# skman`) or `# <name> <version>` (e.g., `# uv 0.11.19`)
   - `## Overview` — what it does
   - `## Usage` — Optional: how to use it with examples
   - `## Gotchas` — Optional: The most useful part of teaching a skill is listing its hidden traps. Instead of vague advice, provide specific rules that stop the agent from making predictable, common-sense mistakes in that specific environment.
   - `## References` — Optional: Provides on-demand reference material for agents.

4. **Create a main script** (if automation is needed) — write the implementation as `scripts/_<skill-name>.py` (underscore prefix) and a thin bash wrapper `scripts/<skill-name>.sh` that passes all arguments through. Scripts are **executed** (not loaded into context). The SKILL.md references only the `.sh` file. Include `--help` at every level. Use stdlib only unless instructed otherwise. Scaffold with `--with-scripts`.

5. **Validate** — run the validation script:
   ```bash
   skman.sh validate <path-to-skill>
   ```

### Using the Scaffold Script

```bash
# Into default location (.agents/skills/my-skill/)
skman.sh create my-skill "Extracts text from PDF files"

# With version (dir: uv-0-11-19/, H1: # uv 0.11.19)
skman.sh create uv "Fast Python package manager" --version 0.11.19

# With scripts and references
skman.sh create my-skill "Desc" --with-scripts --with-references

# Into a specific parent directory
skman.sh create my-skill "Desc" -o ./custom-skills
```

The script validates name and description before creating files.

### Manual Creation

When writing files directly, ensure:
- Directory is named after the skill (e.g., `skman`) or `<skill-name>-<version>` (e.g., `uv-0-11-19`)
- Frontmatter `name` must match the directory name exactly (e.g., `name: uv-0-11-19` for `uv-0-11-19/`, or `name: skman` for `skman/`)
- `SKILL.md` exists at the directory root
- Body starts with `# <name>` or `# <name> <version>` matching the directory (e.g., `# uv 0.11.19` for `uv-0-11-19/`)

## Editing a Skill

Common operations:

- **Update description** — edit the frontmatter; this is what agents see in the system prompt
- **Split long content** — move sections >100 lines into `references/NN-topic.md`, link from SKILL.md
- **Add a script** — place in `scripts/` with the skill's name as base name
- **Restructure references** — keep references one level deep; all should link directly from SKILL.md

## Validation

Run the built-in validator:

```bash
skman.sh validate ./my-skill
skman.sh validate --strict ./my-skill
```

Checks performed:
- Frontmatter presence and required fields
- Name format (case, characters, length, hyphen rules)
- Description presence, length, and absence of XML/HTML tags
- Body starts with a level-1 heading
- Body line count warning (>500 lines)
- Name vs directory basename consistency (warns on mismatch)
- H1 heading format (`# <name>` or `# <name> <version>` — errors on mismatch)
- Recommended section presence (`## Overview` — warns if missing)
- Truly optional sections (`## Usage`, `## Gotchas`, `## References` — no warning when absent)
- Script executability (`<name>.sh` must be `chmod +x` — warns if not)
- Script usage references (`./<name>.sh` → `<name>.sh` — warns if the body uses `./<name>.sh` outside fenced code blocks)

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

### Progressive Disclosure
Skills use a four-level loading system:

1. **Metadata** (name + description) — always in context (~100 words). This is what determines whether the skill triggers.
2. **SKILL.md body** — loaded when skill triggers (<500 lines ideal). Contains the core instructions.
3. **Scripts** — executed (not loaded into context). Run via `<name>.sh`.
4. **References** — loaded as needed (unlimited). Reference files load on demand.

Guidelines:
- Keep SKILL.md body under 500 lines
- Move detailed content to `references/` files linked from SKILL.md
- Avoid deeply nested references — all reference files should link directly from SKILL.md
- Include a table of contents in reference files longer than 100 lines
- **Reference file naming** — use numeric prefixes (`01-`, `02-`, `03-`, …) for deterministic ordering and easy insertion. Files should be named `NN-topic.md` where `NN` is an incrementing number starting from 01
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

## Gotchas

- **Scaffolded `.sh` files may lose execute permission** — `skman.sh create --with-scripts` sets `chmod 0o755`, but editors or git checkouts can strip it. Always verify with `ls -l <name>.sh`; the validator warns if the bit is missing.
- **`--strict` turns section warnings into errors** — only `## Overview` produces a warning when missing. `## Usage`, `## Gotchas`, and `## References` are truly optional and never warn (knowledge-only skills often have no Usage section). In strict mode, any warning fails validation.
- **Frontmatter `name` must match the directory basename exactly** — e.g., `uv-0-11-19/` requires `name: uv-0-11-19`, `skman/` requires `name: skman`. The validator warns on mismatch. Fix by renaming the directory or correcting the frontmatter.
- **H1 heading must match `# <name>` or `# <base> <version>`** — the validator errors if the first heading doesn't match. For `skman/` it must be `# skman`; for `uv-0-11-19/` it must be `# uv 0.11.19` (version uses dots, not hyphens). The version in the H1 must correspond to the hyphenated version suffix in the directory/frontmatter name.
- **Reference files are loaded on demand, not into context** — keep SKILL.md self-contained for core instructions; move deep-dive content to `references/NN-topic.md` and link from the body.

## References

For detailed background on skill design decisions and agent behavior patterns, see:

- Agent prompt engineering best practices (progressive disclosure, token budgeting)
- Skill discovery mechanics (how descriptions trigger loading)
- Multi-domain skill organization patterns

## Generating README

After adding, removing, or renaming skills, regenerate the auto-generated section of `README.md`:

```bash
skman.sh generate
```

This scans `.agents/skills/` for all `SKILL.md` files, parses their frontmatter, and replaces everything from the auto-generated marker to end of file with a fresh Skills Table and Statistics section.

## Script Reference

```bash
skman.sh --help              # Top-level help
skman.sh create --help       # Create subcommand
skman.sh validate --help     # Validate subcommand
skman.sh info --help         # Info subcommand
skman.sh generate --help     # Generate subcommand
```

| Command | Purpose |
|---|---|
| `create <name> <desc> [--version <ver>]` | Scaffold a new skill directory with SKILL.md |
| `validate <path>` | Check SKILL.md against spec rules |
| `info <path>` | Print frontmatter and structural summary |
| `generate` | Generate Skills Table and Statistics in README.md |
