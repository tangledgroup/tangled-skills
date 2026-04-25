# Command Reference

> **Source:** https://cli.github.com/manual/
> **Loaded from:** SKILL.md (via progressive disclosure)

Complete listing of all `gh` commands and subcommands available in v2.91.0.

## agent-task

Manage AI agent tasks on GitHub.

- `gh agent-task create` — Create a new agent task
- `gh agent-task list` — List agent tasks
- `gh agent-task view` — View an agent task

## alias

Create and manage command aliases.

- `gh alias delete <name>` — Remove an alias
- `gh alias import` — Import aliases from stdin
- `gh alias list` — List all aliases
- `gh alias set <name> <value>` — Create or update an alias

## api

Make authenticated HTTP requests to the GitHub API.

```bash
gh api <endpoint> [flags]
```

- Endpoint is a REST v3 path or `graphql` for GraphQL v4
- `{owner}`, `{repo}`, `{branch}` placeholders are auto-populated from the current repo
- Default method is GET (POST if fields are added)
- `-f key=value` — Add static string parameters
- `-F key=value` — Magic type conversion (true/false/null/numbers become JSON types)
- `--method <METHOD>` — Override HTTP method
- `-h name` / `--header name` — Add custom headers
- `-i` — Include HTTP response headers in output
- `--jq <filter>` — Filter JSON output with jq syntax
- `--template <tmpl>` — Format output with Go template
- `-p <preview>` / `--preview <preview>` — Opt into API previews

```bash
# GET request
gh api repos/{owner}/{repo}/issues

# POST with fields
gh api repos/{owner}/{repo}/issues -f title="Bug fix" -f body="Fixed the bug"

# GraphQL query
gh api graphql -f query='query{viewer{login,name}}'

# Raw JSON input
gh api repos/{owner}/{repo}/issues/123/comments --input -
```

## attestation

Verify and download software supply-chain attestations.

- `gh attestation download` — Download attestation bundles
- `gh attestation trusted-root` — Display the Sigstore public good trusted root
- `gh attestation verify` — Verify artifact provenance against GitHub repository attestations

## auth

Authenticate gh and git with GitHub.

- `gh auth login` — Authenticate to a GitHub host
- `gh auth logout` — Remove stored credentials
- `gh auth refresh` — Refresh expired tokens
- `gh auth setup-git` — Configure git to use gh for authentication
- `gh auth status` — Display authentication state
- `gh auth switch` — Switch between authenticated accounts
- `gh auth token` — Write the authentication token to stdout

## browse

Open the repository in the web browser.

```bash
gh browse                              # open current repo
gh browse --path docs/README.md        # open specific file path
gh browse -R owner/repo                # specify repo
```

## cache

Manage Actions caches.

- `gh cache delete` — Delete a cache entry
- `gh cache list` — List repository cache entries

## codespace

Connect to and manage GitHub Codespaces (alias: `gh cs`).

- `gh codespace code` — Generate VS Code settings for remote connection
- `gh codespace cp` — Copy files to/from a codespace
- `gh codespace create` — Create a new codespace
- `gh codespace delete` — Delete a codespace
- `gh codespace edit` — Edit codespace configuration
- `gh codespace jupyter` — Open Jupyter in a codespace
- `gh codespace list` — List your codespaces
- `gh codespace logs` — Show codespace logs
- `gh codespace ports` — Manage forwarded ports
- `gh codespace ports forward <local>:<remote>` — Forward a port
- `gh codespace ports visibility` — Manage port visibility
- `gh codespace rebuild` — Rebuild a codespace from scratch
- `gh codespace ssh` — SSH into a codespace
- `gh codespace stop` — Stop a running codespace
- `gh codespace view` — Open a codespace in the browser

See [GitHub Codespaces](02-codespaces.md) for detailed usage.

## completion

Generate shell completion scripts.

```bash
gh completion -s bash   >> ~/.bashrc
gh completion -s zsh   >> ~/.zshrc
gh completion -s fish  > ~/.config/fish/completions/gh.fish
```

