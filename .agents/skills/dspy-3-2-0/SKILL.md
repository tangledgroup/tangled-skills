---
name: dspy-3-2-0
description: DSPy is the framework for programming—rather than prompting—language models. It provides modular AI system components (Signatures, Modules, Adapters) and optimization algorithms that compile declarative LM calls into self-improving pipelines by tuning prompts and/or LM weights to maximize user-defined metrics. Use when building classifiers, RAG pipelines, agents, or any multi-stage LM program where you want automated prompt engineering, few-shot example synthesis, instruction optimization, or model fine-tuning driven by evaluation metrics rather than manual prompt hacking.
license: MIT
author: Tangled <noreply@tangledgroup.com>
version: "3.2.0"
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
  - https://dspy.ai/
  - https://arxiv.org/abs/2310.03714
---

# DSPy 3.2.0

## Overview

DSPy (Declarative Self-improving Python) is a framework for **programming**—not prompting—foundation models. Instead of crafting brittle prompts, you write compositional Python code using DSPy modules and signatures, then use DSPy optimizers to **teach your LM to deliver high-quality outputs** by automatically tuning prompts and/or model weights.

DSPy treats language model programs like neural networks: modules have learnable parameters (prompts, demonstrations, LM weights), optimizers tune those parameters against a metric, and the compiled program can be saved and loaded. This mirrors PyTorch's design but applied to LM programs instead of tensor computations.

**Core thesis:** DSPy optimizers can produce better prompts than humans write—not because they are more creative, but because they can try more combinations and tune directly against metrics.

## When to Use

- Building multi-stage AI pipelines (RAG, classification, agents, extraction) where prompt quality matters
- Automating prompt engineering: replacing manual iteration with metric-driven optimization
- Synthesizing high-quality few-shot examples from training data
- Optimizing natural-language instructions for each step of a pipeline
- Fine-tuning small LMs from DSPy program traces
- Composing prompt optimization and weight optimization in sequences
- Building production AI systems where prompts need to adapt to data distributions

## Core Architecture

DSPy has three layers:

1. **Signatures** — Declarative input/output specifications (what the LM should do)
2. **Modules** — Reusable building blocks that implement prompting techniques (how to do it)
3. **Optimizers** — Algorithms that tune module parameters against metrics (how to improve it)

```python
# Basic pattern: declare signature, wrap in module, optimize with metric
import dspy

lm = dspy.LM('openai/gpt-4o-mini')
dspy.configure(lm=lm)

# 1. Define a program using signatures and modules
qa = dspy.ChainOfThought("question -> answer")

# 2. Define a metric
def validate_answer(example, pred, trace=None):
    return example.answer.lower() == pred.answer.lower()

# 3. Optimize
optimizer = dspy.MIPROv2(metric=validate_answer, auto="medium")
optimized_qa = optimizer.compile(qa, trainset=trainset)

# 4. Use the optimized program
result = optimized_qa(question="What is the capital of France?")
```

## Installation / Setup

Install via pip:

```bash
pip install dspy
```

For the latest from main:

```bash
pip install git+https://github.com/stanfordnlp/dspy.git
```

Configure a language model before any DSPy code:

```python
import dspy

lm = dspy.LM('openai/gpt-4o-mini', api_key='YOUR_KEY')
dspy.configure(lm=lm)
```

DSPy supports OpenAI, Gemini, Anthropic, Vertex AI, Databricks, local LMs via any LiteLLM-compatible provider, and custom providers.

## Advanced Topics

**Signatures & Modules**: The building blocks of DSPy programs → [Signatures & Modules](reference/01-signatures-and-modules.md)

**Few-Shot Optimizers**: LabeledFewShot, BootstrapFewShot, BootstrapRS, KNNFewShot → [Few-Shot Learning Optimizers](reference/02-fewshot-optimizers.md)

**Instruction Optimizers**: COPRO, MIPROv2, SIMBA — algorithms that evolve prompt instructions → [Instruction Optimization Algorithms](reference/03-instruction-optimizers.md)

**GEPA**: Genetic-Pareto reflective optimizer with textual feedback and Pareto-frontier evolution → [GEPA Reflective Optimizer](reference/04-gepa-optimizer.md)

**Finetuning & Meta-Optimizers**: BootstrapFinetune, BetterTogether, Ensemble → [Finetuning & Meta-Optimizers](reference/05-finetuning-meta.md)

**Evaluation & Metrics**: Defining metrics, the Evaluate utility, GEPA feedback metrics → [Evaluation & Metrics](reference/06-evaluation-metrics.md)
