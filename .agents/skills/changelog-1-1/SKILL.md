---
name: changelog-1-1
description: A skill for creating and maintaining changelogs following the Keep a Changelog specification v1.1.0, providing standardized format guidelines, best practices, and examples for documenting project changes in a human-readable way.
version: "0.2.0"
author: Your Name <email@example.com>
license: MIT
tags:
  - changelog
  - documentation
  - versioning
  - semver
  - release-notes
category: documentation
---

# Keep a Changelog v1.1.0

A skill for creating and maintaining changelogs following the [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) specification, a widely-adopted convention for documenting notable changes in software projects.

## When to Use

- Creating a new CHANGELOG.md file for a project
- Documenting changes between releases
- Following Semantic Versioning (SemVer) conventions
- Writing release notes for users and contributors
- Standardizing changelog format across teams

## What Is a Changelog

A changelog is a file which contains a curated, chronologically ordered list of notable changes for each version of a project. It should be human-readable and focused on meaningful changes that affect users.

## Guiding Principles

- Changelogs are **for humans**, not machines
- There should be an entry for every single version
- The same types of changes should be grouped
- Versions and sections should be linkable
- The latest version comes first (reverse chronological order)
- The release date of each version is displayed
- Mention whether you follow [Semantic Versioning](https://semver.org/)

## Change Types

Use these standardized section headers to categorize changes:

| Section | When to Use |
|---------|-------------|
| **Added** | New features |
| **Changed** | Changes in existing functionality |
| **Deprecated** | Soon-to-be removed features |
| **Removed** | Now removed features |
| **Fixed** | Any bug fixes |
| **Security** | In case of vulnerabilities |

## Basic Template

```markdown
# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- Feature that will be in the next release.

### Changed

- Changes to existing functionality.

### Fixed

- Bug fixes pending release.

## [1.0.0] - 2024-01-15

### Added

- New authentication system.
- API rate limiting support.

### Changed

- Updated error message formatting.

### Fixed

- Login timeout issue under high load.

[unreleased]: https://github.com/username/project/compare/v1.0.0...HEAD
[1.0.0]: https://github.com/username/project/releases/tag/v1.0.0
```

## Writing Changelog Entries

### Entry Format

Each entry should:
- Start with a capital letter
- End with a period
- Use imperative mood ("Add feature" not "Added feature")
- Be concise but descriptive
- Reference issues/PRs when applicable

**Good examples:**
```markdown
### Added

- User authentication via OAuth 2.0 (#123).
- Dark mode theme support.

### Fixed

- Memory leak in image processing module (#456).
- Incorrect date formatting for European locales.
```

**Avoid:**
```markdown
### Added

- added oauth (too vague, lowercase)
- we implemented a new authentication system (not imperative)
- fixed the bug where sometimes it doesn't work (vague)
```

## Date Format

Use **ISO 8601** format (`YYYY-MM-DD`) for release dates:

```markdown
## [2.1.0] - 2024-03-15
```

This format is recommended because:
- It follows largest to smallest units (year, month, day)
- It's an ISO standard
- It avoids regional ambiguity (unlike MM/DD/YYYY vs DD/MM/YYYY)

## Version Linking

Create linkable version references at the bottom of the file:

```markdown
[unreleased]: https://github.com/username/project/compare/v1.0.0...HEAD
[1.0.0]: https://github.com/username/project/releases/tag/v1.0.0
[0.9.0]: https://github.com/username/project/compare/v0.8.0...v0.9.0
```

For Git-based projects, use comparison URLs to show changes between versions.

## Unreleased Section

Keep an `Unreleased` section at the top to track upcoming changes:

```markdown
## [Unreleased]

### Added

- Feature being developed for next release.

### Fixed

- Bug fix not yet released.
```

**Benefits:**
- People can see what changes to expect in upcoming releases
- At release time, move `Unreleased` content into a new version section with date

## Yanked Releases

For versions that were pulled due to serious bugs or security issues:

```markdown
## [1.2.0] - 2024-02-20 [YANKED]

### Removed

- Feature that caused critical issues.
```

The `[YANKED]` tag is important for users to notice and can be parsed programmatically.

## Common Mistakes to Avoid

### Commit Log Diffs

**Don't** use commit log diffs as changelogs. They contain noise like:
- Merge commits
- Obscure commit titles
- Documentation-only changes
- Refactoring that doesn't affect users

**Do** curate entries that communicate noteworthy differences to end users.

### Ignoring Deprecations

Always list deprecations, removals, and breaking changes. Users need to know:
1. What will break when they upgrade
2. How to migrate before the removal
3. Which version introduced the deprecation

### Inconsistent Updates

A changelog that only mentions some changes is as dangerous as no changelog. Maintain consistency:
- Document all notable changes
- Don't skip versions
- Update the changelog with every release

### Confusing Dates

Avoid regional date formats. Use ISO 8601 (`YYYY-MM-DD`) for clarity across all locales.

## File Naming

Name the file `CHANGELOG.md` (uppercase, `.md` extension).

Alternative names exist (`HISTORY`, `NEWS`, `RELEASES`) but `CHANGELOG.md` is the most discoverable and widely recognized convention.

## GitHub Releases Integration

GitHub Releases can complement a CHANGELOG.md:
- Create releases from git tags (e.g., `v1.0.0`)
- Add release notes manually or pull from annotated tags
- Link to the CHANGELOG.md in release descriptions

**Note:** GitHub Releases are not portable (only visible on GitHub). Keep a CHANGELOG.md file for portability and discoverability.

## Workflow Example

### Before Release

```markdown
## [Unreleased]

### Added

- New export feature (#234).

### Fixed

- Crash when importing large files (#235).
```

### At Release Time (v1.1.0)

```markdown
## [1.1.0] - 2024-03-20

### Added

- New export feature (#234).

### Fixed

- Crash when importing large files (#235).

## [Unreleased]

### Added

- Next feature in development.

[1.1.0]: https://github.com/username/project/releases/tag/v1.1.0
```

## Tools and Automation

Several tools can help maintain changelogs:

- **git-changelog**: Generate changelogs from git commits
- **keep-a-changelog-action**: GitHub Action for automated changelog management
- **Vandamme**: Ruby gem that parses many open source project changelogs
- **semantic-release**: Automated versioning and changelog generation

## Resources

- [Keep a Changelog v1.1.0](https://keepachangelog.com/en/1.1.0/) - Official specification
- [Semantic Versioning 2.0.0](https://semver.org/spec/v2.0.0.html) - Versioning standard
- [GNU Changelog Style Guide](https://www.gnu.org/prep/standards/html_node/Style-of-Change-Logs.html) - Alternative style guide

## Troubleshooting

**Q: Should I rewrite an existing changelog?**

A: Yes, if it improves clarity or adds missing releases. Many projects benefit from retroactive changelog improvements.

**Q: How detailed should entries be?**

A: Focus on notable changes that affect users. Internal refactoring without user impact doesn't need to be included.

**Q: What about translations?**

A: Keep a Changelog is available in 28+ languages. Consider providing changelogs in your project's supported languages.
