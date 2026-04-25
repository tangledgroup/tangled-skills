# Extensions Guide

Comprehensive guide to the Spec Kit extension system, including installation, development, and community catalog.

## Extension Overview

Extensions add domain-specific workflows and integrations to Spec Kit. They provide:

- **Additional slash commands** - Namespaced commands like `/speckit.jira.specstoissues`
- **Hook integrations** - Automated actions at lifecycle events (before/after specify, plan, tasks, implement)
- **Configuration templates** - Project-specific configuration files
- **Custom workflows** - Domain-specific development patterns

## Built-in Extensions

### Git Extension (Auto-installed)

The Git extension is bundled with Spec Kit and provides:

**Commands:**
- `/speckit.git.initialize` - Initialize git repository
- `/speckit.git.feature` - Create feature branch
- `/speckit.git.remote` - Configure remote repository
- `/speckit.git.commit` - Commit with conventional messages
- `/speckit.git.validate` - Validate branch naming

**Hooks:**
- `before_specify`: Automatically creates git branch `NNN-feature-name`
- Validates branch naming conventions

**Configuration:**

```yaml
# .specify/extensions.yml
extensions:
  git:
    version: 0.1.0
    enabled: true
    registered_commands:
      - speckit.git.initialize
      - speckit.git.feature
      - speckit.git.remote
      - speckit.git.commit
      - speckit.git.validate
```

**Environment Variables:**

| Variable | Description | Default |
|----------|-------------|---------|
| `GIT_BRANCH_NAME` | Override auto-generated branch name | Auto-generated |

---

## Installing Extensions

### From Community Catalog

**List available extensions:**

```bash
# Search catalog
specify extension search <keyword>

# List all extensions
specify extension list
```

**Install extension:**

```bash
# Install by ID
specify extension install jira

# Install specific version
specify extension install jira@1.2.3

# From custom catalog URL
specify extension install --catalog https://example.com/catalog.json linear
```

**Installation process:**
1. Downloads extension package (ZIP or from git repository)
2. Validates manifest (`extension.yml`)
3. Checks compatibility with Spec Kit version
4. Registers commands with AI agent
5. Updates `.specify/extensions.yml`

**Verify installation:**

```bash
# List installed extensions
specify extension list --installed

# Check registered commands
ls -la .claude/commands/speckit.*
```

### From Local Directory

**Development/testing scenario:**

```bash
# Install from local path
specify extension install /path/to/local/extension
```

### From Git Repository

**Custom extensions:**

```bash
# Install from git URL
specify extension install git+https://github.com/user/custom-extension.git@v1.0.0
```

---

## Managing Extensions

### List Extensions

```bash
# All available extensions (from active catalogs)
specify extension list

# Installed extensions only
specify extension list --installed

# Filter by tag
specify extension list --tag "ci-cd"

# Search by keyword
specify extension search "jira"
```

### Uninstall Extension

```bash
# Remove extension
specify extension uninstall jira

# Keep configuration files
specify extension uninstall jira --keep-config
```

**What gets removed:**
- Extension directory (`.specify/extensions/jira/`)
- Registered commands (`.claude/commands/speckit.jira.*`)
- Hook registrations

**What stays (with `--keep-config`):**
- Configuration files created by extension
- Custom modifications to extension files

### Update Extension

```bash
# Update specific extension
specify extension update jira

# Update all extensions
specify extension update --all

# Update to latest version
specify extension update jira --latest
```

### Extension Catalogs

**Default catalogs:**

| Catalog | URL | Priority | Install Allowed |
|---------|-----|----------|-----------------|
| Official | `https://github.com/github/spec-kit/extensions/catalog.official.json` | 1 | Yes |
| Community | `https://github.com/github/spec-kit/extensions/catalog.community.json` | 2 | Yes |

**Add custom catalog:**

```bash
# Add catalog
specify extension catalog add my-catalog https://example.com/catalog.json --priority 3

# List catalogs
specify extension catalog list

# Remove catalog
specify extension catalog remove my-catalog
```

**Catalog configuration:**

```json
{
  "catalogs": [
    {
      "url": "https://example.com/catalog.json",
      "name": "my-catalog",
      "priority": 3,
      "install_allowed": true,
      "description": "Custom enterprise extensions"
    }
  ]
}
```

