---
name: gh-2-91-0
description: GitHub CLI v2.91.0 for managing repositories, pull requests, issues, releases, workflows, codespaces, and more from the terminal. Use when automating GitHub workflows, scripting API calls, managing PRs/issues/releases from the command line, or integrating GitHub into CI/CD pipelines.
license: MIT
author: Tangled <noreply@tangledgroup.com>
version: "2.91.0"
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

## Overview

`gh` is GitHub's official command-line tool that brings pull requests, issues, releases, workflows, codespaces, and other GitHub concepts to the terminal. It is a standalone tool (not a git proxy) written in Go, supporting macOS, Windows, and Linux. Version 2.91.0 adds pseudonymous telemetry, expanded `gh skill` agent support, and improved skill discovery with hidden directory detection.

Supported platforms: GitHub.com, GitHub Enterprise Cloud, and GitHub Enterprise Server 2.20+.

## When to Use

- Managing pull requests from the terminal (create, review, merge, checkout)
- Creating, listing, editing, and closing issues without leaving the shell
- Automating GitHub Actions workflows and run management
- Scripting GitHub API calls with `gh api` for custom automation
- Managing releases, secrets, variables, and repository settings from CLI
- Working with GitHub Codespaces (create, manage, SSH, ports)
- Installing and managing AI agent skills via `gh skill`
- Authenticating to GitHub.com or GitHub Enterprise Server
- Searching across code, issues, PRs, commits, and repositories

## Installation / Setup

### macOS

```bash
# Homebrew
brew install gh

# Precompiled binary from releases page
# Download from https://github.com/cli/cli/releases/latest
```

### Linux & Unix

```bash
# Debian, Ubuntu, Raspberry Pi (apt)
# Follow instructions at docs/install_linux.md

# Amazon Linux, CentOS, Fedora, openSUSE, RHEL, SUSE (rpm)
# Follow instructions at docs/install_linux.md

# Precompiled binary from releases page
# Download from https://github.com/cli/cli/releases/latest
```

### Windows

```bash
# WinGet
winget install GitHub.cli

# Precompiled binary from releases page
# Download from https://github.com/cli/cli/releases/latest
```

### GitHub Codespaces

Add to your devcontainer configuration:

```json
"features": {
  "ghcr.io/devcontainers/features/github-cli:1": {}
}
```

### GitHub Actions

GitHub-hosted runners have `gh` pre-installed and updated weekly. For a specific version, install it using the platform-specific instructions above.

### Build from Source