## config

Display or change configuration settings.

- `gh config clear-cache` — Clear cached data
- `gh config get <key>` — Get a configuration value
- `gh config list` — List all configuration settings
- `gh config set <key> <value>` — Set a configuration value

Configurable settings: `git_protocol`, `editor`, `prompt`, `prefer_editor_prompt`, `pager`, `http_unix_socket`, `browser`, `color_labels`, `accessible_colors`, `accessible_prompter`, `spinner`, `telemetry`.

## copilot

Manage GitHub Copilot associations and suggestions.

- `gh copilot` — Subcommand group for Copilot features

## extension

Manage gh extensions (alias: `gh ext`, `gh extensions`).

- `gh extension browse` — Open extensions marketplace in browser
- `gh extension create <name>` — Create a new extension
- `gh extension exec <name>` — Execute an extension (use when name conflicts with core command)
- `gh extension install <repo>` — Install an extension
- `gh extension list` — List installed extensions
- `gh extension remove <name>` — Remove an extension
- `gh extension search <query>` — Search for extensions
- `gh extension upgrade` — Upgrade all extensions

Extensions are repositories with names starting with `gh-` containing a matching executable. gh checks for updates every 24 hours and displays upgrade notices.

## gist

Work with GitHub gists.

- `gh gist clone <gist-id>` — Clone a gist locally
- `gh gist create [file...]` — Create a new gist
- `gh gist delete <gist-id>` — Delete a gist
- `gh gist edit <gist-id>` — Edit a gist
- `gh gist list` — List your gists
- `gh gist rename <gist-id> <name>` — Rename a gist
- `gh gist view [gist-id]` — View a gist

```bash
gh gist create script.py -d "My Python script"
gh gist create --public README.md
```

## gpg-key

Manage GPG keys.

- `gh gpg-key add [file]` — Add a GPG public key
- `gh gpg-key delete <key-id>` — Delete a GPG key
- `gh gpg-key list` — List your GPG keys

## help

Access gh documentation and reference material.

- `gh help` — Show help for gh
- `gh help <command>` — Show help for a specific command
- `gh help environment` — List environment variables
- `gh help exit-codes` — List exit codes
- `gh help formatting` — Explain output formatting options
- `gh help mintty` — Mintty-specific notes (Windows)
- `gh help reference` — Full command reference
- `gh help telemetry` — Telemetry information

## issue

Work with GitHub issues.

**General commands:**

- `gh issue create` — Create a new issue
- `gh issue list` — List issues in a repository
- `gh issue status` — View your issue status digest

**Targeted commands:**

- `gh issue close <number>` — Close an issue
- `gh issue comment <number>` — Leave or view comments
- `gh issue delete <number>` — Delete an issue
- `gh issue develop` — Show issues and their code change development
- `gh issue edit <number>` — Edit an issue
- `gh issue lock <number>` — Lock an issue's conversation
- `gh issue pin <number>` — Pin an issue
- `gh issue reopen <number>` — Reopen an issue
- `gh issue transfer <number> <owner/repo>` — Transfer to another repository
- `gh issue unlock <number>` — Unlock an issue
- `gh issue unpin <number>` — Unpin an issue
- `gh issue view [number]` — View an issue

```bash
gh issue list --label bug --state open --limit 10
gh issue create --title "Fix crash" --body "Steps to reproduce..." --assignee @me
gh issue view 123 --web  # open in browser
gh issue create --repo owner/repo --label "enhancement"
```

## label

Work with GitHub labels.

- `gh label clone <source-repo>` — Clone labels from another repository
- `gh label create <name> [<color>]` — Create a new label
- `gh label delete <name>` — Delete a label
- `gh label edit <name>` — Edit a label
- `gh label list` — List labels in a repository

## licenses

Interact with GitHub license templates.

- `gh licenses clone` — Clone the licenses repository
- `gh licenses list` — List available license templates
- `gh licenses view <license>` — View a specific license template

## org

Work with GitHub organizations.

- `gh org list` — List organizations you belong to

## pr

