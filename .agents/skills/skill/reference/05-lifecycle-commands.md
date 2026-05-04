# Lifecycle Commands

## Contents
- Write Skill
- Update Skill
- Improve Skill
- Remove Skill
- Upload to GitHub
- Download from GitHub

The `skill` meta-skill supports six lifecycle commands. Each is a distinct workflow an agent should recognize and execute.

## Write Skill

Create a new skill from scratch. Follow the **Generation Workflow** (Steps 0–8 in SKILL.md) in full. The user provides:
- Project/tool name and version
- At least one source (URL, filesystem path, or both)
- Optional: request for scripts/assets

## Update Skill

Update an existing skill for a new upstream version. Step 0 of the Generation Workflow detects this automatically when the name already exists. Key rules:
- Read the existing SKILL.md first — preserve structure and working sections
- Crawl new sources, diff against old content
- Create a **new versioned directory** — never overwrite the old one (e.g., `curl-8-19-0` → `curl-8-20-0`)
- Update the `version` field in YAML header to the new version
- After both are written, run `bash scripts/gen-skill-list.sh`

## Improve Skill

Improve an existing skill's quality without changing its version. This is a content quality pass, not a version update. Common improvements:
- Fix factual errors or outdated information
- Add missing sections (e.g., "When to Use", code examples)
- Improve description specificity (apply the Description Formula)
- Split monolithic SKILL.md into reference files if it exceeds 300 lines
- Fix broken internal links
- Remove redundant content that the agent already knows

Run the validation checklist (reference/03-validation-checklist.md) after improvements.

## Remove Skill

Delete a skill from the local skills directory:

```bash
# Remove the skill directory entirely
rm -r .agents/skills/<skill-name>/

# Regenerate the README skills table
bash scripts/gen-skill-list.sh
```

Or use the helper script:

```bash
bash scripts/remove-skill.sh <skill-name>
```

This removes the directory and regenerates the README table in one step.

## Upload to GitHub

Push local skill changes to the tangled-skills GitHub repository. The `git` skill covers detailed git operations; use these commands for the standard upload workflow:

```bash
# Stage all skill changes
git add .agents/skills/

# Commit with a Conventional Commits message
git commit -m "feat(skills): add <skill-name> v<version>"
# Or for updates:
git commit -m "chore(skills): update <skill-name> to v<version>"
# Or for improvements:
git commit -m "fix(skills): improve <skill-name> content"

# Push to remote
git push origin main
```

Or use the helper script:

```bash
bash scripts/upload-skills.sh
```

This stages `.agents/skills/` and `README.md`, commits with an auto-generated conventional commit message based on changed files, and pushes to `origin main`.

## Download from GitHub

Fetch the latest skills from the tangled-skills repository. This is the same command documented in README.md:

```bash
mkdir -p .agents/skills && \
curl -L https://github.com/tangledgroup/tangled-skills/archive/refs/heads/main.tar.gz | \
tar -xz --strip-components=3 -C .agents/skills tangled-skills-main/.agents/skills
```

Or use the helper script:

```bash
bash scripts/download-skills.sh
```

**Merge behavior:** Download overwrites existing skills with the same name. To preserve local modifications, back up before downloading:

```bash
cp -r .agents/skills/. .agents/skills-backup/
bash scripts/download-skills.sh
```
