# Conventional Commits v1.0.0

This reference covers the full Conventional Commits specification (v1.0.0), a lightweight convention on top of commit messages that enables automated tooling for changelogs, version bumping, and release notes.

## Format Structure

Every commit message MUST follow this structure:

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

### Structural Elements

| Element | Required | Description |
|---------|----------|-------------|
| `type` | Yes | A noun describing the change (e.g., `feat`, `fix`) |
| `scope` | No | Noun in parentheses describing the code section (e.g., `parser`) |
| `!` | No | Exclamation mark before `:` to indicate breaking change |
| `: ` | Yes | Colon followed by a space after type/scope/! |
| `description` | Yes | Short summary of the code changes |
| `body` | No | Longer description, one blank line after description |
| `footer(s)` | No | One or more trailers, one blank line after body |

## Commit Types

### Mandatory Types

| Type | SemVer Impact | Description |
|------|--------------|-------------|
| `feat` | MINOR | A new feature for the user |
| `fix` | PATCH | A bug fix for the user |

### Breaking Changes

A commit introduces a breaking API change (correlating with MAJOR in SemVer) in one of two ways:

**Option 1 — Exclamation mark before colon:**
```
feat!: send an email to the customer when a product is shipped
```

**Option 2 — BREAKING CHANGE footer:**
```
feat: allow provided config object to extend other configs

BREAKING CHANGE: `extends` key in config file is now used for extending other config files
```

**Option 3 — Both (for emphasis):**
```
feat!: drop support for Node 6

BREAKING CHANGE: use JavaScript features not available in Node 6.
```

Both methods are equivalent. The description in the footer (or commit message) SHALL describe the breaking change.

### Recommended Additional Types