Stored in `.specify/catalogs.json`

---

## Extension Manifest Schema

File: `extension.yml`

```yaml
schema_version: "1.0"

extension:
  id: jira                    # Required, pattern: ^[a-z0-9-]+$
  name: Jira Integration      # Required, human-readable name
  version: 1.2.3              # Required, semantic version (X.Y.Z)
  description: Sync specs to Jira issues  # Required, <200 chars
  author: Jane Doe <jane@example.com>     # Required
  repository: https://github.com/example/jira-extension  # Required, valid URL
  license: MIT                # Required (e.g., "MIT", "Apache-2.0")
  homepage: https://jira-extension.example.com  # Optional

requires:
  speckit_version: ">=0.4.0"  # Required, version specifier
  tools:                       # Optional
    - name: jira-cli
      version: ">=3.0.0"
      required: false

provides:
  commands:                    # Required, at least one command
    - name: speckit.jira.specstoissues
      file: commands/speckit.jira.specstoissues.md
      description: Convert specifications to Jira issues
      aliases:
        - speckit.jira.sync-specs

    - name: speckit.jira.sync
      file: commands/speckit.jira.sync.md
      description: Sync task status with Jira

  config:                      # Optional
    - name: jira-config.yml
      template: configs/jira-config.yml.template
      description: Jira instance configuration
      required: true

hooks:                         # Optional
  after_specify:
    - command: speckit.jira.specstoissues
      optional: true
      prompt: "Create Jira issue from spec?"
      description: Automatically create Jira issue
      condition: null

tags:                          # Optional, 2-10 recommended
  - jira
  - project-management
  - integration

defaults:                      # Optional
  jira_instance: "company.atlassian.net"
  auto_create_issues: true
```

### Field Specifications

**`extension.id`:**
- Pattern: `^[a-z0-9-]+$`
- Examples: `jira`, `linear`, `azure-devops`
- Invalid: `Jira`, `my_extension`, `extension.id`

**`extension.version`:**
- Format: Semantic versioning (X.Y.Z)
- Examples: `1.0.0`, `0.9.5`, `2.1.3`
- Invalid: `v1.0`, `1.0`, `1.0.0-beta`

**`requires.speckit_version`:**
- Format: Version specifier
- Examples:
  - `>=0.4.0` - Any version 0.4.0 or higher
  - `>=0.4.0,<2.0.0` - Version 0.4.x to 1.x
  - `==0.6.1` - Exactly 0.6.1

**`provides.commands[].name`:**
- Pattern: `^speckit\.[a-z0-9-]+\.[a-z0-9-]+$`
- Format: `speckit.{extension-id}.{command-name}`
- Examples: `speckit.jira.specstoissues`, `speckit.linear.sync`

**`hooks`:**
- Keys: Event names (`before_specify`, `after_plan`, etc.)
- Values: Array of hook configurations

---

## Community Extensions Catalog

### Project Management Integrations

| Extension | ID | Description | Version |
|-----------|-----|-------------|---------|
| Jira Integration | `jira` | Sync specs to Jira issues, bidirectional status updates | 1.2.3 |
| Linear Integration | `linear` | Create Linear issues from specifications | 0.8.1 |
| Azure DevOps | `azure-devops` | Integrate with Azure DevOps work items | 1.0.0 |
| GitHub Projects | `github-projects` | Manage GitHub Projects from specs | 0.5.2 |

### Documentation Tools

| Extension | ID | Description | Version |
|-----------|-----|-------------|---------|
| Confluence | `confluence` | Export specifications to Confluence pages | 1.1.1 |
| Notion | `notion` | Sync specs to Notion workspace | 0.6.0 |
| DocGuard | `docguard` | Enforce documentation quality standards | 0.9.11 |

### Quality & Security

| Extension | ID | Description | Version |
|-----------|-----|-------------|---------|
| Security Review | `security-review` | Automated security analysis hooks | 1.1.1 |
| Memorylint | `memorylint` | Context memory optimization for AI agents | 0.3.0 |
| SpecTest | `spec-test` | Specification testing and validation | 0.2.1 |
| Verify Tasks | `verify-tasks` | Task verification before implementation | 0.4.0 |

