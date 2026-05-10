---
name: dspy-3-2-0
description: Framework for programming rather than prompting language models. Compiles LM calls into self-improving pipelines by tuning prompts or weights to maximize user-defined metrics. Use when building classifiers, RAG pipelines, agents, or any multi-stage LM program requiring automated prompt engineering or model fine-tuning driven by evaluation metrics.
license: MIT
author: Tangled <noreply@tangledgroup.com>
version: "0.1.0"
tags:
  - llm-programming
  - prompt-optimization
  - ai-compilation
  - few-shot-learning
  - instruction-tuning
  - agent-framework
  - meta-prompting
category: ai-framework
external_references:
  - https://github.com/stanfordnlp/dspy
  - https://github.com/stanfordnlp/dspy/tree/main/docs/docs
  - https://dspy.ai/
---

# DSPy 3.2.0

## Overview

DSPy (Declarative Self-improving Python) is the framework for **programming—rather than prompting—language models**. Instead of writing brittle, hand-crafted prompts, you write compositional Python code using declarative modules and let DSPy's optimizers teach your language model to deliver high-quality outputs.

DSPy provides three core abstractions:

- **Signatures** — Declarative specifications of input/output behavior that tell the LM _what_ to do without specifying _how_.
- **Modules** — Building blocks that abstract prompting techniques (chain-of-thought, ReAct, program-of-thought) and can be composed into larger programs.
- **Optimizers** — Algorithms that tune prompts and/or LM weights to maximize user-defined metrics like accuracy.

Think of DSPy as a higher-level language for AI programming, similar to the shift from assembly to C or from pointer arithmetic to SQL. It works with any LLM provider supported by LiteLLM (OpenAI, Anthropic, Google, local models via Ollama/SGLang, and dozens more).

## When to Use

- Building **classifiers** that need automated prompt optimization instead of manual tuning
- Creating **RAG pipelines** where retrieval and generation steps benefit from compiled prompts
- Implementing **agent loops** (ReAct, ProgramOfThought) with tools and self-correction
- Any multi-stage LM program where you want to optimize few-shot examples, instructions, or model weights driven by evaluation metrics
- Migrating from hand-crafted prompt chains to modular, optimizable AI software
- Fine-tuning small LMs on task-specific data using DSPy's BootstrapFinetune optimizer

## Installation

```bash
pip install dspy
```

To install the latest from `main`:

```bash
pip install git+https://github.com/stanfordnlp/dspy.git
```

## Core Concepts

### Signatures

A **Signature** is a declarative specification of input/output behavior. Instead of writing prompts, you define what inputs go in and what outputs come out.

**Inline signatures** use short string notation:

```python
import dspy

# Question answering
classify = dspy.Predict("question -> answer")

# Sentiment classification
classify = dspy.Predict("sentence -> sentiment: bool")

# Multi-field with types
classify = dspy.Predict("context: list[str], question: str -> answer: str")
```

**Class-based signatures** provide more control for advanced tasks:

```python
from typing import Literal

class Emotion(dspy.Signature):
    """Classify emotion in the given sentence."""

    sentence: str = dspy.InputField()
    sentiment: Literal['sadness', 'joy', 'love', 'anger', 'fear', 'surprise'] = dspy.OutputField()

classify = dspy.Predict(Emotion)
result = classify(sentence="i started feeling vulnerable")
print(result.sentiment)  # 'fear'
```

You can add instructions and field descriptions:

```python
toxicity = dspy.Predict(
    dspy.Signature(
        "comment -> toxic: bool",
        instructions="Mark as 'toxic' if the comment includes insults, harassment, or sarcastic remarks.",
    ),
)
```

### Modules

A **Module** is a building block that abstracts a prompting technique. All built-in modules handle any signature you give them.

- **`dspy.Predict`** — Basic predictor; does not modify the signature
- **`dspy.ChainOfThought`** — Adds step-by-step reasoning before the output
- **`dspy.ProgramOfThought`** — Generates code, executes it, uses results for the answer
- **`dspy.ReAct`** — Agent that can use tools to implement the signature
- **`dspy.MultiChainComparison`** — Compares multiple ChainOfThought outputs
- **`dspy.CodeAct`** — Agent with tool-use via code generation
- **`dspy.RLM`** — Recursive Language Model for large contexts via sandboxed Python REPL

