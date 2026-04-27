# Instruction Optimization Algorithms

These optimizers produce optimal natural-language instructions for prompts. They go beyond few-shot examples to actually rewrite *what* the prompt tells the LM to do.

## COPRO (Coordinate Prompt Asccent)

COPRO generates and refines new instructions for each predictor using coordinate ascent (hill-climbing). It optimizes one predictor at a time while holding others fixed, cycling through all predictors for multiple rounds.

### How COPRO Works — Step by Step

**Phase 1: Seed Generation**

For each predictor in the program:
1. Extract the current basic instruction and output prefix
2. Use a prompt model (separate LM or the configured one) to generate `breadth` new instruction candidates via the `BasicGenerateInstruction` signature:

```python
class BasicGenerateInstruction(dspy.Signature):
    """You are an instruction optimizer for large language models. I will give you a ``signature`` of fields (inputs and outputs) in English. Your task is to propose an instruction that will lead a good language model to perform the task well. Don't be afraid to be creative."""

    basic_instruction = dspy.InputField(desc="The initial instructions before optimization")
    proposed_instruction = dspy.OutputField(desc="The improved instructions for the language model")
    proposed_prefix_for_output_field = dspy.OutputField(
        desc="The string at the end of the prompt, which will help the model start solving the task",
    )
```

3. Generates `breadth - 1` new candidates plus keeps the original instruction as a candidate
4. Uses `n=breadth-1` with `temperature=init_temperature` for diverse proposals

**Phase 2: Coordinate Ascent Loop (Depth Iterations)**

For each depth iteration (1 to `depth`):

For each predictor in the program (in order):
1. Take all instruction candidates for this predictor from the previous iteration
2. If multiple predictors exist, re-evaluate each candidate instruction combined with the *currently best* instructions for other predictors
3. Score each candidate by running the full program on the trainset and computing the metric
4. Keep the top-scoring candidates
5. Feed these attempted instructions (with scores) to `GenerateInstructionGivenAttempts`:

```python
class GenerateInstructionGivenAttempts(dspy.Signature):
    """You are an instruction optimizer for large language models. I will give some task instructions I've tried, along with their corresponding validation scores. The instructions are arranged in increasing order based on their scores, where higher scores indicate better quality.

    Your task is to propose a new instruction that will lead a good language model to perform the task even better. Don't be afraid to be creative."""

    attempted_instructions = dspy.InputField()
    proposed_instruction = dspy.OutputField(desc="The improved instructions for the language model")
    proposed_prefix_for_output_field = dspy.OutputField(
        desc="The string at the end of the prompt, which will help the model start solving the task",
    )
```

6. Generate `breadth` new candidates informed by what worked and what didn't
7. Deduplicate candidates (check both instruction text and output prefix)

**Phase 3: Selection**

After all depth iterations, select the predictor configuration with the highest overall score.

### Parameters

- `prompt_model`: Separate LM for instruction generation (optional, defaults to configured LM)
- `metric`: Task metric for evaluation (required)
- `breadth`: New prompts generated per iteration (default: 10)
- `depth`: Number of refinement rounds (default: 3)
- `init_temperature`: Temperature for initial proposals (default: 1.4 — higher = more creative)
- `track_stats`: Track optimization statistics

```python
from dspy.teleprompt import COPRO

optimizer = COPRO(
    metric=validate_answer,
    breadth=10,
    depth=3,
    init_temperature=1.4,
)
optimized = optimizer.compile(student, trainset=trainset, eval_kwargs=dict(num_threads=4))
```

### Key Characteristics

- **Zero-shot by default**: COPRO optimizes instructions without few-shot examples. It can work on programs that already have demos (from BootstrapFewShot).
- **Coordinate ascent**: Optimizes one predictor at a time. This makes the search space tractable for multi-predictor programs but means it may miss interactions between predictors.
- **Hill-climbing with diversity**: The high initial temperature and multi-candidate evaluation prevent premature convergence.
- **Instruction + prefix**: Optimizes both the task instruction AND the output field prefix (the string that prompts the LM to start generating).

## MIPROv2 (Meta-Instruction Prompt Optimization v2)

MIPROv2 is DSPy's most sophisticated instruction optimizer. It generates both instructions AND few-shot examples, then uses Bayesian Optimization to search over their combinations.

### How MIPROv2 Works — Step by Step

**Step 1: Bootstrap Few-Shot Examples**

Same bootstrapping process as `BootstrapFewShot`:
1. Run the (potentially unoptimized) program on training examples
2. Collect traces where the metric passes
3. Creates `num_fewshot_candidates` sets of demonstrations, each containing up to `max_bootstrapped_demos` bootstrapped examples and `max_labeled_demos` labeled examples

**Step 2: Propose Instruction Candidates**

For each predictor, generate instruction candidates using four awareness dimensions:

1. **Data-aware**: Summarizes properties of the training dataset (distribution, patterns, edge cases)
2. **Program-aware**: Analyzes the DSPy program's code structure and the specific predictor's role
3. **Few-shot-aware**: Shows bootstrapped examples as reference inputs/outputs for the predictor
4. **Tip-aware**: Includes a randomly sampled generation tip (e.g., "be creative", "be concise", "think step by step") to explore the instruction space

