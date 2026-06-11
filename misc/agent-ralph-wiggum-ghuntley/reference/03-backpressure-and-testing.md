# Backpressure and Testing

## What Is Backpressure

Backpressure is the validation mechanism wired into the Ralph loop that rejects invalid code generation. While code generation is now cheap, ensuring that Ralph has generated the right thing is hard. Backpressure is where you put your engineering hat on.

In Huntley's diagrams, this phase is labeled "test and build," but anything can serve as backpressure:

- Type systems (compiled languages)
- Test suites
- Static analyzers
- Security scanners
- Custom validation scripts

The key collective sum is that the wheel has got to turn fast. Slow backpressure means more iterations before feedback, which means more tokens burned on wrong paths.

## Type Systems as Built-In Backpressure

Specific programming languages have built-in backpressure through their type systems. The choice of language involves a tradeoff between correctness and iteration speed:

- **Rust**: Extreme correctness through its type system, but slow compilation speed. LLMs are not very good at generating perfect Rust code in one attempt, meaning more iterations are needed. This can be positive (more feedback cycles) or negative (slower overall progress).
- **Dynamically typed languages**: Faster iteration but require additional backpressure mechanisms like static analyzers.

The speed of the wheel turning matters, balanced against the axis of correctness. Which language to use requires experimentation for your specific project.

## Static Analysis for Dynamic Languages

If using a dynamically typed language, wiring in a static analyzer or type checker is essential:

- **Dialyzer** for Erlang/Elixir
- **Pyrefly** (or mypy) for Python
- **Flow** or **TypeScript** for JavaScript

Without static analysis on dynamic languages, you will run into "a bonfire of outcomes" — accumulated type errors and logic bugs that compound across iterations.

## Unit Testing Per Loop

A staple of the Ralph technique: after making a change, run tests just for the unit of code that was implemented and improved:

```
After implementing functionality or resolving problems, run the tests
for that unit of code that was improved.
```

This targeted approach keeps feedback fast. Running the entire test suite every loop may be too slow — focus on what changed.

## Capturing Test Importance

Because each loop iteration starts with a fresh context window, future iterations will not remember why a particular test exists. Instruct Ralph to document the importance of tests at the moment they are written:

```
Important: When authoring documentation capture the why tests and the
backing implementation is important.
```

In practice, this means tests include docstrings or comments explaining what they verify and why it matters:

```elixir
@doc """
Tests that the QueryOptimizer initializes the required ETS tables.

This test ensures that the init function properly creates the ETS tables
needed for caching and statistics tracking. This is fundamental to the
module's operation.
"""
test "creates required ETS tables" do
  # ...
end
```

This helps future LLM iterations decide if a test is no longer relevant, if it is important, and whether to delete, modify, or resolve a test failure.

## Handling Unrelated Test Failures

Instruct Ralph to take responsibility for all test failures, not just those related to its current work:

```
If tests unrelated to your work fail then it's your job to resolve these
tests as part of the increment of change.
```

This prevents test debt from accumulating across iterations. Each loop should leave the test suite in at least as good a state as it found it.

## Anti-Placeholder Testing

LLMs have an inherent bias toward minimal implementations that compile but do not fully satisfy specifications. Counter this with explicit directives:

```
If functionality is missing then it's your job to add it as per the
application specifications. Think hard.

DO NOT IMPLEMENT PLACEHOLDER OR SIMPLE IMPLEMENTATIONS. WE WANT FULL
IMPLEMENTATIONS.
```

In early iterations, Ralph may ignore these signs. The models chase their reward function, and compiling code is the primary reward. You can always run additional Ralph loops specifically to identify placeholders and transform findings into a TODO list for future iterations.

## Backpressure Design Principles

When designing backpressure for your Ralph loop:

1. **Speed matters**: Fast feedback loops are more valuable than comprehensive but slow validation
2. **Layer multiple checks**: Combine type systems, unit tests, static analysis, and integration tests
3. **Target what changed**: Run tests specific to modified code rather than full suites
4. **Document the why**: Every test should explain its purpose for future iterations
5. **Resolve all failures**: Do not let unrelated test failures accumulate

## The Tradeoff Surface

Backpressure design is a tradeoff surface with multiple axes:

- **Correctness vs. Speed**: More thorough validation catches more issues but slows iteration
- **Breadth vs. Depth**: Full test suites vs. targeted unit tests
- **Static vs. Dynamic**: Compile-time checks vs. runtime assertions
- **Automated vs. Manual**: Everything in the loop vs. periodic human review

The right balance depends on your project's requirements, language choice, and tolerance for broken intermediate states.
