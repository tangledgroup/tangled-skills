# GitHub Actions

## Workflow Management

List, enable, and disable CI/CD workflows:

```bash
# List all workflows
gh workflow list

# View workflow details
gh workflow view ci.yml

# Disable a workflow
gh workflow disable ci.yml

# Enable a workflow
gh workflow enable ci.yml
```

## Run Management

Manage GitHub Actions workflow runs:

```bash
# List recent runs
gh run list

# View a specific run
gh run view 12345

# Watch a run (follow logs in real-time)
gh run watch 12345

# Cancel a running workflow
gh run cancel 12345

# Rerun a failed job
gh run rerun 12345 --job build

# Rerun all failed jobs
gh run rerun 12345

# Delete a workflow run
gh run delete 12345

# Download artifacts from a run
gh run download 12345

# Download a specific artifact
gh run download 12345 --name my-artifact
```

## Secrets

Manage repository and organization secrets for workflow authentication:

```bash
# List repository secrets
gh secret list

# Set a repository secret
gh secret set MY_API_KEY

# Read secret value from stdin
echo "sk-12345" | gh secret set MY_API_KEY

# Set an organization secret
gh secret set MY_API_KEY --org myorg

# Set an environment secret
gh secret set MY_API_KEY --env production

# Delete a secret
gh secret delete MY_API_KEY

# Set a repository-level secret for a specific repo
gh secret set MY_API_KEY --repo owner/repo
```

## Variables

Manage repository and organization variables (non-sensitive configuration):

```bash
# List variables
gh variable list

# Get a variable value
gh variable get DEPLOY_ENV

# Set a variable
gh variable set DEPLOY_ENV --body production

# Set an organization variable
gh variable set APP_URL --org myorg --body https://app.example.com

# Delete a variable
gh variable delete DEPLOY_ENV
```

## Cache

Manage GitHub Actions dependency caches:

```bash
# List caches
gh cache list

# Filter by branch ref
gh cache list --ref refs/heads/main

# Sort by size
gh cache list --sort size_in_bytes

# Delete a specific cache
gh cache delete <cache-id>

# Delete all caches
gh cache delete --all

# Delete all caches for a branch
gh cache delete --all --ref refs/heads/main
```

## Repository Context

All GitHub Actions commands accept `-R OWNER/REPO` to target a specific repository:

```bash
# List runs for a specific repo
gh run list --repo owner/repo

# Set a secret for a specific repo
gh secret set MY_KEY --repo owner/repo
```

## Status Command

Get an overview of your GitHub activity and pending items:

```bash
# Show status summary (PRs, issues, notifications)
gh status

# Exclude specific repositories
gh status -e cli/cli -e cli/go-gh

# Limit to a single organization
gh status -o myorg
```

## Agent Tasks (v2.91)

GitHub's built-in AI agent task management:

```bash
# List recent agent tasks
gh agent-task list

# Create a new agent task
gh agent-task create "Improve the performance of the data processing pipeline"

# Create from file
gh agent-task create --from-file task.md

# View agent task details
gh agent-task view 12345abc-12345-12345-12345-12345abc

# View tasks for a pull request
gh agent-task view 123

# Follow agent session logs
gh agent-task view 123 --follow
```
