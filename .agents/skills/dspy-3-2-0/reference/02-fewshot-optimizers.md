# Few-Shot Learning Optimizers

These optimizers extend prompts by automatically generating and including optimized few-shot examples (demonstrations). They work by running a teacher program on training data, collecting successful traces, and injecting the best examples into each predictor's prompt.

## LabeledFewShot

The simplest optimizer. Randomly selects `k` labeled examples from the trainset and assigns them as demonstrations to every predictor.

### How It Works

1. Takes the student program and a trainset of labeled examples
2. For each predictor in the program, randomly samples `min(k, len(trainset))` examples
3. Assigns those examples as `predictor.demos`
4. Returns the student with demos populated

```python
from dspy.teleprompt import LabeledFewShot

optimizer = LabeledFewShot(k=16)
optimized = optimizer.compile(student, trainset=trainset)
```

### Parameters

- `k`: Number of examples per predictor (default: 16)

### Internal Logic

```python
# Simplified implementation
for predictor in student.predictors():
    predictor.demos = rng.sample(trainset, min(k, len(trainset)))
```

No metric is needed — it purely distributes labeled data as few-shot context. Use this as a baseline before trying more sophisticated optimizers.

## BootstrapFewShot

The foundational DSPy optimizer. Uses a teacher module to generate complete multi-step demonstrations by running the full program on training examples, then validates them with a metric.

### How It Works — Step by Step

1. **Prepare student and teacher**: The student is reset (no demos). The teacher defaults to the student itself but can be a separate, pre-compiled program with compatible structure.

2. **Bootstrap the teacher**: If the teacher is uncompiled, first optimize it with `LabeledFewShot` using `max_labeled_demos` examples so it has some demonstrations to work from.

3. **Iterate through trainset examples**: For each training example:
   a. Clear the current example from all predictor demos (to avoid data leakage)
   b. Run the teacher on the example's inputs
   c. Capture the full execution trace (inputs/outputs at every predictor)
   d. Validate the final output against the metric
   e. If validation passes, record the trace as a bootstrapped demonstration
   f. If it fails and `max_rounds > 1`, retry with a fresh LM rollout at `temperature=1.0` to bypass caches

4. **Collect bootstrapped demos**: Stop after collecting `max_bootstrapped_demos` successful traces.

5. **Train the student**: For each predictor, assemble its demos from:
   - Up to `max_labeled_demos` randomly sampled labeled examples from the trainset
   - Up to `max_bootstrapped_demos` bootstrapped traces (filtered to include only examples where this predictor was part of a successful trajectory)

### Parameters

- `metric`: Validation function `(example, pred, trace=None) -> bool|float`
- `metric_threshold`: If metric returns float, only accept if >= threshold
- `max_bootstrapped_demos`: Max bootstrapped traces to collect (default: 4)
- `max_labeled_demos`: Max labeled examples per predictor (default: 16)
- `max_rounds`: Retry attempts per example with fresh rollouts (default: 1)
- `teacher_settings`: LM settings for the teacher model
- `teacher`: Optional separate teacher program

```python
from dspy.teleprompt import BootstrapFewShot

optimizer = BootstrapFewShot(
    metric=validate_answer,
    max_bootstrapped_demos=4,
    max_labeled_demos=16,
    max_rounds=2,
)
optimized = optimizer.compile(student, trainset=trainset)
```

### Key Design Decisions

- **Teacher-student separation**: The teacher generates traces; the student learns from them. They must have identical program structure (same predictors with same signatures).
- **Cache bypass**: When `max_rounds > 1`, each retry uses `lm.copy(rollout_id=round_idx, temperature=1.0)` to force fresh generations instead of cached responses.
- **Example exclusion**: During bootstrapping, the current training example is removed from all predictor demos to prevent trivial success from seeing its own answer.
- **Validation set**: Examples that failed to bootstrap form a validation set for later evaluation.

## BootstrapFewShotWithRandomSearch (BootstrapRS)

Applies `BootstrapFewShot` multiple times with different random seeds and selects the best program.

### How It Works

1. Runs several candidate programs:
   - The uncompiled program (zero-shot baseline)
   - A `LabeledFewShot` optimized program
   - A `BootstrapFewShot` program with unshuffled examples
   - `num_candidate_programs` additional `BootstrapFewShot` programs, each with a different random shuffle of the bootstrapped demos

2. Evaluates all candidates on the validation set (examples not used during bootstrapping)

3. Returns the candidate with the highest validation score

### Parameters

Same as `BootstrapFewShot`, plus:

- `num_candidate_programs`: Number of random-shuffle candidates to evaluate (default varies)
- `max_bootstraps`: Max examples to bootstrap from
- `num_threads`: Parallel evaluation threads

```python
from dspy.teleprompt import BootstrapFewShotWithRandomSearch

optimizer = BootstrapFewShotWithRandomSearch(
    metric=validate_answer,
    max_bootstrapped_demos=4,
    max_labeled_demos=4,
    num_candidate_programs=10,
    num_threads=4,
)
optimized = optimizer.compile(student, trainset=trainset)
```

### When to Use

- **~10 examples**: Start with `BootstrapFewShot`
- **50+ examples**: Use `BootstrapFewShotWithRandomSearch` — more data means more diversity in candidate programs, making random search effective

## KNNFewShot

Uses k-Nearest Neighbors to find the most relevant training examples at inference time, then uses those as demonstrations.

### How It Works

1. Embeds all training examples using a provided `Embedder`
2. At inference time, for each input, finds the `k` nearest neighbors in embedding space
3. Attaches those neighbors as dynamic few-shot demonstrations
4. Internally wraps a `BootstrapFewShot` optimizer for trace generation

```python
from dspy.teleprompt import KNNFewShot

optimizer = KNNFewShot(
    k=3,
    trainset=trainset,
    vectorizer=dspy.Embedder(my_embedding_fn),
)
optimized = optimizer.compile(student)
```

### Parameters

- `k`: Number of nearest neighbors (required)
- `trainset`: Training examples to search over (required)
- `vectorizer`: An `Embedder` instance for computing similarities (required)
- `**few_shot_bootstrap_args`: Passed to internal `BootstrapFewShot`

### Use Cases

Best when training data has clear clusters and the nearest examples are genuinely more relevant than random samples. Particularly effective for domain-specific tasks where examples vary significantly in difficulty or topic.
