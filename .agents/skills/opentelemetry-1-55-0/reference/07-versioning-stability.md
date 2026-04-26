# Versioning and Stability

## Design Goals

1. Users MUST always be able to upgrade to the latest minor version without compilation or runtime errors
2. Never create dependency conflicts between packages relying on different versions of OpenTelemetry
3. Avoid breaking all stable public APIs — backwards compatibility is a strict requirement
4. Instrumentation APIs cannot create version conflicts — they may be embedded in widely shared libraries
5. Code written against older API versions MUST work with all newer API versions
6. Allow multiple levels of package stability within the same release

## Signal Lifecycle

Signals progress through these stages:

1. **Development**: New signal under active development. APIs and data models may change between releases.
2. **Stable**: The signal is stable. Backwards compatibility is guaranteed. No breaking changes without major version bump.
3. **Deprecated**: Signal is scheduled for removal. Existing implementations MUST continue to be supported for at least one year after deprecation.
4. **Removed**: Signal has been removed from the specification.

### Current Signal Statuses (1.55.0)

- **Traces**: Stable
- **Metrics**: Mixed (API and Data Model are Stable; SDK has Development components)
- **Logs**: Stable
- **Baggage**: Stable
- **Profiles**: Development
- **Entities**: Development
- **Context**: Stable

## API Stability

The API is the most stability-critical component:

- Code written against older API versions MUST work with all newer versions
- Transitive dependencies of the API cannot create version conflicts
- APIs can be deprecated and eventually removed, but this process is measured in years
- The OpenTelemetry API cannot depend on a particular package if there is any chance of version conflict

## SDK Stability

- SDKs provide implementation of the API
- Different packages within the same release may have different stability levels
- Stable SDK components guarantee backwards compatibility
- Development SDK components may have breaking changes between minor versions

### Extending API/SDK Abstractions

New abstractions can be added to existing signals. The process ensures that:

- New stable APIs do not break existing code
- Development APIs are clearly marked and versioned separately
- Contrib packages follow their own stability lifecycle

## Contrib Stability

Contrib packages (optional plugins, instrumentation) have independent stability:

- **API Contrib**: Depends only on the API
- **SDK Contrib**: Depends on both API and SDK
- Each contrib package has its own stability status
- Third-party plugins are not part of the official Contrib collection

## Semantic Conventions Stability

Semantic conventions follow their own stability model:

- Generated values should not be distributed in stable packages until conventions are stable
- YAML files in the semantic-conventions repository are the source of truth
- Code generators (weaver) produce language-specific constants

## Version Numbers

### Major Version Bump

- Backwards incompatible changes
- Only for stable components after deprecation period
- Rare — OpenTelemetry values stability highly

### Minor Version Bump

- Backwards compatible additions
- New features, new signals in Development status
- Bug fixes that do not change behavior

### Patch Version Bump

- Backwards compatible fixes
- Documentation corrections
- No behavioral changes

## Language Version Support

Each language implementation defines its own version support policy:

- Minimum supported runtime versions
- Long-term support (LTS) commitments
- EOL schedules for unsupported runtimes

## API Support vs SDK Support

- **API packages**: Must work with any compatible SDK version
- **SDK packages**: May have stricter version requirements
- The API is designed to be embeddable in libraries without creating conflicts

## Deprecated Signals

When a signal is deprecated:

- Existing stable exporters/implementations MUST continue to be supported for at least one year
- Users are directed to alternatives
- Example: Zipkin exporter deprecated in 1.55.0, removal scheduled for December 2026

## Removed Signals

After the deprecation period expires:

- Signal code may be removed from the specification
- Language implementations may remove support
- Migration guides should be provided
