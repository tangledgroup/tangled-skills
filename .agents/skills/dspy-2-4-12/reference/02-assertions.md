# DSPy Assertions

## Contents
- Overview
- dspy.Assert vs dspy.Suggest
- How Backtracking Works
- Using Assertions in Programs
- Activating Assertions

## Overview

**DSPy Assertions** automate the enforcement of computational constraints on LM outputs. They empower developers to guide LMs towards desired outcomes with minimal manual intervention, enhancing reliability, predictability, and correctness.

Two primary constructs:

- **`dspy.Assert`** — Hard constraint; initiates retry upon failure. If failures persist past `max_backtracking_attempts`, halts execution and raises `dspy.AssertionError`.
- **`dspy.Suggest`** — Soft constraint; encourages self-refinement through retries without enforcing hard stops. Logs failures after max backtracking and continues execution.

## dspy.Assert vs dspy.Suggest

| Aspect | `dspy.Assert` | `dspy.Suggest` |
|--------|---------------|----------------|
| Failure behavior | Halts with `AssertionError` | Logs and continues |
| Best for | Development ("checkers") | Evaluation ("helpers") |
| Backtracking | Yes | Yes |
| Hard stop | After max retries | Never |

Unlike conventional Python `assert` statements that terminate the program, `dspy.Assert` conducts a sophisticated retry mechanism allowing the pipeline to adjust.

## How Backtracking Works

When a constraint is not met:

1. **Backtracking Mechanism** — Under-the-hood backtracking is initiated, offering the model a chance to self-refine.
2. **Dynamic Signature Modification** — Internally modifies your DSPy program's Signature by adding:
   - **Past Output**: The model's past output that failed validation
   - **Instruction**: Your user-defined feedback message on what went wrong

If the error continues past `max_backtracking_attempts`, `dspy.Assert` halts with an `AssertionError`.

## Using Assertions in Programs

Define validation checks as boolean functions or expressions:

```python
# Simple boolean check
len(query) <= 100

# Python function for validation
def validate_query_distinction_local(previous_queries, query):
    """Check if query is distinct from previous queries."""
    if previous_queries == []:
        return True
    if dspy.evaluate.answer_exact_match_str(query, previous_queries, frac=0.8):
        return False
    return True
```

Include assertions in your program after the relevant module calls:

```python
class SimplifiedBaleenAssertions(dspy.Module):
    def __init__(self, passages_per_hop=2, max_hops=2):
        super().__init__()
        self.generate_query = [dspy.ChainOfThought(GenerateSearchQuery) for _ in range(max_hops)]
        self.retrieve = dspy.Retrieve(k=passages_per_hop)
        self.generate_answer = dspy.ChainOfThought(GenerateAnswer)
        self.max_hops = max_hops

    def forward(self, question):
        context = []
        prev_queries = [question]

        for hop in range(self.max_hops):
            query = self.generate_query[hop](context=context, question=question).query

            dspy.Suggest(
                len(query) <= 100,
                "Query should be short and less than 100 characters",
            )

            dspy.Suggest(
                validate_query_distinction_local(prev_queries, query),
                "Query should be distinct from: "
                + "; ".join(f"{i+1}) {q}" for i, q in enumerate(prev_queries)),
            )

            prev_queries.append(query)
            passages = self.retrieve(query).passages
            context = deduplicate(context + passages)

        pred = self.generate_answer(context=context, question=question)
        return dspy.Prediction(context=context, answer=pred.answer)
```

## Activating Assertions

Transform your program to wrap it with internal assertions backtracking and retry logic:

```python
from dspy.primitives.assertions import assert_transform_module, backtrack_handler
import functools

# Method 1: Using activate_assertions (default max_backtracks=2)
baleen_with_assertions = SimplifiedBaleenAssertions().activate_assertions()

# Method 2: Manual transform with custom settings
baleen_with_assertions = assert_transform_module(
    SimplifiedBaleenAssertions(),
    backtrack_handler,
)

# Method 3: Custom max backtracks
baleen_retry_once = assert_transform_module(
    SimplifiedBaleenAssertions(),
    functools.partial(backtrack_handler, max_backtracks=1),
)
```

The `backtrack_handler` is parameterized over settings for the backtracking mechanism. Default `max_backtracks=2`.
