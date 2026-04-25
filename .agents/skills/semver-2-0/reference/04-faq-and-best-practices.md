# FAQ and Best Practices

## Frequently Asked Questions

### How Should I Deal with Revisions in the 0.y.z Initial Development Phase?

**Answer:** Start your initial development release at `0.1.0` and increment the minor version for each subsequent release.

**Recommended approach:**
```
0.1.0  # First public release
0.2.0  # Second release with changes
0.3.0  # Third release
...
0.9.0  # Approaching stability
0.9.1  # Bug fix during development
0.9.2  # Another bug fix
1.0.0  # API stable, ready for production
```

**Rationale:** In major version zero, anything can change at any time. Using minor version increments clearly signals "new development release" without implying stability.

### How Do I Know When to Release 1.0.0?

**Answer:** Release `1.0.0` when:
- Your software is being used in production
- You have a stable API on which users have come to depend
- You're worrying a lot about backward compatibility

**Practical guidance:**
- If your software is being used in production, it should probably already be `1.0.0`
- If you have users depending on your API, you should be `1.0.0`
- Don't delay `1.0.0` indefinitely waiting for "perfect" stability

**Signs you're ready for 1.0.0:**
- Public API is well-documented
- You have real users in production
- Breaking changes require careful consideration
- You've established deprecation workflows

### Doesn't This Discourage Rapid Development and Fast Iteration?

**Answer:** No. Major version zero (`0.y.z`) is specifically designed for rapid development.

**Strategy for fast iteration:**
- Stay in `0.y.z` while API changes frequently
- If changing the API daily, either:
  - Remain in version `0.y.z`, OR
  - Work on a separate development branch for the next major version

**Example workflow:**
```
Main branch:     1.4.2 (stable)
Dev branch:      2.0.0-alpha (rapid changes, breaking API modifications)
Hotfix branch:   1.4.3 (bug fixes for stable)
```

### Won't I End Up at Version 42.0.0 Very Rapidly with Breaking Changes?

**Answer:** This is a question of responsible development and foresight. Incompatible changes should not be introduced lightly to software with dependent code.

**Why major version bumps are valuable:**
- Forces you to think through the impact of changes
- Encourages evaluation of cost/benefit ratio
- Signals to users that upgrading requires attention
- Prevents accidental breaking changes