**Using modules:**

```python
# 1) Declare with a signature
classify = dspy.ChainOfThought("question -> answer", temperature=0.7)

# 2) Call with inputs
response = classify(question="What's great about ColBERT?")

# 3) Access outputs (ChainOfThought adds 'reasoning' field)
print(response.reasoning)
print(response.answer)
```

**Composing modules into programs:**

```python
class RAG(dspy.Module):
    def __init__(self, num_docs=5):
        super().__init__()
        self.num_docs = num_docs
        self.retrieve = dspy.Retrieve(k=num_docs)
        self.respond = dspy.ChainOfThought("context, question -> response")

    def forward(self, question):
        context = self.retrieve(question).passages
        return self.respond(context=context, question=question)

# Use the composed program
rag = RAG()
result = rag(question="When was the first FIFA World Cup?")
```

### Language Models

Configure DSPy with any LM supported by LiteLLM:

```python
import dspy

# OpenAI
lm = dspy.LM("openai/gpt-4o-mini")
dspy.configure(lm=lm)

# Anthropic
lm = dspy.LM("anthropic/claude-sonnet-4-5-20250929")
dspy.configure(lm=lm)

# Local via Ollama
lm = dspy.LM("ollama_chat/llama3.2:1b", api_base="http://localhost:11434", api_key="")
dspy.configure(lm=lm)
```

### Optimizers (Teleprompters)

An **Optimizer** tunes the parameters of a DSPy program (prompts and/or LM weights) to maximize your metric. All optimizers share a common interface:

```python
optimizer = dspy.<OptimizerName>(metric=your_metric, **config)
optimized_program = optimizer.compile(your_program, trainset=trainset)
```

**Available optimizers:**

- **`LabeledFewShot`** — Constructs few-shot examples from labeled data. Simple, no bootstrapping.
- **`BootstrapFewShot`** — Self-generates demonstrations for every module step, validated by your metric.
- **`BootstrapFewShotWithRandomSearch`** — Runs BootstrapFewShot multiple times with random search over demonstrations.
- **`KNNFewShot`** — Uses k-Nearest Neighbors to find the most relevant training examples per query.
- **`COPRO`** — Generates and refines instructions via coordinate ascent (hill-climbing).
- **`MIPROv2`** — Data-aware instruction generation with Bayesian Optimization over instructions and demonstrations. Best for 50+ examples.
- **`SIMBA`** — Identifies challenging examples with high output variability, then generates self-reflective improvement rules.
- **`GEPA`** — Reflective prompt evolution; the LM analyzes its own trajectory to propose improvements. Can outperform RL on many tasks.
- **`BootstrapFinetune`** — Distills a prompt-based DSPy program into weight updates for fine-tuning small LMs.
- **`Ensemble`** — Combines multiple DSPy programs into one.
- **`BetterTogether`** — Meta-optimizer that sequences prompt optimization and weight optimization.

**Choosing an optimizer:**

- ~10 examples → `BootstrapFewShot`
- 50+ examples → `BootstrapFewShotWithRandomSearch`
- Instruction-only (0-shot) → `MIPROv2` configured for 0-shot
- 200+ examples, long optimization → `MIPROv2` with many trials
- Need efficient small LM → `BootstrapFinetune`

### Evaluation

Define metrics as functions that take gold examples and predictions:

```python
def gsm8k_metric(example, pred, trace=None):
    return int(parse_integer(str(example.answer))) == int(parse_integer(str(pred.answer)))
```

Run evaluations with DSPy's built-in evaluator:

```python
from dspy.evaluate import Evaluate

evaluate = Evaluate(devset=devset, metric=gsm8k_metric, num_threads=4, display_progress=True)
evaluate(your_program)
```

DSPy also provides LLM-as-judge metrics:

```python
class FactJudge(dspy.Signature):
    """Judge if the answer is factually correct based on the context."""
    context = dspy.InputField(desc="Context for the prediction")
    question = dspy.InputField()
    answer = dspy.InputField()
    factually_correct: bool = dspy.OutputField()

judge = dspy.ChainOfThought(FactJudge)

# Built-in metrics
metric = dspy.evaluate.answer_exact_match   # exact string match
metric = dspy.SemanticF1()                  # LLM-based semantic F1 score
```