Work with GitHub pull requests.

**General commands:**

- `gh pr create` — Create a new PR
- `gh pr list` — List PRs in a repository
- `gh pr status` — View PR status digest

**Targeted commands:**

- `gh pr checkout <number>` — Checkout a PR locally
- `gh pr checks` — View CI check status for a PR
- `gh pr close <number>` — Close a PR
- `gh pr comment <number>` — Leave or view comments
- `gh pr create --fill` — Auto-fill title and body from commits
- `gh pr diff [number]` — View PR diff
- `gh pr edit <number>` — Edit a PR
- `gh pr lock <number>` — Lock conversation
- `gh pr merge <number>` — Merge a PR (`--squash`, `--rebase`, `--merge`)
- `gh pr ready <number>` — Mark draft PR as ready for review
- `gh pr reopen <number>` — Reopen a closed PR
- `gh pr revert <number>` — Revert a merged PR
- `gh pr review <number>` — Review a PR (`--approve`, `--comment`, `--changes-requested`)
- `gh pr unlock <number>` — Unlock conversation
- `gh pr update-branch <number>` — Update branch to match base
- `gh pr view [number]` — View a PR

```bash
gh pr create --title "Fix auth" --body "Resolves #123" --reviewer alice,bob
gh pr checkout 353          # fetch and switch to PR branch
gh pr review --approve      # approve current branch's PR
gh pr merge --squash --delete-branch
gh pr list --state merged --author me --json number,title,mergedAt
```

## preview

Access preview (experimental) features.

- `gh preview` — List available preview commands

## project

Work with GitHub Projects (beta).

- `gh project close` — Close a project
- `gh project copy` — Copy a project
- `gh project create` — Create a new project
- `gh project delete` — Delete a project
- `gh project edit` — Edit a project
- `gh project field-create` — Create a project field
- `gh project field-delete` — Delete a project field
- `gh project field-list` — List project fields
- `gh project item-add` — Add an item to a project
- `gh project item-archive` — Archive a project item
- `gh project item-create` — Create a project item
- `gh project item-delete` — Delete a project item
- `gh project item-edit` — Edit a project item
- `gh project item-list` — List project items
- `gh project link` — Link a repository to a project
- `gh project list` — List projects
- `gh project mark-template` — Mark a project as a template
- `gh project unlink` — Unlink a repository from a project
- `gh project view` — View a project

See [GitHub Projects](03-projects.md) for detailed usage.

## prompter

Access the interactive prompter (preview).

- `gh preview prompter` — Interactive command builder

## release

Work with GitHub releases.

- `gh release create <tag>` — Create a new release
- `gh release delete <tag>` — Delete a release
- `gh release delete-asset <tag> <name>` — Delete a release asset
- `gh release download <tag>` — Download release assets
- `gh release edit <tag>` — Edit a release
- `gh release list` — List releases
- `gh release upload <tag> <file...>` — Upload assets to a release
- `gh release verify <digest>` — Verify release signature
- `gh release verify-asset <tag> <name>` — Verify an asset's signature
- `gh release view [tag]` — View a release

```bash
gh release create v1.0.0 --title "v1.0" --notes "Stable release"
gh release create v1.0.0 --generate-notes  # auto-generate from commits
gh release upload v1.0.0 bin/linux-amd64.bin
gh release download v1.0.0 -p "*.tar.gz" -D ./releases
```

## repo

Work with GitHub repositories.

**General commands:**

- `gh repo create` — Create a new repository
- `gh repo list` — List repositories

**Targeted commands:**

- `gh repo archive` — Archive a repository
- `gh repo autolink` — Manage autolink references
- `gh repo clone <repo>` — Clone a repository locally
- `gh repo delete` — Delete a repository
- `gh repo deploy-key` — Manage deploy keys (`add`, `delete`, `list`)
- `gh repo edit` — Edit repository settings
- `gh repo fork` — Fork a repository
- `gh repo gitignore` — View or list gitignore templates (`list`, `view`)
- `gh repo license` — View or list license templates (`list`, `view`)
- `gh repo rename <name>` — Rename a repository
- `gh repo set-default [<repo>]` — Set the default repository
- `gh repo sync` — Sync a fork with upstream
- `gh repo unarchive` — Unarchive a repository
- `gh repo view [repo]` — View a repository

