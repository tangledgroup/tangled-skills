# Finetuning & Meta-Optimizers

## BootstrapFinetune

Distills a prompt-based DSPy program into weight updates. The output is a DSPy program with the same structure, but where each step uses a fine-tuned model instead of a prompted LM.

**Constructor:** `dspy.BootstrapFinetune(metric=None, multitask=True, train_kwargs=None, adapter=None, exclude_demos=False, num_threads=None)`

### How BootstrapFinetune Works

1. **Bootstrap traces**: Like `BootstrapFewShot`, runs a teacher program on training data to collect full execution traces (inputs and outputs at every predictor)

2. **Build training datasets per predictor**: For each predictor in the program, extracts its input/output pairs from the collected traces to form a supervised fine-tuning dataset

3. **Fine-tune LM weights**: Trains a smaller LM (e.g., 1B-7B parameter model) on each predictor's dataset using standard fine-tuning

4. **Replace prompted predictors with finetuned models**: The compiled program has the same structure, but each `dspy.Predict` internally uses the fine-tuned weights instead of prompt engineering

### Requirements

- Student program must have LMs explicitly set via `set_lm()` — cannot rely on global `dspy.settings.lm`
- Requires a fine-tunable model backend (e.g., OpenAI finetuning, local training)

### Parameters

- `metric`: Validation function (required)
- `multitask`: Train all predictors jointly (default: True) vs separately
- `train_kwargs`: Fine-tuning parameters, can be per-LM dict
- `adapter`: Adapter to use during fine-tuning, can be per-LM dict
- `exclude_demos`: Exclude demonstration examples from fine-tuning data
- `num_threads`: Parallel execution threads

```python
classify.set_lm(lm)

optimizer = dspy.BootstrapFinetune(
    metric=lambda x, y, trace=None: x.label == y.label,
    num_threads=24,
)
optimized = optimizer.compile(classify, trainset=trainset)
```

## BetterTogether

A meta-optimizer that combines prompt optimization and weight optimization (fine-tuning) in configurable sequences. Proposed in "Fine-Tuning and Prompt Optimization: Two Great Steps that Work Better Together" (Soylu, Potts, Khattab, 2024).

**Constructor:** `dspy.BetterTogether(metric, **optimizers)`

### Core Insight

Prompt optimization discovers effective task decompositions and reasoning strategies. Weight optimization specializes the model to execute these patterns efficiently. Using them in sequences allows each to build on the other's improvements.

Empirically, `prompt → weight` or `prompt → weight → prompt` sequences often outperform either strategy alone, even with state-of-the-art optimizers.

### How BetterTogether Works

1. **Initialize** with a prompt optimizer (`p`) and a weight optimizer (`w`)
2. **Parse the strategy string**: e.g., `"p -> w"` means prompt-then-weight, `"p -> w -> p"` means three stages
3. **Execute optimizers in sequence**: Each optimizer's output becomes the next optimizer's input
4. **Track validation scores**: When a valset is provided, return the best-performing program across all stages

```python
optimizer = dspy.BetterTogether(
    metric=my_metric,
    p=dspy.GEPA(metric=my_metric, auto="medium"),
    w=dspy.BootstrapFinetune(metric=my_metric),
)

student.set_lm(lm)

compiled = optimizer.compile(
    student,
    trainset=trainset,
    valset=valset,
    strategy="p -> w",
)
```

### Strategy Strings

- `"p"`: Prompt optimization only
- `"w"`: Weight optimization only
- `"p -> w"`: Prompt then weight (most common)
- `"p -> w -> p"`: Prompt, weight, then refine prompts on the fine-tuned model

### Passing Optimizer-Specific Arguments

```python
compiled = optimizer.compile(
    student,
    trainset=trainset,
    valset=valset,
    strategy="p -> w",
    optimizer_compile_args={
        "p": {"auto": "heavy"},
        "w": {"max_bootstrapped_demos": 8},
    },
)
```

### Requirements

- Student program must have LMs explicitly set via `set_lm()`
- Both `p` and `w` optimizers must accept the same metric interface
- Weight optimizers require fine-tunable model backends

## Ensemble

Ensembles multiple DSPy programs into a single program that runs all of them and reduces outputs.

**Constructor:** `dspy.Ensemble(reduce_fn=None, size=None, deterministic=False)`

### How Ensemble Works

1. Takes a list of trained DSPy programs
2. Creates an `EnsembledProgram` module that:
   - On each forward call, optionally samples `size` programs from the list (or uses all if `size` is None)
   - Runs all selected programs on the inputs
   - Applies a `reduce_fn` to combine outputs
3. Returns the ensembled program

```python
programs = [prog1, prog2, prog3, prog4, prog5]

optimizer = dspy.Ensemble(
    reduce_fn=dspy.majority,  # Vote for the most common answer
    size=3,                   # Sample 3 out of 5 at inference time
)
ensembled = optimizer.compile(programs)
```

### Common reduce_fn: dspy.majority

Takes a list of predictions and returns the most common value for each output field:

```python
outputs = [pred1, pred2, pred3, pred4, pred5]
result = dspy.majority(outputs)  # Returns prediction with majority-voted fields
```

### Use Cases

- **Scale inference-time compute**: After optimization, extract top-N candidates and ensemble them
- **Complementary strategies**: Different optimizers may discover different reasoning patterns; ensembling captures all of them
- **Robustness**: Reduces variance by averaging across diverse programs

## Composing Optimizers

DSPy optimizers compose naturally. Common patterns:

```python
# Pattern 1: Optimize prompts, then fine-tune
mipro = dspy.MIPROv2(metric=metric, auto="medium")
prompt_optimized = mipro.compile(student, trainset=trainset)

finetune = dspy.BootstrapFinetune(metric=metric)
final = finetune.compile(prompt_optimized, trainset=trainset)

# Pattern 2: Optimize, ensemble top candidates, optimize again
mipro = dspy.MIPROv2(metric=metric, auto="heavy")
optimized = mipro.compile(student, trainset=trainset)

ensemble = dspy.Ensemble(reduce_fn=dspy.majority)
final = ensemble.compile(optimized.candidate_programs[:5])

# Pattern 3: BetterTogether (prompt -> weight -> prompt)
bt = dspy.BetterTogether(metric=metric, p=dspy.MIPROv2(...), w=dspy.BootstrapFinetune(...))
final = bt.compile(student, trainset=trainset, valset=valset, strategy="p -> w -> p")
```

This composability is central to DSPy's design: you can scale both **pre-inference compute** (optimization budget) and **inference-time compute** (ensembles) systematically.