The prompt model receives all this context and generates `num_instruct_candidates` instruction proposals per predictor.

**Step 3: Bayesian Optimization Search**

This is where MIPROv2 differs fundamentally from COPRO:

1. Initialize a surrogate model (acquisition function) over the discrete space of instruction/demo combinations
2. For each of `num_trials` trials:
   a. Sample a minibatch of `minibatch_size` examples from the validation set
   b. The acquisition function proposes which instruction + demo combination to evaluate next
   c. Evaluate the candidate program on the minibatch
   d. Update the surrogate model with the result
3. Every `minibatch_full_eval_steps` trials, evaluate top candidates on the full validation set
4. Return the program with the best full-validation score

The Bayesian Optimization allows MIPROv2 to:
- Explore the joint space of instructions AND demonstrations across ALL predictors simultaneously (not coordinate ascent)
- Learn which combinations work well together
- Be sample-efficient by focusing evaluations on promising regions

### Parameters

- `metric`: Task metric (required)
- `auto`: Preset budget — "light", "medium", or "heavy"
- `num_trials`: Total BO trials (set automatically when using `auto`)
- `num_candidates`: Number of instruction/demo candidates per predictor
- `num_instruct_candidates` / `num_fewshot_candidates`: Separate control
- `max_bootstrapped_demos` / `max_labeled_demos`: Demo limits
- `minibatch`: Use minibatch evaluation (default: True)
- `minibatch_size`: Examples per trial evaluation (default: 35)
- `minibatch_full_eval_steps`: Full eval frequency (default: 5)
- `program_aware_proposer` / `data_aware_proposer` / `tip_aware_proposer` / `fewshot_aware_proposer`: Toggle awareness dimensions (all default True)
- `view_data_batch_size`: Examples shown to instruction proposer (default: 10)
- `task_model`: LM for the actual task execution
- `prompt_model`: LM for instruction generation

```python
from dspy.teleprompt import MIPROv2

optimizer = MIPROv2(
    metric=validate_answer,
    auto="medium",  # light/medium/heavy
    num_threads=4,
)
optimized = optimizer.compile(student, trainset=trainset)
```

### When to Use MIPROv2

- **200+ examples with sufficient budget**: MIPROv2 shines with enough data to prevent overfitting and enough trials to explore the space
- **40+ trials**: Longer optimization runs give BO time to find good combinations
- **Multi-predictor programs**: The joint search over predictors outperforms coordinate ascent
- **Zero-shot mode**: Set `max_bootstrapped_demos=0, max_labeled_demos=0` for instruction-only optimization

## SIMBA (Stochastic Introspective Mini-Batch Ascent)

SIMBA uses the LLM to introspectively analyze its own failures and generate self-improvement rules or demonstrations.

### How SIMBA Works — Step by Step

1. **Initialize**: Start with the unoptimized student program as program index 0

2. **Mini-batch sampling**: Sample a batch of `bsize` examples from the trainset

3. **Variability detection**: For each example in the batch, run multiple candidate programs and measure output variability. Examples with high variability are "challenging" — they expose weaknesses

4. **Candidate selection**: Use softmax-weighted sampling over program scores (temperature-controlled) to select source programs for mutation

5. **Introspective improvement**: For challenging examples, apply one of two strategies:
   - **append_a_rule**: The LLM analyzes why the program failed on specific examples and generates a self-reflective rule to add to the prompt instruction
   - **append_a_demo**: Adds a successful example as a demonstration (only if `max_demos > 0`)

6. **Program registration**: New candidate programs are registered with unique indices and their scores tracked

7. **Top-K + baseline selection**: Maintain the top-K scoring programs plus the original baseline, using softmax sampling for diversity

8. **Repeat** for `max_steps` iterations, tracking which programs improve

### Parameters

- `metric`: Evaluation function (required)
- `bsize`: Mini-batch size (default: 32)
- `num_candidates`: New candidates per iteration (default: 6)
- `max_steps`: Optimization steps (default: 8)
- `max_demos`: Max demonstrations per predictor (default: 4; set to 0 for rules-only)
- `prompt_model`: LM for introspection (defaults to configured LM)
- `temperature_for_sampling`: Temperature for trajectory sampling (default: 0.2)
- `temperature_for_candidates`: Temperature for source program selection (default: 0.2)

```python
from dspy.teleprompt import SIMBA

optimizer = SIMBA(
    metric=validate_answer,
    bsize=32,
    num_candidates=6,
    max_steps=8,
    max_demos=4,
)
optimized = optimizer.compile(student, trainset=trainset)
```

### Key Characteristics

- **Self-reflective**: Unlike COPRO/MIPRO which use a separate prompt model, SIMBA uses the task LM itself to reason about its failures
- **Variability-driven**: Focuses on examples where programs disagree, which are most informative for improvement
- **Lightweight**: Fewer LM calls than MIPROv2's Bayesian Optimization loop
- **Rules + demos**: Can improve either through instruction rules or few-shot examples