```bash
gh repo create my-app --private --source=. --remote=origin
gh repo clone owner/repo -- --depth 1
gh repo fork cli/cli --clone=true
gh repo sync --commit <sha>
gh repo view --web
```

## ruleset

Work with repository rulesets.

- `gh ruleset check <name> <branch>` — Check if a branch matches a ruleset
- `gh ruleset list` — List rulesets
- `gh ruleset view <name>` — View a ruleset

## run

Manage GitHub Actions workflow runs.

- `gh run cancel <run-id>` — Cancel a workflow run
- `gh run delete <run-id>` — Delete a workflow run
- `gh run download <run-id>` — Download artifacts from a run
- `gh run list` — List workflow runs
- `gh run rerun <run-id>` — Rerun a failed workflow
- `gh run view [run-id]` — View a workflow run
- `gh run watch <run-id>` — Watch a run until completion

```bash
gh run list --workflow=ci.yml --status=success
gh run view --log 1234567890
gh run watch 1234567890   # poll until complete
gh run rerun 1234567890 --failed
```

## search

Search across all of GitHub.

- `gh search code` — Search code
- `gh search commits` — Search commits
- `gh search issues` — Search issues
- `gh search prs` — Search pull requests
- `gh search repos` — Search repositories

```bash
gh search issues --label bug --state open --limit 20
gh search prs --author me --merged --json number,title,mergedAt
gh search code "TODO" --language python --repo owner/repo
gh search repos --topic rust --stars=">1000" --sort stars
```

**Excluding results:** Use `--` before the query to prevent hyphen interpretation as a flag:

```bash
gh search issues -- "query -label:wontfix"
```

## secret

Manage secrets for GitHub Actions, Dependabot, and Codespaces. Secrets can be set at repository, organization, or environment level.

- `gh secret delete <name>` — Delete a secret
- `gh secret list` — List secrets
- `gh secret set <name>` — Create or update a secret

```bash
gh secret set MY_KEY --body "value" --repo owner/repo
gh secret set DEPLOY_TOKEN --visibility private --org myorg
echo "secret-value" | gh secret set MY_KEY --stdin
gh secret list -R owner/repo
```

## skill

Manage AI skills (preview).

- `gh skill install` — Install a skill
- `gh preview publish` — Publish a skill
- `gh preview search` — Search for skills
- `gh preview update` — Update a skill

## ssh-key

Manage SSH keys.

- `gh ssh-key add [file]` — Add an SSH public key
- `gh ssh-key delete <key-id>` — Delete an SSH key
- `gh ssh-key list` — List your SSH keys

## status

Display combined gh and git status.

```bash
gh status
```

Shows current repository, branch, associated PR, CI checks, and notifications.

## variable

Manage variables for GitHub Actions and Dependabot. Variables can be set at repository, environment, or organization level.

- `gh variable delete <name>` — Delete a variable
- `gh variable get <name>` — Get a variable value
- `gh variable list` — List variables
- `gh variable set <name>` — Create or update a variable

```bash
gh variable set APP_ENV --body production --repo owner/repo
gh variable list -R owner/repo
```

## watch

Manage watched repositories and organizations.

- `gh watch` — Watch the current repository
- `gh watch --has-notification` — Only show items with notifications
- `gh watch --repo-owner <owner>` — Filter by repository owner

## workflow

Manage GitHub Actions workflows.

- `gh workflow disable <name>` — Disable a workflow
- `gh workflow enable <name>` — Enable a workflow
- `gh workflow list` — List workflows
- `gh workflow run <name>` — Trigger a workflow
- `gh workflow view <name>` — View a workflow

```bash
gh workflow list --state active
gh workflow run ci.yml --ref main --field "env=staging"
gh workflow disable nightly-build.yml
```
