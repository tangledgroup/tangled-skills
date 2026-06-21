# Dependencies

## Plan Dependencies

Multiple `PLAN.md` files can exist in different locations, forming a directed acyclic graph (DAG) via the `Depends On` header field. Manage dependencies with `plan.sh set-plan-depends-on`.

- Multiple dependencies are comma-separated with spaces: `../a/PLAN.md , ../../b/PLAN.md`
- Default value is `NONE` when the plan has no dependencies
- Cycles are not allowed. The script checks for cycles (including transitive) whenever `Depends On` is modified. If a cycle is detected, report it to the user and stop until resolved
- The dependency graph is resolved transitively by visiting referenced `PLAN.md` headers — not inline-expanded
- When a dependency is incomplete, ask the user what to do before proceeding

## Dependency Management

Manage dependencies incrementally as you identify them using `plan.sh add-task-dependency` and `plan.sh remove-task-dependency`. Don't wait until all tasks are listed.

- **Add dependencies** when a new task depends on an existing one, or cross-phase prerequisites are discovered
- **Remove dependencies** when restructuring makes them invalid, or a task split moves the dependency

There is no bulk command — call `add-task-dependency` for each individual edge.
