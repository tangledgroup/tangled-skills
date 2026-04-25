---
name: gh-2-91-0
description: GitHub CLI v2.91.0 for managing repositories, pull requests, issues, releases, workflows, codespaces, and more from the terminal. Use when automating GitHub workflows, scripting API calls, managing PRs/issues/releases from the command line, or integrating GitHub into CI/CD pipelines.
license: MIT
author: Tangled <noreply@tangledgroup.com>
version: "0.1.0"
tags:
  - github
  - cli
  - devops
  - automation
  - ci-cd
category: development-tools
external_references:
  - https://cli.github.com/
  - https://github.com/cli/cli
  - https://github.com/cli/cli#installation
  - https://github.com/cli/cli/releases
  - https://github.com/topics/gh-extension
  - https://cli.github.com/manual/
  - https://github.com/cli/cli/releases/tag/v2.91.0
---

# GitHub CLI v2.91.0


## Core Concepts

This skill covers the key concepts and fundamental ideas related to this topic.
## Overview

`gh` is GitHub on the command line. It brings pull requests, issues, releases, workflows, and other GitHub concepts to the terminal next to where you are already working with `git` and your code. Written in Go, it supports macOS, Windows, and Linux, and works with GitHub.com, GitHub Enterprise Cloud, and GitHub Enterprise Server 2.20+.

## When to Use

- Managing pull requests, issues, or releases from the terminal
- Scripting GitHub API calls without writing custom HTTP clients
- Automating CI/CD workflows (triggering runs, managing secrets)
- Creating or cloning repositories from the command line
- Working with GitHub Codespaces
- Building shell scripts that interact with GitHub programmatically
- Setting up aliases for frequently used GitHub operations

## Installation

**macOS (Homebrew):**

```bash
brew install gh
```

**Linux (Debian/Ubuntu):**

```bash
sudo apt install gh
```

**Windows (WinGet):**

```powershell
winget install GitHub.cli
```

