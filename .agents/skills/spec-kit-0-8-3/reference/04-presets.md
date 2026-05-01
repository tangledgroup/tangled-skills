# Presets System

Presets customize how Spec Kit works — overriding templates, commands, and terminology without changing any tooling. They let you enforce organizational standards, adapt the workflow to your methodology, or localize the entire experience. Multiple presets can be stacked with priority ordering.

## Composition Strategies

Presets support three composition strategies for templates, commands, and scripts:

- **prepend** — insert content before the original
- **append** — add content after the original
- **wrap** — surround the original with wrapper content

These strategies allow fine-grained control over how preset overrides compose with core and extension templates.

## Template Resolution Order

Templates are resolved at runtime. Spec Kit walks the stack top-down and uses the first match:

| Priority | Component Type                                    | Location                         |
| -------: | ------------------------------------------------- | -------------------------------- |
|        1 | Project-Local Overrides                           | `.specify/templates/overrides/`  |
|        2 | Presets — Customize core & extensions             | `.specify/presets/templates/`    |
|        3 | Extensions — Add new capabilities                 | `.specify/extensions/templates/` |
|        4 | Spec Kit Core — Built-in SDD commands & templates | `.specify/templates/`            |

Project-local overrides (`.specify/templates/overrides/`) let you make one-off adjustments for a single project without creating a full preset.

## CLI Commands

### Search Presets

```bash
specify preset search [query]
```

| Option     | Description          |
| ---------- | -------------------- |
| `--tag`    | Filter by tag        |
| `--author` | Filter by author     |

Searches all active catalogs for presets matching the query. Without a query, lists all available presets.

### Install a Preset

```bash
specify preset add [<preset_id>]
```

| Option           | Description                                              |
| ---------------- | -------------------------------------------------------- |
| `--dev <path>`   | Install from a local directory (for development)         |
| `--from <url>`   | Install from a custom URL instead of the catalog         |
| `--priority <N>` | Resolution priority (default: 10; lower = higher precedence) |

Installs a preset from the catalog, a URL, or a local directory. Preset commands are automatically registered with the currently installed AI coding agent integration.

### Remove a Preset

```bash
specify preset remove <preset_id>
```

Removes an installed preset and cleans up its registered commands.

### List Installed Presets

```bash
specify preset list
```

Lists installed presets with their versions, descriptions, template counts, and current status.

### Preset Info

```bash
specify preset info <preset_id>
```

Shows detailed information about an installed or available preset, including its templates, metadata, and tags.

### Resolve a File

```bash
specify preset resolve <name>
```

Shows which file will be used for a given name by tracing the full resolution stack. Useful for debugging when multiple presets provide the same file.

### Enable / Disable

```bash
specify preset enable <preset_id>
specify preset disable <preset_id>
```

Disable a preset without removing it. Disabled presets are skipped during file resolution but their commands remain registered. Re-enable with `enable`.

### Set Priority

```bash
specify preset set-priority <preset_id> <priority>
```

Changes the resolution priority of an installed preset. Lower numbers take precedence. When multiple presets provide the same file, the one with the lowest priority number wins.

## Catalog Management

Preset catalogs control where `search` and `add` look for presets. Catalogs are checked in priority order.

### List Catalogs

```bash
specify preset catalog list
```

Shows all active catalogs with their priorities and install permissions.

### Add a Catalog

```bash
specify preset catalog add <url> --name <name>
```

| Option                                       | Description                                        |
| -------------------------------------------- | -------------------------------------------------- |
| `--name <name>`                              | Required. Unique name for the catalog              |
| `--priority <N>`                             | Priority (default: 10; lower = higher precedence)  |
| `--install-allowed / --no-install-allowed`   | Whether presets can be installed from this catalog (default: discovery only) |
| `--description <text>`                       | Optional description                               |

Adds a catalog to the project's `.specify/preset-catalogs.yml`.

### Remove a Catalog

```bash
specify preset catalog remove <name>
```

Removes a catalog from the project configuration.

## When to Use Presets vs Extensions

| Goal | Use |
| --- | --- |
| Add a brand-new command or workflow | Extension |
| Customize the format of specs, plans, or tasks | Preset |
| Integrate an external tool or service | Extension |
| Enforce organizational or regulatory standards | Preset |
| Ship reusable domain-specific templates | Either — presets for template overrides, extensions for templates bundled with new commands |

## Community Presets

Community-contributed presets customize Spec Kit behavior. See the full list on the [Community Presets](https://github.github.io/spec-kit/community/presets.html) page. Examples include compliance-oriented formats, Agile/Kanban/Waterfall methodology adaptations, security review gates, test-first task ordering, and language localization.

To submit your own preset, see the [Presets Publishing Guide](https://github.com/github/spec-kit/blob/main/presets/PUBLISHING.md).
