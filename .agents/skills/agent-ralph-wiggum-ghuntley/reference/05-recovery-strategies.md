# Recovery Strategies

## You Will Wake Up to a Broken Codebase

It is inevitable that Ralph will produce broken code at some point. The codebase may not compile, tests may be failing across multiple modules, or the agent may have taken a fundamentally wrong architectural direction. This is not a failure of the technique — it is an expected state in the eventual consistency model.

When this happens, you need to make a judgment call as an engineer:

1. **Git reset and restart**: `git reset --hard` to a known-good state, then kick Ralph back off with adjusted prompts
2. **Rescue prompts**: Craft specific prompts designed to diagnose and repair the current state
3. **Cross-model triage**: Feed error output into a different LLM to generate a recovery plan

## Git Reset Strategy

The nuclear option: discard broken work and restart from a known-good commit. This is appropriate when:

- The number of compilation errors fills the context window
- Ralph has taken a fundamentally wrong architectural direction
- Multiple modules are broken in interconnected ways
- The cost of fixing exceeds the cost of regenerating

```bash
git reset --hard <known-good-commit>
# Then restart the loop with tuned prompts
```

Through building CURSED, Huntley deleted the TODO list multiple times and regenerated it. The TODO list is what to watch like a hawk — and throw out often.

## Rescue Prompts

When a full reset is too aggressive, craft targeted rescue prompts that address specific failure modes:

- **Diagnosis mode**: Instruct Ralph to study the codebase and produce a report of what is broken, without making changes
- **Incremental repair**: Focus on fixing one module or subsystem at a time
- **Test-driven recovery**: Run tests first, then have Ralph fix failures in order of severity

## Cross-Model Triage

When compilation errors or test failures overwhelm the context window of one model, use a different model to analyze and plan:

> "I took the file of compilation errors and threw it into Gemini, asking Gemini to create a plan for Ralph."

This cross-model approach leverages different models' strengths. One model may be better at generating code, another at analyzing error output and producing structured plans.

## The TODO List As Recovery Tool

The TODO list (fix_plan.md) serves as both a planning mechanism and a recovery tool:

- When Ralph goes off track, regenerate the TODO list with explicit instructions
- Use subagents to compare current code against specifications
- Search for TODO markers, minimal implementations, and placeholders
- Sort items by priority based on dependency analysis

```
Study @fix_plan.md (it may be incorrect) and use up to 500 subagents
to study existing source code and compare it against the compiler
specifications. From that create/update a @fix_plan.md which is a
bullet point list sorted in priority of items yet to be implemented.
Consider searching for TODO, minimal implementations and placeholders.
```

## Placeholder Detection Loops

Run dedicated Ralph loops to identify placeholder and minimal implementations:

1. Instruct Ralph to search the codebase for TODO markers, stub functions, and incomplete implementations
2. Transform findings into a prioritized TODO list
3. Run a separate Ralph loop focused on replacing placeholders with full implementations

This two-phase approach separates discovery from implementation, keeping context windows focused.

## Specification Audits

When Ralph produces wrong output, audit the specifications before blaming the agent:

- Check for contradictory requirements (e.g., a keyword defined twice for opposing scenarios)
- Verify that specifications are unambiguous and complete
- Ensure technical patterns in the standard library align with specifications

A hard lesson from building CURSED: a specification error defining a keyword twice for two opposing scenarios resulted in significant wasted time. The operator's responsibility is to ensure specifications are correct.

## Loop-Back Evaluation

Program Ralph to evaluate its own output and feed results back into the loop:

- Instruct Ralph to add logging for debugging issues
- Ask Ralph to compile and examine intermediate representations (e.g., LLVM IR)
- Have Ralph compare generated code against specifications before committing

```
You may add extra logging if required to be able to debug the issues.
```

## Git Commit Discipline

Build commit discipline into the loop so that known-good states are always available:

```
When the tests pass update the @fix_plan.md, then add changed code and
@fix_plan.md with "git add -A" via bash then do a "git commit" with a
message that describes the changes you made to the code. After the
commit do a "git push" to push the changes to the remote repository.

As soon as there are no build or test errors create a git tag. If there
are no git tags start at 0.0.0 and increment patch by 1 for example
0.0.1 if 0.0.0 does not exist.
```

This ensures that every working state is tagged and available for rollback.

## Recovery Decision Framework

When faced with a broken codebase, use this decision framework:

1. **How many errors?** If errors fill the context window → git reset
2. **Are errors localized?** If one module → rescue prompt targeting that module
3. **Is the direction wrong?** If architectural decisions are fundamentally flawed → git reset with new specs
4. **Are there placeholders?** Run placeholder detection loop, then implementation loop
5. **Are specs correct?** Audit specifications before continuing

## The Human Engineer's Role

Recovery is where the human engineer's expertise matters most. Ralph cannot always fix itself. The operator must:

- Judge whether to reset or repair
- Craft rescue prompts based on understanding of the system
- Identify when specifications need correction
- Make architectural decisions that Ralph cannot make alone
- Know when to throw out the TODO list and start fresh

> "Having said all of that, engineers are still needed. There is no way this is possible without senior expertise guiding Ralph."