See the [install_source.md](https://github.com/cli/cli/blob/trunk/docs/install_source.md) in the cli/cli repository for building from source.

### Binary Verification

Since v2.50.0, `gh` produces Build Provenance Attestation via Sigstore:

```bash
# Verify a downloaded release (requires gh already installed)
gh attestation verify -R cli/cli gh_2.91.0_macOS_arm64.zip
```

## Core Concepts

**Authentication**: `gh` authenticates via OAuth device flow or personal access tokens. Use `gh auth login` to begin interactive setup, or `gh auth login --with-token` for non-interactive token-based authentication.

**Repository Context**: Commands operate on the current repository by default (detected from git remote). Override with `-R OWNER/REPO` or set `GH_REPO`.

**Output Formatting**: All list/view commands support `--json` for structured output, `--jq` for filtering with jq syntax, and `--template` for Go template rendering.

**Aliases**: Create shortcuts for frequently used command combinations with `gh alias set`.

**Extensions**: Extend `gh` with community or custom extensions installed via `gh extension install`.

**Skills (v2.91)**: Install AI agent skills from GitHub repositories using `gh skill install`, supporting multiple agent hosts (Claude Code, pi, Codex, etc.) with hidden directory discovery (`--allow-hidden-dirs`).

## Usage Examples

### Pull Requests

```bash
# List open pull requests
gh pr list

# Create a PR interactively
gh pr create

# Create a PR with title and body
gh pr create --title "Fix bug" --body "Fixed the login issue"

# Create with reviewers
gh pr create --reviewer monalisa,hubot

# Auto-fill from commit messages
gh pr create --fill

# Checkout a PR locally
gh pr checkout 321

# View PR status
gh pr status

# Check CI status
gh pr checks

# Merge a PR
gh pr merge 123 --delete-branch

# Review a PR
gh pr review 123 --comment --body "Looks good!"
```

### Issues

```bash
# List open issues
gh issue list

# Create an issue with label
gh issue create --label bug

# View an issue
gh issue view 123

# Close an issue
gh issue close 123

# Add a comment
gh issue comment 123 --body "Working on this"
```

### Repositories

```bash
# Create a new repository
gh repo create my-project --private --source=.

# Clone a repository
gh repo clone cli/cli

# View repository details
gh repo view

# Fork a repository
gh repo fork cli/cli

# Archive/unarchive a repository
gh repo archive owner/repo
gh repo unarchive owner/repo
```

### GitHub Actions

```bash
# List workflow runs
gh run list

# View a specific run
gh run view 12345

# Watch a run (follow logs)
gh run watch 12345

# Download artifacts
gh run download 12345

# Rerun a failed job
gh run rerun 12345 --job build

# List workflows
gh workflow list

# Disable/enable a workflow
gh workflow disable ci.yml
gh workflow enable ci.yml
```

### API Access

```bash
# REST API call
gh api repos/{owner}/{repo}/releases

# POST with fields
gh api repos/{owner}/{repo}/issues/123/comments -f body='Hi from CLI'

# Use jq to filter response
gh api repos/{owner}/{repo}/issues --jq '.[].title'

# GraphQL query
gh api graphql -f query='
  query {
    viewer {
      repositories(first: 10) {
        nodes { nameWithOwner }
      }
    }
  }
'

# Paginated request
gh api graphql --paginate -f query='
  query($endCursor: String) {
    viewer {
      repositories(first: 100, after: $endCursor) {
        nodes { nameWithOwner }
        pageInfo { hasNextPage endCursor }
      }
    }
  }
'
```

### Skills (v2.91)

```bash
# Search for skills
gh skill search terraform

# Install a skill interactively
gh skill install github/awesome-copilot

# Install a specific skill
gh skill install github/awesome-copilot git-commit

# Pin to version
gh skill install github/awesome-copilot git-commit@v1.2.0

# Install from local directory
gh skill install ./my-skills --from-local

# Install for Claude Code at user scope
gh skill install github/awesome-copilot git-commit --agent claude-code --scope user

# Allow hidden directories (.claude/skills/, .agents/skills/)
gh skill install owner/repo --allow-hidden-dirs

# Update all installed skills
gh skill update --all

# Preview a skill before installing
gh skill preview github/awesome-copilot git-commit
```

### Aliases

```bash
# Set an alias
gh alias set bugs 'issue list --label="bug"'

# List aliases
gh alias list

# Import aliases from file
gh alias import aliases.json

# Delete an alias
gh alias delete bugs
```

## Advanced Topics

**Authentication and Enterprise**: OAuth flows, token management, GitHub Enterprise Server setup, SSH key integration → See [Authentication](reference/01-authentication.md)

**Output Formatting**: JSON output, jq filtering, Go templates, helper functions (tablerow, timeago, hyperlink) → See [Output Formatting](reference/02-output-formatting.md)

**Extensions and Skills**: Extension system architecture, creating extensions, skill installation across agent hosts → See [Extensions and Skills](reference/03-extensions-skills.md)

**GitHub Actions Automation**: Workflow management, run control, secrets, variables, cache operations → See [GitHub Actions](reference/04-github-actions.md)

**Codespaces Management**: Creating, managing, SSH access, port forwarding, Jupyter integration → See [Codespaces](reference/05-codespaces.md)

**Search and API**: Full-text search across code/issues/PRs/repos, REST and GraphQL API patterns → See [Search and API](reference/06-search-api.md)

**Configuration and Environment**: Config keys, environment variables, shell completion, telemetry → See [Configuration](reference/07-configuration.md)
