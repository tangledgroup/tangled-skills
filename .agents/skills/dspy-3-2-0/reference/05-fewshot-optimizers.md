# Few-Shot Learning Optimizers

These optimizers extend prompts by automatically generating and including optimized few-shot examples (demonstrations). They work by running a teacher program on training data, collecting successful traces, and injecting the best examples into each predictor's prompt.

## LabeledFewShot

The simplest optimizer. Randomly selects `k` labeled examples from the trainset and assigns them as demonstrations to every predictor.

```python
optimizer = dspy.LabeledFewShot(k=16)
optimized = optimizer.compile(student, trainset=trainset)
```

**Internal logic:** For each predictor in the student program, randomly samples `min(k, len(trainset))` examples and assigns them as `predictor.demos`. No metric is needed — it purely distributes labeled data as few-shot context.

**Parameters:**
- `k`: Number of examples per predictor (default: 16)

## BootstrapFewShot

The foundational DSPy optimizer. Uses a teacher module to generate complete multi-step demonstrations by running the full program on training examples, then validates them with a metric.

```python
optimizer = dspy.BootstrapFewShot(
    metric=validate_answer,
    max_bootstrapped_demos=4,
    max_labeled_demos=16,
    max_rounds=2,
)
optimized = optimizer.compile(student, trainset=trainset)
```

**How It Works — Step by Step:**

1. **Prepare student and teacher**: Student is reset (no demos). Teacher defaults to the student itself but can be a separate pre-compiled program with compatible structure.

2. **Bootstrap the teacher**: If uncompiled, first optimize it with `LabeledFewShot` using `max_labeled_demos` examples so it has demonstrations to work from.

3. **Iterate through trainset examples**: For each training example:
   - Clear the current example from all predictor demos (to avoid data leakage)
   - Run the teacher on the example's inputs
   - Capture the full execution trace (inputs/outputs at every predictor)
   - Validate the final output against the metric
   - If validation passes, record the trace as a bootstrapped demonstration
   - If it fails and `max_rounds > 1`, retry with a fresh LM rollout at `temperature=1.0` to bypass caches

4. **Collect bootstrapped demos**: Stop after collecting `max_bootstrapped_demos` successful traces.

5. **Train the student**: For each predictor, assemble its demos from:
   - Up to `max_labeled_demos` randomly sampled labeled examples
   - Up to `max_bootstrapped_demos` bootstrapped traces (filtered to include only examples where this predictor was part of a successful trajectory)

**Parameters:**
- `metric`: Validation function `(example, pred, trace=None) -> bool|float`
- `metric_threshold`: If metric returns float, only accept if >= threshold
- `max_bootstrapped_demos`: Max bootstrapped traces (default: 4)
- `max_labeled_demos`: Max labeled examples per predictor (default: 16)
- `max_rounds`: Retry attempts per example with fresh rollouts (default: 1)
- `teacher_settings`: LM settings for the teacher model
- `teacher`: Optional separate teacher program

**Key design decisions:**
- Teacher-student separation: they must have identical program structure
- Cache bypass: retries use `lm.copy(rollout_id=round_idx, temperature=1.0)`
- Example exclusion during bootstrapping prevents trivial success from seeing its own answer
- Failed examples form a validation set for later evaluation

## BootstrapFewShotWithRandomSearch (BootstrapRS)

Applies `BootstrapFewShot` multiple times with different random seeds and selects the best program.

```python
optimizer = dspy.BootstrapFewShotWithRandomSearch(
    metric=validate_answer,
    max_bootstrapped_demos=4,
    max_labeled_demos=4,
    num_candidate_programs=16,
    num_threads=4,
)
optimized = optimizer.compile(student, trainset=trainset)
```

**How It Works:**

1. Runs several candidate programs:
   - The uncompiled program (zero-shot baseline)
   - A `LabeledFewShot` optimized program
   - A `BootstrapFewShot` program with unshuffled examples
   - `num_candidate_programs` additional `BootstrapFewShot` programs, each with a different random shuffle of the bootstrapped demos

2. Evaluates all candidates on the validation set (examples not used during bootstrapping)

3. Returns the candidate with the highest validation score

**Parameters:** Same as `BootstrapFewShot`, plus:
- `num_candidate_programs`: Number of random-shuffle candidates (default: 16)
- `num_threads`: Parallel evaluation threads
- `stop_at_score`: Early stopping threshold

## KNNFewShot

Uses k-Nearest Neighbors to find the most relevant training examples at inference time.

```python
optimizer = dspy.KNNFewShot(
    k=3,
    trainset=trainset,
    vectorizer=dspy.Embedder(my_embedding_fn),
)
optimized = optimizer.compile(student)
```

**How It Works:**

1. Embeds all training examples using a provided `Embedder`
2. At inference time, for each input, finds the `k` nearest neighbors in embedding space
3. Attaches those neighbors as dynamic few-shot demonstrations
4. Internally wraps a `BootstrapFewShot` optimizer for trace generation

**Parameters:**
- `k`: Number of nearest neighbors (required)
- `trainset`: Training examples to search over (required)
- `vectorizer`: An `Embedder` instance for computing similarities (required)
- `**few_shot_bootstrap_args`: Passed to internal `BootstrapFewShot`

## InferRules

Extends `BootstrapFewShot` by inducing general rules from bootstrapped examples.

```python
optimizer = dspy.InferRules(
    num_candidates=10,
    num_rules=10,
    metric=my_metric,
)
optimized = optimizer.compile(student, trainset=trainset)
```

**Parameters:**
- `num_candidates`: Number of candidate rule sets (default: 10)
- `num_rules`: Number of rules to induce (default: 10)

## Choosing a Few-Shot Optimizer

- **~10 examples**: Start with `BootstrapFewShot`
- **50+ examples**: Use `BootstrapFewShotWithRandomSearch` — more data means more diversity in candidate programs
- **Domain-specific clustering**: Use `KNNFewShot` when nearest examples are genuinely more relevant
- **Rule-based reasoning**: Use `InferRules` for tasks where general principles matter more than specific examples