**Strategies to minimize major version increments:**
- Design APIs with extensibility in mind (add parameters, don't remove)
- Use option bags/config objects instead of long parameter lists
- Deprecate before removing (minor → major workflow)
- Provide migration guides for breaking changes

### Documenting the Entire Public API is Too Much Work!

**Answer:** It is your responsibility as a professional developer to properly document software intended for use by others.

**Why documentation matters:**
- Managing software complexity is crucial for project efficiency
- Users need to know how to use your software
- Users need to know what methods are safe to call
- Clear API boundaries enable proper versioning

**Long-term benefits:**
- Reduces support burden
- Enables users to self-service
- Keeps everyone running smoothly
- Facilitates automated tooling (dependency resolution, etc.)

**Minimum viable documentation:**
- List all exported/public functions and their signatures
- Describe expected behavior and side effects
- Note any constraints or requirements
- Provide usage examples

### What Do I Do If I Accidentally Release a Backward Incompatible Change as a Minor Version?

**Immediate actions:**
1. Fix the problem as soon as discovered
2. Release a new minor version that corrects the problem and restores backward compatibility
3. Never modify already-released versions (immutability rule)
4. Document the offending version and inform users

**Example scenario:**
```
1.5.0  # Accidentally released with breaking change
1.6.0  # Restores backward compatibility
Documentation updated to warn about 1.5.0
Users notified via changelog, email, or other channels
```

**Communication template:**
```
IMPORTANT: Version 1.5.0 contains an unintentional breaking change.
Please upgrade to 1.6.0 which restores compatibility.
Affected functionality: [describe what broke]
Migration path: [how to fix if already upgraded]
```

### What Should I Do If I Update My Own Dependencies Without Changing the Public API?

**Answer:** This is considered backward compatible since it doesn't affect the public API.

**Version increment depends on purpose:**
- Updated dependencies to fix a bug → **Patch version** (`1.2.3` → `1.2.4`)
- Updated dependencies to introduce new functionality → **Minor version** (`1.2.3` → `1.3.0`)

**Considerations:**
- Software that explicitly depends on the same dependencies should have their own dependency specifications
- The dependent author will notice any conflicts through their own dependency resolution
- Additional code usually indicates new functionality (minor version)

**Example:**
```
Updated lodash from 4.17.20 to 4.17.21 for security fix:
→ Patch version (bug/security fix, no API change)

Updated React from 18.1.0 to 18.2.0 to use new features in our public API:
→ Minor version (new functionality exposed to users)
```

### What If I Inadvertently Alter the Public API in a Way That Is Not Compliant with the Version Number Change?

**Example:** Code incorrectly introduces a major breaking change in a patch release.

**Answer:** Use your best judgment based on audience impact.

**Small audience / minimal impact:**
- Revert the breaking change
- Release correct version (patch for bug fix)
- Document the error

**Large audience / significant impact:**
- May be best to perform a major version release
- Even though strictly the "fix" could be a patch
- The version number should convey the importance of changes to users

**Key principle:** Semantic Versioning is about conveying meaning. If changes are important to users, use the version number to inform them appropriately.

### How Should I Handle Deprecating Functionality?

**Answer:** Follow a two-step deprecation process.

**Step 1: Minor version with deprecation notice**
- Update documentation to let users know about the change
- Issue a new minor release with deprecation in place
- Mark deprecated functionality clearly (e.g., `@deprecated` annotations)
- Provide migration path to replacement

**Step 2: Major version removes deprecated functionality**
- Before removal, ensure at least one minor release contained the deprecation
- This gives users time to transition smoothly
- Document removal in major version changelog

**Example timeline:**
```
1.4.0  # oldMethod() works normally
1.5.0  # oldMethod() marked @deprecated, newMethod() introduced
1.6.0  # More time for migration, warnings logged when oldMethod() used
2.0.0  # oldMethod() removed entirely
```

**Deprecation notice template:**
```
@deprecated Since version 1.5.0. Use newMethod() instead.
           oldMethod() will be removed in version 2.0.0.
           Migration guide: [link]
```

### Does SemVer Have a Size Limit on the Version String?

**Answer:** No official limit, but use good judgment.

**Practical considerations:**
- A 255 character version string is probably overkill
- Specific systems may impose their own limits:
  - Git tag names: ~64KB (effectively unlimited for versions)
  - Package managers: Vary by implementation
  - Filesystems: Filename length limits (typically 255 characters)
  - Databases: Column width constraints

**Recommendation:** Keep version strings under 100 characters for maximum compatibility.

**Examples of reasonable lengths:**
```
1.2.3                          # 5 chars
1.2.3-alpha.1                  # 13 chars
1.2.3-beta.2+build.123         # 20 chars
10.20.30-rc.1+20231215.abc123 # 27 chars (reasonable)
```

### Is "v1.2.3" a Semantic Version?

**Answer:** No, "v1.2.3" is NOT a semantic version.

**Context:**
- Prefixing with "v" is a common convention in English to indicate "version"
- Commonly seen with version control: `git tag v1.2.3`
- In this case, "v1.2.3" is the tag name, but the semantic version is "1.2.3"

**Handling the "v" prefix:**
```bash
# Git tag (conventional)
git tag v1.2.3 -m "Release version 1.2.3"

# The actual SemVer is: 1.2.3
# Strip "v" when parsing for validation/comparison
```

**Code handling:**
```python
def extract_semver(tag):
    if tag.startswith('v'):
        return tag[1:]
    return tag

extract_semver("v1.2.3")  # Returns "1.2.3"
```

## Best Practices

### Public API Definition

**Clearly define your public API:**
- Document all exported functions, classes, and interfaces
- Use language mechanisms to mark public vs private (e.g., export statements, visibility modifiers)
- Maintain a changelog that tracks API changes
- Provide migration guides for breaking changes

**Example public API documentation structure:**
```
## Public API

### Functions
- `parseJSON(string): Object` - Parse JSON string
- `validateSchema(data, schema): boolean` - Validate data against schema

### Classes
- `Validator` - Schema validation class
  - Methods: `validate()`, `errors()`, `reset()`

### Configuration
- Environment variables: `API_KEY`, `DEBUG_MODE`
- Config file format: JSON with specific schema
```

### Changelog Best Practices

**Structure your changelog:**
```markdown
# Changelog

## [1.5.0] - 2024-01-15
### Added
- New function `parseXML()` for XML parsing
- Configuration option `strictMode`

### Deprecated
- `oldParse()` method, use `parseJSON()` instead

### Fixed
- Memory leak in parser when handling large files

## [1.4.2] - 2024-01-10
### Fixed
- Crash when parsing empty strings
- Incorrect error messages for invalid input
```

**Changelog entry guidelines:**
- Group changes by type (Added, Changed, Deprecated, Removed, Fixed, Security)
- Include version number and date
- Be specific about what changed
- Note breaking changes prominently

### Pre-Release Versioning Strategy

**Common pre-release naming conventions:**
```
1.0.0-alpha        # Early development, API may change significantly
1.0.0-alpha.1      # First alpha release
1.0.0-alpha.2      # Second alpha release
1.0.0-beta         # Feature complete, testing phase
1.0.0-beta.1       # First beta release
1.0.0-rc.1         # Release candidate, likely final version
1.0.0-rc.2         # Second release candidate (if issues found)
1.0.0              # Stable release
```

**When to use each:**
- **alpha**: Early development, API unstable, for developers only
- **beta**: Feature complete, testing needed, limited user base
- **rc**: Believed stable, seeking final validation before release

### Build Metadata Usage

**Appropriate uses for build metadata:**
```
1.0.0+202312151430   # Build timestamp (YYYYMMDDHHMM)
1.0.0+abc123def456   # Git commit hash
1.0.0+build.1234     # CI/CD build number
1.0.0+prod.us-east-1 # Deployment environment and region
```

**Important:** Build metadata is ignored in precedence comparisons. Use it for:
- Tracking build information
- Debugging and support
- Audit trails
- NOT for version ordering or dependency resolution

### Dependency Specification Patterns

**Safe dependency specifications using SemVer:**

**Allow any backward compatible update:**
```json
{
  "dependency": ">=1.2.0 <2.0.0"
}
```
Allows: `1.2.0`, `1.2.1`, `1.3.0`, `1.99.0` (any 1.x >= 1.2.0)

**Allow only patch updates:**
```json
{
  "dependency": ">=1.2.0 <1.3.0"
}
```
Allows: `1.2.0`, `1.2.1`, `1.2.99` (only 1.2.x)

**Require exact version:**
```json
{
  "dependency": "=1.2.3"
}
```
Allows: Only `1.2.3`

**Shorthand in package managers:**
- npm: `"^1.2.3"` means `>=1.2.0 <2.0.0` (caret range)
- npm: `"~1.2.3"` means `>=1.2.3 <1.3.0` (tilde range)
- Ruby gems: `("~> 1.2.3")` means `>=1.2.3 <1.3.0` (pessimistic constraint)

### Migration Strategies for Breaking Changes

**When you must introduce a breaking change:**

1. **Deprecate first** (if possible):
   - Release minor version with deprecation notice
   - Provide clear migration path
   - Wait at least one minor release before removal

2. **Provide migration guide**:
   ```markdown
   ## Migrating from 1.x to 2.0
   
   ### Breaking Changes
   - `oldMethod()` removed, use `newMethod()` instead
   - Configuration key `old_key` renamed to `new_key`
   
   ### Migration Steps
   1. Replace all calls to `oldMethod()` with `newMethod()`
   2. Update configuration files to use `new_key`
   3. Test thoroughly before deploying
   ```

3. **Version increment correctly**:
   - Breaking change → Major version bump
   - Reset minor and patch to zero
   - Document all breaking changes in release notes

### Tooling and Automation

**Validate versions automatically:**
- Use SemVer validation regex in CI/CD pipelines
- Enforce version format in release workflows
- Automatically extract version from source code or config files

**Example CI check:**
```yaml
# .github/workflows/validate-version.yml
name: Validate Version
on: [push, pull_request]
jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Check version format
        run: |
          VERSION=$(cat package.json | jq -r '.version')
          echo "Version: $VERSION"
          # Validate against SemVer regex
```

**Automated changelog generation:**
- Use tools like `conventional-changelog` to generate changelogs from commit messages
- Enforce commit message conventions (e.g., Conventional Commits)
- Auto-increment version based on commit types:
  - `feat:` → Minor version bump
  - `fix:` → Patch version bump
  - `breaking change:` → Major version bump

## Real-World Examples

### Library Versioning Journey

```
0.1.0  # First release, API experimental
0.2.0  # Added new features, changed some APIs (OK in 0.x)
0.3.0  # More changes, gaining users
0.9.0  # API stabilizing, preparing for 1.0
0.9.1  # Bug fix before 1.0
1.0.0  # Public API declared stable
1.0.1  # Bug fix (backward compatible)
1.1.0  # New feature added to public API
1.1.1  # Another bug fix
1.2.0  # Deprecated oldMethod(), added newMethod()
1.3.0  # More features, oldMethod() still works
2.0.0  # Removed oldMethod() (breaking change)
2.0.1  # Bug fix in new implementation
```

### Framework Versioning with Long Support Cycles

```
3.0.0   # Major release with breaking changes
3.0.1   # Critical bug fix
3.1.0   # New features (backward compatible)
3.2.0   # More features
3.2.1   # Bug fix
3.2.2   # Security patch
4.0.0-alpha.1  # Next major in development
4.0.0-beta.1   # Beta testing
4.0.0-rc.1     # Release candidate
4.0.0          # New major version released
3.2.3          # Backport critical fix to 3.x (if supported)
```

## Common Pitfalls to Avoid

### ❌ Don't Use Leading Zeros
```
Invalid: 1.02.03  # Has leading zeros
Valid:   1.2.3    # No leading zeros
```

### ❌ Don't Skip Version Components
```
Invalid: 1.2      # Missing patch version
Valid:   1.2.0    # All three components present
```

### ❌ Don't Modify Released Versions
```
Wrong:  Updating 1.2.3 after release
Right:  Release 1.2.4 with corrections
```

### ❌ Don't Use Major Version Zero for Production
```
Risky:  Using 0.9.5 in production (API can change anytime)
Safe:   Use 1.0.0+ for production systems
```

### ❌ Don't Bump Patch for New Features
```
Wrong:  1.2.3 → 1.2.4 for new feature
Right:  1.2.3 → 1.3.0 for new feature
```

### ✅ Do Deprecate Before Removing
```
Good practice:
1.5.0  # Mark oldMethod() as deprecated
1.6.0  # Users have time to migrate
2.0.0  # Remove oldMethod()
```

### ✅ Do Document Breaking Changes
```
Always include in release notes:
## Breaking Changes
- Removed X, use Y instead
- Changed behavior of Z from A to B
```
