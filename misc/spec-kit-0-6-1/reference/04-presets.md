# Presets System

## Overview

Presets customize *how* Spec Kit works without adding new capabilities. They override the templates and commands that ship with the core and with installed extensions — for example, enforcing a compliance-oriented spec format, using domain-specific terminology, or applying organizational standards to plans and tasks.

Presets customize the artifacts and instructions that Spec Kit produces. Extensions expand what Spec Kit can do; presets change how it does what it already does.

## Preset Structure

```text
your-preset/
├── preset.yml                 # Required: Preset manifest
├── README.md                  # Required: Documentation
├── LICENSE                    # Required: License file
├── CHANGELOG.md               # Recommended
│
├── templates/                 # Template overrides
│   ├── spec-template.md
│   ├── plan-template.md
│   └── ...
│
└── commands/                  # Command overrides (optional)
    └── speckit.specify.md
```

## Preset Manifest (`preset.yml`)

```yaml
schema_version: "1.0"

preset:
  id: "your-preset"               # Unique lowercase-hyphenated ID
  name: "Your Preset Name"        # Human-readable name
  version: "1.0.0"                # Semantic version
  description: "Brief description (one sentence)"
  author: "Your Name or Organization"
  repository: "https://github.com/your-org/spec-kit-preset-your-preset"
  license: "MIT"

requires:
  speckit_version: ">=0.1.0"      # Required spec-kit version

provides:
  templates:
    - type: "template"
      name: "spec-template"
      file: "templates/spec-template.md"
      description: "Custom spec template"
      replaces: "spec-template"

tags:                              # 2-5 relevant tags
  - "category"
  - "workflow"
```

### Validation Rules

- `id`: lowercase with hyphens only (no underscores, spaces, special characters)
- `version`: semantic versioning (X.Y.Z)
- `description`: concise (under 200 characters)
- `repository`: valid and public URL
- Template names: lowercase with hyphens only
- Command names: dot notation (e.g., `speckit.specify`)

## Resolution Priority

Templates are resolved at runtime — Spec Kit walks the stack top-down and uses the first match:

| Priority | Component Type | Location |
|----------|---------------|----------|
| 1 (highest) | Project-Local Overrides | `.specify/templates/overrides/` |
| 2 | Presets | `.specify/presets/templates/` |
| 3 | Extensions | `.specify/extensions/templates/` |
| 4 (lowest) | Spec Kit Core | `.specify/templates/` |

- Project-local overrides let you make one-off adjustments for a single project without creating a full preset
- Extension/preset commands are applied at install time — command files written into agent directories
- If multiple presets or extensions provide the same command, the highest-priority version wins
- On removal, the next-highest-priority version is restored automatically
- Multiple presets can be stacked with priority ordering

## CLI Commands

```bash
# Search available presets
specify preset search
specify preset search healthcare

# Install a preset
specify preset add <preset-name>

# Test locally from directory
specify preset add --dev /path/to/your-preset

# Verify templates resolve from your preset
specify preset resolve spec-template

# Get preset info
specify preset info your-preset

# List installed presets
specify preset list

# Remove a preset
specify preset remove your-preset
```

## When to Use Which

- **Extension** — add a brand-new command or workflow, integrate an external tool or service
- **Preset** — customize the format of specs/plans/tasks, enforce organizational or regulatory standards
- **Either** — ship reusable domain-specific templates (presets for template overrides, extensions for templates bundled with new commands)

## Example Use Cases

- Restructure spec templates to require regulatory traceability
- Adapt workflow to fit your methodology (Agile, Kanban, Waterfall, jobs-to-be-done, domain-driven design)
- Add mandatory security review gates to plans
- Enforce test-first task ordering
- Localize the entire workflow to a different language

## Publishing Presets

To publish to the community catalog:

1. Create `preset.yml` manifest with valid fields
2. Test locally: `specify preset add --dev /path/to/preset`
3. Verify templates resolve: `specify preset resolve spec-template`
4. Create a GitHub release (tag `vX.Y.Z`)
5. Fork `github/spec-kit` and add entry to `presets/catalog.community.json`
6. Add preset row to `docs/community/presets.md` table
7. Submit a Pull Request

See the [Preset Publishing Guide](https://github.com/github/spec-kit/blob/main/presets/PUBLISHING.md) for detailed steps.

## Best Practices

**Template Design**: Keep sections clear with headings and placeholder text the LLM can replace. Match commands to templates — if your preset overrides a command, make sure it references sections in your template.

**Naming**: Preset IDs should be descriptive (`healthcare-compliance`, `enterprise-safe`, `startup-lean`). Avoid generic names (`my-preset`, `custom`, `test`).

**Stacking**: Design presets to work well when stacked with others. Only override templates you need to change. Document which templates and commands your preset modifies.
