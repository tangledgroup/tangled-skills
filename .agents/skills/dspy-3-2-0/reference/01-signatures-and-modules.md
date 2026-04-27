# Signatures & Modules

## What Are Signatures?

A **signature** is a declarative specification of input/output behavior. It tells the LM *what* to do without specifying *how* to prompt it. Unlike function signatures that merely describe types, DSPy signatures declare and initialize module behavior.

Field names carry semantic meaning: `question` differs from `answer`, `sql_query` differs from `python_code`. The optimizer uses these names to generate appropriate prompts.

### Defining Signatures

Use the short string notation for simple cases:

```python
# Question answering
qa = dspy.Predict("question -> answer")

# Sentiment classification
classify = dspy.Predict("sentence -> sentiment: bool")

# Summarization
summarize = dspy.ChainOfThought("document -> summary")
```

Multiple inputs and outputs:

```python
# RAG with context
rag = dspy.ChainOfThought("context: list[str], question: str -> answer: str")

# Multiple-choice with reasoning
mcq = dspy.Predict("question, choices: list[str] -> reasoning: str, selection: int")
```

### Full Signature Class

For more control, define a class with explicit fields and instructions:

```python
class GenerateTweet(dspy.Signature):
    """Generate an engaging tweet that answers the given question."""

    question = dspy.InputField()
    answer = dspy.InputField()
    tweet = dspy.OutputField(desc="A self-contained, engaging tweet under 280 chars")
```

Add instructions at runtime:

```python
toxicity = dspy.Predict(
    dspy.Signature(
        "comment -> toxic: bool",
        instructions="Mark as 'toxic' if the comment includes insults, harassment, or sarcastic derogatory remarks.",
    )
)
```

### InputField and OutputField

Both accept:

- `prefix`: The label shown in the prompt (defaults to field name)
- `desc`: A description used by optimizers to understand the field's purpose
- `type_`: Python type for structured output (`bool`, `int`, `list[str]`, `Literal[...]`)

```python
class Classify(dspy.Signature):
    from typing import Literal
    text = dspy.InputField()
    label: Literal["spam", "ham", "promo"] = dspy.OutputField(
        desc="The category of the text"
    )
```

## What Are Modules?

A **module** is a building block that abstracts a prompting technique. Each module:

- Takes a signature as input
- Has learnable parameters (instructions, demonstrations, LM weights)
- Can be composed into larger programs
- Is optimized by DSPy optimizers

### Core Modules

**dspy.Predict** — Basic predictor. Does not modify the signature. Stores instructions, demonstrations, and handles learning updates.

```python
classify = dspy.Predict("sentence -> sentiment: bool")
result = classify(sentence="It's a charming journey.")
print(result.sentiment)  # True
```

**dspy.ChainOfThought** — Teaches the LM to reason step-by-step before producing output. Internally adds a `reasoning` field to the signature.

```python
summarize = dspy.ChainOfThought("document -> summary")
result = summarize(document=long_text)
print(result.reasoning)  # Internal reasoning steps
print(result.summary)    # Final output
```

**dspy.ProgramOfThought** — Teaches the LM to output code whose execution results dictate the response.

**dspy.ReAct** — An agent module that can use tools to implement the given signature. Supports function calling and tool use.

```python
def search(query: str) -> list[str]:
    """Search Wikipedia for relevant documents."""
    ...

agent = dspy.ReAct("question -> answer", tools=[search])
result = agent(question="Who won the 2024 Nobel Prize in Physics?")
```

**dspy.MultiChainComparison** — Compares multiple ChainOfThought outputs to produce a final prediction. Used internally by some optimizers.

**dspy.RLM** — Recursive Language Model that explores large contexts through sandboxed Python REPL with recursive sub-LLM calls.

### Composition: Building Programs

Modules compose into programs using `dspy.Module`:

```python
class RAG(dspy.Module):
    def __init__(self, num_docs=5):
        super().__init__()
        self.retrieve = dspy.Retrieve(k=num_docs)
        self.generate_answer = dspy.ChainOfThought("context, question -> answer")

    def forward(self, question):
        context = self.retrieve(question).passages
        return self.generate_answer(context=context, question=question)
```

Key patterns:

- `dspy.Parallel` — Run multiple modules in parallel
- `dspy.BestOfN` — Generate N candidates and select the best
- `dspy.Refine` — Iteratively refine outputs with constraint checking
- `dspy.majority` — Vote across multiple predictions

### Module Parameters

Each predictor within a module has learnable parameters:

- **Instructions**: The natural-language task description
- **Demos**: Few-shot examples shown in the prompt
- **LM weights**: When fine-tuned via BootstrapFinetune

Access predictors:

```python
for name, predictor in my_program.named_predictors():
    print(f"{name}: {predictor.signature.instructions}")
    print(f"  demos: {len(predictor.demos)}")
```

### Adapters

Adapters control how signatures are rendered into actual prompts. DSPy provides several:

- **ChatAdapter** (default) — Renders as a chat conversation with system/user/assistant messages
- **XMLAdapter** — Wraps fields in XML tags
- **JSONAdapter** — Structured JSON output format
- **TwoStepAdapter** — Two-stage generation for complex tasks

```python
# Use a specific adapter
pred = dspy.Predict("question -> answer", adapter=dspy.XMLAdapter())
```

### Tools and MCP

DSPy supports external tools via the `dspy.Tool` primitive and Model Context Protocol (MCP) integration:

```python
my_tool = dspy.Tool(
    name="calculator",
    description="Evaluate a math expression",
    json_schema={"type": "object", "properties": {"expression": {"type": "string"}}}
)

agent = dspy.ReAct("question -> answer", tools=[my_tool])
```
