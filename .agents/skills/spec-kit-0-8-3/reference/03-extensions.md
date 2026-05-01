# Extensions System

Extensions add new capabilities to Spec Kit — domain-specific commands, external tool integrations, quality gates, and more. They introduce new commands and templates that go beyond the built-in Spec-Driven Development workflow.

## Extension Categories

- `docs` — reads, validates, or generates spec artifacts
- `code` — reviews, validates, or modifies source code
- `process` — orchestrates workflow across phases
- `integration` — syncs with external platforms
- `visibility` — reports on project health or progress

## Extension Effects

- `Read-only` — produces reports without modifying files
- `Read+Write` — modifies files, creates artifacts, or updates specs

## CLI Commands

### Search Extensions

```bash
specify extension search [query]
```

| Option       | Description                     |
| ------------ | ------------------------------- |
| `--tag`      | Filter by tag                   |
| `--author`   | Filter by author                |
| `--verified` | Show only verified extensions   |

Searches all active catalogs for extensions matching the query. Without a query, lists all available extensions.

### Install an Extension

```bash
specify extension add <name>
```

| Option          | Description                                              |
| --------------- | -------------------------------------------------------- |
| `--dev`         | Install from a local directory (for development)         |
| `--from <url>`  | Install from a custom URL instead of the catalog         |
| `--priority <N>`| Resolution priority (default: 10; lower = higher precedence) |

Installs an extension from the catalog, a URL, or a local directory. Extension commands are automatically registered with the currently installed AI coding agent integration.

> **Note:** All extension commands require a project already initialized with `specify init`.

### Remove an Extension

```bash
specify extension remove <name>
```

| Option          | Description                                    |
| --------------- | ---------------------------------------------- |
| `--keep-config` | Preserve configuration files during removal    |
| `--force`       | Skip confirmation prompt                       |

Removes an installed extension. Configuration files are backed up by default.

### List Installed Extensions

```bash
specify extension list
```

| Option        | Description                                        |
| ------------- | -------------------------------------------------- |
| `--available` | Show available (uninstalled) extensions            |
| `--all`       | Show both installed and available extensions       |

Lists installed extensions with their status, version, and command counts.

### Extension Info

```bash
specify extension info <name>
```

Shows detailed information about an installed or available extension, including description, version, commands, and configuration.

### Update Extensions

```bash
specify extension update [<name>]
```

Updates a specific extension, or all installed extensions if no name is given.

### Enable / Disable

```bash
specify extension enable <name>
specify extension disable <name>
```

Disable an extension without removing it. Disabled extensions are not loaded and their commands are not available. Re-enable with `enable`.

### Set Priority

```bash
specify extension set-priority <name> <priority>
```

Changes the resolution priority of an extension. When multiple extensions provide a command with the same name, the extension with the lowest priority number takes precedence.

## Catalog Management

Extension catalogs control where `search` and `add` look for extensions. Catalogs are checked in priority order (lower number = higher precedence).

### List Catalogs

```bash
specify extension catalog list
```

Shows all active catalogs in the stack with their priorities and install permissions.

### Add a Catalog

```bash
specify extension catalog add <url> --name <name>
```

| Option                               | Description                                        |
| ------------------------------------ | -------------------------------------------------- |
| `--name <name>`                      | Required. Unique name for the catalog              |
| `--priority <N>`                     | Priority (default: 10; lower = higher precedence)  |
| `--install-allowed / --no-install-allowed` | Whether extensions can be installed from this catalog |
| `--description <text>`               | Optional description                               |

Adds a catalog to the project's `.specify/extension-catalogs.yml`.

### Remove a Catalog

```bash
specify extension catalog remove <name>
```

Removes a catalog from the project configuration.

## Authentication

Extensions and catalogs hosted on GitHub can be authenticated with `GITHUB_TOKEN` or `GH_TOKEN` environment variables. This enables access to private repositories and higher API rate limits.

## Community Extensions

The community maintains 70+ extensions covering Jira integration, Azure DevOps sync, CI/CD gates, code review, security auditing, V-Model test traceability, Ralph loop automation, and more. Browse them on the [Community Extensions website](https://speckit-community.github.io/extensions/).

## Extension Development

To create your own extension:

1. Create a directory with `extension.yaml` manifest
2. Define commands as Markdown files in `templates/`
3. Test locally with `specify extension add --dev <path>`
4. Publish to the community catalog via the [Extension Publishing Guide](https://github.com/github/spec-kit/blob/main/extensions/EXTENSION-PUBLISHING-GUIDE.md)
