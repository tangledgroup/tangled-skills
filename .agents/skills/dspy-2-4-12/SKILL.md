---
name: dspy-2-4-12
description: Framework for programming rather than prompting language models. Compiles LM calls into self-improving pipelines by tuning prompts and/or weights to maximize user-defined metrics. Use when building classifiers, RAG pipelines, agents, or any multi-stage LM program requiring automated prompt engineering, few-shot bootstrapping, or model fine-tuning driven by evaluation metrics.
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

**Note:** DSPy 2.4.x uses `dspy.OpenAI`, `dspy.Cohere`, etc. for LM clients directly — not the `dspy.LM()` LiteLLM-style unified interface introduced in later versions. Optimizers are imported from `dspy.teleprompt`.

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

**Class-based signatures** provide more control:

```python
class Emotion(dspy.Signature):
    """Classify emotion among sadness, joy, love, anger, fear, surprise."""
    sentence = dspy.InputField()
    sentiment = dspy.OutputField()

classify = dspy.Predict(Emotion)
result = classify(sentence="i started feeling a little vulnerable")
```

### Modules

A **Module** is a building block that abstracts a prompting technique:

- **`dspy.Predict`** — Basic predictor
- **`dspy.ChainOfThought`** — Adds step-by-step reasoning
- **`dspy.ProgramOfThought`** — Generates and executes code
- **`dspy.ReAct`** — Agent with tool use
- **`dspy.MultiChainComparison`** — Compares multiple ChainOfThought outputs
- **`dspy.majority`** — Voting over predictions

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

### Language Models

Configure DSPy with provider-specific LM clients:

```python
import dspy

# OpenAI
gpt3 = dspy.OpenAI(model='gpt-3.5-turbo-1106', max_tokens=300)
dspy.configure(lm=gpt3)

# GPT-4
gpt4 = dspy.OpenAI(model='gpt-4-1106-preview', max_tokens=300)

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

with dspy.context(lm=gpt4):
    response = qa(question="How many floors are in the castle?")
    print('GPT-4:', response.answer)
```

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

## Usage Examples

### Example 1: Simple Classification

```python
import dspy

dspy.configure(lm=dspy.OpenAI(model='gpt-3.5-turbo-1106', max_tokens=300))

classify = dspy.Predict('sentence -> sentiment')
result = classify(sentence="It's a charming and often affecting journey.")
print(result.sentiment)  # 'Positive'
```

### Example 2: RAG Pipeline

```python
import dspy

dspy.configure(lm=dspy.OpenAI(model='gpt-3.5-turbo-1106', max_tokens=300))

class RAG(dspy.Module):
    def __init__(self, num_passages=3):
        super().__init__()
        self.retrieve = dspy.Retrieve(k=num_passages)
        self.generate_answer = dspy.ChainOfThought("context, question -> answer")

    def forward(self, question):
        context = self.retrieve(question).passages
        return self.generate_answer(context=context, question=question)

rag = RAG()
result = rag(question="What castle did David Gregory inherit?")
```

### Example 3: Compiling a Program

```python
import dspy
from dspy.teleprompt import BootstrapFewShot

dspy.configure(lm=dspy.OpenAI(model='gpt-3.5-turbo-1106', max_tokens=300))

qa = dspy.ChainOfThought("question -> answer")
trainset = [dspy.Example(question=f"Q{i}", answer=f"A{i}").with_inputs("question") for i in range(50)]

optimizer = BootstrapFewShot(metric=dspy.evaluate.metrics.answer_exact_match)
optimized_qa = optimizer.compile(student=qa, trainset=trainset)
result = optimized_qa(question="What is the capital of France?")
```

### Example 4: ReAct Agent

```python
import dspy

dspy.configure(lm=dspy.OpenAI(model='gpt-3.5-turbo-1106', max_tokens=300))

class BasicQA(dspy.Signature):
    """Answer questions with short factoid answers."""
    question = dspy.InputField()
    answer = dspy.OutputField(desc="often between 1 and 5 words")

react = dspy.ReAct(BasicQA)
result = react(question="What is the color of the sky?")
```

### Example 5: ProgramOfThought for Math

```python
import dspy

dspy.configure(lm=dspy.OpenAI(model='gpt-3.5-turbo-1106', max_tokens=300))

class GenerateAnswer(dspy.Signature):
    """Answer questions with short factoid answers."""
    question = dspy.InputField()
    answer = dspy.OutputField(desc="often between 1 and 5 words")

pot = dspy.ProgramOfThought(GenerateAnswer)
result = pot(question="Sarah has 5 apples. She buys 7 more. How many does she have?")
```

## Tips and Best Practices

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

**Data & Metrics**: Example objects, training data patterns, and metric design → [Data & Metrics](reference/04-data-and-metrics.md)

## References

- DSPy Documentation: <https://dspy-docs.vercel.app/>
- GitHub Repository: <https://github.com/stanfordnlp/dspy>
- DSPy Paper (ICLR 2024): "DSPy: Compiling Declarative Language Model Calls into Self-Improving Pipelines" — <https://arxiv.org/abs/2310.03714>
- DSPy Assertions Paper: "DSPy Assertions: Computational Constraints for Self-Refining Language Model Pipelines" — <https://arxiv.org/abs/2312.13382>
- DSPy Discord: <https://discord.gg/XCGy2WDCQB>
