# Typed Predictors

## Contents
- Overview
- Defining Input and Output Models
- Creating Typed Predictors
- Typed Chain of Thought
- Decorator-Style Typed Predictors
- Composing Functional Typed Predictors in Modules
- Optimizing Typed Predictors

## Overview

In DSPy Signatures, `InputField` and `OutputField` define the nature of inputs and outputs. However, values are always `str`-typed, which requires input/output string processing.

**Typed Predictors** resolve this by enforcing type constraints on inputs and outputs via Pydantic `BaseModel`, enabling structured I/O with automatic validation.

## Defining Input and Output Models

Define Pydantic models for your inputs and outputs:

```python
from pydantic import BaseModel, Field
import dspy

class Input(BaseModel):
    context: str = Field(description="The context for the question")
    query: str = Field(description="The question to be answered")

class Output(BaseModel):
    answer: str = Field(description="The answer for the question")
    confidence: float = Field(ge=0, le=1, description="Confidence score for the answer")
```

## Creating Typed Predictors

Create a **Typed Signature** that references your Pydantic models:

```python
class QASignature(dspy.Signature):
    """Answer the question based on the context and query provided."""

    input: Input = dspy.InputField()
    output: Output = dspy.OutputField()
```

Then use `dspy.TypedPredictor`:

```python
predictor = dspy.TypedPredictor(QASignature)

doc_query_pair = Input(
    context="The quick brown fox jumps over the lazy dog",
    query="What does the fox jump over?",
)

prediction = predictor(input=doc_query_pair)

# Access typed outputs
answer = prediction.output.answer              # str
confidence_score = prediction.output.confidence  # float
```

**String signature syntax:**

```python
predictor = dspy.TypedPredictor("input:Input -> output:Output")
```

## Typed Chain of Thought

Use `dspy.TypedChainOfThought` for chain-of-thought reasoning with typed I/O:

```python
cot_predictor = dspy.TypedChainOfThought(QASignature)

doc_query_pair = Input(
    context="The quick brown fox jumps over the lazy dog",
    query="What does the fox jump over?",
)

prediction = cot_predictor(input=doc_query_pair)
```

## Decorator-Style Typed Predictors

Use `@dspy.predictor` and `@dspy.cot` decorators for concise typed modules:

```python
@dspy.predictor
def answer(doc_query_pair: Input) -> Output:
    """Answer the question based on context and query."""
    pass

@dspy.cot
def answer_with_reasoning(doc_query_pair: Input) -> Output:
    """Answer the question with step-by-step reasoning."""
    pass

prediction = answer(doc_query_pair=doc_query_pair)
```

## Composing Functional Typed Predictors in Modules

Use decorators within `FunctionalModule` subclasses for full pipeline composition:

```python
from dspy.functional import FunctionalModule, cot

class SimplifiedBaleen(FunctionalModule):
    def __init__(self, passages_per_hop=3, max_hops=1):
        super().__init__()
        self.retrieve = dspy.Retrieve(k=passages_per_hop)
        self.max_hops = max_hops

    @cot
    def generate_query(self, context: list[str], question: str) -> str:
        """Write a simple search query that will help answer a complex question."""
        pass

    @cot
    def generate_answer(self, context: list[str], question: str) -> str:
        """Answer questions with short factoid answers."""
        pass

    def forward(self, question):
        context = []

        for _ in range(self.max_hops):
            query = self.generate_query(context=context, question=question)
            passages = self.retrieve(query).passages
            context = deduplicate(context + passages)

        answer = self.generate_answer(context=context, question=question)
        return dspy.Prediction(context=context, answer=answer)
```

## Optimizing Typed Predictors

Typed predictors can be optimized on Signature instructions through the `optimize_signature` optimizer:

```python
from dspy.teleprompt.signature_opt_typed import optimize_signature
from dspy.evaluate import Evaluate
from dspy.evaluate.metrics import answer_exact_match

turbo = dspy.OpenAI(model='gpt-3.5-turbo', max_tokens=4000)
gpt4 = dspy.OpenAI(model='gpt-4', max_tokens=4000)
dspy.configure(lm=turbo)

evaluator = Evaluate(devset=devset, metric=answer_exact_match, num_threads=10, display_progress=True)

result = optimize_signature(
    student=dspy.TypedPredictor(QASignature),
    evaluator=evaluator,
    initial_prompts=6,
    n_iterations=100,
    max_examples=30,
    verbose=True,
    prompt_model=gpt4,
)
```

Or use the simpler functional form:

```python
from dspy.functional import TypedChainOfThought

compiled_program = optimize_signature(
    student=TypedChainOfThought("question -> answer"),
    evaluator=Evaluate(devset=devset, metric=answer_exact_match, num_threads=10, display_progress=True),
    n_iterations=50,
).program
```
