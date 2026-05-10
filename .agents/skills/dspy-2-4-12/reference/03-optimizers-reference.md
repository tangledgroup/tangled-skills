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
- `teacher_settings` — Settings for the teacher predictor (e.g., `dict(lm=stronger_lm)`)
- `max_bootstrapped_demos` — Max bootstrapped demonstrations per predictor (default: 4)
- `max_labeled_demos` — Max labeled demonstrations per predictor (default: 16)
- `max_rounds` — Max bootstrapping rounds (default: 1)
- `max_errors` — Max errors before halting (default: 5)

**Bootstrapping a bootstrapped program:** You can compile an already-compiled program using it as the teacher:

```python
program_compiled_x2 = teleprompter.compile(
    student=your_program,
    teacher=your_program_compiled,
    trainset=trainset,
)
```

### BootstrapFewShotWithRandomSearch

Runs BootstrapFewShot multiple times with random search over demonstrations, selecting the best program. Default starting point if unsure which optimizer to use.

```python
from dspy.teleprompt import BootstrapFewShotWithRandomSearch

config = dict(
    max_bootstrapped_demos=4,
    max_labeled_demos=4,
    num_candidate_programs=10,
    num_threads=4,
)
teleprompter = BootstrapFewShotWithRandomSearch(metric=my_metric, **config)
compiled = teleprompter.compile(RAG(), trainset=trainset, valset=devset)
```

**Parameters:** All `BootstrapFewShot` params plus:
- `num_candidate_programs` — Number of random programs to evaluate
- `num_threads` — Parallel threads for evaluation

### BootstrapFewShotWithOptuna

Applies BootstrapFewShot with Optuna hyperparameter optimization across demonstration sets, running trials to maximize evaluation metrics.

```python
from dspy.teleprompt import BootstrapFewShotWithOptuna

teleprompter = BootstrapFewShotWithOptuna(
    metric=my_metric,
    max_bootstrapped_demos=2,
    num_candidate_programs=8,
    num_threads=NUM_THREADS,
)
compiled = teleprompter.compile(student=RAG(), trainset=trainset, valset=devset)
```

### KNNFewShot

Selects demonstrations through k-Nearest Neighbors algorithm for diverse example selection from different clusters. Vectorizes examples, clusters them, then uses cluster centers with BootstrapFewShot. Useful when there's a lot of data over random spaces.

```python
from dspy.predict import KNN
from dspy.teleprompt import KNNFewShot

knn_optimizer = KNNFewShot(KNN, k=3, trainset=trainset)
compiled = knn_optimizer.compile(student=RAG(), trainset=trainset, valset=devset)
```

## Automatic Instruction Optimization

### COPRO

Generates and refines new instructions for each step via coordinate ascent (hill-climbing using the metric function and trainset). Also optimizes output field prefixes.

```python
from dspy.teleprompt import COPRO

teleprompter = COPRO(
    prompt_model=gpt4,
    metric=my_metric,
    breadth=10,   # number of instruction/prefix candidates
    depth=10,     # iterations of optimization
    init_temperature=1.0,
    verbose=True,
)

eval_kwargs = dict(num_threads=16, display_progress=True, display_table=0)
compiled = teleprompter.compile(RAG(), trainset=trainset, eval_kwargs=eval_kwargs)
```

COPRO uses internal signatures (`BasicGenerateInstruction`, `GenerateInstructionGivenAttempts`) to iteratively generate and refine instructions. After optimization, copy the best instruction/prefix into your signature class manually.

### MIPRO

Generates instructions *and* few-shot examples in each step. Instruction generation is data-aware and demonstration-aware. Uses Bayesian Optimization to search over the space of instructions/demonstrations across modules. Best for 300+ examples.

```python
from dspy.teleprompt import MIPRO

teleprompter = MIPRO(
    prompt_model=gpt4,
    task_model=turbo,
    metric=my_metric,
    num_candidates=10,
    init_temperature=1.0,
)

kwargs = dict(num_threads=NUM_THREADS, display_progress=True, display_table=0)
compiled = teleprompter.compile(
    RAG(), trainset=trainset,
    num_trials=100,
    max_bootstrapped_demos=3,
    max_labeled_demos=5,
    eval_kwargs=kwargs,
)
```

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
    epochs=2,
    bf16=True,
    bsize=6,
    accumsteps=2,
    lr=5e-5,
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

After finetuning, load the checkpoint and activate it in the program:

```python
ckpt_path = "saved_checkpoint_path"
LM = dspy.HFModel(checkpoint=ckpt_path, model='google/flan-t5-base')

for p in compiled.predictors():
    p.lm = LM
    p.activated = False
```

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

Typical workflow: compile with BootstrapFewShotWithRandomSearch, then ensemble the top candidate programs:

```python
fewshot_optimizer = BootstrapFewShotWithRandomSearch(metric=my_metric, num_candidate_programs=8)
compiled = fewshot_optimizer.compile(RAG(), trainset=trainset, valset=devset)

ensemble_optimizer = Ensemble(reduce_fn=dspy.majority)
programs = [x[-1] for x in compiled.candidate_programs]
ensembled = ensemble_optimizer.compile(programs[:3])
```

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
