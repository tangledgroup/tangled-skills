# Optimizers Reference

## Contents
- Overview
- Automatic Few-Shot Learning
- Automatic Instruction Optimization
- Automatic Finetuning
- Program Transformations
- Optimizer Selection Guide
- Saving and Loading

## Overview

A **DSPy optimizer** is an algorithm that tunes the parameters of a DSPy program (prompts and/or LM weights) to maximize user-defined metrics. Each DSPy module has internal parameters of three kinds:

1. **LM weights** — The underlying model parameters
2. **Instructions** — The prompt text for each step
3. **Demonstrations** — Few-shot examples in the prompt

Optimizers can combine gradient descent (for LM weights) and discrete LM-driven optimization (for instructions and demonstrations).

All optimizers are imported from `dspy.teleprompt`:

```python
from dspy.teleprompt import BootstrapFewShot, BootstrapFewShotWithRandomSearch, MIPRO
```

## Automatic Few-Shot Learning

These optimizers extend the signature by automatically generating and including optimized examples within the prompt.

### LabeledFewShot

Simply constructs few-shot examples from provided labeled data. No bootstrapping.

```python
from dspy.teleprompt import LabeledFewShot

teleprompter = LabeledFewShot(k=16)
compiled = teleprompter.compile(student=RAG(), trainset=trainset)
```

**Parameters:**
- `k` — Number of examples per predictor (default: 16)

### BootstrapFewShot

Uses a teacher module to generate complete demonstrations for every stage of your program, validated by your metric.

```python
from dspy.teleprompt import BootstrapFewShot

teacher = dspy.OpenAI(model='gpt-3.5-turbo', api_key=openai.api_key, model_type='chat')
teleprompter = BootstrapFewShot(
    metric=my_metric,
    teacher_settings=dict(lm=teacher),
    max_bootstrapped_demos=4,
    max_labeled_demos=16,
)
compiled = teleprompter.compile(student=RAG(), trainset=trainset)
```

**Parameters:**
- `metric` — Metric function to evaluate during bootstrapping
- `metric_threshold` — Score threshold for successful examples
- `teacher_settings` — Settings for the teacher predictor
- `max_bootstrapped_demos` — Max bootstrapped demonstrations per predictor (default: 4)
- `max_labeled_demos` — Max labeled demonstrations per predictor (default: 16)
- `max_rounds` — Max bootstrapping rounds (default: 1)
- `max_errors` — Max errors before halting (default: 5)

### BootstrapFewShotWithRandomSearch

Runs BootstrapFewShot multiple times with random search over demonstrations, selecting the best program.

```python
from dspy.teleprompt import BootstrapFewShotWithRandomSearch

config = dict(
    max_bootstrapped_demos=4,
    max_labeled_demos=4,
    num_candidate_programs=10,
    num_threads=4,
)
teleprompter = BootstrapFewShotWithRandomSearch(metric=my_metric, **config)
compiled = teleprompter.compile(RAG(), trainset=trainset)
```

**Parameters:** All `BootstrapFewShot` params plus:
- `num_candidate_programs` — Number of random programs to evaluate (default varies)

### BootstrapFewShotWithOptuna

Applies BootstrapFewShot with Optuna optimization across demonstration sets.

### KNNFewShot

Selects demonstrations through k-Nearest Neighbors algorithm for diverse example selection from different clusters. Vectorizes examples, clusters them, then uses cluster centers with BootstrapFewShot. Useful when there's a lot of data over random spaces.

## Automatic Instruction Optimization

### COPRO

Generates and refines new instructions for each step via coordinate ascent (hill-climbing using the metric function and trainset).

```python
from dspy.teleprompt import COPRO

teleprompter = COPRO(metric=my_metric, depth=10)
compiled = teleprompter.compile(RAG(), trainset=trainset)
```

**Parameters:**
- `depth` — Number of iterations of prompt improvement (default varies)

### MIPRO

Generates instructions *and* few-shot examples in each step. Instruction generation is data-aware and demonstration-aware. Uses Bayesian Optimization to search over the space of instructions/demonstrations across modules. Best for 300+ examples.

## Automatic Finetuning

### BootstrapFinetune

Distills a prompt-based DSPy program into weight updates for smaller LMs. The output is a DSPy program with the same steps, but each step uses a finetuned model instead of prompted LM.

```python
from dspy.teleprompt import BootstrapFinetune

teacher = dspy.OpenAI(model='gpt-3.5-turbo', api_key=openai.api_key, model_type='chat')
teleprompter = BootstrapFinetune(
    metric=my_metric,
    teacher_settings=dict(lm=teacher),
)
compiled = teleprompter.compile(
    student=RAG(),
    trainset=trainset,
    target='google/flan-t5-base',
)
```

**Parameters:** All `BootstrapFewShot` params plus:
- `target` — Target model for fine-tuning (default: 't5-large')
- `bsize` — Batch size (default: 12)
- `accumsteps` — Gradient accumulation steps (default: 1)
- `lr` — Learning rate (default: 5e-5)
- `epochs` — Number of training epochs (default: 1)
- `bf16` — Enable BF16 mixed precision (default: False)
- `multitask` — Enable multitask fine-tuning (default: True)

## Program Transformations

### Ensemble

Combines multiple DSPy programs into one, reducing outputs via a reduction function.

```python
from dspy.teleprompt import Ensemble

teleprompter = Ensemble(reduce_fn=dspy.majority, size=2)
ensembled = teleprompter.compile([program1, program2, program3])
```

**Parameters:**
- `reduce_fn` — Function to reduce multiple outputs (e.g., `dspy.majority`)
- `size` — Number of programs to sample for ensembling

## Optimizer Selection Guide

| Data Size | Recommended Optimizer |
|-----------|----------------------|
| ~10 examples | `BootstrapFewShot` |
| ~50 examples | `BootstrapFewShotWithRandomSearch` |
| 300+ examples | `MIPRO` |
| Need small LM | `BootstrapFinetune` (after prompt optimization) |

**Default starting point:** If unsure, use `BootstrapFewShotWithRandomSearch`.

## Saving and Loading

After compiling, save the optimized program:

```python
optimized_program.save("path/to/program.json")
```

The file is plain-text JSON containing all parameters and steps. You can read it to inspect what the optimizer generated.

To load:

```python
loaded_program = YOUR_PROGRAM_CLASS()
loaded_program.load(path="path/to/program.json")
```
