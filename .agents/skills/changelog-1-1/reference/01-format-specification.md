# Format Specification

## File Name

Call the file `CHANGELOG.md`. Some projects use `HISTORY`, `NEWS`, or `RELEASES`, but `CHANGELOG.md` is the recommended convention for discoverability.

## Header

Every changelog should begin with a title and introduction:

```markdown
# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).
```

## Version Entry Format

Each version gets a level-2 heading with the version number and release date:

```markdown
## [1.0.0] - 2024-01-15
```

The version number should be a linkable Markdown reference. The date must follow ISO 8601 format (`YYYY-MM-DD`) — year, month, day from largest to smallest units.

## Unreleased Section

Place an `Unreleased` section at the top to track upcoming changes:

```markdown
## [Unreleased]

### Added

- Feature that will be in the next release
```

This serves two purposes:

- People can see what changes they might expect in upcoming releases
- At release time, you move the `Unreleased` section into a new versioned entry

## Change Types

Group changes under level-3 headings using these standard categories:

**`### Added`** — New features.

```markdown
### Added

- User authentication with OAuth2
- REST API endpoints for resource management
```

**`### Changed`** — Changes in existing functionality.

```markdown
### Changed

- Upgraded database driver from v3 to v4
- Renamed `getUser()` to `fetchUser()` in the API client
```

**`### Deprecated`** — Soon-to-be removed features. Always list deprecations so users can prepare for removal.

```markdown
### Deprecated

- `legacy_mode` flag will be removed in v2.0.0, use `classic_mode` instead
```

**`### Removed`** — Features that have been removed.

```markdown
### Removed

- Support for Python 3.7 (end of life)
- `legacy_mode` flag, replaced by `classic_mode` in v1.5.0
```

**`### Fixed`** — Bug fixes.

```markdown
### Fixed

- Memory leak in background worker process
- Incorrect date formatting in timezone UTC-5
```

**`### Security`** — Vulnerability fixes or security-related changes.

```markdown
### Security

- Patched SQL injection vulnerability in search endpoint (CVE-2024-1234)
```

Only include change type sections that have entries. Do not leave empty sections — missing sections imply no notable changes of that type.

## Markdown Link References

Place link references at the bottom of the file:

```markdown
[unreleased]: https://github.com/example/project/compare/v1.0.0...HEAD
[1.0.0]: https://github.com/example/project/compare/v0.9.0...v1.0.0
[0.9.0]: https://github.com/example/project/compare/v0.8.0...v0.9.0
```

These links point to commit comparisons between releases, providing a bridge between the curated changelog and the full commit history.

## Yanked Releases

Yanked releases are versions pulled due to serious bugs or security issues. Mark them with `[YANKED]`:

```markdown
## [0.0.5] - 2014-12-13 [YANKED]
```

The `[YANKED]` tag is loud and surrounded by brackets for easy programmatic parsing.

## Ordering

Versions should be in reverse chronological order — the latest version comes first. This makes the most recent changes immediately visible.

## Complete Example

```markdown
# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- Dark mode support for the dashboard

## [2.1.0] - 2024-06-15

### Added

- Export data to CSV format
- Webhook notifications for status changes

### Changed

- Improved query performance by 40% with database indexing
- Updated dependency `requests` from v2.28 to v2.31

### Deprecated

- XML output format, use JSON instead (will be removed in v3.0.0)

### Fixed

- Off-by-one error in pagination for large datasets
- Null pointer exception when user profile image is missing

### Security

- Updated `crypto-js` to fix vulnerability CVE-2024-5678

## [2.0.0] - 2024-03-01

### Added

- Multi-tenant architecture
- Role-based access control (RBAC)
- GraphQL API alongside REST endpoints

### Changed

- Breaking: Authentication now requires API keys instead of basic auth
- Breaking: Minimum Python version bumped from 3.8 to 3.10

### Removed

- Legacy SOAP API endpoints
- Support for Python 3.7 and earlier

### Fixed

- Race condition in concurrent request handling

[unreleased]: https://github.com/example/project/compare/v2.1.0...HEAD
[2.1.0]: https://github.com/example/project/compare/v2.0.0...v2.1.0
[2.0.0]: https://github.com/example/project/compare/v1.5.0...v2.0.0
```
