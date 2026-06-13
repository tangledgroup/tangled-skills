# CLI Reference

The Specify CLI (`specify`) manages the full lifecycle of Spec-Driven Development — from project initialization to workflow automation.

## Core Commands

### Initialize a Project

```bash
specify init [<project_name>]
```

| Option                   | Description                                                              |
| ------------------------ | ------------------------------------------------------------------------ |
| `--integration <key>`    | AI coding agent integration (e.g. `copilot`, `claude`, `gemini`)         |
| `--integration-options`  | Options for the integration (e.g. `--integration-options="--skills"`)    |
| `--script sh\|ps`        | Script type: `sh` (bash/zsh) or `ps` (PowerShell)                       |
| `--here`                 | Initialize in the current directory instead of creating a new one        |
| `--force`                | Force merge/overwrite when initializing in an existing directory         |
| `--no-git`               | Skip git repository initialization (**deprecated**, gated at v0.10.0)   |
| `--ignore-agent-tools`   | Skip checks for AI coding agent CLI tools                                |
| `--preset <id>`          | Install a preset during initialization                                   |
| `--branch-numbering`     | Branch numbering strategy: `sequential` (default) or `timestamp`         |

Creates a new Spec Kit project with the necessary directory structure, templates, scripts, and AI coding agent integration files.

Use `<project_name>` to create a new directory, or `--here` (or `.`) to initialize in the current directory. If the directory already has files, use `--force` to merge without confirmation.

### Check Installed Tools

```bash
specify check
```

Checks that required tools are available on your system: `git` and any CLI-based AI coding agents. IDE-based agents are skipped since they don't require a CLI tool.

### Version Information

```bash
specify version
specify --version
specify -V
```

Displays the Spec Kit CLI version, Python version, platform, and architecture.

## Integrations

Integrations connect Spec Kit to your AI coding agent. Each integration sets up the appropriate command files, context rules, and directory structures for a specific agent. Only one integration is active per project at a time.

```bash
specify integration list
```

Lists all available integrations. Spec Kit works with 30+ AI coding agents — both CLI tools and IDE-based assistants.

## Extensions

```bash
specify extension search [query]
specify extension add <name>
specify extension remove <name> [--keep-config] [--force]
specify extension list [--available] [--all]
specify extension info <name>
specify extension update [<name>]
specify extension enable <name>
specify extension disable <name>
specify extension set-priority <name> <priority>
```

See the [Extensions System](reference/03-extensions.md) for full details.

## Presets

```bash
specify preset search [query]
specify preset add [<preset_id>]
specify preset remove <preset_id>
specify preset list
specify preset info <preset_id>
specify preset resolve <name>
specify preset enable <preset_id>
specify preset disable <preset_id>
specify preset set-priority <preset_id> <priority>
```

See the [Presets System](reference/04-presets.md) for full details.

## Workflows

```bash
specify workflow run <source> [-i key=value]
specify workflow resume <run_id>
specify workflow status [<run_id>]
specify workflow list
specify workflow add <source>
specify workflow remove <workflow_id>
specify workflow search [query] [--tag <tag>]
specify workflow info <workflow_id>
```

See the [Workflows Engine](reference/06-workflows.md) for full details.

## Environment Variables

| Variable          | Description                                                              |
| ----------------- | ------------------------------------------------------------------------ |
| `SPECIFY_FEATURE` | Override feature detection for non-Git repositories. Set to the feature directory name (e.g., `001-photo-albums`) to work on a specific feature when not using Git branches. Must be set in the context of the agent prior to using `/speckit.plan` or follow-up commands. |
| `GITHUB_TOKEN`    | Authenticate GitHub-hosted catalog and download requests                 |
| `GH_TOKEN`        | Alternative to `GITHUB_TOKEN` for authentication                         |

## Upgrade

```bash
# Upgrade CLI
uv tool install specify-cli --force --from git+https://github.com/github/spec-kit.git@v0.8.3

# Update project files
specify init --here --force --integration copilot
```

See the [Upgrade Guide](https://github.com/github/spec-kit/blob/main/docs/upgrade.md) for detailed instructions.

## Troubleshooting

If you encounter issues with an agent, open a GitHub issue so the maintainers can refine the integration. For Git Credential Manager issues on Linux, see the troubleshooting section in the README.
