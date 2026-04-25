# GitHub Projects

> **Source:** https://cli.github.com/manual/gh_project
> **Loaded from:** SKILL.md (via progressive disclosure)

GitHub Projects provides project management boards. The `gh project` commands interact with the Projects API (beta).

## Project Management

```bash
# List your projects
gh project list

# Create a new project
gh project create --title "Roadmap Q1" --body "Quarterly planning"

# View a project
gh project view 123
gh project view 123 --web

# Edit a project
gh project edit 123 --title "Updated Title"

# Close or delete
gh project close 123
gh project delete 123
```

## Fields

Projects use configurable fields (text, number, single-select, date, iteration, etc.).

```bash
# List available field types
gh project field-list 123

# Create a field
gh project field-create 123 single-select --name "Priority" --options "High,Medium,Low"

# Delete a field
gh project field-delete 123 <field-id>
```

## Items

Items are the entries in a project (linked to issues, PRs, or standalone).

```bash
# List items
gh project item-list 123

# Create an item
gh project item-create 123 --title "Task name" --body "Description"

# Add existing issue/PR to project
gh project item-add 123 --owner owner --repo repo --number 456

# Edit an item
gh project item-edit 123 <item-id> --field "Status" --value "In Progress"

# Archive or delete
gh project item-archive 123 <item-id>
gh project item-delete 123 <item-id>
```

## Repository Linking

Link repositories to projects so issues and PRs appear automatically.

```bash
# Link a repository
gh project link 123 --repo owner/repo

# Unlink
gh project unlink 123 --repo owner/repo
```

## Templates and Copying

```bash
# Mark as template
gh project mark-template 123

# Copy from template or another project
gh project copy <source-id> --title "New Project"
```
