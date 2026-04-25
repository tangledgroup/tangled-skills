# Version Increment Rules and Public API Requirements

## Core Principles

### Declare a Public API

Software using Semantic Versioning MUST declare a public API. This API could be:
- Declared in the code itself (type signatures, exported symbols)
- Exist strictly in documentation
- A combination of both

The public API SHOULD be precise and comprehensive to enable users to understand what changes will affect compatibility.

### Immutable Releases

Once a versioned package has been released, the contents of that version MUST NOT be modified. Any modifications MUST be released as a new version. This ensures:
- Reproducible builds
- Reliable dependency resolution
- Clear audit trails for changes

## Version Component Rules

### Patch Version (x.y.Z | x > 0)

**MUST be incremented when:**
- Backward compatible bug fixes are introduced

**Definition of a bug fix:**
An internal change that fixes incorrect behavior without affecting the public API.

**Examples:**
- `1.2.3` → `1.2.4`: Fixed a calculation error in an internal function
- `2.0.5` → `2.0.6`: Corrected documentation that affected code behavior
- `1.10.2` → `1.10.3`: Fixed memory leak in private implementation

**MUST NOT be incremented for:**
- New functionality (use minor version)
- API changes (use minor or major version)
- Documentation-only updates (unless they correct misleading information about behavior)

### Minor Version (x.Y.z | x > 0)

**MUST be incremented when:**
- New, backward compatible functionality is introduced to the public API
- Any public API functionality is marked as deprecated

**MAY be incremented when:**
- Substantial new functionality or improvements are introduced within private code

**Includes:**
- Patch level changes may be included in a minor version bump

**Reset rule:**
Patch version MUST be reset to 0 when minor version is incremented.

**Examples:**
- `1.2.3` → `1.3.0`: Added new function `calculateTotal()` to public API
- `2.5.1` → `2.6.0`: Deprecated `oldMethod()` in favor of `newMethod()`
- `1.9.0` → `1.10.0`: Note numeric increment (9 → 10, not 9 → 91)

**Deprecation workflow:**
1. Release minor version with deprecation notice
2. Users have at least one minor release to transition
3. Remove deprecated functionality in a major version bump

### Major Version (X.y.z | X > 0)

**MUST be incremented when:**
- Any backward incompatible changes are introduced to the public API

**MAY include:**
- Minor level changes (new backward compatible features)
- Patch level changes (bug fixes)

**Reset rules:**
- Patch version MUST be reset to 0 when major version is incremented
- Minor version MUST be reset to 0 when major version is incremented

**Examples:**
- `1.4.2` → `2.0.0`: Removed parameter from public function (breaking change)
- `2.3.1` → `3.0.0`: Changed return type of exported method
- `1.0.5` → `2.0.1`: Breaking change plus bug fix in same release

## Major Version Zero (0.y.z)

### Initial Development Phase

Major version zero (`0.y.z`) is for initial development. During this phase:

**Anything MAY change at any time:**
- Public API is NOT considered stable
- Breaking changes do not require major version bump (already at 0)
- Users should expect instability

**RECOMMENDED practice:**
- Start initial development release at `0.1.0`
- Increment minor version for each subsequent release
- Use patch version for critical bug fixes during development

**Examples:**
- `0.1.0`: First public release
- `0.2.0`: Added new features, changed some API (acceptable in 0.y.z)
- `0.9.5`: Mature pre-1.0 release with several bug fixes

### When to Release 1.0.0

Release `1.0.0` when:
- Your software is being used in production
- You have a stable API on which users have come to depend
- You're worrying about backward compatibility
- The public API is well-defined and documented

**Note:** If your software is being used in production, it should probably already be `1.0.0`.

## Numeric Increment Rules

Each version element MUST increase numerically, not lexicographically:

**Correct examples:**
- `1.9.0` → `1.10.0` → `1.11.0` (not 1.9.0 → 1.91.0)
- `2.99.0` → `2.100.0` → `2.101.0`

**Incorrect examples:**
- `1.9.0` → `1.91.0` (string comparison would make 91 > 10)
- `2.10.0` → `2.9.0` (decrementing is not allowed for new releases)

## Dependency Specification Examples

Using SemVer enables precise dependency specifications:

**Compatible with current minor version:**
```
>=3.1.0 <4.0.0
```
Allows: `3.1.0`, `3.1.1`, `3.2.0`, `3.99.0` (any 3.x.x >= 3.1.0)

**Compatible with current major version:**
```
>=2.0.0 <3.0.0
```
Allows: Any `2.x.x` version (all backward compatible within major 2)

**Exact version:**
```
=1.2.3
```
Allows: Only `1.2.3`

**Any patch version of minor:**
```
>=1.4.0 <1.5.0
```
Allows: `1.4.0`, `1.4.1`, `1.4.99` (any 1.4.x)

## Common Scenarios

### Scenario 1: Bug Fix Without API Change

**Situation:** Fixed an internal calculation error that doesn't affect the public API.

**Action:** Increment patch version
- `1.2.3` → `1.2.4`

### Scenario 2: Adding New Public Function

**Situation:** Added a new exported function `parseJSON()` to the library.

**Action:** Increment minor version, reset patch
- `1.2.3` → `1.3.0`

### Scenario 3: Deprecating Old API

**Situation:** Marking `oldParse()` as deprecated in favor of `newParse()`.

**Action:** Increment minor version (deprecation requires minor bump)
- `1.5.0` → `1.6.0`
- Document deprecation clearly
- Plan removal in next major version (`2.0.0`)

### Scenario 4: Breaking Change

**Situation:** Removed required parameter from public function signature.

**Action:** Increment major version, reset minor and patch
- `1.9.3` → `2.0.0`

### Scenario 5: Multiple Changes in One Release

**Situation:** Release includes both breaking changes and bug fixes.

**Action:** Follow the highest-level change (major takes precedence)
- Breaking change + bug fix: `1.4.2` → `2.0.0`
- New feature + bug fix: `1.4.2` → `1.5.0`
- Multiple bug fixes: `1.4.2` → `1.4.3`

## Accidental Non-Compliant Releases

### If You Release a Breaking Change as Minor Version

**Immediate actions:**
1. Fix the problem as soon as discovered
2. Release a new minor version that restores backward compatibility
3. Document the offending version and inform users
4. Never modify already-released versions

**Example:**
- `1.5.0` accidentally released with breaking change
- `1.6.0` released to restore compatibility
- Documentation updated to warn about `1.5.0`

### If You Release a Breaking Change as Patch Version

**Use judgment based on impact:**
- Small audience: Revert and release correct minor version
- Large audience with significant impact: May need major version bump even though strictly a "fix"
- Remember: SemVer is about conveying meaning to users

## Updating Own Dependencies

When updating your own dependencies without changing the public API:

**Considered:** Backward compatible (doesn't affect public API)

**Version increment depends on purpose:**
- Updated dependencies to fix a bug → Patch version (`1.2.3` → `1.2.4`)
- Updated dependencies to introduce new functionality → Minor version (`1.2.3` → `1.3.0`)

**Note:** Software that explicitly depends on the same dependencies should have their own dependency specifications and will notice any conflicts independently.