### CI/CD Integration

| Extension | ID | Description | Version |
|-----------|-----|-------------|---------|
| CI Guard | `ci-guard` | Gate implementations behind CI checks | 0.7.0 |
| PR Bridge | `pr-bridge` | Auto-generate PRs from completed features | 0.5.1 |
| Status Report | `status-report` | Generate progress reports from task status | 0.3.2 |

### Workflow Enhancements

| Extension | ID | Description | Version |
|-----------|-----|-------------|---------|
| Bugfix Workflow | `bugfix-workflow` | Streamlined workflow for bug fixes | 0.4.0 |
| Worktree Isolation | `worktree-isolation` | Use git worktrees for feature isolation | 0.2.0 |
| Checkpoint | `checkpoint` | Save implementation checkpoints | 0.6.1 |
| Optimize | `optimize` | Performance optimization suggestions | 0.3.0 |

### Domain-Specific

| Extension | ID | Description | Version |
|-----------|-----|-------------|---------|
| Confluence | `confluence` | Atlassian Confluence integration | 1.1.1 |
| Fleet | `fleet` | Device management workflows | 1.1.0 |
| MAQA Suite | `maqa-*` | Model-assisted quality assurance (7 extensions) | 1.0.0 |
| Spec Diagram | `spec-diagram` | Generate diagrams from specifications | 0.4.0 |

### Full Catalog

Browse complete catalog:
- **GitHub Repository**: https://github.com/github/spec-kit/tree/main/extensions
- **Community Catalog JSON**: https://github.com/github/spec-kit/blob/main/extensions/catalog.community.json

---

## Developing Extensions

### Extension Scaffold

**Create new extension:**

```bash
# Use scaffold preset
specify init my-extension --preset scaffold --ai claude
```

**Directory structure:**

```
my-extension/
├── extension.yml              # Manifest file
├── commands/
│   ├── speckit.myext.command1.md
│   └── speckit.myext.command2.md
├── configs/
│   └── config-template.yml    # Configuration templates
├── scripts/
│   ├── bash/
│   │   └── helper.sh
│   └── powershell/
│       └── helper.ps1
└── README.md                  # Extension documentation
```

### Command Development

**Create slash command:**

```markdown
---
description: "Custom command for my extension"
---

## User Input

```text
$ARGUMENTS
```

## Execution

1. Read configuration from `.specify/extensions/myext/config.yml`
2. Process user input
3. Generate output artifacts

## Output

- Creates `specs/<feature>/myext-output.md`
- Updates extension state
```

**Register command in manifest:**

```yaml
provides:
  commands:
    - name: speckit.myext.command1
      file: commands/speckit.myext.command1.md
      description: Custom command for my extension
```

### Hook Development

**Implement hook:**

```yaml
hooks:
  after_specify:
    - command: speckit.myext.process-spec
      optional: true
      prompt: "Process specification with MyExt?"
      description: Apply MyExt transformations to spec
      condition: "spec_contains('API')"  # Optional condition
```

**Hook command:**

```markdown
---
description: "Process spec with MyExt"
---

## Execution

1. Read current spec from `SPEC_FILE`
2. Apply MyExt transformations
3. Update spec in place
4. Report changes made
```

### Testing Extensions

**Self-test extension:**

```bash
# Install self-test preset
specify init test-project --preset self-test --ai claude

# Run tests
cd test-project
/speckit.selftest.validate
```

**Manual testing:**

```bash
# Install extension in test project
specify extension install /path/to/my-extension

# Verify commands registered
ls -la .claude/commands/speckit.myext.*

# Test each command manually
/speckit.myext.command1 test argument
```

---

## Publishing Extensions

### Preparation

1. **Complete manifest** with all required fields
2. **Write README.md** with:
   - Extension overview and use cases
   - Installation instructions
   - Configuration options
   - Command reference
   - Examples
3. **Test thoroughly** in multiple projects
4. **Set version** to `1.0.0` for initial release

### Submission Process

**Option 1: GitHub Pull Request**

