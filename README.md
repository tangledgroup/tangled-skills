# tangled-skills

Collection of Skills for Agents by Tangled

## About

All skills in this repository are automatically generated using the `skill` skill. Each skill is created from public references, official documentation URLs, and other publicly available resources to ensure accuracy and completeness.

This repository also includes meta skills that govern agent behavior and workflows: `skman`, `git`, `tzip`, `plan`, `pipe`, `webfetch`, and `websearch`.

## Install / Update
<!-- IMPORTANT: never change this section and code block -->
```bash
mkdir -p .agents/skills && \
curl -L https://github.com/tangledgroup/tangled-skills/archive/refs/heads/main.tar.gz | \
tar -xz --strip-components=3 -C .agents/skills tangled-skills-main/.agents/skills
```

### Skill Design Principles

- **Detailed yet concise**: Skills provide comprehensive coverage while staying within typical LLM context limits
- **Modular reference files**: Large topics are broken down into separate reference files that can be loaded on demand
- **Markdown only**: All skill files are plain Markdown documents - no scripts or executable code
- **Reference-driven**: Each skill links to official documentation and public resources for further exploration

<!-- IMPORTANT: never change after this point because it is automatically generated -->
## Skills Table

| No | Skill | Description |
|----|-------|-------------|
| 1 | git | Git version control. Use when the user mentions git, commits, branches, pushing, pulling, merging, rebasing, stashing, worktrees, submodules, or any version control task. Covers straightforward workflows (add/commit/push) and advanced topics. |
| 2 | plan | Phase/task based workflow system with PLAN.md as single source of truth. Use when tackling projects that require structured iteration through Planning, Analysis, Design, Implementation, Testing, Deployment, Maintenance, etc phases with clear dependency graphs. |
| 3 | skman | Scaffold, validate, and inspect agent skills (SKILL.md files). Use when creating new skills, checking skill format compliance, or reviewing skill structure. |
| 4 | tzip | Lightweight token-pruning communication mode that drops filler and hedging while keeping full sentences and professional tone. Follows guidelines for code quality. Default intensity is lite. Use when user requests tzip, prune tokens, be concise, or needs efficient communication without losing clarity. |

## Statistics

- **Total Skills**: 4
