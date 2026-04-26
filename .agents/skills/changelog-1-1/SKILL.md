---
name: changelog-1-1
description: A skill for creating and maintaining changelogs following the Keep a Changelog specification v1.1.0, providing standardized format guidelines, best practices, and examples for documenting project changes in a human-readable way.
version: "1.1.0"
author: Tangled <noreply@tangledgroup.com>
license: MIT
tags:
- changelog
- documentation
- versioning
- semver
- release-notes
category: documentation
external_references:
- https://keepachangelog.com/en/1.1.0/
- https://semver.org/spec/v2.0.0.html
---

# Keep a Changelog 1.1.0

## Overview

A changelog is a file containing a curated, chronologically ordered list of notable changes for each version of a project. The Keep a Changelog specification (v1.1.0) defines conventions for writing human-readable changelogs that make it easy for users and contributors to see precisely what notable changes have been made between releases.

This skill covers the complete Keep a Changelog format, its guiding principles, types of changes, bad practices to avoid, frequently asked questions, and the Semantic Versioning 2.0.0 specification that changelog versions should follow.

## When to Use

- Creating a new `CHANGELOG.md` for a project
- Maintaining or updating an existing changelog
- Writing release notes that follow standardized conventions
- Understanding how version numbers relate to types of changes
- Converting git commit logs into proper human-readable changelog entries
- Deciding whether a change warrants a major, minor, or patch version bump
- Validating changelog format against the specification

## Core Concepts

**Changelog**: A curated file (typically `CHANGELOG.md`) listing notable changes per version, written for humans not machines.

**Version entry**: Each release gets its own section with a version number and release date in ISO 8601 format (`YYYY-MM-DD`).

**Change types**: Changes are categorized into six standard types — Added, Changed, Deprecated, Removed, Fixed, Security — each signaling a different kind of modification to end users.

**Semantic Versioning (SemVer)**: The versioning scheme (`MAJOR.MINOR.PATCH`) that changelog entries should follow, where the version number communicates the nature and impact of changes.

**Unreleased section**: A top-of-file section for tracking upcoming changes before they are released, serving as both a development log and release preparation tool.

## Example Format

A minimal changelog following the specification:

```markdown
# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.0.0] - 2024-01-15

### Added

- User authentication with OAuth2
- REST API endpoints for resource management

### Changed

- Upgraded database driver from v3 to v4

### Fixed

- Memory leak in background worker process
```

With Markdown link references at the bottom:

```markdown
[unreleased]: https://github.com/example/project/compare/v1.0.0...HEAD
[1.0.0]: https://github.com/example/project/compare/v0.9.0...v1.0.0
```

## Advanced Topics

**Format Specification**: Complete changelog format rules, change types, and Markdown structure → [Format Specification](reference/01-format-specification.md)

**Semantic Versioning 2.0.0**: Full SemVer specification covering version format, precedence rules, pre-release and build metadata → [Semantic Versioning 2.0.0](reference/02-semantic-versioning.md)

**Best Practices and FAQ**: Guiding principles, bad practices to avoid, effort reduction tips, and frequently asked questions → [Best Practices and FAQ](reference/03-best-practices-faq.md)
