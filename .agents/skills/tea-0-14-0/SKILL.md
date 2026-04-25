---
name: tea-0-14-0
description: Official CLI for Gitea servers. Manage issues, pull requests, releases, milestones, labels, notifications, actions/workflows, webhooks, repositories, organizations, and more from the terminal. Supports multiple Gitea instances, OAuth2 and token auth, interactive prompts, and machine-readable output (JSON/YAML/CSV/TSV/table). Use when automating Gitea workflows, managing PRs/issues from the shell, or scripting CI/CD interactions with Gitea.
license: MIT
author: Tangled <noreply@tangledgroup.com>
version: "0.14.0"
tags:
  - gitea
  - cli
  - git
  - ci-cd
  - go
category: development-tools
external_references:
  - https://gitea.com/gitea/tea
  - https://code.gitea.io/sdk/gitea
  - https://dl.gitea.com/tea/
  - https://hub.docker.com/r/gitea/tea
  - https://pkg.go.dev/code.gitea.io/tea
  - https://gitea.com/gitea/tea/src/branch/main/docs
---
## Overview
Tea is the official command-line client for Gitea. Written in Go, it interacts with one or more Gitea instances via the Gitea API (using `code.gitea.io/sdk/gitea`). It manages issues, pull requests, releases, milestones, labels, notifications, actions/workflows, webhooks, repositories, branches, organizations, and admin users.

Tea auto-detects context from the local git repository (`$PWD`), making it ideal for upstream/fork workflows where the local `main` branch tracks an upstream remote. Configuration persists in `$XDG_CONFIG_HOME/tea`.

## When to Use
- Managing Gitea issues and pull requests from the terminal
- Automating PR review, merge, or cleanup workflows
- Scripting CI/CD interactions (workflow dispatch, run logs, secrets/variables)
- Listing notifications, milestones, releases across repositories
- Creating or editing webhooks, action secrets, or repository settings
- Working with multiple Gitea instances simultaneously
- Building shell scripts that integrate with Gitea APIs

## Installation / Setup
```bash
# Homebrew (macOS, official)
brew install tea

# Go install
go install code.gitea.io/tea@latest

# Prebuilt binaries
# Download from https://dl.gitea.com/tea/

# Docker
docker run gitea/tea tea --version

# From source
git clone https://gitea.com/gitea/tea.git
cd tea && make && make install
```

## Authentication
First step: log in to a Gitea instance.

```bash
# Interactive login (prompts for auth type)
tea login add

# Token auth (fastest, works everywhere)
tea login add --url https://gitea.example.com --token <access-token>

# OAuth2 flow (Gitea 0.10+, may not work on all deployments)
tea login add --oauth

# SSH key auth (needs running ssh-agent)
tea login add --ssh-agent-key

# Basic auth (creates a token from username/password)
tea login add --user alice --password secret
```

Multiple logins are supported. Switch between them with `--login <name>` or let tea auto-detect from the git remote:

```bash
tea login list                        # show configured logins
tea login default                     # show/set default login
tea pulls --login gitea.com          # use specific login
tea pulls --remote upstream           # discover login from "upstream" remote
```

## Core Concepts
- **Repository context**: Tea reads the current directory's git remotes to determine which Gitea repo to operate on. Override with `--repo owner/name` or `--repo /path/to/local/repo`.
- **Output formats**: All list commands support `--output simple|table|csv|tsv|yaml|json`. Use `--fields` to customize columns.
- **Interactive mode**: Commands called without arguments enter interactive prompts (powered by Charm libraries).
- **Shell completion**: Generate with `tea completion bash|zsh|fish|powershell`.
- **Man page**: Hidden command `tea man` generates the full man page.

## Quick Examples
```bash
# List open issues in current repo
tea issues list

# List open PRs with custom fields
tea pr ls --fields index,title,state,author,ci

# Checkout a PR locally
tea pr checkout 42

# Create an issue
tea issue create --title "Fix typo" --description "In README.md" --labels bug

# Approve and merge a PR
tea pr approve 42
tea pr merge 42 --style squash

# View notifications across all repos
tea notifications --mine

# Open issue in browser
tea open 42

# Dispatch a CI workflow
tea actions workflows dispatch ci.yml --ref main --follow

# List action secrets
tea actions secrets list
```

## Command Reference
Tea has a large command surface. See the reference files for full coverage:

- [Reference: Issues & Pull Requests](reference/01-issues-pulls.md) — issues, pulls (create, edit, checkout, review, merge, approve, reject, clean)
- [Reference: Releases, Milestones, Labels](reference/02-releases-milestones-labels.md) — releases, milestones, labels management
- [Reference: Repositories & Organizations](reference/03-repos-orgs.md) — repos (create, fork, migrate, search, edit), organizations
- [Reference: Actions, Webhooks, Notifications](reference/04-actions-webhooks-notifications.md) — CI actions/workflows, secrets, variables, webhooks, notifications
- [Reference: Branches, Times, Comments, API](reference/05-branches-times-comments-api.md) — branches, time tracking, comments, open, clone, admin, raw API

## Advanced Topics
## Advanced Topics

- [Issues Pulls](reference/01-issues-pulls.md)
- [Releases Milestones Labels](reference/02-releases-milestones-labels.md)
- [Repos Orgs](reference/03-repos-orgs.md)
- [Actions Webhooks Notifications](reference/04-actions-webhooks-notifications.md)
- [Branches Times Comments Api](reference/05-branches-times-comments-api.md)

