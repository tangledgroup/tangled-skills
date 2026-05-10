---
name: tea-0-14-0
description: Official CLI for Gitea servers. Manage repositories, issues, pull requests, releases, and admin operations from the terminal. Supports multiple Gitea instances, OAuth2/token auth, and machine-readable output (JSON, YAML, CSV). Use when automating Gitea workflows, managing PRs and issues from the shell, or scripting CI/CD interactions.
license: MIT
author: Tangled <noreply@tangledgroup.com>
version: "0.1.0"
tags:
  - gitea
  - cli
  - git
  - devops
  - ci-cd
  - automation
category: cli-tool
external_references:
  - https://gitea.com/gitea/tea
  - https://code.gitea.io/sdk/gitea
  - https://dl.gitea.com/tea/
  - https://hub.docker.com/r/gitea/tea
  - https://pkg.go.dev/code.gitea.io/tea
  - https://gitea.com/gitea/tea/src/branch/main/docs
---

# tea 0.14.0

## Overview

tea is the official command-line tool for interacting with Gitea servers. Written in Go and built on `code.gitea.io/sdk/gitea`, it provides a productivity helper for managing most entities on one or multiple Gitea instances. It also offers local git helpers like `tea pr checkout` that work in an upstream/fork workflow.

tea automatically detects context from the repository in `$PWD` when available, and works best when the local main branch tracks the upstream repo. Configuration is persisted in `$XDG_CONFIG_HOME/tea`.

Key capabilities:

- **Multi-instance support** — log in to multiple Gitea servers simultaneously
- **Authentication** — application tokens, OAuth2 flow, basic auth, SSH keys
- **Machine-readable output** — JSON, YAML, CSV, TSV, table, and simple formats
- **Interactive mode** — commands without arguments enter interactive prompts
- **Shell completion** — bash, zsh, fish, PowerShell
- **Docker image** — available at `docker.io/gitea/tea`

## When to Use

- Managing Gitea issues, pull requests, releases, or milestones from the terminal
- Automating Gitea workflows in CI/CD pipelines (dispatching actions, merging PRs)
- Working across multiple Gitea instances without switching browsers
- Scripting bulk operations (closing issues, updating labels, managing webhooks)
- Integrating with AI-driven development flows (auto-merge on approval, re-trigger CI)
- Generating machine-readable output for data analysis or reporting

## Installation / Setup

Install via package manager:

```bash
# macOS (official Homebrew)
brew install tea

# Arch Linux (thirdparty)
pacman -S tea

# Alpine Linux (thirdparty)
apk add tea
```

Or use prebuilt binaries from [dl.gitea.com/tea/](https://dl.gitea.com/tea/) or Docker:

```bash
docker run --rm docker.io/gitea/tea --version
```

Install from source (requires Go 1.26+):

```bash
go install code.gitea.io/tea@latest
```

### Logging In

The most compatible authentication method across Gitea deployments:

1. Generate an application token in your Gitea user settings (at least **user read** scope)
2. Run `tea login add`, select **application token**, and paste the token

Since v0.10, OAuth2 interactive flow is also supported:

```bash
tea login add --oauth
```

SSH authentication is also available:

```bash
tea login add --ssh-agent-key <fingerprint>
```

### Shell Completion

```bash
# bash
source <(tea completion bash)

# zsh
source <(tea completion zsh)

# fish
tea completion fish > ~/.config/fish/completions/tea.fish
```

### Man Page

```bash
man <(tea man)
```

## Core Concepts

**Repository Context**: tea auto-detects the Gitea login and repository from git remotes in `$PWD`. Override with `--repo`, `--login`, or `--remote` flags.

**Command Structure**: Subcommands follow `tea <noun> <verb> [<args>] [<flags>]`. The default verb is `list`.

**Output Formats**: All commands support `--output` (`-o`) with values: `simple`, `table`, `csv`, `tsv`, `yaml`, `json`.

**Field Selection**: List commands support `--fields` (`-f`) for comma-separated field selection.

**Pagination**: Use `--limit` / `--lm` and `--page` / `-p` for paginated results.

**Login Management**: Multiple Gitea logins are stored in `$XDG_CONFIG_HOME/tea/config.yml`. OAuth tokens can be stored in the OS keyring via credstore (v0.13+).

## Advanced Topics

**Command Reference**: Complete CLI reference for all subcommands and flags → [Command Reference](reference/01-command-reference.md)

**Authentication and Configuration**: Login methods, config structure, OAuth2, SSH auth → [Authentication](reference/02-authentication.md)

**CI/CD and Automation Workflows**: Workflow dispatch, PR auto-merge, action secrets, webhooks → [Automation Workflows](reference/03-automation-workflows.md)