These types are NOT mandated by the spec but are recommended by [@commitlint/config-conventional](https://github.com/conventional-changelog/commitlint/tree/master/%40commitlint/config-conventional) (based on the Angular convention):

| Type | SemVer Impact | Description |
|------|--------------|-------------|
| `build` | — | Changes that affect the build system or external dependencies |
| `chore` | — | Other changes that don't modify src or test files |
| `ci` | — | Changes to CI configuration files and scripts |
| `docs` | — | Documentation only changes |
| `style` | — | Changes that do not affect the meaning of the code (white-space, formatting) |
| `refactor` | — | A code change that neither fixes a bug nor adds a feature |
| `perf` | PATCH | A code change that improves performance |
| `test` | — | Adding missing tests or correcting existing tests |

Types other than `feat` and `fix` have no implicit effect in Semantic Versioning (unless they include a BREAKING CHANGE).

## Complete Examples

### Simple Commit (No Body, No Scope)

```
docs: correct spelling of CHANGELOG
```

### With Scope

```
feat(lang): add Polish language
```

### With Breaking Change via `!`

```
feat!: send an email to the customer when a product is shipped
```

### With Scope and Breaking Change

```
feat(api)!: send an email to the customer when a product is shipped
```

### With Description and BREAKING CHANGE Footer

```
feat: allow provided config object to extend other configs

BREAKING CHANGE: `extends` key in config file is now used for extending other config files
```

### Multi-Paragraph Body with Multiple Footers

```
fix: prevent racing of requests

Introduce a request id and a reference to latest request. Dismiss
incoming responses other than from latest request.

Remove timeouts which were used to mitigate the racing issue but are
obsolete now.

Reviewed-by: Z
Refs: #123
```

### Revert Commits

Conventional Commits does not define an explicit revert type, but recommends using the `revert` type with a footer referencing the reverted commit SHAs:

```
revert: let us never again speak of the noodle incident

Refs: 676104e, a215868
```

## Specification Rules (RFC 2119)

The following rules are mandatory for spec compliance:

1. Commits **MUST** be prefixed with a type, consisting of a noun (`feat`, `fix`, etc.), followed by the OPTIONAL scope, OPTIONAL `!`, and REQUIRED terminal colon and space.
2. The type `feat` **MUST** be used when a commit adds a new feature to your application or library.
3. The type `fix` **MUST** be used when a commit represents a bug fix for your application.
4. A scope **MAY** be provided after a type. A scope **MUST** consist of a noun describing a section of the codebase surrounded by parentheses, e.g., `fix(parser):`.
5. A description **MUST** immediately follow the colon and space after the type/scope prefix. The description is a short summary of the code changes.
6. A longer commit body **MAY** be provided after the short description, providing additional contextual information. The body **MUST** begin one blank line after the description.
7. A commit body is free-form and **MAY** consist of any number of newline-separated paragraphs.
8. One or more footers **MAY** be provided one blank line after the body. Each footer **MUST** consist of a word token, followed by either `:<space>` or `<space>#` separator, followed by a string value.
9. A footer's token **MUST** use `-` in place of whitespace characters, e.g., `Acked-by`. An exception is made for `BREAKING CHANGE`, which **MAY** also be used as a token.
10. A footer's value **MAY** contain spaces and newlines, and parsing **MUST** terminate when the next valid footer token/separator pair is observed.
11. Breaking changes **MUST** be indicated in the type/scope prefix of a commit, or as an entry in the footer.
12. If included as a footer, a breaking change **MUST** consist of the uppercase text `BREAKING CHANGE`, followed by a colon, space, and description.
13. If included in the type/scope prefix, breaking changes **MUST** be indicated by a `!` immediately before the `:`. If `!` is used, `BREAKING CHANGE:` **MAY** be omitted from the footer section.
14. Types other than `feat` and `fix` **MAY** be used in your commit messages.
15. The units of information that make up Conventional Commits **MUST NOT** be treated as case-sensitive by implementors, with the exception of `BREAKING CHANGE` which **MUST** be uppercase.
16. `BREAKING-CHANGE` **MUST** be synonymous with `BREAKING CHANGE`, when used as a token in a footer.

## Why Use Conventional Commits

- **Automatically generating CHANGELOGs** — tools can parse commit history to produce release notes
- **Automatically determining semantic version bumps** — based on the types of commits landed
- **Communicating the nature of changes** — to teammates, the public, and other stakeholders
- **Triggering build and publish processes** — CI/CD pipelines can react to specific commit types
- **Making it easier for people to contribute** — by allowing them to explore a more structured commit history

## FAQ

### How should I deal with commit messages in the initial development phase?

Proceed as if you've already released the product. Typically *somebody*, even if it's your fellow developers, is using your software. They'll want to know what's fixed and what breaks.

### Are the types in the commit title uppercase or lowercase?

Any casing may be used, but it's best to be consistent across the project.

### What do I do if the commit conforms to more than one of the commit types?

Go back and make multiple commits whenever possible. Part of the benefit of Conventional Commits is its ability to drive you to make more organized commits and PRs.

### Doesn't this discourage rapid development and fast iteration?

It discourages moving fast in a disorganized way. It helps you be able to move fast long term across multiple projects with varied contributors.

### How does this relate to SemVer?

- `fix` type commits should be translated to **PATCH** releases
- `feat` type commits should be translated to **MINOR** releases
- Commits with `BREAKING CHANGE` in the commits, regardless of type, should be translated to **MAJOR** releases

### Do all my contributors need to use the Conventional Commits specification?

No! If you use a squash-based workflow on Git, lead maintainers can clean up the commit messages as they're merged — adding no workload to casual committers. A common workflow is to have your git system automatically squash commits from a pull request and present a form for the lead maintainer to enter the proper git commit message for the merge.

### How should I version my extensions to the Conventional Commits Specification?

Use SemVer to release your own extensions to this specification.

See [SemVer 2.0.0](../04-semver-2-0-0.md) for versioning rules that complement Conventional Commits.
See [Core Git Commands](../01-core-git-commands.md) for the `git commit` command reference.
