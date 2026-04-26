# Best Practices and FAQ

## Guiding Principles

- Changelogs are **for humans**, not machines
- There should be an entry for every single version
- The same types of changes should be grouped
- Versions and sections should be linkable
- The latest version comes first
- The release date of each version is displayed
- Mention whether you follow Semantic Versioning

## Reducing Maintenance Effort

Keep an `Unreleased` section at the top to track upcoming changes. This serves two purposes:

1. People can see what changes they might expect in upcoming releases
2. At release time, move the `Unreleased` section into a new versioned entry

This turns changelog maintenance into an incremental process rather than a last-minute documentation effort.

## Bad Practices

### Commit Log Diffs

Using commit log diffs as changelogs is a bad idea — they are full of noise: merge commits, commits with obscure titles, documentation changes, etc.

The purpose of a commit is to document a step in the evolution of the source code. The purpose of a changelog entry is to document the noteworthy difference, often across multiple commits, and communicate it clearly to end users.

### Ignoring Deprecations

When people upgrade from one version to another, it should be clear when something will break. It should be possible to upgrade to a version that lists deprecations, remove what is deprecated, then upgrade to the version where deprecations become removals.

If you do nothing else, list deprecations, removals, and any breaking changes in your changelog.

### Confusing Dates

Regional date formats vary throughout the world. The format `2017-07-17` (ISO 8601) is recommended because:

- It follows largest-to-smallest units: year, month, day
- It does not overlap ambiguously with other regional formats
- It is an ISO standard

### Inconsistent Changes

A changelog that only mentions some changes can be as dangerous as no changelog at all. While trivial changes (removing whitespace) may not need recording, any important changes should be mentioned. With great power comes great responsibility — having a good changelog means having a consistently updated changelog.

## Frequently Asked Questions

### What about GitHub Releases?

GitHub Releases can turn simple git tags into rich release notes. However, they create a non-portable changelog that can only be displayed within GitHub's context. They are also less discoverable than standard uppercase files like `README` and `CONTRIBUTING`.

It is possible to make GitHub Releases follow the Keep a Changelog format, but it tends to be more involved.

### Can changelogs be automatically parsed?

It is difficult because people follow wildly different formats and file names. [Vandamme](https://github.com/tech-angels/vandamme/) is a Ruby gem that parses many (but not all) open source project changelogs.

The Keep a Changelog format is designed to be more parseable than arbitrary formats — standardized section headings and consistent structure make automated extraction feasible.

### Should you ever rewrite a changelog?

Yes. There are always good reasons to improve a changelog. You might discover that you forgot to address a breaking change in the notes for a version — it is important to update your changelog in this case.

Many maintainers regularly open pull requests to add missing releases to open source projects with unmaintained changelogs.

### Is there a standard changelog format?

There is the [GNU changelog style guide](https://www.gnu.org/prep/standards/html_node/Style-of-Change-Logs.html) and the [GNU NEWS file](https://www.gnu.org/prep/standards/html_node/NEWS-File.html) guideline, but both are considered inadequate or insufficient.

Keep a Changelog aims to be a better convention, derived from observing good practices in the open source community.

### What about yanked releases?

Yanked releases should appear in the changelog with a `[YANKED]` tag:

```markdown
## [0.0.5] - 2014-12-13 [YANKED]
```

The tag is loud for a reason — it is important for people to notice it. The brackets make it easier to parse programmatically.

## Writing Good Changelog Entries

### Be Specific

```markdown
# Good
- Added OAuth2 authentication supporting Google, GitHub, and Microsoft providers

# Vague
- Added auth
```

### Include Impact When Relevant

```markdown
# Good
- Improved query performance by 40% with database indexing on user email field

# Less useful
- Made queries faster
```

### Reference Issues or PRs

```markdown
# Good
- Fixed memory leak in background worker process (#423)
- Added CSV export feature, closes #156

# Acceptable but less traceable
- Fixed memory leak in background worker process
```

### Keep Entries Concise

Each entry should be a single line when possible. If more detail is needed, use a paragraph under the bullet.

```markdown
### Changed

- Replaced `asyncio.sleep()` with proper event-driven scheduling in the task runner.
  This reduces idle CPU usage from 15% to near-zero during wait periods.
```

### Use Past Tense for Completed Changes

```markdown
# Good (released)
- Added support for dark mode

# Good (unreleased, future tense acceptable)
- Will add support for dark mode
```
