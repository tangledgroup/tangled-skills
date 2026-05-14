---
name: dspy-2-4-12
description: Framework for programming rather than prompting language models. Compiles LM calls into self-improving pipelines by tuning prompts and/or weights to maximize user-defined metrics. Use when building classifiers, RAG pipelines, agents, or any multi-stage LM program requiring automated prompt engineering, few-shot bootstrapping, or model fine-tuning driven by evaluation metrics.
license: MIT
author: Tangled <noreply@tangledgroup.com>
version: "0.2.0"
tags:
  - llm-programming
  - prompt-optimization
  - ai-compilation
  - few-shot-learning
  - instruction-tuning
  - agent-framework
  - dspy
category: ai-framework
external_references:
  - https://github.com/stanfordnlp/dspy/tree/v2.4.12
---

# DSPy 2.4.12

## Overview

DSPy (Declarative Self-improving Python) is the framework for **programming—rather than prompting—language models**. Instead of writing brittle, hand-crafted prompts, you write compositional Python code using declarative modules and let DSPy's optimizers teach your language model to deliver high-quality outputs.

DSPy provides three core abstractions:

- **Signatures** — Declarative specifications of input/output behavior that tell the LM _what_ to do without specifying _how_.
- **Modules** — Building blocks that abstract prompting techniques (chain-of-thought, ReAct, program-of-thought) and can be composed into larger programs.
- **Optimizers** (formerly Teleprompters) — Algorithms that tune prompts and/or LM weights to maximize user-defined metrics like accuracy.

## When to Use

- Building **classifiers** that need automated prompt optimization instead of manual tuning
- Creating **RAG pipelines** where retrieval and generation steps benefit from compiled prompts
- Implementing **agent loops** (ReAct, ProgramOfThought) with tools and self-correction
- Any multi-stage LM program where you want to optimize few-shot examples, instructions, or model weights driven by evaluation metrics
- Fine-tuning small LMs on task-specific data using DSPy's BootstrapFinetune optimizer
- Enforcing computational constraints on LM outputs with **DSPy Assertions**
- Building typed LM programs with **TypedPredictor** for Pydantic-compatible structured outputs

## Installation

```bash
pip install dspy-ai
```

Optional extras:

```bash
pip install dspy-ai[chromadb]   # ChromaDB
pip install dspy-ai[qdrant]     # Qdrant
pip install dspy-ai[milvus]     # Milvus
pip install dspy-ai[pinecone]   # Pinecone
pip install dspy-ai[weaviate]   # Weaviate
pip install dspy-ai[faiss-cpu]  # FAISS
pip install dspy-ai[groq]       # Groq
```

## Core Concepts

### Signatures

A **Signature** is a declarative specification of input/output behavior.

**Inline signatures** use short string notation:

```python
import dspy

classify = dspy.Predict("question -> answer")
classify = dspy.Predict("sentence -> sentiment")
classify = dspy.Predict("context, question -> answer")
```

**Class-based signatures** provide more control with docstrings, field descriptions, and prefixes:

```python
class Emotion(dspy.Signature):
    """Classify emotion among sadness, joy, love, anger, fear, surprise."""
    sentence = dspy.InputField()
    sentiment = dspy.OutputField()

classify = dspy.Predict(Emotion)
result = classify(sentence="i started feeling a little vulnerable")
```

Fields support `desc` (description), `prefix` (placeholder text in the prompt), and `format` (handling non-string inputs).

### Modules

A **Module** is a building block that abstracts a prompting technique:

- **`dspy.Predict`** — Basic predictor; foundation all other modules build on
- **`dspy.ChainOfThought`** — Adds step-by-step reasoning before output
- **`dspy.ChainOfThoughtWithHint`** — Chain-of-thought with an additional hint input
- **`dspy.ProgramOfThought`** — Generates and executes Python code to solve problems
- **`dspy.ReAct`** — Agent with tool use (Thought/Action/Observation loop, max 1 output field)
- **`dspy.MultiChainComparison`** — Compares multiple ChainOfThought outputs
- **`dspy.majority`** — Voting over a set of predictions
- **`dspy.Retrieve(k=N)`** — Retrieves top-k passages from a configured retrieval model

**Composing modules into programs:**

```python
class RAG(dspy.Module):
    def __init__(self, num_passages=3):
        super().__init__()
        self.retrieve = dspy.Retrieve(k=num_passages)
        self.generate_answer = dspy.ChainOfThought("context, question -> answer")

    def forward(self, question):
        context = self.retrieve(question).passages
        return self.generate_answer(context=context, question=question)

rag = RAG()
result = rag(question="When was the first FIFA World Cup?")
```

DSPy programs are just Python code with any control flow you like — loops, conditionals, recursion. No special chaining abstractions needed.

### Language Models

Configure DSPy with provider-specific LM clients:

```python
import dspy

# OpenAI
gpt3 = dspy.OpenAI(model='gpt-3.5-turbo-1106', max_tokens=300)
dspy.configure(lm=gpt3)

# Cohere
cohere = dspy.Cohere(model='command')

# Anyscale (hosted Llama2)
anyscale = dspy.Anyscale(model='meta-llama/Llama-2-7b-chat-hf')

# Together
together = dspy.Together(model='togethercomputer/llama-2-7b')
```

**Local models:**