## Usage Examples

### Example 1: Simple Classification

```python
import dspy

dspy.configure(lm=dspy.LM("openai/gpt-4o-mini"))

class Sentiment(dspy.Signature):
    """Classify the sentiment of a sentence."""
    sentence: str = dspy.InputField()
    sentiment: str = dspy.OutputField(desc="positive, negative, or neutral")

classify = dspy.Predict(Sentiment)
result = classify(sentence="This product exceeded my expectations!")
print(result.sentiment)  # 'positive'
```

### Example 2: RAG Pipeline

```python
import dspy

dspy.configure(lm=dspy.LM("openai/gpt-4o-mini"))

# Configure a retrieval model
rm = dspy.ColBERTv2(url='http://20.102.90.50:2017/wiki17_abstracts')
dspy.configure(rm=rm)

class RAG(dspy.Module):
    def __init__(self, num_docs=3):
        super().__init__()
        self.retrieve = dspy.Retrieve(k=num_docs)
        self.generate = dspy.ChainOfThought("context, question -> answer")

    def forward(self, question):
        context = self.retrieve(question).passages
        return self.generate(context=context, question=question)

rag = RAG()
result = rag(question="What castle did David Gregory inherit?")
print(result.answer)
```

### Example 3: ReAct Agent with Tools

```python
import dspy

dspy.configure(lm=dspy.LM("openai/gpt-4o-mini"))

def search_wikipedia(query: str) -> list[str]:
    """Search Wikipedia for relevant passages."""
    results = dspy.ColBERTv2(url='http://20.102.90.50:2017/wiki17_abstracts')(query, k=3)
    return [x['text'] for x in results]

react = dspy.ReAct("question -> answer", tools=[search_wikipedia])
result = react(question="What is the population of Paris divided by 2?")
print(result.answer)
```

### Example 4: Optimizing a Program

```python
import dspy
from dspy.datasets import HotPotQA

dspy.configure(lm=dspy.LM("openai/gpt-4o-mini"))

# Build a simple program
qa = dspy.ChainOfThought("question -> answer")

# Prepare training data
trainset = [x.with_inputs("question") for x in HotPotQA(train_seed=2024, train_size=500).train]

# Optimize with BootstrapFewShot
optimizer = dspy.BootstrapFewShot(
    metric=dspy.evaluate.answer_exact_match,
    max_bootstrapped_demos=4,
    max_labeled_demos=4,
)
optimized_qa = optimizer.compile(qa, trainset=trainset)

# Use the optimized program
result = optimized_qa(question="What is the capital of France?")
print(result.answer)
```

### Example 5: ProgramOfThought for Math

```python
import dspy

dspy.configure(lm=dspy.LM("openai/gpt-4o-mini"))

pot = dspy.ProgramOfThought("question -> answer: float")

result = pot(question="Two dice are tossed. What is the probability that the sum equals two?")
print(result.answer)  # 0.0278 (1/36)
```

## Tips and Best Practices

- **Start simple** — Begin with `dspy.Predict` and a basic signature. Swap to `ChainOfThought` if quality is insufficient.
- **Don't over-engineer signatures** — Field names should be semantically meaningful but start simple. Let the DSPy compiler optimize keywords rather than hand-tuning them.
- **Invest in metrics** — A well-defined metric is the foundation of optimization. Start simple and iterate.
- **Small data works** — DSPy optimizers can produce strong results with as few as 5–10 training examples.
- **Compose optimizers** — Run one optimizer, then use its output as input to another (e.g., MIPROv2 → BootstrapFinetune via BetterTogether).
- **Use `teacher_settings`** — Compile with a stronger LM than you deploy with, by passing `teacher_settings=dict(lm=stronger_lm)`.

## References

- DSPy Documentation: <https://dspy.ai/>
- GitHub Repository: <https://github.com/stanfordnlp/dspy>
- DSPy Paper (ICLR 2024): "DSPy: Compiling Declarative Language Model Calls into Self-Improving Pipelines" — <https://arxiv.org/abs/2310.03714>
- GEPA Paper: "Reflective Prompt Evolution Can Outperform Reinforcement Learning" — <https://arxiv.org/abs/2507.19457>
- DSPy Discord: <https://discord.gg/XCGy2WDCQB>