1. Fork https://github.com/github/spec-kit
2. Add extension to `extensions/catalog.community.json`:

   ```json
   {
     "id": "myext",
     "name": "My Extension",
     "version": "1.0.0",
     "description": "Extension description",
     "author": "Your Name <email@example.com>",
     "repository": "https://github.com/yourusername/myext-extension",
     "license": "MIT",
     "tags": ["tag1", "tag2"],
     "download_url": "https://github.com/yourusername/myext-extension/releases/download/v1.0.0/myext.zip"
   }
   ```

3. Submit PR to main repository
4. Wait for maintainer review and merge

**Option 2: Issue Template**

Use the extension submission issue template:

```markdown
---
name: Extension Submission
about: Submit your extension to the community catalog
title: "Add MyExt to community catalog"
labels: ["extension-submission"]
---

**Extension ID**: myext

**Name**: My Extension

**Version**: 1.0.0

**Description**: <200 character description>

**Repository URL**: https://github.com/username/myext-extension

**License**: MIT

**Tags**: tag1, tag2, tag3

**Download URL**: https://.../myext.zip

**Author**: Your Name <email@example.com>

**Documentation**: Link to extension README
```

### Packaging Extension

**Create distribution package:**

```bash
# In extension directory
zip -r myext-1.0.0.zip \
  extension.yml \
  commands/ \
  configs/ \
  scripts/ \
  README.md
```

**Upload to release:**
- GitHub Releases (recommended)
- Other CDN or hosting service
- Ensure download URL is publicly accessible

---

## Extension Best Practices

### Command Naming

✅ **Good:**
- `speckit.jira.specstoissues`
- `speckit.linear.sync`
- `speckit.confluence.export`

❌ **Bad:**
- `speckit.jira.CreateIssues` (uppercase)
- `jira.specstoissues` (missing speckit prefix)
- `speckit.create_issues` (underscore instead of hyphen)

### Hook Design

✅ **Good:**
- Optional hooks for non-critical operations
- Clear prompts explaining what hook does
- Idempotent operations (safe to run multiple times)

❌ **Bad:**
- Mandatory hooks that block workflow
- Hooks with side effects not clearly documented
- Hooks that modify spec without user confirmation

### Error Handling

✅ **Good:**

```markdown
## Error Handling

If Jira API returns 401:
ERROR "Jira authentication failed. Please check JIRA_TOKEN environment variable."

If specification missing required fields:
ERROR "Specification incomplete. Run /speckit.clarify to resolve ambiguities."
```

❌ **Bad:**
- Silent failures
- Generic error messages without remediation steps

### Configuration Management

✅ **Good:**
- Provide configuration templates
- Document all configuration options
- Use sensible defaults

❌ **Bad:**
- Hardcoded values
- Required config with no template provided

---

## Troubleshooting Extensions

### Extension Not Installing

**Symptom:** `specify extension install jira` fails

**Checks:**
1. Verify catalog URL is accessible: `curl https://github.com/github/spec-kit/extensions/catalog.community.json`
2. Check Spec Kit version compatibility with extension requirements
3. Review `.specify/catalogs.json` for catalog configuration

### Commands Not Registered

**Symptom:** Extension installed but commands not showing up

**Solutions:**
1. Verify command files exist: `ls -la .claude/commands/speckit.jira.*`
2. Check `.specify/extensions.yml` for registration
3. Restart AI agent to reload commands
4. Reinstall extension: `specify extension uninstall jira && specify extension install jira`

### Hook Not Executing

**Symptom:** Hook configured but not running

**Checks:**
1. Verify hook enabled in `.specify/extensions.yml`: `enabled: true`
2. Check hook condition (if present) evaluates to true
3. Review command logs for errors
4. Test hook command manually: `/speckit.jira.specstoissues`

### Version Conflict

**Symptom:** Extension requires different Spec Kit version

**Solutions:**
1. Upgrade Spec Kit: `specify init --here --force --ai claude`
2. Downgrade extension to compatible version
3. Check for updated extension version that supports current Spec Kit

---

## Next Steps

- Review [Command Reference](references/03-command-reference.md) for hook integration details
- Explore [AI Agent Support](references/05-ai-agents.md) for agent-specific command formats
- Browse [Community Extensions](https://github.com/github/spec-kit/tree/main/extensions) for inspiration