```python
tgi = dspy.HFClientTGI(model="mistralai/Mistral-7B-Instruct-v0.2", port=8080, url="http://localhost")
vllm = dspy.HFClientVLLM(model="mistralai/Mistral-7B-Instruct-v0.2", port=8080, url="http://localhost")
ollama = dspy.OllamaLocal(model='mistral')
hf = dspy.HFModel(model='mistralai/Mistral-7B-Instruct-v0.2')
```

**Using multiple LMs with context:**

```python
response = qa(question="How many floors are in the castle?")
print('GPT-3.5:', response.answer)

gpt4 = dspy.OpenAI(model='gpt-4-1106-preview', max_tokens=300)
with dspy.context(lm=gpt4):
    response = qa(question="How many floors are in the castle?")
    print('GPT-4:', response.answer)
```

**Generating multiple completions:** Use `n=5` in the module constructor or pass `config=dict(n=5)` when invoking. Access via `response.completions.answer`.

**Inspecting LM history:** Call `lm.inspect_history(n=3)` after running a program to see the last N prompts/responses.

### Retrieval Models

Configure a retrieval model for `dspy.Retrieve` to use:

```python
colbertv2 = dspy.ColBERTv2(url='http://20.102.90.50:2017/wiki17_abstracts')
dspy.configure(rm=colbertv2)

retriever = dspy.Retrieve(k=3)
passages = retriever("When was the first FIFA World Cup?").passages
```

Custom RM clients can inherit from `dspy.Retrieve` and implement a `forward` method returning `dspy.Prediction(passages=...)`.

### Optimizers (Teleprompters)

An **Optimizer** tunes program parameters to maximize your metric. Import from `dspy.teleprompt`:

```python
from dspy.teleprompt import BootstrapFewShot

optimizer = BootstrapFewShot(metric=your_metric)
optimized_program = optimizer.compile(student=your_program, trainset=trainset)
```

**Choosing an optimizer:**

- ~10 examples → `BootstrapFewShot`
- 50+ examples → `BootstrapFewShotWithRandomSearch`
- 300+ examples → `MIPRO`
- Need efficient small LM → `BootstrapFinetune`

**Saving and loading compiled programs:**

```python
optimized_program.save("path/to/program.json")
loaded_program = YOUR_PROGRAM_CLASS()
loaded_program.load(path="path/to/program.json")
```

### Data and Metrics

**`dspy.Example` objects** are the core data type — similar to dicts with utilities for marking inputs vs labels:

```python
qa_pair = dspy.Example(question="Q?", answer="A.").with_inputs("question")
input_only = qa_pair.inputs()    # fields marked as inputs
label_only = qa_pair.labels()    # remaining fields
```

**Metrics** are Python functions taking `example`, `pred`, and optional `trace`, returning a score:

```python
def validate_answer(example, pred, trace=None):
    return example.answer.lower() == pred.answer.lower()
```

When `trace is None`, the metric is used for evaluation. When `trace` is provided, it's used during bootstrapping to validate intermediate steps.

**Built-in metrics:** `dspy.evaluate.metrics.answer_exact_match`, `dspy.evaluate.metrics.answer_passage_match`.

**Evaluation utility:**

```python
from dspy.evaluate import Evaluate

evaluator = Evaluate(devset=devset, num_threads=1, display_progress=True, display_table=5)
evaluator(your_program, metric=validate_answer)
```

### Tips and Best Practices

- **Start simple** — Begin with `dspy.Predict` and a basic signature. Swap to `ChainOfThought` if quality is insufficient.
- **Don't over-engineer signatures** — Let the DSPy compiler optimize keywords rather than hand-tuning them.
- **Invest in metrics** — A well-defined metric is the foundation of optimization.
- **Small data works** — DSPy optimizers can produce strong results with as few as 10 training examples.
- **Use `teacher_settings`** — Compile with a stronger LM than you deploy with via `teacher_settings=dict(lm=stronger_lm)`.
- **Save compiled programs** — Use `.save()` and `.load()` to persist optimized programs as JSON.

## Advanced Topics

**Typed Predictors**: Pydantic-compatible structured I/O for DSPy signatures → [Typed Predictors](reference/01-typed-predictors.md)

**DSPy Assertions**: Enforce computational constraints on LM outputs with retry/backtracking → [DSPy Assertions](reference/02-assertions.md)

**Optimizers Reference**: Detailed optimizer configurations, parameters, and selection guide → [Optimizers Reference](reference/03-optimizers-reference.md)

**Data & Metrics**: Example objects, training data patterns, DataLoader, and metric design → [Data & Metrics](reference/04-data-and-metrics.md)

**Retrieval Models**: Configuring retrieval backends and building custom RM clients → [Retrieval Models](reference/05-retrieval-models.md)

**Advanced Signatures**: Signature internals, `replace` context manager, and prompt inspection → [Advanced Signatures](reference/06-advanced-signatures.md)

## References

- DSPy Documentation: <https://dspy-docs.vercel.app/>
- GitHub Repository: <https://github.com/stanfordnlp/dspy>
- DSPy Paper (ICLR 2024): "DSPy: Compiling Declarative Language Model Calls into Self-Improving Pipelines" — <https://arxiv.org/abs/2310.03714>
- DSPy Assertions Paper: "DSPy Assertions: Computational Constraints for Self-Refining Language Model Pipelines" — <https://arxiv.org/abs/2312.13382>
- DSPy Discord: <https://discord.gg/XCGy2WDCQB>
