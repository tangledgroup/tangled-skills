# Signatures

A **signature** is a declarative specification of input/output behavior. Unlike function signatures that merely describe types, DSPy signatures declare and initialize module behavior. Field names carry semantic meaning: `question` differs from `answer`, `sql_query` differs from `python_code`. The optimizer uses these names to generate appropriate prompts.

## Inline Signatures

Define signatures as short strings with argument names and optional types. Default type is `str`.

```python
# Question answering
qa = dspy.Predict("question -> answer")

# Sentiment classification
classify = dspy.Predict("sentence -> sentiment: bool")

# Summarization
summarize = dspy.ChainOfThought("document -> summary")

# Multiple inputs and outputs
rag = dspy.ChainOfThought("context: list[str], question: str -> answer: str")
mcq = dspy.Predict("question, choices: list[str] -> reasoning: str, selection: int")
```

Any valid Python variable name works as a field name. Use semantically meaningful names but start simple — leave keyword optimization to the DSPy compiler.

### Adding Instructions at Runtime

Use `dspy.Signature` with an `instructions` argument:

```python
toxicity = dspy.Predict(
    dspy.Signature(
        "comment -> toxic: bool",
        instructions="Mark as 'toxic' if the comment includes insults, harassment, or sarcastic derogatory remarks.",
    )
)
```

## Class-Based Signatures

For more control, define a class with explicit fields and instructions:

```python
class GenerateTweet(dspy.Signature):
    """Generate an engaging tweet that answers the given question."""

    question = dspy.InputField()
    answer = dspy.InputField()
    tweet = dspy.OutputField(desc="A self-contained, engaging tweet under 280 chars")
```

Use the class directly with any module:

```python
generate = dspy.ChainOfThought(GenerateTweet)
result = generate(question="What is Python?", answer="A programming language.")
print(result.tweet)
```

## InputField and OutputField

Both are thin wrappers around `pydantic.Field` that mark fields as inputs or outputs.

**Parameters:**

- `prefix`: The label shown in the prompt (defaults to field name)
- `desc`: A description used by optimizers to understand the field's purpose
- Type annotation: Python type for structured output (`bool`, `int`, `list[str]`, `Literal[...]`)

```python
from typing import Literal

class Classify(dspy.Signature):
    text = dspy.InputField()
    label: Literal["spam", "ham", "promo"] = dspy.OutputField(
        desc="The category of the text"
    )
```

## Signature Polymorphism

A key DSPy feature: the same signature syntax works across all modules. `dspy.Predict`, `dspy.ChainOfThought`, `dspy.ReAct`, and others all accept the same signature format, but implement it differently internally. This is called **signature polymorphism**.

```python
sig = "question -> answer"

predict = dspy.Predict(sig)            # Direct prediction
cot = dspy.ChainOfThought(sig)         # Step-by-step reasoning
react = dspy.ReAct(sig, tools=[...])   # Tool-using agent
```

## Signature Operations

Signatures support programmatic manipulation:

```python
# Append a field to an existing signature
new_sig = old_sig.append("reasoning", InputField(prefix="Reasoning:"))

# Prepend a field
new_sig = old_sig.prepend("context", InputField())
```

These operations are used internally by modules like `MultiChainComparison` to dynamically extend signatures.

## Type Annotations

DSPy supports Python type hints in signatures for structured output:

```python
# Inline types
qa = dspy.Predict("question: str -> answer: str, confidence: float")

# Class with types
from typing import Literal
class MultiLabel(dspy.Signature):
    text: str = dspy.InputField()
    categories: list[str] = dspy.OutputField(desc="List of applicable categories")
    primary: Literal["spam", "ham"] = dspy.OutputField()
```

The adapter translates these types into appropriate LM instructions and parsing logic.
