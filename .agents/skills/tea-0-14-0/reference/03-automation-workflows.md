# Automation Workflows

## CI/CD with Gitea Actions

### Managing Secrets and Variables

Store CI/CD credentials as action secrets:

```bash
tea actions secrets create API_KEY          # interactive prompt for value
tea actions secrets create DB_PASS --stdin  # pipe from stdin
tea actions secrets list                    # view stored secrets
```

Set action variables (non-sensitive config):

```bash
tea actions variables set DEPLOY_ENV production
tea actions variables set API_URL https://api.example.com
tea actions variables list
```

### Workflow Runs

Monitor and manage CI runs:

```bash
# List recent runs
tea actions runs list --status failure
tea actions runs list --branch main --since 24h

# View a specific run
tea actions runs view 12345 --jobs

# Follow logs in real-time
tea actions runs logs 12345 --follow
tea actions runs logs 12345 --job 67890     # specific job

# Cancel a stuck run
tea actions runs delete 12345
```

### Workflow Dispatch (v0.14+)

Trigger `workflow_dispatch` workflows from the CLI:

```bash
# Dispatch on current branch
tea actions workflows dispatch deploy.yml

# Dispatch on specific ref with inputs
tea actions workflows dispatch deploy.yml --ref main \
  --input env=production --input version=2.0.0

# Dispatch and follow output
tea actions workflows dispatch ci.yml --ref feature/my-pr --follow
```

Example `workflow_dispatch` workflow definition:

```yaml
name: deploy
on:
  workflow_dispatch:
    inputs:
      env:
        description: "Target environment"
        required: true
        default: "staging"
      version:
        description: "Version to deploy"
        required: true

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v6
      - name: Deploy
        run: |
          echo "Deploying ${{ gitea.event.inputs.version }} to ${{ gitea.event.inputs.env }}"
```

Enable/disable workflows:

```bash
tea actions workflows enable deploy.yml
tea actions workflows disable deploy.yml --confirm
```

## Automated PR Merge on Approval

Use tea in a Gitea Actions workflow to auto-merge PRs when approved:

```yaml
name: Auto-merge on approval
on:
  pull_request_review:
    types: [submitted, dismissed]
jobs:
  approved:
    name: Approved
    if: gitea.event.review.type == 'pull_request_review_approved'
    container:
      image: docker.io/gitea/tea:latest
    runs-on: ubuntu-latest
    steps:
      - name: Configure Tea
        env:
          TEA_CREDENTIALS: ${{ secrets.TEA_CREDENTIALS }}
        run: |
          echo "$TEA_CREDENTIALS" > $HOME/.config/tea/config.yml
      - name: Rebase then fast-forward merge
        run: |
          tea pr merge --repo ${{ gitea.event.repository.full_name }} \
            --style rebase ${{ gitea.event.pull_request.number }}
  dismissed:
    name: Dismissed
    if: gitea.event.review.type == 'pull_request_review_rejected'
    runs-on: ubuntu-latest
    steps:
      - run: |
          tea pr reject --repo ${{ gitea.event.repository.full_name }} \
            ${{ gitea.event.pull_request.number }} "Dismissed"
```

## AI-Driven PR Flow

Re-trigger CI after automated changes:

```bash
# Push auto-fix, then re-trigger CI
git push origin feature/auto-fix
tea actions workflows dispatch check-and-test --ref feature/auto-fix --follow
```

## Desktop Notifications

Poll for Gitea notifications with desktop alerts:

```bash
# bash + libnotify
while :; do
  tea notifications --mine -o simple | xargs -I {} notify-send "{}"
  sleep 300
done
```

## Webhook Management

Create and manage webhooks from the CLI:

```bash
# Create a webhook for push events
tea webhooks create https://example.com/hook --events push,pull_request

# Create a Slack webhook
tea webhooks create https://hooks.slack.com/services/xxx --type slack --events push

# List and manage
tea webhooks list
tea webhooks update 1 --url https://new-url.example.com
tea webhooks delete 1 --confirm
```

Organization-level webhooks:

```bash
tea webhooks list --org myorg
tea webhooks create https://example.com/org-hook --org myorg
```

## Bulk Operations

Use machine-readable output for scripting:

```bash
# List all open issues as JSON, process with jq
tea issues list -o json | jq -r '.[] | select(.state=="open") | .index'

# Close all issues with a specific label
tea issues list --labels "duplicate" -o simple | while read id; do
  tea issues close "$id"
done

# Export PR data to CSV for analysis
tea pr list -o csv > pull-requests.csv
```

## Docker Usage

Run tea in containers for CI/CD:

```bash
# One-off command
docker run --rm -v ~/.config/tea:/root/.config/tea \
  docker.io/gitea/tea pr list --repo owner/repo

# In a workflow step
container:
  image: docker.io/gitea/tea:latest
```

The Docker image is available at `docker.io/gitea/tea` with tags matching release versions.