**Precompiled binaries:** Download from the [GitHub CLI releases page](https://github.com/cli/cli/releases).

**Upgrade:**

```bash
gh extension install github/gh-upgrade
gh upgrade
```

**Verify binary provenance (since v2.50.0):**

```bash
gh at verify -R cli/cli gh_2.91.0_macOS_arm64.zip
```

## Authentication

Authenticate with GitHub:

```bash
gh auth login
```

Interactive prompts guide you through choosing the host, authenticating via browser or token, and selecting Git protocol (HTTPS or SSH).

```bash
# Check auth status
gh auth status

# Logout
gh auth logout

# Get raw token for scripting
gh auth token

# Switch between accounts
gh auth switch
```

## Quick Start Examples

```bash
# List issues in current repo
gh issue list

# Create a PR interactively
gh pr create

# View PR checks
gh pr checks

# Clone a repository
gh repo clone cli/cli

# Create a release
gh release create v1.0.0 --generate-notes

# Run a workflow
gh workflow run ci.yml

# Call the GitHub API
gh api repos/{owner}/{repo}/issues
```

## Core Command Groups

### Issues

Work with GitHub issues: create, list, view, edit, close, comment, lock, pin, transfer.

```bash
gh issue list --label bug --state open
gh issue create --title "Fix login" --body "Description here" --assignee @me
gh issue view 123 --web
gh issue close 456
gh issue comment 123 --body "On it"
```

### Pull Requests

Full PR lifecycle: create, checkout, review, merge, diff, update branch, revert.

```bash
gh pr create --fill
gh pr checkout 353
gh pr review --approve
gh pr merge --squash --delete-branch
gh pr diff > changes.patch
gh pr list --state merged --author me
```

### Repositories

Create, clone, fork, edit, archive, view repositories.

```bash
gh repo create my-project --private --source=. --remote=origin
gh repo fork cli/cli
gh repo view --web
gh repo sync  # sync fork with upstream
```

### Releases

Manage releases and assets.

```bash
gh release create v2.0.0 --title "Version 2" --notes "New features"
gh release download v2.0.0 --pattern "*.tar.gz" -D ./dist
gh release upload v2.0.0 binary-linux-amd64
gh release edit v2.0.0 --notes-file RELEASE.md
```

### GitHub Actions (Workflows & Runs)

Manage workflows and workflow runs.

```bash
gh workflow list
gh workflow run ci.yml --ref main
gh run list --workflow=ci.yml
gh run view --log 1234567890
gh run watch 1234567890
```

### Secrets & Variables

Manage repository and organization secrets/variables for Actions.

```bash
gh secret set MY_KEY --body "value" --repo owner/repo
gh secret list -R owner/repo
gh variable set APP_ENV --body production
echo "my-secret" | gh secret set MY_KEY --stdin
```

### API Access

Direct access to GitHub REST and GraphQL APIs.

```bash
# REST API GET
gh api repos/{owner}/{repo}/issues?state=open

# REST API POST with fields
gh api repos/{owner}/{repo}/issues -f title="Bug" -f body="Found a bug"

# GraphQL
gh api graphql -q '{viewer{login}}' -f query='query{viewer{login}}'

# Custom headers
gh api -H "Accept: application/vnd.github+json" repos/{owner}/{repo}
```

### Search

Search across code, issues, PRs, and repositories.

```bash
gh search issues --label bug --state open
gh search prs --author me --merged
gh search code "TODO" --language go
gh search repos --topic rust --private
```

## Configuration

```bash
# View/edit settings
gh config get git_protocol
gh config set git_protocol ssh
gh config set editor vim
gh config list

# Clear cached credentials
gh config clear-cache
```

**Respected settings:** `git_protocol`, `editor`, `prompt`, `prefer_editor_prompt`, `pager`, `browser`, `color_labels`, `accessible_colors`, `spinner`, `telemetry`.

## Aliases

Create shortcuts for frequently used commands.

```bash
gh alias set co 'pr checkout'
gh alias set bugs 'issue list --label bug'
gh alias set myprs 'pr list --author me'
gh alias list
gh alias delete co
```

## Extensions

Extend `gh` with community-built plugins.

```bash
gh extension list
gh extension search copilot
gh extension install github/gh-copilot
gh extension remove gh-copilot
gh extension upgrade
gh extension browse  # open extensions marketplace in browser
```

Extension repositories must start with `gh-` and contain an executable of the same name. Browse available extensions at <https://github.com/topics/gh-extension>.

## Output Formatting

Commands support multiple output formats for scripting:

```bash
# JSON output with specific fields
gh issue list --json number,title,state

# jq filtering (built-in, no jq install needed)
gh pr list --json number,title --jq '.[] | select(.title | test("fix"))'

# Go template formatting
gh release list --template '{{range .}}{{.TagName}} {{end}}'
```

Template functions: `autocolor`, `color`, `join`, `pluck`, `tablerow`, `tablerender`, `timeago`, `timefmt`, `truncate`.

## Environment Variables

Key environment variables for configuration:

- `GH_TOKEN` / `GITHUB_TOKEN` — authentication token for github.com
- `GH_ENTERPRISE_TOKEN` / `GITHUB_ENTERPRISE_TOKEN` — token for GitHub Enterprise Server
- `GH_HOST` — default hostname
- `GH_REPO` — default repository (`[HOST/]OWNER/REPO`)
- `GH_EDITOR` / `GIT_EDITOR` / `EDITOR` — text editor (in order of precedence)
- `GH_BROWSER` / `BROWSER` — web browser
- `GH_DEBUG` — verbose output; set to `api` for HTTP traffic logging
- `GH_PAGER` / `PAGER` — terminal pager
- `NO_COLOR` — disable colored output
- `GLAMOUR_STYLE` — Markdown rendering style

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Command completed successfully |
| 1 | Command failed |
| 2 | Command was cancelled |
| 4 | Authentication required |

## Advanced Topics

- [Command Reference](references/01-command-reference.md) — Complete list of all `gh` commands and subcommands
- [GitHub Codespaces](references/02-codespaces.md) — Managing codespaces from the terminal
- [GitHub Projects](references/03-projects.md) — Working with GitHub Projects via CLI
- [Attestation & Security](references/04-attestation.md) — Build provenance verification and security features


